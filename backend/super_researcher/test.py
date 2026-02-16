from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json
import weaviate
from weaviate.classes.config import Configure
from weaviate.util import generate_uuid5
from prompting import search_system_prompt, reliability_prompt, urgency_prompt, question

# Initialize clients
search_client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)

llm_client = OpenAI(
    base_url="http://127.0.0.1:8082/v1",
    api_key="sk-no-key-required"
)

# MCP server configuration
server_params = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
    env=None
)

async def run_chat_loop():
    print("Starting MCP Server (DuckDuckGo)...")

    # Start the MCP Server as a subprocess
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Discover tools from MCP and convert to OpenAI format
            print("Discovering tools...")
            mcp_tools = await session.list_tools()

            openai_tools = []
            for tool in mcp_tools.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            print(f"Found {len(openai_tools)} tools: {[t['function']['name'] for t in openai_tools]}")

            # Initialize Weaviate client
            db_client = weaviate.connect_to_local(
                headers={"X-OpenAI-Api-Key": "sk-no-key-required"}
            )

            try:
                # Clean slate for this example
                if db_client.collections.exists("Question"):

                    questions = db_client.collections.create(
                        name="Question",
                        vector_config=Configure.Vectors.text2vec_openai(
                            base_url="http://host.docker.internal:8082",
                            model="qwen3-4b-embedding",
                        ),
                    )

                    # Chat loop
                    messages = [
                        {"role": "system", "content": search_system_prompt},
                        {"role": "user", "content": question}
                    ]

                    # Call OpenAI to get search results
                    search_response = search_client.chat.completions.create(
                        model="local-model",
                        messages=messages,
                        tools=openai_tools,
                    )

                    assistant_message = search_response.choices[0].message
                    messages.append(assistant_message)

                    # Check if OpenAI wants to call a tool
                    search_results = []
                    for tool_call in assistant_message.tool_calls:
                        func_name = tool_call.function.name
                        func_args = json.loads(tool_call.function.arguments)

                        print(f"-> OpenAI requested tool: {func_name} with args {func_args}")

                        # Execute the tool call on the MCP Server
                        result = await session.call_tool(func_name, arguments=func_args)

                        # Extract text content from MCP result (already in JSON format)
                        result_text = "".join([c.text for c in result.content if hasattr(c, 'text')])

                        print(f"-> MCP Result: {result_text[:100]}...")

                        # Parse the search results directly from MCP response
                        search_results = json.loads(result_text)
                        if isinstance(search_results, dict):
                            search_results = [search_results]

                        # Feed the result back to OpenAI
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text
                        })

                    # Skip asking LLM to reformat - use raw results directly
                    print(f"\nParsed {len(search_results)} items from search results.")

                    # Perform reliability analysis on search results
                    reliability_response = search_client.chat.completions.create(
                        model="local-model",
                        messages=[
                            {"role": "system", "content": reliability_prompt},
                            {"role": "user", "content": json.dumps(search_results)}
                        ],
                        tools=openai_tools,
                    )

                    reliability_message = reliability_response.choices[0].message
    

                    reliability_data = json.loads(reliability_message.content)
                    print(f"\nReliability Analysis completed.")

                    # Create URL -> reliability score mapping
                    reliability_map = {r["url"]: r["score"] for r in reliability_data.get("rankings", [])}

                    # Perform urgency analysis for each result
                    print(f"Analyzing urgency for {len(search_results)} items...")
                    data_list = []

                    for item in search_results:
                        urgency_response = search_client.chat.completions.create(
                            model="local-model",
                            messages=[
                                {"role": "system", "content": urgency_prompt},
                                {"role": "user", "content": f"Analyze urgency for: {json.dumps(item)}"}
                            ],
                            tools=openai_tools,
                        )

                        urgency_message = urgency_response.choices[0].message

                        urgency_data = json.loads(urgency_message.content)

                        # Merge reliability score
                        item_url = item.get("url")
                        reliability_score = reliability_map.get(item_url, 5)  # Default to 5 if not found

                        data_list.append({
                            "title": item.get("title"),
                            "url": item_url,
                            "snippet": item.get("snippet"),
                            "date": item.get("date"),
                            "urgency_score": urgency_data.get("urgency_score", 0),
                            "reliability_score": reliability_score,
                            "total_score": float(reliability_score) * float(urgency_data.get("urgency_score", 0)),
                            "top_urgency_indicators": urgency_data.get("top_urgency_indicators", [])
                        })

                    # Load into Weaviate
                    print(f"Loading {len(data_list)} items into Weaviate...")
                    with questions.batch.dynamic() as batch:
                        for d in data_list:
                            if not d.get("url"):
                                continue

                            object_id = generate_uuid5(d["url"])

                            batch.add_object(
                                properties={
                                    "title": d.get("title", "No Title"),
                                    "url": d["url"],
                                    "snippet": d.get("snippet", ""),
                                    "date": d.get("date"),
                                    "urgency_score": d["urgency_score"],
                                    "reliability_score": d["reliability_score"],
                                    "total_score": d["total_score"],
                                    "top_indicators": d.get("top_urgency_indicators", [])
                                },
                                uuid=object_id
                            )

                            if batch.number_errors > 10:
                                print("Batch import stopped due to excessive errors.")
                                break

                    failed_objects = questions.batch.failed_objects
                    if failed_objects:
                        print(f"Number of failed imports: {len(failed_objects)}")
                        print(f"First failed object: {failed_objects[0]}")

                    # Query results
                    response = questions.query.near_text(query=question, limit=2)
                    print(f"\nTop results for '{question}':")
                    for obj in response.objects:
                        print(json.dumps(obj.properties, indent=2))
                else:
                    print("Weaviate collection 'Question' does not exist. Please create it before running the chat loop.")

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

            finally:
                db_client.close()


if __name__ == "__main__":
        asyncio.run(run_chat_loop())
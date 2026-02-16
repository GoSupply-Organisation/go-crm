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



async def execute_tool_call(session, tool_call, timeout=90.0): # Add timeout param
    """Execute a single tool call with a timeout."""
    func_name = tool_call.function.name
    func_args = json.loads(tool_call.function.arguments)

    try:
        # Wrap the call in a timeout
        result = await asyncio.wait_for(
            session.call_tool(func_name, arguments=func_args), 
            timeout=timeout
        )
        
        result_text = "".join([c.text for c in result.content if hasattr(c, 'text')])
        return result_text
    except asyncio.TimeoutError:
        print(f"Timeout: {func_name} took too long.")
        return f"Error: Tool execution timed out after {timeout} seconds."
    except Exception as e:
        print(f"Tool call failed for {func_name}: {e}")
        return f"Error: Tool execution failed: {str(e)}"

async def llm_with_tools(client, model, messages, tools, session):
    """
    Execute LLM calls with tool support.
    Returns the final content after handling all tool calls.
    """
    max_iterations = 10  # Limit tool calls to prevent infinite loops
    iteration = 0

    while iteration < max_iterations:
        response = search_client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
        )

        message = response.choices[0].message
        messages.append(message)

        # If no tool calls, return the content
        if not message.tool_calls:
            return message.content

        # Execute tool calls
        for tool_call in message.tool_calls:
            func_name = tool_call.function.name
            print(f"-> Tool: {func_name}")

            result_text = await execute_tool_call(session, tool_call, timeout=90.0)

            # Truncate result to prevent context overflow
            if len(result_text) > 2000:
                result_text = result_text[:2000] + "... [truncated]"

            print(f"-> Result length: {len(result_text)} chars")

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result_text
            })

        iteration += 1

    # Return whatever content we have after max iterations
    return message.content if message.content else '{"error": "Max tool iterations reached"}'


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
                    db_client.collections.delete("Question")

                    questions = db_client.collections.create(
                        name="Question",
                        vector_config=Configure.Vectors.text2vec_openai(
                            base_url="http://host.docker.internal:8082",
                            model="qwen3-4b-embedding",
                        ),
                    )

                    # Phase 1: Search
                    print("\n=== PHASE 1: SEARCH ===")
                    messages = [
                        {"role": "system", "content": search_system_prompt},
                        {"role": "user", "content": question}
                    ]

                    search_response = search_client.chat.completions.create(
                        model="local-model",
                        messages=messages,
                        tools=openai_tools,
                    )

                    assistant_message = search_response.choices[0].message
                    messages.append(assistant_message)

                    # Execute search tools
                    search_results = []
                    for tool_call in assistant_message.tool_calls:
                        print(f"-> Search tool: {tool_call.function.name}")
                        result = await session.call_tool(tool_call.function.name, arguments=json.loads(tool_call.function.arguments))
                        result_text = "".join([c.text for c in result.content if hasattr(c, 'text')])
                        search_results = json.loads(result_text)
                        if isinstance(search_results, dict):
                            search_results = [search_results]
                        print(f"-> Found {len(search_results)} results")

                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": result_text
                        })

                    # Phase 2: Reliability Analysis
                    print("\n=== PHASE 2: RELIABILITY ANALYSIS ===")
                    reliability_messages = [
                        {"role": "system", "content": reliability_prompt},
                        {"role": "user", "content": json.dumps(search_results)}
                    ]

                    reliability_content = await llm_with_tools(
                        search_client, "local-model", reliability_messages, openai_tools, session
                    )
                    reliability_data = json.loads(reliability_content)
                    print(f"Reliability analysis completed. Rated {len(reliability_data.get('rankings', []))} items.")

                    # Create URL -> reliability score mapping
                    reliability_map = {r["url"]: r["score"] for r in reliability_data.get("rankings", [])}

                    # Phase 3: Urgency Analysis
                    print("\n=== PHASE 3: URGENCY ANALYSIS ===")
                    data_list = []

                    for idx, item in enumerate(search_results, 1):
                        print(f"\n[{idx}/{len(search_results)}] Analyzing: {item.get('title', 'unknown')[:50]}...")

                        urgency_messages = [
                            {"role": "system", "content": urgency_prompt},
                            {"role": "user", "content": f"Analyze urgency for: {json.dumps(item)}"}
                        ]

                        urgency_content = await llm_with_tools(
                            search_client, "local-model", urgency_messages, openai_tools, session
                        )
                        urgency_data = json.loads(urgency_content)

                        # Merge reliability score
                        item_url = item.get("url")
                        reliability_score = reliability_map.get(item_url, 5)

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
                        print(f"  Urgency: {urgency_data.get('urgency_score', 0)}, Reliability: {reliability_score}, Total: {data_list[-1]['total_score']}")

                    # Phase 4: Load into Weaviate
                    print("\n=== PHASE 4: LOAD TO DB ===")
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

                    # Phase 5: Query from DB
                    print("\n=== PHASE 5: QUERY FROM DB ===")
                    response = questions.query.near_text(query=question, limit=2)
                    print(f"Top results for '{question}':")
                    for obj in response.objects:
                        print(json.dumps(obj.properties, indent=2))

                else:
                    print("Weaviate collection 'Question' does not exist.")

            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

            finally:
                db_client.close()


if __name__ == "__main__":
    asyncio.run(run_chat_loop())

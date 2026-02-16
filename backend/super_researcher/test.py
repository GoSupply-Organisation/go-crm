from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from prompting import search_system_prompt
import json
import weaviate
from weaviate.classes.config import Configure

client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)

llm_client = OpenAI(
    base_url="http://127.0.0.1:8082/v1",
    api_key="sk-no-key-required"
)


server_params = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
    env= None
)


def get_embedding(text):
    try:
        response = llm_client.embeddings.create(
            input=text,
            model="qwen3-4b-embedding"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

async def run_chat_loop():
    print("Starting MCP Server (DuckDuckGo)...")
    
    # 2. Start the MCP Server as a subprocess
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. Discover tools from MCP and convert to OpenAI format
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

            # Chat loop
            messages = [
                {"role": "system", "content": search_system_prompt},
                {"role": "user", "content": "What is the latest news on the stock market?"}
            ]
            
            # 4. Call OpenAI
            response = client.chat.completions.create(
                model="local-model",
                messages=messages,
                tools=openai_tools,
            )
            
            assistant_message = response.choices[0].message
            messages.append(assistant_message)

            # 5. Check if OpenAI wants to call a tool
            try: 
                for tool_call in assistant_message.tool_calls:
                    func_name = tool_call.function.name
                    func_args = json.loads(tool_call.function.arguments)
                    
                    print(f"-> OpenAI requested tool: {func_name} with args {func_args}")
                    
                    # 6. Execute the tool call on the MCP Server
                    result = await session.call_tool(func_name, arguments=func_args)
                    
                    # MCP returns a list of content blocks (text, images, etc.)
                    # We assume text content for this integration
                    result_text = "".join([c.text for c in result.content if hasattr(c, 'text')])
                    
                    print(f"-> MCP Result: {result_text[:100]}...")

                    # 7. Feed the result back to OpenAI
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": result_text
                    })
                
                # 8. Ask OpenAI to generate the final answer based on tool result
                final_response = client.chat.completions.create(
                    model="local-model",
                    messages=messages,
                    tools=openai_tools,
                )
                
                final_message = final_response.choices[0].message
                print(f"\nAssistant: {final_message.content}")
                messages.append(final_message)
                db_client = weaviate.connect_to_local(
                    headers={
                        "X-OpenAI-Api-Key": "sk-no-key-required"
                    }
                )

                if db_client.collections.exists("Question"):
                    db_client.collections.delete("Question") # Clean slate for this example

                questions = db_client.collections.create(
                    name="Question",
                    vector_config=Configure.Vectors.text2vec_openai(
                        base_url="http://host.docker.internal:8082",
                        model="qwen3-4b-embedding",
                    ),
                )


                data_list = json.loads(final_message.content)

                # Handle both single object and list of objects
                if isinstance(data_list, dict):
                    data_list = [data_list]

                print(f"Parsed {len(data_list)} items from OpenAI response.")
                print(data_list[:2])  # Print first 2 items for verification

                if db_client.collections.exists("Article"):
                    db_client.collections.delete("Article") # Clean slate for this example
                
                print("loading into weaviate")
                with questions.batch.dynamic() as batch:
                    for d in data_list:
                        batch.add_object(
                            {
                                "title": d["title"],
                                "url": d["url"],
                                "snippet": d["snippet"],
                                "date": d["date"],
                            }
                        )
                        if batch.number_errors > 10:
                            print("Batch import stopped due to excessive errors.")
                            break
                    
                failed_objects = questions.batch.failed_objects
                if failed_objects:
                    print(f"Number of failed imports: {len(failed_objects)}")
                    print(f"First failed object: {failed_objects[0]}")

                response = questions.query.near_text(query="", limit=2)

                for obj in response.objects:
                    print(json.dumps(obj.properties, indent=2))


            except Exception as e:
                print(f"  Search error: {e}")
                db_client.close()

            finally:
                db_client.close()


if __name__ == "__main__":
        asyncio.run(run_chat_loop())
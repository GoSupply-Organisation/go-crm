from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
from prompting import search_system_prompt
import json
client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)

server_params = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
    env= None
)

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
            if assistant_message.tool_calls:
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
            else:
                # No tool call, just standard reply
                print(f"\nAssistant: {assistant_message.content}")

if __name__ == "__main__":
    # Ensure you have OPENAI_API_KEY set in your environment
        asyncio.run(run_chat_loop())
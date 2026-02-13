from pydantic import BaseModel, Field
import asyncio
import json
import os
from openai import OpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from prompting import reliability_prompt
from datetime import datetime   

current_datetime = datetime.now()   

print(current_datetime.time())


reasoning_client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)
async def run_chat():
    # 1. Initialize OpenAI Client
    # 2. Configure the MCP Server (DuckDuckGo)
    # We assume 'duckduckgo-mcp' is installed and in the path
    server_params = StdioServerParameters(
        command="uvx",
        args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"], # Add any args if the specific tool requires them
    )

    class ToolCall(BaseModel):
        content: str
        link: str

    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 3. List Tools from MCP Server
            tools_list = await session.list_tools()
            print(f"Found {len(tools_list.tools)} tools:")
            
            # 4. Convert MCP Tools to OpenAI Tool Schema
            openai_tools = []
            for tool in tools_list.tools:
                print(f"- {tool.name}: {tool.description}")
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            # 5. Start the conversation loop
            messages = [
                {"role": "user", "content": "What is the latest news on the stock market, the date today is the 13th of feburary 2026"}
            ]

            # First call to OpenAI
            response = reasoning_client.chat.completions.create(
                model="local-model",
                messages=messages,
                temperature=0.4,
                tools=openai_tools,
                tool_choice="auto", 
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "ToolCall",
                        "description": "A structured response containing content and a link",
                        "schema": ToolCall.model_json_schema(),
                        "strict": True
                    }
                }            
                )

            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # 6. Handle Tool Calls (Agentic Loop)
            # If the model wants to call a tool, we execute it and send the result back
            while tool_calls:
                print(f"OpenAI wants to call tools: {[tc.function.name for tc in tool_calls]}")
                
                # Append the model's request to history
                messages.append(response_message)

                # Process each tool call
                for tool_call in tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    print(f"Executing MCP Tool: {function_name} with args {function_args}")

                    # Call the MCP Tool
                    result = await session.call_tool(function_name, arguments=function_args)
                    
                    # Extract text content from MCP result
                    # MCP returns a list of content blocks (TextContent, ImageContent, etc.)
                    # We assume text for this example
                    result_text = ""
                    for content in result.content:
                        if content.type == 'text':
                            result_text += content.text

                    print(f"Tool Result Snippet: {result_text[:100]}...")

                    # Append the tool result to messages for OpenAI
                    messages.append({
                        "tool_call_id": tool_call.id,
                        "role": "tool",
                        "name": function_name,
                        "content": result_text,
                    })

                response = reasoning_client.chat.completions.create(
                    model="local-model",
                    messages=messages,
                )
                
                # Update variables for the loop check
                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

            # 7. Print Final Answer
            print("\n--- Final Response ---")
            print(response_message.content)


            messages = [
                {"role": "system", "content": reliability_prompt},
                {"role": "user", "content": response_message.content}
            ]

            # This ranks the reliablity and urgency of the news articles and returns a prioritized list.
            reliablity = reasoning_client.chat.completions.create(
                model="local-model",
                messages=messages,
                temperature=0.1
            )

            print("\n--- News Scores ---")
            print(reliablity.choices[0].message.content)






if __name__ == "__main__":
    asyncio.run(run_chat())
    
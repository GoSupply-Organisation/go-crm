import asyncio
import json
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from prompting import reliability_prompt, urgency_prompt, search_system_prompt, question
# import weaviate

# ── WEAVIATE CONFIG ───────────────────────────────────
# weaviate_client = weaviate.connect_to_local()

# ── YOUR INFERENCE ENGINE ──────────────────────────────
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required",
)

embed = AsyncOpenAI(
    base_url="http://127.0.0.1:8082/v1",
    api_key="sk-no-key-required",
)
# ── MCP SERVER CONFIG ──────────────────────────────────
MCP_PARAMS = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
)

# ── HELPER: CONVERT MCP TOOLS TO OPENAI ───────────────────
async def get_openai_tools(session: ClientSession):
    """Fetches tools from the active MCP session and converts schema."""
    mcp_tools = await session.list_tools()
    return [
        {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": tool.inputSchema,
            }
        }
        for tool in mcp_tools.tools
    ]

# ── RELIABILITY AGENT (REFACTORED) ──────────────────────
async def reliability_agent(search_query: str) -> dict:
    """
    Intakes search query -> searches web -> returns reliability rankings.
    """
    # 1. Open the connection and KEEP it open for the whole function
    async with stdio_client(MCP_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            # 2. Get tools
            openai_tools = await get_openai_tools(session)
            
            messages = [
                {"role": "system", "content": f"{search_system_prompt}\n\n{reliability_prompt}"},
                {"role": "user", "content": search_query}
            ]

            # 3. AGENTIC LOOP: Think -> Act -> Observe -> Repeat
            while True:
                response = await client.chat.completions.create(
                    model="glm-5",
                    tools=openai_tools,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000,
                )

                message = response.choices[0].message
                
                # 4. Check if LLM wants to use tools
                if message.tool_calls:
                    # Append the assistant's decision to history
                    messages.append(message)
                    
                    # Execute each tool call
                    for tool_call in message.tool_calls:
                        print(f"🔧 Calling Tool: {tool_call.function.name}")
                        
                        # Execute via MCP
                        result = await session.call_tool(
                            tool_call.function.name, 
                            arguments=json.loads(tool_call.function.arguments)
                        )
                        
                        # Append tool result to history
                        # Note: MCP returns content as a list, we take the text
                        tool_content = result.content[0].text if result.content else ""
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_content
                        })
                    
                    # Loop back to LLM with the new search results
                    continue 
                
                else:
                    # 5. No tool calls: LLM is done. Return content.
                    try:
                        print(json.loads(message.content))
                        return json.loads(message.content)
                    except json.JSONDecodeError:
                        return {"raw_response": message.content}

# ── URGENCY AGENT (REFACTORED) ──────────────────────────
async def urgency_agent(reliability_data: dict) -> dict:
    """
    Intakes reliability data -> analyzes urgency via web search.
    """
    context = json.dumps(reliability_data, indent=2)

    # 1. Open connection
    async with stdio_client(MCP_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            openai_tools = await get_openai_tools(session)
            
            messages = [
                {"role": "system", "content": urgency_prompt},
                {"role": "user", "content": f"Analyze the urgency of these findings:\n\n{context}"}
            ]

            # 2. AGENTIC LOOP
            while True:
                response = await client.chat.completions.create(
                    model="glm-5",
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000,
                    tools=openai_tools
                )

                message = response.choices[0].message

                if message.tool_calls:
                    messages.append(message)
                    for tool_call in message.tool_calls:
                        print(f"🔧 Calling Tool: {tool_call.function.name}")
                        
                        result = await session.call_tool(
                            tool_call.function.name, 
                            arguments=json.loads(tool_call.function.arguments)
                        )
                        
                        tool_content = result.content[0].text if result.content else ""
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": tool_content
                        })
                    continue
                
                else:
                    try:
                        print(json.loads(message.content))
                        return json.loads(message.content)
                    except json.JSONDecodeError:
                        return {"raw_response": message.content}

# ── MAIN PIPELINE ──────────────────────────────────────
async def run_pipeline(search_query: str):
    """
    Full pipeline that:
    1. Starts with a search query
    2. Reliability agent searches and evaluates sources
    3. Urgency agent analyzes urgency based on findings
    """
    print("🔍 Initializing Pipeline...")

    print("\n" + "="*60)
    print("📊 STAGE 1: Reliability Agent")
    print("="*60)
    reliability_output = await reliability_agent(search_query)
    print(json.dumps(reliability_output, indent=2))

    for r_item in reliability_output['rankings']:
        score = r_item['score']
        url = r_item['url']
        verification = r_item['verification_method']

        print(f"Found Score: {score} for URL: {url} (Verification: {verification})")

    print("\n" + "="*60)
    print("⚡ STAGE 2: Urgency Agent")
    print("="*60)
    urgency_output = await urgency_agent(reliability_output)
    print(json.dumps(urgency_output, indent=2)) 

    for u_item in urgency_output:
        u_score = u_item['urgency_score']
        indicators = u_item['top_urgency_indicators']
        summary = u_item['summary']
        print(f"Urgency Score: {u_score} (Top Indicators: {indicators})")
        print(f"Summary: {summary}")

    return {
        "search_query": search_query,
        "reliability": reliability_output,
        "urgency": urgency_output
    }

# ── RUN EXAMPLE ────────────────────────────────────────
if __name__ == "__main__":
    search_query = question
    result = asyncio.run(run_pipeline(search_query))

    print("\n" + "="*60)
    print("📋 FINAL REPORT")
    print("="*60)
    print(json.dumps(result, indent=2))


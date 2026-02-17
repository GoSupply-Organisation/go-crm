import asyncio
import json
from openai import AsyncOpenAI
from mcp.client.stdio import stdio_client
from mcp import ClientSession, StdioServerParameters
from prompting import reliability_prompt, urgency_prompt, search_system_prompt, question

# ── YOUR INFERENCE ENGINE ──────────────────────────────
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key",
)

# ── MCP SERVER CONFIG ──────────────────────────────────
MCP_PARAMS = StdioServerParameters(
    command="python",
    args=["server.py"],
    cwd="/Users/zacharyaldin/Coding/Go-crm/backend/super_researcher"
)

# ── MCP TOOLS INTEGRATION ──────────────────────────────
async def get_mcp_tools():
    """Connect to MCP server and get available tools in OpenAI format"""
    async with stdio_client(MCP_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # Get tools from MCP server
            tools_result = await session.list_tools()

            # Convert MCP tools to OpenAI format
            openai_tools = []
            for tool in tools_result.tools:
                openai_tools.append({
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                })

            return openai_tools, session

# ── TOOL EXECUTION HANDLER ──────────────────────────────
async def execute_tool_call(tool_call, session):
    """Execute a tool call via MCP session and return the result"""
    try:
        result = await session.call_tool(
            tool_call.function.name,
            json.loads(tool_call.function.arguments)
        )
        # Extract content from MCP result
        if result.content:
            return result.content[0].text if hasattr(result.content[0], 'text') else str(result.content[0])
        return str(result) 
    except Exception as e:
        return f"Error executing tool {tool_call.function.name}: {str(e)}"

# ── RELIABILITY AGENT (WITH TOOL ACCESS) ────────────────
async def reliability_agent(search_query: str, tools: list, session) -> dict:
    """
    Intakes search query → searches web → returns reliability rankings.
    Has direct access to MCP tools.
    """
    messages = [
        {"role": "system", "content": f"{search_system_prompt}\n\n{reliability_prompt}"},
        {"role": "user", "content": search_query}
    ]

    max_iterations = 5
    for iteration in range(max_iterations):
        response = await client.chat.completions.create(
            model="local-model",
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            tools=tools
        )

        message = response.choices[0].message

        # If no tool calls, we're done
        if not message.tool_calls:
            break

        # Execute each tool call and append results
        for tool_call in message.tool_calls:
            result = await execute_tool_call(tool_call, session)
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    # Extract final JSON response
    final_response = message.content
    final_response = final_response.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(final_response)
    except json.JSONDecodeError:
        # Fallback: return raw content if JSON parsing fails
        return {"raw_response": final_response}

# ── URGENCY AGENT (WITH TOOL ACCESS) ────────────────────
async def urgency_agent(reliability_data: dict, tools: list, session) -> dict:
    """
    Intakes reliability data → analyzes urgency via web search.
    Has direct access to MCP tools.
    """
    # Build context from reliability data
    context = json.dumps(reliability_data, indent=2)

    messages = [
        {"role": "system", "content": urgency_prompt},
        {"role": "user", "content": f"Analyze the urgency of these findings:\n\n{context}"}
    ]

    max_iterations = 5
    for iteration in range(max_iterations):
        response = await client.chat.completions.create(
            model="local-model",
            messages=messages,
            temperature=0.1,
            max_tokens=2000,
            tools=tools
        )

        message = response.choices[0].message

        # If no tool calls, we're done
        if not message.tool_calls:
            break

        # Execute each tool call and append results
        for tool_call in message.tool_calls:
            result = await execute_tool_call(tool_call, session)
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [tool_call]
            })
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": result
            })

    # Extract final JSON response
    final_response = message.content
    final_response = final_response.replace("```json", "").replace("```", "").strip()

    try:
        return json.loads(final_response)
    except json.JSONDecodeError:
        return {"raw_response": final_response}

# ── MAIN PIPELINE ──────────────────────────────────────
async def run_pipeline(search_query: str):
    """
    Full pipeline that:
    1. Starts with a search query
    2. Reliability agent searches and evaluates sources
    3. Urgency agent analyzes urgency based on findings
    """
    print("🔍 Initializing MCP connection...")
    tools, session = await get_mcp_tools()
    print(f"✅ Loaded {len(tools)} tools: {[t['function']['name'] for t in tools]}")

    print("\n" + "="*60)
    print("📊 STAGE 1: Reliability Agent")
    print("="*60)
    reliability_output = await reliability_agent(search_query, tools, session)
    print(json.dumps(reliability_output, indent=2))

    print("\n" + "="*60)
    print("⚡ STAGE 2: Urgency Agent")
    print("="*60)
    urgency_output = await urgency_agent(reliability_output, tools, session)
    print(json.dumps(urgency_output, indent=2))

    return {
        "search_query": search_query,
        "reliability": reliability_output,
        "urgency": urgency_output
    }

# ── RUN EXAMPLE ────────────────────────────────────────
if __name__ == "__main__":
    # The pipeline will do the searching - just provide a query
    search_query = question

    result = asyncio.run(run_pipeline(search_query))

    print("\n" + "="*60)
    print("📋 FINAL REPORT")
    print("="*60)
    print(json.dumps(result, indent=2))

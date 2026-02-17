import asyncio
import json
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from prompting import reliability_prompt, urgency_prompt, search_system_prompt, question

# ── YOUR INFERENCE ENGINE ──────────────────────────────
client = AsyncOpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key",
)

# ── MCP SERVER CONFIG ──────────────────────────────────
MCP_PARAMS = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
)
async def mcp_tool_assess(params: StdioServerParameters):
    async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                # Initialize the connection
                await session.initialize()
                
                # 3. "Plug & Play": Get the tools automatically from the server
                mcp_tools = await session.list_tools()
                
                # Convert MCP tools to OpenAI tool format
                openai_tools = [
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

# ── RELIABILITY AGENT (WITH TOOL ACCESS) ────────────────
async def reliability_agent(search_query: str) -> dict:
    """
    Intakes search query → searches web → returns reliability rankings.
    Has direct access to MCP tools.
    """
    messages = [
        {"role": "system", "content": f"{search_system_prompt}\n\n{reliability_prompt}"},
        {"role": "user", "content": search_query}
    ]
    openai_tools = await mcp_tool_assess(MCP_PARAMS)

    response = await client.chat.completions.create(
                model="local-model",
                tools = openai_tools,
                messages=messages,
                temperature=0.1,
                max_tokens=2000,
            )

    message = response.choices[0].message
    try:
        return json.loads(message.content)
    except json.JSONDecodeError:
        # Fallback: return raw content if JSON parsing fails
        return {"raw_response": message.content}

# ── URGENCY AGENT (WITH TOOL ACCESS) ────────────────────
async def urgency_agent(reliability_data: dict) -> dict:
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

    response = await client.chat.completions.create(
        model="local-model",
        messages=messages,
        temperature=0.1,
        max_tokens=2000,
        tools = await mcp_tool_assess(MCP_PARAMS)
    )

    message = response.choices[0].message

    try:
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
    print("🔍 Initializing MCP connection...")

    print("\n" + "="*60)
    print("📊 STAGE 1: Reliability Agent")
    print("="*60)
    reliability_output = await reliability_agent(search_query)
    print(json.dumps(reliability_output, indent=2))

    print("\n" + "="*60)
    print("⚡ STAGE 2: Urgency Agent")
    print("="*60)
    urgency_output = await urgency_agent(reliability_output)
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

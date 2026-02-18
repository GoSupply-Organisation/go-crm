from decouple import config
import asyncio
import json
import weaviate
from weaviate.classes.config import Configure
from weaviate.util import generate_uuid5
from openai import AsyncOpenAI
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from prompting import reliability_prompt, urgency_prompt, search_system_prompt, question

# ── YOUR INFERENCE ENGINE ──────────────────────────────
# client = AsyncOpenAI(
    # base_url="http://127.0.0.1:8081/v1",
    # api_key="sk-no-key-required",
# )

# embed = AsyncOpenAI(
    # base_url="http://127.0.0.1:8082/v1",
    # api_key="sk-no-key-required",
# )

client = AsyncOpenAI(
    base_url=config("GLM_BASE_URL"),
    api_key=config("GLM_API_KEY"),
)

embed = AsyncOpenAI(
    api_key=config("OPENAI_API_KEY"),
)

# ── MCP SERVER CONFIG ──────────────────────────────────
MCP_PARAMS = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
)

# ── EMBEDDING FUNCTION ──────────────────────────────────────
def get_embedding(text):
    try:
        response = embed.embeddings.create(
            input=text,
            model="text-embedding-3-large"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None

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

# ── RELIABILITY AGENT ──────────────────────────────
async def reliability_agent(search_query: str) -> dict:
    """
    Intakes search query -> searches web -> returns reliability rankings.
    """
    async with stdio_client(MCP_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            openai_tools = await get_openai_tools(session)
            
            messages = [
                {"role": "system", "content": f"{search_system_prompt}\n\n{reliability_prompt}"},
                {"role": "user", "content": search_query}
            ]

            while True:
                response = await client.chat.completions.create(
                    model="glm-5",
                    tools=openai_tools,
                    messages=messages,
                    temperature=0.1,
                    max_tokens=2000,
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
                        return json.loads(message.content)
                    except json.JSONDecodeError:
                        return {"raw_response": message.content}

# ── URGENCY AGENT ──────────────────────────────────
async def urgency_agent(reliability_data: dict) -> list:
    """
    Intakes reliability data -> analyzes urgency via web search.
    """
    context = json.dumps(reliability_data, indent=2)

    async with stdio_client(MCP_PARAMS) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            openai_tools = await get_openai_tools(session)
            
            messages = [
                {"role": "system", "content": urgency_prompt},
                {"role": "user", "content": f"Analyze the urgency of these findings:\n\n{context}"}
            ]

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
                        # Expecting a list of items
                        return json.loads(message.content)
                    except json.JSONDecodeError:
                        return [{"raw_response": message.content}]

# ── WEAVIATE INTEGRATION ──────────────────────────────────
def save_to_weaviate(reliability_output: dict, urgency_output: list):
    """
    Connects to Weaviate, sets up schema, and inserts the processed data.
    """
    print("\n💾 Saving to Weaviate...")
    
    # 1. Connect to local Docker instance
    db_client = weaviate.connect_to_local(
        host="localhost",
        port=8080,
        headers={
            "X-OpenAI-Api-Key": "sk-no-key-required"  # Required by the vectorizer config
        }
    )

    try:
        # 2. Define Collection Name
        collection_name = "Question"

        # 3. Clean slate (Optional: comment this out to keep existing data)
        if db_client.collections.exists(collection_name):
            db_client.collections.delete(collection_name)

        # 4. Create Collection with Vectorizer
        # Note: This points to your local embedding server via Docker internal URL
        questions = db_client.collections.create(
            name=collection_name,
            vector_config=Configure.Vectors.text2vec_openai(
                base_url="http://host.docker.internal:8082",
                model="qwen3-4b-embedding",
            ),
        )

        # 5. Prepare data map for easy lookup
        # Map URL -> Reliability Score
        reliability_map = {
            r_item['url']: r_item['score'] 
            for r_item in reliability_output.get('rankings', [])
        }

        # 6. Insert Data
        print(f"Loading {len(urgency_output)} items into Weaviate...")
        
        with questions.batch.dynamic() as batch:
            for item in urgency_output:
                url = item.get("url")
                u_score = item.get("urgency_score", 0)
                # Look up reliability score, default to 0 if not found
                r_score = reliability_map.get(url, 0)
                
                total_score = float(r_score) * float(u_score)

                # Generate deterministic UUID based on URL
                object_id = generate_uuid5(url)

                batch.add_object(
                    properties={
                        "title": item.get("title", "No Title"),
                        "url": url,
                        "snippet": item.get("snippet", ""),
                        "date": item.get("date"), 
                        "urgency_score": u_score,
                        "reliability_score": r_score,
                        "total_score": total_score,
                        "top_indicators": item.get("top_urgency_indicators", [])
                    },
                    uuid=object_id
                )
                
            if batch.number_errors > 10:
                print("Batch import stopped due to excessive errors.")
                failed_objects = questions.batch.failed_objects
                print(f"First failed object: {failed_objects[0]}")

        print(f"✅ Successfully inserted {len(urgency_output)} objects.")

        # 7. Verify (Optional)
        response = questions.query.near_text(query="stock market", limit=2)
        print("\n🔎 Verification Query Results:")
        for obj in response.objects:
            print(json.dumps(obj.properties, indent=2))

    except Exception as e:
        print(f"❌ Weaviate Error: {e}")
    finally:
        db_client.close()

# ── MAIN PIPELINE ──────────────────────────────────────
async def run_pipeline(search_query: str):
    """
    Full pipeline that:
    1. Starts with a search query
    2. Reliability agent searches and evaluates sources
    3. Urgency agent analyzes urgency based on findings
    4. Saves combined results to Weaviate
    """
    print("🔍 Initializing Pipeline...")

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

    # ── SAVE TO WEAVIATE ─────────────────────────────
    if urgency_output:
        save_to_weaviate(reliability_output, urgency_output)
    else:
        print("No urgency data to save.")

    # Return final aggregated data
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
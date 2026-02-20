from decouple import config
import asyncio
import json
import requests
import weaviate
from weaviate.classes.config import Configure
from weaviate.util import generate_uuid5
from weaviate.classes.query import Sort 
from openai import AsyncOpenAI
from prompting import reliability_prompt, urgency_prompt, search_system_prompt, question

# ── YOUR INFERENCE ENGINE ──────────────────────────────
client = AsyncOpenAI(
    base_url=config("GLM_BASE_URL"),
    api_key=config("GLM_API_KEY"),
)

embed = AsyncOpenAI(
    api_key=config("OPENAI_API_KEY"),
)

# client = AsyncOpenAI(
#     base_url="",
#     api_key="",)

# embed = AsyncOpenAI(
#     base_url="",
#     api_key="",
#     )

# ── SERPER CONFIG ──────────────────────────────────────
SERPER_API_KEY = config("SERPER_API_KEY")

# ── TOOL DEFINITIONS ───────────────────────────────────
def google_search(query):
    """
    Performs a Google search using the Serper API.
    """
    url = "https://google.serper.dev/search"
    payload = json.dumps({"q": query})
    headers = {
        'X-API-KEY': SERPER_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()
        return response.text
    except Exception as e:
        return json.dumps({"error": str(e)})

# Schema for the LLM to understand the tool
OPENAI_TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "google_search",
            "description": "Search Google for real-time information, current events, or specific data.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on Google",
                    }
                },
                "required": ["query"],
            },
        },
    }
]

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

# ── RELIABILITY AGENT ──────────────────────────────
async def reliability_agent(search_query: str, recent_context) -> dict:
    """
    Intakes search query -> searches web -> returns reliability rankings.
    """
    messages = [
        {"role": "system", "content": f"{search_system_prompt}\n\n{reliability_prompt}\n\n{recent_context}"},
        {"role": "user", "content": search_query}
    ]

    max_tool_calls = 12
    tool_call_count = 0

    while tool_call_count < max_tool_calls:
        response = await client.chat.completions.create(
            model="glm-4.7-flash",
            tools=OPENAI_TOOLS,
            messages=messages,
            temperature=0.7,
            max_tokens=16000,
            frequency_penalty=0.5,
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                print(f"🔧 Calling Tool: {tool_call.function.name}")
                
                # Execute the tool locally
                if tool_call.function.name == "google_search":
                    args = json.loads(tool_call.function.arguments)
                    tool_content = google_search(args["query"])
                else:
                    tool_content = "Error: Unknown tool"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content
                })
            
            tool_call_count += 1
            continue
        else:
            try:
                return json.loads(message.content)
            except json.JSONDecodeError:
                return {"raw_response": message.content}

    print(f"⚠️  Reached maximum tool calls ({max_tool_calls}). Returning current results.")
    try:
        return json.loads(message.content)
    except json.JSONDecodeError:
        return {"rankings": [], "error": f"Max tool calls ({max_tool_calls}) reached without valid response"}

# ── URGENCY AGENT ──────────────────────────────────
async def urgency_agent(reliability_data: dict) -> list:
    """
    Intakes reliability data -> analyzes urgency via web search.
    """
    context = json.dumps(reliability_data, indent=2)

    messages = [
        {"role": "system", "content": urgency_prompt},
        {"role": "user", "content": f"Analyze the urgency of these findings:\n\n{context}"}
    ]

    max_tool_calls = 12
    tool_call_count = 0

    while tool_call_count < max_tool_calls:
        response = await client.chat.completions.create(
            model="glm-4.7-flash",
            messages=messages,
            temperature=0.7,
            max_tokens=16000,
            tools=OPENAI_TOOLS,
            frequency_penalty=0.5,
        )

        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                print(f"🔧 Calling Tool: {tool_call.function.name}")
                
                # Execute the tool locally
                if tool_call.function.name == "google_search":
                    args = json.loads(tool_call.function.arguments)
                    tool_content = google_search(args["query"])
                else:
                    tool_content = "Error: Unknown tool"

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content
                })
            
            tool_call_count += 1
            continue
        else:
            try:
                return json.loads(message.content)
            except json.JSONDecodeError:
                return [{"raw_response": message.content}]

    print("⚠️  Reached maximum search iterations. Returning current results.")
    try:
        return json.loads(message.content)
    except json.JSONDecodeError:
        return [{"error": "Max iterations reached without valid response"}]

def load_weaviate_client():
    """
    Initializes and returns a Weaviate client connected to the local instance.
    """
    return weaviate.connect_to_local(
        host="localhost",
        port=8080,
        headers={
            "X-OpenAI-Api-Key": "sk-no-key-required"
        }
    )

def get_recent_context(limit: int = 5) -> str:
    """
    Fetches the most recent results from Weaviate and formats them 
    as a context string for an LLM prompt.
    """
    client = None
    try:
        client = load_weaviate_client()
        collection = client.collections.get("Question")
        
        response = collection.query.fetch_objects(
            limit=limit,
            sort=Sort.by_property("date", ascending=False),
            return_properties=["title", "url", "snippet", "date", "total_score", "urgency_score", "reliability_score"]
        )
        
        if not response.objects:
            return "No recent data found in the database."

        context_string = "Here are the most recent findings from the database:\n\n"
        
        for i, obj in enumerate(response.objects, 1):
            props = obj.properties
            context_string += (
                f"--- Result {i} ---\n"
                f"Title: {props.get('title', 'N/A')}\n"
                f"Date: {props.get('date', 'N/A')}\n"
                f"Scores: Urgency {props.get('urgency_score', 0)} | Reliability {props.get('reliability_score', 0)} | Total {props.get('total_score', 0)}\n"
                f"Snippet: {props.get('snippet', 'N/A')}\n"
                f"URL: {props.get('url', 'N/A')}\n\n"
            )
            
        return context_string

    except Exception as e:
        return f"Error retrieving context from database: {e}"
    
    finally:
        if client:
            client.close()

# ── WEAVIATE INTEGRATION ──────────────────────────────────
def save_to_weaviate(reliability_output: dict, urgency_output: list):
    """
    Connects to Weaviate, sets up schema, and inserts the processed data.
    """
    print("\n💾 Saving to Weaviate...")
    
    db_client = load_weaviate_client()

    try:
        collection_name = "Question"

        if db_client.collections.exists(collection_name):
            db_client.collections.delete(collection_name)

        questions = db_client.collections.create(
            name=collection_name,
            vector_config=Configure.Vectors.text2vec_openai(
                base_url="http://host.docker.internal:8082",
                model="qwen3-4b-embedding",
            ),
        )

        reliability_map = {
            r_item['url']: r_item['score'] 
            for r_item in reliability_output.get('rankings', [])
        }

        print(f"Loading {len(urgency_output)} items into Weaviate...")
        
        with questions.batch.dynamic() as batch:
            for item in urgency_output:
                url = item.get("url")
                u_score = item.get("urgency_score", 0)
                r_score = reliability_map.get(url, 0)
                
                total_score = float(r_score) * float(u_score)

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

    print("Getting most recent context from Weaviate...")
    recent_context = get_recent_context()
    if recent_context and "No recent data" not in recent_context:
        print(recent_context[:100] + "...\n")
    else:
        print("No recent context found, starting fresh search.\n")

    print("\n" + "="*60)
    print("📊 STAGE 1: Reliability Agent")
    print("="*60)
    reliability_output = await reliability_agent(search_query, recent_context)
    print(json.dumps(reliability_output, indent=2))

    print("\n" + "="*60)
    print("⚡ STAGE 2: Urgency Agent")
    print("="*60)
    urgency_output = await urgency_agent(reliability_output)
    print(json.dumps(urgency_output, indent=2)) 

    if urgency_output:
        save_to_weaviate(reliability_output, urgency_output)
    else:
        print("No urgency data to save.")

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
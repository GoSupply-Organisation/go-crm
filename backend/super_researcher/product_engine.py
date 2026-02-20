from decouple import config
import asyncio
import json
import requests
import logging
import weaviate
from weaviate.classes.config import Configure
from weaviate.util import generate_uuid5
from weaviate.classes.query import Sort
from openai import AsyncOpenAI
from prompting import reliability_prompt, urgency_prompt, search_system_prompt, question

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


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
    logger.info("=" * 60)
    logger.info("📊 RELIABILITY AGENT STARTED")
    logger.info("=" * 60)
    logger.info(f"Search Query: {search_query}")
    logger.info(f"Recent Context Length: {len(recent_context)} characters")

    messages = [
        {"role": "system", "content": f"{search_system_prompt}\n\n{reliability_prompt}\n\n{recent_context}"},
        {"role": "user", "content": search_query}
    ]

    max_tool_calls = 12
    tool_call_count = 0

    logger.info(f"Starting reliability analysis with max {max_tool_calls} tool calls")

    while tool_call_count < max_tool_calls:
        logger.info(f"Iteration {tool_call_count + 1}/{max_tool_calls}")
        logger.info(f"Messages in conversation: {len(messages)}")

        response = await client.chat.completions.create(
            model="glm-5",
            tools=OPENAI_TOOLS,
            messages=messages,
            temperature=1.0,
            max_tokens=16000,
        )

        message = response.choices[0].message
        logger.info(f"LLM Response - Finish Reason: {response.choices[0].finish_reason}")
        logger.debug(f"LLM Response Content: {message.content}")

        if message.tool_calls:
            messages.append(message)
            logger.info(f"Tool calls requested: {len(message.tool_calls)}")

            for tool_call in message.tool_calls:
                logger.info(f"🔧 Tool Call #{len([tc for tc in message.tool_calls if message.tool_calls.index(tc) <= message.tool_calls.index(tool_call)])}")
                logger.info(f"   Tool Name: {tool_call.function.name}")
                logger.info(f"   Arguments: {tool_call.function.arguments}")

                # Execute the tool locally
                if tool_call.function.name == "google_search":
                    args = json.loads(tool_call.function.arguments)
                    query = args["query"]
                    logger.info(f"   Executing Google Search: {query}")
                    tool_content = google_search(args["query"])

                    try:
                        search_results = json.loads(tool_content)
                        logger.info(f"   Search returned {len(search_results.get('organic', []))} organic results")
                        logger.debug(f"   Search results snippet: {str(search_results)[:200]}...")
                    except json.JSONDecodeError:
                        logger.warning(f"   Tool response was not valid JSON: {tool_content[:100]}...")
                else:
                    tool_content = "Error: Unknown tool"
                    logger.error(f"   Unknown tool called: {tool_call.function.name}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content
                })
                logger.debug(f"   Tool result added to messages (length: {len(tool_content)})")

            tool_call_count += 1
            continue
        else:
            logger.info("No tool calls - returning final response")
            try:
                result = json.loads(message.content)
                logger.info(f"Successfully parsed JSON response with {len(result.get('rankings', []))} rankings")
                logger.debug(f"Full response: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                logger.warning(f"Response was not valid JSON, returning raw content: {message.content[:100]}...")
                return {"raw_response": message.content}

    logger.warning(f"⚠️  Reached maximum tool calls ({max_tool_calls}). Returning current results.")
    try:
        result = json.loads(message.content)
        logger.info(f"Returning partial results after max iterations: {len(result.get('rankings', []))} rankings")
        return result
    except json.JSONDecodeError:
        logger.error(f"Max iterations reached without valid JSON response")
        return {"rankings": [], "error": f"Max tool calls ({max_tool_calls}) reached without valid response"}

# ── URGENCY AGENT ──────────────────────────────────
async def urgency_agent(reliability_data: dict) -> list:
    """
    Intakes reliability data -> analyzes urgency via web search.
    """
    logger.info("=" * 60)
    logger.info("⚡ URGENCY AGENT STARTED")
    logger.info("=" * 60)
    logger.info(f"Reliability data received with {len(reliability_data.get('rankings', []))} rankings")

    context = json.dumps(reliability_data, indent=2)
    logger.debug(f"Full reliability context: {context[:500]}...")

    messages = [
        {"role": "system", "content": urgency_prompt},
        {"role": "user", "content": f"Analyze the urgency of these findings:\n\n{context}"}
    ]

    max_tool_calls = 12
    tool_call_count = 0

    logger.info(f"Starting urgency analysis with max {max_tool_calls} tool calls")

    while tool_call_count < max_tool_calls:
        logger.info(f"Iteration {tool_call_count + 1}/{max_tool_calls}")
        logger.info(f"Messages in conversation: {len(messages)}")

        response = await client.chat.completions.create(
            model="glm-5",
            messages=messages,
            temperature=1.0,
            max_tokens=16000,
            tools=OPENAI_TOOLS,
        )

        message = response.choices[0].message
        logger.info(f"LLM Response - Finish Reason: {response.choices[0].finish_reason}")
        logger.debug(f"LLM Response Content: {message.content}")

        if message.tool_calls:
            messages.append(message)
            logger.info(f"Tool calls requested: {len(message.tool_calls)}")

            for tool_call in message.tool_calls:
                logger.info(f"🔧 Tool Call #{len([tc for tc in message.tool_calls if message.tool_calls.index(tc) <= message.tool_calls.index(tool_call)])}")
                logger.info(f"   Tool Name: {tool_call.function.name}")
                logger.info(f"   Arguments: {tool_call.function.arguments}")

                # Execute the tool locally
                if tool_call.function.name == "google_search":
                    args = json.loads(tool_call.function.arguments)
                    query = args["query"]
                    logger.info(f"   Executing Google Search: {query}")
                    tool_content = google_search(args["query"])

                    try:
                        search_results = json.loads(tool_content)
                        logger.info(f"   Search returned {len(search_results.get('organic', []))} organic results")
                        logger.debug(f"   Search results snippet: {str(search_results)[:200]}...")
                    except json.JSONDecodeError:
                        logger.warning(f"   Tool response was not valid JSON: {tool_content[:100]}...")
                else:
                    tool_content = "Error: Unknown tool"
                    logger.error(f"   Unknown tool called: {tool_call.function.name}")

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": tool_content
                })
                logger.debug(f"   Tool result added to messages (length: {len(tool_content)})")

            tool_call_count += 1
            continue
        else:
            logger.info("No tool calls - returning final response")
            try:
                result = json.loads(message.content)
                logger.info(f"Successfully parsed JSON response with {len(result)} urgency items")
                logger.debug(f"Full response: {json.dumps(result, indent=2)}")
                return result
            except json.JSONDecodeError:
                logger.warning(f"Response was not valid JSON, returning raw content: {message.content[:100]}...")
                return [{"raw_response": message.content}]

    logger.warning("⚠️  Reached maximum search iterations. Returning current results.")
    try:
        result = json.loads(message.content)
        logger.info(f"Returning partial results after max iterations: {len(result)} urgency items")
        return result
    except json.JSONDecodeError:
        logger.error("Max iterations reached without valid JSON response")
        return [{"error": "Max iterations reached without valid response"}]

def load_weaviate_client():
    """
    Initializes and returns a Weaviate client connected to the local instance.
    """
    return weaviate.connect_to_local(
        host="localhost",
        port=8080,
        headers={
            "X-OpenAI-Api-Key": config("OPENAI_API_KEY")
        }
    )

def get_recent_context(limit: int = 5) -> str:
    """
    Fetches the most recent results from Weaviate and formats them
    as a context string for an LLM prompt.
    """
    logger.info(f"Fetching recent context from Weaviate (limit: {limit})")
    client = None
    try:
        client = load_weaviate_client()
        collection = client.collections.get("Question")
        logger.info("Successfully connected to Weaviate collection 'Question'")

        response = collection.query.fetch_objects(
            limit=limit,
            sort=Sort.by_property("date", ascending=False),
            return_properties=["title", "url", "snippet", "date", "total_score", "urgency_score", "reliability_score"]
        )

        if not response.objects:
            logger.info("No recent data found in the database")
            return "No recent data found in the database."

        logger.info(f"Retrieved {len(response.objects)} recent results from Weaviate")
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

        logger.debug(f"Context string generated (length: {len(context_string)} characters)")
        return context_string

    except Exception as e:
        logger.error(f"Error retrieving context from database: {e}", exc_info=True)
        return f"Error retrieving context from database: {e}"

    finally:
        if client:
            client.close()
            logger.debug("Weaviate client closed")

# ── WEAVIATE INTEGRATION ──────────────────────────────────
def save_to_weaviate(reliability_output: dict, urgency_output: list):
    """
    Connects to Weaviate, sets up schema, and inserts the processed data.
    """
    logger.info("=" * 60)
    logger.info("💾 SAVING TO WEAVIATE")
    logger.info("=" * 60)

    db_client = load_weaviate_client()

    try:
        collection_name = "Question"
        logger.info(f"Target collection: {collection_name}")

        if db_client.collections.exists(collection_name):
            logger.info(f"Collection '{collection_name}' already exists, deleting...")
            db_client.collections.delete(collection_name)

        logger.info("Creating new collection with text2vec_openai vectorizer...")
        questions = db_client.collections.create(
            name=collection_name,
            vectorizer_config=Configure.Vector.from_text2vec_openai(
                model="text-embedding-3-large",
                dimensions=3072,
            ),
        )
        logger.info("Collection created successfully")

        reliability_map = {
            r_item['url']: r_item['score']
            for r_item in reliability_output.get('rankings', [])
        }
        logger.info(f"Built reliability map with {len(reliability_map)} entries")

        logger.info(f"Loading {len(urgency_output)} items into Weaviate...")

        with questions.batch.dynamic() as batch:
            for i, item in enumerate(urgency_output, 1):
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

                if i % 5 == 0:
                    logger.info(f"Processed {i}/{len(urgency_output)} items")

            if batch.number_errors > 10:
                logger.error(f"Batch import stopped due to excessive errors ({batch.number_errors})")
                failed_objects = questions.batch.failed_objects
                logger.error(f"First failed object: {failed_objects[0]}")

        logger.info(f"✅ Successfully inserted {len(urgency_output)} objects")

        response = questions.query.near_text(query="stock market", limit=2)
        logger.info("\n🔎 Verification Query Results:")
        for obj in response.objects:
            logger.info(json.dumps(obj.properties, indent=2))

    except Exception as e:
        logger.error(f"❌ Weaviate Error: {e}", exc_info=True)
    finally:
        db_client.close()
        logger.info("Weaviate client closed")

# ── MAIN PIPELINE ──────────────────────────────────────
async def run_pipeline(search_query: str):
    """
    Full pipeline that:
    1. Starts with a search query
    2. Reliability agent searches and evaluates sources
    3. Urgency agent analyzes urgency based on findings
    4. Saves combined results to Weaviate
    """
    logger.info("=" * 60)
    logger.info("🔍 INITIALIZING PIPELINE")
    logger.info("=" * 60)
    logger.info(f"Search Query: {search_query}")

    logger.info("Getting most recent context from Weaviate...")
    recent_context = get_recent_context()
    if recent_context and "No recent data" not in recent_context:
        logger.info(f"Recent context found: {recent_context[:100]}...")
    else:
        logger.info("No recent context found, starting fresh search.")

    reliability_output = await reliability_agent(search_query, recent_context)
    logger.info(f"Reliability agent returned: {json.dumps(reliability_output, indent=2)}")

    urgency_output = await urgency_agent(reliability_output)
    logger.info(f"Urgency agent returned: {json.dumps(urgency_output, indent=2)}")

    if urgency_output:
        save_to_weaviate(reliability_output, urgency_output)
    else:
        logger.warning("No urgency data to save.")

    result = {
        "search_query": search_query,
        "reliability": reliability_output,
        "urgency": urgency_output
    }
    logger.info("=" * 60)
    logger.info("✅ PIPELINE COMPLETED")
    logger.info("=" * 60)
    return result

# ── RUN EXAMPLE ────────────────────────────────────────
if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info("📋 STARTING SUPER RESEARCHER")
    logger.info("=" * 60)

    search_query = question
    result = asyncio.run(run_pipeline(search_query))

    logger.info("=" * 60)
    logger.info("📋 FINAL REPORT")
    logger.info("=" * 60)
    logger.info(json.dumps(result, indent=2))
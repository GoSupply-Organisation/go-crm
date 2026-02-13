import time
import asyncio
from qdrant_client import QdrantClient, models
from openai import OpenAI
import uuid
import hashlib
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Setup Qdrant Client
host = "localhost"
port = 7333
collection_name = "news"
vector_size = 2560
distance_metric = models.Distance.COSINE
qdrant_client = QdrantClient(host=host, port=port)


def content_id(text):
    return str(uuid.UUID(hashlib.md5(text.encode()).hexdigest()))


# Local LLM for reasoning
reasoning_client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)

# Local LLM for embeddings
llm_client = OpenAI(
    base_url="http://127.0.0.1:8082/v1",
    api_key="sk-no-key-required"
)


# ==============================================================================
# AI-POWERED RESEARCH AGENT
# ==============================================================================

async def ai_research_agent():
    """
    AI-powered research agent that:
    1. Generates search queries
    2. Uses DuckDuckGo to search
    3. Ranks sources by reliability
    4. Scores urgency
    5. Saves to Qdrant
    6. Returns prioritized list
    """
    # Step 1: LLM generates search queries
    print("Generating research queries...")
    queries = await generate_search_queries()

    server_params = StdioServerParameters(
        command="uvx",
        args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"]
    )

    all_analyzed = []

    # Step 2-5: For each query, search, rank, score urgency, save
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            for query in queries:
                print(f"\n--- Processing query: {query} ---")

                # Step 2: Search DuckDuckGo
                search_results = ""
                try:
                    result = await session.call_tool("duckduckgo_search", {"query": query})
                    if result.content:
                        for item in result.content:
                            if hasattr(item, 'text'):
                                search_results += item.text + "\n"
                except Exception as e:
                    print(f"  Search error: {e}")
                    continue

                if not search_results:
                    print("  No results found")
                    continue

                print(f"  Found {len(search_results)} characters of results")

                # Step 3: Extract and rank sources by reliability
                sources = await rank_source_reliability(search_results)
                print(f"  Ranked {len(sources)} sources by reliability")

                # Step 4: Score urgency for each source
                for source in sources:
                    source['urgency_score'] = await score_source_urgency(source['url'], query)
                    source['query'] = query

                # Step 5: Save to Qdrant
                for source in sources:
                    summary = source.get('summary', '')
                    embedding = get_embedding(summary)

                    if embedding:
                        final_score = source['reliability'] * source['urgency_score']
                        source['final_score'] = final_score

                        point = models.PointStruct(
                            id=content_id(source['url']),
                            vector=embedding,
                            payload={
                                "page_content": summary,
                                "title": query,
                                "source_url": source['url'],
                                "reliability": source['reliability'],
                                "urgency_score": source['urgency_score'],
                                "final_score": final_score,
                                "raw_results": search_results[:3000]
                            }
                        )

                        qdrant_client.upsert(
                            collection_name=collection_name,
                            points=[point]
                        )
                        all_analyzed.append(source)

                print(f"  Saved {len(sources)} sources to Qdrant")

    # Step 6: Pull back from Qdrant and return prioritized list
    return get_prioritized_sources(all_analyzed)


async def generate_search_queries():
    """LLM generates relevant search queries for financial research."""
    try:
        response = reasoning_client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "system",
                    "content": "You are a research strategist. Generate focused search queries."
                },
                {
                    "role": "user",
                    "content": """Generate 5-8 search queries for financial research today.

Focus on:
- Breaking financial news
- Market-moving developments
- Central bank activity
- Economic data releases
- Social media discussions (LinkedIn, Reddit, X) about finance

Return ONLY a JSON array: {["query1", "query2", ...]}"""
                }
            ],
            temperature=0.7,
            max_tokens=200
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Query generation error: {e}")
        return ["financial news today", "market trends", "economy updates"]


async def rank_source_reliability(search_results):
    """
    LLM ranks sources from search results by reliability.
    LinkedIn/Reddit sources get higher scores.
    """
    try:
        response = reasoning_client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "system",
                    "content": "You are evaluating source reliability for research."
                },
                {
                    "role": "user",
                    "content": f"""Extract and rank sources by reliability from these search results.

Search Results:
{search_results[:3000]}

Reliability scoring (0.5 to 3.0):
- 2.5-3.0: LinkedIn professionals, Reddit moderators/verified users, verified X accounts
- 2.0-2.4: Active Reddit contributors, LinkedIn posts with engagement
- 1.5-1.9: General social media posts with some credibility
- 1.0-1.4: Unverified accounts, low engagement
- 0.5-0.9: Spam, suspicious content

For each source, extract:
- url
- summary (2-3 sentences)
- reliability score (0.5-3.0)

Return ONLY JSON array: {[
    {{"url": "...", "summary": "...", "reliability": 2.5}},
    ...
]}"""
                }
            ],
            temperature=0.3,
            max_tokens=500
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"Reliability ranking error: {e}")
        return []


async def score_source_urgency(source_url, query):
    """
    LLM scores source urgency (1-10) based on immediate relevance.
    """
    try:
        response = reasoning_client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "system",
                    "content": "You are assessing research urgency. JSON only, no markdown."
                },
                {
                    "role": "user",
                    "content": f"""Score urgency (1-10) for this source:

Query: {query}
Source URL: {source_url}

Urgency scale:
- 9-10: Critical, breaking, immediate action needed
- 7-8: Significant, requires attention
- 4-6: Notable, should be reviewed
- 1-3: Routine, can be processed later

Return ONLY JSON: {{"urgency_score": int}}"""
                }
            ],
            temperature=0.2,
            max_tokens=50
        )
        result = json.loads(response.choices[0].message.content)
        return result.get("urgency_score", 5)
    except Exception as e:
        print(f"Urgency scoring error: {e}")
        return 5


def get_embedding(text):
    """Generate embedding using local LLM."""
    try:
        response = llm_client.embeddings.create(
            input=text,
            model="qwen3-4b-embedding"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Embedding error: {e}")
        return None


def get_prioritized_sources(all_sources):
    """
    Pull from Qdrant and return prioritized list sorted by reliability * urgency.
    """
    results = qdrant_client.scroll(
        collection_name="news",
        limit=100,
        with_payload=True,
        with_vectors=False
    )

    articles = results[0]

    # Sort by final_score (reliability * urgency)
    articles.sort(key=lambda x: x.payload.get("final_score", 0), reverse=True)
    top = articles[:15]

    print(f"\n{'='*70}")
    print(f"TOP {len(top)} PRIORITIZED RESEARCH SOURCES")
    print(f"{'='*70}")
    for i, point in enumerate(top, 1):
        reliability = point.payload.get("reliability", 0)
        urgency = point.payload.get("urgency_score", 0)
        final = point.payload.get("final_score", 0)
        url = point.payload.get("source_url", "unknown")[:40]
        print(f"{i}. [Rel:{reliability:.1f}] [Urg:{urgency}/10] [Final:{final:.1f}] {url}")
    print()

    return top


async def generate_research_summary(top_sources):
    """
    Generate final research summary from prioritized sources.
    """
    sources_text = ""
    for i, point in enumerate(top_sources, 1):
        reliability = point.payload.get("reliability", 0)
        urgency = point.payload.get("urgency_score", 0)
        url = point.payload.get("source_url", "unknown")
        summary = point.payload.get("page_content", "")[:100]
        sources_text += f"{i}. {url}\n   Summary: {summary}\n   Reliability: {reliability:.1f}, Urgency: {urgency}/10\n\n"

    response = reasoning_client.chat.completions.create(
        model="local-model",
        messages=[
            {
                "role": "system",
                "content": "You are synthesizing research findings for the team."
            },
            {
                "role": "user",
                "content": f"""Here are the prioritized research sources:

{sources_text}

Generate a research summary that:
1. Highlights the most urgent and reliable findings
2. Identifies key themes across sources
3. Recommends areas for deeper investigation
4. Notes any conflicting information

Focus on actionable insights for the research team."""
            }
        ],
        temperature=0.5,
        max_tokens=1500
    )
    return response.choices[0].message.content


async def run_research_pipeline():
    """
    Main AI-powered research pipeline.
    """
    start_time = time.perf_counter()

    # Run the AI research agent
    top_sources = await ai_research_agent()

    # Generate final summary
    print("\nGenerating research summary...")
    summary = await generate_research_summary(top_sources)
    print(summary)

    elapsed_time = time.perf_counter() - start_time
    print(f"\nTotal research time: {elapsed_time:.2f} seconds")

    return top_sources, summary


if __name__ == "__main__":
    asyncio.run(run_research_pipeline())

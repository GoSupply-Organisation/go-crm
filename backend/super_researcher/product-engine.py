import time
import asyncio
from qdrant_client import QdrantClient, models
from openai import OpenAI
import threading
import uuid
import hashlib
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


# Setup Qdrant Client
host = "localhost"
port = 6335
collection_name = "financial_news"
qdrant_client = QdrantClient(host=host, port=port)


def content_id(text):
    return str(uuid.UUID(hashlib.md5(text.encode()).hexdigest()))

# This is the inference client, this is the qwen3 4b
# Your local LLM for reasoning
reasoning_client = OpenAI(
    base_url="http://127.0.0.1:8081/v1",
    api_key="sk-no-key-required"
)

# This is the inference client, this is the qwen3 4b embedding model
# Setup OpenAI Client for embeddings
llm_client = OpenAI(
    base_url="http://127.0.0.1:8082/v1",
    api_key="sk-no-key-required"
)


# ==============================================================================
# DYNAMIC SOURCE DISCOVERY WITH DUCKDUCKGO MCP
# ==============================================================================

async def research_agent(query: str) -> list:
    """
    Research agent using DuckDuckgo MCP to search for relevant content.
    Returns a list of discovered content URLs and snippets.
    """
    discovered_content = []

    server_params = StdioServerParameters(
        command="uvx",
        args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"]
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            try:
                result = await session.call_tool("duckduckgo_search", {"query": query})
                if result.content:
                    import re
                    for item in result.content:
                        if hasattr(item, 'text'):
                            # Extract URLs from search results
                            urls = re.findall(r'https?://[^\s\>"\'<]+', item.text)
                            discovered_content.extend(urls)
            except Exception as e:
                print(f"  Research agent error for '{query}': {e}")

    return discovered_content


async def discover_content_sources():
    """
    Discover content dynamically using the research agent.
    Searches for financial news, central bank, and geopolitical content.
    Not limited to RSS - searches for any relevant content.
    """
    search_queries = [
        "financial news breaking today",
        "central bank press releases today",
        "market news latest developments",
        "economic data released today",
        "geopolitical news breaking",
        "stock market moving news",
        "commodities news latest",
        "forex market developments"
    ]

    discovered_content = set()

    for query in search_queries:
        print(f"  Researching: {query}")
        urls = await research_agent(query)
        discovered_content.update(urls)

    return list(discovered_content)


def get_domain_from_url(url):
    """Extract domain from URL, removing www prefix."""
    from urllib.parse import urlparse
    parsed = urlparse(url)
    return parsed.netloc.replace("www.", "")


# Cache for source weights to avoid repeated LLM calls
_source_weight_cache = {}


def assess_source_reliability(domain):
    """
    Dynamically assess source reliability using LLM.
    Returns a weight score (0.5 to 3.0) based on source authority.
    """
    try:
        response = reasoning_client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "system",
                    "content": "You are a research analyst evaluating information source reliability."
                },
                {
                    "role": "user",
                    "content": f"""Assess the reliability of this news source as a weight from 0.5 to 3.0:

Source: {domain}

Reliability Scale:
- 2.5-3.0: Central banks, official government bodies, regulatory agencies (primary sources)
- 2.0-2.4: Major established financial news with editorial standards (Reuters, WSJ, Dow Jones)
- 1.5-1.9: Industry-specific sources, economic data providers (specialized sources)
- 1.0-1.4: General financial news outlets (secondary sources)
- 0.5-0.9: Analysis/opinion sites, think tanks (interpretive sources)

Respond with ONLY a JSON number: {{"weight": float}}"""
                }
            ],
            temperature=0.1,
            max_tokens=50
        )
        result = json.loads(response.choices[0].message.content)
        weight = result.get("weight", 1.0)
        return max(0.5, min(3.0, weight))  # Clamp between 0.5 and 3.0
    except Exception as e:
        print(f"  Reliability assessment error for {domain}: {e}")
        return 1.0


def get_source_weight(url):
    """Get source weight, using cache and dynamic LLM assessment."""
    domain = get_domain_from_url(url)
    if domain not in _source_weight_cache:
        _source_weight_cache[domain] = assess_source_reliability(domain)
    return _source_weight_cache[domain]


def get_embedding(text):
    """Generate embedding using local LLM."""
    try:
        response = llm_client.embeddings.create(
            input=text,
            model="qwen3-4b-embedding"
        )
        return response.data[0].embedding
    except Exception as e:
        print(f"Error generating embedding: {e}")
        return None


def fetch_content(url):
    """
    Fetch content from URL. Currently supports RSS feeds.
    Can be extended to handle other content types (HTML, JSON, etc.).
    """
    import feedparser

    try:
        feed = feedparser.parse(url)
        if feed.status == 200:
            print("Feed fetched successfully (200 OK)")
        elif feed.status == 404:
            print("Feed not found (404 Not Found)")
        elif feed.status == 301:
            print("Feed permanently redirected (301 Moved Permanently)")
        elif feed.status == 304:
            print("Feed not modified (304 Not Modified)")
        return feed
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return None


def content_engine(sources_list):
    """
    Main orchestration of content ingestion, embedding, and saving to Qdrant.
    Dynamically assesses each source's reliability for weighting.
    Currently handles RSS feeds - can be extended for other content types.
    """
    for source_url in sources_list:
        print(f"Fetching from {source_url}...")
        feed = fetch_content(source_url)

        if feed and hasattr(feed, 'entries') and len(feed.entries) > 0:
            for entry in feed.entries:
                title = entry.get('title', '')
                description = entry.get('description', '')
                link = entry.get('link', '')
                published = entry.get('published', '')
                text_content = f"{title}. {description}"

                embedding = get_embedding(text_content)

                if embedding is None:
                    print(f"Failed to generate embedding for: {title[:50]}...")
                    continue

                domain = get_domain_from_url(source_url)
                weight = get_source_weight(source_url)

                point = models.PointStruct(
                    id=content_id(text_content),
                    vector=embedding,
                    payload={
                        "page_content": text_content,
                        "title": title,
                        "description": description,
                        "link": link,
                        "published": published,
                        "source_url": source_url,
                        "domain": domain,
                        "source_weight": weight
                    }
                )

                qdrant_client.upsert(
                    collection_name=collection_name,
                    points=[point]
                )

            print(f"  -> Processed {len(feed.entries)} entries")
        else:
            print(f"  -> No entries found or error occurred")


def get_recent_articles(hours=24, limit=100):
    """Pull all recent articles from Qdrant."""
    results = qdrant_client.scroll(
        collection_name="financial_news",
        limit=limit,
        with_payload=True,
        with_vectors=False
    )
    return results[0]


def score_article_urgency(title, domain, reliability_weight):
    """
    Score article urgency (time-sensitive importance) using local LLM.
    Returns urgency score from 1-10 based on immediate relevance.
    """
    try:
        response = reasoning_client.chat.completions.create(
            model="local-model",
            messages=[
                {
                    "role": "system",
                    "content": "You are a research analyst assessing information urgency. Respond with valid JSON only, no markdown."
                },
                {
                    "role": "user",
                    "content": f"""Assess the urgency of this headline from 1-10.

Headline: {title}
Source: {domain} (reliability weight: {reliability_weight})

Urgency considers: Immediate action required, breaking developments, time-sensitive information, emerging situations.
- 1-3 = Routine information, can be processed later
- 4-6 = Notable development, should be reviewed
- 7-8 = Significant development, requires attention
- 9-10 = Critical/breaking, immediate attention required

Respond ONLY with: {{"urgency_score": int, "reasoning": "one sentence", "topic": ["topic1"]}}"""
                }
            ],
            temperature=0.1,
            max_tokens=150
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        print(f"  Urgency scoring error: {e}")
        return {"urgency_score": 0, "reasoning": "failed to score", "topic": []}


def generate_research_summary(top_articles):
    """
    Generate research summary based on urgency scores and reliability weights.
    Prioritizes high urgency from reliable sources for research focus.
    """
    signals = ""
    for i, article in enumerate(top_articles, 1):
        urgency = article.get("urgency_score", 0)
        reliability = article.get("weight", 1.0)
        topic = article.get("topic", [])
        topic_str = ", ".join(topic) if topic else "N/A"
        signals += f"{i}. [{article['domain']}] {article['title']} (urgency: {urgency}/10, reliability: {reliability:.1f}, topics: {topic_str})\n"

    response = reasoning_client.chat.completions.create(
        model="local-model",
        messages=[
            {
                "role": "system",
                "content": "You are a lead research analyst synthesizing information for a research team. Prioritize high urgency, high reliability sources."
            },
            {
                "role": "user",
                "content": f"""Here are today's research signals:

{signals}

Generate a research summary that:
1. Highlights the most urgent developments from the most reliable sources
2. Identifies cross-cutting themes across multiple sources
3. Notes any conflicting information that needs verification
4. Recommends areas requiring deeper research

Focus on: What the research team needs to know now, what to investigate further, and where gaps in information exist."""
            }
        ],
        temperature=0.5,
        max_tokens=2000
    )
    return response.choices[0].message.content


def run_pipeline():
    """
    Research team pipeline:
    1. Get articles from Qdrant
    2. Score urgency using LLM
    3. Rank by (urgency * reliability) to identify priorities
    4. Generate research summary
    """
    # Step 1: Get articles
    print("Pulling articles from Qdrant...")
    articles = get_recent_articles()
    print(f"Found {len(articles)} articles\n")

    # Step 2: Score urgency
    print("Scoring articles for research urgency...")
    scored = []
    for point in articles:
        title = point.payload.get("title", "")
        domain = point.payload.get("domain", "unknown")
        weight = point.payload.get("source_weight", 1.0)

        if not title:
            continue

        result = score_article_urgency(title, domain, weight)
        scored.append({
            "title": title,
            "domain": domain,
            "weight": weight,
            "urgency_score": result.get("urgency_score", 0),
            "reasoning": result.get("reasoning", ""),
            "topic": result.get("topic", [])
        })
        print(f"  [{result.get('urgency_score', 0):>2}/10] {title[:80]}")

    # Step 3: Rank by urgency * reliability
    scored.sort(key=lambda x: x["urgency_score"] * x["weight"], reverse=True)
    top = scored[:15]

    print(f"\n{'='*60}")
    print(f"TOP {len(top)} RESEARCH PRIORITIES")
    print(f"{'='*60}")
    for a in top:
        print(f"  [{a['urgency_score']}/10] [{a['domain']}] {a['title'][:100]}")
    print()

    # Step 4: Generate research summary
    print("Generating research summary...\n")
    summary = generate_research_summary(top)
    print(summary)

    return {"scored": scored, "top": top, "summary": summary}


if __name__ == "__main__":
    # Step 0: Discover content dynamically using research agent
    print("Discovering content sources using research agent...")
    sources = asyncio.run(discover_content_sources())
    print(f"Discovered {len(sources)} content source URLs\n")

    start_time = time.perf_counter()

    # Step 1: Ingest from discovered content sources
    t1 = threading.Thread(target=content_engine, args=(sources,))
    t1.start()
    t1.join()

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Ingestion executed in: {elapsed_time:.4f} seconds\n")

    # Step 2: Run the research team pipeline
    run_pipeline()
    start_time = time.perf_counter()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Analysis executed in: {elapsed_time:.4f} seconds")

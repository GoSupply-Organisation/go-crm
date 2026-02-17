from fastmcp import FastMCP
from ddgs import DDGS
import logging

logger = logging.getLogger(__name__)

mcp = FastMCP("My Tools")

# ---------------------------------------------------------
# Tool 1: General Web Search
# ---------------------------------------------------------
@mcp.tool()
def duckduckgo_search(query: str, num_results: int = 5) -> str:
    """Search the web using DuckDuckGo and return formatted results."""
    try:
        num_results = min(num_results, 10)
        results = []
        with DDGS() as ddgs:
            search_results = list(ddgs.text(query, max_results=num_results))
            if not search_results:
                return "No results found."
            for i, r in enumerate(search_results, 1):
                results.append(
                    f"{i}. **{r.get('title', 'No Title')}**\n"
                    f"   URL: {r.get('href', 'N/A')}\n"
                    f"   Summary: {r.get('body', 'No description')}\n"
                )
        return f"Search Results for '{query}':\n\n" + "\n".join(results)
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------------------------------------
# Tool 2: Instant Answer
# ---------------------------------------------------------
@mcp.tool()
def duckduckgo_answer(query: str) -> str:
    """Get instant answers from DuckDuckGo."""
    try:
        with DDGS() as ddgs:
            answers = list(ddgs.answers(query))
            if not answers:
                return "No instant answer available."
            answer = answers[0]
            return f"Answer: {answer.get('text', 'N/A')}\nSource: {answer.get('url', 'N/A')}"
    except Exception as e:
        return f"Error: {str(e)}"

# ---------------------------------------------------------
# Tool 3: Add (test tool)
# ---------------------------------------------------------
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two integers together."""
    return a + b

# ---------------------------------------------------------
# VERIFY TOOLS BEFORE RUNNING
# ---------------------------------------------------------
if __name__ == "__main__":
    # List all registered tools
    if hasattr(mcp, '_tool_registry'):
        logger.info(f"Registered tools: {list(mcp._tool_registry.keys())}")
    else:
        logger.warning("Cannot access tool registry")

mcp.run()

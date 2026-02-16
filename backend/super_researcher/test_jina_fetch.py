from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import json

# MCP server configuration
server_params = StdioServerParameters(
    command="uvx",
    args=["--python", ">=3.10,<3.14", "duckduckgo-mcp", "serve"],
    env=None
)

# Test URLs - mix of government, simple, and complex pages
TEST_URLS = [
    # Simple pages
    "https://example.com",
    "https://httpbin.org/html",

    # Government pages (like the ones from your workflow)
    "https://www.tga.gov.au/safety/shortages-and-supply-disruptions/medicine-shortages/accessing-medicines-during-shortage/serious-scarcity-substitution-instruments-sssis",
    "https://www.pbs.gov.au/info/browse/medicine-shortages",

    # News sites
    "https://www.reuters.com",
    "https://www.bbc.com",
]


async def test_jina_fetch():
    print("Starting MCP Server...")
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            print("Testing jina_fetch with different URLs...\n")
            print("=" * 80)

            for url in TEST_URLS:
                print(f"\nTesting: {url[:70]}...")

                try:
                    result = await session.call_tool("jina_fetch", arguments={
                        "url": url,
                        "format": "json"
                    })

                    result_text = "".join([c.text for c in result.content if hasattr(c, 'text')])

                    # Parse to see what we got
                    try:
                        parsed = json.loads(result_text)
                        print(f"  ✓ SUCCESS - Got {len(str(parsed))} chars of JSON")
                        if parsed.get('data'):
                            print(f"  ✓ Has data: {parsed['data'].get('title', 'No title')[:50]}...")
                    except json.JSONDecodeError:
                        print(f"  ✓ SUCCESS - Got {len(result_text)} chars (non-JSON)")

                except Exception as e:
                    print(f"  ✗ FAILED: {type(e).__name__}: {str(e)[:100]}")

            print("\n" + "=" * 80)
            print("Test complete.")


if __name__ == "__main__":
    asyncio.run(test_jina_fetch())

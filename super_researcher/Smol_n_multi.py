import asyncio
import os
from dotenv import load_dotenv

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.base import TaskResult
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from autogen_ext_mcp.tools import get_tools_from_mcp_server
from mcp import StdioServerParameters


async def main() -> TaskResult:
    """
    Orchestrates a multi-agent research team to identify desperate healthcare facilities in Australia
    requiring urgent medical supplies, leveraging external tools for data aggregation.

    This function:
    1. Loads environment variables for API keys.
    2. Initializes MCP servers for search and scraping tools (Serper, DuckDuckGo, Firecrawl).
    3. Configures a local LLM client (Qwen3-4B-Instruct).
    4. Creates five specialized agents: four researchers and one critic.
    5. Uses a RoundRobinGroupChat to coordinate agent collaboration.
    6. Terminates when the critic agent explicitly approves the output ("APPROVE").
    7. Runs the task and returns the final result.

    Returns:
        TaskResult: The final outcome of the multi-agent research task.

    Raises:
        ValueError: If required API keys (SERPER_API_KEY, FIRECRAWL_API_KEY) are not set.
    """
    # Load environment variables
    load_dotenv()

    # Retrieve and validate API keys
    serper_api_key = os.getenv("SERPER_API_KEY")
    firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")

    if not serper_api_key:
        raise ValueError("Environment variable 'SERPER_API_KEY' is not set.")
    if not firecrawl_api_key:
        raise ValueError("Environment variable 'FIRECRAWL_API_KEY' is not set.")

    # Initialize MCP server configurations for external tools
    serper_server = StdioServerParameters(
        command="npx",
        args=["-y", "serper-search-scrape-mcp-server"],
        env={"SERPER_API_KEY": serper_api_key},
    )

    duckduckgo_server = StdioServerParameters(
        command="uvx",
        args=["duckduckgo-mcp-server"],
    )

    firecrawl_server = StdioServerParameters(
        command="npx",
        args=["-y", "firecrawl-mcp"],
        env={"FIRECRAWL_API_KEY": firecrawl_api_key},
    )

    # Initialize the LLM client (local Qwen3-4B-Instruct)
    llm_client = OpenAIChatCompletionClient(
        model="qwen3-4b-instruct-2507",
        base_url="http://127.0.0.1:1234/v1",
        api_key="sk-xxxx",
        model_info={
            "vision": True,
            "function_calling": True,
            "json_output": False,
            "family": ModelFamily.UNKNOWN,
            "structured_output": False,
        },
    )

    # Load tools from MCP servers asynchronously
    serper_tools = await get_tools_from_mcp_server(serper_server)
    duckduckgo_tools = await get_tools_from_mcp_server(duckduckgo_server)
    firecrawl_tools = await get_tools_from_mcp_server(firecrawl_server)

    # Define agent roles and their tool sets
    primary_researcher = AssistantAgent(
        name="primary_researcher",
        model_client=llm_client,
        tools=serper_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=(
            "You are a primary research agent tasked with gathering initial data on healthcare "
            "facilities in Australia in urgent need of medical supplies. Use Serper to find "
            "company websites, LinkedIn profiles, and news articles."
        ),
    )

    secondary_researcher = AssistantAgent(
        name="secondary_researcher",
        model_client=llm_client,
        tools=duckduckgo_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=(
            "You are a secondary research agent. Use DuckDuckGo to cross-reference and expand "
            "on findings from the primary researcher. Focus on uncovering lesser-known facilities "
            "and community health centers."
        ),
    )

    tertiary_researcher = AssistantAgent(
        name="tertiary_researcher",
        model_client=llm_client,
        tools=firecrawl_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=(
            "You are a tertiary research agent. Use Firecrawl to extract detailed content from "
            "websites of hospitals, aged care units, and telehealth providers. Prioritize pages "
            "with contact info, supply requests, or recent updates."
        ),
    )

    quaternary_researcher = AssistantAgent(
        name="quaternary_researcher",
        model_client=llm_client,
        tools=firecrawl_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=(
            "You are a quaternary research agent. Focus on identifying supply chain bottlenecks, "
            "staffing shortages, and public appeals from Australian healthcare providers. "
            "Highlight urgency and customer service needs."
        ),
    )

    critic_agent = AssistantAgent(
        name="critic_agent",
        model_client=llm_client,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=(
            "You are a critical review agent. Analyze the collective findings of the researchers. "
            "Ensure data is accurate, non-redundant, and prioritized by urgency. Only respond with "
            "'APPROVE' when the aggregated report is comprehensive, actionable, and meets quality "
            "standards. Otherwise, provide constructive feedback."
        ),
    )

    # Define termination condition: task ends when critic says "APPROVE"
    termination_condition = TextMentionTermination("APPROVE")

    # Create team with all agents in round-robin order
    research_team = RoundRobinGroupChat(
        agents=[
            primary_researcher,
            secondary_researcher,
            tertiary_researcher,
            quaternary_researcher,
            critic_agent,
        ],
        termination_condition=termination_condition,
    )

    # Define the research task
    research_task = """
    Aggregate data using the tools available for the most desperate hospitals, aged care units, 
    and telehealth services in Australia that are in urgent need of medical supplies. 
    This medical supplies company emphasizes speed and exceptional customer service.

    Search LinkedIn, company websites, news articles, public health bulletins, and any other 
    relevant sources. Prioritize facilities with public appeals, staffing shortages, or supply gaps. 
    Compile a prioritized list with contact details, specific needs, and urgency indicators.
    """

    # Run the team and capture the result
    console = Console(research_team)
    result = await console.run_stream(task=research_task)

    # Close the LLM client gracefully
    await llm_client.close()

    return result


if __name__ == "__main__":
    asyncio.run(main())
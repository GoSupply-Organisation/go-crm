from typing import Any, Dict, List

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
import asyncio

async def get_stock_data(symbol: str) -> Dict[str, Any]:
    """Get stock market data for a given symbol"""
    return {"price": 180.25, "volume": 1000000, "pe_ratio": 65.4, "market_cap": "700B"}


async def get_news(query: str) -> List[Dict[str, str]]:
    """Get recent news articles about a company"""
    return [
        {
            "title": "Tesla Expands Cybertruck Production",
            "date": "2024-03-20",
            "summary": "Tesla ramps up Cybertruck manufacturing capacity at Gigafactory Texas, aiming to meet strong demand.",
        },
        {
            "title": "Tesla FSD Beta Shows Promise",
            "date": "2024-03-19",
            "summary": "Latest Full Self-Driving beta demonstrates significant improvements in urban navigation and safety features.",
        },
        {
            "title": "Model Y Dominates Global EV Sales",
            "date": "2024-03-18",
            "summary": "Tesla's Model Y becomes best-selling electric vehicle worldwide, capturing significant market share.",
        },
    ]


model_client = OpenAIChatCompletionClient(
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


async def main():
    planner = AssistantAgent(
        "planner",
        model_client=model_client,
        handoffs=["financial_analyst", "news_analyst", "writer"],
        system_message="""You are a research planning coordinator.
        Coordinate market research by delegating to specialized agents:
        - Financial Analyst: For stock data analysis
        - News Analyst: For news gathering and analysis
        - Writer: For compiling final report
        Always send your plan first, then handoff to appropriate agent.
        Always handoff to a single agent at a time.
        Use TERMINATE when research is complete.""",
    )

    financial_analyst = AssistantAgent(
        "financial_analyst",
        model_client=model_client,
        handoffs=["planner"],
        tools=[get_stock_data],
        system_message="""You are a financial analyst.
        Analyze stock market data using the get_stock_data tool.
        Provide insights on financial metrics.
        Always handoff back to planner when analysis is complete.""",
    )

    news_analyst = AssistantAgent(
        "news_analyst",
        model_client=model_client,
        handoffs=["planner"],
        tools=[get_news],
        system_message="""You are a news analyst.
        Gather and analyze relevant news using the get_news tool.
        Summarize key market insights from news.
        Always handoff back to planner when analysis is complete.""",
    )

    writer = AssistantAgent(
        "writer",
        model_client=model_client,
        handoffs=["planner"],
        system_message="""You are a financial report writer.
        Compile research findings into clear, concise reports.
        Always handoff back to planner when writing is complete.""",
    )


    # Define termination condition
    text_termination = TextMentionTermination("TERMINATE")
    termination = text_termination

    research_team = Swarm(
        participants=[planner, financial_analyst, news_analyst, writer], termination_condition=termination
    )

    task = "Conduct market research for TSLA stock"
    await Console(research_team.run_stream(task=task))
    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main())
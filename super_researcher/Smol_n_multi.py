#!/usr/bin/env python3
"""
Swarm-style Medical Supplies Research System

This system uses the Swarm pattern where agents can intelligently hand off tasks
to specialized agents based on their capabilities, rather than following a fixed sequence.
"""

import asyncio
import os
from typing import Dict, Any, List
from dotenv import load_dotenv
from prompting import *
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination, HandoffTermination
from autogen_agentchat.messages import HandoffMessage
from autogen_agentchat.teams import Swarm
from autogen_agentchat.ui import Console
from autogen_core import CancellationToken
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.models import ModelFamily
from mcp import StdioServerParameters
from autogen_ext_mcp.tools import get_tools_from_mcp_server

load_dotenv()


async def main():
    """Main function to run the swarm research system"""
    
    # Load API keys
    serp = os.getenv("SERPER_API_KEY")
    fire = os.getenv("FIRECRAWL_API_KEY")
    
    # Set up MCP servers for different search capabilities
    serper_server = StdioServerParameters(
        command="npx",
        args=["-y", "serper-search-scrape-mcp-server"],
        env={"SERPER_API_KEY": str(serp)} if serp else {},
    )

    duck_server = StdioServerParameters(
        command="uvx",
        args=["duckduckgo-mcp-server"],
    )

    firecrawl_server = StdioServerParameters(
        command="npx",
        args=["-y", "firecrawl-mcp"],
        env={"FIRECRAWL_API_KEY": str(fire)} if fire else {},
    )

    # Initialize the model client
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

    # model_client = OpenAIChatCompletionClient(
    #     model="gpt-4.1",
    #     api_key=os.getenv("OPENAI_API_KEY"),
    # )

    # Get tools from MCP servers
    print("Loading research tools...")
    serper_tools = await get_tools_from_mcp_server(serper_server) if serp else []
    duck_tools = await get_tools_from_mcp_server(duck_server)
    firecrawl_tools = await get_tools_from_mcp_server(firecrawl_server) if fire else []
    
    print(f"Loaded {len(serper_tools)} serper tools, {len(duck_tools)} duck tools, {len(firecrawl_tools)} firecrawl tools")

    # Create the coordinator/planner agent
    coordinator = AssistantAgent(
        "coordinator",
        model_client=model_client,
        handoffs=["blackstar", "duck_researcher", "firecrawl_researcher", "critic", "synthesis_agent", "user"],
        system_message=COORDINATOR_PROMPT,
    )

    # Create specialized research agents
    serper_researcher = AssistantAgent(
        "blackstar",
        model_client=model_client,
        handoffs=["coordinator"],
        tools=duck_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=RESEARCH_PROMPT,
    )

    duck_researcher = AssistantAgent(
        "duck_researcher", 
        model_client=model_client,
        handoffs=["coordinator"],
        tools=duck_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=RESEARCH_PROMPT,
    )

    firecrawl_researcher = AssistantAgent(
        "firecrawl_researcher",
        model_client=model_client,
        handoffs=["coordinator"],
        tools=duck_tools,
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=RESEARCH_PROMPT,
    )

    # Create critic agent for quality assurance
    critic = AssistantAgent(
        "critic",
        model_client=model_client,
        handoffs=["coordinator"],
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=CRITIC_PROMPT,
    )

    # Create synthesis agent for final report
    synthesis_agent = AssistantAgent(
        "synthesis_agent",
        model_client=model_client,
        handoffs=["coordinator"],
        reflect_on_tool_use=True,
        model_client_stream=True,
        system_message=SYNTHESIS_PROMPT,
    )

    # Define termination conditions
# More specific termination conditions
    termination = (
        TextMentionTermination("FINAL_REPORT_COMPLETE") | 
        TextMentionTermination("RESEARCH_COMPLETE") |
        TextMentionTermination("TASK_COMPLETE") |
        TextMentionTermination("APPROVE")
    )

    # Create the swarm team
    research_team = Swarm(
        participants=[coordinator, serper_researcher, duck_researcher, firecrawl_researcher, critic, synthesis_agent],
        termination_condition=termination,
    )

    # Define the research task
    task = """Research and aggregate data on the most desperate hospitals, aged care units, and telehealth services in Australia that need medical supplies. 

        This research is for a medical supplies company that specializes in speed and excellent customer service. Focus on:

        1. **Hospitals with urgent medical supply needs** - especially those experiencing shortages
        2. **Aged care facilities requiring medical equipment** - prioritize those with recent supply chain issues  
        3. **Telehealth services needing medical supplies** - focus on rapid growth and service expansion

        Research sources should include:
        - LinkedIn company updates and hiring patterns
        - Company websites and press releases  
        - News articles about supply shortages
        - Healthcare industry publications
        - Government health department reports
        - Social media mentions of supply issues

        For each facility found, gather:
        - Facility name and location
        - Specific medical supplies needed
        - Contact information (phone, email, key personnel)
        - Business size and patient volume
        - Evidence of supply urgency or shortage
        - Any mentions of preferring fast, reliable suppliers

        Present findings in a structured format suitable for sales outreach."""

    print("Starting Swarm research system...")
    print("=" * 60)
    
    try:
        # Run the swarm research system
        await Console(research_team.run_stream(task=task))
        
    except Exception as e:
        print(f"Error during research: {e}")
        
    finally:
        # Clean up model client
        await model_client.close()


if __name__ == "__main__":
    asyncio.run(main())
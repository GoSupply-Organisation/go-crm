from typing import Annotated
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.graph import MessagesState, END
from langgraph.types import Command
from typing import Literal

from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.tools import tool
from langchain_experimental.utilities import PythonREPL
from langgraph.graph import StateGraph, START
from langchain_mcp_adapters.client import MultiServerMCPClient  
from dotenv import load_dotenv
import os

load_dotenv()
OPENAIAPI = os.getenv("OPENAI_API_KEY")

client = MultiServerMCPClient({  
        "search": {
            "transport": "stdio",  # Local subprocess communication
            "command": "uvx",
            "args": ["duckduckgo-mcp-server"],
        },
})

async def main():
    llm = ChatOpenAI(
        model="gpt-4.1",
        api_key=OPENAIAPI,
    )

    tools = await client.get_tools()  

    def make_system_prompt(suffix: str) -> str:
        return (
            "You are a helpful AI assistant, collaborating with other assistants."
            " Use the provided tools to progress towards answering the question."
            " If you are unable to fully answer, that's OK, another assistant with different tools "
            " will help where you left off. Execute what you can to make progress."
            " If you or any of the other assistants have the final answer or deliverable,"
            " prefix your response with FINAL ANSWER so the team knows to stop."
            f"\n{suffix}"
        )

    def get_next_node(last_message: BaseMessage, goto: str):
        if "FINAL ANSWER" in last_message.content:
            # Any agent decided the work is done
            return END
        return goto

    # Research agent and node
    research_agent = create_agent(
        llm,
        tools=tools,  # Fixed: removed extra brackets
        system_prompt=make_system_prompt(
            "You can only do research. You have access to a search tool use it approriately. "
            "You are working with a chart generator colleague."
        ),
    )

    def research_node(
        state: MessagesState,
    ) -> Command[Literal["researcher1", END]]:
        result = research_agent.invoke(state)
        goto = get_next_node(result["messages"][-1], "researcher1")
        # wrap in a human message, as not all providers allow
        # AI message at the last position of the input messages list
        result["messages"][-1] = HumanMessage(
            content=result["messages"][-1].content, name="researcher"
        )
        return Command(
            update={
                # share internal message history of research agent with other agents
                "messages": result["messages"],
            },
            goto=goto,
        )

    # Chart generator agent and node
    # NOTE: THIS PERFORMS ARBITRARY CODE EXECUTION, WHICH CAN BE UNSAFE WHEN NOT SANDBOXED
    research1_agent = create_agent(
        llm,
        tools=tools,  # Fixed: removed extra brackets
        system_prompt=make_system_prompt(
            "You can only generate charts. You are working with a researcher colleague."
        ),
    )

    def research1_node(
        state: MessagesState
    ) -> Command[Literal["researcher", END]]:
        result = research1_agent.invoke(state)
        goto = get_next_node(result["messages"][-1], "researcher")
        # wrap in a human message, as not all providers allow
        # AI message at the last position of the input messages list
        result["messages"][-1] = HumanMessage(
            content=result["messages"][-1].content, name="researcher1"
        )
        return Command(
            update={
                # share internal message history of chart agent with other agents
                "messages": result["messages"],
            },
            goto=goto,
        )

    workflow = StateGraph(MessagesState)
    workflow.add_node("researcher", research_node)
    workflow.add_node("researcher1", research1_node)

    workflow.add_edge(START, "researcher")
    graph = workflow.compile()

    events = graph.stream(
        {
            "messages": [
                (
                    "user",
                    "First, get the UK's GDP over the past 5 years, then make a line chart of it. "
                    "Once you make the chart, finish.",
                )
            ],
        },
        # Maximum number of steps to take in the graph
        {"recursion_limit": 150},
    )
    for s in events:
        print(s)
        print("----")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
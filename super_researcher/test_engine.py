from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.agents import create_agent
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model = "ah",
    api_key="",
    base_url="",
)

agent = create_agent(
    
)
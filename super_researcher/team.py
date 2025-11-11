# Alright we have a few agents here we have a deep researcher, and 2 general researchers, and a orchestrator.
# Both of them feed the neo4j vector hourly with new data from the web and other sources. 
# Then everyday we have the orchestrator agent summarize the findings of the researchers then give a list of possible clients interested in gosupplys services.
# Imports
from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    WebSearchTool,
    VisitWebpageTool,
    OpenAIServerModel,
)

# Model setup
model = OpenAIServerModel(
    model_id="local-model",
    api_base="http://localhost:1234/v1",
    api_key="Faaahhh",
)



web_agent = ToolCallingAgent(
    tools=[WebSearchTool(), VisitWebpageTool()],
    model=model,
    max_steps=10,
    name="web_search_agent",
    description="Runs web searches for you.",
)


manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
)

answer = manager_agent.run("If LLM training continues to scale up at the current rhythm until 2030, what would be the electric power in GW required to power the biggest training runs by 2030? What would that correspond to, compared to some countries? Please provide a source for any numbers used.")
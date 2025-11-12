from smolagents import (
    CodeAgent,
    ToolCallingAgent,
    OpenAIServerModel,
    WebSearchTool,
    VisitWebpageTool,
)

# Configure the model
model = OpenAIServerModel(
    model_id="local-model",
    api_base="http://localhost:1234/v1",
    api_key="Faaahhh",
)

# Create the web search tool
web_search_tool = WebSearchTool()
visit_webpage = VisitWebpageTool()

# Create the web agent with proper tools
web_agent = ToolCallingAgent(
    tools=[web_search_tool, visit_webpage],
    model=model,
    max_steps=10,
    name="web_search_agent",
    description="Runs web searches and visits webpages for you.",
)

# Create the manager agent that can delegate to the web agent
manager_agent = CodeAgent(
    tools=[],
    model=model,
    managed_agents=[web_agent],
    additional_authorized_imports=["time", "numpy", "pandas"],
)

# Run the query
answer = manager_agent.run(
    "If LLM training continues to scale up at the current rhythm until 2030, what would be the electric power in GW required to power the biggest training runs by 2030? What would that correspond to, compared to some countries? Please provide a source for any numbers used."
)

print("\nFinal answer:")
print(answer)
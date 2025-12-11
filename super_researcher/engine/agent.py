from google.adk.agents import LlmAgent  
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv 
from .prompting import research_prompt
import litellm

load_dotenv()




# Define the model once and reuse it
model_name_at_endpoint = "lm_studio/glm-z1-9b-0414"
api_base_url = "http://localhost:1234/v1"

# Create the LiteLlm model instance
model = LiteLlm(
    # model = model_name_at_endpoint,
    # base_url=api_base_url
    stream = True,
    model = "openai/glm-4.6",
    api_key=os.getenv("GLM_API_KEY"),
    base_url="https://api.z.ai/api/paas/v4/"
)


root_agent = LlmAgent(
    name="research", 
    output_key='research_output', 
    # output_schema=TopLevelOutput,
    instruction=research_prompt,
    model=model,  # Add this line
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                server_params = StdioServerParameters(
                    command="uvx",  # The command to run the server
                    args=["duckduckgo-mcp-server"]  # Path to server script and transport mode
                )
            )
        ),
        # McpToolset(
        #     connection_params=StdioConnectionParams(
        #         timeout=20,
        #         server_params=StdioServerParameters(
        #             command="npx",
        #             args=[
        #                 "-y", "mcp-searxng"
        #             ],
        #             env={
        #                 "SEARXNG_URL": "YOUR_SEARXNG_INSTANCE_URL"
        #             }
        #         )
        #     )
        # ),
        McpToolset(
            connection_params=StdioConnectionParams(
                timeout=20,
                server_params=StdioServerParameters(
                    command="uvx",
                    args=[
                        "--from",
                        "git+https://github.com/walksoda/crawl-mcp",
                        "crawl-mcp"
                    ],
                    env={
                        "CRAWL4AI_LANG": "en"  # Optional: set language
                    }
                )
            )
        ),
        McpToolset(
            connection_params=StdioConnectionParams(
                timeout=20,
                server_params=StdioServerParameters(
                    command="uvx",
                args=["mcp-neo4j-cypher@0.5.1", "--transport", "stdio"],
                )
            )
        )  
    ]
)


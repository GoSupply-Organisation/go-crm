from google.adk.agents import LlmAgent  
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, SseConnectionParams, SseServerParams
from mcp import StdioServerParameters
from google.adk.models.lite_llm import LiteLlm
import os
from dotenv import load_dotenv 
from .prompting import research_prompt
import litellm
from pydantic import BaseModel, Field
from typing import Literal

load_dotenv()


# Define the model once and reuse it
model_name_at_endpoint = "lm_studio/glm-4.6v-flash"
api_base_url = "http://localhost:1234/v1"

# Create the LiteLlm model instance
model = LiteLlm(
    model = model_name_at_endpoint,
    base_url=api_base_url,
    stream = True,
    # model = "openai/glm-4.6",
    # api_key=os.getenv("GLM_API_KEY"),
    # base_url="https://api.z.ai/api/paas/v4/",
    # response_format={"type": "json_object"}

)



class ResearchOutput(BaseModel):
    company: str = Field(..., description="The name of the company.")
    website: str = Field(..., description="The company's website URL.")
    phone_number: str = Field(..., description="The company's phone number.")
    email: str = Field(..., description="The contact email address.")
    LEAD_CLASSIFICATIONS: Literal["New"]
    address: str = Field(..., description="The address of the company.")
    

root_agent = LlmAgent(
    name="research", 
    output_key='research_output', 
    # output_schema=ResearchOutput,
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
            connection_params=SseConnectionParams(
                url="http://localhost:11235/mcp/sse",
                timeout=20,
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



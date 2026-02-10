from google.adk.agents import LlmAgent  
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams, SseConnectionParams, SseServerParams
from mcp import StdioServerParameters
from google.adk.models.lite_llm import LiteLlm
from .prompting import research_prompt
from pydantic import BaseModel, Field
from typing import Literal
from decouple import config


GLM_BASE_URL = config("GLM_API_BASE_URL", default="https://api.z.ai/api/paas/v4/")
# Define the model once and reuse it
model_name_at_endpoint = "lm_studio/glm-4.6v-flash"
api_base_url = "http://localhost:1234/v1"
model_name = "openai/GLM-4.7-Flash"
# Create the LiteLlm model instance
model = LiteLlm(
    # model = model_name_at_endpoint,
    # base_url=api_base_url,
    stream = True,
    model = "openai/GLM-4.7-Flash",
    api_key=config("GLM_API_KEY"),
    base_url=GLM_BASE_URL,
    response_format={"type": "json_object"}
)
class ResearchOutput(BaseModel):
    company: str = Field(..., description="The name of the company.")
    website: str = Field(..., description="The company's website URL.")
    phone_number: str = Field(..., description="The company's phone number.")
    email: str = Field(..., description="The contact email address.")
    LEAD_CLASSIFICATIONS: Literal["New"]
    address: str = Field(..., description="The address of the company.")
    notes: str = Field(..., description="Additional notes about the company, What they do, etc.")
    

root_agent = LlmAgent(
    name="research", 
    output_key='research_output', 
    output_schema=ResearchOutput,
    instruction=research_prompt,
    model=model,  # Add this line
    tools=[
        McpToolset(
            connection_params=StdioConnectionParams(
                timeout=300,
                server_params=StdioServerParameters(
                    command="npx",
                    args=["-y", "firecrawl-mcp"],
                    env={
                        "FIRECRAWL_API_URL": config("FIRECRAWL_API_URL", default="http://localhost:3002"),
                        "FIRECRAWL_API_KEY": config("FIRECRAWL_API_KEY", default="sk-local")
                    },
                )
            )
        ),
        McpToolset(
            connection_params=StdioConnectionParams(
                timeout=300,
                server_params=StdioServerParameters(
                    command="uvx",
                    args=["duckduckgo-mcp", "serve"]
                )
            )
        ),
    ]
)



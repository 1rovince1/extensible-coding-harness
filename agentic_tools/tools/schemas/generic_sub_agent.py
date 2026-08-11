from pydantic import BaseModel, Field


class SubAgentTool(BaseModel):
    task: str = Field(..., description="The task for sub-agent")
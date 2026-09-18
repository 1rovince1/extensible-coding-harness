from pydantic import BaseModel, Field


class DelegateTask(BaseModel):
    task: str = Field(..., description="The task for sub-agent")
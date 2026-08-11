from pydantic import BaseModel, Field


class LoadSkill(BaseModel):
    skill_name: str = Field(..., description="Name of the skill to be loaded")
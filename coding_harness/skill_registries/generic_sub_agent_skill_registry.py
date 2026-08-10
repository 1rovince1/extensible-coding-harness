import asyncio

from agentic_skills.utils.skill_parser import load_skills


ALLOWED_SKILLS = [
    "shell_skill"
]
SKILLS = asyncio.run(load_skills(ALLOWED_SKILLS))
SKILLS_METADATA = [skill_data["skill_metadata"] for skill_name, skill_data in SKILLS.items()]
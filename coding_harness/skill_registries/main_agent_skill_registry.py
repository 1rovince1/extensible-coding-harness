from agentic_skills.utils.skill_parser import load_skills


ALLOWED_SKILLS = [
    "shell_skill"
]

class SkillRegistry:
    def __init__(self, ALLOWED_SKILLS):
        self.ALLOWED_SKILLS = ALLOWED_SKILLS
        self.SKILL_REGISTRY = []
        self.SKILLS_METADATA = []

    async def initialize_skills(self):
        self.SKILL_REGISTRY = await load_skills(self.ALLOWED_SKILLS)
        self.SKILLS_METADATA = [skill_data["skill_metadata"] for skill_data in self.SKILL_REGISTRY.values()]


main_agent_skill_registry = SkillRegistry(ALLOWED_SKILLS)
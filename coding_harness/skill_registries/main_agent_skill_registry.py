import asyncio
from agentic_skills.utils.skill_parser import load_skills


ALLOWED_SKILLS = [
    "shell_skill"
]
SKILLS = asyncio.run(load_skills(ALLOWED_SKILLS))
SKILLS_METADATA = [skill_data["skill_metadata"] for skill_name, skill_data in SKILLS.items()]

# skill_metadata_list = []
# skill_content_list = []
# for skill in SKILLS:
#     skill_metadata_list.append(skill["skill_metadata"])
#     skill_content_list.append(skill["skill_content"])


# class SkillRegistry:
#     def __init__(self, ALLOWED_SKILLS):
#         self.SKILLS = asyncio.run(load_skills(ALLOWED_SKILLS))


#     def compile_skill_metadata(self):
#         skill_metadata_list = []
#         skill_content_list = []
#         for skill in self.SKILLS:
#             skill_metadata_list.append(skill["skill_metadata"])
#             skill_content_list.append(skill["skill_content"])
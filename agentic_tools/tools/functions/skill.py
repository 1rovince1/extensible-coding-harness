import logging

logger = logging.getLogger(__name__)


async def load_skill(skill_registry: dict, skill_name: str) -> str:
    """
    Returns the content of a skill
    """
    logger.info(f"Skill request: {skill_name}")

    if skill_name not in skill_registry:
        return "Skill not found in registry"

    skill_data = skill_registry[skill_name]
    skill_content = skill_data["skill_content"]
    return skill_content
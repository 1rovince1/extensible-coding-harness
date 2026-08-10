import os
import logging

import aiofiles

from helpers.parse_utils import MarkdownParsing

logger = logging.getLogger(__name__)


markdown_parser = MarkdownParsing()
skill_file_path_prefix = "agentic_skills"


async def load_skills(skill_list: list[str]) -> dict[str, dict[str, str]]:
    logger.info("Loading skills...")

    skill_data = {}
    for skill_name in skill_list:
        skill_file_path = os.path.join(skill_file_path_prefix, skill_name, "SKILL.md")

        skill_metadata = ""
        skill_content = ""
        async with aiofiles(skill_file_path, "r") as skill_file:
            raw_skill_file_content = await skill_file.read()

        skill_metadata = markdown_parser.extract_frontmatter(raw_skill_file_content)
        skill_content = markdown_parser.extract_markdown_content(raw_skill_file_content)

        skill_data[skill_name] = {
            "skills_metadata": skill_metadata,
            "skill_content": skill_content
        }

    return skill_data
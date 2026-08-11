import logging
import os

from jinja2 import Template
import aiofiles

logger = logging.getLogger(__name__)


def compile_prompt(prompt_content: str, input_mapping: dict) -> str:
    template = Template(prompt_content)
    prompt = template.render(input_mapping=input_mapping)
    return prompt


async def load_prompt_template(prompt_file: str) -> str:
    prompt_filepath_prefix = os.path.join("coding_harness", "prompts")
    prompt_filepath = os.path.join(prompt_filepath_prefix, f"{prompt_file}.md")
    async with aiofiles.open(prompt_filepath) as file:
        prompt_template = await file.read()
    return prompt_template
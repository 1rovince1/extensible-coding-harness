import logging
import re
import yaml

logger = logging.getLogger(__name__)


class MarkdownParsing:
    def __init__(self):
        self.frontmatter_regex = re.compile("^---\s*\n(.*?)\n---\s*\n")


    def extract_frontmatter(self, content: str):
        logger.info("Parsing for frontmatter...")
        match = self.frontmatter_regex.search(content)

        if match:
            yaml_block = match.group(1)
            metadata = yaml.safe_load(yaml_block)
            return metadata
        else:
            raise ValueError("No frontmatter found, or invalid frontmatter format")


    def extract_markdown_content(self, content: str):
        logger.info("Parsing for content after frontmatter...")
        match = self.frontmatter_regex.search(content)

        if match:
            content = content[match.end():]
            return content
        else:
            return content
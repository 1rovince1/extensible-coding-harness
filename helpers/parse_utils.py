import logging
import re
import yaml
import json

logger = logging.getLogger(__name__)


class MarkdownParsing:
    def __init__(self):
        self.frontmatter_regex = re.compile(
            "^---\s*\n(.*?)\n---\s*\n",
            re.DOTALL | re.MULTILINE
        )


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


class LLMResponseParsing:
    @staticmethod
    def parse_openai_responses_response(llm_response):
        turn_messages = []
        for message in llm_response.output:
            if message.type != "reasoning":
                continue
            summaries = []
            for summary in message.summary:
                summaries.append({
                    "type": "summary_text",
                    "text": summary.text
                })
            turn_messages.append({
                "type": "reasoning",
                "summary": summaries
            })
    
        if llm_response.output_text:
            turn_messages.append({
                "role": "assistant",
                "content": llm_response.output_text
            })
    
        tool_calls = []
        for message in llm_response.output:
            if message.type != "function_call":
                continue
            tool_calls.append({
                "tool_call_id": message.call_id,
                "tool_name": message.name,
                "tool_args": json.loads(message.arguments)
            })
            turn_messages.append({
                "type": "function_call",
                "call_id": message.call_id,
                "name": message.name,
                "arguments": message.arguments
            })

        return {
            "output_text": llm_response.output_text,
            "turn_messages": turn_messages,
            "tool_calls": tool_calls,
            "input_tokens": llm_response.usage.input_tokens,
            "output_tokens": llm_response.usage.output_tokens
        }


    @staticmethod
    def parse_ollama_response(llm_response):
        turn_messages = []
        if llm_response.message.content:
            turn_messages.append({
                "role": "assistant",
                "content": llm_response.message.content
            })

        tool_calls = []
        if llm_response.tools:
            for tool_call in llm_response.message.tool_calls:
                tool_calls.append({
                        "tool_name": tool_call.function.name,
                        "tool_args": tool_call.function.arguments
                })
                turn_messages.append({
                    "role": "assistant",
                    "tool_calls": tool_call.model_dump()
                })

        return {
            "output_text": llm_response.message.content,
            "turn_messages": turn_messages,
            "tool_calls": tool_calls,
            "input_tokens": llm_response.prompt_eval_count,
            "output_tokens": llm_response.eval_count
        }


class ToolResponseParsing:
    @staticmethod
    def compile_tool_messages(
        tool_completions: list[tuple[dict[str, str]]],
        llm_provider_api: str
    ):
        tool_messages = []
        for tool_completion in tool_completions:
            if llm_provider_api == "openai_responses":
                tool_messages.append({
                    "type": "function_call_output",
                    "call_id": tool_completion[0]["tool_call_id"],
                    "output": tool_completion[1]
                })
            if llm_provider_api == "openai_chat_completions":
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_completion[0]["tool_call_id"],
                    "content": tool_completion[1]
                })
            if llm_provider_api == "ollama":
                tool_messages.append({
                    "role": "tool",
                    "tool_name": tool_completion[0]["tool_name"],
                    "content": tool_completion[1]
                })

        return tool_messages
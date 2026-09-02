import logging
import re
import yaml
import json
from typing import Literal

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
    def parse_llm_response(
        llm_provider_api: Literal[
            "openai_chat_completions",
            "openai_responses",
            "ollama"
        ],
        llm_response
    ):
        if llm_provider_api == "openai_chat_completions":
            turn_message = {
                "role": "assistant"
            }
            if hasattr(llm_response.choices[0].message, "reasoning"):
                turn_message["reasoning"] = llm_response.choices[0].message.reasoning

            if llm_response.choices[0].message.content:
                turn_message["content"] = llm_response.choices[0].message.content

            tool_calls = []
            if llm_response.choices[0].message.tool_calls:
                tool_call_messages = []
                for tool_call in llm_response.choices[0].message.tool_calls:
                    tool_calls.append({
                        "tool_call_id": tool_call.id,
                        "tool_name": tool_call.function.name,
                        "tool_args": json.loads(tool_call.function.arguments)
                    })
                    tool_call_messages.append(tool_call.model_dump())
                turn_message["tool_calls"] = tool_call_messages

            return {
                "output_text": llm_response.choices[0].message.content,
                "turn_messages": [turn_message],
                "tool_calls": tool_calls,
                "input_tokens": llm_response.usage.prompt_tokens,
                "output_tokens": llm_response.usage.completion_tokens
            }

        
        elif llm_provider_api == "openai_responses":
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


        elif llm_provider_api == "ollama":
            turn_messages = []
            if llm_response.message.content:
                turn_messages.append({
                    "role": "assistant",
                    "content": llm_response.message.content
                })

            tool_calls = []
            if llm_response.message.tool_calls:
                tool_call_messages = []
                for tool_call in llm_response.message.tool_calls:
                    tool_calls.append({
                        "tool_name": tool_call.function.name,
                        "tool_args": tool_call.function.arguments
                    })
                    tool_call_messages.append(tool_call.model_dump())
                turn_messages.append({
                    "role": "assistant",
                    "tool_calls": tool_call_messages
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
        llm_provider_api: Literal[
            "openai_chat_completions",
            "openai_responses",
            "ollama"
        ],
        tool_completions: list[tuple[dict[str, str]]]
    ):
        tool_messages = []
        for tool_completion in tool_completions:
            if llm_provider_api == "openai_chat_completions":
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_completion[0]["tool_call_id"],
                    "content": tool_completion[1]
                })
            elif llm_provider_api == "openai_responses":
                tool_messages.append({
                    "type": "function_call_output",
                    "call_id": tool_completion[0]["tool_call_id"],
                    "output": tool_completion[1]
                })
            elif llm_provider_api == "ollama":
                tool_messages.append({
                    "role": "tool",
                    "tool_name": tool_completion[0]["tool_name"],
                    "content": tool_completion[1]
                })

        return tool_messages
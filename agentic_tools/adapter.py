from typing import Literal

from agentic_tools.utils.formatter import inline_pydantic_schema


def build_ollama_tools(tool_registry: dict):
    ollama_format_tools = []
    
    for tool_name, tool_data in tool_registry.items():
        ollama_format_tools.append({
            "type": "function",
            "function": {
                "name": tool_name,
                "description": tool_data["description"],
                # "parameters": tool_data["input_schema"].model_json_schema()
                "parameters": inline_pydantic_schema(tool_data["input_schema"])
            }
        })

    return ollama_format_tools


def build_openai_tools(
    llm_provider_api: Literal[
        "openai_chat_completions",
        "openai_responses"
    ],
    tool_registry: dict
):
    openai_format_tools = []

    for tool_name, tool_data in tool_registry.items():
        if llm_provider_api == "openai_chat_completions":
            openai_format_tools.append({
                "type": "function",
                "function": {
                    "name": tool_name,
                    "description": tool_data["description"],
                    "parameters": inline_pydantic_schema(tool_data["input_schema"])
                }
            })
        elif llm_provider_api == "openai_responses":
            openai_format_tools.append({
                "type": "function",
                "name": tool_name,
                "description": tool_data["description"],
                # "parameters": tool_data["input_schema"].model_json_schema()
                "parameters": inline_pydantic_schema(tool_data["input_schema"])
            })

    return openai_format_tools
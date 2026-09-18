from typing_extensions import TypedDict
from typing import Literal


class BaseAgentState(TypedDict):
    llm_provider_api: Literal[
        "openai_chat_completions",
        "openai_responses",
        "ollama"
    ]
    agent_type: str
    
    session_messages: list[dict[str, str]]
    session_context_messages: list[dict[str, str]]

    agent_calls: int
    session_input_tokens: int
    session_output_tokens: int
    session_context_current_token_count: int

    skill_registry: dict
    tool_registry: dict

    tool_calls: list
    tool_results: list


class MainAgentState(BaseAgentState):
    streaming: bool


class GenericSubAgentState(BaseAgentState):
    current_task: str
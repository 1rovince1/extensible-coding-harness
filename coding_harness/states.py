# import operator
# from typing import Annotated
from typing_extensions import TypedDict


class MainAgentState(TypedDict):
    # session_messages: Annotated[list[dict[str, str]], operator.add]
    stream_mode: bool
    
    session_messages: list[dict[str, str]]
    session_context_messages: list[dict[str, str]]

    agent_calls: int
    session_input_tokens: int
    session_output_tokens: int
    session_context_current_token_count: int

    tool_registry: dict
    tool_calls: list
    tool_results: list

    function_calls: list
    function_results: list

    sub_agent_calls: list
    sub_agent_results: list

    skill_registry: dict
    skill_calls: list
    skill_results: list


class GenericSubAgentState(TypedDict):
    current_task: str
    # session_messages: Annotated[list[dict[str, str]], operator.add]
    session_messages: list[dict[str, str]]
    session_context_messages: list[dict[str, str]]

    agent_calls: int
    session_input_tokens: int
    session_output_tokens: int
    session_context_current_token_count: int

    tool_registry: dict
    tool_calls: list
    tool_results: list

    function_calls: list
    function_results: list

    skill_registry: dict
    skill_calls: list
    skill_results: list
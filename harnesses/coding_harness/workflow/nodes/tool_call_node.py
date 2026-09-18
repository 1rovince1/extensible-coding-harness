import logging
import asyncio

from langsmith import traceable

from ..states import MainAgentState, GenericSubAgentState
from agentic_tools.utils.call_tool import call_function
from helpers.parse_utils import ToolResponseParsing

logger = logging.getLogger(__name__)


@traceable
async def tool_call(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside tool call node")
    logger.debug(f"State inside function call node: {state}")

    tasks = []
    tool_registry = state.get("tool_registry", {})
    tool_calls = state.get("tool_calls", [])
    
    for tool_call in tool_calls:
        tasks.append(
            call_function(
                tool_registry=tool_registry,
                fn_name=tool_call["tool_name"],
                fn_args=tool_call["tool_args"],
                additional_context={
                    "skill_registry": state.get("skill_registry", {})
                }
            )
        )
    
    tool_results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info(f"Tool results: {tool_results}")

    tool_messages = ToolResponseParsing.compile_tool_messages(
        tool_completions=list(zip(tool_calls, tool_results)),
        llm_provider_api=state["llm_provider_api"]
    )

    logger.info("Exiting tool call node")
    return {
        "tool_calls": [],
        "tool_results": [],
        "session_messages": state.get("session_messages", []) + tool_messages,
        "session_context_messages": state.get("session_context_messages", []) + tool_messages
    }
    
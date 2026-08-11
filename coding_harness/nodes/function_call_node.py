import logging
import asyncio

from langsmith import traceable

from coding_harness.states import MainAgentState, GenericSubAgentState
from agentic_tools.utils.call_tool import call_function

logger = logging.getLogger(__name__)


@traceable
async def function_call(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside function call node")
    logger.debug(f"state inside function call node: {state}")
    tasks = []
    tool_registry = state.get("tool_registry", {})
    # tool_calls = state.get("tool_calls", [])
    function_calls = state.get("function_calls", [])
    
    for function_call in function_calls:
        tasks.append(
            call_function(
                tool_registry=tool_registry,
                fn_name=function_call["tool_name"],
                fn_args=function_call["tool_args"]
            )
        )
    
    function_results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info(f"Tool results: {function_results}")
    # tool_messages = []
    # if function_results:
    #     for idx, function_call in enumerate(function_calls):
    #         tool_messages.append({
    #             "role": "tool",
    #             "tool_name": function_call["tool_name"],
    #             "content": function_results[idx]
    #         })

    logger.info("Exiting function call node")
    return {
        # "session_messages": tool_messages
        # "session_messages": state.get("session_messages", []) + tool_messages,
        "function_results": function_results
    }
    
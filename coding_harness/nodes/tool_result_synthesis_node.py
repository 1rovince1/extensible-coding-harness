import logging

from langsmith import traceable

from coding_harness.states import MainAgentState

logger = logging.getLogger(__name__)


@traceable
async def tool_result_synthesizer(state: MainAgentState):
    logger.info("Inside tool synthesizer node")

    function_calls = state.get("function_calls", [])
    function_results = state.get("function_results", [])
    sub_agent_calls = state.get("sub_agent_calls", [])
    sub_agent_results = state.get("sub_agent_results", [])
    skill_calls = state.get("skill_calls", [])
    skill_results = state.get("skill_results", [])

    sub_agent_responses = [
        sub_agent_result["session_context_messages"][-1]["content"]
        for sub_agent_result in sub_agent_results
    ]

    # tool_messages = []
    # for idx, function_call in enumerate(function_calls):
    #     tool_messages.append({
    #         "role": "tool",
    #         "tool_name": function_call["tool_name"],
    #         "content": function_results[idx]
    #     })
    # for idx, sub_agent_call in enumerate(sub_agent_calls):
    #     tool_messages.append({
    #         "role": "tool",
    #         "tool_name": sub_agent_call["tool_name"],
    #         "content": sub_agent_results[idx]
    #     })

    # logger.info("Exiting tool synthesizer node")
    # return {
    #     "session_messages": state.get("session_messages", []) + tool_messages
    # }

    tool_calls = function_calls + sub_agent_calls + skill_calls
    tool_results = function_results + sub_agent_responses + skill_results

    logger.info("Exiting tool synthesizer node")
    return{
        "tool_calls": tool_calls,
        "tool_results": tool_results,
        "function_calls": [],
        "function_results": [],
        "sub_agent_calls": [],
        "sub_agent_results": [],
        "skill_calls": [],
        "skill_results": []
    }
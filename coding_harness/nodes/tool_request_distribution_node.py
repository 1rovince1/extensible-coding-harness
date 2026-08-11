import logging

from langsmith import traceable

from coding_harness.states import MainAgentState, GenericSubAgentState

logger = logging.getLogger(__name__)


@traceable
async def tool_request_distributor(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside tool distributor node")

    all_tool_calls = state.get("tool_calls", [])
    function_calls = []
    sub_agent_calls = []
    skill_calls = []

    for tool_call in all_tool_calls:
        if tool_call["tool_name"] == "invoke_generic_sub_agent":
            sub_agent_calls.append(tool_call)
        elif tool_call["tool_name"] == "load_skill":
            skill_calls.append(tool_call)
        else:
            function_calls.append(tool_call)

    task_distribution = {
        "function_calls": function_calls,
        "skill_calls": skill_calls,
        "sub_agent_calls": sub_agent_calls
    }

    logger.info("Exiting tool dstributor node")
    return task_distribution
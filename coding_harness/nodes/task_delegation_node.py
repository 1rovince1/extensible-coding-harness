import logging
import asyncio

from langsmith import traceable

from coding_harness.states import MainAgentState, GenericSubAgentState
from coding_harness.orchestration_generic_sub_agent import compiled_sub_agent_orchestration

logger = logging.getLogger(__name__)


@traceable
async def task_delegator(state: MainAgentState):
    logger.info("Inside task delegator node")
    # tool_calls = state.get("tool_calls", [])
    # sub_tasks = [
    #     tool_call["tool_args"]["task"]
    #     for tool_call in tool_calls
    #     if tool_call["tool_name"] == "invoke_generic_sub_agent"
    # ]
    sub_agent_calls = state.get("sub_agent_calls", [])
    sub_tasks = [
        sub_agent_call["tool_args"]["task"]
        for sub_agent_call in sub_agent_calls
    ]

    tasks_to_send = []
    for task in sub_tasks:
        sub_agent_session_messages = [{
            "role": "user",
            "content": f"Your task is: {task}"
        }]
        sub_agent_state: GenericSubAgentState = {
            "current_task": task,
            "session_messages": sub_agent_session_messages,
            "session_context_messages": sub_agent_session_messages
        }
        tasks_to_send.append(
            compiled_sub_agent_orchestration.ainvoke(sub_agent_state)
        )

    sub_agent_results = await asyncio.gather(*tasks_to_send, return_exceptions=True)
    # tool_messages = []
    # if sub_agent_results:
    #     for idx, task in enumerate(sub_tasks):
    #         tool_messages.append({
    #             "role": "tool",
    #             "tool_name": "invoke_generic_sub_agent",
    #             "content": sub_agent_results[idx]["session_messages"][-1]["content"]
    #         })

    logger.info("Exiting task delegator node")
    return {
        # "session_messages": tool_messages
        # "session_messages": state.get("session_messages", []) + tool_messages
        "sub_agent_results": sub_agent_results
    }
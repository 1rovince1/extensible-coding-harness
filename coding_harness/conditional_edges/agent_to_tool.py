import logging

from coding_harness.states import MainAgentState, GenericSubAgentState

logger = logging.getLogger(__name__)


def tool_call_decision_edge(state: MainAgentState | GenericSubAgentState) -> str:
    logger.info("Inside tool call decision edge")

    combined_tool_calls = state.get("tool_calls", [])

    # # tool_node_tasks = [
    # #     tool_call
    # #     for tool_call in combined_tool_calls
    # #     if tool_call["tool_name"] != "invoke_generic_sub_agent"
    # # ]
    # # delegate_node_tasks = [
    # #     tool_call
    # #     for tool_call in combined_tool_calls
    # #     if tool_call["tool_name"] == "invoke_generic_sub_agent"
    # # ]
    # tool_node_tasks = False
    # delegate_node_tasks = False
    # for tool_call in combined_tool_calls:
    #     if tool_call["tool_name"] == "invoke_generic_sub_agent":
    #         delegate_node_tasks = True
    #     else:
    #         tool_node_tasks = True
    #     if delegate_node_tasks and tool_node_tasks:
    #         break

    # node_list = []
    # if tool_node_tasks:
    #     node_list.append("tool")
    # if delegate_node_tasks:
    #     node_list.append("delegate")

    # logger.info("Exiting tool call decision edge")
    # return node_list

    decision = "final_answer"
    if combined_tool_calls:
        decision = "tool_calls"

    logger.info("Exiting tool call decision edge")
    return decision

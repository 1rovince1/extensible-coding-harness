import logging

from ..states import MainAgentState, GenericSubAgentState

logger = logging.getLogger(__name__)


def tool_call_decision_edge(state: MainAgentState | GenericSubAgentState) -> str:
    logger.info("Inside tool call decision edge")

    combined_tool_calls = state.get("tool_calls", [])

    decision = "final_answer"
    if combined_tool_calls:
        decision = "tool_calls"

    logger.info("Exiting tool call decision edge")
    return decision

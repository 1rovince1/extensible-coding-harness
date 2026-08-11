import logging
import asyncio

from langsmith import traceable

from coding_harness.states import MainAgentState, GenericSubAgentState
from agentic_tools.utils.call_tool import call_function

logger = logging.getLogger(__name__)


@traceable
async def skill_loader(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside skill loader node...")

    skill_registry = state.get("skill_registry", {})
    skill_requests = state.get("skill_calls", [])
    tool_registry = state.get("tool_registry", {})

    tasks = []
    for skill_request in skill_requests:
        tasks.append(
            call_function(
                tool_registry=tool_registry,
                fn_name=skill_request["tool_name"],
                fn_args={
                    "skill_registry": skill_registry,
                    **skill_request["tool_args"]
                }
            )
        )

    skill_results = await asyncio.gather(*tasks, return_exceptions=True)
    logger.info(f"skill results: {skill_results}")

    logger.info("Exiting skill loader node...")
    return {
        "skill_results": skill_results
    }
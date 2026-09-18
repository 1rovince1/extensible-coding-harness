import logging

from config.env_config import env_settings
from ....agents import generic_sub_agent

logger = logging.getLogger(__name__)


async def delegate_task(task: str, additional_context: dict = {}) -> str:
    """
    Executes a sub-agent with the given task, and returns the result.
    """
    logger.info(f"Executing task delegator tool with task: {task}")
    sub_agent_session_messages = [{
        "role": "user",
        "content": f"Your task is: {task}"
    }]
    sub_agent_state = {
        "current_task": task,
        "session_messages": sub_agent_session_messages,
        "session_context_messages": sub_agent_session_messages,
        "llm_provider_api": env_settings.LLM_PROVIDER_API,
        "agent_type": "generic_sub_agent"
    }
    
    sub_agent_result = await generic_sub_agent.agent_loop.ainvoke(sub_agent_state)
    return sub_agent_result["session_context_messages"][-1]["content"]
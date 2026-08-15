import logging

from langsmith import traceable

from services.llm_service import call_llm
from coding_harness.states import MainAgentState, GenericSubAgentState
from config.env_config import env_settings

logger = logging.getLogger(__name__)


prompt = """
You are a context compression agent.
Your job is to compress the given context into a brief summary.
The context will be brief, but it should contain everything that has happened till now,
and what is currently requested by the user, or what is being done at the moment should be preserved as it is of great importance.
This compressed context will replace the given context, and will be used to further understand the tasks to be performed.

When generting a context summary:
Clearly mention the goal (user's request):
**GOAL**
Clearly mention what has been done to achieve the goal, and what more is required:
**Steps taken**

The resulting summary would be a prompt that would guide the agents to work towards the goal, which was the user's request.
Important things like the plan of work should not be summarised and kept as they are in the context.
"""
# If something is important (like the work plan, etc.) to the goal and process, it should not be summarised and tried to be replicated in the new context.


@traceable
async def context_manager(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside context manager node")

    tool_calls = state.get("tool_calls", [])
    tool_results = state.get("tool_results", [])
    tool_messages = []
    for idx, tool_call in enumerate(tool_calls):
        # tool_messages.append({
        #     "role": "tool",
        #     "tool_name": tool_call["tool_name"],
        #     "content": tool_results[idx]
        # })
        # tool_messages.append({
        #     "type": "function_call_output",
        #     "call_id": message.call_id,
        #     "output": json.dumps(result)
        # })
        tool_messages.append({
            "type": "function_call_output",
            "call_id": tool_call["tool_call_id"],
            "output": tool_results[idx]
        })

    session_context_messages = state.get("session_context_messages", []) + tool_messages
    current_session_context_tokens = state.get("session_context_current_token_count", 0)

    compressed_context_messages = []
    if current_session_context_tokens >= env_settings.CONTEXT_TOKENS_ALLOWED:
        logger.info("Compressing context")
        messages_to_compress = session_context_messages
        messages = [
            {
                "role": "system",
                "content": prompt.strip()
            },
            {
                "role": "user",
                "content": f"Context to compress:\n{messages_to_compress}"
            }
        ]
        llm_response = await call_llm(
            messages=messages,
            # model=env_settings.OLLAMA_CONTEXT_COMPRESSION_MODEL
            model=env_settings.OPENAI_COMPATIBLE_CONTEXT_COMPRESSION_LLM
        )
        compressed_context_messages = [{
            "role": "user",
            "content": f"Compressed context of what happened till now:\n{llm_response.message.content}"
        }]

    logger.info("Exiting context manager node")
    return {
        "session_messages": state.get("session_messages", []) + tool_messages + compressed_context_messages,
        "session_context_messages": compressed_context_messages if compressed_context_messages else session_context_messages
    }
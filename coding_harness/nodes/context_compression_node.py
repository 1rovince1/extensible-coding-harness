import logging

from langsmith import traceable

from services.llm_service import call_llm
from coding_harness.states import MainAgentState, GenericSubAgentState
from config.env_config import env_settings
from coding_harness.prompts.pompt_utils import compile_prompt, load_prompt_template
from helpers.parse_utils import LLMResponseParsing

logger = logging.getLogger(__name__)


@traceable
async def context_compressor(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside context compressor node")

    session_context_messages = state.get("session_context_messages", [])
    current_session_context_tokens = state.get("session_context_current_token_count", 0)

    compressed_context_messages = []
    if current_session_context_tokens >= env_settings.CONTEXT_TOKENS_ALLOWED:
        logger.info("Compressing context")
        messages_to_compress = session_context_messages

        prompt_template = await load_prompt_template(prompt_file="context_manager.system")
        prompt = compile_prompt(prompt_content=prompt_template, input_mapping={})
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
            llm_provider_api=state["llm_provider_api"],
            messages=messages,
            model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
            reasoning_effort="medium",
            stream=state.get("streaming", False),
            invoking_agent_name="context_compressor_agent"
        )

        parsed_llm_response = LLMResponseParsing.parse_llm_response(
            llm_provider_api=state["llm_provider_api"],
            llm_response=llm_response
        )

        compressed_context_messages = [{
            "role": "user",
            "content": f"Compressed context of what happened till now:\n{parsed_llm_response["output_text"]}"
        }]

    logger.info("Exiting context compressor node")
    return {
        "session_messages": state.get("session_messages", []) + compressed_context_messages,
        "session_context_messages": compressed_context_messages if compressed_context_messages else session_context_messages
    }
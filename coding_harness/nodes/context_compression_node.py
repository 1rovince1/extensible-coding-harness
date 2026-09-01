import logging

from langsmith import traceable

from services.llm_service import call_ollama_llm, call_openai_llm, call_openai_llm_with_stream
from coding_harness.states import MainAgentState, GenericSubAgentState
from config.env_config import env_settings
from coding_harness.prompts.pompt_utils import compile_prompt, load_prompt_template
from helpers.stream_utils import stream_response
from helpers.parse_utils import LLMResponseParsing

logger = logging.getLogger(__name__)


@traceable
async def context_compressor(state: MainAgentState | GenericSubAgentState):
    logger.info("Inside context manager node")

    # tool_calls = state.get("tool_calls", [])
    # tool_results = state.get("tool_results", [])
    # tool_messages = []
    # for idx, tool_call in enumerate(tool_calls):
    #     # tool_messages.append({
    #     #     "role": "tool",
    #     #     "tool_name": tool_call["tool_name"],
    #     #     "content": tool_results[idx]
    #     # })
    #     # tool_messages.append({
    #     #     "type": "function_call_output",
    #     #     "call_id": message.call_id,
    #     #     "output": json.dumps(result)
    #     # })
    #     tool_messages.append({
    #         "type": "function_call_output",
    #         "call_id": tool_call["tool_call_id"],
    #         "output": tool_results[idx]
    #     })

    # session_context_messages = state.get("session_context_messages", []) + tool_messages
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
        # llm_response = await call_ollama_llm(
        #     messages=messages,
        #     model=env_settings.OLLAMA_CONTEXT_COMPRESSION_MODEL
        # )
        # compressed_context_messages = [{
        #     "role": "user",
        #     "content": f"Compressed context of what happened till now:\n{llm_response.message.content}"
        # }]
        if not state.get("streaming", False):
            llm_response = await call_openai_llm(
                messages=messages,
                model=env_settings.OPENAI_COMPATIBLE_CONTEXT_COMPRESSION_LLM
            )
        else:
            llm_stream = call_openai_llm_with_stream(
                messages=messages,
                model=env_settings.OPENAI_COMPATIBLE_CONTEXT_COMPRESSION_LLM
            )
            llm_response = await stream_response(
                agent_name="context_compressor_agent",
                stream_generator=llm_stream
            )

        parsed_llm_response = LLMResponseParsing.parse_llm_response(
            llm_response=llm_response,
            llm_provider_api=state["llm_provider_api"]
        )

        compressed_context_messages = [{
            "role": "user",
            "content": f"Compressed context of what happened till now:\n{parsed_llm_response["output_text"]}"
        }]

    logger.info("Exiting context manager node")
    return {
        # "session_messages": state.get("session_messages", []) + tool_messages + compressed_context_messages,
        "session_messages": state.get("session_messages", []) + compressed_context_messages,
        "session_context_messages": compressed_context_messages if compressed_context_messages else session_context_messages
    }
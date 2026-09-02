import logging
from typing import Literal

from langgraph.config import get_stream_writer
from openai.types.chat.chat_completion import (
    ChatCompletion as OpenAIChatCompletion,
    Choice as OpenAIChoice
)
from openai.types.chat.chat_completion_message import ChatCompletionMessage as OpenAIChatCompletionMessage
from openai.types.completion_usage import CompletionUsage as OpenAICompletionUsage
from ollama import (
    ChatResponse as OllamaChatResponse,
    Message as OllamaMessage
)

logger = logging.getLogger(__name__)


def create_stream_event(
        type: str,
        stream: str,
        content: str | None = None
):
    stream_event = {
        "type": type,
        "stream": stream
    }
    if content:
        stream_event["content"] = content

    return stream_event


async def stream_and_consolidate_response(
    llm_provider_api: Literal[
        "openai_chat_completions",
        "openai_responses"
    ],
    stream_generator,
    agent_name: str = "",
):
    stream_writer = get_stream_writer()
    consolidated_llm_response = None

    if llm_provider_api == "openai_chat_completions":
        last_chunk_type = None
        consolidated_llm_response = OpenAIChatCompletion.model_construct()
        consolidated_llm_response.choices = [OpenAIChoice.model_construct()]
        consolidated_llm_response.choices[0].message = OpenAIChatCompletionMessage.model_construct()
        consolidated_llm_response.choices[0].message.reasoning = ""
        consolidated_llm_response.choices[0].message.content = ""
        consolidated_llm_response.choices[0].message.tool_calls = []
        consolidated_llm_response.usage = OpenAICompletionUsage.model_construct()
        async for chunk in stream_generator:
            print(chunk)
            if chunk.usage:
                consolidated_llm_response.usage = chunk.usage
                last_chunk_type == "usage"

            elif chunk.choices[0].finish_reason:
                if last_chunk_type == "response":
                    stream_writer(create_stream_event("stream_break", f"{agent_name}_response"))
                last_chunk_type == "finish"
            
            elif hasattr(chunk.choices[0].delta, "reasoning"):
                stream_writer(create_stream_event("chunk", f"{agent_name}_reasoning", chunk.choices[0].delta.reasoning))
                consolidated_llm_response.choices[0].message.reasoning += chunk.choices[0].delta.reasoning
                last_chunk_type = "reasoning"

            elif chunk.choices[0].delta.content:
                if last_chunk_type == "reasoning":
                    stream_writer(create_stream_event("stream_break", f"{agent_name}_reasoning"))
                stream_writer(create_stream_event("chunk", f"{agent_name}_response", chunk.choices[0].delta.content))
                consolidated_llm_response.choices[0].message.content += chunk.choices[0].delta.content
                last_chunk_type = "response"

            elif chunk.choices[0].delta.tool_calls:
                if last_chunk_type == "reasoning":
                    stream_writer(create_stream_event("stream_break", f"{agent_name}_reasoning"))
                consolidated_llm_response.choices[0].message.tool_calls.extend(chunk.choices[0].delta.tool_calls)
                last_chunk_type == "tool_call"


    elif llm_provider_api == "openai_responses":
        async for chunk in stream_generator:
            print(chunk)
            if chunk.type == "response.completed":
                consolidated_llm_response = chunk.response
            
            elif chunk.type == "response.reasoning_summary_text.delta":
                stream_writer(create_stream_event("chunk", f"{agent_name}_reasoning", chunk.delta))
            elif chunk.type == "response.reasoning_summary_text.done":
                stream_writer(create_stream_event("stream_break", f"{agent_name}_reasoning"))

            elif chunk.type == "response.output_text.delta":
                stream_writer(create_stream_event("chunk", f"{agent_name}_response", chunk.delta))
            elif chunk.type == "response.output_text.done":
                stream_writer(create_stream_event("stream_break", f"{agent_name}_response"))


    elif llm_provider_api == "ollama":
        last_chunk_type = None
        consolidated_llm_response = OllamaChatResponse.model_construct()
        consolidated_llm_response.message = OllamaMessage.model_construct()
        consolidated_llm_response.message.thinking = ""
        consolidated_llm_response.message.content = ""
        consolidated_llm_response.message.tool_calls = []
        async for chunk in stream_generator:
            print(chunk)
            if chunk.done:
                if last_chunk_type == "response":
                    stream_writer(create_stream_event("stream_break", f"{agent_name}_response"))
                consolidated_llm_response.prompt_eval_count = chunk.prompt_eval_count
                consolidated_llm_response.eval_count = chunk.eval_count
                last_chunk_type == "finish"

            elif chunk.message.thinking:
                stream_writer(create_stream_event("chunk", f"{agent_name}_reasoning", chunk.message.thinking))
                consolidated_llm_response.message.thinking += chunk.message.thinking
                last_chunk_type = "reasoning"

            elif chunk.message.content:
                if last_chunk_type == "reasoning":
                    stream_writer(create_stream_event("stream_break", f"{agent_name}_reasoning"))
                stream_writer(create_stream_event("chunk", f"{agent_name}_response", chunk.message.content))
                consolidated_llm_response.message.content += chunk.message.content
                last_chunk_type = "response"

            elif chunk.message.tool_calls:
                if last_chunk_type == "reasoning":
                    stream_writer(create_stream_event("stream_break", f"{agent_name}_reasoning"))
                consolidated_llm_response.message.tool_calls.extend(chunk.message.tool_calls)
                last_chunk_type == "tool_call"

    return consolidated_llm_response
import logging

from langgraph.config import get_stream_writer

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


async def stream_response(agent_name: str, stream_generator):
    stream_writer = get_stream_writer()
    llm_response = None
    
    async for chunk in stream_generator:
        # print(chunk)
        if chunk.type == "response.reasoning_summary_text.delta":
            stream_writer(create_stream_event("chunk", f"{agent_name}_reasoning", chunk.delta))
        if chunk.type == "response.reasoning_summary_text.done":
            stream_writer(create_stream_event("stream_break", f"{agent_name}_reasoning"))

        if chunk.type == "response.output_text.delta":
            stream_writer(create_stream_event("chunk", f"{agent_name}_response", chunk.delta))
        if chunk.type == "response.output_text.done":
            stream_writer(create_stream_event("stream_break", f"{agent_name}_response"))

        if chunk.type == "response.completed":
            llm_response = chunk.response

    return llm_response
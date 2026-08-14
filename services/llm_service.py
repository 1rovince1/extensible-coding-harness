import logging
from typing import Literal

from ollama import ChatResponse
from openai.types.responses.response import Response
from openai.types.responses.response_stream_event import ResponseStreamEvent

from clients.ollama_llm_client import ollama_manager
from clients.openai_llm_client import openai_manager
# from langchain_ollama import ChatOllama
from helpers.retry_utils import retry_with_backoff_async, retry_with_backoff_async_generator

logger = logging.getLogger(__name__)


@retry_with_backoff_async(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_openai_llm(
    messages: list[dict[str, str]],
    model: str,
    think: Literal[
        "high",
        "medium",
        "low",
        "xhigh",
        "none",
        "minimal",
        "max"
    ] = "none",
    tools: list[dict[str, str]] | None = None
) -> Response:
    logger.info("Calling llm via openai client...")

    logger.debug(f"Input messages: {messages}")
    llm_response = await openai_manager.client.responses.create(
        model=model,
        input=messages,
        reasoning={
            "effort": think
        },
        tools=tools
    )

    logger.info(f"Raw LLM response: {llm_response}")
    logger.info(
        "Token usage:\n"
        f"Input tokens: {llm_response.usage.input_tokens}\n"
        f"Output tokens: {llm_response.usage.output_tokens}"
    )

    return llm_response


@retry_with_backoff_async_generator(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_openai_llm_with_stream(
    messages: list[dict[str, str]],
    model: str,
    think: Literal[
        "high",
        "medium",
        "low",
        "xhigh",
        "none",
        "minimal",
        "max"
    ] = "none",
    tools: list[dict[str, str]] | None = None
):
    logger.info("Calling llm via openai client...")

    logger.debug(f"Input messages: {messages}")
    llm_response = await openai_manager.client.responses.create(
        model=model,
        input=messages,
        reasoning={
            "effort": think
        },
        tools=tools,
        stream=True
    )

    logger.info(f"Raw LLM response: {llm_response}")
    # logger.info(
    #     "Token usage:\n"
    #     f"Input tokens: {llm_response.usage.input_tokens}\n"
    #     f"Output tokens: {llm_response.usage.output_tokens}"
    # )

    async for event in llm_response:
        # print(event)
        # if event.type == "response.reasoning_summary_text.delta":
        #     # print(f"Thinking: {event.delta}", end="")
        #     print(event.delta, end="", flush=True)
        # if event.type == "response.output_text.delta":
        #     print(event.delta, end="", flush=True)
        yield event


@retry_with_backoff_async(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_llm(
        messages: list[dict[str, str]],
        model: str,
        think: bool = False,
        tools: list[dict[str, str]] | None = None
) -> ChatResponse:
    logger.info("Calling llm...")

    logger.debug(f"Input messages: {messages}")
    llm_response: ChatResponse = await ollama_manager.client.chat(
        model=model,
        messages=messages,
        tools=tools,
        think=think,
        # options={
        #     "num_ctx": 32768,
        #     "n_thread": 6
        # }
    )
    logger.info(f"Raw LLM response: {llm_response}")
    logger.info(f"Token usage:\nInput tokens: {llm_response.prompt_eval_count}\nOutput tokens: {llm_response.eval_count}")

    return llm_response


# async def call_llm(
#         messages: list[str],
#         model: str,
#         think: bool = False,
#         tools: list[dict[str, str]] | None = None
# ):
#     logger.info("Calling llm...")
#     ollama_client = ChatOllama(model=model)

#     llm_response = await ollama_client.ainvoke(
#         # model=model,
#         input=messages,
#         # tools=tools,
#         # think=think
#     )

#     logger.info(f"Raw LLM response: {llm_response}")

#     return llm_response
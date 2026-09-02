import logging
from typing import Literal

from clients.ollama_llm_client import ollama_manager
from clients.openai_llm_client import openai_manager
# from langchain_ollama import ChatOllama
from helpers.retry_utils import retry_with_backoff_async, retry_with_backoff_async_generator
from helpers.stream_utils import stream_and_consolidate_response

logger = logging.getLogger(__name__)


@retry_with_backoff_async(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_llm(
    llm_provider_api: Literal[
        "openai_chat_completions",
        "openai_responses",
        "ollama"
    ],
    messages: list[dict[str, str]],
    model: str,
    reasoning_effort: str | bool,
    tools: list = [],
    invoking_agent_name : str = "",
    stream: bool = False
):
    logger.info("Calling LLM...")
    logger.debug(f"Input messages: {messages}")

    if llm_provider_api == "openai_chat_completions":
        llm_response = await openai_manager.client.chat.completions.create(
            model=model,
            messages=messages,
            reasoning_effort=reasoning_effort,
            tools=tools,
            stream=stream,
            stream_options={
                "include_usage": True
            }
        )
    elif llm_provider_api == "openai_responses":
        llm_response = await openai_manager.client.responses.create(
            model=model,
            input=messages,
            reasoning={
                "effort": reasoning_effort
            },
            tools=tools,
            stream=stream
        )
    elif llm_provider_api == "ollama":
        llm_response = await ollama_manager.client.chat(
            model=model,
            messages=messages,
            tools=tools,
            think=reasoning_effort,
            stream=stream
        )

    logger.info(f"Raw LLM response: {llm_response}")
    if stream:
        return await stream_and_consolidate_response(
            llm_provider_api=llm_provider_api,
            stream_generator=llm_response,
            agent_name=invoking_agent_name
        )
    else:
        return llm_response


@retry_with_backoff_async(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_openai_llm(
    llm_provider_api: Literal[
        "openai_chat_completions",
        "openai_responses"
    ],
    messages: list[dict[str, str]],
    model: str,
    reasoning_effort: Literal[
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

    if llm_provider_api == "openai_chat_completions":
        llm_response = await openai_manager.client.chat.completions.create(
            model=model,
            messages=messages,
            reasoning_effort=reasoning_effort,
            tools=tools
        )
    elif llm_provider_api == "openai_responses":
        llm_response = await openai_manager.client.responses.create(
            model=model,
            input=messages,
            reasoning={
                "effort": reasoning_effort
            },
            tools=tools
        )

    logger.info(f"Raw LLM response: {llm_response}")
    # logger.info(
    #     "Token usage:\n"
    #     f"Input tokens: {llm_response.usage.input_tokens}\n"
    #     f"Output tokens: {llm_response.usage.output_tokens}"
    # )
    return llm_response


@retry_with_backoff_async_generator(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_openai_llm_with_stream(
    llm_provider_api: Literal[
        "openai_chat_completions",
        "openai_responses"
    ],
    messages: list[dict[str, str]],
    model: str,
    reasoning_effort: Literal[
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

    if llm_provider_api == "openai_chat_completions":
        llm_response = await openai_manager.client.chat.completions.create(
            model=model,
            messages=messages,
            reasoning_effort=reasoning_effort,
            tools=tools,
            stream=True,
            stream_options={
                "include_usage": True
            }
        )
    elif llm_provider_api == "openai_responses":
        llm_response = await openai_manager.client.responses.create(
            model=model,
            input=messages,
            reasoning={
                "effort": reasoning_effort
            },
            tools=tools,
            stream=True
        )

    logger.info(f"Raw LLM response: {llm_response}")
    async for event in llm_response:
        yield event


@retry_with_backoff_async(
        retry_count=5, 
        retry_multiplier=5,
        exceptions_to_retry=[TimeoutError]
)
async def call_ollama_llm(
        messages: list[dict[str, str]],
        model: str,
        think: bool = False,
        tools: list[dict[str, str]] | None = None
):
    logger.info("Calling llm...")

    logger.debug(f"Input messages: {messages}")
    llm_response = await ollama_manager.client.chat(
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


# async def call_ollama_llm(
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
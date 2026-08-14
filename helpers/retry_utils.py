import logging
import asyncio
from typing import Callable
from functools import wraps

from ollama import ChatResponse

logger = logging.getLogger(__name__)


def retry_with_backoff_async(
        retry_count: int,
        exceptions_to_retry: list = [],
        retry_start_value: int = 1,
        retry_multiplier: int = 1,
):
    def decorator_function(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, retry_count + 1):
                logger.info(f"Executing function {fn.__name__}. Attempt: {attempt}")
                try:
                    result = await fn(*args, **kwargs)
                    if isinstance(result, ChatResponse) and result.done_reason == "load" and attempt < retry_count:
                        await asyncio.sleep(retry_start_value * (retry_multiplier * attempt))
                        continue
                    return result
                except Exception as e:
                    logger.exception("Retrying attempt. Error received", exc_info=True)
                    if e in exceptions_to_retry and attempt < retry_count:
                        await asyncio.sleep(retry_start_value * (retry_multiplier * attempt))
        return wrapper
    return decorator_function


def retry_with_backoff_async_generator(
        retry_count: int,
        exceptions_to_retry: list = [],
        retry_start_value: int = 1,
        retry_multiplier: int = 1,
):
    def decorator_function(fn: Callable):
        @wraps(fn)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, retry_count + 1):
                logger.info(f"Executing function {fn.__name__}. Attempt: {attempt}")
                try:
                    async for event in fn(*args, **kwargs):
                        yield event
                    return
                except Exception as e:
                    logger.exception("Retrying attempt. Error received", exc_info=True)
                    if e in exceptions_to_retry and attempt < retry_count:
                        await asyncio.sleep(retry_start_value * (retry_multiplier * attempt))
        return wrapper
    return decorator_function
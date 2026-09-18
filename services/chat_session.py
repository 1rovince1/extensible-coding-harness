import logging
from uuid import UUID
import json
import time

from clients.redis_client import redis_manager
from harnesses.coding_harness.entrypoint import run_harness, run_harness_streaming
from config.env_config import env_settings

logger = logging.getLogger(__name__)


async def process_user_request(
        user_query: str,
        session_id: UUID
):
    response_messages = await run_harness(
        session_id=session_id,
        user_query=user_query
    )
    return response_messages


async def process_user_request_streaming(
        user_query: str,
        session_id: UUID
):
    async for event in run_harness_streaming(
        session_id=session_id,
        user_query=user_query
    ):
        yield event


async def get_all_active_sessions():
    session_key_pattern = "session-*"

    try:
        matching_keys = []
        match_results = redis_manager.client.scan_iter(match=session_key_pattern)
        async for key in match_results:
            matching_keys.append(key)
    except Exception as e:
        logger.exception(f"Exception occured while getting all active sessions", exc_info=True)

    sessions_data = await redis_manager.client.mget(matching_keys)

    sessions = [
        (session_key.removeprefix("session-"), json.loads(session_data))
        for session_key, session_data in zip(matching_keys, sessions_data)
        if session_data is not None
    ]
    sessions.sort(key=lambda x: x[1]["updated_at"], reverse=True)
    
    return sessions
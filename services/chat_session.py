import logging
from uuid import UUID
import json
import time

from clients.redis_client import redis_manager
from coding_harness.orchestration_main_agent import compiled_harness
from config.env_config import env_settings

logger = logging.getLogger(__name__)


async def process_user_request(
        user_query: str,
        session_id: UUID
):
    logger.info(f"Processing user request (session-{session_id}): {user_query}")

    session_key = f"session-{session_id}"
    redis_session = await redis_manager.client.get(name=session_key)
    session_state = json.loads(redis_session) if redis_session else {"session_messages": []}

    session_state["session_messages"].append({
        "role": "user",
        "content": user_query
    })

    resultant_state = await compiled_harness.ainvoke(session_state)
    logger.info(f"User request processing result: {resultant_state}")

    resultant_state["updated_at"] = int(time.time())

    await redis_manager.client.set(
        name=session_key,
        value=json.dumps(resultant_state),
        ex=env_settings.CHAT_SESSION_EXPIRATION_TIME
    )

    return resultant_state["session_messages"][-1]["content"]


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
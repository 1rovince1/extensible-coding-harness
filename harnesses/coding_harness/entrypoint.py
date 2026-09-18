import logging
from uuid import UUID
import json
import time

from clients.redis_client import redis_manager
from config.env_config import env_settings
from .agents import main_agent

logger = logging.getLogger(__name__)


async def run_harness(session_id: UUID, user_query: str):
    logger.info(f"Processing user request (session-{session_id}): {user_query}")

    session_key = f"session-{session_id}"
    redis_session = await redis_manager.client.get(name=session_key)
    session_state = json.loads(redis_session) if redis_session else {
        "session_messages": [],
        "session_context_messages": []
    }

    user_query_message = {
        "role": "user",
        "content": user_query
    }
    session_state["session_messages"].append(user_query_message)
    session_state["session_context_messages"].append(user_query_message)
    session_state["streaming"] = False
    session_state["llm_provider_api"] = env_settings.LLM_PROVIDER_API
    session_state["agent_type"] = "main_agent"

    resultant_state = await main_agent.agent_loop.ainvoke(session_state)
    logger.info(f"User request processing result: {resultant_state}")

    resultant_state["updated_at"] = int(time.time())

    await redis_manager.client.set(
        name=session_key,
        value=json.dumps(resultant_state),
        ex=env_settings.CHAT_SESSION_EXPIRATION_TIME
    )

    new_messages_start_index = len(session_state["session_messages"])
    new_messages = resultant_state["session_messages"][new_messages_start_index:]

    # return resultant_state["session_messages"][-1]["content"]
    return new_messages


async def run_harness_streaming(session_id: UUID, user_query: str):
    logger.info(f"Processing user request (session-{session_id}): {user_query}")

    session_key = f"session-{session_id}"
    redis_session = await redis_manager.client.get(name=session_key)
    session_state = json.loads(redis_session) if redis_session else {
        "session_messages": [],
        "session_context_messages": []
    }

    user_query_message = {
        "role": "user",
        "content": user_query
    }
    session_state["session_messages"].append(user_query_message)
    session_state["session_context_messages"].append(user_query_message)
    session_state["streaming"] = True
    session_state["llm_provider_api"] = env_settings.LLM_PROVIDER_API
    session_state["agent_type"] = "main_agent"

    # graph_config = {
    #     "configurable": {
    #         "thread_id": str(session_key)
    #     }
    # }

    # resultant_state = await compiled_agent_loop.ainvoke(session_state)
    async for event in main_agent.agent_loop.astream(
        session_state,
        # config=graph_config,
        stream_mode=["custom", "updates", "values"],
        version="v2"
    ):
        if event["type"] == "custom":
            # print(event)
            yield event["data"]
        # elif event["type"] == "updates":
        #     for node_name, state in event["data"].items():
        #         if node_name == "context_manager":
        #             yield {
        #                 "data": {
        #                     "compressed_context": state.get("session_context_messages", [])
        #                 }
        #             }
        elif event["type"] == "values":
            resultant_state = event["data"]

    # resultant_state = await compiled_agent_loop.aget_state(config=graph_config)
    # print("\n\nRESULTANT_STATE", resultant_state)
    logger.info(f"User request processing result: {resultant_state}")

    resultant_state["updated_at"] = int(time.time())

    await redis_manager.client.set(
        name=session_key,
        value=json.dumps(resultant_state),
        ex=env_settings.CHAT_SESSION_EXPIRATION_TIME
    )

    # return resultant_state["session_messages"][-1]["content"]
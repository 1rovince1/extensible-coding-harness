import os
import logging
import json

from langsmith import traceable
from langgraph.config import get_stream_writer
from openai.types.responses.response import Response

from services.llm_service import call_llm, call_openai_llm, call_openai_llm_with_stream
from coding_harness.states import MainAgentState
from config.env_config import env_settings
from coding_harness.tool_registries.main_agent_tool_registry import TOOLS as MAIN_AGENT_TOOLS
from agentic_tools.adapter import build_ollama_tools, build_openai_tools
from coding_harness.skill_registries.main_agent_skill_registry import main_agent_skill_registry
from coding_harness.prompts.pompt_utils import compile_prompt, load_prompt_template
from helpers.stream_utils import create_stream_event

logger = logging.getLogger(__name__)


agent_tool_registry = {**MAIN_AGENT_TOOLS}
# agent_tools = build_ollama_tools(agent_tool_registry)
agent_tools = build_openai_tools(agent_tool_registry)


@traceable
async def main_agent(state: MainAgentState):
    logger.info("Inside main agent node")
    logger.debug(f"state inside main agent node: {state}")
    os.makedirs(env_settings.AGENT_WORK_DIR, exist_ok=True)

    prompt_template = await load_prompt_template(prompt_file="main_agent.system")
    agent_skills_metadata = main_agent_skill_registry.SKILLS_METADATA
    formatted_skills_metadata = "\n\n".join(
        f"skill name: {skill_metadata['name']}\n"
        f"skill description: {skill_metadata['description']}"
        for skill_metadata in agent_skills_metadata
    )
    prompt_vars = {
        "formatted_skills_metadata": formatted_skills_metadata
    }
    prompt = compile_prompt(prompt_content=prompt_template, input_mapping=prompt_vars)
    # print(prompt)

    messages = [{
        "role": "system",
        "content": prompt.strip()
    }]
    messages.extend(state.get("session_context_messages", []))

    if not state.get("streaming", False):
        llm_response: Response = await call_openai_llm(
            messages=messages,
            model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
            tools=agent_tools,
            think="medium"
        )
    else:
        stream_writer = get_stream_writer()
        llm_stream = call_openai_llm_with_stream(
            messages=messages,
            # model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
            model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
            tools=agent_tools,
            think="medium"
        )
        async for chunk in llm_stream:
            # print(chunk)
            if chunk.type == "response.reasoning_summary_text.delta":
                # print(f"Thinking: {chunk.delta}", end="")
                # print(chunk.delta, end="", flush=True)
                # stream_writer({"main_agent_reasoning_chunk": chunk.delta})
                stream_writer(create_stream_event("chunk", "main_agent_reasoning", chunk.delta))
            if chunk.type == "response.reasoning_summary_text.done":
                stream_writer(create_stream_event("stream_break", "main_agent_reasoning"))

            if chunk.type == "response.output_text.delta":
                # print(chunk.delta, end="", flush=True)
                stream_writer(create_stream_event("chunk", "main_agent_response", chunk.delta))
            if chunk.type == "response.output_text.done":
                stream_writer(create_stream_event("stream_break", "main_agent_response"))

            if chunk.type == "response.completed":
                llm_response = chunk.response


    # State management
    turn_messages = []
    for message in llm_response.output:
        if message.type != "reasoning":
            continue
        summaries = []
        for summary in message.summary:
            summaries.append({
                "type": "summary_text",
                "text": summary.text
            })
        turn_messages.append({
            "type": "reasoning",
            "summary": summaries
        })

    if llm_response.output_text:
        turn_messages.append({
            "role": "assistant",
            "content": llm_response.output_text
        })

    tool_calls = []
    for message in llm_response.output:
        if message.type != "function_call":
            continue
        tool_calls.append({
            "tool_call_id": message.call_id,
            "tool_name": message.name,
            "tool_args": json.loads(message.arguments)
        })
        turn_messages.append({
            "type": "function_call",
            "call_id": message.call_id,
            "name": message.name,
            "arguments": message.arguments
        })

    logger.info("Exiting main agent node")
    return {
        "session_messages": state.get("session_messages", []) + turn_messages,
        "session_context_messages": state.get("session_context_messages", []) + turn_messages,

        "agent_calls": state.get("agent_calls", 0) + 1,
        "session_input_tokens": state.get("session_input_tokens", 0) + llm_response.usage.input_tokens,
        "session_output_tokens": state.get("session_output_tokens", 0) + llm_response.usage.output_tokens,
        "session_context_current_token_count": llm_response.usage.input_tokens + llm_response.usage.output_tokens,

        "skill_registry": main_agent_skill_registry.SKILL_REGISTRY if tool_calls else {},
        "tool_registry": agent_tool_registry if tool_calls else {},
        "tool_calls": tool_calls if tool_calls else [],
        "tool_results": []
    }

    # state_updates = {
    #     # "session_messages": []
    #     "session_messages": state.get("session_messages", []),
    #     "skill_registry": main_agent_skill_registry.SKILL_REGISTRY
    # }
    # state_updates["agent_calls"] = state.get("agent_calls", 0) + 1
    # if llm_response:
    #     state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.usage.input_tokens
    #     state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.usage.output_tokens
    #     state_updates["session_context_current_token_count"] = llm_response.usage.input_tokens + llm_response.usage.output_tokens

    # for message in llm_response.output:
    #     if message.type != "reasoning":
    #         continue
    #     summaries = []
    #     for summary in message.summary:
    #         summaries.append({
    #             "type": "summary_text",
    #             "text": summary.text
    #         })
    #     state_updates["session_messages"].append({
    #         # "role": "assistant",
    #         "type": "reasoning",
    #         "summary": summaries
    #     })
    
    # if llm_response.output_text:
    #     state_updates["session_messages"].append({
    #         "role": "assistant",
    #         "content": llm_response.output_text
    #     })

    # tool_calls = []
    # for message in llm_response.output:
    #     if message.type != "function_call":
    #         continue
    #     tool_calls.append({
    #         "tool_call_id": message.call_id,
    #         "tool_name": message.name,
    #         "tool_args": json.loads(message.arguments)
    #     })
    #     state_updates["session_messages"].append({
    #         "type": "function_call",
    #         "call_id": message.call_id,
    #         "name": message.name,
    #         "arguments": message.arguments
    #     })

    # if tool_calls:
    #     state_updates["tool_registry"] = agent_tool_registry
    #     state_updates["tool_calls"] = tool_calls
    # else:
    #     state_updates["tool_registry"] = {}
    #     state_updates["tool_calls"] = []
    #     state_updates["tool_results"] = []

    # logger.info("Exiting main agent node")
    # return state_updates

    # if llm_response:
    #     state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.prompt_eval_count
    #     state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.eval_count
    #     state_updates["session_context_current_token_count"] = llm_response.prompt_eval_count + llm_response.eval_count
    # if llm_response.tools:
    #     state_updates["tool_registry"] = agent_tool_registry
    #     state_updates["tool_calls"] = [
    #         {
    #             "tool_name": tool_call.function.name,
    #             "tool_args": tool_call.function.arguments
    #         } for tool_call in llm_response.message.tool_calls
    #     ]
    #     state_updates["session_messages"].append({
    #         "role": "assistant",
    #         "tool_calls": [tool_call.model_dump() for tool_call in llm_response.message.tool_calls]
    #     })
    # else:
    #     state_updates["tool_registry"] = {}
    #     state_updates["tool_calls"] = []
    #     state_updates["tool_results"] = []

    # logger.info("Exiting main agent node")
    # return state_updates
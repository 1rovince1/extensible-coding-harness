import os
import logging
import json

from langsmith import traceable
from openai.types.responses.response import Response

from services.llm_service import call_llm, call_openai_llm
from coding_harness.states import GenericSubAgentState
from config.env_config import env_settings
from coding_harness.tool_registries.generic_sub_agent_tool_registry import TOOLS as SUB_AGENT_TOOLS
from agentic_tools.adapter import build_ollama_tools, build_openai_tools
from coding_harness.skill_registries.generic_sub_agent_skill_registry import generic_sub_agent_skill_registry
from coding_harness.prompts.pompt_utils import compile_prompt, load_prompt_template

logger = logging.getLogger(__name__)


agent_tool_registry = {**SUB_AGENT_TOOLS}
# agent_tools = build_ollama_tools(agent_tool_registry)
agent_tools = build_openai_tools(agent_tool_registry)


@traceable
async def generic_sub_agent(state: GenericSubAgentState):
    logger.info("Inside generic sub agent node")
    os.makedirs(env_settings.AGENT_WORK_DIR, exist_ok=True)

    prompt_template = await load_prompt_template(prompt_file="generic_sub_agent.system")
    agent_skills_metadata = generic_sub_agent_skill_registry.SKILLS_METADATA
    formatted_skills_metadata = "\n\n".join(
        f"skill name: {skill_metadata['name']}\n"
        f"skill description: {skill_metadata['description']}"
        for skill_metadata in agent_skills_metadata
    )
    prompt_vars = {
        "formatted_skills_metadata": formatted_skills_metadata
    }
    prompt = compile_prompt(prompt_content=prompt_template, input_mapping=prompt_vars)

    messages = [{
        "role": "system",
        "content": prompt.strip()
    }]
    messages.extend(state.get("session_context_messages", []))
    
    # llm_response = await call_llm(
    #     messages=messages,
    #     model=env_settings.OLLAMA_SUB_AGENT_MODEL,
    #     tools=agent_tools,
    #     think=True
    # )
    llm_response: Response = await call_openai_llm(
        messages=messages,
        # model=env_settings.OLLAMA_SUB_AGENT_MODEL,
        model=env_settings.OPENAI_COMPATIBLE_GENERIC_SUB_AGENT_LLM,
        tools=agent_tools,
        think="medium"
    )

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

    logger.info("Exiting generic sub agent node")
    return {
        "session_messages": state.get("session_messages", []) + turn_messages,
        "session_context_messages": state.get("session_context_messages", []) + turn_messages,

        "agent_calls": state.get("agent_calls", 0) + 1,
        "session_input_tokens": state.get("session_input_tokens", 0) + llm_response.usage.input_tokens,
        "session_output_tokens": state.get("session_output_tokens", 0) + llm_response.usage.output_tokens,
        "session_context_current_token_count": llm_response.usage.input_tokens + llm_response.usage.output_tokens,

        "skill_registry": generic_sub_agent_skill_registry.SKILL_REGISTRY if tool_calls else {},
        "tool_registry": agent_tool_registry if tool_calls else {},
        "tool_calls": tool_calls if tool_calls else [],
        "tool_results": []
    }
    
    # state_updates = {
    #     # "session_messages": []
    #     "session_messages": state.get("session_messages", []),
    #     "session_context_messages": state.get("session_context_messages", []),
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
    #     state_updates["skill_registry"] = generic_sub_agent_skill_registry.SKILL_REGISTRY
    #     state_updates["tool_registry"] = agent_tool_registry
    #     state_updates["tool_calls"] = tool_calls
    # else:
    #     state_updates["skill_registry"] = {}
    #     state_updates["tool_registry"] = {}
    #     state_updates["tool_calls"] = []
    #     state_updates["tool_results"] = []

    # logger.info("Exiting main agent node")
    # return state_updates


    # if llm_response:
    #     state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.prompt_eval_count
    #     state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.eval_count
    #     state_updates["session_context_current_token_count"] = llm_response.prompt_eval_count + llm_response.eval_count
    # if llm_response.message.content:
    #     state_updates["session_messages"].append({
    #         "role": "assistant",
    #         "content": llm_response.message.content
    #     })
    # if llm_response.message.tool_calls:
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

    logger.info("Exiting sub agent node")
    return state_updates
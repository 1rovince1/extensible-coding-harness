import os
import logging
import json

from langsmith import traceable
from openai.types.responses.response import Response

from services.llm_service import call_llm, call_openai_llm, call_openai_llm_with_stream
from coding_harness.states import MainAgentState
from config.env_config import env_settings
from coding_harness.tool_registries.main_agent_tool_registry import TOOLS as MAIN_AGENT_TOOLS
from agentic_tools.adapter import build_ollama_tools, build_openai_tools
from coding_harness.skill_registries.main_agent_skill_registry import main_agent_skill_registry
from coding_harness.prompts.pompt_utils import compile_prompt, load_prompt_template
from helpers.stream_utils import stream_response
from helpers.parse_utils import LLMResponseParsing

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
        llm_stream = call_openai_llm_with_stream(
            messages=messages,
            # model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
            model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
            tools=agent_tools,
            reasoning_effort="medium"
        )
        llm_response = await stream_response(
            agent_name="main_agent",
            stream_generator=llm_stream
        )

    # response parsing
    parsed_llm_response = LLMResponseParsing.parse_openai_responses_response(llm_response=llm_response)
    
    logger.info("Exiting main agent node")
    return {
        "session_messages": state.get("session_messages", []) + parsed_llm_response["turn_messages"],
        "session_context_messages": state.get("session_context_messages", []) + parsed_llm_response["turn_messages"],

        "agent_calls": state.get("agent_calls", 0) + 1,
        "session_input_tokens": state.get("session_input_tokens", 0) + parsed_llm_response["input_tokens"],
        "session_output_tokens": state.get("session_output_tokens", 0) + parsed_llm_response["output_tokens"],
        "session_context_current_token_count": parsed_llm_response["input_tokens"] + parsed_llm_response["output_tokens"],

        "skill_registry": main_agent_skill_registry.SKILL_REGISTRY if parsed_llm_response["tool_calls"] else {},
        "tool_registry": agent_tool_registry if parsed_llm_response["tool_calls"] else {},
        "tool_calls": parsed_llm_response["tool_calls"] if parsed_llm_response["tool_calls"] else [],
        "tool_results": []
    }
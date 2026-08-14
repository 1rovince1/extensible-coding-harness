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

logger = logging.getLogger(__name__)


agent_tool_registry = {**MAIN_AGENT_TOOLS}
# agent_tools = build_ollama_tools(agent_tool_registry)
agent_tools = build_openai_tools(agent_tool_registry)
# agent_skill_registry = main_agent_skill_registry.SKILL_REGISTRY
# agent_skills_metadata = main_agent_skill_registry.SKILLS_METADATA
# formatted_skills_metadata = "\n\n".join(
#     f"skill name: {skill_metadata['name']}"
#     f"skill description: {skill_metadata['description']}"
#     for skill_metadata in agent_skills_metadata
# )
# formatted_skills_metadata = ""
# for skill_metadata in agent_skills_metadata:
#     formatted_skills_metadata = (
#         formatted_skills_metadata +
#         "\n\n" +
#         "skill name: " + skill_metadata["name"] +
#         "skill description: " + skill_metadata["description"]
#     )
# print("registry in main agent", agent_skill_registry)
# print("raw_metadata", agent_skills_metadata)
# print("formatted", formatted_skills_metadata)


# prompt = f"""
# You are a coding assistant.
# You have access to a few tools to help with your job.
# Your tasks:
#     - Analyze the user request
#     - Ask to the user for any clarifications required to perform the given task
#     - If the task is of less complexity, do it on your own
#     - If the task is too complex or multi-step, break it down into sub-tasks, which you can delegate to sub agents with detailed instructions on what the task is, and what actions to take, file paths etc.
#     - If nature of sub-tasks allows it, then multiple sub agents should be used in parallel to keep individual workload in check
#     - Try to use sub agents at every opportunity there is a task that can be broken down into sub-tasks and/or parallelized, like when you have to work on multiple files at a time
#     - If multiple sub-agents are writing/editing code, then they should be clearly instructed so that code is coherent
#     - Task given to a sub agent should be simple and complete instructions should be provided for guidance
#     - You and sub agents have access to the same working dir, and all the coding should be done in there
#     - Any shell commands executed in this working dir itself; you can read/write files using shell commands
#     - Consolidate the final reply to the user after the task is done

# Instructions when calling sub-agents:
#     - When calling sub-agents, you will act as their manager
#     - You will be the glue among the sib-agents
#     - The subagents start with an empty context, so they do not know anything except the given task
#     - If you want multiple sub-agents to work cohesively, then you need to clearly instruct them on:
#         1. what functions (with names) to create - so that they do not go one creating them with whatever name
#         2. what APIs, if required, to create, etc.
#         3. any task that is concerned with combining the work of multiple sub-agents, should be done by yourself only

# Given a coding task from user, you have to do the task if simple and/or single step.
# If the task is complex and/or multi-step, you have to create a plan and then use sub-agents to delegate the tasks,
# with proper instructions so that the final application code is cohesive.

# You also have access to a set of skills given below, which you can load using the load skill tool.
# A skill is a set of instructions for more efficient use of tools, or some specific tasks.

# Available Skills:
# {formatted_skills_metadata.strip()}
# """

# Allowed shell commands via the shell tool are: {env_settings.SHELL_COMMANDS_ALLOWED}
# If you want to write to a file use this method: cat > filename <<'EOF'.....
# If you want to update some part an existing file use: sed ....


# @traceable
# async def main_agent(state: MainAgentState):
#     logger.info("Inside main agent node")
#     logger.debug(f"state inside main agent node: {state}")
#     os.makedirs(env_settings.AGENT_WORK_DIR, exist_ok=True)

#     prompt_template = await load_prompt_template(prompt_file="main_agent.system")
#     agent_skills_metadata = main_agent_skill_registry.SKILLS_METADATA
#     formatted_skills_metadata = "\n\n".join(
#         f"skill name: {skill_metadata['name']}\n"
#         f"skill description: {skill_metadata['description']}"
#         for skill_metadata in agent_skills_metadata
#     )
#     prompt_vars = {
#         "formatted_skills_metadata": formatted_skills_metadata
#     }
#     prompt = compile_prompt(prompt_content=prompt_template, input_mapping=prompt_vars)
#     # print(prompt)

#     messages = [{
#         "role": "system",
#         "content": prompt.strip()
#     }]
#     messages.extend(state.get("session_messages", []))
    
#     # llm_response = await call_llm(
#     #     messages=messages,
#     #     model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
#     #     tools=agent_tools,
#     #     think=True
#     # )
#     llm_response: Response = await call_openai_llm(
#         messages=messages,
#         # model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
#         model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
#         tools=agent_tools,
#         think="medium"
#     )

#     state_updates = {
#         # "session_messages": []
#         "session_messages": state.get("session_messages", []),
#         "skill_registry": main_agent_skill_registry.SKILL_REGISTRY
#     }
#     state_updates["agent_calls"] = state.get("agent_calls", 0) + 1
#     if llm_response:
#         state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.usage.input_tokens
#         state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.usage.output_tokens
#         state_updates["session_current_token_count"] = llm_response.usage.input_tokens + llm_response.usage.output_tokens

#     for message in llm_response.output:
#         if message.type != "reasoning":
#             continue
#         summaries = []
#         for summary in message.summary:
#             summaries.append({
#                 "type": "summary_text",
#                 "text": summary.text
#             })
#         state_updates["session_messages"].append({
#             "type": "reasoning",
#             "summary": summaries
#         })
    
#     if llm_response.output_text:
#         state_updates["session_messages"].append({
#             "role": "assistant",
#             "content": llm_response.output_text
#         })

#     tool_calls = []
#     for message in llm_response.output:
#         if message.type != "function_call":
#             continue
#         tool_calls.append({
#             "tool_call_id": message.call_id,
#             "tool_name": message.name,
#             "tool_args": json.loads(message.arguments)
#         })
#         state_updates["session_messages"].append({
#             "type": "function_call",
#             "call_id": message.call_id,
#             "name": message.name,
#             "arguments": message.arguments
#         })

#     if tool_calls:
#         state_updates["tool_registry"] = agent_tool_registry
#         state_updates["tool_calls"] = tool_calls
#     else:
#         state_updates["tool_registry"] = {}
#         state_updates["tool_calls"] = []
#         state_updates["tool_results"] = []

#     logger.info("Exiting main agent node")
#     return state_updates

#     # if llm_response:
#     #     state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.prompt_eval_count
#     #     state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.eval_count
#     #     state_updates["session_current_token_count"] = llm_response.prompt_eval_count + llm_response.eval_count
#     # if llm_response.tools:
#     #     state_updates["tool_registry"] = agent_tool_registry
#     #     state_updates["tool_calls"] = [
#     #         {
#     #             "tool_name": tool_call.function.name,
#     #             "tool_args": tool_call.function.arguments
#     #         } for tool_call in llm_response.message.tool_calls
#     #     ]
#     #     state_updates["session_messages"].append({
#     #         "role": "assistant",
#     #         "tool_calls": [tool_call.model_dump() for tool_call in llm_response.message.tool_calls]
#     #     })
#     # else:
#     #     state_updates["tool_registry"] = {}
#     #     state_updates["tool_calls"] = []
#     #     state_updates["tool_results"] = []

#     # logger.info("Exiting main agent node")
#     # return state_updates


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
    messages.extend(state.get("session_messages", []))
    
    # llm_response = await call_llm(
    #     messages=messages,
    #     model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
    #     tools=agent_tools,
    #     think=True
    # )
    stream_writer = get_stream_writer()
    # llm_stream_event: Response = call_openai_llm_with_stream(
    #     messages=messages,
    #     # model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
    #     model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
    #     tools=agent_tools,
    #     think="medium"
    # )

    # async for event in llm_stream_event:
    #     if event.type == "response.reasoning_summary_text.delta":
    #         # print(f"Thinking: {event.delta}", end="")
    #         # print(llm_stream_event.delta, end="", flush=True)
    #         stream_writer({"thinking_chunk": event.delta})
    #     if event.type == "response.output_text.delta":
    #         # print(llm_stream_event.delta, end="", flush=True)
    #         stream_writer({"respsonse_chunk": event.delta})

    async for event in call_openai_llm_with_stream(
        messages=messages,
        # model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
        model=env_settings.OPENAI_COMPATIBLE_MAIN_AGENT_LLM,
        tools=agent_tools,
        think="medium"
    ):
        if event.type == "response.reasoning_summary_text.delta":
            # print(f"Thinking: {event.delta}", end="")
            # print(llm_stream_event.delta, end="", flush=True)
            stream_writer({"thinking_chunk": event.delta})
        if event.type == "response.output_text.delta":
            # print(llm_stream_event.delta, end="", flush=True)
            stream_writer({"respsonse_chunk": event.delta})

    # state_updates = {
    #     # "session_messages": []
    #     "session_messages": state.get("session_messages", []),
    #     "skill_registry": main_agent_skill_registry.SKILL_REGISTRY
    # }
    # state_updates["agent_calls"] = state.get("agent_calls", 0) + 1
    # if llm_response:
    #     state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.usage.input_tokens
    #     state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.usage.output_tokens
    #     state_updates["session_current_token_count"] = llm_response.usage.input_tokens + llm_response.usage.output_tokens

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
    #     state_updates["session_current_token_count"] = llm_response.prompt_eval_count + llm_response.eval_count
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
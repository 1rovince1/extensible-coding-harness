import os
import logging

from langsmith import traceable

from services.ollama_llm_service import call_llm
from coding_harness.states import MainAgentState
from config.env_config import env_settings
from coding_harness.tool_registries.main_agent_tool_registry import TOOLS as MAIN_AGENT_TOOLS
from agentic_tools.adapter import build_ollama_tools
from coding_harness.skill_registries.main_agent_skill_registry import (
    SKILLS as MAIN_AGENT_SKILLS,
    SKILLS_METADATA as MAIN_AGENT_SKILLS_METADATA
)

logger = logging.getLogger(__name__)


prompt = f"""
You are a coding assistant.
You have access to a few tools to help with your job.
Your tasks:
    - Analyze the user request
    - Ask to the user for any clarifications requried to perform the given task
    - If the task is of less complexity, do it on your own
    - If the task is too complex or multi-step, break it down into sub-tasks, which you can delegate to sub agents with detailed instructions on what the task is, and what actions to take, file paths etc.
    - If nature of sub-tasks allows it, then multiple sub agents should be used in parallel to keep individual workload in check
    - Try to use sub agents at every opportunity there is a task that can be broken down into sub-tasks and/or parallelized, like when you have to work on multiple files at a time
    - If multiple sub-agents are writing/editing code, then they should be clearly instructed so that code is coherent
    - Task given to a sub agent should be simple and complete instructions should be provided for guidance
    - You and sub agents have access to the same working dir, and all the coding should be done in there
    - Any shell commands executed in this working dir itself; you can read/write files using shell commands
    - Consolidate the final reply to the user after the task is done

Instructions when calling sub-agents:
    - When calling sub-agents, you will act as their manager
    - You will be the glue among the sib-agents
    - The subagents start with an empty context, so they do not know anything except the given task
    - If you want multiple sub-agents to work cohesively, then you need to clearly instruct them on:
        1. what functions (with names) to create - so that they do not go one creating them with whatever name
        2. what APIs, if required, to create, etc.
        3. any task that is concerned with combining the work of multiple sub-agents, should be done by yourself only

Given a coding task from user, you have to do the task if simple and/or single step.
If the task is complex and/or multi-step, you have to create a plan and then use sub-agents to delegate the tasks,
with proper instructions so that the final application code is cohesive.

You also have access to a set of skills given below.
A skill is a set of instructions for more efficient of tools, or some specific tasks.
Available Skills:
{MAIN_AGENT_SKILLS_METADATA}
"""
# Allowed shell commands via the shell tool are: {env_settings.SHELL_COMMANDS_ALLOWED}
# If you want to write to a file use this method: cat > filename <<'EOF'.....
# If you want to update some part an existing file use: sed ....

agent_tool_registry = {**MAIN_AGENT_TOOLS}
agent_tools = build_ollama_tools(agent_tool_registry)


@traceable
async def main_agent(state: MainAgentState):
    logger.info("Inside main agent node")
    logger.debug(f"state inside main agent node: {state}")
    os.makedirs(env_settings.AGENT_WORK_DIR, exist_ok=True)

    messages = [{
        "role": "system",
        "content": prompt.strip()
    }]
    messages.extend(state.get("session_messages", []))
    
    llm_response = await call_llm(
        messages=messages,
        model=env_settings.OLLAMA_MAIN_AGENT_MODEL,
        tools=agent_tools,
        think=True
    )

    state_updates = {
        # "session_messages": []
        "session_messages": state.get("session_messages", []),
        "tool_registry": agent_tool_registry,
        "skill_registry": MAIN_AGENT_SKILLS
    }
    state_updates["agent_calls"] = state.get("agent_calls", 0) + 1
    if llm_response:
        state_updates["session_input_tokens"] = state.get("session_input_tokens", 0) + llm_response.prompt_eval_count
        state_updates["session_output_tokens"] = state.get("session_output_tokens", 0) + llm_response.eval_count
        state_updates["session_current_token_count"] = llm_response.prompt_eval_count + llm_response.eval_count
    if llm_response.message.content:
        state_updates["session_messages"].append({
            "role": "assistant",
            "content": llm_response.message.content
        })
    if llm_response.message.tool_calls:
        state_updates["tool_calls"] = [
            {
                "tool_name": tool_call.function.name,
                "tool_args": tool_call.function.arguments
            } for tool_call in llm_response.message.tool_calls
        ]
        state_updates["session_messages"].append({
            "role": "assistant",
            "tool_calls": [tool_call.model_dump() for tool_call in llm_response.message.tool_calls]
        })
    else:
        state_updates["tool_registry"] = {}
        state_updates["tool_calls"] = []
        state_updates["tool_results"] = []

    logger.info("Exiting main agent node")
    return state_updates
from ..workflow.agent_loop import AgentLoopBuilder
from ..workflow.registries.tool_registries.generic_sub_agent_tool_registry import TOOLS as generic_sub_agent_tool_registry
from ..workflow.registries.skill_registries.generic_sub_agent_skill_registry import generic_sub_agent_skill_registry
from ..workflow.states import GenericSubAgentState


agent_loop_builder = AgentLoopBuilder()

agent_loop = agent_loop_builder.build(
    agent_state_schema=GenericSubAgentState,
    tool_registry=generic_sub_agent_tool_registry,
    skill_registry=generic_sub_agent_skill_registry
)
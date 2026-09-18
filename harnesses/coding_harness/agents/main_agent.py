from ..workflow.agent_loop import AgentLoopBuilder
from ..workflow.registries.tool_registries.main_agent_tool_registry import TOOLS as main_agent_tool_registry
from ..workflow.registries.skill_registries.main_agent_skill_registry import main_agent_skill_registry
from ..workflow.states import MainAgentState


agent_loop_builder = AgentLoopBuilder()

agent_loop = agent_loop_builder.build(
    agent_state_schema=MainAgentState,
    tool_registry=main_agent_tool_registry,
    skill_registry=main_agent_skill_registry
)
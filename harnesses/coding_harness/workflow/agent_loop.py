from langgraph.graph import StateGraph, START, END

from .nodes import (
    LLMWorkerNode,
    tool_call,
    context_compressor
)
from .conditional_edges import tool_call_decision_edge


class AgentLoopBuilder:
    def build(
            self,
            agent_state_schema,
            tool_registry,
            skill_registry
    ):
        agent_loop = StateGraph(agent_state_schema)

        # nodes
        agent_loop.add_node(
            "llm_worker",
            LLMWorkerNode(
                tool_registry,
                skill_registry
            )
        )
        agent_loop.add_node("tool_call", tool_call)
        agent_loop.add_node("context_compressor", context_compressor)

        # edges
        agent_loop.add_edge(START, "context_compressor")
        agent_loop.add_edge("context_compressor", "llm_worker")
        agent_loop.add_conditional_edges(
            "llm_worker",
            tool_call_decision_edge,
            {
                "tool_calls": "tool_call",
                "final_answer": END
            }
        )
        agent_loop.add_edge("tool_call", "context_compressor")

        # compilation
        compiled_agent_loop = agent_loop.compile()
        return compiled_agent_loop
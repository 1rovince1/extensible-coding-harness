from langgraph.graph import START, END, StateGraph
from coding_harness.states import GenericSubAgentState
from coding_harness.nodes import (
    generic_sub_agent,
    function_call,
    context_manager,
    tool_distributor,
    tool_synthesizer
)
from coding_harness.conditional_edges import *


sub_agent_orchestration = StateGraph(GenericSubAgentState)


# nodes
sub_agent_orchestration.add_node("generic_sub_agent", generic_sub_agent)
sub_agent_orchestration.add_node("function_call", function_call)
sub_agent_orchestration.add_node("context_manager", context_manager)
sub_agent_orchestration.add_node("tool_distributor", tool_distributor)
sub_agent_orchestration.add_node("tool_synthesizer", tool_synthesizer)

# # edges
# sub_agent_orchestration.add_edge(START, "sub_agent")
# sub_agent_orchestration.add_conditional_edges(
#     "sub_agent",
#     tool_call_decision_edge,
#     {
#         "tool": "tool_call"
#     }
# )
# # sub_agent_orchestration.add_edge("tool_call", "sub_agent")
# sub_agent_orchestration.add_conditional_edges(
#     "tool_call",
#     context_compression_decision_edge,
#     {
#         "compress": "context_compressor",
#         "continue": "sub_agent"
#     }
# )
# sub_agent_orchestration.add_edge("context_compressor", "sub_agent")

# edges
sub_agent_orchestration.add_edge(START, "context_manager")
sub_agent_orchestration.add_edge("context_manager", "generic_sub_agent")
sub_agent_orchestration.add_conditional_edges(
    "generic_sub_agent",
    tool_call_decision_edge,
    {
        "tool_calls": "tool_distributor",
        "final_answer": END
    }
)
sub_agent_orchestration.add_edge("tool_distributor", "function_call")
sub_agent_orchestration.add_edge("function_call", "tool_synthesizer")
sub_agent_orchestration.add_edge("tool_synthesizer", "context_manager")


# compilation
compiled_sub_agent_orchestration = sub_agent_orchestration.compile()
from langgraph.graph import START, END, StateGraph
from coding_harness.states import GenericSubAgentState
from coding_harness.nodes import (
    generic_sub_agent,
    function_call,
    context_manager,
    tool_request_distributor,
    tool_result_synthesizer,
    skill_loader
)
from coding_harness.conditional_edges import *


sub_agent_orchestration = StateGraph(GenericSubAgentState)


# nodes
sub_agent_orchestration.add_node("generic_sub_agent", generic_sub_agent)
sub_agent_orchestration.add_node("function_call", function_call)
sub_agent_orchestration.add_node("context_manager", context_manager)
sub_agent_orchestration.add_node("tool_request_distributor", tool_request_distributor)
sub_agent_orchestration.add_node("tool_result_synthesizer", tool_result_synthesizer)
sub_agent_orchestration.add_node("skill_loader", skill_loader)

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
        "tool_calls": "tool_request_distributor",
        "final_answer": END
    }
)
sub_agent_orchestration.add_edge("tool_request_distributor", "function_call")
sub_agent_orchestration.add_edge("tool_request_distributor", "skill_loader")
sub_agent_orchestration.add_edge(["function_call", "skill_loader"], "tool_result_synthesizer")
sub_agent_orchestration.add_edge("tool_result_synthesizer", "context_manager")


# compilation
compiled_sub_agent_orchestration = sub_agent_orchestration.compile()
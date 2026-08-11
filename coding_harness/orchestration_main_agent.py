from langgraph.graph import StateGraph, START, END

from coding_harness.states import MainAgentState
from coding_harness.nodes import (
    main_agent,
    function_call,
    context_manager,
    tool_request_distributor,
    tool_result_synthesizer,
    task_delegator,
    skill_loader
)
from coding_harness.conditional_edges import *


code_harness = StateGraph(MainAgentState)


# nodes
code_harness.add_node("main_agent", main_agent)
code_harness.add_node("function_call", function_call)
code_harness.add_node("task_delegator", task_delegator)
code_harness.add_node("context_manager", context_manager)
code_harness.add_node("tool_request_distributor", tool_request_distributor)
code_harness.add_node("tool_result_synthesizer", tool_result_synthesizer)
code_harness.add_node("skill_loader", skill_loader)


# # edges
# code_harness.add_edge(START, "main_agent")
# code_harness.add_conditional_edges(
#     "main_agent",
#     tool_call_decision_edge,
#     {
#         "tool": "tool_call",
#         "delegate": "task_delegator"
#     }
# )
# # code_harness.add_edge("tool_call", "main_agent")
# # code_harness.add_edge("task_delegator", "main_agent")
# code_harness.add_conditional_edges(
#     "tool_call",
#     context_compression_decision_edge,
#     {
#         "compress": "context_compressor",
#         "continue": "main_agent"
#     }
# )
# code_harness.add_conditional_edges(
#     "task_delegator",
#     context_compression_decision_edge,
#     {
#         "compress": "context_compressor",
#         "continue": "main_agent"
#     }
# )
# code_harness.add_edge("context_compressor", "main_agent")


# edges
code_harness.add_edge(START, "context_manager")
code_harness.add_edge("context_manager", "main_agent")
code_harness.add_conditional_edges(
    "main_agent",
    tool_call_decision_edge,
    {
        "tool_calls": "tool_request_distributor",
        "final_answer": END
    }
)
code_harness.add_edge("tool_request_distributor", "function_call")
code_harness.add_edge("tool_request_distributor", "task_delegator")
code_harness.add_edge("tool_request_distributor", "skill_loader")
code_harness.add_edge(["function_call", "task_delegator", "skill_loader"], "tool_result_synthesizer")
code_harness.add_edge("tool_result_synthesizer", "context_manager")


# compilation
compiled_harness = code_harness.compile()
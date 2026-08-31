from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod

from coding_harness.orchestration_main_agent import compiled_harness
from coding_harness.orchestration_generic_sub_agent import compiled_sub_agent_orchestration


try:
    # compiled_harness.get_graph(xray=True).draw_png(output_file_path="main_graph.png")
    # compiled_sub_agent_orchestration.get_graph(xray=True).draw_png(output_file_path="sub_graph.png")
    try:
        compiled_harness.get_graph(xray=True).draw_mermaid_png(
            output_file_path="graph.png",
            curve_style=CurveStyle.BASIS
        )
    except Exception as e:
        print(f"Error generating graph using mermaid: {e}")
        compiled_harness.get_graph(xray=True).draw_png(output_file_path="graph.png")
except Exception as e:
    print(f"Error generating graph.png: {e}")
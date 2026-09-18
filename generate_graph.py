from langchain_core.runnables.graph import CurveStyle

from harnesses.coding_harness.agents.main_agent import agent_loop


try:
    try:
        agent_loop.get_graph(xray=True).draw_mermaid_png(
            output_file_path="graph.png",
            curve_style=CurveStyle.BASIS
        )
    except Exception as e:
        print(f"Error generating graph using mermaid: {e}")
        agent_loop.get_graph(xray=True).draw_png(output_file_path="graph.png")
except Exception as e:
    print(f"Error generating graph.png: {e}")
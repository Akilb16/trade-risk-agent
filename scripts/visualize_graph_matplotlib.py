"""Render the Trade Risk Agent workflow to graph.png using Matplotlib."""
from pathlib import Path
import sys
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def main():
    try:
        from src.graph import AGENT
        nodes = list(AGENT.get_graph().nodes)
    except (ImportError, AttributeError):
        nodes = ["guard_input", "retrieve", "decide", "tool", "answer_node", "guard_output"]

    # Stable positions make the diagram readable even when the graph has conditional edges.
    positions = {
        "guard_input": (0, 3), "retrieve": (2, 3), "decide": (4, 3),
        "tool": (6, 4), "answer_node": (6, 2), "guard_output": (8, 3),
        "__start__": (-2, 3), "__end__": (10, 3),
    }
    edges = [("__start__", "guard_input"), ("guard_input", "retrieve"), ("retrieve", "decide"),
             ("decide", "tool"), ("decide", "answer_node"), ("tool", "guard_output"),
             ("answer_node", "guard_output"), ("guard_output", "__end__")]

    fig, ax = plt.subplots(figsize=(14, 5.5), dpi=160)
    ax.set_facecolor("#fafaf8"); fig.patch.set_facecolor("#fafaf8")
    for source, target in edges:
        x1, y1 = positions[source]; x2, y2 = positions[target]
        ax.add_patch(FancyArrowPatch((x1 + .45, y1), (x2 - .45, y2), arrowstyle="-|>", mutation_scale=15, linewidth=1.4, color="#777b78", connectionstyle="arc3,rad=0.0"))
    for name in nodes:
        if name not in positions: continue
        x, y = positions[name]
        fill = "#e4eee8" if name in {"guard_input", "guard_output"} else "#e7edf3" if name in {"tool", "answer_node"} else "#f0eee6"
        box = FancyBboxPatch((x-.45, y-.28), .9, .56, boxstyle="round,pad=.04,rounding_size=.08", linewidth=1.2, edgecolor="#5f6662", facecolor=fill)
        ax.add_patch(box); ax.text(x, y, name.replace("_", "\n"), ha="center", va="center", fontsize=9, color="#202421")
    ax.text(-2, 3.48, "START", ha="center", fontsize=8, color="#777b78")
    ax.text(10, 3.48, "END", ha="center", fontsize=8, color="#777b78")
    ax.set_xlim(-2.8, 10.8); ax.set_ylim(1.2, 4.8); ax.axis("off")
    ax.set_title("Trade Risk Agent — LangGraph workflow", loc="left", fontsize=15, weight="medium", color="#202421", pad=16)
    output = Path("graph.png"); fig.savefig(output, bbox_inches="tight"); print(f"Saved {output.resolve()}")

if __name__ == "__main__": main()


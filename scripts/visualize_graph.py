"""Export the compiled LangGraph workflow as Mermaid text."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.graph import AGENT

def main():
    if not hasattr(AGENT, "get_graph"):
        raise SystemExit("LangGraph is not installed in this interpreter. Run: pip install -r requirements.txt")
    graph = AGENT.get_graph()
    mermaid = graph.draw_mermaid()
    output = Path("graph.mmd")
    output.write_text(mermaid, encoding="utf-8")
    print(mermaid)
    print(f"\nSaved Mermaid graph to {output.resolve()}")

if __name__ == "__main__":
    main()


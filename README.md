# Trade Risk Agent

An offline-first market-risk agent with a real LangGraph workflow, validated citations, deterministic risk tools, optional OpenAI-compatible function calling, async FastAPI execution, pgvector hooks, MCP tools, guardrails, evaluation, and a minimal browser interface.

## Run

```powershell
cd A:\trade-risk-agent
python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m pytest -q
python -m src.cli "What is model risk?"
python -m src.cli "compute VaR" --tool-args '{"returns":[-0.1,0.02,0.01],"confidence":0.95,"horizon_days":1}'
uvicorn src.api:app --reload
```

Open http://127.0.0.1:8000/frontend/ for the minimal browser frontend. It includes examples for policy questions, VaR, Greeks, and guardrail behavior.

`docker compose up -d` starts Postgres with pgvector. The current demo retrieval is deterministic and offline; `src/retrieval.py` is the seam for replacing it with pgvector cosine search. Eval reports go under `evals/report/`.

The project now contains a 30-item golden set, deterministic local embeddings, a pgvector search function, stress and limit tools, an optional MCP server, and an OpenAI-compatible async client. Real provider calls require `LLM_API_KEY`; real pgvector retrieval requires a running database and populated chunks.

Known limits: the checked-in corpus is still a small demo corpus, the default route is deterministic, citation membership is validated but semantic entailment is not, and human agreement labels have not been supplied.

For a systematic explanation of the architecture, risk concepts, guardrails, evaluation system, backend technologies, interview questions, and production gaps, read [PROJECT_GUIDE.md](PROJECT_GUIDE.md).

For definitions of the project terminology, read [GLOSSARY.md](GLOSSARY.md).

For the complete end-to-end execution flow and file responsibility map, read [PROJECT_FLOW.md](PROJECT_FLOW.md).

To export the actual LangGraph workflow as Mermaid, run `python scripts/visualize_graph.py`. It creates `graph.mmd`, which can be opened in Mermaid Live or a Mermaid-enabled Markdown editor.

To render a local PNG with Matplotlib, run `python scripts/visualize_graph_matplotlib.py`. It creates `graph.png` in the project root.


# Trade Risk Agent

A market-risk agent with a real LangGraph workflow, validated citations, deterministic risk tools, optional OpenAI-compatible function calling, async FastAPI execution, pgvector hooks, MCP tools, guardrails, evaluation, and a minimal browser interface.

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


<img width="1768" height="771" alt="08c5913b-1105-4cbf-81c6-5eb791e6803c" src="https://github.com/user-attachments/assets/02ba0af5-8a49-478a-b85c-c07327860d28" />

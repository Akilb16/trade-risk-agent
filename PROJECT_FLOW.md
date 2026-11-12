# Trade Risk Agent — End-to-End Project Flow

> **Implementation status update:** The current flow uses an actual LangGraph `StateGraph`, not only a conceptual custom function. The API is async, stress and limit routes are included, and optional provider, pgvector, MCP, and persistence modules are available. The default route remains offline and deterministic.

This document explains what happens from the moment a user enters a question until the project returns a response.

## 1. Whole-project view

```text
User
  |
  | browser frontend or command line
  v
FastAPI POST /ask  <-------------------- CLI: python -m src.cli
  |
  v
src.graph.run_agent(question, tool_args)
  |
  v
Input guardrail
  |---- invalid, unsafe, or off-topic --> escalation response
  |
  v
Retrieval: src.retrieval.search()
  |
  v
Route decision
  |---- policy/regulatory question --> answer from retrieved chunk
  |---- VaR question ---------------> compute_var()
  |---- Greeks question ------------> compute_greeks()
  |---- missing/ambiguous input ----> escalation response
  |
  v
Output with citation and trace
  |
  v
Output guardrail
  |---- invalid citation or PII ----> escalation response
  |
  v
JSON response to the user
```

## 2. Starting the application

The developer runs:

```powershell
cd A:\trade-risk-agent
uvicorn src.api:app --reload
```

Uvicorn starts the FastAPI application in `src/api.py`. FastAPI registers:

- `POST /ask` for agent requests.
- `/frontend/` for the browser interface.
- `/docs` for interactive API documentation.

The `--reload` option watches source files and restarts the development server after changes. It is convenient for development, not a production process manager.

## 3. Browser flow

The browser opens:

```text
http://127.0.0.1:8000/frontend/
```

The frontend consists of three plain files:

1. `frontend/index.html` creates the page structure.
2. `frontend/style.css` provides the minimalist layout.
3. `frontend/app.js` reads the question and optional JSON tool arguments.

When the user clicks **Run request**, JavaScript sends:

```http
POST /ask
Content-Type: application/json
```

with a body such as:

```json
{
  "question": "What is model risk?",
  "tool_args": null
}
```

The frontend waits for the JSON response and prints it in the response panel. It does not calculate VaR or Greeks itself; all business logic stays in the backend.

## 4. CLI flow

The command line uses:

```powershell
python -m src.cli "What is model risk?"
```

or:

```powershell
python -m src.cli "compute VaR" --tool-args '{"returns":[-0.1,0.02,0.01],"confidence":0.95,"horizon_days":1}'
```

`src/cli.py`:

1. Reads the question.
2. Reads optional tool arguments.
3. Parses strict JSON first.
4. Includes fallback handling for shells that remove quotes from object keys.
5. Calls the same `run_agent()` function used by the API.
6. Prints the response as formatted JSON.

Because the API and CLI call the same backend function, they should behave consistently.

## 5. FastAPI request flow

`src/api.py` defines an `AskRequest` Pydantic model:

```python
class AskRequest(BaseModel):
    question: str
    tool_args: dict | None = None
```

FastAPI receives the request and Pydantic checks that the body contains a string question and optional object-like tool arguments. The endpoint then calls:

```python
run_agent(req.question, req.tool_args)
```

FastAPI serializes the returned Python dictionary as JSON.

## 6. Agent orchestration flow

`src/graph.py` contains the current orchestration path. The main function is:

```python
run_agent(question, tool_args)
```

Conceptually, it carries these state values:

- User question.
- Retrieved chunks.
- Tool calls.
- Draft answer.
- Citation IDs.
- Confidence score.
- Route.

The current MVP represents this flow in a compact deterministic function. The project dependencies include LangGraph so this can later become an explicit state graph with nodes, conditional edges, and checkpointing.

## 7. Input guardrail flow

Before retrieval, `src/guardrails.py` runs `input_guardrail()`.

It checks:

1. Whether the question is empty.
2. Whether it exceeds the length limit.
3. Whether it contains likely PII.
4. Whether it appears related to the supported risk topics.

If any check fails, the function returns an escalation response immediately. The system does not call a calculation tool or produce a normal cited answer for that request.

Example reasons:

```text
empty_input
input_too_long
pii:email,pan
off_topic
```

The system records categories and reasons rather than intentionally printing raw PII values.

## 8. PII scanning flow

`scan_pii()` applies regular expressions for:

- Email addresses.
- Indian mobile numbers.
- PAN numbers.
- Aadhaar-like numbers.
- Card-like digit sequences.

It returns category names. It is a lightweight pattern filter, not proof that a value is genuine and not a replacement for a full data-loss-prevention system.

## 9. Retrieval flow

If the input passes, `src/retrieval.py` runs:

```python
search(question, k=3)
```

The current demo returns representative chunks containing:

- Chunk ID.
- Document ID.
- Section.
- Page.
- Text.
- Similarity-like score.

The demo is intentionally offline. The intended production retrieval flow is:

```text
PDF or HTML source
  -> clean text
  -> section-first chunks
  -> embedding model
  -> PostgreSQL + pgvector
  -> cosine similarity search
  -> top-k chunks
```

## 10. Policy-question flow

For a question such as:

```text
What is model risk?
```

the backend:

1. Passes the input guardrail.
2. Retrieves the SR 11-7 demo chunk.
3. Does not identify a calculation keyword.
4. Builds an answer from retrieved text.
5. Adds a citation such as `[cite:sr11-7-001]`.
6. Runs the output guardrail.
7. Returns the answer with route `answer`.

## 11. VaR flow

For a question containing `var`, the backend:

1. Passes input checks.
2. Retrieves context and obtains a citation ID.
3. Routes to `compute_var()`.
4. Checks that tool arguments exist.
5. Calculates the empirical lower-tail quantile.
6. Converts the negative return quantile into positive loss magnitude.
7. Applies square-root-of-time scaling.
8. Adds the result to a cited answer.
9. Runs the output guardrail.

The tool itself rejects:

- Empty returns.
- Confidence outside `(0, 1)`.
- Horizon less than one day.

## 12. Greeks flow

For a question containing `greek`, `delta`, `gamma`, `vega`, `theta`, or `rho`, the backend:

1. Passes input checks.
2. Retrieves context and obtains a citation ID.
3. Routes to `compute_greeks()`.
4. Checks that tool arguments exist.
5. Validates positive `S`, `K`, `T`, and `sigma`.
6. Validates `option_type` as `call` or `put`.
7. Calculates `d1` and `d2`.
8. Calculates all five Greeks.
9. Adds the result to a cited answer.
10. Runs the output guardrail.

## 13. Tool validation flow

`src/tools/schemas.py` defines Pydantic input models:

- `VaRInput`.
- `GreeksInput`.

The purpose of schemas is to make tool execution predictable. A future LLM may propose arguments, but the proposal must be parsed and validated before trusted code runs.

The safety principle is:

```text
model proposal -> schema validation -> deterministic function -> structured result
```

not:

```text
model text -> direct execution
```

## 14. Citation and output flow

After an answer is created, `output_guardrail()`:

1. Extracts citation IDs from `[cite:...]` markers.
2. Confirms at least one citation exists.
3. Confirms every cited ID belongs to the retrieved set.
4. Scans the answer for PII.

If validation fails, the normal answer is replaced with an escalation response.

This guarantees citation ID membership, but it does not yet prove that every claim is semantically supported. A production evaluation should add claim-level citation-support checks.

## 15. Response flow

A successful response looks like:

```json
{
  "answer": "... [cite:sr11-7-001]",
  "route": "answer",
  "citations": ["sr11-7-001"],
  "confidence": 0.84,
  "trace": {"tools": []}
}
```

The fields mean:

- `answer`: user-facing text.
- `route`: `answer` or `escalate`.
- `citations`: retrieved IDs used by the answer.
- `confidence`: current retrieval-based confidence estimate.
- `trace.tools`: tools called during processing.

## 16. Escalation flow

Escalation occurs when the system cannot safely provide a normal answer, for example:

- The question is off-topic.
- PII is detected.
- A VaR or Greeks request has no arguments.
- The output has no valid citation.
- The output contains PII.

Current behavior returns an escalation JSON response. A production implementation should write an event to a review queue or database table containing the question, safe draft, retrieved IDs, reason, timestamp, and status.

## 17. Evaluation flow

The evaluation pipeline is separate from normal user requests:

```text
evals/golden/golden.jsonl
  -> evals/run_eval.py
  -> run_agent(question)
  -> evals/judge.py
  -> scores and reasons
  -> evals/report/TIMESTAMP.json
```

Each JSONL line contains a question, reference idea, and expected source. The runner executes every case and saves the answer and score data.

The current starter dataset has five cases. The intended finished dataset has 30 cases covering direct lookup, paraphrased lookup, tool use, and escalation.

## 18. Regression flow

To evaluate a change:

1. Run the baseline dataset.
2. Save the timestamped report.
3. Change code, routing, retrieval, prompt, or model.
4. Run the same dataset again.
5. Compare scores per question.
6. Flag drops of two or more points.
7. Inspect the failed question, retrieved chunks, citation, route, and tool trace.

The average score alone is not enough because it can hide a serious failure on one question.

## 19. Test flow

Running:

```powershell
python -m pytest -q
```

uses `pytest.ini`, which adds the project root to Python’s import path. Pytest discovers tests in `tests/`:

- `test_var.py`: VaR positivity and horizon scaling.
- `test_greeks.py`: basic Greek shape and signs.
- `test_pii.py`: planted email, PAN, and Aadhaar detection.
- `test_graph.py`: citation behavior and VaR tool routing.

## 20. File responsibility map

```text
frontend/index.html       page structure
frontend/style.css        minimal styling
frontend/app.js           browser request logic

src/api.py                FastAPI app and /ask endpoint
src/cli.py                command-line entry point
src/graph.py              orchestration and route decisions
src/guardrails.py         input/output safety checks
src/retrieval.py          demo retrieval and chunk model
src/ingest.py             ingestion entry point placeholder
src/tools/var.py          historical VaR calculation
src/tools/greeks.py       Black-Scholes Greeks calculation
src/tools/schemas.py      tool input schemas

evals/golden/golden.jsonl evaluation examples
evals/judge.py            scoring component
evals/run_eval.py         evaluation runner
tests/                    automated tests
config.yaml               runtime configuration
docker-compose.yml        PostgreSQL + pgvector service
README.md                setup and overview
PROJECT_GUIDE.md         detailed learning guide
GLOSSARY.md              term dictionary
DECISIONS.md             architecture decisions
```

## 21. Current flow versus production flow

### Current implementation

- Fixed offline demo chunks.
- Keyword-based routing.
- Deterministic answers and calculations.
- Escalation schema and persistence helper are available; the default can still run without a database.
- A 30-item golden dataset is present.
- Deterministic judge-compatible scoring is present; a real LLM judge remains opt-in.

### Remaining production integration

- Downloaded and reviewed public documents.
- PDF/HTML parsing and section-aware chunking.
- Provider-backed embedding model and populated reviewed corpus.
- PostgreSQL and pgvector HNSW retrieval.
- LangGraph checkpoint persistence.
- External answering LLM.
- Separate judge model and human agreement study.
- Operational review queue and escalation workflow.
- Full traces, cost, token, and latency metrics.
- Human-labeled judge agreement and multiple regression baselines.

## 22. One-minute explanation

“The user can interact through a minimal frontend, CLI, or FastAPI endpoint. The request enters one shared backend path. An input guardrail checks relevance and PII, retrieval finds regulatory chunks, and routing decides between a cited policy answer, historical VaR, Black-Scholes Greeks, or escalation. Tools are deterministic and validated before execution. The output guardrail checks citations and PII before returning JSON. Separate evaluation scripts run a JSONL golden set, score responses, and save timestamped reports for regression testing.”


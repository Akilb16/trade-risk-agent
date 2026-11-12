# Trade Risk Agent — Complete Project Learning Guide

> **Implementation status update:** This guide was originally written for the first MVP. The project now also includes an actual LangGraph `StateGraph`, async API execution, optional OpenAI-compatible function calling, deterministic embeddings, pgvector search/database hooks, NumPy stress testing, limit checks, an optional MCP server, persistent escalation schema, pandas evaluation summaries, and a 30-item golden dataset. Where older sections say a feature is “planned,” interpret that as “the production connection or population step remains,” not that the code module is absent.

This guide explains what the project does, how its parts work, the meaning of the important terms, and the questions you should be prepared to answer about it.

## 1. What the project is

Trade Risk Agent is a small market-risk assistant. A user can ask a question about public regulatory material or request a quantitative calculation. The system then:

1. Checks the input for safety and relevance.
2. Retrieves relevant regulatory chunks.
3. Decides whether to answer from retrieved text, call a calculation tool, or escalate.
4. Validates and runs a tool when needed.
5. Requires the answer to contain a citation tied to retrieved material.
6. Checks the output again for invalid citations and PII.
7. Returns the answer, route, confidence, citations, and a small trace.

The project is an offline-first MVP. It has a deterministic demo corpus and does not currently require an external LLM API key. PostgreSQL, pgvector, LangGraph, and LangChain dependencies are included as the production-shaped extension points.

## 2. What the user can do

### Regulatory questions

The demo corpus contains representative material about:

- Basel market-risk capital requirements.
- Federal Reserve SR 11-7 model-risk management.
- RBI market-risk measurement and controls.

Example:

```text
What is model risk?
```

The answer includes retrieved text and a citation such as `[cite:sr11-7-001]`.

### Historical VaR

Example CLI request:

```powershell
python -m src.cli "compute VaR" --tool-args '{"returns":[-0.1,0.02,0.01],"confidence":0.95,"horizon_days":1}'
```

The tool returns a positive loss estimate. The implemented convention is historical VaR with square-root-of-time scaling.

### Black-Scholes Greeks

Example arguments:

```json
{
  "S": 100,
  "K": 100,
  "T": 1,
  "r": 0.05,
  "sigma": 0.2,
  "option_type": "call"
}
```

The tool returns delta, gamma, vega, theta, and rho.

### Guardrail behavior

The system can reject or escalate:

- Empty questions.
- Questions longer than the configured limit.
- Questions containing detected PII.
- Questions unrelated to the regulatory corpus or supported tools.
- Tool requests missing required arguments.
- Answers without a valid retrieved citation.
- Outputs containing detected PII.

### Browser testing

Start the server:

```powershell
uvicorn src.api:app --reload
```

Open `http://127.0.0.1:8000/frontend/`. The minimal frontend has examples for policy questions, VaR, Greeks, and guardrail testing.

## 3. Request lifecycle

```text
User question
  -> FastAPI or CLI
  -> input_guardrail
  -> retrieval.search
  -> route decision
      -> answer from retrieved chunk
      -> compute_var
      -> compute_greeks
      -> escalation response
  -> output_guardrail
  -> JSON response
```

The API response has this general shape:

```json
{
  "answer": "...",
  "route": "answer",
  "citations": ["sr11-7-001"],
  "confidence": 0.84,
  "trace": {"tools": []}
}
```

## 4. VaR in detail

### Meaning of VaR

VaR means Value at Risk. It estimates a loss threshold over a selected time horizon and confidence level.

For example, a one-day 95% VaR of 1,000 means that, under the chosen model and data assumptions, losses should exceed 1,000 on roughly 5% of comparable days. VaR does not say the maximum possible loss. It does not describe the size of losses beyond the threshold.

### Historical VaR

Historical VaR uses observed historical returns rather than assuming a normal distribution. The project:

1. Receives a list of returns.
2. Sorts the returns from worst to best.
3. Selects the `(1 - confidence)` quantile.
4. Converts a negative return quantile into a positive loss number.
5. Multiplies by `sqrt(horizon_days)`.

The square-root scaling is a convention, not a universal truth. It assumes returns behave sufficiently like independent observations with stable variance. Volatility clustering, autocorrelation, jumps, and regime changes can make this approximation inaccurate.

### Important VaR interview questions

**What is the difference between return VaR and currency VaR?**

The current tool returns a return-based loss measure. Currency VaR would multiply the loss fraction by a portfolio value.

**Why is VaR positive in the output?**

The tool represents risk as a positive loss magnitude, even though the underlying quantile is a negative return.

**What does 95% confidence mean?**

It means the selected threshold is intended to be exceeded by losses in approximately 5% of modeled observations. It is not a guarantee.

**What is the weakness of VaR?**

VaR does not describe the average loss beyond the threshold and can hide tail severity. Expected Shortfall is often used to measure the average tail loss.

**What validation should be added?**

Backtesting should compare predicted VaR with realized losses. Production work should also examine exceptions, data quality, stress periods, and model drift.

## 5. Greeks in detail

The Black-Scholes model prices European-style options under simplifying assumptions. The Greeks are sensitivities of option value to market variables.

### Inputs

- `S`: current underlying price.
- `K`: strike price.
- `T`: time to expiry in years.
- `r`: continuously compounded risk-free interest rate.
- `sigma`: volatility, expressed as a decimal such as `0.20` for 20%.
- `option_type`: `call` or `put`.

### Delta

Delta measures the approximate change in option price for a one-unit change in the underlying price.

- Call delta is generally between 0 and 1.
- Put delta is generally between -1 and 0.
- Delta is also sometimes used as a rough hedge ratio.

### Gamma

Gamma measures how quickly delta changes as the underlying price changes. It is the curvature of the option value with respect to the underlying.

High gamma means a hedge based only on delta can become inaccurate quickly.

### Vega

Vega measures sensitivity to implied volatility. A positive vega generally means the option becomes more valuable when volatility rises. The implementation returns the standard Black-Scholes vega scale per unit volatility, so users should document whether they interpret a one-point volatility move as `0.01` or a full `1.0`.

### Theta

Theta measures sensitivity to the passage of time. For many long options, theta is negative because time value decays. The sign and interpretation depend on position and conventions.

### Rho

Rho measures sensitivity to the interest rate. Calls and puts have different signs and magnitudes.

### Black-Scholes assumptions

The classic model assumes constant volatility and interest rates, lognormal underlying prices, continuous trading, no transaction costs, and European exercise. Real markets violate these assumptions, so the output is a model estimate rather than a guaranteed market value.

### Greek validation questions

**How do you test the formulas?**

The current tests check expected shape and sign: call delta is between 0 and 1, gamma is positive, and vega is positive. A production-quality version should add textbook reference values and finite-difference checks.

**What is a finite-difference check?**

Calculate the option value at slightly different inputs and compare the numerical derivative with the analytic Greek. For example, approximate delta as `(V(S+h) - V(S-h)) / (2h)`.

**Why validate `T` and `sigma`?**

The formulas divide by `sigma * sqrt(T)`. Non-positive values are mathematically invalid for this implementation.

## 6. PII detection

PII means personally identifiable information: information that can identify or help identify a person.

The project uses regular expressions to detect:

- Email addresses.
- Indian mobile numbers.
- PAN format: five letters, four digits, one letter.
- Aadhaar-like 12-digit numbers, including spaced variants.
- Card-like digit sequences.

The scanner returns category names such as `email`, `pan`, or `aadhaar`, not the raw detected value. This is important for logging because logs should not reproduce sensitive data.

### What PII detection does

It provides a lightweight pattern-based filter before and after the agent runs. A match causes the input or output guardrail to fail.

### What it does not do

Regex detection cannot prove that a string is truly a real identity number. It can produce false positives and false negatives. It may miss obfuscated, OCR-corrupted, encoded, or unusual formats.

### PII interview questions

**Why scan both input and output?**

The user may submit PII, and an answer or retrieved document may accidentally reproduce it. Both directions need protection.

**Why not log the raw PII?**

Logging raw sensitive data increases exposure and can violate privacy requirements. The project logs categories and reasons instead.

**How would you improve it?**

Use a dedicated data-loss-prevention service, checksums or tokenization, configurable regional patterns, allowlists, structured audit events, and security testing with synthetic and adversarial examples.

## 7. Citation behavior

Each retrieved chunk has a stable ID such as `sr11-7-001`. The answer uses the format:

```text
[cite:sr11-7-001]
```

The output guardrail extracts citation IDs from the answer and checks that:

1. At least one citation exists.
2. Every citation is a member of the retrieved chunk set.

This prevents the model from inventing a citation ID that was never retrieved.

### Citation questions

**Does a valid ID guarantee a correct answer?**

No. It proves only that the cited chunk was retrieved. Citation accuracy also requires checking whether the chunk actually supports the claim.

**What should production add?**

Store source URL, document version, page, section, retrieval score, and text offsets. Add a citation-support evaluation that asks whether each claim is entailed by the cited text.

## 8. Tool routing

Tool routing decides whether the request should use a calculation tool.

Current routing behavior:

- Questions containing `var` route to `compute_var`.
- Questions mentioning `greek`, `delta`, `gamma`, `vega`, `theta`, or `rho` route to `compute_greeks`.
- Other in-scope questions use retrieved regulatory text.
- Missing tool arguments result in escalation.
- Invalid tool values raise validation or calculation errors.

### Why route tools instead of asking an LLM to calculate?

Deterministic code is easier to test, reproduce, audit, and validate. An LLM can identify the requested operation and propose arguments, but the numerical calculation should happen in trusted code.

### Production tool-routing questions

**How should tool arguments be validated?**

Validate them against Pydantic models or JSON Schema before execution. Reject unknown, missing, negative, or out-of-range values.

**What if the model selects the wrong tool?**

Use explicit tool descriptions, routing tests, confidence thresholds, schema validation, and human escalation. Never silently execute an unsafe or ambiguous request.

**How should tool calls be audited?**

Record tool name, validated arguments after masking sensitive data, result status, duration, request ID, and escalation state.

## 9. JSONL golden dataset

JSONL means JSON Lines: one independent JSON object per line. It is useful for evaluation because each question can be streamed, edited, diffed, and processed independently.

Example:

```json
{"question":"What is model risk?","reference":"Potential adverse consequences...","expected_source":"sr11-7"}
```

The fields mean:

- `question`: test input.
- `reference`: human-written expected answer or key idea.
- `expected_source`: expected document family or `none` for escalation.

The current repository contains a 30-item starter dataset across direct policy lookup, paraphrased lookup, numeric tools, and out-of-scope/escalation cases. It still needs human review and an independently labeled subset before benchmark claims are made.

## 10. LLM-as-judge-compatible evaluation

An LLM judge is a separate model or scoring component that evaluates an answer against a reference and supporting text. The intended dimensions are:

1. Groundedness: are claims supported by retrieved material?
2. Correctness: does the answer match the reference?
3. Citation accuracy: does the citation support the claim?

Each dimension should be scored from 1 to 5 with a short reason. The current `evals/judge.py` has the compatible output shape, but uses a deterministic baseline judge rather than a real external LLM.

### Judge questions

**Why use a different judge model?**

Using the same model to answer and judge can create correlated errors and inflated scores. A different model or human labels reduce that risk.

**What is agreement with human labels?**

Have a human label a subset, such as 20 answers, using the same rubric. Compare judge labels with human labels using agreement percentage or a statistic such as Cohen's kappa for categorical labels.

**What makes a good rubric?**

It defines score anchors, distinguishes unsupported claims from incorrect claims, and gives examples of borderline cases.

## 11. Timestamped evaluation reports

`evals/run_eval.py` runs each golden question, records the answer and scores, then writes a file under `evals/report/` with a timestamped filename such as:

```text
20261111-153000.json
```

Timestamped reports preserve historical evidence. They allow you to compare a baseline prompt or retriever with an improved version instead of overwriting the previous result.

A useful report should include dataset version, code version, model name, retrieval configuration, average scores, per-question results, latency, tool usage, and escalation rate.

## 12. Regression evaluation design

Regression evaluation checks that a change did not make existing behavior worse.

Recommended process:

1. Run the golden set before a change.
2. Save the report as the baseline.
3. Change code, prompts, retrieval, or model settings.
4. Run the same dataset again.
5. Compare per-question scores.
6. Flag any item whose score drops by two or more points.
7. Inspect the retrieved chunks and answer before accepting the change.

Do not rely only on the average score. An average can hide a severe failure on one safety-critical question.

## 13. Backend technology explained

### Python

Python is the implementation language. It is used for the API, orchestration, calculations, guardrails, ingestion, tests, and evaluation scripts.

### FastAPI

FastAPI maps HTTP requests to Python functions. The `/ask` endpoint accepts a JSON request and returns a JSON response. Pydantic models define the request shape and generate API documentation.

### Uvicorn

Uvicorn is the ASGI server that runs the FastAPI application locally.

### Pydantic

Pydantic validates typed data at runtime. In this project it validates API requests and provides schemas for VaR and Greeks inputs.

### Regular expressions

Regular expressions describe text patterns. The guardrail uses them to detect likely PII and avoid sending or returning sensitive values.

### PostgreSQL

PostgreSQL is the relational database intended to store chunks, metadata, traces, and escalations.

### pgvector

pgvector adds vector columns and similarity operators to PostgreSQL. Text chunks can be represented as embedding vectors, then searched by cosine distance or another distance function.

### Docker Compose

Docker Compose describes local services in YAML. Here it starts PostgreSQL with the pgvector extension consistently across machines.

### LangGraph and LangChain Core

LangGraph is designed for stateful, branching agent workflows. A graph has state, nodes, and edges. LangChain Core supplies common runnable and message abstractions. They are dependencies in this MVP, while the current execution path is intentionally deterministic and lightweight.

### Pytest

Pytest discovers and runs tests. `pytest.ini` adds the project root to the Python import path so tests can import `src`.

### HTTPX

HTTPX is an HTTP client dependency suitable for testing the FastAPI endpoint without manually starting a browser.

## 14. Repository map

- `src/api.py`: FastAPI application and static frontend mounting.
- `src/cli.py`: command-line interface and tool-argument parsing.
- `src/graph.py`: request orchestration and route decisions.
- `src/guardrails.py`: input/output checks and PII patterns.
- `src/retrieval.py`: demo chunk model and retrieval seam.
- `src/tools/var.py`: historical VaR.
- `src/tools/greeks.py`: Black-Scholes Greeks.
- `src/tools/schemas.py`: Pydantic tool schemas.
- `src/ingest.py`: ingestion entry point placeholder.
- `frontend/`: minimal browser client.
- `evals/golden/golden.jsonl`: starter evaluation dataset.
- `evals/judge.py`: judge-compatible scoring function.
- `evals/run_eval.py`: evaluation runner and report writer.
- `tests/`: automated tests.
- `config.yaml`: model, retrieval, database, and embedding settings.
- `docker-compose.yml`: local pgvector database service.
- `DECISIONS.md`: architectural decision record.

## 15. What is implemented versus future work

Implemented now:

- Working CLI.
- Working FastAPI endpoint.
- Working minimal frontend.
- Deterministic regulatory demo retrieval.
- Historical VaR.
- Black-Scholes Greeks.
- Basic PII guardrails.
- Citation ID validation.
- Tool routing.
- Escalation responses.
- Unit tests.
- Starter evaluation harness.

Future production work:

- Downloading and cleaning the full public document corpus.
- PDF parsing and page-aware chunking.
- Real embeddings.
- PostgreSQL chunk storage and pgvector HNSW index.
- Actual LangGraph state graph and checkpoint persistence.
- External answering model and separate judge model.
- Persistent escalation table or review queue.
- More complete trace logging with tokens and node latency.
- Finite-difference Greeks tests.
- Full 30-item golden set and 20-item human agreement study.
- Two meaningful before/after regression reports.

## 16. Questions you should be ready to answer

### Architecture

- What happens from user input to final response?
- Why are numerical calculations implemented as tools?
- Where would you add a human review queue?
- How does the system prevent invented citations?
- What is the failure behavior for an off-topic question?

### Risk mathematics

- What is historical VaR?
- Why is the quantile `(1-confidence)`?
- Why use square-root-of-time scaling?
- What are the limitations of VaR?
- What do delta, gamma, vega, theta, and rho measure?
- What assumptions does Black-Scholes make?
- How would you verify a Greek with finite differences?

### Safety

- Which PII formats are detected?
- Why are input and output both scanned?
- What false positives or false negatives can regex detection have?
- Why should raw PII not be logged?
- What causes escalation?

### Retrieval and citations

- What is a chunk?
- Why preserve section and page metadata?
- What is an embedding?
- What is vector similarity search?
- What is the difference between citation existence and citation correctness?
- How would you evaluate retrieval independently?

### Evaluation

- What does each JSONL field mean?
- Why hand-write the golden set?
- Why use a separate judge?
- How do you measure judge/human agreement?
- What is a regression failure?
- Why inspect per-question results instead of only averages?

### Engineering

- Why use Pydantic schemas?
- Why use FastAPI and Uvicorn together?
- Why use Docker Compose?
- How does pytest find the `src` package?
- How would you add authentication, rate limits, and observability?
- What would you change before production?

## 17. A concise project explanation

“I built an offline-first market-risk assistant in Python. It retrieves regulatory chunks, requires citations from the retrieved set, routes quantitative requests to validated deterministic tools, calculates historical VaR and Black-Scholes Greeks, scans inputs and outputs for common PII formats, and escalates unsupported or unsafe requests. It has a FastAPI endpoint, CLI, minimal browser frontend, tests, and a JSONL-based evaluation harness. The current corpus and model are deterministic demo components; the next production steps are real PDF ingestion, embeddings, pgvector search, persistent LangGraph checkpoints, and a separately evaluated LLM judge.”

## 18. Updated implementation summary

The current codebase has progressed beyond the original MVP wording in earlier sections:

- `src/graph.py` builds an actual LangGraph `StateGraph` and has a fallback only for environments where LangGraph has not been installed.
- `src/api.py` exposes an async `/ask` handler and `run_agent_async()` runs the workflow without blocking the event loop.
- `src/llm.py` provides an optional OpenAI-compatible `/chat/completions` client with a system prompt and tool-call payload support.
- `src/embeddings.py` provides deterministic local embeddings; `src/retrieval.py` provides pgvector cosine search.
- `src/db.py` creates chunk, escalation, and trace tables.
- `src/tools/stress.py` and `src/tools/limits.py` add stress scenarios and risk-limit checks.
- `src/mcp_server.py` exposes VaR and Greeks with FastMCP when the optional dependency is installed.
- `evals/golden/golden.jsonl` now contains 30 cases and `evals/run_eval.py` produces pandas-backed summaries.

The remaining gaps are operational rather than absent concepts: populate the database with reviewed documents, configure provider credentials, connect provider embeddings, add checkpoint persistence, run a real judge, and obtain human labels. Personal certifications and employment history must be supplied by the candidate.


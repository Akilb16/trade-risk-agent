# Decision log

## Scope
Built a runnable, production-shaped reference implementation. The default path remains offline and deterministic, while LangGraph, async execution, provider integration, pgvector, MCP, persistence, stress testing, limits, and evaluation components are available as explicit modules.

## Model and provider
Kept `local-deterministic-v1` as the default so tests run without credentials. Added `OpenAICompatibleClient` with a system prompt, structured-output instruction, and optional function-calling payload when `LLM_API_KEY` is configured.

## Retrieval
Kept three representative offline chunks for zero-setup use. Added deterministic local embeddings, PostgreSQL/pgvector schema support, cosine-distance search, and database initialization hooks. Full PDF extraction and corpus population remain deployment work.

## VaR, Greeks, stress, and limits
Historical VaR returns a positive loss and uses square-root-of-time scaling. Black-Scholes Greeks validate inputs and calculate call/put sensitivities. NumPy-backed stress testing applies additive shocks, and limit checking reports `within_limit` or `breach`.

## Guardrails and escalation
Input checks cover length, topic, and common PII patterns. Output checks require citation IDs from the retrieved set and rescan for PII. PostgreSQL tables and `save_escalation()` now support persistent escalation, while the default response remains safe and local.

## Graph and API
The workflow is an actual LangGraph `StateGraph` with guard-input, retrieve, decide, tool/answer, and guard-output nodes. A local fallback preserves testability when LangGraph has not been installed. FastAPI `/ask` is async and the CLI shares the same graph.

## MCP
`src/mcp_server.py` exposes VaR and Greeks through FastMCP when `mcp[cli]` is installed. This is optional so the core application does not require an MCP host.

## Evaluation
The project now has 30 hand-written JSONL cases, pandas summary statistics, timestamped reports, and deterministic judge-compatible scores. A real external judge and 20 human labels still require credentials and human review; they are not fabricated.

## Remaining work
Add full PDF extraction and cleaning, populate reviewed documents, configure provider embeddings, connect production retrieval to the graph, add LangGraph checkpoint persistence, finite-difference Greek tests, claim-level citation entailment, and human agreement labels. FRM/CQF certification and regulated-employer experience are personal requirements and cannot be created by software.

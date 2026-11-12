# Trade Risk Agent Glossary

> **Implementation status update:** The glossary terms now map to implemented modules as well as planned integrations. LangGraph, async execution, local embeddings, pgvector hooks, MCP tools, stress testing, limits, pandas evaluation summaries, and the 30-item golden set are present. External provider credentials, populated regulatory documents, and human certification/experience remain user-owned or deployment-specific.

Definitions of the main finance, AI, backend, retrieval, safety, API, testing, and evaluation terms used by this project.

## Finance and risk

### Market risk
The possibility of loss caused by movements in market variables such as prices, rates, currencies, spreads, or volatility. This project focuses on regulatory market-risk material and two calculation tools.

### VaR / Value at Risk
A loss threshold defined by a confidence level and time horizon. A 95% one-day VaR is intended to be exceeded by losses in roughly 5% of comparable modeled observations. It is not a maximum-loss estimate.

### Historical VaR
VaR calculated from observed historical returns rather than a theoretical distribution. This project sorts returns, selects the `(1-confidence)` quantile, converts a negative return into a positive loss, and applies square-root-of-time scaling.

### Quantile
A value below which a specified fraction of observations fall. At 95% confidence, the lower-tail historical VaR quantile is the 5th percentile because `1 - 0.95 = 0.05`.

### Horizon
The time period measured by a risk calculation. The tool accepts `horizon_days`.

### Square-root-of-time scaling
An approximation that multiplies one-period volatility by the square root of the number of periods. It assumes reasonably stable, independent returns. The project uses it as a documented convention, not a universal law.

### Expected Shortfall
The average loss beyond the VaR threshold. It describes tail severity better than VaR, but is not implemented in this MVP.

### Return
The percentage or fractional change in an asset or portfolio value. VaR receives a list of historical returns.

### Option
A contract whose value depends on an underlying asset. A call gives the right to buy; a put gives the right to sell.

### Black-Scholes model
A mathematical model for European option prices and sensitivities. It uses underlying price, strike, time, interest rate, volatility, and option type. Its simplifying assumptions mean outputs are model estimates.

### Call / put
A call has the right to buy at the strike. A put has the right to sell at the strike. The tool accepts `option_type` as `call` or `put`.

### Underlying price (`S`)
The current price of the asset on which an option is based.

### Strike price (`K`)
The contractual exercise price of an option.

### Time to expiry (`T`)
Remaining time until expiration, expressed in years. It must be positive.

### Interest rate (`r`)
The risk-free rate input used by Black-Scholes.

### Volatility (`sigma`)
The expected variability of the underlying price, entered as a decimal such as `0.20` for 20%.

### Greeks
Sensitivities of an option’s value to market variables. This project calculates delta, gamma, vega, theta, and rho.

### Delta
Approximate option-price change for a one-unit change in the underlying. Call delta is usually between 0 and 1; put delta is usually between -1 and 0.

### Gamma
The rate at which delta changes as the underlying price changes. It measures option-value curvature.

### Vega
Sensitivity of option value to volatility. The project returns standard Black-Scholes vega.

### Theta
Sensitivity of option value to the passage of time. Long options often have negative theta because time value decays.

### Rho
Sensitivity of option value to the interest rate.

### Finite difference
A numerical derivative estimated from small input changes. It can independently check analytic Greeks, for example `(V(S+h)-V(S-h))/(2h)` for delta.

## Agent and retrieval

### Agent
A system that receives a goal, makes decisions, uses tools, and returns an outcome. Here it routes questions, retrieves text, calls risk tools, and applies guardrails.

### RAG / Retrieval-Augmented Generation
A design that retrieves source material before generating an answer. This MVP implements the retrieval-and-citation shape with a deterministic answer path rather than an external generative model.

### Corpus
The collection of documents searched by the system. Intended sources include Basel/BIS, Federal Reserve SR 11-7, and RBI material.

### Document
A source publication in the corpus, identified by a `doc_id` and source URL.

### Chunk
A manageable text segment extracted from a document. Chunks carry text and metadata such as document, section, page, ID, and score.

### Section-first chunking
Splitting around logical headings before applying a size limit. This preserves regulatory rule context better than arbitrary splitting alone.

### Chunk overlap
Repeated text between neighboring chunks. It reduces context loss at boundaries. The configured target is 50 tokens.

### Token
A unit of text used by language models and chunk-size settings. A token may be a word, part of a word, punctuation, or whitespace pattern.

### Embedding
A numerical vector representing text meaning. Similar texts should have nearby vectors. The project now has a deterministic local embedding fallback and a pgvector search hook; provider-backed embeddings remain an operational configuration choice.

### Vector similarity
A mathematical comparison between embeddings. Cosine similarity compares vector direction and is commonly used for semantic retrieval.

### pgvector
A PostgreSQL extension that stores vectors and supports similarity operators and indexes.

### HNSW index
Hierarchical Navigable Small World approximate-nearest-neighbor index. It can make vector search fast at scale and is planned for the full database implementation.

### Metadata
Data describing other data. Project chunk metadata includes source ID, section, page, citation ID, and retrieval score.

### Citation
A reference linking an answer claim to retrieved source material. The project uses IDs such as `[cite:sr11-7-001]`.

### Citation existence
Whether an answer contains a citation ID that exists in the retrieved set. The output guardrail checks this.

### Citation accuracy
Whether the cited text actually supports the answer claim. This requires semantic evaluation; a valid ID alone does not guarantee accuracy.

### Retrieval score
A number estimating how relevant a chunk is to the query. The demo uses fixed representative scores; production scores would come from vector search.

### Confidence score
An estimate of answer reliability. The current MVP uses the selected demo chunk score. Production confidence should combine retrieval quality, citation support, tool validity, and model uncertainty.

## Safety and controls

### Guardrail
A rule that blocks, modifies, or escalates unsafe or invalid behavior.

### Input guardrail
Checks a question before retrieval or tool execution. It handles empty input, excessive length, PII, and off-topic requests.

### Output guardrail
Checks the answer after processing. It requires a valid citation and scans the answer for PII.

### PII
Personally identifiable information: data that can identify or help identify a person.

### Regex / regular expression
A pattern language for matching text. The project uses regexes to detect likely emails, Indian mobile numbers, PAN, Aadhaar, and card-like sequences.

### PAN
Permanent Account Number, an Indian tax identifier. The project looks for the common five-letters, four-digits, one-letter format.

### Aadhaar
An Indian identity number. The project detects Aadhaar-like 12-digit values, including spaced forms.

### False positive
A value incorrectly detected as a match, such as an ordinary number flagged as card-like.

### False negative
Sensitive data that exists but was not detected, for example an obfuscated or unusual format.

### Escalation
Sending a request for higher-trust or human review instead of returning a normal answer. The MVP returns an escalation response; persistent review storage is future work.

### Validation
Checking whether data or behavior meets defined rules. This project validates tool inputs, citation IDs, PII behavior, and test outcomes.

### Tool
A deterministic function the agent can call. The tools are `compute_var` and `compute_greeks`.

### Tool routing
Mapping a question to a tool, retrieval answer, or escalation. Current routing uses keywords; production routing can use an LLM classifier plus strict schemas and tests.

### JSON Schema
A formal description of valid JSON fields, types, and constraints. The Pydantic tool models provide this validation structure.

## Backend and web technology

### Python
The implementation language for API, orchestration, calculations, guardrails, ingestion, tests, and evaluation.

### FastAPI
A Python web framework. It exposes `POST /ask` and generates interactive documentation at `/docs`.

### Uvicorn
An ASGI server that runs the FastAPI app. Start it with `uvicorn src.api:app --reload`.

### ASGI
Asynchronous Server Gateway Interface, the Python protocol between web servers and web applications.

### Pydantic
A runtime data-validation library. It validates API requests and VaR/Greeks inputs.

### REST endpoint
A URL plus an HTTP method used to perform an operation. The main endpoint is `POST /ask`.

### HTTP
The protocol used for browser and API communication.

### JSON
JavaScript Object Notation, a structured text format used by API requests and responses.

### CLI
Command-line interface. `src/cli.py` lets users run requests from PowerShell without a browser.

### Frontend
The user-facing browser application. This project uses plain HTML, CSS, and JavaScript with no frontend framework.

### PostgreSQL
An open-source relational database intended to store chunks, embeddings, traces, and escalations.

### Database driver
A library that lets Python communicate with a database. `psycopg` is the PostgreSQL driver dependency.

### Docker
A container platform for packaging and running services consistently.

### Docker Compose
A YAML-based definition for local multi-service environments. Here it starts PostgreSQL with pgvector.

### YAML
A human-readable configuration format. `config.yaml` stores model, retrieval, database, and embedding settings.

### LangGraph
A framework for stateful, branching agent workflows built from state, nodes, and edges. It is included as a production extension point; the current MVP uses lightweight deterministic orchestration.

### LangChain Core
Shared abstractions for language-model applications, messages, and runnable components. It is included for future LLM integration.

## Evaluation and engineering

### Unit test
A small automated test of one behavior or component. The project tests VaR, Greeks, PII, citations, and tool routing.

### Pytest
The Python test framework used to discover and run the tests.

### Golden dataset
A trusted set of examples with expected answers or labels. It is used to detect regressions in agent behavior.

### JSONL
JSON Lines: one JSON object per line. The golden dataset uses it because examples can be streamed and edited independently.

### Reference answer
A human-written expected answer or key idea for a golden question. It is used for correctness evaluation.

### Expected source
The document family expected to support a golden answer, such as `sr11-7` or `none` for an escalation case.

### LLM-as-judge
Using a language model to score another model’s answer. The intended dimensions are groundedness, correctness, and citation accuracy. The current judge is deterministic and compatible with that output structure.

### Groundedness
Whether claims are supported by the retrieved source text.

### Correctness
Whether the response matches the reference answer or expected conclusion.

### Judge agreement
How often the automated judge agrees with human labels. A 20-item human-labeled subset is recommended before trusting judge scores.

### Timestamped report
An evaluation output saved with the run date and time in its filename. It preserves historical results instead of overwriting them.

### Regression evaluation
Comparing a new run with a previous baseline on the same golden set. A per-question score drop, especially two or more points, should trigger inspection.

### Trace
A record of processing details. The MVP returns selected tools; production tracing should add model name, token counts, latency, retrieval IDs, and escalation status.

### Latency
Elapsed time from request start to response completion. It can also be measured per workflow node or tool.

### Model risk
The possibility of adverse consequences from incorrect, misused, poorly implemented, or misunderstood model outputs. SR 11-7 is a key public source in the project.

### Model validation
Independent testing of whether a model is appropriate, correctly implemented, and used within its limitations.

## Important distinctions

### Retrieval versus generation
Retrieval finds source text; generation writes an answer. Reliable systems need both relevant sources and an answer grounded in those sources.

### Valid citation versus supported citation
A valid citation ID exists in the retrieved set. A supported citation actually entails the claim. The current guardrail guarantees the first, not fully the second.

### Input validation versus model validation
Input validation checks shape and values. Model validation checks whether a quantitative model is conceptually and empirically appropriate.

### Deterministic tool versus LLM answer
A deterministic tool gives reproducible results for the same inputs. An LLM answer is flexible but probabilistic, so it needs grounding and evaluation.

### VaR versus Expected Shortfall
VaR is a threshold; Expected Shortfall is the average loss beyond the threshold.

## Implementation-status terms

### OpenAI-compatible client
A client that sends the standard chat-completions request shape to an OpenAI-compatible endpoint. `src/llm.py` supports system instructions, context, optional tool definitions, and response usage metadata. It is opt-in and requires `LLM_API_KEY`.

### Local embedding fallback
A deterministic hash-based vector representation used when no embedding provider is configured. It makes tests and offline demos reproducible; it is not a substitute for semantic production embeddings.

### Persistent escalation
Writing escalation records to durable storage instead of returning them only in memory. `src/db.py` defines the PostgreSQL table and `save_escalation()` helper.

### Stress test
Applying a deliberate market shock to returns or positions to examine adverse scenarios. `apply_stress()` currently applies an additive return shock using NumPy.

### Limit framework
A rule comparing a risk metric with an approved threshold. `check_limit()` reports whether the absolute value is within the limit or breaches it.

### MCP server
A Model Context Protocol server that exposes tools to MCP clients. `src/mcp_server.py` publishes VaR and Greeks through FastMCP when the optional MCP dependency is installed.

### State graph
A workflow made of typed state, nodes, and edges. The project’s LangGraph state graph passes the request through input guard, retrieval, decision, tool or answer, and output guard nodes.


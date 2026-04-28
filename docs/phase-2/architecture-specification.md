# Secure Agentic IT Support Copilot - Architecture Specification

Date: 2026-04-25
Phase: 2 - Architecture Lock, Threat Model, and Repository Plan
Lead team: Team 2 - Architecture and Agent Orchestration
Supporting teams: Team 1, Team 4, Team 6

## Architecture Decision

The application will use a layered Python-first architecture:

1. Streamlit demo UI for analyst workflows.
2. FastAPI backend for typed API contracts and future service integration.
3. Application services for ticket triage, RAG, command safety, KB generation, approvals, and audit logging.
4. LangGraph orchestration for the required agent flow.
5. Adapter layer for LLM providers, embeddings, vector stores, and persistence.
6. Local SQLite for audit records and approval records.
7. Local Chroma persistent storage for MVP vector retrieval, wrapped behind a replaceable vector-store interface.

This keeps the model from owning security decisions. The model may draft and reason, but deterministic application code owns validation, safety checks, approval status, audit logging, retrieval thresholds, and blocked command handling.

## Source-Grounded Research Summary

- LangGraph is documented as a low-level orchestration framework for long-running, stateful agents with persistence, human-in-the-loop, and streaming support.
- LangGraph interrupts allow graph execution to pause and wait for human input, while persistence/checkpointing saves graph state and resumes using a thread identifier. This matches the product's approval-gate requirement.
- FastAPI uses Python type declarations and Pydantic models to validate JSON request bodies and generate OpenAPI schemas for API documentation.
- FastAPI supports larger applications through modular routers, which fits the planned endpoint separation for tickets, documents, approvals, and evaluations.
- Streamlit reruns scripts on interaction and uses Session State to persist per-session UI state, so approval cards and ticket results should store only UI-safe IDs and response summaries in session state.
- Chroma supports persistent local clients for development and testing and can be replaced by server-backed storage later.
- Sentence Transformers support text embeddings and similarity operations, making them a practical local embedding default while preserving provider-embedding adapters.
- NCSC warns that prompt injection is not fully analogous to SQL injection because LLMs do not enforce a robust instruction/data boundary; the architecture therefore uses deterministic safeguards outside the model.
- OWASP LLM Top 10 2025 identifies prompt injection, sensitive information disclosure, excessive agency, vector/embedding weaknesses, misinformation, and unbounded consumption as risks relevant to this product.

## System Context

Actors:
- Help desk analyst.
- System administrator.
- Support manager.
- Security reviewer.
- Developer extender.

External systems in MVP:
- Optional LLM provider.
- Optional local embedding model.
- Local file corpus.
- Local SQLite database.
- Local vector store.

External systems deferred:
- Ticketing platforms such as ServiceNow, Jira Service Management, Zendesk, or Freshservice.
- Real command execution engines.
- Enterprise identity providers.
- Production object storage or database services.

## Runtime Components

### Streamlit UI

Responsibilities:
- Ticket intake form.
- Retrieval source display.
- Final answer display.
- Command suggestion cards.
- Approval and rejection workflow.
- KB article generation screen.
- Settings screen for local provider/configuration status.

Constraints:
- No command execution.
- Store only lightweight IDs and display state in Session State.
- Avoid storing secrets in Session State.
- Show uncertainty, citations, approval status, and safety findings visibly.

### FastAPI Backend

Responsibilities:
- Typed request/response contracts.
- Run ticket workflow.
- Ingest documents.
- Retrieve source chunks.
- Generate KB article.
- Create/update approval records.
- Read audit events.
- Health and configuration diagnostics.

Constraints:
- Pydantic schemas define public contracts.
- Service layer owns business logic.
- API must not expose raw secrets or unnecessary PII.

### LangGraph Agent Flow

Required nodes:
- intake.
- classify.
- retrieve.
- reason.
- draft_solution.
- safety_check.
- final_answer.

The flow is deterministic at the graph boundary. Nodes may call model adapters, but the safety checker and approval layer are normal application code.

### RAG Pipeline

Responsibilities:
- Load sanitized documents.
- Extract text.
- Chunk text with metadata.
- Embed chunks.
- Store vectors.
- Retrieve candidate chunks.
- Filter or flag suspicious chunks.
- Score retrieval sufficiency.
- Produce citation objects.

MVP vector store:
- Chroma persistent local store.

Fallback:
- In-memory keyword retrieval for tests when embeddings/vector DB are unavailable.

### Model Adapter Layer

Responsibilities:
- Provide a stable interface for classification, reasoning, drafting, summarization, and KB generation.
- Support deterministic local/test implementation.
- Support provider-backed implementation when credentials are configured.

Constraints:
- Provider keys come only from environment variables.
- No secrets in prompts beyond necessary task context.
- Do not send real private documents in sample/demo mode.

### Safety Layer

Responsibilities:
- Prompt injection detection.
- Secret and PII heuristics.
- Command risk classification.
- Retrieval sufficiency check.
- Citation coverage check.
- Final-answer safety findings.

Constraints:
- Deterministic checks must run after model output.
- High-risk or blocked commands cannot become approved by model output alone.
- Retrieved content is evidence, not instruction.

### Approval and Audit Layer

Responsibilities:
- Create approval records for commands and other actions.
- Track approval status: pending, approved, rejected, expired.
- Record audit events for workflow runs, retrieval, safety findings, command suggestions, and approval decisions.

MVP:
- Records approvals only.
- Does not execute actions.

### Persistence

SQLite:
- Approval records.
- Audit events.
- Workflow run metadata.
- Optional document catalog metadata.

Chroma:
- Chunk embeddings.
- Chunk metadata.
- Source references.

File system:
- Sanitized sample corpus.
- Evaluation fixtures.

## Module Map

| Module | Responsibility |
| --- | --- |
| `src/itsupport_copilot/api` | FastAPI app factory, routers, dependencies |
| `src/itsupport_copilot/app_services` | Ticket workflow service, ingestion service, approval service, audit service |
| `src/itsupport_copilot/agents` | LangGraph graph builder, node implementations, state reducers |
| `src/itsupport_copilot/rag` | loaders, chunking, embedding adapters, vector store adapters, retrieval scoring |
| `src/itsupport_copilot/models` | LLM adapter interface, deterministic test model, provider adapters |
| `src/itsupport_copilot/safety` | command safety, prompt injection, privacy redaction, grounding checks |
| `src/itsupport_copilot/schemas` | Pydantic request/response/domain schemas |
| `src/itsupport_copilot/storage` | SQLite repositories, migrations/bootstrap, document catalog |
| `src/itsupport_copilot/evals` | evaluation runner and scoring helpers used by `evals/` |
| `app/streamlit_app.py` | Streamlit UI entrypoint |
| `api/main.py` | FastAPI ASGI entrypoint |
| `tests/` | unit, integration, safety, and API tests |
| `evals/` | evaluation cases, fixtures, rubrics, runner config |
| `docs/` | architecture, security, evaluation, release docs |

## Data Flow

1. Analyst submits ticket through Streamlit or FastAPI.
2. API validates request using Pydantic schema.
3. Ticket workflow service creates a workflow run and audit event.
4. LangGraph executes intake and classify nodes.
5. Retrieve node queries RAG service.
6. RAG service retrieves chunks and marks citations, scores, and prompt-injection flags.
7. Reason and draft nodes synthesize evidence using model adapter.
8. Command suggester proposes commands only as structured suggestions.
9. Safety checker evaluates grounding, privacy, prompt injection, and command risk.
10. Final answer is returned with citations and approval requirements.
11. Approval service creates pending approval records for proposed actions.
12. Human can approve, reject, or expire records.
13. Audit service records all material events.

## Key Architecture Decisions

### Decision 1: Streamlit plus FastAPI

Decision:
- Build both a Streamlit demo and a FastAPI backend.

Rationale:
- Streamlit gives a practical local demo UI.
- FastAPI provides typed contracts, API docs, testing via TestClient, and future integration boundaries.

Tradeoff:
- Slightly more wiring than Streamlit-only, but far more GitHub-ready and extensible.

### Decision 2: Chroma for MVP Vector Store

Decision:
- Use Chroma persistent client for MVP local development, behind a vector-store adapter.

Rationale:
- Chroma supports local persistence for development and testing.
- Adapter boundary keeps pgvector or FAISS viable later.

Tradeoff:
- Production deployments may need a server-backed or database-native vector store.

### Decision 3: Deterministic Safety Outside the Model

Decision:
- Safety checker, command blocking, approval records, and audit logs live in application code.

Rationale:
- Prompt injection risk cannot be solved purely inside prompts.
- Deterministic controls reduce impact even if model output is manipulated.

Tradeoff:
- Some safe-but-unusual commands may be conservatively flagged.

### Decision 4: No Command Execution in MVP

Decision:
- MVP suggests and records approvals only.

Rationale:
- User requirement permits MVP to limit itself to suggestions and approval recording.
- This avoids operational risk while proving the safety workflow.

Tradeoff:
- Demo shows approval state, not execution.

### Decision 5: Replaceable Model and Embedding Adapters

Decision:
- Define stable interfaces for LLM and embedding behavior.

Rationale:
- Repository must run without private credentials.
- Tests need deterministic behavior.

Tradeoff:
- More initial interface work, but lower long-term coupling.

## Nonfunctional Requirements

- Local setup must work with documented commands.
- Tests must run without provider credentials.
- Sample data must be sanitized.
- CI must run linting and tests.
- Audit logs must avoid raw secrets.
- Safety checks must be repeatable.
- Retrieval must include citations and bad-retrieval fallback.
- API contracts must be versionable.
- No automatic command execution.

## Open Questions Deferred to Later Phases

- Exact LLM provider and model selection for optional live mode.
- Whether to add authentication in MVP or leave it documented as production hardening.
- Whether to include Docker in Phase 8 or document virtualenv-only setup.
- Whether Chroma remains default after Phase 3 implementation benchmarking.

## Research Sources

- LangGraph overview: https://docs.langchain.com/oss/python/langgraph/overview
- LangGraph interrupts: https://docs.langchain.com/oss/python/langgraph/human-in-the-loop
- LangGraph persistence: https://docs.langchain.com/oss/python/langgraph/persistence
- FastAPI request body and Pydantic validation: https://fastapi.tiangolo.com/he/tutorial/body/
- FastAPI larger applications: https://fastapi.tiangolo.com/tr/tutorial/bigger-applications/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- Pydantic serialization: https://pydantic.dev/docs/validation/latest/concepts/serialization/
- Streamlit Session State: https://docs.streamlit.io/develop/concepts/architecture/session-state
- Streamlit forms: https://docs.streamlit.io/develop/concepts/architecture/forms
- Chroma Python client: https://docs.trychroma.com/reference/python/client
- Sentence Transformers docs: https://www.sbert.net/
- NCSC prompt injection guidance: https://www.ncsc.gov.uk/blog-post/prompt-injection-is-not-sql-injection
- OWASP LLM01 Prompt Injection: https://genai.owasp.org/llmrisk/llm01-prompt-injection/
- OWASP LLM02 Sensitive Information Disclosure: https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/

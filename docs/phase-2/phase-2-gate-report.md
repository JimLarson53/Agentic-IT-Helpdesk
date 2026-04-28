# Phase 2 Gate Report

Date: 2026-04-25
Phase: 2 - Architecture Lock, Threat Model, and Repository Plan

## 1. Phase Name

Architecture Lock, Threat Model, and Repository Plan

## 2. AI LLM Agent Used

Claude Systems Architect Agent was recommended.

Substitution used: Claude is not available in this Codex session, so the strongest available Codex reasoning model was used as the closest equivalent for Phase 2 architecture synthesis.

## 3. Lead Team

Team 2 - Architecture and Agent Orchestration

## 4. Supporting Teams

- Team 1 - Product, ITSM Research, and Requirements
- Team 4 - Safety, Security, and Human Approval
- Team 6 - Release, Documentation, Compliance, and GitHub Authority

## 5. Objective

Lock the architecture, LangGraph workflow design, RAG boundaries, API contracts, approval gates, audit model, threat model, repository layout, and architecture diagram source before implementation begins.

## 6. Research Performed

Sources reviewed:
- LangGraph overview, interrupts, and persistence documentation.
- FastAPI documentation for Pydantic request bodies, larger applications, and testing.
- Pydantic serialization documentation.
- Streamlit Session State and forms documentation.
- Chroma Python client documentation.
- Sentence Transformers documentation.
- NCSC prompt injection guidance.
- OWASP LLM01 Prompt Injection and LLM02 Sensitive Information Disclosure.
- Phase 1 requirements artifacts.

## 7. Key Findings

- LangGraph is a strong fit for the required stateful flow and future human-in-the-loop pause/resume behavior.
- Human approval should be modeled deterministically in application services, not delegated to model output.
- FastAPI plus Pydantic gives strong request/response contracts and generated API docs.
- Streamlit is appropriate for the local analyst demo but must store only UI-safe state.
- Chroma persistent local storage is suitable for MVP RAG, provided it is behind an adapter.
- Prompt injection must be treated as a residual architectural risk; deterministic controls should reduce impact.
- RAG must include citation metadata, retrieval sufficiency, prompt-injection flags, and bad-retrieval fallback.

## 8. Decisions Made

- Use Streamlit plus FastAPI.
- Use LangGraph Graph API for the required workflow.
- Keep true LangGraph interrupt-based approval as a future execution-enabled path; MVP records approval without execution.
- Use Chroma as default local vector store behind an adapter.
- Use SQLite for audit and approval records.
- Use deterministic test model and replaceable provider adapters.
- Keep command safety, grounding checks, prompt-injection checks, and privacy redaction outside the model.
- No command execution endpoints in MVP.

## 9. Alternatives Considered

- Streamlit-only architecture: rejected because it lacks durable API contracts and integration readiness.
- FastAPI-only architecture: rejected for MVP demo because Streamlit provides faster analyst workflow iteration.
- FAISS default vector store: deferred because Chroma's local persistence and metadata handling are more convenient for MVP; FAISS remains a possible adapter later.
- Provider-only embeddings: rejected because tests and local demos must run without credentials.
- Model-owned approval: rejected because approval must be deterministic and auditable.
- Auto-execution after approval: rejected for MVP because execution materially increases operational risk.

## 10. Risks and Mitigations

- Prompt injection: mitigate with untrusted-content boundaries, injection detection, evidence-only retrieval, deterministic safety checks, and tests.
- Unsafe commands: mitigate with risk taxonomy, blocked patterns, required approval records, and no execution path.
- Sensitive data leakage: mitigate with redaction, sample-only data, audit minimization, and privacy documentation.
- Bad retrieval: mitigate with retrieval sufficiency thresholds, citations, conflict detection, and uncertainty fallback.
- Dependency risk: mitigate with pinned dependencies, CI, and release-phase dependency review.
- MVP complexity: mitigate with clear module boundaries and adapter interfaces.

## 11. Deliverables Produced

- `docs/phase-2/architecture-specification.md`
- `docs/phase-2/langgraph-state-and-flow.md`
- `docs/phase-2/api-contracts-and-repository-plan.md`
- `docs/phase-2/threat-model-and-approval-gates.md`
- `docs/phase-2/architecture-diagram.mmd`
- `docs/phase-2/data-flow-diagram.mmd`
- `docs/phase-2/phase-2-gate-report.md`

## 12. Acceptance Criteria Check

- Architecture specification: met.
- Module map: met.
- Data flow diagram: met.
- LangGraph state design: met.
- API contract summary: met.
- Repository file layout: met.
- Threat model: met.
- Approval gate design: met.
- Architecture diagram source: met.

## 13. Signoff Status

Team 2 signoff: complete.
Team 1 requirements alignment: complete.
Team 4 preliminary security architecture signoff: complete, with implementation validation required in Phases 4, 6, and 7.
Team 6 repository planning signoff: complete, with final release authority reserved for Phase 8.

## 14. Gate Result: PASS or BLOCKED

PASS

## 15. Handoff Recommendation

Proceed to Phase 3 only after explicit user approval. Phase 3 should implement the RAG data pipeline and knowledge engineering foundation: ingestion, chunking, metadata, embeddings, vector store adapter, retrieval, citations, bad-retrieval detection, and retrieval test fixtures.

## 16. Recommended Next Phase Agent

GPT-5 Codex Implementation Agent with RAG Engineer focus.

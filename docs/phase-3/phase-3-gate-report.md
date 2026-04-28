# Phase 3 Gate Report

Date: 2026-04-25
Phase: 3 - RAG Data Pipeline and Knowledge Engineering

## 1. Phase Name

RAG Data Pipeline and Knowledge Engineering

## 2. AI LLM Agent Used

GPT-5 Codex Implementation Agent with RAG Engineer focus.

## 3. Lead Team

Team 3 - Development and Integration

## 4. Supporting Teams

- Team 2 - Architecture and Agent Orchestration
- Team 4 - Safety, Security, and Human Approval
- Team 5 - Evaluation, QA, and Red Team

## 5. Objective

Implement the RAG foundation for Secure Agentic IT Support Copilot: document ingestion, metadata-aware chunking, embeddings, vector storage, retrieval, citations, prompt-injection flags, bad-retrieval safeguards, sanitized sample corpus, and retrieval tests.

## 6. Research Performed

Phase 3 used the Phase 2 architecture research and current official/library references:
- LangGraph architecture constraints from Phase 2 for future graph integration.
- Chroma Python client documentation for local vector-store direction.
- Sentence Transformers documentation for embedding adapter direction.
- Pydantic documentation for schema serialization and validation.
- OWASP LLM prompt-injection and sensitive-information disclosure guidance.
- NCSC guidance that prompt injection is a residual architecture risk requiring deterministic safeguards.

Local environment research:
- `python` and `py` are not on PATH in this PowerShell shell.
- Bundled Python is available at `C:\Users\crazy\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe`.
- Bundled Python includes Pydantic 2.13.3.
- Bundled Python does not include pytest, Chroma, or sentence-transformers.

## 7. Key Findings

- The RAG foundation must work without provider keys or network downloads.
- A deterministic local hashing embedder is necessary for repeatable tests and offline development.
- A local vector store is needed as the Phase 3 fallback while preserving the Chroma/pgvector-ready adapter boundary.
- Retrieved documents must carry source metadata, citation location, prompt-injection flags, and sensitive-pattern flags.
- Bad retrieval must be explicit through structured assessment rather than hidden in the final answer.

## 8. Decisions Made

- Implemented Pydantic schemas for RAG documents, chunks, citations, results, and retrieval assessment.
- Implemented text loaders for `.md`, `.txt`, and `.rst`.
- Implemented metadata-aware chunking with source IDs, chunk IDs, character ranges, token estimates, sensitivity, document type, prompt-injection flags, and sensitive-pattern flags.
- Implemented `HashingEmbeddingModel` for deterministic local embeddings.
- Implemented optional `SentenceTransformersEmbeddingModel` adapter that activates only if installed.
- Implemented `LocalVectorStore` with cosine search and JSON persistence.
- Implemented `Retriever` with citation generation, document type filtering, retrieval sufficiency, unsafe-result counting, and bad-retrieval reasons.
- Added sanitized sample corpus and retrieval fixtures.
- Added unittest-based tests that are also pytest-collectable.

## 9. Alternatives Considered

- Chroma-only implementation: deferred because Chroma is not installed locally and tests must run offline.
- sentence-transformers-only embeddings: rejected for Phase 3 because the dependency is not installed and would require downloads.
- Plain keyword search only: rejected because the architecture needs a vector-store abstraction and embedding path.
- No persistence test: rejected because vector-store persistence is part of local RAG readiness.
- pytest-only tests: deferred because pytest is not installed in the bundled runtime; unittest tests remain compatible with pytest later.

## 10. Risks and Mitigations

- Lower retrieval quality from hashing embeddings: mitigated by adapter design so transformer/provider embeddings can replace it later.
- Prompt injection in retrieved content: mitigated by chunk-level flags and retrieval assessment; later phases must enforce these flags in LangGraph safety checks.
- Sensitive data in documents: mitigated with sensitive-pattern flags and redaction helpers.
- Bad retrieval: mitigated with `RetrievalAssessment` and insufficient-evidence reasons.
- Dependency drift: mitigated by a minimal core dependency set and optional RAG extras.
- Test write permissions: mitigated by running persistence verification with approved filesystem access.

## 11. Deliverables Produced

Code:
- `pyproject.toml`
- `.gitignore`
- `src/itsupport_copilot/schemas/rag.py`
- `src/itsupport_copilot/rag/loaders.py`
- `src/itsupport_copilot/rag/chunking.py`
- `src/itsupport_copilot/rag/embeddings.py`
- `src/itsupport_copilot/rag/vector_store.py`
- `src/itsupport_copilot/rag/retrieval.py`
- `src/itsupport_copilot/safety/prompt_injection.py`
- `src/itsupport_copilot/safety/privacy.py`

Sample data and fixtures:
- `sample_data/docs/kb/windows-vpn-error-809.md`
- `sample_data/docs/troubleshooting/linux-disk-space.md`
- `sample_data/docs/it-docs/password-reset-policy.md`
- `sample_data/docs/resumes/synthetic-helpdesk-resume.md`
- `sample_data/docs/job-descriptions/synthetic-systems-admin-job.md`
- `sample_data/docs/security/malicious-prompt-injection-sample.md`
- `evals/fixtures/retrieval_cases.json`

Tests:
- `tests/unit/test_rag_pipeline.py`

Documentation:
- `docs/phase-3/rag-pipeline.md`
- `docs/phase-3/retrieval-fixtures.md`
- `docs/phase-3/phase-3-gate-report.md`

## 12. Acceptance Criteria Check

- Ingestion: met.
- Metadata-aware chunking: met.
- Document metadata and sensitivity: met.
- Embedding adapter: met.
- Vector store/local fallback: met.
- Retrieval: met.
- Citation tracking: met.
- Source display metadata: met.
- Prompt-injection flags: met.
- Bad-retrieval detection: met.
- Retrieval test fixtures: met.
- Sanitized sample corpus: met.

Verification:
- Command run with approved filesystem access:
  - `$env:PYTHONPATH='src'; python -m unittest discover -s tests -p 'test_*.py'`
- Result:
  - 7 tests ran.
  - 7 tests passed.

## 13. Signoff Status

Team 3 RAG implementation signoff: complete.
Team 2 architecture alignment: complete.
Team 4 safety alignment: complete for Phase 3, with full validation required in Phase 7.
Team 5 retrieval test coverage signoff: complete for Phase 3, with broader evaluation required in Phase 6.

## 14. Gate Result: PASS or BLOCKED

PASS

## 15. Handoff Recommendation

Proceed to Phase 4 only after explicit user approval. Phase 4 should implement the LangGraph agent flow and tools: ticket summarizer, command suggester, KB generator, safety checker integration, and approval state handling.

## 16. Recommended Next Phase Agent

GPT-5 Codex Implementation Agent.

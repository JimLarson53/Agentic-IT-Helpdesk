# Phase 3 RAG Pipeline Design and Implementation

Date: 2026-04-25
Phase: 3 - RAG Data Pipeline and Knowledge Engineering

## Implemented Components

- Text document loading for `.md`, `.txt`, and `.rst` files.
- Document type inference for IT docs, troubleshooting notes, KB articles, resumes, job descriptions, sample tickets, and security notes.
- Stable source IDs derived from sanitized content and filename.
- Metadata-aware chunking with source filename, document type, sensitivity, character location, chunk ID, approximate token count, and tags.
- Prompt-injection flagging during chunk creation.
- Sensitive-pattern detection and redaction helpers.
- Deterministic hashing embedding model for offline tests and credential-free local demos.
- Optional sentence-transformers adapter that activates only when the optional dependency is installed.
- Local in-process vector store with JSON persistence.
- Retrieval service with citation generation, document-type filtering, retrieval sufficiency checks, unsafe-result counting, and bad-retrieval fallback reasons.
- Sanitized sample corpus.
- Retrieval fixtures and unit tests.

## Architecture Fit

Phase 3 implements the RAG foundation described in Phase 2 without implementing later-phase LangGraph, command tools, approvals, or UI. The RAG service is deliberately usable from future LangGraph nodes and FastAPI services.

## Bad-Retrieval Behavior

Retrieval responses include `RetrievalAssessment`:
- `sufficient`.
- `reason`.
- `top_score`.
- `result_count`.
- `safe_result_count`.
- `unsafe_result_count`.
- `min_score`.
- `query_terms`.

Current reasons:
- `sufficient`.
- `empty_query`.
- `no_results`.
- `only_unsafe_results`.
- `top_score_below_threshold`.
- `no_safe_results_above_threshold`.

## Citation Behavior

Each result includes:
- Source ID.
- Chunk ID.
- Filename.
- Document type.
- Character location.
- Retrieval score.
- Excerpt.

The future answer-generation layer must use only results marked `used_in_answer=True` for grounded claims.

## Safety Notes

Retrieved text is still untrusted. Phase 3 flags suspicious chunks but does not rely on the model to enforce safety. Later phases must keep these flags in the LangGraph state and final answer safety checks.

The malicious prompt-injection sample is intentional test data and must not be used as policy.

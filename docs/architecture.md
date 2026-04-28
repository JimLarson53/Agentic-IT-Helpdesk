# Architecture

Date: 2026-04-25

## Overview

Secure Agentic IT Support Copilot is a Python-first local MVP with a FastAPI backend, Streamlit demo UI, deterministic RAG pipeline, LangGraph-compatible support workflow, safety checks, approval records, audit logging, and repeatable evaluations.

See the Mermaid source in `docs/architecture-diagram.mmd`.

## Runtime Components

- `app/streamlit_app.py`: analyst-facing demo UI for ticket analysis, citations, commands, approvals, KB draft generation, and settings/status.
- `api/main.py`: ASGI entrypoint for Uvicorn.
- `src/itsupport_copilot/api/app.py`: FastAPI application factory and router registration.
- `src/itsupport_copilot/app_services/bootstrap.py`: shared service container used by API, UI, and tests.
- `src/itsupport_copilot/agents/`: support workflow state, nodes, sequential runner, and optional LangGraph graph builder.
- `src/itsupport_copilot/rag/`: loaders, metadata-aware chunking, local embeddings, vector store, retrieval assessment, citations, and bad-retrieval fallback.
- `src/itsupport_copilot/tools/`: ticket summarizer, command suggester, and KB generator.
- `src/itsupport_copilot/safety/`: command safety, prompt injection detection, privacy redaction, and grounding checks.
- `src/itsupport_copilot/storage/sqlite.py`: SQLite persistence for local audit events and approval records.

## Agent Flow

The required workflow is implemented as:

1. `intake`: records a redacted workflow start event.
2. `classify`: classifies category, severity, platform, and command need.
3. `retrieve`: builds a redacted query and retrieves relevant chunks.
4. `reason`: summarizes evidence, assumptions, missing information, and confidence.
5. `draft_solution`: drafts troubleshooting steps, command suggestions, and KB notes.
6. `safety_check`: checks command risk, privacy, prompt injection, and grounding.
7. `final_answer`: produces a cited answer with approval requirements.

`SupportAgentRunner.build_langgraph()` builds the same node order as a LangGraph graph when LangGraph is installed. The deterministic sequential runner is used in tests and CI to keep the suite offline and repeatable.

## RAG Pipeline

The RAG pipeline loads sanitized Markdown files, infers document type from path, assigns metadata, chunks text with source locations, flags prompt injection and sensitive patterns, embeds chunks using deterministic hashing embeddings, and stores them in a local vector store.

Retrieval responses include citations, scores, safety flags, and an assessment. Unsafe chunks are not used as grounded evidence. When retrieval is insufficient, the final answer states uncertainty instead of inventing a source-grounded solution.

## Approval And Audit

Command suggestions create approval records only when they are not blocked. Approval records include action, risk, rationale, affected system/data, approving human, timestamps, status, and execution status. Execution status remains `not_applicable`; no execution engine exists in the MVP.

Audit events and approval records are stored in SQLite at `data/app.sqlite3` for local development. The `data/` directory is gitignored.

## API Boundaries

FastAPI exposes local demo endpoints for:

- Health/status.
- Ticket analysis and summarization.
- Retrieval search.
- Command safety checks.
- Approval decisions.
- KB draft generation.
- Document ingestion.
- Redacted audit event listing.

Public response models exclude raw ticket payloads, full internal chunks, and local source paths.

## Production Limitations

The current repository is GO for local MVP/demo use, not direct production exposure. Production requires authentication, RBAC, TLS, rate limits, request size limits, tenant-aware retrieval authorization, durable backup/retention policy, encryption at rest, monitoring, deployment hardening, and legal/privacy review for real support or HR data.

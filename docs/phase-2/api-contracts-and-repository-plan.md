# API Contracts and Repository Plan

Date: 2026-04-25
Phase: 2 - Architecture Lock, Threat Model, and Repository Plan

## API Boundary Principles

- FastAPI routes are thin and delegate to services.
- All request and response bodies use Pydantic schemas.
- API responses never expose secrets.
- Commands are returned as suggestions, never execution results.
- Approval records can be created and updated, but approval does not trigger command execution in MVP.
- Audit logs expose redacted summaries and metadata, not raw sensitive payloads.

## API Contract Summary

### Health

`GET /health`

Purpose:
- Return app health and configuration readiness.

Response:
- `status`.
- `version`.
- `llm_mode`.
- `embedding_mode`.
- `vector_store_status`.
- `database_status`.

### Ticket Workflow

`POST /api/v1/tickets/analyze`

Purpose:
- Run the full LangGraph ticket workflow.

Request:
- `title`.
- `description`.
- `affected_user`.
- `affected_system`.
- `environment`.
- `urgency`.
- `attempted_fixes`.
- `requester_context`.
- `generate_kb_draft`.

Response:
- `run_id`.
- `classification`.
- `summary`.
- `retrieved_sources`.
- `final_answer`.
- `command_suggestions`.
- `approval_records`.
- `safety_findings`.

### Ticket Summary

`POST /api/v1/tickets/summarize`

Purpose:
- Generate structured ticket summary without full RAG flow.

Response sections:
- Issue summary.
- Affected user/system.
- Symptoms.
- Attempted fixes.
- Likely category.
- Severity.
- Missing information.
- Next best action.

### Document Ingestion

`POST /api/v1/documents/ingest`

Purpose:
- Ingest sanitized local documents from configured corpus paths.

Request:
- `paths`.
- `document_type`.
- `sensitivity`.
- `tags`.

Response:
- `ingestion_run_id`.
- `documents_processed`.
- `chunks_created`.
- `chunks_indexed`.
- `warnings`.

MVP note:
- Upload endpoints are deferred. Local path ingestion is simpler and safer for repository demo data.

### Retrieval

`POST /api/v1/retrieval/search`

Purpose:
- Search indexed corpus for a query.

Request:
- `query`.
- `document_types`.
- `top_k`.
- `min_score`.

Response:
- `results`.
- `retrieval_assessment`.

### Command Safety

`POST /api/v1/commands/check`

Purpose:
- Risk-score proposed commands.

Request:
- `shell`.
- `target_os`.
- `command`.
- `intent`.

Response:
- `risk_level`.
- `blocked`.
- `findings`.
- `requires_human_approval`.
- `safe_alternative`.

### KB Generation

`POST /api/v1/kb/generate`

Purpose:
- Generate KB article from ticket and resolution context.

Request:
- `ticket_summary`.
- `resolution_notes`.
- `environment`.
- `source_ids`.

Response:
- `article`.
- `citations`.
- `safety_findings`.

### Approval Records

`POST /api/v1/approvals`

Purpose:
- Create an approval record for a proposed action.

Request:
- `proposed_action`.
- `action_type`.
- `risk_level`.
- `rationale`.
- `affected_system_or_data`.

Response:
- `approval_id`.
- `status`.
- `created_at`.

`POST /api/v1/approvals/{approval_id}/decision`

Purpose:
- Approve or reject a pending action.

Request:
- `decision`: approved or rejected.
- `approving_human`.
- `comment`.

Response:
- `approval_id`.
- `status`.
- `decided_at`.

### Audit

`GET /api/v1/audit/events`

Purpose:
- Return redacted audit events for local review.

Query parameters:
- `run_id`.
- `event_type`.
- `limit`.

Response:
- `events`.

## Repository File Layout

```text
secure-agentic-it-support-copilot/
  README.md
  pyproject.toml
  .env.example
  .gitignore
  .github/
    workflows/
      ci.yml
  api/
    main.py
  app/
    streamlit_app.py
  src/
    itsupport_copilot/
      __init__.py
      api/
        __init__.py
        app.py
        dependencies.py
        routers/
          __init__.py
          approvals.py
          audit.py
          commands.py
          documents.py
          health.py
          kb.py
          retrieval.py
          tickets.py
      agents/
        __init__.py
        graph.py
        nodes.py
        state.py
      app_services/
        __init__.py
        approval_service.py
        audit_service.py
        document_service.py
        kb_service.py
        ticket_service.py
      rag/
        __init__.py
        chunking.py
        embeddings.py
        loaders.py
        retrieval.py
        vector_store.py
      models/
        __init__.py
        base.py
        deterministic.py
        provider.py
      safety/
        __init__.py
        command_safety.py
        grounding.py
        privacy.py
        prompt_injection.py
      schemas/
        __init__.py
        approvals.py
        audit.py
        commands.py
        documents.py
        kb.py
        retrieval.py
        tickets.py
      storage/
        __init__.py
        database.py
        repositories.py
      evals/
        __init__.py
        runner.py
        scoring.py
  sample_data/
    README.md
    docs/
    tickets/
  tests/
    unit/
    integration/
    safety/
    api/
  evals/
    cases/
    fixtures/
    rubrics/
  docs/
    architecture.md
    architecture-diagram.mmd
    security.md
    evaluation.md
    phase-1/
    phase-2/
  demo/
    demo-script.md
```

## Dependency Direction

Allowed:
- API routes -> services -> agents/rag/safety/storage.
- Agents -> schemas, rag, safety, models.
- RAG -> schemas, safety metadata, model embedding adapters.
- Services -> storage repositories.
- UI -> API client or service facade.

Not allowed:
- Safety layer depending on Streamlit.
- Storage layer depending on model provider.
- RAG layer approving actions.
- Model adapter mutating audit or approval records.
- LangGraph nodes executing shell commands.

## Testing Layout

Unit tests:
- command safety patterns.
- prompt injection detector.
- privacy redaction.
- chunking.
- retrieval scoring.
- Pydantic schemas.

Integration tests:
- full ticket workflow with deterministic model.
- ingestion and retrieval with sample docs.
- approval record lifecycle.
- FastAPI TestClient endpoints.

Safety tests:
- destructive command blocked.
- credential exfiltration command blocked.
- prompt injection in retrieved doc ignored.
- insufficient retrieval triggers uncertainty.

Evaluation:
- fixture-driven test cases with rubrics and pass/fail thresholds.

## CI Plan

GitHub Actions should run:
- Python setup.
- Dependency install.
- Ruff lint.
- Pytest test suite.
- Evaluation smoke run.

Provider-backed tests must be skipped unless credentials are explicitly configured.

# Agentic IT Support

Agentic IT Support is a Python-first IT support assistant for help desk analysts, system administrators, MSPs, security-conscious IT teams, and technical staffing teams. It triages tickets, retrieves relevant support knowledge, drafts grounded troubleshooting responses, suggests risk-scored PowerShell or Bash commands, generates KB article drafts, and records human approval before any command or action.

The MVP is intentionally local and safe by default:

- No command execution.
- No ticket mutation or external API action.
- No real secrets or private documents in the repository.
- Deterministic local reasoning and embeddings for offline tests.
- SQLite-backed local audit and approval records.
- Source citations when retrieved evidence is used.
- Safe uncertainty when retrieval is insufficient.

## Features

- Metadata-aware document ingestion for IT docs, troubleshooting notes, KBs, resumes, job descriptions, and sample tickets.
- RAG pipeline with chunking, deterministic local embeddings, retrieval scores, citations, prompt-injection flags, and bad-retrieval fallback.
- Required support flow: intake -> classify -> retrieve -> reason -> draft solution -> safety check -> final answer.
- LangGraph-compatible graph builder plus deterministic sequential runner for local CI.
- Ticket summarizer, command suggester, KB article generator, command safety checker, approval records, audit logging, FastAPI API, and Streamlit UI.
- Evaluation suite for hallucination, unsafe commands, bad retrieval, prompt injection, answer quality, citation correctness, classification accuracy, and approval workflow behavior.

## Repository Layout

```text
api/                         FastAPI ASGI entrypoint
app/                         Streamlit demo UI
docs/                        Architecture, security, evaluation, phase reports
evals/                       Evaluation case fixtures
sample_data/                 Sanitized demo corpus
src/itsupport_copilot/       Application package
tests/                       Unit, integration, security, and evaluation tests
.github/workflows/ci.yml     GitHub Actions CI
```

## Requirements

- Python 3.12 or newer.
- No model provider key is required for the deterministic local MVP.
- Optional future provider keys must be stored in `.env`, never committed.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
```

## Run The API

```powershell
$env:PYTHONPATH="src"
uvicorn api.main:app --reload --host 127.0.0.1 --port 8000
```

Open `http://127.0.0.1:8000/docs` for interactive OpenAPI docs.

## Run The Streamlit UI

```powershell
$env:PYTHONPATH="src"
streamlit run app/streamlit_app.py
```

Open the URL printed by Streamlit, usually `http://localhost:8501`.

## Run Tests And Evals

```powershell
$env:PYTHONPATH="src"
python -m unittest discover -s tests -p "test_*.py"
python -m itsupport_copilot.evals.runner
python -m compileall -q src app api tests
python -m pip check
```

If `ruff` is installed:

```powershell
python -m ruff check .
```

## Safety Model

Commands are suggestions only. Every suggestion includes shell, target OS, intent, command text, risk level, explanation, expected output, rollback/recovery note, and approval requirement. Blocked commands cannot be approved. Approval records are durable audit records; they do not execute anything.

Retrieved documents are treated as untrusted evidence, not instructions. Prompt injection found in tickets or retrieved chunks is surfaced as a safety finding and unsafe retrieved chunks are not used as grounded evidence.

## Data Handling

The repository contains only sanitized sample data. Real tickets, resumes, job descriptions, and internal IT documents can contain sensitive personal or business data. Production use requires authentication, RBAC, tenant-aware retrieval authorization, retention/deletion workflows, encryption at rest, secure secret handling, and qualified legal/privacy review.

## Documentation

- [Architecture](docs/architecture.md)
- [Security](docs/security.md)
- [Evaluation](docs/evaluation.md)
- [Deployment](docs/deployment.md)
- [Demo Script](demo/demo-script.md)
- [Phase 8 Release Checklist](docs/phase-8/release-checklist.md)

## Release Status

Team 6 release decision: GO for GitHub-ready local MVP and demo repository. Production deployment is not approved until the documented hardening items are completed.

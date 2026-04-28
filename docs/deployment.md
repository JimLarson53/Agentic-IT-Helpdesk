# Setup And Deployment Guide

Date: 2026-04-25

## Local Development

1. Create and activate a virtual environment.
2. Install the project in editable mode.
3. Copy `.env.example` to `.env`.
4. Run tests and evaluations.
5. Start FastAPI and/or Streamlit.

Windows:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
$env:PYTHONPATH="src"
python -m unittest discover -s tests -p "test_*.py"
python -m itsupport_copilot.evals.runner
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
cp .env.example .env
export PYTHONPATH=src
python -m unittest discover -s tests -p "test_*.py"
python -m itsupport_copilot.evals.runner
```

## FastAPI

```powershell
$env:PYTHONPATH="src"
uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```

Open `http://127.0.0.1:8000/docs`.

## Streamlit

```powershell
$env:PYTHONPATH="src"
streamlit run app/streamlit_app.py
```

Open the URL printed by Streamlit.

## Local Data

The app creates `data/app.sqlite3` for audit and approval records. The `data/` directory is ignored by Git. Delete it to reset local audit/approval state.

## Production Hardening Required

Do not expose this MVP directly to untrusted networks. Before production deployment:

- Add authentication and RBAC.
- Add tenant-aware authorization on retrieval and document ingestion.
- Add TLS, trusted proxy configuration, request size limits, and rate limits.
- Add encryption at rest, backups, retention, deletion, and re-indexing workflows.
- Add centralized logging without secrets.
- Add secret management outside `.env`.
- Pin and review dependencies.
- Complete legal/privacy review for real tickets, resumes, job descriptions, and internal IT documentation.

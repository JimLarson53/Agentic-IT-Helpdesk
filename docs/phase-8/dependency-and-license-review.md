# Dependency And License Review

Date: 2026-04-25

## Runtime Dependencies

- FastAPI: backend API.
- LangGraph: optional graph builder for the required support workflow.
- Pydantic: typed schemas and response contracts.
- Streamlit: local analyst demo UI.
- Uvicorn: local ASGI server.

## Optional RAG Dependencies

- ChromaDB: future vector store adapter.
- sentence-transformers: future embedding adapter.

The MVP uses deterministic local hashing embeddings and an in-memory vector store by default, so provider keys and model downloads are not required for tests.

## Development Dependencies

- httpx: FastAPI TestClient support.
- pytest: optional test runner compatibility.
- ruff: linting.

## Standard Library Storage

SQLite persistence uses Python's standard `sqlite3` module and does not add a runtime dependency.

## License

The repository includes an MIT License in `LICENSE`.

## Review Result

- `python -m pip install -e ".[dev]"` completed successfully.
- `python -m pip check` reported no broken requirements in the local validation runtime.
- `python -m ruff check .` passed after local dev dependencies were installed.

## Release Notes

Dependency versions are specified as ranges for developer convenience. Before production deployment, generate a lockfile or constraints file, review licenses and vulnerabilities, and pin deployable artifacts according to organizational policy.

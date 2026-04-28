"""FastAPI application factory."""

from __future__ import annotations

from pathlib import Path

from itsupport_copilot.app_services.bootstrap import create_app_container


def create_app(project_root: str | Path | None = None):
    """Create the FastAPI app and attach the shared service container."""

    try:
        from fastapi import FastAPI
    except ImportError as exc:
        raise RuntimeError("FastAPI is not installed. Install project dependencies.") from exc

    from itsupport_copilot.api.routers import (
        approvals,
        audit,
        commands,
        documents,
        health,
        kb,
        retrieval,
        tickets,
    )

    app = FastAPI(
        title="Secure Agentic IT Support Copilot",
        version="0.1.0",
        description="Secure IT support copilot with RAG, command safety, approval records, and audit logging.",
    )
    app.state.container = create_app_container(project_root)

    app.include_router(health.router)
    app.include_router(tickets.router, prefix="/api/v1")
    app.include_router(retrieval.router, prefix="/api/v1")
    app.include_router(commands.router, prefix="/api/v1")
    app.include_router(approvals.router, prefix="/api/v1")
    app.include_router(kb.router, prefix="/api/v1")
    app.include_router(documents.router, prefix="/api/v1")
    app.include_router(audit.router, prefix="/api/v1")
    return app

"""FastAPI dependency helpers."""

from __future__ import annotations

from fastapi import Request

from itsupport_copilot.app_services.bootstrap import AppContainer


def get_container(request: Request) -> AppContainer:
    return request.app.state.container

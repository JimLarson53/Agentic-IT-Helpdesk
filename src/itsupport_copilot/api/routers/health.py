"""Health and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer

router = APIRouter(tags=["health"])


@router.get("/health")
def health(request: Request, container: AppContainer = Depends(get_container)) -> dict[str, object]:
    del request
    return container.status()

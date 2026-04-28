"""Audit endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.schemas.audit import AuditEvent

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("/events", response_model=list[AuditEvent])
def list_events(
    request: Request,
    run_id: str | None = None,
    limit: int = 50,
    container: AppContainer = Depends(get_container),
) -> list[AuditEvent]:
    del request
    events = container.audit_service.list_events(run_id=run_id)
    return events[-limit:]

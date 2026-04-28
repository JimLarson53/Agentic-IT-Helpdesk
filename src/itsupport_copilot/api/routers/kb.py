"""KB generation endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.schemas.kb import KBArticle
from itsupport_copilot.schemas.tickets import TicketInput

router = APIRouter(prefix="/kb", tags=["kb"])


@router.post("/generate", response_model=KBArticle)
def generate_kb(
    ticket: TicketInput,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> KBArticle:
    del request
    response = container.runner.run(ticket)
    return container.kb_service.generate_from_workflow(response)

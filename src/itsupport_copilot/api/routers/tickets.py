"""Ticket workflow endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from itsupport_copilot.agents.nodes import classify_ticket
from itsupport_copilot.api.dependencies import get_container
from itsupport_copilot.app_services.bootstrap import AppContainer
from itsupport_copilot.schemas.tickets import TicketInput, TicketSummary, TicketWorkflowResponse
from itsupport_copilot.tools.ticket_summarizer import summarize_ticket

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post("/analyze", response_model=TicketWorkflowResponse)
def analyze_ticket(
    ticket: TicketInput,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> TicketWorkflowResponse:
    del request
    return container.runner.run(ticket)


@router.post("/summarize", response_model=TicketSummary)
def summarize(
    ticket: TicketInput,
    request: Request,
    container: AppContainer = Depends(get_container),
) -> TicketSummary:
    del request, container
    classification = classify_ticket(ticket.title, ticket.description, ticket.urgency.value)
    return summarize_ticket(ticket, classification)

"""Ticket workflow service."""

from __future__ import annotations

from itsupport_copilot.agents.graph import SupportAgentRunner
from itsupport_copilot.rag import Retriever
from itsupport_copilot.schemas.tickets import TicketInput, TicketWorkflowResponse


class TicketWorkflowService:
    """Application service wrapper around the support agent runner."""

    def __init__(self, *, retriever: Retriever | None = None) -> None:
        self.runner = SupportAgentRunner(retriever=retriever)

    def analyze(self, ticket: TicketInput) -> TicketWorkflowResponse:
        return self.runner.run(ticket)

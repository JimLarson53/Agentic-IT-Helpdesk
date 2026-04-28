"""Support agent state."""

from __future__ import annotations

from uuid import uuid4

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.approvals import ApprovalRecord
from itsupport_copilot.schemas.commands import CommandSuggestion
from itsupport_copilot.schemas.rag import RetrievalResponse
from itsupport_copilot.schemas.tickets import (
    Classification,
    DraftSolution,
    FinalAnswer,
    ReasoningSummary,
    SafetyFinding,
    TicketInput,
    TicketSummary,
)


class SupportAgentState(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run_{uuid4().hex[:16]}")
    ticket: TicketInput
    ticket_summary: TicketSummary | None = None
    classification: Classification | None = None
    retrieval: RetrievalResponse | None = None
    reasoning_summary: ReasoningSummary | None = None
    draft_solution: DraftSolution | None = None
    command_suggestions: list[CommandSuggestion] = Field(default_factory=list)
    safety_findings: list[SafetyFinding] = Field(default_factory=list)
    approval_records: list[ApprovalRecord] = Field(default_factory=list)
    final_answer: FinalAnswer | None = None
    audit_metadata: dict[str, object] = Field(default_factory=dict)

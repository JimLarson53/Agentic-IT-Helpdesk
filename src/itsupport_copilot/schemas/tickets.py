"""Ticket workflow schemas."""

from __future__ import annotations

from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.approvals import ApprovalRecord
from itsupport_copilot.schemas.commands import CommandSuggestion
from itsupport_copilot.schemas.rag import Citation, RetrievalResponse


class Urgency(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Platform(str, Enum):
    WINDOWS = "windows"
    LINUX = "linux"
    MACOS = "macos"
    CLOUD = "cloud"
    NETWORK = "network"
    APPLICATION = "application"
    IDENTITY = "identity"
    UNKNOWN = "unknown"


class TicketInput(BaseModel):
    title: str
    description: str
    affected_user: str | None = None
    affected_system: str | None = None
    environment: str | None = None
    urgency: Urgency = Urgency.MEDIUM
    attempted_fixes: str | None = None
    requester_context: str | None = None
    generate_kb_draft: bool = False


class TicketSummary(BaseModel):
    issue_summary: str
    affected_user_or_system: str
    symptoms: list[str]
    attempted_fixes: list[str]
    likely_category: str
    severity: Severity
    missing_information: list[str]
    next_best_action: str


class Classification(BaseModel):
    issue_type: str
    category: str
    severity: Severity
    platform: Platform
    likely_domain: str
    requires_command_suggestions: bool = False
    security_incident_suspected: bool = False
    escalation_recommended: bool = False
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class ReasoningSummary(BaseModel):
    evidence_summary: str
    assumptions: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    support_strategy: str
    escalation_reason: str | None = None
    confidence: float = Field(ge=0.0, le=1.0, default=0.5)


class DraftSolution(BaseModel):
    user_response: str
    troubleshooting_steps: list[str]
    kb_notes: list[str] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)


class SafetyFinding(BaseModel):
    finding_id: str = Field(default_factory=lambda: f"safety_{uuid4().hex[:16]}")
    finding_type: str
    severity: str
    message: str
    affected_item_id: str | None = None
    recommended_action: str


class FinalAnswer(BaseModel):
    summary: str
    recommended_steps: list[str]
    commands: list[CommandSuggestion] = Field(default_factory=list)
    citations: list[Citation] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)
    escalation: str | None = None
    approval_requirements: list[str] = Field(default_factory=list)
    safety_notes: list[str] = Field(default_factory=list)


class TicketWorkflowResponse(BaseModel):
    run_id: str
    ticket: TicketInput = Field(exclude=True)
    summary: TicketSummary
    classification: Classification
    retrieval: RetrievalResponse
    reasoning_summary: ReasoningSummary
    draft_solution: DraftSolution
    command_suggestions: list[CommandSuggestion]
    safety_findings: list[SafetyFinding]
    approval_records: list[ApprovalRecord]
    final_answer: FinalAnswer

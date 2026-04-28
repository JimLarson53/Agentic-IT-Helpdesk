"""Schemas for human approval records."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.commands import RiskLevel


class ActionType(str, Enum):
    COMMAND = "command"
    TICKET_UPDATE = "ticket_update"
    FILE_OPERATION = "file_operation"
    EXTERNAL_API_ACTION = "external_api_action"
    WORKFLOW_AUTOMATION = "workflow_automation"
    KB_PUBLICATION = "kb_publication"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


class ExecutionStatus(str, Enum):
    NOT_APPLICABLE = "not_applicable"
    NOT_CONFIGURED = "not_configured"
    NOT_EXECUTED = "not_executed"


class ApprovalRecord(BaseModel):
    approval_id: str = Field(default_factory=lambda: f"appr_{uuid4().hex[:16]}")
    run_id: str
    proposed_action: str
    action_type: ActionType
    risk_level: RiskLevel
    rationale: str
    affected_system_or_data: str
    approving_human: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    decided_at: datetime | None = None
    expires_at: datetime = Field(default_factory=lambda: datetime.now(UTC) + timedelta(hours=24))
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
    execution_status: ExecutionStatus = ExecutionStatus.NOT_APPLICABLE
    safety_findings: list[str] = Field(default_factory=list)


class ApprovalDecision(BaseModel):
    decision: ApprovalStatus
    approving_human: str
    comment: str | None = None

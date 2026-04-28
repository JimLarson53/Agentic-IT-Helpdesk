"""Schemas for command suggestions and command safety."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class ShellType(str, Enum):
    POWERSHELL = "powershell"
    BASH = "bash"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    BLOCKED = "blocked"


class CommandSafetyFinding(BaseModel):
    rule_id: str
    message: str
    severity: str = "medium"


class CommandSafetyResult(BaseModel):
    risk_level: RiskLevel
    blocked: bool = False
    findings: list[CommandSafetyFinding] = Field(default_factory=list)
    requires_human_approval: bool = True
    safe_alternative: str | None = None


class CommandCheckRequest(BaseModel):
    shell: ShellType
    target_os: str
    command: str
    intent: str


class CommandSuggestion(BaseModel):
    command_id: str
    shell: ShellType
    target_os: str
    intent: str
    command: str
    risk_level: RiskLevel
    explanation: str
    expected_output: str
    rollback_or_recovery: str
    requires_human_approval: bool = True
    blocked_reason: str | None = None
    approval_id: str | None = None

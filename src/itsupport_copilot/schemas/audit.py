"""Schemas for redacted audit logging."""

from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, Field


class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: f"audit_{uuid4().hex[:16]}")
    run_id: str
    event_type: str
    actor: str = "system"
    summary: str
    redacted_metadata: dict[str, object] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

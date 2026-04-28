"""Schemas for generated knowledge base articles."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.rag import Citation


class RevisionHistoryEntry(BaseModel):
    version: str = "0.1"
    author: str = "Secure Agentic IT Support Copilot"
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    notes: str = "Initial generated draft for human review."


class KBArticle(BaseModel):
    title: str
    problem: str
    environment: str
    symptoms: list[str]
    root_cause: str | None = None
    resolution_steps: list[str]
    verification_steps: list[str]
    prevention_notes: list[str]
    related_sources: list[Citation] = Field(default_factory=list)
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=lambda: [RevisionHistoryEntry()])

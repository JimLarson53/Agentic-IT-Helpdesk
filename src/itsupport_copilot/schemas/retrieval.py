"""API request schemas for retrieval."""

from __future__ import annotations

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.rag import DocumentType


class RetrievalSearchRequest(BaseModel):
    query: str = Field(min_length=1)
    document_types: list[DocumentType] = Field(default_factory=list)
    top_k: int = Field(default=5, ge=1, le=20)
    min_score: float | None = Field(default=None, ge=-1.0, le=1.0)

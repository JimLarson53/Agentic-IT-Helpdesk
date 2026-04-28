"""Document ingestion API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field

from itsupport_copilot.schemas.rag import Sensitivity


class DocumentIngestionRequest(BaseModel):
    paths: list[str] = Field(default_factory=list)
    sensitivity: Sensitivity = Sensitivity.INTERNAL
    tags: list[str] = Field(default_factory=list)


class DocumentIngestionResult(BaseModel):
    ingestion_run_id: str
    documents_processed: int
    chunks_created: int
    chunks_indexed: int
    warnings: list[str] = Field(default_factory=list)

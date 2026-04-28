"""Schemas for document ingestion, chunking, retrieval, and citations."""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class DocumentType(str, Enum):
    IT_DOCUMENTATION = "it_documentation"
    TROUBLESHOOTING_NOTE = "troubleshooting_note"
    KB_ARTICLE = "kb_article"
    RESUME = "resume"
    JOB_DESCRIPTION = "job_description"
    SAMPLE_TICKET = "sample_ticket"
    SECURITY_NOTE = "security_note"
    UNKNOWN = "unknown"


class Sensitivity(str, Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class DocumentMetadata(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    source_id: str = Field(..., description="Stable identifier derived from sanitized content.")
    source_path: str | None = Field(default=None, exclude=True, description="Original local source path.")
    filename: str
    document_type: DocumentType = DocumentType.UNKNOWN
    sensitivity: Sensitivity = Sensitivity.INTERNAL
    title: str | None = None
    tags: list[str] = Field(default_factory=list)


class LoadedDocument(BaseModel):
    metadata: DocumentMetadata
    content: str


class DocumentChunk(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    chunk_id: str
    source_id: str
    text: str
    metadata: DocumentMetadata
    chunk_index: int
    location: str
    start_char: int
    end_char: int
    token_count: int
    prompt_injection_flags: list[str] = Field(default_factory=list)
    sensitive_flags: list[str] = Field(default_factory=list)

    @property
    def is_unsafe(self) -> bool:
        return bool(self.prompt_injection_flags)


class Citation(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    source_id: str
    chunk_id: str
    filename: str
    document_type: DocumentType
    location: str
    score: float
    excerpt: str


class RetrievalResult(BaseModel):
    chunk: DocumentChunk = Field(exclude=True)
    score: float
    citation: Citation
    prompt_injection_flags: list[str] = Field(default_factory=list)
    sensitive_flags: list[str] = Field(default_factory=list)
    used_in_answer: bool = False


class RetrievalAssessment(BaseModel):
    sufficient: bool
    reason: str
    top_score: float = 0.0
    result_count: int = 0
    safe_result_count: int = 0
    unsafe_result_count: int = 0
    min_score: float
    query_terms: list[str] = Field(default_factory=list)


class RetrievalResponse(BaseModel):
    query: str
    results: list[RetrievalResult]
    assessment: RetrievalAssessment

"""Metadata-aware chunking for local RAG corpora."""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass

from itsupport_copilot.safety.privacy import find_sensitive_patterns
from itsupport_copilot.safety.prompt_injection import detect_prompt_injection
from itsupport_copilot.schemas.rag import DocumentChunk, LoadedDocument


@dataclass(frozen=True)
class ChunkingConfig:
    max_chars: int = 900
    overlap_chars: int = 120
    min_chars: int = 80

    def __post_init__(self) -> None:
        if self.max_chars <= 0:
            raise ValueError("max_chars must be positive")
        if self.overlap_chars < 0:
            raise ValueError("overlap_chars cannot be negative")
        if self.overlap_chars >= self.max_chars:
            raise ValueError("overlap_chars must be smaller than max_chars")
        if self.min_chars < 0:
            raise ValueError("min_chars cannot be negative")


def count_tokens_approx(text: str) -> int:
    """Approximate token count for chunk metadata without tokenizer dependencies."""

    return len(re.findall(r"[A-Za-z0-9_@./:-]+", text))


def _chunk_id(source_id: str, chunk_index: int, text: str) -> str:
    digest = hashlib.sha256(f"{source_id}:{chunk_index}:{text}".encode("utf-8")).hexdigest()
    return digest[:24]


def _choose_breakpoint(text: str, start: int, hard_end: int, config: ChunkingConfig) -> int:
    if hard_end >= len(text):
        return hard_end

    search_start = min(hard_end, start + max(config.min_chars, config.max_chars // 2))
    candidates = [
        text.rfind("\n\n", search_start, hard_end),
        text.rfind("\n", search_start, hard_end),
        text.rfind(". ", search_start, hard_end),
        text.rfind("; ", search_start, hard_end),
    ]
    breakpoint = max(candidates)
    if breakpoint > start:
        return breakpoint + 1
    return hard_end


def chunk_document(
    document: LoadedDocument,
    config: ChunkingConfig | None = None,
) -> list[DocumentChunk]:
    """Split a loaded document into citation-ready chunks."""

    chunking = config or ChunkingConfig()
    text = document.content.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not text:
        return []

    chunks: list[DocumentChunk] = []
    start = 0
    chunk_index = 0
    while start < len(text):
        hard_end = min(len(text), start + chunking.max_chars)
        end = _choose_breakpoint(text, start, hard_end, chunking)
        chunk_text = text[start:end].strip()
        if chunk_text and len(chunk_text) >= chunking.min_chars:
            chunks.append(
                DocumentChunk(
                    chunk_id=_chunk_id(document.metadata.source_id, chunk_index, chunk_text),
                    source_id=document.metadata.source_id,
                    text=chunk_text,
                    metadata=document.metadata,
                    chunk_index=chunk_index,
                    location=f"chars {start}-{end}",
                    start_char=start,
                    end_char=end,
                    token_count=count_tokens_approx(chunk_text),
                    prompt_injection_flags=detect_prompt_injection(chunk_text),
                    sensitive_flags=find_sensitive_patterns(chunk_text),
                )
            )
            chunk_index += 1

        if end >= len(text):
            break
        start = max(start + 1, end - chunking.overlap_chars)

    return chunks


def chunk_documents(
    documents: list[LoadedDocument],
    config: ChunkingConfig | None = None,
) -> list[DocumentChunk]:
    """Chunk multiple documents."""

    chunks: list[DocumentChunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, config=config))
    return chunks

"""Retrieval service with citations and bad-retrieval detection."""

from __future__ import annotations

import re
from dataclasses import dataclass

from itsupport_copilot.rag.chunking import ChunkingConfig, chunk_documents
from itsupport_copilot.rag.embeddings import EmbeddingModel, HashingEmbeddingModel
from itsupport_copilot.rag.loaders import load_documents_from_directory
from itsupport_copilot.rag.vector_store import LocalVectorStore
from itsupport_copilot.schemas.rag import (
    Citation,
    DocumentChunk,
    DocumentType,
    LoadedDocument,
    RetrievalAssessment,
    RetrievalResponse,
    RetrievalResult,
)


@dataclass(frozen=True)
class RetrievalConfig:
    top_k: int = 5
    min_score: float = 0.18
    min_safe_results: int = 1
    excerpt_chars: int = 280

    def __post_init__(self) -> None:
        if self.top_k <= 0:
            raise ValueError("top_k must be positive")
        if self.min_safe_results < 0:
            raise ValueError("min_safe_results cannot be negative")
        if self.excerpt_chars < 80:
            raise ValueError("excerpt_chars must be at least 80")


class Retriever:
    """High-level RAG retriever over chunked local documents."""

    def __init__(
        self,
        *,
        embedding_model: EmbeddingModel | None = None,
        vector_store: LocalVectorStore | None = None,
        retrieval_config: RetrievalConfig | None = None,
        chunking_config: ChunkingConfig | None = None,
    ) -> None:
        self.embedding_model = embedding_model or HashingEmbeddingModel()
        self.vector_store = vector_store or LocalVectorStore()
        self.retrieval_config = retrieval_config or RetrievalConfig()
        self.chunking_config = chunking_config or ChunkingConfig()

    def ingest_documents(self, documents: list[LoadedDocument]) -> list[DocumentChunk]:
        chunks = chunk_documents(documents, config=self.chunking_config)
        if not chunks:
            return []
        embeddings = self.embedding_model.embed_documents([chunk.text for chunk in chunks])
        self.vector_store.add(chunks, embeddings)
        return chunks

    def ingest_directory(self, root: str) -> list[DocumentChunk]:
        documents = load_documents_from_directory(root)
        return self.ingest_documents(documents)

    def retrieve(
        self,
        query: str,
        *,
        document_types: set[DocumentType] | None = None,
        top_k: int | None = None,
        min_score: float | None = None,
    ) -> RetrievalResponse:
        query = query.strip()
        config = self.retrieval_config
        requested_top_k = top_k or config.top_k
        threshold = config.min_score if min_score is None else min_score
        query_terms = _query_terms(query)

        if not query:
            return RetrievalResponse(
                query=query,
                results=[],
                assessment=RetrievalAssessment(
                    sufficient=False,
                    reason="empty_query",
                    min_score=threshold,
                    query_terms=[],
                ),
            )

        query_embedding = self.embedding_model.embed_query(query)
        candidate_count = max(requested_top_k * 3, requested_top_k)
        matches = self.vector_store.search(query_embedding, top_k=candidate_count, min_score=-1.0)

        results: list[RetrievalResult] = []
        for match in matches:
            chunk = match.chunk
            if document_types and DocumentType(chunk.metadata.document_type) not in document_types:
                continue
            citation = Citation(
                source_id=chunk.source_id,
                chunk_id=chunk.chunk_id,
                filename=chunk.metadata.filename,
                document_type=DocumentType(chunk.metadata.document_type),
                location=chunk.location,
                score=round(match.score, 4),
                excerpt=_make_excerpt(chunk.text, query_terms, config.excerpt_chars),
            )
            results.append(
                RetrievalResult(
                    chunk=chunk,
                    score=round(match.score, 4),
                    citation=citation,
                    prompt_injection_flags=chunk.prompt_injection_flags,
                    sensitive_flags=chunk.sensitive_flags,
                    used_in_answer=False,
                )
            )
            if len(results) >= requested_top_k:
                break

        safe_results = [
            result
            for result in results
            if result.score >= threshold and not result.prompt_injection_flags
        ]
        unsafe_count = sum(1 for result in results if result.prompt_injection_flags)
        top_score = results[0].score if results else 0.0
        sufficient = len(safe_results) >= config.min_safe_results
        reason = _assessment_reason(
            result_count=len(results),
            safe_count=len(safe_results),
            unsafe_count=unsafe_count,
            top_score=top_score,
            threshold=threshold,
        )

        marked_results = []
        safe_ids = {result.chunk.chunk_id for result in safe_results}
        for result in results:
            marked_results.append(result.model_copy(update={"used_in_answer": result.chunk.chunk_id in safe_ids}))

        return RetrievalResponse(
            query=query,
            results=marked_results,
            assessment=RetrievalAssessment(
                sufficient=sufficient,
                reason=reason,
                top_score=top_score,
                result_count=len(marked_results),
                safe_result_count=len(safe_results),
                unsafe_result_count=unsafe_count,
                min_score=threshold,
                query_terms=query_terms,
            ),
        )


def _query_terms(query: str) -> list[str]:
    return sorted(set(re.findall(r"[a-zA-Z][a-zA-Z0-9_+.#-]{1,}", query.lower())))


def _make_excerpt(text: str, query_terms: list[str], max_chars: int) -> str:
    if len(text) <= max_chars:
        return text

    lower_text = text.lower()
    positions = [lower_text.find(term) for term in query_terms if lower_text.find(term) >= 0]
    center = min(positions) if positions else 0
    start = max(0, center - max_chars // 3)
    end = min(len(text), start + max_chars)
    if end - start < max_chars:
        start = max(0, end - max_chars)
    excerpt = text[start:end].strip()
    if start > 0:
        excerpt = "..." + excerpt
    if end < len(text):
        excerpt += "..."
    return excerpt


def _assessment_reason(
    *,
    result_count: int,
    safe_count: int,
    unsafe_count: int,
    top_score: float,
    threshold: float,
) -> str:
    if result_count == 0:
        return "no_results"
    if safe_count > 0:
        return "sufficient"
    if unsafe_count == result_count:
        return "only_unsafe_results"
    if top_score < threshold:
        return "top_score_below_threshold"
    return "no_safe_results_above_threshold"

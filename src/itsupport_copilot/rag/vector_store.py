"""Local vector store adapter for Phase 3 retrieval."""

from __future__ import annotations

import json
import math
from pathlib import Path

from pydantic import BaseModel

from itsupport_copilot.schemas.rag import DocumentChunk


class VectorRecord(BaseModel):
    chunk: DocumentChunk
    embedding: list[float]


class VectorSearchMatch(BaseModel):
    chunk: DocumentChunk
    score: float


class LocalVectorStore:
    """Simple persistent in-process vector store.

    Embeddings are expected to be normalized, but cosine similarity is computed
    defensively in case a provider returns non-normalized vectors.
    """

    def __init__(self) -> None:
        self._records: list[VectorRecord] = []

    @property
    def count(self) -> int:
        return len(self._records)

    def clear(self) -> None:
        self._records.clear()

    def add(self, chunks: list[DocumentChunk], embeddings: list[list[float]]) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks and embeddings must have the same length")
        for chunk, embedding in zip(chunks, embeddings, strict=True):
            if not embedding:
                raise ValueError(f"Empty embedding for chunk {chunk.chunk_id}")
            self._records.append(VectorRecord(chunk=chunk, embedding=embedding))

    def search(
        self,
        query_embedding: list[float],
        *,
        top_k: int = 5,
        min_score: float = -1.0,
    ) -> list[VectorSearchMatch]:
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        if not query_embedding:
            return []

        matches = [
            VectorSearchMatch(
                chunk=record.chunk,
                score=_cosine_similarity(query_embedding, record.embedding),
            )
            for record in self._records
        ]
        matches = [match for match in matches if match.score >= min_score]
        matches.sort(key=lambda match: match.score, reverse=True)
        return matches[:top_k]

    def save_json(self, path: str | Path) -> None:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        payload = [record.model_dump(mode="json") for record in self._records]
        target.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    @classmethod
    def load_json(cls, path: str | Path) -> "LocalVectorStore":
        source = Path(path)
        store = cls()
        payload = json.loads(source.read_text(encoding="utf-8"))
        store._records = [VectorRecord.model_validate(item) for item in payload]
        return store


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embeddings must have the same dimension")
    dot = sum(a * b for a, b in zip(left, right, strict=True))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)

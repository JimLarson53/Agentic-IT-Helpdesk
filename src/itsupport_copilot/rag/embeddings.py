"""Embedding adapters for retrieval."""

from __future__ import annotations

import hashlib
import math
import re
from collections import Counter
from typing import Protocol


class EmbeddingModel(Protocol):
    """Protocol implemented by embedding providers."""

    dimensions: int

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Embed document texts."""

    def embed_query(self, text: str) -> list[float]:
        """Embed a query."""


_STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "if",
    "in",
    "into",
    "is",
    "it",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "with",
    "when",
    "where",
}


class HashingEmbeddingModel:
    """Deterministic local embedding model for offline development and tests.

    This is a real bag-of-terms hashing embedder. It is not intended to match
    transformer quality, but it gives repeatable semantic-ish retrieval without
    network access, provider keys, or model downloads.
    """

    def __init__(self, dimensions: int = 384) -> None:
        if dimensions < 32:
            raise ValueError("dimensions must be at least 32")
        self.dimensions = dimensions

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        terms = Counter(_tokenize(text))
        for term, count in terms.items():
            digest = hashlib.blake2b(term.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            weight = 1.0 + math.log(count)
            vector[bucket] += sign * weight

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class SentenceTransformersEmbeddingModel:
    """Optional sentence-transformers adapter used when the dependency exists."""

    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
    ) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise RuntimeError(
                "sentence-transformers is not installed. Install the optional 'rag' extras."
            ) from exc

        self._model = SentenceTransformer(model_name)
        self.dimensions = int(self._model.get_sentence_embedding_dimension() or 0)

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [list(map(float, vector)) for vector in self._model.encode(texts)]

    def embed_query(self, text: str) -> list[float]:
        return list(map(float, self._model.encode([text])[0]))


def _tokenize(text: str) -> list[str]:
    raw_terms = re.findall(r"[a-zA-Z][a-zA-Z0-9_+.#-]{1,}", text.lower())
    terms: list[str] = []
    for term in raw_terms:
        if term in _STOP_WORDS:
            continue
        terms.append(term)
        if "-" in term:
            terms.extend(part for part in term.split("-") if part and part not in _STOP_WORDS)
    return terms

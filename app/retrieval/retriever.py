from __future__ import annotations

import math
from collections.abc import Sequence
from typing import Any, Protocol

from app.core.models import RetrievedChunk
from app.index.chroma_store import VectorMatch


class QueryEmbedder(Protocol):
    def embed_one(self, text: str) -> list[float]: ...


class SearchStore(Protocol):
    def search(
        self,
        query_embedding: list[float],
        *,
        limit: int,
        where: dict[str, Any] | None = None,
    ) -> list[VectorMatch]: ...


def cosine_similarity(left: Sequence[float], right: Sequence[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding dimensions must match")
    left_norm = math.sqrt(sum(value * value for value in left))
    right_norm = math.sqrt(sum(value * value for value in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return sum(a * b for a, b in zip(left, right, strict=True)) / (left_norm * right_norm)


def mmr_rerank(
    query_embedding: Sequence[float],
    matches: list[VectorMatch],
    *,
    limit: int,
    diversity: float = 0.2,
) -> list[RetrievedChunk]:
    """Select relevant but non-redundant results using Maximal Marginal Relevance."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    if not 0 <= diversity <= 1:
        raise ValueError("diversity must be between 0 and 1")

    remaining = list(matches)
    selected: list[VectorMatch] = []
    while remaining and len(selected) < limit:
        best = max(
            remaining,
            key=lambda match: _mmr_score(query_embedding, match, selected, diversity),
        )
        remaining.remove(best)
        selected.append(best)

    return [
        RetrievedChunk(chunk=match.chunk, score=cosine_similarity(query_embedding, match.embedding), rank=rank)
        for rank, match in enumerate(selected, start=1)
    ]


def _mmr_score(
    query_embedding: Sequence[float],
    candidate: VectorMatch,
    selected: list[VectorMatch],
    diversity: float,
) -> float:
    relevance = cosine_similarity(query_embedding, candidate.embedding)
    redundancy = max(
        (cosine_similarity(candidate.embedding, item.embedding) for item in selected),
        default=0.0,
    )
    return (1 - diversity) * relevance - diversity * redundancy


class Retriever:
    def __init__(
        self,
        embedder: QueryEmbedder,
        store: SearchStore,
        *,
        candidate_multiplier: int = 3,
        diversity: float = 0.2,
    ) -> None:
        if candidate_multiplier < 1:
            raise ValueError("candidate_multiplier must be positive")
        self.embedder = embedder
        self.store = store
        self.candidate_multiplier = candidate_multiplier
        self.diversity = diversity

    def retrieve(
        self,
        query: str,
        *,
        k: int = 5,
        where: dict[str, Any] | None = None,
    ) -> list[RetrievedChunk]:
        if not query.strip():
            raise ValueError("query must not be empty")
        if k <= 0:
            raise ValueError("k must be positive")
        query_embedding = self.embedder.embed_one(query)
        matches = self.store.search(
            query_embedding,
            limit=k * self.candidate_multiplier,
            where=where,
        )
        return mmr_rerank(
            query_embedding,
            matches,
            limit=k,
            diversity=self.diversity,
        )

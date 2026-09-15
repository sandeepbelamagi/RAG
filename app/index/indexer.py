from __future__ import annotations

from collections.abc import Sequence
from typing import Protocol

from app.core.models import DocumentChunk


class Embedder(Protocol):
    def embed(self, texts: Sequence[str]) -> list[list[float]]: ...


class VectorStore(Protocol):
    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None: ...


class ChunkIndexer:
    """Embeds chunks and incrementally upserts them into a vector store."""

    def __init__(
        self,
        embedder: Embedder,
        vector_store: VectorStore,
        *,
        batch_size: int = 32,
    ) -> None:
        if batch_size <= 0:
            raise ValueError("batch_size must be positive")
        self.embedder = embedder
        self.vector_store = vector_store
        self.batch_size = batch_size

    def index(self, chunks: list[DocumentChunk]) -> int:
        indexed = 0
        for start in range(0, len(chunks), self.batch_size):
            batch = chunks[start : start + self.batch_size]
            embeddings = self.embedder.embed([chunk.text for chunk in batch])
            self.vector_store.upsert_chunks(batch, embeddings)
            indexed += len(batch)
        return indexed

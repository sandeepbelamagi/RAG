from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.core.models import DocumentChunk


@dataclass(slots=True)
class VectorMatch:
    chunk: DocumentChunk
    distance: float
    embedding: list[float]


def _chroma_metadata(metadata: dict[str, Any]) -> dict[str, str | int | float | bool]:
    """Convert optional application metadata to Chroma's scalar metadata format."""
    result: dict[str, str | int | float | bool] = {}
    for key, value in metadata.items():
        if value is None:
            continue
        if isinstance(value, (str, int, float, bool)):
            result[key] = value
        else:
            result[key] = str(value)
    return result


class ChromaVectorStore:
    """Persistent Chroma collection used by the indexing and retrieval layers."""

    def __init__(
        self,
        persist_dir: str | Path,
        *,
        collection_name: str = "book_chunks",
    ) -> None:
        try:
            import chromadb
        except ImportError as exc:
            raise RuntimeError("Install chromadb before creating ChromaVectorStore") from exc

        self.persist_dir = Path(persist_dir)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        self._client = chromadb.PersistentClient(path=str(self.persist_dir))
        self.collection = self._client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    @property
    def count(self) -> int:
        return int(self.collection.count())

    def upsert_chunks(
        self,
        chunks: list[DocumentChunk],
        embeddings: list[list[float]],
    ) -> None:
        if len(chunks) != len(embeddings):
            raise ValueError("Each chunk must have exactly one embedding")
        if not chunks:
            return

        self.collection.upsert(
            ids=[chunk.chunk_id for chunk in chunks],
            documents=[chunk.text for chunk in chunks],
            embeddings=embeddings,
            metadatas=[_chroma_metadata(chunk.metadata) for chunk in chunks],
        )

    def delete_document(self, document_id: str) -> None:
        self.collection.delete(where={"document_id": document_id})

    def search(
        self,
        query_embedding: list[float],
        *,
        limit: int,
        where: dict[str, Any] | None = None,
    ) -> list[VectorMatch]:
        if limit <= 0:
            raise ValueError("limit must be positive")

        query_args: dict[str, Any] = {
            "query_embeddings": [query_embedding],
            "n_results": limit,
            "include": ["documents", "metadatas", "distances", "embeddings"],
        }
        if where:
            query_args["where"] = where
        result = self.collection.query(**query_args)

        ids = result.get("ids", [[]])[0]
        documents = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]
        embeddings = result.get("embeddings", [[]])[0]
        matches: list[VectorMatch] = []
        for chunk_id, document, metadata, distance, embedding in zip(
            ids, documents, metadatas, distances, embeddings, strict=True
        ):
            metadata = metadata or {}
            matches.append(
                VectorMatch(
                    chunk=DocumentChunk(
                        chunk_id=chunk_id,
                        document_id=str(metadata.get("document_id", "")),
                        text=document,
                        page_start=_optional_int(metadata.get("page_start")),
                        page_end=_optional_int(metadata.get("page_end")),
                        chapter=_optional_str(metadata.get("chapter")),
                        section=_optional_str(metadata.get("section")),
                        chunk_index=int(metadata.get("chunk_index", 0)),
                        metadata=dict(metadata),
                    ),
                    distance=float(distance),
                    embedding=list(embedding),
                )
            )
        return matches


def _optional_int(value: Any) -> int | None:
    return None if value is None else int(value)


def _optional_str(value: Any) -> str | None:
    return None if value is None else str(value)

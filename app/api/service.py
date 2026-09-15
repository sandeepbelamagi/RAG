from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from app.chunking import chunk_parsed_document_fixed, chunk_parsed_document_semantic
from app.core.config import Settings
from app.core.models import RetrievedChunk
from app.embeddings.ollama_client import OllamaEmbedder
from app.generation.generator import GeneratedAnswer, GroundedGenerator
from app.generation.ollama_client import OllamaChatClient
from app.index.chroma_store import ChromaVectorStore
from app.index.indexer import ChunkIndexer
from app.ingest.document_parser import parse_document
from app.retrieval.retriever import Retriever


@dataclass(slots=True)
class QueryResult:
    generated: GeneratedAnswer
    retrieved: list[RetrievedChunk]


class RAGService:
    """Application facade that composes ingestion, retrieval, and generation."""

    def __init__(
        self,
        indexer: ChunkIndexer,
        retriever: Retriever,
        generator: GroundedGenerator,
        *,
        store: ChromaVectorStore | None = None,
    ) -> None:
        self.indexer = indexer
        self.retriever = retriever
        self.generator = generator
        self.store = store

    def ingest(self, path: str | Path, *, strategy: str = "semantic") -> int:
        if strategy not in {"fixed", "semantic"}:
            raise ValueError("strategy must be 'fixed' or 'semantic'")
        parsed = parse_document(path)
        chunks = (
            chunk_parsed_document_fixed(parsed)
            if strategy == "fixed"
            else chunk_parsed_document_semantic(parsed)
        )
        return self.indexer.index(chunks)

    def query(
        self,
        question: str,
        *,
        k: int = 5,
        book_title: str | None = None,
    ) -> QueryResult:
        where: dict[str, Any] | None = {"book_title": book_title} if book_title else None
        retrieved = self.retriever.retrieve(question, k=k, where=where)
        return QueryResult(
            generated=self.generator.answer(question, retrieved),
            retrieved=retrieved,
        )


def build_rag_service(settings: Settings) -> RAGService:
    embedder = OllamaEmbedder(
        settings.ollama_base_url,
        settings.ollama_embed_model,
        timeout=settings.ollama_timeout,
    )
    store = ChromaVectorStore(
        settings.chroma_persist_dir,
        collection_name=settings.chroma_collection,
    )
    indexer = ChunkIndexer(
        embedder,
        store,
        batch_size=settings.embedding_batch_size,
    )
    retriever = Retriever(embedder, store)
    chat_client = OllamaChatClient(
        settings.ollama_base_url,
        settings.ollama_chat_model,
        timeout=settings.ollama_timeout,
    )
    generator = GroundedGenerator(chat_client)
    return RAGService(indexer, retriever, generator, store=store)

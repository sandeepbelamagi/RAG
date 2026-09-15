"""Embedding providers."""

from app.embeddings.ollama_client import OllamaEmbedder, OllamaEmbeddingError

__all__ = ["OllamaEmbedder", "OllamaEmbeddingError"]

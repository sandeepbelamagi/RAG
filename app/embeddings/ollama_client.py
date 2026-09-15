from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import httpx


class OllamaEmbeddingError(RuntimeError):
    """Raised when Ollama cannot produce embeddings."""


class OllamaEmbedder:
    """Small HTTP client for Ollama's batch embedding endpoint."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self._endpoint = f"{base_url.rstrip('/')}/api/embed"
        self._client = client if client is not None else httpx.Client(timeout=timeout)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def __enter__(self) -> OllamaEmbedder:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def embed(self, texts: Sequence[str]) -> list[list[float]]:
        if not texts:
            return []
        if any(not text.strip() for text in texts):
            raise ValueError("Cannot embed empty text")

        try:
            response = self._client.post(
                self._endpoint,
                json={"model": self.model, "input": list(texts)},
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            embeddings = payload.get("embeddings")
        except (httpx.HTTPError, ValueError) as exc:
            raise OllamaEmbeddingError(f"Ollama embedding request failed: {exc}") from exc

        if not isinstance(embeddings, list) or len(embeddings) != len(texts):
            raise OllamaEmbeddingError("Ollama returned an unexpected embeddings payload")
        if not all(isinstance(vector, list) for vector in embeddings):
            raise OllamaEmbeddingError("Ollama returned an invalid embedding vector")
        return embeddings

    def embed_one(self, text: str) -> list[float]:
        vectors = self.embed([text])
        return vectors[0]

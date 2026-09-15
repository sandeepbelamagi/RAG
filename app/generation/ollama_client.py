from __future__ import annotations

from typing import Any

import httpx


class OllamaGenerationError(RuntimeError):
    """Raised when Ollama cannot generate an answer."""


class OllamaChatClient:
    """Small client for Ollama's non-streaming chat endpoint."""

    def __init__(
        self,
        base_url: str,
        model: str,
        *,
        timeout: float = 120.0,
        client: httpx.Client | None = None,
    ) -> None:
        self.model = model
        self._endpoint = f"{base_url.rstrip('/')}/api/chat"
        self._client = client if client is not None else httpx.Client(timeout=timeout)
        self._owns_client = client is None

    def close(self) -> None:
        if self._owns_client:
            self._client.close()

    def chat(self, *, system: str, user: str) -> str:
        try:
            response = self._client.post(
                self._endpoint,
                json={
                    "model": self.model,
                    "stream": False,
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                },
            )
            response.raise_for_status()
            payload: dict[str, Any] = response.json()
            content = payload.get("message", {}).get("content")
        except (httpx.HTTPError, ValueError, AttributeError) as exc:
            raise OllamaGenerationError(f"Ollama generation request failed: {exc}") from exc

        if not isinstance(content, str) or not content.strip():
            raise OllamaGenerationError("Ollama returned an empty answer")
        return content.strip()

    def __enter__(self) -> OllamaChatClient:
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

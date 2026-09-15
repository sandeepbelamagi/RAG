from __future__ import annotations

from typing import Any

import httpx


class APIClientError(RuntimeError):
    """Raised when the Streamlit client cannot call the backend."""


class RAGAPIClient:
    def __init__(self, base_url: str, *, timeout: float = 180.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def ingest(self, filename: str, content: bytes, *, strategy: str = "semantic") -> dict[str, Any]:
        try:
            response = httpx.post(
                f"{self.base_url}/ingest",
                files={"file": (filename, content)},
                data={"strategy": strategy},
                timeout=self.timeout,
            )
            return self._json_response(response)
        except httpx.HTTPError as exc:
            raise APIClientError(f"Could not reach the API: {exc}") from exc

    def query(self, question: str, *, k: int = 5, book_title: str | None = None) -> dict[str, Any]:
        payload: dict[str, Any] = {"question": question, "k": k}
        if book_title:
            payload["book_title"] = book_title
        try:
            response = httpx.post(
                f"{self.base_url}/query",
                json=payload,
                timeout=self.timeout,
            )
            return self._json_response(response)
        except httpx.HTTPError as exc:
            raise APIClientError(f"Could not reach the API: {exc}") from exc

    @staticmethod
    def _json_response(response: httpx.Response) -> dict[str, Any]:
        try:
            payload = response.json()
        except ValueError as exc:
            raise APIClientError("The API returned an invalid response") from exc
        if response.is_error:
            detail = payload.get("detail", "Request failed") if isinstance(payload, dict) else "Request failed"
            raise APIClientError(str(detail))
        if not isinstance(payload, dict):
            raise APIClientError("The API returned an unexpected response")
        return payload

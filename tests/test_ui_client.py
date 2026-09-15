import httpx

from app.ui.api_client import APIClientError, RAGAPIClient


def test_api_client_rejects_error_response():
    response = httpx.Response(400, json={"detail": "Question is required"})

    try:
        RAGAPIClient._json_response(response)
    except APIClientError as exc:
        assert str(exc) == "Question is required"
    else:
        raise AssertionError("expected APIClientError")


def test_api_client_accepts_json_response():
    response = httpx.Response(200, json={"answer": "grounded"})

    assert RAGAPIClient._json_response(response) == {"answer": "grounded"}

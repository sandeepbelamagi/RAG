from app.api import routes


def test_readiness_reports_missing_ollama_without_crashing(monkeypatch, tmp_path):
    settings = routes.get_settings()
    monkeypatch.setattr(settings, "chroma_persist_dir", str(tmp_path))
    monkeypatch.setattr(settings, "ollama_base_url", "http://127.0.0.1:1")

    response = routes.ready()

    assert response.status == "not_ready"
    assert response.chroma == "ok"
    assert response.ollama == "unavailable"

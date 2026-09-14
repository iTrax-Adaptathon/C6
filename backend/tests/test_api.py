from fastapi.testclient import TestClient

from app.main import app


def test_health_endpoint() -> None:
    response = TestClient(app).get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_frontend_is_served_by_api() -> None:
    response = TestClient(app).get("/")
    assert response.status_code == 200
    assert "AI Debate Judge" in response.text
    script = TestClient(app).get("/script.js")
    assert script.status_code == 200
    assert "API setup" in script.text


def test_configuration_never_returns_secret() -> None:
    response = TestClient(app).get("/api/v1/configuration")
    assert response.status_code == 200
    assert set(response.json()) == {"ready", "model", "allow_custom_provider"}

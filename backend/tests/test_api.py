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


def test_mocked_judgment_creation_works_without_live_key(monkeypatch) -> None:
    from app.services import judge as judge_module

    def fake_judge_debate(request, settings):
        return {
            "motion": "Mock motion",
            "pull_quote": "Evidence and reasoning matter more than tone.",
            "winner": "A",
            "overall_score": {"a": 8.5, "b": 6.4},
            "argument_profile": {
                "logic": {"a": 8.7, "b": 6.9},
                "evidence": {"a": 8.3, "b": 6.3},
                "rebuttal": {"a": 8.1, "b": 5.9},
                "rhetoric": {"a": 7.8, "b": 6.5},
                "relevance": {"a": 8.4, "b": 6.8},
            },
            "claims": {
                "a": [{
                    "claim": "Strong claims need support.",
                    "logic_score": 8.7,
                    "evidence_score": 8.3,
                    "rebuttal_score": 8.1,
                    "rhetoric_score": 7.8,
                    "relevance_score": 8.4,
                    "fallacies": [],
                    "analysis": "Logic, evidence, and rebuttal point to the stronger claim."
                }],
                "b": [{
                    "claim": "Support is uneven.",
                    "logic_score": 6.9,
                    "evidence_score": 6.3,
                    "rebuttal_score": 5.9,
                    "rhetoric_score": 6.5,
                    "relevance_score": 6.8,
                    "fallacies": [],
                    "analysis": "The response remains weaker overall on evidence and direct rebuttal."
                }]
            },
            "final_verdict": "Side A is stronger because its evidence and claim structure outweigh the weaker counterargument.",
            "confidence": 0.82,
            "margin_of_victory": 2.1,
            "is_draw": False,
        }

    monkeypatch.setattr(judge_module, "judge_debate", fake_judge_debate)
    payload = {
        "topic": "Example motion",
        "side_a": "This is a sufficiently long argument about the issue and its evidence.",
        "side_b": "This is another sufficiently long argument with different evidence and rebuttal.",
    }
    response = TestClient(app).post("/api/v1/judgments", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["winner"] in {"A", "B", "Draw"}
    history = TestClient(app).get("/api/v1/debates")
    assert history.status_code == 200
    assert history.json()["total"] >= 1


def test_invalid_preset_is_rejected() -> None:
    payload = {
        "topic": "Example motion",
        "side_a": "This is a sufficiently long argument about the issue and its evidence.",
        "side_b": "This is another sufficiently long argument with different evidence and rebuttal.",
        "scoring_preset": "unknown",
    }
    assert TestClient(app).post("/api/v1/judgments", json=payload).status_code == 422


def test_identical_sides_are_rejected_case_insensitively() -> None:
    text = "This is a sufficiently long argument that should not be submitted twice."
    payload = {"topic": "Example motion", "side_a": text, "side_b": text.upper()}
    assert TestClient(app).post("/api/v1/judgments", json=payload).status_code == 422

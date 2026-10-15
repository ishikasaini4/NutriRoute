"""Tests for app.main. Owner: Member M, Day 4."""

from fastapi.testclient import TestClient

import app.main as main_module
from app.agent.react_loop import AgentResult, Observation
from app.main import app


def test_health():
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_success(monkeypatch):
    fake_result = AgentResult(
        final_answer="Banana has 358.0 mg potassium.",
        observations=[
            Observation(step=0, tool_name="lookup_nutrient", args={}, result={}, ok=True, error=None, latency_ms=1.0)
        ],
        num_steps=2,
    )
    monkeypatch.setattr(main_module, "answer_question", lambda question, **kwargs: fake_result)

    client = TestClient(app)
    response = client.post("/ask", json={"question": "How much potassium in banana?"})
    assert response.status_code == 200
    body = response.json()
    assert body["answer"] == "Banana has 358.0 mg potassium."
    assert body["tool_calls"] == ["lookup_nutrient"]
    assert body["steps"] == 2


def test_ask_failure_returns_500(monkeypatch):
    def boom(question, **kwargs):
        raise RuntimeError("OPENAI_API_KEY not set")

    monkeypatch.setattr(main_module, "answer_question", boom)

    client = TestClient(app)
    response = client.post("/ask", json={"question": "anything"})
    assert response.status_code == 500
    assert "OPENAI_API_KEY" in response.json()["detail"]

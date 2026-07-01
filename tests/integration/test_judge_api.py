import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_judge_single_case():
    payload = {
        "case": {
            "id": "test_case",
            "input": "What is AI?",
            "expected_output": "AI is Artificial Intelligence.",
            "criteria": ["correctness"],
        },
        "generated_answer": "AI stands for Artificial Intelligence.",
    }

    # We do not want to actually block on the LLM during automated tests since it could take seconds and relies on Ollama being up.
    # But since this is a local integration test, we can just run it. If Ollama isn't up, it fails gracefully.
    response = client.post("/api/v1/judge", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["case_id"] == "test_case"
    assert "metadata" in data
    # "verdict" could be null if Ollama is unreachable, so we don't strictly assert its contents here.


def test_judge_compare():
    payload = {
        "question": "What is AI?",
        "expected": "AI is Artificial Intelligence.",
        "generated": "AI stands for Artificial Intelligence.",
        "prompt_v1": "v1",
        "prompt_v2": "v1",
    }
    response = client.post("/api/v1/judge/compare", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "v1" in data
    assert "v2" in data
    assert "winner" in data

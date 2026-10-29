from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "operational",
        "engine": "SentiVerse AI API v2.1.0",
        "environment": "development",
    }


@pytest.fixture
def mock_pipeline():
    with (
        patch("app.services.recommendation.recommendation_service.get_recommendations", new_callable=AsyncMock) as mock_rec,
        patch("app.ml.emotion_classifier.emotion_engine.detect_emotions_async", new_callable=AsyncMock) as mock_emotion,
        patch("app.core.memory.memory_manager.get_user_context", new_callable=AsyncMock) as mock_memory_get,
        patch("app.core.memory.memory_manager.update_user_context", new_callable=AsyncMock) as mock_memory_set,
    ):
        mock_rec.return_value = [{
            "id": "test-1",
            "title": "Mocked Movie",
            "medium": "Movie",
            "themes": ["hope", "journey"],
            "tone": "uplifting",
            "pacing": "fast",
            "ending_type": "happy",
            "confidence_score": 95,
            "ai_explanation": "This is a mocked LLM explanation.",
            "streaming_links": {"Netflix": "https://netflix.com"},
        }]
        mock_emotion.return_value = [{"label": "joy", "score": 0.98}]
        mock_memory_get.return_value = {"seen_items": [], "mood_history": []}
        yield mock_rec, mock_emotion, mock_memory_set


def test_recommendation_endpoint(mock_pipeline):
    payload = {
        "query": "I am feeling so happy today",
        "limit": 1,
        "session_id": "test_uuid_123",
        "medium_filters": ["Movie"],
    }
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["status"] == "success"
    assert data["query_intent"] == payload["query"]
    assert data["detected_emotions"] == [{"label": "joy", "score": 0.98}]
    assert data["recommendations"][0]["title"] == "Mocked Movie"
    assert data["recommendations"][0]["ai_explanation"] == "This is a mocked LLM explanation."


def test_recommendation_invalid_payload():
    response = client.post("/api/v1/recommend", json={"limit": 5})
    assert response.status_code == 422


def test_empty_query_after_sanitization():
    response = client.post("/api/v1/recommend", json={"query": "<script></script>"})
    assert response.status_code == 400

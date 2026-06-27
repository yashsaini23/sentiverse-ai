import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

# 1. Health Check Test
def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "operational", "engine": "SentiVerse Engine v2.0.0"}

# 2. Mocked Recommendation Endpoint Test
@pytest.fixture
def mock_pipeline():
    """Mocks the heavy AI processes to allow instant, deterministic testing."""
    with patch('app.services.recommendation.recommendation_service.get_recommendations', new_callable=AsyncMock) as mock_rec, \
         patch('app.ml.emotion_classifier.emotion_engine.detect_emotions_async', new_callable=AsyncMock) as mock_emotion, \
         patch('app.core.memory.memory_manager.get_user_context', new_callable=AsyncMock) as mock_memory_get, \
         patch('app.core.memory.memory_manager.update_user_context', new_callable=AsyncMock) as mock_memory_set:
        
        # Define the fake mock returns
        mock_rec.return_value = [
            {
                "id": "test-1",
                "title": "Mocked Movie",
                "medium": "Movie",
                "themes": ["hope", "journey"],
                "tone": "uplifting",
                "pacing": "fast",
                "ending_type": "happy",
                "confidence_score": 95,
                "ai_explanation": "This is a mocked LLM explanation.",
                "streaming_links": {"Netflix": "https://netflix.com"}
            }
        ]
        mock_emotion.return_value = [{"label": "joy", "score": 0.98}]
        mock_memory_get.return_value = {"seen_items": [], "mood_history": []}
        
        yield mock_rec, mock_emotion

def test_recommendation_endpoint(mock_pipeline):
    """Tests the main orchestration pipeline using strict Pydantic payload models."""
    payload = {
        "query": "I am feeling so happy today",
        "limit": 1,
        "session_id": "test_uuid_123",
        "medium_filters": ["Movie"]
    }
    
    response = client.post("/api/v1/recommend", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    
    # Assert core structures
    assert data["status"] == "success"
    assert data["query_intent"] == "I am feeling so happy today"
    
    # Assert Emotion Classification mapping
    assert len(data["detected_emotions"]) == 1
    assert data["detected_emotions"][0]["label"] == "joy"
    
    # Assert Recommendation payload
    assert len(data["recommendations"]) == 1
    assert data["recommendations"][0]["title"] == "Mocked Movie"
    assert data["recommendations"][0]["ai_explanation"] == "This is a mocked LLM explanation."

def test_recommendation_invalid_payload():
    """Ensures Pydantic schema rejection for invalid inputs."""
    # Query is missing, which violates the MoodRequest schema
    payload = {"limit": 5} 
    response = client.post("/api/v1/recommend", json=payload)
    assert response.status_code == 422 # Unprocessable Entity
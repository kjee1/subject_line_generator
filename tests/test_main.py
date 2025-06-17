import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}

def test_generate_headlines():
    test_request = {
        "newsletter_text": "This is a test newsletter about productivity and mindset.",
        "audience_profile": "Startup founders",
        "goal": "Increase open rates",
        "tone": "Professional but friendly",
        "past_headlines": ["Test headline 1", "Test headline 2"],
        "constraints": {
            "max_length": 60,
            "avoid_clickbait": True,
            "require_numbers": False
        }
    }
    
    response = client.post("/generate", json=test_request)
    assert response.status_code == 200
    
    data = response.json()
    assert "headlines" in data
    assert "trending_topics" in data
    assert isinstance(data["headlines"], list)
    assert isinstance(data["trending_topics"], list)

def test_generate_headlines_invalid_input():
    # Test with missing required field
    invalid_request = {
        "newsletter_text": "Test newsletter",
        "audience_profile": "Startup founders",
        # Missing required fields
    }
    
    response = client.post("/generate", json=invalid_request)
    assert response.status_code == 422  # Validation error 
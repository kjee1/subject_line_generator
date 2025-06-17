import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
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
    with patch("headline_generator.HeadlineGenerator.generate_headlines") as mock_generate:
        mock_generate.return_value = {
            "headlines": [
                {
                    "title": "Mocked Headline",
                    "keywords": ["mock", "test"],
                    "reason": "This is a mock response."
                }
            ],
            "trending_topics": ["mock trending"]
        }
        response = client.post("/generate", json=test_request)
        assert response.status_code == 200
        data = response.json()
        assert "headlines" in data
        assert "trending_topics" in data
        assert data["headlines"][0]["title"] == "Mocked Headline"

def test_generate_headlines_invalid_input():
    # Test with missing required field
    invalid_request = {
        "newsletter_text": "Test newsletter",
        "audience_profile": "Startup founders",
        # Missing required fields
    }
    response = client.post("/generate", json=invalid_request)
    assert response.status_code == 422  # Validation error

def test_generate_headlines_empty_newsletter():
    # Test with empty newsletter text
    test_request = {
        "newsletter_text": "",
        "audience_profile": "Startup founders",
        "goal": "Increase open rates",
        "tone": "Professional but friendly",
        "past_headlines": ["Test headline 1"],
        "constraints": {
            "max_length": 60,
            "avoid_clickbait": True,
            "require_numbers": False
        }
    }
    response = client.post("/generate", json=test_request)
    assert response.status_code == 422 or response.status_code == 400

def test_generate_headlines_trends_error():
    # Simulate error in trends fetcher
    test_request = {
        "newsletter_text": "This is a test newsletter about productivity and mindset.",
        "audience_profile": "Startup founders",
        "goal": "Increase open rates",
        "tone": "Professional but friendly",
        "past_headlines": ["Test headline 1"],
        "constraints": {
            "max_length": 60,
            "avoid_clickbait": True,
            "require_numbers": False
        }
    }
    with patch("trends_fetcher.TrendsFetcher.get_trending_topics", side_effect=Exception("Trends API error")):
        with patch("headline_generator.HeadlineGenerator.generate_headlines") as mock_generate:
            mock_generate.return_value = {
                "headlines": [
                    {
                        "title": "Fallback Headline",
                        "keywords": ["fallback"],
                        "reason": "Fallback due to trends error."
                    }
                ],
                "trending_topics": []
            }
            response = client.post("/generate", json=test_request)
            assert response.status_code == 200
            data = response.json()
            assert data["headlines"][0]["title"] == "Fallback Headline" 
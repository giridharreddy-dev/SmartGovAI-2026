import pytest
from unittest.mock import patch, MagicMock
from app import app
from services.semantic_search import semantic_search

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_semantic_search_endpoint_missing_q(client):
    response = client.get("/api/semantic-search")
    assert response.status_code == 400
    assert "error" in response.json

@patch("app.perform_semantic_search")
def test_semantic_search_endpoint_success(mock_perform, client):
    mock_perform.return_value = {
        "status": "success",
        "results": [
            {"id": "Test_Scheme", "scheme_name": "Test Scheme", "category": "Health", "distance": 0.1}
        ]
    }
    
    response = client.get("/api/semantic-search?q=hospital")
    assert response.status_code == 200
    assert "results" in response.json
    assert len(response.json["results"]) == 1
    assert response.json["results"][0]["scheme_name"] == "Test Scheme"

@patch("app.perform_semantic_search")
def test_semantic_search_endpoint_error(mock_perform, client):
    mock_perform.return_value = {
        "status": "error",
        "message": "DB not initialized"
    }
    
    response = client.get("/api/semantic-search?q=hospital")
    assert response.status_code == 503
    assert "error" in response.json

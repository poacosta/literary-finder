"""Unit test for Literary Finder API health endpoint."""
import pytest
from fastapi.testclient import TestClient
from literary_finder.api.server import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] in ["healthy", "unhealthy"]
    assert "timestamp" in data
    assert "graph_initialized" in data

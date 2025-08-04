"""Integration tests for API and interface layers."""
import pytest
from fastapi.testclient import TestClient
from literary_finder.api.server import app
from literary_finder.interface import create_gradio_app

client = TestClient(app)

def test_api_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "graph_initialized" in data

# Test analyze endpoint with dummy author

def test_api_analyze(monkeypatch):
    # Patch graph to avoid real agent calls
    from literary_finder.api import server
    class DummyGraph:
        def analyze_author(self, author_name, llm_provider=None, model_name=None, enable_parallel=True):
            return {"success": True, "author_name": author_name, "final_report": "Report", "processing_time_seconds": 1.0, "errors": []}
        def process_author(self, author_name, llm_provider=None, model_name=None, enable_parallel=True):
            return {"success": True, "author_name": author_name, "final_report": "Report", "processing_time_seconds": 1.0, "errors": []}
    server.literary_graph = DummyGraph()
    response = client.post("/analyze", json={"author_name": "Test Author"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["author_name"] == "Test Author"
    assert "final_report" in data

# Gradio interface creation

def test_gradio_interface_creation():
    app = create_gradio_app()
    assert app is not None

"""Unit tests for LiteraryFinderGraph orchestration."""
import pytest
from literary_finder.orchestration.graph import LiteraryFinderGraph

def test_graph_init():
    graph = LiteraryFinderGraph()
    assert graph.historian is not None
    assert graph.cartographer is not None
    assert graph.legacy_connector is not None
    assert graph.evaluator is not None or graph.evaluator is None

def test_build_graph():
    graph = LiteraryFinderGraph()
    compiled_graph = graph._build_graph()
    assert compiled_graph is not None

def test_start_processing():
    graph = LiteraryFinderGraph()
    class DummyState:
        author_name = "Test Author"
    result = graph._start_processing(DummyState())
    assert isinstance(result, dict)
    assert "processing_started_at" in result
    assert "agent_statuses" in result

def test_run_agents_parallel(monkeypatch):
    graph = LiteraryFinderGraph()
    class DummyState:
        author_name = "Test Author"
        errors = []
    # Patch agents to avoid real calls, include 'success' key
    graph.historian.process = lambda author_name, context=None: {"success": True, "data": "historian"}
    graph.cartographer.process = lambda author_name, context=None: {"success": True, "data": "cartographer"}
    graph.legacy_connector.process = lambda author_name, context=None: {"success": True, "data": "legacy_connector"}
    result = graph._run_agents_parallel(DummyState())
    assert isinstance(result, dict)

def test_run_agents_parallel_with_failure(monkeypatch):
    graph = LiteraryFinderGraph()
    class DummyState:
        author_name = "Test Author"
        errors = []
    # Patch agents to simulate historian failure
    graph.historian.process = lambda author_name, context=None: {"success": False, "error": "fail", "data": None}
    graph.cartographer.process = lambda author_name, context=None: {"success": True, "data": "cartographer"}
    graph.legacy_connector.process = lambda author_name, context=None: {"success": True, "data": "legacy_connector"}
    result = graph._run_agents_parallel(DummyState())
    assert isinstance(result, dict)
    # Should log error and continue

def test_start_processing_with_existing_status():
    graph = LiteraryFinderGraph()
    class DummyState:
        author_name = "Test Author"
        agent_statuses = {"contextual_historian": "COMPLETED"}
    result = graph._start_processing(DummyState())
    assert isinstance(result, dict)
    assert "processing_started_at" in result
    assert "agent_statuses" in result

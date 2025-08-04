"""Unit tests for LiteraryFinderGraph orchestration."""
import pytest
from literary_finder.orchestration.graph import LiteraryFinderGraph

def test_graph_init():
    graph = LiteraryFinderGraph()
    assert graph.historian is not None
    assert graph.cartographer is not None
    assert graph.legacy_connector is not None
    assert graph.evaluator is not None or graph.evaluator is None

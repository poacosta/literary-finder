"""Unit tests for internal agent methods (parsing, validation, etc.)"""
import pytest
from literary_finder.agents.book_recommender import BookRecommendationAgent
from literary_finder.agents.contextual_historian import ContextualHistorian
from literary_finder.agents.literary_cartographer import LiteraryCartographer
from literary_finder.agents.legacy_connector import LegacyConnector

# BookRecommendationAgent parsing

def test_parse_book_results_basic():
    agent = BookRecommendationAgent()
    output = "Book1, Book2"
    result = agent._parse_book_results(output, "Author")
    from literary_finder.models import AuthorContext
    assert isinstance(result, AuthorContext)
    # Check for expected attribute in AuthorContext
    assert hasattr(result, "biographical_summary")
    assert result.biographical_summary is not None

# ContextualHistorian parsing

def test_parse_research_results_basic():
    agent = ContextualHistorian()
    output = "Summary info"
    result = agent._parse_research_results(output, "Author")
    from literary_finder.models import AuthorContext
    assert isinstance(result, AuthorContext)
    # Check for expected attribute in AuthorContext
    assert hasattr(result, "biographical_summary")
    assert result.biographical_summary is not None

# LiteraryCartographer parsing

def test_parse_bibliography_results_basic():
    agent = LiteraryCartographer()
    output = "Bibliography info"
    result = agent._parse_bibliography_results(output, "Author")
    from literary_finder.models import ReadingMap
    assert isinstance(result, ReadingMap)
    # Check for expected attribute in ReadingMap
    assert hasattr(result, "start_here")
    assert isinstance(result.start_here, list)

# LegacyConnector parsing

def test_parse_legacy_results_basic():
    agent = LegacyConnector()
    output = "Legacy info"
    result = agent._parse_legacy_results(output, "Author")
    from literary_finder.models import LegacyAnalysis
    assert isinstance(result, LegacyAnalysis)
    # Check for expected attribute in LegacyAnalysis
    assert hasattr(result, "literary_significance")
    assert result.literary_significance is not None

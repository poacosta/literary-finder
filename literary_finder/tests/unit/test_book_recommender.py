"""Unit test for BookRecommendationAgent basic functionality."""
import pytest
from literary_finder.agents.book_recommender import BookRecommendationAgent

class DummyGoogleBooksAPI:
    def search_books_by_author(self, author_name, max_results=10):
        return [type('Book', (), {
            'title': 'Test Book',
            'published_date': '2000-01-01',
            'description': 'A test book description',
            'categories': ['Fiction'],
        })()]

@pytest.fixture
def agent():
    agent = BookRecommendationAgent()
    agent.google_books = DummyGoogleBooksAPI()
    return agent

def test_get_author_books(agent):
    result = agent._get_author_books('Test Author')
    assert 'Test Book' in result
    assert 'A test book description' in result

def test_get_author_books_empty(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate no books found
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: []})()
    result = agent._get_author_books("Unknown Author")
    assert "No books found" in result

def test_get_author_books_quality(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with short descriptions
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [type('Book', (), {'title': 'Short', 'published_date': '2020', 'description': 'Short', 'categories': ['Fiction']})() for _ in range(5)]})()
    result = agent._get_author_books("Test Author")
    assert "Books by Test Author" in result

def test_get_agent_role():
    agent = BookRecommendationAgent()
    assert agent.get_agent_role() == "Book Recommendation Agent"

def test_get_tools():
    agent = BookRecommendationAgent()
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert any(tool.name == "get_author_books" for tool in tools)

def test_get_system_prompt():
    agent = BookRecommendationAgent()
    prompt = agent.get_system_prompt()
    assert isinstance(prompt, str)
    assert "Book Recommender" in prompt

def test_process_returns_dict(monkeypatch):
    agent = BookRecommendationAgent()
    # Mock _parse_book_results to avoid external calls
    agent._parse_book_results = lambda output, author_name: {"books": output}
    # Patch AgentExecutor.invoke at the class level
    monkeypatch.setattr(type(agent.agent), "invoke", lambda self, input_dict: {"output": "Book results"})
    result = agent.process("Test Author")
    assert isinstance(result, dict)
    assert "data" in result
    assert "books" in result["data"]

def test_process_exception(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate agent.invoke raising exception
    monkeypatch.setattr(type(agent.agent), "invoke", lambda self, input_dict: (_ for _ in ()).throw(Exception("fail")))
    result = agent.process("Test Author")
    assert result["success"] is False
    assert "error" in result

def test_handle_error(monkeypatch):
    agent = BookRecommendationAgent()
    error = Exception("fail")
    # Simulate error handling (if implemented)
    if hasattr(agent, "_handle_error"):
        result = agent._handle_error(error, "test context")
        assert isinstance(result, dict)
        assert "error" in result

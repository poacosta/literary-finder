# Additional coverage: error handling and edge cases
def test_get_author_books_error(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate GoogleBooksAPI raising an exception
    class Dummy:
        def search_books_by_author(self, author_name, max_results=10):
            raise Exception("API error")
    agent.google_books = Dummy()
    result = agent._get_author_books("Any Author")
    assert "Error retrieving books" in result

def test_get_book_details_error(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate GoogleBooksAPI raising an exception
    class Dummy:
        def search_books_by_author(self, author_name, max_results=10):
            raise Exception("API error")
    agent.google_books = Dummy()
    result = agent._get_book_details("for Any Author")
    assert "Error getting book details" in result

def test_find_popular_books_error(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate GoogleBooksAPI raising an exception
    class Dummy:
        def search_books_by_author(self, author_name, max_results=10):
            raise Exception("API error")
    agent.google_books = Dummy()
    result = agent._find_popular_books("Any Author")
    assert "Error finding popular books" in result

def test_tool_registration():
    agent = BookRecommendationAgent()
    tools = agent.get_tools()
    tool_names = [tool.name for tool in tools]
    assert set(tool_names) == {"get_author_books", "get_book_details", "find_popular_books"}

def test_system_prompt_content():
    agent = BookRecommendationAgent()
    prompt = agent.get_system_prompt()
    assert "efficient AI agent" in prompt
    assert "Google Books data" in prompt
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


# Additional tests for coverage
def test_repr_and_str():
    agent = BookRecommendationAgent()
    # If __repr__ or __str__ are implemented, test them
    assert isinstance(repr(agent), str)
    assert isinstance(str(agent), str)

def test_get_author_books_type(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with different types
    class Book:
        def __init__(self):
            self.title = "TypeTest"
            self.published_date = "2021"
            self.description = "TypeTestDesc"
            self.categories = ["TestCat"]
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book()]})()
    result = agent._get_author_books("TypeTest Author")
    assert "TypeTest" in result

def test_get_tools_content():
    agent = BookRecommendationAgent()
    tools = agent.get_tools()
    for tool in tools:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")

def test_get_system_prompt_content():
    agent = BookRecommendationAgent()
    prompt = agent.get_system_prompt()
    assert "Book Recommender" in prompt
    assert "recommend" in prompt.lower()

def test_find_popular_books_categories(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with multiple categories
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [type('Book', (), {'title': 'Novel', 'published_date': '2010-01-01', 'description': 'A'*120, 'categories': ['Fiction', 'Adventure']})() for _ in range(2)]})()
    result = agent._find_popular_books("Popular Author")
    assert "Popular/Essential books by Popular Author" in result
    assert "Novel" in result
    # The output does not include categories, only title and header
def test_get_book_details(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with rich metadata
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [type('Book', (), {'title': 'Rich', 'published_date': '2020-01-01', 'description': 'A'*201, 'categories': ['Fiction', 'Drama']})() for _ in range(3)]})()
    result = agent._get_book_details("for Rich Author")
    assert "Detailed book information" in result
    assert "Rich" in result

def test_get_book_details_no_books(monkeypatch):
    agent = BookRecommendationAgent()
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: []})()
    result = agent._get_book_details("for Unknown Author")
    assert "No detailed book information found" in result

def test_find_popular_books(monkeypatch):
    agent = BookRecommendationAgent()
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [type('Book', (), {'title': 'Novel', 'published_date': '2010-01-01', 'description': 'A'*120, 'categories': ['Fiction']})() for _ in range(5)]})()
    result = agent._find_popular_books("Popular Author")
    assert "Popular/Essential books by Popular Author" in result
    assert "Novel" in result

def test_find_popular_books_no_books(monkeypatch):
    agent = BookRecommendationAgent()
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: []})()
    result = agent._find_popular_books("Unknown Author")
    assert "No popular books found" in result

def test_parse_book_results_years():
    agent = BookRecommendationAgent()
    output = "1980, 2000, 2010"
    context = agent._parse_book_results(output, "Test Author")
    assert hasattr(context, "biographical_summary")
    assert "Essential Books by Test Author" in context.biographical_summary
    assert context.birth_year is not None

def test_parse_book_results_no_years():
    agent = BookRecommendationAgent()
    output = "No years here"
    context = agent._parse_book_results(output, "Test Author")
    assert hasattr(context, "biographical_summary")
    assert "Essential Books by Test Author" in context.biographical_summary

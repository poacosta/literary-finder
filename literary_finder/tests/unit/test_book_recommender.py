# Edge case: _get_author_books with all books missing description and published_date
def test_get_author_books_all_missing(monkeypatch):
    agent = BookRecommendationAgent()
    class Book:
        def __init__(self):
            self.title = "NoMeta"
            self.published_date = None
            self.description = None
            self.categories = []
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book() for _ in range(5)]})()
    result = agent._get_author_books("NoMeta Author")
    assert "Books by NoMeta Author" in result or "No books found" in result

# Edge case: _get_book_details with all books missing description and published_date
def test_get_book_details_all_missing(monkeypatch):
    agent = BookRecommendationAgent()
    class Book:
        def __init__(self):
            self.title = "NoMeta"
            self.published_date = None
            self.description = None
            self.categories = []
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book() for _ in range(5)]})()
    result = agent._get_book_details("for NoMeta Author")
    assert "No detailed book information found" in result or "Detailed book information" in result

# Edge case: _find_popular_books with all books missing description, published_date, categories
def test_find_popular_books_all_missing(monkeypatch):
    agent = BookRecommendationAgent()
    class Book:
        def __init__(self):
            self.title = "NoMeta"
            self.published_date = None
            self.description = None
            self.categories = []
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book() for _ in range(5)]})()
    result = agent._find_popular_books("NoMeta Author")
    assert "Popular/Essential books by NoMeta Author" in result or "No popular books found" in result

# Test _parse_book_results with no years
def test_parse_book_results_no_years_content():
    agent = BookRecommendationAgent()
    output = "No years or dates here"
    context = agent._parse_book_results(output, "NoYear Author")
    assert hasattr(context, "biographical_summary")
    assert "Essential Books by NoYear Author" in context.biographical_summary

# Test _parse_book_results with years
def test_parse_book_results_with_years():
    agent = BookRecommendationAgent()
    output = "1980, 2000, 2010"
    context = agent._parse_book_results(output, "Year Author")
    assert hasattr(context, "biographical_summary")
    assert context.birth_year is not None
    assert "Essential Books by Year Author" in context.biographical_summary

# Test error handling for process
def test_process_error(monkeypatch):
    agent = BookRecommendationAgent()
    monkeypatch.setattr(type(agent.agent), "invoke", lambda self, input_dict: (_ for _ in ()).throw(Exception("fail")))
    result = agent.process("Test Author")
    assert result["success"] is False
    assert "error" in result

# Test __init__ and tool registration
def test_agent_tool_registration():
    agent = BookRecommendationAgent()
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert any(tool.name == "get_author_books" for tool in tools)
    assert any(tool.name == "get_book_details" for tool in tools)
    assert any(tool.name == "find_popular_books" for tool in tools)

# Test get_system_prompt content
def test_system_prompt_content_full():
    agent = BookRecommendationAgent()
    prompt = agent.get_system_prompt()
    assert "Book Recommender" in prompt
    assert "recommendations" in prompt
# Additional coverage: edge cases, error handling, and tool behaviors
def test_get_author_books_no_description(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with no description
    class Book:
        def __init__(self):
            self.title = "NoDesc"
            self.published_date = "2022"
            self.description = None
            self.categories = ["Unknown"]
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book()]})()
    result = agent._get_author_books("NoDesc Author")
    assert "NoDesc" in result

def test_get_author_books_no_published_date(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with no published_date
    class Book:
        def __init__(self):
            self.title = "NoDate"
            self.published_date = None
            self.description = "A book with no date but a long enough description to be quality. " * 2
            self.categories = ["Unknown"]
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book()]})()
    result = agent._get_author_books("NoDate Author")
    assert "NoDate" in result

def test_get_book_details_short_description(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with short description
    class Book:
        def __init__(self):
            self.title = "ShortDesc"
            self.published_date = "2020"
            self.description = "Short desc"
            self.categories = ["TestCat"]
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book()]})()
    result = agent._get_book_details("for ShortDesc Author")
    assert "ShortDesc" in result

def test_find_popular_books_title_keywords(monkeypatch):
    agent = BookRecommendationAgent()
    # Simulate books with 'novel' keyword in title
    class Book:
        def __init__(self):
            self.title = "Great Novel"
            self.published_date = "2015"
            self.description = "A novel with a long enough description to be scored. " * 2
            self.categories = ["Fiction"]
    agent.google_books = type("Dummy", (), {"search_books_by_author": lambda self, author_name, max_results=10: [Book()]})()
    result = agent._find_popular_books("Keyword Author")
    assert "Great Novel" in result

def test_parse_book_results_no_years(monkeypatch):
    agent = BookRecommendationAgent()
    output = "No years or dates here"
    context = agent._parse_book_results(output, "NoYear Author")
    assert hasattr(context, "biographical_summary")
    assert "Essential Books by NoYear Author" in context.biographical_summary

def test_repr(monkeypatch):
    agent = BookRecommendationAgent()
    assert isinstance(repr(agent), str)

def test_str(monkeypatch):
    agent = BookRecommendationAgent()
    assert isinstance(str(agent), str)
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

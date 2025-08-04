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

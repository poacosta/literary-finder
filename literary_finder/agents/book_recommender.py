"""Book Recommender agent for efficient book discovery and recommendations."""

from typing import Any, Dict, List, Optional
from langchain.tools import Tool
from ..tools import GoogleBooksAPI
from ..models import AuthorContext
from .base import BaseAgent
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class BookRecommendationAgent(BaseAgent):
    def get_agent_role(self) -> str:
        return "Book Recommendation Agent"
    """Lightweight agent focused on book recommendations using Google Books API."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.google_books = GoogleBooksAPI()
        self.tools = self.get_tools()
        self.agent = self._create_agent_executor()

    def get_tools(self) -> List[Tool]:
        """Get tools for book recommendations."""
        return [
            Tool(
                name="get_author_books",
                description="Get all books by an author from Google Books",
                func=self._get_author_books
            ),
            Tool(
                name="get_book_details",
                description="Get detailed information about specific books",
                func=self._get_book_details
            ),
            Tool(
                name="find_popular_books",
                description="Find the most popular/highly-rated books by the author",
                func=self._find_popular_books
            )
        ]

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Book Recommender."""
        return """You are the Book Recommender, an efficient AI agent focused on book discovery and recommendations.

Your mission: Provide essential book information and recommendations using Google Books data.

Tasks:
1. **Essential Books**: Identify 3-5 most important/popular works
2. **Basic Info**: Extract key details (publication years, descriptions)
3. **Quick Recommendations**: Suggest reading order for new readers

Guidelines:
- Focus on major published works only
- Prioritize books with good descriptions and ratings
- Keep recommendations practical and concise
- Use available Google Books data efficiently

Output: Structured book recommendations with brief explanations."""

    def process(self, author_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process book recommendations for an author."""
        try:
            logger.info(f"Starting book recommendations for: {author_name}")

            # Simple, focused input for the agent
            input_text = f"""Find and recommend the essential books by author: {author_name}
            
Please:
1. Get all books by this author
2. Identify the 3-5 most important/popular works
3. Provide brief descriptions and publication info
4. Suggest a reading order for new readers

Focus on major published works with good descriptions."""

            result = self.agent.invoke({"input": input_text})

            context_data = self._parse_book_results(result["output"], author_name)

            return {
                "success": True,
                "data": context_data,
                "raw_output": result["output"]
            }

        except Exception as e:
            return self._handle_error(e, "book recommendation")

    def _get_author_books(self, author_name: str) -> str:
        """Get books by the author using Google Books API."""
        try:
            books = self.google_books.search_books_by_author(author_name, max_results=40)

            if not books:
                return f"No books found for author: {author_name}"

            quality_books = [
                book for book in books
                if book.description and len(book.description) > 50 and book.published_date
            ]

            if not quality_books:
                quality_books = books[:10]

            summary = f"Books by {author_name} ({len(quality_books)} quality results):\n\n"

            for i, book in enumerate(quality_books[:10], 1):
                summary += f"{i}. **{book.title}**"
                if book.published_date:
                    year = book.published_date.split('-')[0]
                    summary += f" ({year})"
                if book.categories:
                    summary += f" - {book.categories[0]}"
                summary += "\n"
                if book.description:
                    desc = book.description[:150] + "..." if len(book.description) > 150 else book.description
                    summary += f"   Description: {desc}\n"
                summary += "\n"

            return summary

        except Exception as e:
            logger.error(f"Error getting author books: {e}")
            return f"Error retrieving books: {str(e)}"

    def _get_book_details(self, query: str) -> str:
        """Get detailed information about specific books."""
        try:
            import re
            author_match = re.search(r"for (.+?)(?:\s|$)", query)
            author_name = author_match.group(1) if author_match else query

            books = self.google_books.search_books_by_author(author_name, max_results=15)

            if not books:
                return f"No detailed book information found for {author_name}"

            # Focus on books with rich metadata
            detailed_books = sorted(
                [book for book in books if book.description and book.published_date],
                key=lambda x: len(x.description or ""),
                reverse=True
            )[:8]

            details = f"Detailed book information for {author_name}:\n\n"

            for book in detailed_books:
                details += f"**{book.title}**\n"
                if book.published_date:
                    details += f"Published: {book.published_date.split('-')[0]}\n"
                if book.categories:
                    details += f"Genre: {', '.join(book.categories[:2])}\n"
                if book.description:
                    desc = book.description[:200] + "..." if len(book.description) > 200 else book.description
                    details += f"Summary: {desc}\n"
                details += "\n"

            return details

        except Exception as e:
            logger.error(f"Error getting book details: {e}")
            return f"Error getting book details: {str(e)}"

    def _find_popular_books(self, author_name: str) -> str:
        """Find the most popular/highly-rated books by the author."""
        try:
            books = self.google_books.search_books_by_author(author_name, max_results=40)

            if not books:
                return f"No popular books found for {author_name}"

            scored_books = []
            for book in books:
                score = 0
                if book.description:
                    score += len(book.description) // 100  # Longer descriptions = more important
                if book.published_date:
                    score += 2
                if book.categories:
                    score += 1
                if any(keyword in book.title.lower() for keyword in ['novel', 'stories', 'collection']):
                    score += 2

                scored_books.append((book, score))

            top_books = sorted(scored_books, key=lambda x: x[1], reverse=True)[:6]

            popular = f"Popular/Essential books by {author_name}:\n\n"

            for i, (book, score) in enumerate(top_books, 1):
                popular += f"{i}. **{book.title}**"
                if book.published_date:
                    year = book.published_date.split('-')[0]
                    popular += f" ({year})"
                popular += f" [Score: {score}]\n"

                if book.description:
                    desc = book.description[:120] + "..." if len(book.description) > 120 else book.description
                    popular += f"   Why it's essential: {desc}\n"
                popular += "\n"

            return popular

        except Exception as e:
            logger.error(f"Error finding popular books: {e}")
            return f"Error finding popular books: {str(e)}"

    def _parse_book_results(self, agent_output: str, author_name: str) -> AuthorContext:
        """Parse agent output into structured AuthorContext with basic info."""

        context = AuthorContext()

        import re

        years = re.findall(r'\b(19\d{2}|20\d{2})\b', agent_output)
        if years:
            years = [int(y) for y in years]
            context.birth_year = min(years) - 25  # Rough estimate
            if max(years) < 2020:
                context.death_year = max(years) + 10  # Rough estimate

        # Store the book recommendations as biographical summary
        context.biographical_summary = f"Essential Books by {author_name}:\n\n{agent_output}"

        return context

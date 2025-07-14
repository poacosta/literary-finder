"""Literary Cartographer agent for bibliography compilation and reading maps."""

from typing import Any, Dict, List, Optional
from langchain.tools import Tool
from ..tools import GoogleBooksAPI
from ..models import ReadingMap, ReadingMapEntry
from .base import BaseAgent
import logging
from collections import defaultdict

logger = logging.getLogger(__name__)


class LiteraryCartographer(BaseAgent):
    """Agent responsible for compiling complete bibliographies and creating reading maps."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.google_books = GoogleBooksAPI()
        self.tools = self.get_tools()
        self.agent = self._create_agent_executor()

    def get_tools(self) -> List[Tool]:
        """Get tools for bibliography compilation."""
        return [
            Tool(
                name="search_author_books",
                description="Search for all books by a specific author using Google Books API",
                func=self._search_author_books
            ),
            Tool(
                name="analyze_book_chronology",
                description="Analyze and organize books chronologically",
                func=self._analyze_chronology
            ),
            Tool(
                name="categorize_works",
                description="Categorize works by genre, theme, or type",
                func=self._categorize_works
            )
        ]

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Literary Cartographer."""
        return """You are the Literary Cartographer. Create organized reading maps and bibliographies for authors.

Tasks:
1. **Bibliography**: Find all major published works using Google Books
2. **Reading Order**: Suggest 2-3 essential works for new readers
3. **Organization**: Group works chronologically and by theme

Guidelines:
- Focus on novels, story collections, and major works
- Prioritize accessible and significant books
- Provide brief descriptions and publication years
- Create clear reading recommendations

Use available tools to research and organize the author's complete works efficiently."""

    def process(self, author_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process bibliography compilation and reading map creation."""
        try:
            logger.info(f"Starting bibliography compilation for: {author_name}")

            input_text = f"""Create a comprehensive bibliography and reading map for author: {author_name}

Please:
1. Search for all published works by this author
2. Organize them chronologically to show literary development
3. Categorize works by type, genre, or theme
4. Create strategic reading recommendations:
   - Identify 2-3 essential "Start Here" works for new readers
   - Suggest thematic groupings
   - Provide the complete chronological bibliography

Focus on major published works (novels, story collections, poetry books, significant essays) and create a strategic guide for readers."""

            result = self.agent.invoke({"input": input_text})

            reading_map = self._parse_bibliography_results(result["output"], author_name)

            return {
                "success": True,
                "data": reading_map,
                "raw_output": result["output"]
            }

        except Exception as e:
            return self._handle_error(e, "bibliography compilation")

    def _search_author_books(self, author_name: str) -> str:
        """Search for books by the author using Google Books API."""
        try:
            books = self.google_books.search_books_by_author(author_name, max_results=20)

            if not books:
                return f"No books found for author: {author_name}"

            # Organize books by publication date
            books_by_year = defaultdict(list)
            undated_books = []

            for book in books:
                if book.published_date:
                    year = book.published_date.split('-')[0]
                    try:
                        year_int = int(year)
                        books_by_year[year_int].append(book)
                    except ValueError:
                        undated_books.append(book)
                else:
                    undated_books.append(book)

            summary = f"Bibliography for {author_name} ({len(books)} works found):\n\n"

            for year in sorted(books_by_year.keys()):
                summary += f"**{year}:**\n"
                for book in books_by_year[year]:
                    summary += f"  - {book.title}"
                    if book.categories:
                        summary += f" (Categories: {', '.join(book.categories[:2])})"
                    summary += "\n"
                summary += "\n"

            if undated_books:
                summary += "**Date Unknown:**\n"
                for book in undated_books[:5]:
                    summary += f"  - {book.title}\n"
                summary += "\n"

            return summary

        except Exception as e:
            logger.error(f"Error searching author books: {e}")
            return f"Error searching books: {str(e)}"

    def _analyze_chronology(self, query: str) -> str:
        """Analyze chronological development of an author's works."""
        try:
            import re
            author_match = re.search(r"for (.+?)(?:\s|$)", query)
            author_name = author_match.group(1) if author_match else query

            books = self.google_books.search_books_by_author(author_name, max_results=20)

            if not books:
                return f"No books found for chronological analysis of {author_name}"

            dated_books = [book for book in books if book.published_date]
            dated_books.sort(key=lambda x: x.published_date)

            analysis = f"Chronological analysis for {author_name}:\n\n"

            if dated_books:
                analysis += "**Literary Development Timeline:**\n"
                current_decade = None

                for book in dated_books:
                    try:
                        year_str = book.published_date.split('-')[0]
                        year_str = ''.join(c for c in year_str if c.isdigit())
                        year = int(year_str) if year_str else None
                        if year is None:
                            continue
                        decade = (year // 10) * 10
                    except (ValueError, IndexError):
                        continue

                    if decade != current_decade:
                        analysis += f"\n**{decade}s:**\n"
                        current_decade = decade

                    analysis += f"  {year}: {book.title}\n"
                    if book.description:
                        desc = book.description[:100] + "..." if len(book.description) > 100 else book.description
                        analysis += f"    - {desc}\n"

            return analysis

        except Exception as e:
            logger.error(f"Error analyzing chronology: {e}")
            return f"Error analyzing chronology: {str(e)}"

    def _categorize_works(self, query: str) -> str:
        """Categorize author's works by genre, theme, or type."""
        try:
            import re
            author_match = re.search(r"for (.+?)(?:\s|$)", query)
            author_name = author_match.group(1) if author_match else query

            books = self.google_books.search_books_by_author(author_name, max_results=20)

            if not books:
                return f"No books found for categorization of {author_name}"

            by_category = defaultdict(list)
            uncategorized = []

            for book in books:
                if book.categories:
                    category = book.categories[0]
                    by_category[category].append(book)
                else:
                    uncategorized.append(book)

            categorization = f"Work categorization for {author_name}:\n\n"

            for category, books_in_category in by_category.items():
                categorization += f"**{category}:**\n"
                for book in books_in_category[:5]:
                    categorization += f"  - {book.title}"
                    if book.published_date:
                        year = book.published_date.split('-')[0]
                        categorization += f" ({year})"
                    categorization += "\n"
                categorization += "\n"

            # Add uncategorized
            if uncategorized:
                categorization += "**Other Works:**\n"
                for book in uncategorized[:5]:
                    categorization += f"  - {book.title}\n"

            return categorization

        except Exception as e:
            logger.error(f"Error categorizing works: {e}")
            return f"Error categorizing works: {str(e)}"

    def _extract_year(self, published_date: str) -> Optional[int]:
        """Extract year from published_date string, handling non-numeric characters."""
        try:
            year_str = published_date.split('-')[0]
            year_str = ''.join(c for c in year_str if c.isdigit())
            return int(year_str) if year_str else None
        except (ValueError, IndexError):
            return None

    def _parse_bibliography_results(self, agent_output: str, author_name: str) -> ReadingMap:
        """Parse agent output into structured ReadingMap."""

        books = self.google_books.search_books_by_author(author_name, max_results=20)

        all_entries = []
        for book in books:
            entry = ReadingMapEntry(
                title=book.title,
                year=self._extract_year(book.published_date) if book.published_date else None,
                description=book.description[:200] + "..." if book.description and len(
                    book.description) > 200 else book.description,
                isbn=book.isbn_13 or book.isbn_10,
                category=book.categories[0] if book.categories else None,
                google_books_link=book.google_books_link,
                preview_link=book.preview_link
            )
            all_entries.append(entry)

        chronological = sorted([e for e in all_entries if e.year], key=lambda x: x.year)

        reading_map = ReadingMap()

        reading_map.chronological = chronological
        reading_map.complete_works = all_entries

        start_candidates = [e for e in chronological if e.description and len(e.description) > 50]
        reading_map.start_here = start_candidates[:3] if start_candidates else chronological[:3]

        # Thematic groups by category
        by_category = defaultdict(list)
        for entry in all_entries:
            if entry.category:
                by_category[entry.category].append(entry)

        reading_map.thematic_groups = dict(by_category)

        return reading_map

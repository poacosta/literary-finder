"""Google Books API integration."""

import os
import requests
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import logging
from requests.exceptions import RequestException, ConnectionError, Timeout
from ..utils.retry import exponential_backoff, RetryError

logger = logging.getLogger(__name__)


@dataclass
class BookInfo:
    """Book information from Google Books API."""
    title: str
    authors: List[str]
    published_date: Optional[str] = None
    description: Optional[str] = None
    isbn_10: Optional[str] = None
    isbn_13: Optional[str] = None
    page_count: Optional[int] = None
    categories: List[str] = None
    language: Optional[str] = None
    google_books_link: Optional[str] = None
    preview_link: Optional[str] = None


class GoogleBooksAPI:
    """Google Books API client."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.base_url = "https://www.googleapis.com/books/v1/volumes"

        if not self.api_key:
            logger.warning("Google Books API key not found. Some features may be limited.")

    @exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=15.0,
        retry_on_exceptions=[RequestException, ConnectionError, Timeout]
    )
    def search_books_by_author(
            self,
            author_name: str,
            max_results: int = 40
    ) -> List[BookInfo]:
        """Search for books by a specific author."""
        try:
            params = {
                "q": f"inauthor:{author_name}",
                "maxResults": max_results,
                "orderBy": "relevance"
            }

            if self.api_key:
                params["key"] = self.api_key

            response = requests.get(self.base_url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()
            books = []

            for item in data.get("items", []):
                volume_info = item.get("volumeInfo", {})
                access_info = item.get("accessInfo", {})
                book = self._parse_book_info(volume_info, access_info)
                if book and author_name.lower() in " ".join(book.authors).lower():
                    books.append(book)

            logger.info(f"Found {len(books)} books for author: {author_name}")
            return books

        except RetryError as e:
            logger.error(f"All retry attempts failed for Google Books search: {e.last_exception}")
            return []
        except requests.RequestException as e:
            logger.error(f"Error searching Google Books: {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error in Google Books search: {e}")
            return []

    @exponential_backoff(
        max_retries=3,
        base_delay=1.0,
        max_delay=15.0,
        retry_on_exceptions=[RequestException, ConnectionError, Timeout]
    )
    def get_book_details(self, volume_id: str) -> Optional[BookInfo]:
        """Get detailed information about a specific book."""
        try:
            url = f"{self.base_url}/{volume_id}"
            params = {}

            if self.api_key:
                params["key"] = self.api_key

            response = requests.get(url, params=params, timeout=60)
            response.raise_for_status()

            data = response.json()
            volume_info = data.get("volumeInfo", {})
            access_info = data.get("accessInfo", {})

            return self._parse_book_info(volume_info, access_info)

        except RetryError as e:
            logger.error(f"All retry attempts failed for Google Books book details: {e.last_exception}")
            return None
        except requests.RequestException as e:
            logger.error(f"Error getting book details: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting book details: {e}")
            return None

    def _parse_book_info(self, volume_info: Dict[str, Any], access_info: Dict[str, Any] = None) -> Optional[BookInfo]:
        """Parse volume info from Google Books API response."""
        try:
            title = volume_info.get("title")
            authors = volume_info.get("authors", [])

            if not title or not authors:
                return None

            isbn_10 = None
            isbn_13 = None

            for identifier in volume_info.get("industryIdentifiers", []):
                if identifier.get("type") == "ISBN_10":
                    isbn_10 = identifier.get("identifier")
                elif identifier.get("type") == "ISBN_13":
                    isbn_13 = identifier.get("identifier")

            google_books_link = volume_info.get("infoLink")
            preview_link = volume_info.get("previewLink")

            if access_info:
                web_reader_link = access_info.get("webReaderLink")
                if web_reader_link:
                    preview_link = web_reader_link

            return BookInfo(
                title=title,
                authors=authors,
                published_date=volume_info.get("publishedDate"),
                description=volume_info.get("description"),
                isbn_10=isbn_10,
                isbn_13=isbn_13,
                page_count=volume_info.get("pageCount"),
                categories=volume_info.get("categories", []),
                language=volume_info.get("language"),
                google_books_link=google_books_link,
                preview_link=preview_link
            )

        except Exception as e:
            logger.error(f"Error parsing book info: {e}")
            return None

"""OpenAI Web Search API integration."""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from openai import OpenAI

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Search result from OpenAI Web Search API."""
    title: str
    link: str
    snippet: str
    display_link: Optional[str] = None


class OpenAISearchAPI:
    """OpenAI Web Search API client."""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-4o"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.client = None

        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
        else:
            logger.warning(
                "OpenAI API key not found. "
                "Search functionality will be limited."
            )

    def search_author_biography(
            self,
            author_name: str,
            num_results: int = 10
    ) -> List[SearchResult]:
        """Search for biographical information about an author."""
        query = f'Find biographical information about author "{author_name}" including birth date, death date, major works, and literary significance'
        return self._search_with_context(query, "biography")

    def search_author_criticism(
            self,
            author_name: str,
            num_results: int = 10
    ) -> List[SearchResult]:
        """Search for literary criticism and analysis of an author."""
        query = f'Find literary criticism, scholarly analysis, and academic papers about author "{author_name}" and their themes, style, and literary contributions'
        return self._search_with_context(query, "criticism")

    def search_author_influences(
            self,
            author_name: str,
            num_results: int = 8
    ) -> List[SearchResult]:
        """Search for information about an author's influences and influences on others."""
        query = f'Find information about "{author_name}" literary influences, who influenced them, and who they influenced in literature'
        return self._search_with_context(query, "influences")

    def search_similar_authors(
            self,
            author_name: str,
            num_results: int = 10
    ) -> List[SearchResult]:
        """Search for authors similar to the given author."""
        query = f'Find authors similar to "{author_name}" with comparable writing styles, themes, or literary movements'
        return self._search_with_context(query, "similar_authors")

    def _search_with_context(
            self,
            query: str,
            context: str
    ) -> List[SearchResult]:
        """Perform a web search using OpenAI's web search tool."""
        if not self.client:
            logger.error("OpenAI client not properly configured")
            return []

        try:
            from openai import OpenAI

            if hasattr(self.client, 'responses'):
                response = self.client.responses.create(
                    model=self.model,
                    input=f"{query}. Please provide search results with titles, URLs, and brief descriptions.",
                    tools=[
                        {
                            "type": "web_search"
                        }
                    ]
                )
            else:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {
                            "role": "user",
                            "content": f"{query}. Please search the web and provide relevant information with sources."
                        }
                    ]
                )

            results = self._parse_response(response, context)
            logger.info(f"Found {len(results)} search results for query: {query}")
            return results

        except Exception as e:
            logger.error(f"Error performing OpenAI web search: {e}")
            return []

    def _parse_response(self, response, context: str) -> List[SearchResult]:
        """Parse OpenAI response to extract search results."""
        results = []

        try:
            content = ""

            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
            elif hasattr(response, 'content'):
                content = response.content
            elif hasattr(response, 'response') and hasattr(response.response, 'content'):
                content = response.response.content
            else:
                content = getattr(response, 'text', str(response)[:200])

            if not content or content == "None":
                content = f"OpenAI web search completed for {context}"

            result = SearchResult(
                title=f"OpenAI Web Search - {context.title()}",
                link="https://openai.com/search",  # Placeholder link
                snippet=content[:300] + "..." if len(content) > 300 else content,
                display_link="OpenAI Web Search"
            )
            results.append(result)

        except Exception as e:
            logger.error(f"Error parsing OpenAI search response: {e}")

            result = SearchResult(
                title=f"OpenAI Web Search - {context.title()}",
                link="https://openai.com/search",
                snippet=f"Web search completed for {context}",
                display_link="OpenAI Web Search"
            )
            results.append(result)

        return results

    def search(self, query: str) -> List[SearchResult]:
        """Generic search method."""
        return self._search_with_context(query, "general")

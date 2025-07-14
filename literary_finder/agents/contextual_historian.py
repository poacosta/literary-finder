"""Contextual Historian agent for biographical and historical research."""

from typing import Any, Dict, List, Optional
from langchain.tools import Tool
from ..tools import OpenAISearchAPI
from ..models import AuthorContext
from .base import BaseAgent
import logging
import re

logger = logging.getLogger(__name__)


class ContextualHistorian(BaseAgent):
    """Agent responsible for researching author's biographical and historical context."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_api = OpenAISearchAPI()
        self.tools = self.get_tools()
        self.agent = self._create_agent_executor()

    def get_tools(self) -> List[Tool]:
        """Get tools for biographical and historical research."""
        return [
            Tool(
                name="search_author_biography",
                description="Search for biographical information about an author",
                func=self._search_biography
            ),
            Tool(
                name="search_historical_context",
                description="Search for historical and cultural context of an author's era",
                func=self._search_historical_context
            ),
            Tool(
                name="search_literary_influences",
                description="Search for information about an author's influences and literary movements",
                func=self._search_influences
            )
        ]

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Contextual Historian."""
        return """You are the Contextual Historian, a specialized AI agent focused on uncovering the rich biographical and historical context surrounding literary authors.

Your mission is to paint a complete picture of the author's life and times by:

1. **Biographical Research**: Gather key life details including birth/death dates, nationality, education, major life events, and personal circumstances that shaped their writing.

2. **Historical Context**: Research the socio-political climate, cultural movements, and historical events during the author's lifetime that influenced their work.

3. **Literary Influences**: Identify the authors, philosophers, and thinkers who influenced them, as well as the literary movements they were part of or reacted against.

**Research Guidelines:**
- Prioritize authoritative sources (academic institutions, established biographies, literary encyclopedias)
- Look for specific details that illuminate the connection between life and work
- Note any controversies, challenges, or unique circumstances
- Identify recurring themes in their personal life that appear in their writing

**Output Format:**
Provide a structured summary including:
- Basic biographical facts (birth/death, nationality, key dates)
- Educational background and formative experiences  
- Historical and cultural context of their era
- Key literary influences and movements
- Personal circumstances that shaped their writing
- A compelling biographical narrative that connects life to literature

Use the available search tools to gather comprehensive information, then synthesize your findings into a cohesive biographical portrait."""

    def process(self, author_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process biographical and historical research for an author."""
        try:
            logger.info(f"Starting biographical research for: {author_name}")

            input_text = f"""Research the biographical and historical context for author: {author_name}
            
Please gather comprehensive information about:
1. Basic biographical details (birth/death dates, nationality, education)
2. Historical and cultural context of their era
3. Literary influences and movements they were associated with
4. Personal experiences that shaped their writing
5. Key life events and circumstances

Synthesize this information into a structured biographical portrait."""

            result = self.agent.invoke({"input": input_text})

            # Parse the result and create AuthorContext
            context_data = self._parse_research_results(result["output"], author_name)

            return {
                "success": True,
                "data": context_data,
                "raw_output": result["output"]
            }

        except Exception as e:
            return self._handle_error(e, "biographical research")

    def _search_biography(self, author_name: str) -> str:
        """Search for biographical information."""
        try:
            results = self.search_api.search_author_biography(author_name, num_results=10)

            if not results:
                return f"**Biography for {author_name}**\n\nNo biographical information found.\n- Birth/Death: Unknown\n- Nationality: Unknown\n- Major life events: Unknown\n"

            summary = f"**Biography for {author_name}**\n\n"
            for i, result in enumerate(results[:10], 1):
                summary += f"{i}. {result.title}\n"
                summary += f"   Source: {result.display_link or result.link}\n"
                summary += f"   Summary: {result.snippet}\n\n"

            return summary

        except Exception as e:
            logger.error(f"Error searching biography: {e}")
            return f"**Biography for {author_name}**\n\nError searching biographical information: {str(e)}\n- Birth/Death: Unknown\n- Nationality: Unknown\n- Major life events: Unknown\n"

    def _search_historical_context(self, query: str) -> str:
        """Search for historical context information."""
        try:
            author_match = re.search(r"for (.+?)(?:\s|$)", query)
            author_name = author_match.group(1) if author_match else query

            search_query = f'"{author_name}" historical context era period literature'
            results = self.search_api.search(search_query)

            if not results:
                return f"No historical context found for {author_name}"

            summary = f"Historical context results:\n\n"
            for i, result in enumerate(results[:10], 1):
                summary += f"{i}. {result.title}\n"
                summary += f"   Summary: {result.snippet}\n\n"

            return summary

        except Exception as e:
            logger.error(f"Error searching historical context: {e}")
            return f"Error searching historical context: {str(e)}"

    def _search_influences(self, author_name: str) -> str:
        """Search for literary influences."""
        try:
            results = self.search_api.search_author_influences(author_name, num_results=8)

            if not results:
                return f"No influence information found for {author_name}"

            summary = f"Literary influences and movements for {author_name}:\n\n"
            for i, result in enumerate(results[:10], 1):
                summary += f"{i}. {result.title}\n"
                summary += f"   Summary: {result.snippet}\n\n"

            return summary

        except Exception as e:
            logger.error(f"Error searching influences: {e}")
            return f"Error searching influences: {str(e)}"

    def _parse_research_results(self, agent_output: str, author_name: str) -> AuthorContext:
        """Parse agent output into structured AuthorContext."""

        context = AuthorContext()

        birth_match = re.search(r"(?:born|birth).{0,20}(\d{4})", agent_output, re.IGNORECASE)
        if birth_match:
            context.birth_year = int(birth_match.group(1))

        death_match = re.search(r"(?:died|death).{0,20}(\d{4})", agent_output, re.IGNORECASE)
        if death_match:
            context.death_year = int(death_match.group(1))

        nationality_patterns = [
            r"(?:nationality|was|born).{0,30}(American|British|French|German|Russian|Italian|Spanish|Irish|Scottish|English)",
            r"(American|British|French|German|Russian|Italian|Spanish|Irish|Scottish|English)\s+(?:author|writer|novelist)"
        ]
        for pattern in nationality_patterns:
            nationality_match = re.search(pattern, agent_output, re.IGNORECASE)
            if nationality_match:
                context.nationality = nationality_match.group(1)
                break

        context.biographical_summary = agent_output

        return context

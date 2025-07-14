"""Legacy Connector agent for style analysis"""

from typing import Any, Dict, List, Optional
from langchain.tools import Tool
from ..tools import OpenAISearchAPI
from ..models import LegacyAnalysis
from .base import BaseAgent
import logging
import re

logger = logging.getLogger(__name__)


class LegacyConnector(BaseAgent):
    """Agent responsible for analyzing author's legacy."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_api = OpenAISearchAPI()
        self.tools = self.get_tools()
        self.agent = self._create_agent_executor()

    def get_tools(self) -> List[Tool]:
        """Get tools for legacy analysis."""
        return [
            Tool(
                name="search_literary_criticism",
                description="Search for academic criticism and analysis of the author's work",
                func=self._search_criticism
            ),
            Tool(
                name="search_themes_and_style",
                description="Search for analysis of the author's recurring themes and style",
                func=self._search_themes_style
            )
        ]

    def get_system_prompt(self) -> str:
        """Get the system prompt for the Legacy Connector."""
        return """You are the Legacy Connector. Analyze literary legacy and provide author's book insights.

Tasks:
1. **Style Analysis**: Identify key writing techniques and innovations
2. **Themes**: Find recurring themes and subjects in their work

Guidelines:
- Search for criticism and scholarly analysis
- Focus on stylistic innovations and major themes

Use available tools to research thoroughly and provide actionable reading recommendations."""

    def process(self, author_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process legacy analysis and recommendations."""
        try:
            logger.info(f"Starting legacy analysis for: {author_name}")

            input_text = f"""Analyze the literary legacy and create recommendations for author: {author_name}

Please research and analyze:
1. The author's unique stylistic innovations and literary techniques
2. Recurring themes and philosophical concerns in their work

Provide a comprehensive analysis that helps readers understand both the author's importance and where to go next in their literary journey."""

            result = self.agent.invoke({"input": input_text})

            legacy_analysis = self._parse_legacy_results(result["output"], author_name)

            return {
                "success": True,
                "data": legacy_analysis,
                "raw_output": result["output"]
            }

        except Exception as e:
            return self._handle_error(e, "legacy analysis")

    def _search_criticism(self, author_name: str) -> str:
        """Search for academic criticism and literary analysis."""
        try:
            results = self.search_api.search_author_criticism(author_name, num_results=8)

            if not results:
                return f"No critical analysis found for {author_name}"

            summary = f"Literary criticism and analysis for {author_name}:\n\n"
            for i, result in enumerate(results[:10], 1):
                summary += f"{i}. {result.title}\n"
                summary += f"   Source: {result.display_link or result.link}\n"
                summary += f"   Analysis: {result.snippet}\n\n"

            return summary

        except Exception as e:
            logger.error(f"Error searching criticism: {e}")
            return f"Error searching literary criticism: {str(e)}"

    def _search_themes_style(self, author_name: str) -> str:
        """Search for analysis of themes and writing style."""
        try:
            # Search for thematic and stylistic analysis
            search_query = f'"{author_name}" themes style writing technique literary analysis'
            results = self.search_api.search(search_query)

            if not results:
                return f"No thematic or stylistic analysis found for {author_name}"

            summary = f"Themes and style analysis for {author_name}:\n\n"
            for i, result in enumerate(results[:10], 1):
                summary += f"{i}. {result.title}\n"
                summary += f"   Analysis: {result.snippet}\n\n"

            return summary

        except Exception as e:
            logger.error(f"Error searching themes and style: {e}")
            return f"Error searching themes and style: {str(e)}"

    def _parse_legacy_results(self, agent_output: str, author_name: str) -> LegacyAnalysis:
        """Parse agent output into structured LegacyAnalysis."""

        legacy = LegacyAnalysis()

        innovations_match = re.search(
            r"(?:stylistic|innovations?|techniques?).{0,100}?[:\n](.+?)(?:\n\n|\n[A-Z]|\n\d+\.)",
            agent_output,
            re.IGNORECASE | re.DOTALL
        )
        if innovations_match:
            innovations_text = innovations_match.group(1)
            # Extract bullet points or list items
            innovation_items = re.findall(r"[-*•]\s*(.+?)(?=\n|$)", innovations_text)
            if innovation_items:
                legacy.stylistic_innovations = [item.strip() for item in innovation_items[:5]]

        themes_match = re.search(
            r"(?:themes?|recurring|concerns?).{0,100}?[:\n](.+?)(?:\n\n|\n[A-Z]|\n\d+\.)",
            agent_output,
            re.IGNORECASE | re.DOTALL
        )
        if themes_match:
            themes_text = themes_match.group(1)
            theme_items = re.findall(r"[-*•]\s*(.+?)(?=\n|$)", themes_text)
            if theme_items:
                legacy.recurring_themes = [item.strip() for item in theme_items[:5]]

        legacy.literary_significance = agent_output

        relevance_match = re.search(
            r"(?:modern|contemporary|relevant|today).{0,200}",
            agent_output,
            re.IGNORECASE
        )
        if relevance_match:
            legacy.modern_relevance = relevance_match.group(0)

        return legacy

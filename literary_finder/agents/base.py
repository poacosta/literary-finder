"""Base agent class for the Literary Finder system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from langchain.agents import AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langsmith import traceable
import logging
import os

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """
    Base class for all Literary Finder agents.
    
    Each agent in the Literary Finder system has a specialized role:
    - Contextual Historian: Biographical and historical research specialist
    - Literary Cartographer: Bibliography compilation and reading map creation expert  
    - Legacy Connector: Literary analysis and critical assessment specialist
    
    All agents share common capabilities: OpenAI LLM integration, tool management,
    error handling, and standardized processing workflows.
    """

    def __init__(
            self,
            model_name: Optional[str] = None
    ):
        # Initialize OpenAI LLM
        model_name = model_name or "gpt-4"
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        self.llm = ChatOpenAI(
            model=model_name,
            api_key=api_key
        )

        # Will be set by subclasses
        self.tools = []
        self.agent = None

        logger.info(f"Initialized {self.__class__.__name__} with OpenAI ({model_name})")

    @abstractmethod
    def get_agent_role(self) -> str:
        """Get the specific role and specialization of this agent."""
        pass

    @abstractmethod
    def get_tools(self) -> list[Tool]:
        """Get the tools this agent uses."""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """Get the system prompt for this agent."""
        pass

    @abstractmethod
    @traceable(name="agent_process")
    def process(self, author_name: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process the author information and return results."""
        pass

    def get_performance_metrics(self) -> Dict[str, Any]:
        """Get performance metrics for this agent."""
        return {
            "agent_role": self.get_agent_role(),
            "tools_count": len(self.get_tools()),
            "model_name": getattr(self, 'llm', {}).model_name if hasattr(self, 'llm') else "unknown"
        }

    def _create_agent_executor(self) -> AgentExecutor:
        """Create the agent executor with OpenAI function calling."""
        from langchain.agents import create_openai_functions_agent
        from langchain_core.prompts import ChatPromptTemplate

        # Create a function calling prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", self.get_system_prompt()),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}")
        ])

        # Create agent using OpenAI function calling (faster than ReAct)
        agent = create_openai_functions_agent(
            llm=self.llm,
            tools=self.get_tools(),
            prompt=prompt
        )

        # Create executor with optimized settings
        return AgentExecutor(
            agent=agent,
            tools=self.get_tools(),
            verbose=True,
            max_iterations=10,
            max_execution_time=300,
            return_intermediate_steps=True
        )

    def _handle_error(self, error: Exception, context: str) -> Dict[str, Any]:
        """Handle errors gracefully and return error information."""
        error_msg = f"Error in {self.__class__.__name__} during {context}: {str(error)}"
        logger.error(error_msg)

        return {
            "success": False,
            "error": error_msg,
            "data": None
        }

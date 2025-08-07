"""Configuration module for Literary Finder."""

import os
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


class LangSmithConfig:
    """Configuration for LangSmith tracing."""
    
    @classmethod
    def setup_tracing(cls, project_name: Optional[str] = None) -> None:
        """Setup LangSmith tracing with environment variables."""
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        
        api_key = os.getenv("LANGCHAIN_API_KEY")
        if api_key:
            os.environ["LANGCHAIN_API_KEY"] = api_key
        
        if project_name:
            os.environ["LANGCHAIN_PROJECT"] = project_name
        elif not os.getenv("LANGCHAIN_PROJECT"):
            # Default project name based on environment
            env = os.getenv("ENVIRONMENT", "dev")
            os.environ["LANGCHAIN_PROJECT"] = f"literary-finder-{env}"
    
    @classmethod
    def is_enabled(cls) -> bool:
        """Check if LangSmith tracing is enabled."""
        return (
            os.getenv("LANGCHAIN_TRACING_V2", "").lower() == "true" and
            bool(os.getenv("LANGCHAIN_API_KEY"))
        )
    
    @classmethod
    def get_project_name(cls) -> str:
        """Get the current LangSmith project name."""
        return os.getenv("LANGCHAIN_PROJECT", "literary-finder")


class Config:
    """Main configuration class."""
    
    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
    LANGCHAIN_API_KEY = os.getenv("LANGCHAIN_API_KEY")
    
    # Environment
    ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
    
    # LangSmith
    LANGSMITH_ENABLED = LangSmithConfig.is_enabled()
    LANGSMITH_PROJECT = LangSmithConfig.get_project_name()
    
    @classmethod
    def validate_required_keys(cls) -> None:
        """Validate that required API keys are present."""
        if not cls.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        if cls.LANGSMITH_ENABLED and not cls.LANGCHAIN_API_KEY:
            raise ValueError("LANGCHAIN_API_KEY is required when LANGCHAIN_TRACING_V2=true")
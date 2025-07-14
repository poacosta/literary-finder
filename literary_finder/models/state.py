"""State management models for the Literary Finder system."""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from enum import Enum


class AgentStatus(str, Enum):
    """Status of individual agents."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ReadingMapEntry(BaseModel):
    """Individual entry in a reading map."""
    title: str
    year: Optional[int] = None
    description: Optional[str] = None
    isbn: Optional[str] = None
    category: Optional[str] = None
    difficulty_level: Optional[str] = None
    google_books_link: Optional[str] = None
    preview_link: Optional[str] = None


class ReadingMap(BaseModel):
    """Structured reading map for an author."""
    start_here: List[ReadingMapEntry] = Field(default_factory=list)
    chronological: List[ReadingMapEntry] = Field(default_factory=list)
    thematic_groups: Dict[str, List[ReadingMapEntry]] = Field(default_factory=dict)
    complete_works: List[ReadingMapEntry] = Field(default_factory=list)


class AuthorContext(BaseModel):
    """Biographical and historical context for an author."""
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    nationality: Optional[str] = None
    literary_movements: List[str] = Field(default_factory=list)
    key_influences: List[str] = Field(default_factory=list)
    historical_context: Optional[str] = None
    biographical_summary: Optional[str] = None


class LegacyAnalysis(BaseModel):
    """Analysis of author's legacy and recommendations."""
    stylistic_innovations: List[str] = Field(default_factory=list)
    recurring_themes: List[str] = Field(default_factory=list)
    literary_significance: Optional[str] = None
    modern_relevance: Optional[str] = None
    similar_authors: List[Dict[str, str]] = Field(default_factory=list)
    critical_acclaim: Optional[str] = None


class AgentResults(BaseModel):
    """Results from individual agents."""
    contextual_historian: Optional[AuthorContext] = None
    literary_cartographer: Optional[ReadingMap] = None
    legacy_connector: Optional[LegacyAnalysis] = None


class LiteraryFinderState(BaseModel):
    """Main state object for the Literary Finder system."""

    # Input
    author_name: str

    # Agent statuses
    agent_statuses: Dict[str, AgentStatus] = Field(
        default_factory=lambda: {
            "contextual_historian": AgentStatus.PENDING,
            "literary_cartographer": AgentStatus.PENDING,
            "legacy_connector": AgentStatus.PENDING
        }
    )

    # Agent results
    results: AgentResults = Field(default_factory=AgentResults)

    # Final output
    final_report: Optional[str] = None

    # Metadata
    processing_started_at: Optional[str] = None
    processing_completed_at: Optional[str] = None
    errors: List[str] = Field(default_factory=list)

    # Configuration
    max_retries: int = Field(default=10)
    timeout_seconds: int = Field(default=300)


class APIResponse(BaseModel):
    """Standard API response format."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    processing_time_seconds: Optional[float] = None

"""Unit tests for data models."""

import pytest
from literary_finder.models import (
    LiteraryFinderState,
    AgentStatus,
    AuthorContext,
    ReadingMap,
    ReadingMapEntry,
    LegacyAnalysis,
    APIResponse,
)


def test_reading_map_entry():
    """Test ReadingMapEntry model."""
    entry = ReadingMapEntry(
        title="1984",
        year=1949,
        description="A dystopian novel",
        isbn="978-0-452-28423-4",
        category="Fiction"
    )

    assert entry.title == "1984"
    assert entry.year == 1949
    assert entry.description == "A dystopian novel"
    assert entry.isbn == "978-0-452-28423-4"
    assert entry.category == "Fiction"


def test_author_context():
    """Test AuthorContext model."""
    context = AuthorContext(
        birth_year=1903,
        death_year=1950,
        nationality="British",
        literary_movements=["Modernism", "Dystopian Fiction"],
        key_influences=["H.G. Wells", "Jack London"],
        biographical_summary="Eric Arthur Blair, known by his pen name George Orwell..."
    )

    assert context.birth_year == 1903
    assert context.death_year == 1950
    assert context.nationality == "British"
    assert "Modernism" in context.literary_movements
    assert "H.G. Wells" in context.key_influences


def test_legacy_analysis():
    """Test LegacyAnalysis model."""
    legacy = LegacyAnalysis(
        stylistic_innovations=["Stream of consciousness", "Interior monologue"],
        recurring_themes=["Time", "Memory", "Identity"],
        literary_significance="Major modernist writer",
        similar_authors=[
            {"name": "James Joyce", "reason": "Similar modernist techniques"},
            {"name": "Marcel Proust", "reason": "Focus on time and memory"}
        ]
    )

    assert len(legacy.stylistic_innovations) == 2
    assert "Time" in legacy.recurring_themes
    assert legacy.literary_significance == "Major modernist writer"
    assert len(legacy.similar_authors) == 2
    assert legacy.similar_authors[0]["name"] == "James Joyce"


def test_literary_finder_state():
    """Test LiteraryFinderState model."""
    state = LiteraryFinderState(author_name="Virginia Woolf")

    assert state.author_name == "Virginia Woolf"
    assert state.agent_statuses["contextual_historian"] == AgentStatus.PENDING
    assert state.agent_statuses["literary_cartographer"] == AgentStatus.PENDING
    assert state.agent_statuses["legacy_connector"] == AgentStatus.PENDING
    assert state.final_report is None
    assert len(state.errors) == 0


def test_reading_map():
    """Test ReadingMap model."""
    entry1 = ReadingMapEntry(title="Mrs. Dalloway", year=1925)
    entry2 = ReadingMapEntry(title="To the Lighthouse", year=1927)

    reading_map = ReadingMap(
        start_here=[entry1],
        chronological=[entry1, entry2],
        thematic_groups={"Modernist": [entry1, entry2]}
    )

    assert len(reading_map.start_here) == 1
    assert len(reading_map.chronological) == 2
    assert "Modernist" in reading_map.thematic_groups
    assert len(reading_map.thematic_groups["Modernist"]) == 2


def test_api_response():
    """Test APIResponse model."""
    # Success response
    success_response = APIResponse(
        success=True,
        data={"author": "Test Author"},
        processing_time_seconds=12.5
    )

    assert success_response.success is True
    assert success_response.data["author"] == "Test Author"
    assert success_response.error is None

    # Error response
    error_response = APIResponse(
        success=False,
        error="API key not found"
    )

    assert error_response.success is False
    assert error_response.error == "API key not found"
    assert error_response.data is None


def test_agent_status_enum():
    """Test AgentStatus enum values."""
    assert AgentStatus.PENDING == "pending"
    assert AgentStatus.IN_PROGRESS == "in_progress"
    assert AgentStatus.COMPLETED == "completed"
    assert AgentStatus.FAILED == "failed"


def test_agent_results_model():
    """Test AgentResults model with all fields."""
    from literary_finder.models import AgentResults, AuthorContext, ReadingMap, LegacyAnalysis
    author_ctx = AuthorContext(birth_year=1800)
    reading_map = ReadingMap()
    legacy = LegacyAnalysis(literary_significance="Significant")
    results = AgentResults(
        contextual_historian=author_ctx,
        literary_cartographer=reading_map,
        legacy_connector=legacy
    )
    assert results.contextual_historian.birth_year == 1800
    assert isinstance(results.literary_cartographer, ReadingMap)
    assert results.legacy_connector.literary_significance == "Significant"


def test_reading_map_entry_all_fields():
    """Test ReadingMapEntry with all optional fields."""
    from literary_finder.models import ReadingMapEntry
    entry = ReadingMapEntry(
        title="Book Title",
        year=2000,
        description="Desc",
        isbn="1234567890",
        category="Cat",
        difficulty_level="Advanced",
        google_books_link="http://books.google.com",
        preview_link="http://preview.com"
    )
    assert entry.difficulty_level == "Advanced"
    assert entry.google_books_link.startswith("http")
    assert entry.preview_link.startswith("http")


def test_reading_map_all_fields():
    """Test ReadingMap with all fields including complete_works."""
    from literary_finder.models import ReadingMap, ReadingMapEntry
    entry = ReadingMapEntry(title="Book")
    reading_map = ReadingMap(
        start_here=[entry],
        chronological=[entry],
        thematic_groups={"Group": [entry]},
        complete_works=[entry]
    )
    assert len(reading_map.complete_works) == 1


def test_author_context_all_fields():
    """Test AuthorContext with all optional fields."""
    from literary_finder.models import AuthorContext
    ctx = AuthorContext(
        birth_year=1900,
        death_year=1950,
        nationality="Test",
        literary_movements=["A"],
        key_influences=["B"],
        historical_context="History",
        biographical_summary="Bio"
    )
    assert ctx.historical_context == "History"
    assert ctx.biographical_summary == "Bio"


def test_legacy_analysis_all_fields():
    """Test LegacyAnalysis with all optional fields."""
    from literary_finder.models import LegacyAnalysis
    legacy = LegacyAnalysis(
        stylistic_innovations=["Style"],
        recurring_themes=["Theme"],
        literary_significance="Significance",
        modern_relevance="Modern",
        similar_authors=[{"name": "Author", "reason": "Reason"}],
        critical_acclaim="Acclaim"
    )
    assert legacy.modern_relevance == "Modern"
    assert legacy.critical_acclaim == "Acclaim"


def test_literary_finder_state_all_fields():
    """Test LiteraryFinderState with all optional and config fields."""
    from literary_finder.models import LiteraryFinderState, AgentResults
    state = LiteraryFinderState(
        author_name="Test Author",
        results=AgentResults(),
        final_report="Report",
        processing_started_at="2024-01-01T00:00:00Z",
        processing_completed_at="2024-01-01T01:00:00Z",
        errors=["error1"],
        max_retries=5,
        timeout_seconds=100
    )
    assert state.final_report == "Report"
    assert state.processing_started_at.startswith("2024")
    assert state.processing_completed_at.endswith("Z")
    assert state.max_retries == 5
    assert state.timeout_seconds == 100
    assert state.errors == ["error1"]

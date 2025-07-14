"""Integration tests for data models and their interactions."""

from literary_finder.models import (
    LiteraryFinderState,
    AgentStatus,
    AuthorContext,
    ReadingMap,
    ReadingMapEntry,
    LegacyAnalysis,
    APIResponse,
    AgentResults,
)

def test_full_state_flow():
    """Test creating a full LiteraryFinderState with all nested models and updating statuses/results."""
    # Create entries and models
    entry = ReadingMapEntry(title="Book", year=2001)
    reading_map = ReadingMap(
        start_here=[entry],
        chronological=[entry],
        thematic_groups={"Group": [entry]},
        complete_works=[entry]
    )
    author_ctx = AuthorContext(
        birth_year=1950,
        death_year=2000,
        nationality="Test",
        literary_movements=["Movement"],
        key_influences=["Influence"],
        historical_context="Context",
        biographical_summary="Bio"
    )
    legacy = LegacyAnalysis(
        stylistic_innovations=["Style"],
        recurring_themes=["Theme"],
        literary_significance="Significance",
        modern_relevance="Modern",
        similar_authors=[{"name": "Author", "reason": "Reason"}],
        critical_acclaim="Acclaim"
    )
    results = AgentResults(
        contextual_historian=author_ctx,
        literary_cartographer=reading_map,
        legacy_connector=legacy
    )
    state = LiteraryFinderState(
        author_name="Test Author",
        results=results,
        final_report="Report",
        processing_started_at="2024-01-01T00:00:00Z",
        processing_completed_at="2024-01-01T01:00:00Z",
        errors=["error1"],
        max_retries=5,
        timeout_seconds=100
    )
    # Update agent statuses
    state.agent_statuses["contextual_historian"] = AgentStatus.COMPLETED
    state.agent_statuses["literary_cartographer"] = AgentStatus.COMPLETED
    state.agent_statuses["legacy_connector"] = AgentStatus.FAILED
    assert state.agent_statuses["contextual_historian"] == AgentStatus.COMPLETED
    assert state.results.contextual_historian.birth_year == 1950
    assert state.results.literary_cartographer.start_here[0].title == "Book"
    assert state.results.legacy_connector.critical_acclaim == "Acclaim"
    assert state.final_report == "Report"
    assert state.errors == ["error1"]


def test_api_response_integration():
    """Test APIResponse with LiteraryFinderState as data."""
    state = LiteraryFinderState(author_name="Author")
    response = APIResponse(success=True, data=state, processing_time_seconds=1.2)
    assert response.success is True
    assert isinstance(response.data, LiteraryFinderState)
    assert response.processing_time_seconds == 1.2
    error_response = APIResponse(success=False, error="fail")
    assert error_response.success is False
    assert error_response.error == "fail"
    assert error_response.data is None

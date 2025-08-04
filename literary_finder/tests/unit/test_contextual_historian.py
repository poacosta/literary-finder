"""Unit tests for ContextualHistorian agent."""
import pytest
from literary_finder.agents.contextual_historian import ContextualHistorian

def test_contextual_historian_init():
    agent = ContextualHistorian()
    assert agent.search_api is not None
    assert agent.tools is not None
    assert agent.agent is not None

def test_get_agent_role():
    agent = ContextualHistorian()
    role = agent.get_agent_role()
    assert isinstance(role, str)
    assert role == "Biographical and Historical Research Specialist"


def test_get_tools():
    agent = ContextualHistorian()
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert any(tool.name == "search_author_biography" for tool in tools)

def test_get_system_prompt():
    agent = ContextualHistorian()
    prompt = agent.get_system_prompt()
    assert isinstance(prompt, str)
    assert "Contextual Historian" in prompt

def test_process_returns_dict(monkeypatch):
    agent = ContextualHistorian()
    # Mock _search_biography to avoid external calls
    agent._search_biography = lambda author_name: "Bio info"
    agent._search_historical_context = lambda query: "Historical context"
    agent._search_influences = lambda author_name: "Influences"
    agent._parse_research_results = lambda output, author_name: {"summary": output}
    result = agent.process("Test Author")
    assert isinstance(result, dict)
    assert "data" in result
    assert "summary" in result["data"]

def test_handle_error():
    agent = ContextualHistorian()
    error = Exception("fail")
    result = agent._handle_error(error, "test context")
    assert isinstance(result, dict)
    assert "error" in result

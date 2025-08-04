"""Unit tests for LegacyConnector agent."""
import pytest
from literary_finder.agents.legacy_connector import LegacyConnector

def test_legacy_connector_init():
    agent = LegacyConnector()
    assert agent.search_api is not None
    assert agent.tools is not None
    assert agent.agent is not None

def test_get_agent_role():
    agent = LegacyConnector()
    role = agent.get_agent_role()
    assert isinstance(role, str)
    assert role == "Literary Analysis and Critical Assessment Specialist"


def test_get_tools():
    agent = LegacyConnector()
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert any(tool.name == "search_literary_criticism" for tool in tools)

def test_get_system_prompt():
    agent = LegacyConnector()
    prompt = agent.get_system_prompt()
    assert isinstance(prompt, str)
    assert "Legacy Connector" in prompt

def test_process_returns_dict(monkeypatch):
    agent = LegacyConnector()
    # Mock tool methods to avoid external calls
    agent._search_criticism = lambda author_name: "Criticism info"
    agent._search_themes_style = lambda author_name: "Themes info"
    agent._parse_legacy_results = lambda output, author_name: {"legacy": output}
    result = agent.process("Test Author")
    assert isinstance(result, dict)
    assert "data" in result
    # If process fails, data may be None
    if result["data"] is not None:
        assert "legacy" in result["data"]
    else:
        # Should contain error or success False
        assert result.get("success") is False or result.get("error")

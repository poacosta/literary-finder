"""Unit tests for LiteraryCartographer agent."""
import pytest
from literary_finder.agents.literary_cartographer import LiteraryCartographer

def test_literary_cartographer_init():
    agent = LiteraryCartographer()
    assert agent.google_books is not None
    assert agent.tools is not None
    assert agent.agent is not None

def test_get_agent_role():
    agent = LiteraryCartographer()
    role = agent.get_agent_role()
    assert isinstance(role, str)
    assert role == "Bibliography Compilation and Reading Map Expert"


def test_get_tools():
    agent = LiteraryCartographer()
    tools = agent.get_tools()
    assert isinstance(tools, list)
    assert any(tool.name == "search_author_books" for tool in tools)

def test_get_system_prompt():
    agent = LiteraryCartographer()
    prompt = agent.get_system_prompt()
    assert isinstance(prompt, str)
    assert "Literary Cartographer" in prompt

def test_process_returns_dict(monkeypatch):
    agent = LiteraryCartographer()
    # Mock tool methods to avoid external calls
    agent._search_author_books = lambda author_name: "Books info"
    agent._analyze_chronology = lambda query: "Chronology"
    agent._categorize_works = lambda query: "Categories"
    agent._parse_bibliography_results = lambda output, author_name: {"bibliography": output}
    result = agent.process("Test Author")
    assert isinstance(result, dict)
    assert "data" in result
    assert "bibliography" in result["data"]

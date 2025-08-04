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

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

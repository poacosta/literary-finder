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

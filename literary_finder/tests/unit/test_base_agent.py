"""Unit tests for BaseAgent class."""
import pytest
from literary_finder.agents.base import BaseAgent

class DummyAgent(BaseAgent):
    def get_agent_role(self):
        return "Dummy"

    def get_system_prompt(self):
        return "Dummy prompt"

    def get_tools(self):
        return []

    def process(self, *args, **kwargs):
        return "Dummy process"

def test_base_agent_init(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    agent = DummyAgent()
    assert agent.llm is not None
    assert agent.get_agent_role() == "Dummy"

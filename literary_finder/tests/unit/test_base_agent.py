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

def test_get_performance_metrics(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    agent = DummyAgent()
    metrics = agent.get_performance_metrics()
    assert isinstance(metrics, dict)
    assert metrics["agent_role"] == "Dummy"
    assert metrics["tools_count"] == 0
    assert "model_name" in metrics

def test_create_agent_executor(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    agent = DummyAgent()
    # Should return an AgentExecutor instance
    executor = agent._create_agent_executor()
    assert executor is not None

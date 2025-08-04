"""Unit tests for evaluation and metrics modules."""
import pytest
from literary_finder.evaluation.metrics import AgentMetrics, SystemMetrics, QualityMetrics, PerformanceReport
from datetime import datetime

def test_agent_metrics_init():
    metrics = AgentMetrics(agent_name="TestAgent", agent_role="Role", execution_time_seconds=1.2, success=True, tools_used=["tool1"], output_quality_score=0.9, data_completeness_score=0.8)
    assert metrics.agent_name == "TestAgent"
    assert metrics.success is True
    assert metrics.tools_used == ["tool1"]


def test_system_metrics_properties():
    metrics = SystemMetrics(total_execution_time_seconds=10.0, parallel_execution=True, total_agents=3, successful_agents=2, failed_agents=1, success_rate=0.66, throughput_score=0.5)
    assert metrics.total_agents == 3
    assert metrics.successful_agents == 2
    assert metrics.failed_agents == 1


def test_quality_metrics_calculate():
    metrics = QualityMetrics(
        biographical_completeness=0.8,
        bibliography_coverage=0.7,
        analysis_depth=0.9,
        citation_quality=0.6,
        narrative_coherence=0.85,
        overall_quality=0.0
    )
    # Should calculate weighted average
    val = metrics.calculate_overall_quality()
    assert isinstance(val, float)


def test_performance_report_init():
    sys_metrics = SystemMetrics(total_execution_time_seconds=10.0, parallel_execution=True, total_agents=3, successful_agents=2, failed_agents=1, success_rate=0.66, throughput_score=0.5)
    agent_metrics = [AgentMetrics(agent_name="A", agent_role="R", execution_time_seconds=1.0, success=True)]
    report = PerformanceReport(author_name="Author", evaluation_timestamp=datetime.now(), system_metrics=sys_metrics, agent_metrics=agent_metrics)
    assert report.author_name == "Author"
    assert isinstance(report.agent_metrics, list)

"""Performance evaluation module for the Literary Finder system."""

from .real_metrics import (
    RealPerformanceEvaluator,
    RealSystemMetrics,
    RealAgentMetrics,
    RealQualityMetrics,
    RealPerformanceReport
)

# Keep old imports for backward compatibility but use real metrics
PerformanceEvaluator = RealPerformanceEvaluator
SystemMetrics = RealSystemMetrics
AgentMetrics = RealAgentMetrics
QualityMetrics = RealQualityMetrics
PerformanceReport = RealPerformanceReport

__all__ = [
    'PerformanceEvaluator',
    'SystemMetrics',
    'AgentMetrics', 
    'QualityMetrics',
    'PerformanceReport',
    'RealPerformanceEvaluator',
    'RealSystemMetrics',
    'RealAgentMetrics',
    'RealQualityMetrics',
    'RealPerformanceReport'
]
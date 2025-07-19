"""Performance metrics data models for the Literary Finder system."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class AgentMetrics:
    """Performance metrics for individual agents."""
    agent_name: str
    agent_role: str
    execution_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    tools_used: List[str] = None
    output_quality_score: Optional[float] = None
    data_completeness_score: Optional[float] = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []


@dataclass 
class SystemMetrics:
    """Overall system performance metrics."""
    total_execution_time_seconds: float
    parallel_execution: bool
    total_agents: int
    successful_agents: int
    failed_agents: int
    success_rate: float
    throughput_score: float
    overall_quality_score: Optional[float] = None
    
    @property
    def failure_rate(self) -> float:
        """Calculate failure rate."""
        return 1.0 - self.success_rate if self.success_rate else 1.0


@dataclass
class QualityMetrics:
    """Content quality assessment metrics."""
    biographical_completeness: float  # 0-1 score for biographical data completeness
    bibliography_coverage: float      # 0-1 score for bibliography comprehensiveness  
    analysis_depth: float             # 0-1 score for literary analysis quality
    citation_quality: float           # 0-1 score for source quality and citations
    narrative_coherence: float        # 0-1 score for final report coherence
    overall_quality: float            # Weighted average of above metrics
    
    def calculate_overall_quality(self) -> float:
        """Calculate weighted overall quality score."""
        weights = {
            'biographical_completeness': 0.2,
            'bibliography_coverage': 0.25, 
            'analysis_depth': 0.25,
            'citation_quality': 0.15,
            'narrative_coherence': 0.15
        }
        
        self.overall_quality = (
            self.biographical_completeness * weights['biographical_completeness'] +
            self.bibliography_coverage * weights['bibliography_coverage'] +
            self.analysis_depth * weights['analysis_depth'] +
            self.citation_quality * weights['citation_quality'] +
            self.narrative_coherence * weights['narrative_coherence']
        )
        return self.overall_quality


@dataclass
class PerformanceReport:
    """Comprehensive performance evaluation report."""
    author_name: str
    evaluation_timestamp: datetime
    system_metrics: SystemMetrics
    agent_metrics: List[AgentMetrics]
    quality_metrics: Optional[QualityMetrics] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert report to dictionary format."""
        return {
            'author_name': self.author_name,
            'evaluation_timestamp': self.evaluation_timestamp.isoformat(),
            'system_metrics': {
                'total_execution_time_seconds': self.system_metrics.total_execution_time_seconds,
                'parallel_execution': self.system_metrics.parallel_execution,
                'total_agents': self.system_metrics.total_agents,
                'successful_agents': self.system_metrics.successful_agents,
                'failed_agents': self.system_metrics.failed_agents,
                'success_rate': self.system_metrics.success_rate,
                'failure_rate': self.system_metrics.failure_rate,
                'throughput_score': self.system_metrics.throughput_score,
                'overall_quality_score': self.system_metrics.overall_quality_score
            },
            'agent_metrics': [
                {
                    'agent_name': agent.agent_name,
                    'agent_role': agent.agent_role,
                    'execution_time_seconds': agent.execution_time_seconds,
                    'success': agent.success,
                    'error_message': agent.error_message,
                    'tools_used': agent.tools_used,
                    'output_quality_score': agent.output_quality_score,
                    'data_completeness_score': agent.data_completeness_score
                }
                for agent in self.agent_metrics
            ],
            'quality_metrics': {
                'biographical_completeness': self.quality_metrics.biographical_completeness,
                'bibliography_coverage': self.quality_metrics.bibliography_coverage,
                'analysis_depth': self.quality_metrics.analysis_depth,
                'citation_quality': self.quality_metrics.citation_quality,
                'narrative_coherence': self.quality_metrics.narrative_coherence,
                'overall_quality': self.quality_metrics.overall_quality
            } if self.quality_metrics else None,
            'recommendations': self.recommendations
        }
    
    def generate_summary(self) -> str:
        """Generate a human-readable performance summary."""
        summary = f"Performance Report: {self.author_name}\n"
        summary += f"Generated: {self.evaluation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        summary += "=== SYSTEM PERFORMANCE ===\n"
        summary += f"Execution Time: {self.system_metrics.total_execution_time_seconds:.2f}s\n"
        summary += f"Success Rate: {self.system_metrics.success_rate:.1%}\n"
        summary += f"Agents: {self.system_metrics.successful_agents}/{self.system_metrics.total_agents} successful\n"
        summary += f"Parallel Execution: {'Yes' if self.system_metrics.parallel_execution else 'No'}\n\n"
        
        summary += "=== AGENT PERFORMANCE ===\n"
        for agent in self.agent_metrics:
            summary += f"• {agent.agent_name} ({agent.agent_role})\n"
            summary += f"  Status: {'✓ Success' if agent.success else '✗ Failed'}\n"
            summary += f"  Time: {agent.execution_time_seconds:.2f}s\n"
            if agent.error_message:
                summary += f"  Error: {agent.error_message}\n"
            summary += f"  Tools: {len(agent.tools_used)} used\n\n"
        
        if self.quality_metrics:
            summary += "=== QUALITY ASSESSMENT ===\n"
            summary += f"Overall Quality: {self.quality_metrics.overall_quality:.1%}\n"
            summary += f"Biographical Completeness: {self.quality_metrics.biographical_completeness:.1%}\n"
            summary += f"Bibliography Coverage: {self.quality_metrics.bibliography_coverage:.1%}\n"
            summary += f"Analysis Depth: {self.quality_metrics.analysis_depth:.1%}\n\n"
        
        if self.recommendations:
            summary += "=== RECOMMENDATIONS ===\n"
            for i, rec in enumerate(self.recommendations, 1):
                summary += f"{i}. {rec}\n"
        
        return summary
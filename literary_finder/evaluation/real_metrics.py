"""Real performance metrics that actually measure meaningful data."""

from dataclasses import dataclass
from typing import Dict, List, Optional, Any
from datetime import datetime
import time
import re
import logging

logger = logging.getLogger(__name__)


@dataclass
class RealAgentMetrics:
    """Actual agent performance metrics based on real execution."""
    agent_name: str
    agent_role: str
    execution_time_seconds: float
    success: bool
    error_message: Optional[str] = None
    output_length: int = 0
    has_structured_data: bool = False
    content_quality_indicators: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.content_quality_indicators is None:
            self.content_quality_indicators = {}


@dataclass 
class RealSystemMetrics:
    """Real system performance based on actual execution."""
    total_execution_time_seconds: float
    parallel_execution: bool
    total_agents: int
    successful_agents: int
    failed_agents: int
    success_rate: float
    has_final_report: bool
    final_report_length: int
    error_count: int
    
    @property
    def failure_rate(self) -> float:
        return 1.0 - self.success_rate if self.success_rate else 1.0


@dataclass
class RealQualityMetrics:
    """Content quality based on actual analysis of generated content."""
    has_biographical_data: bool
    biographical_data_richness: float  # 0-1 based on actual content
    has_bibliography: bool
    bibliography_item_count: int
    has_literary_analysis: bool
    analysis_depth_score: float  # 0-1 based on content length and structure
    final_report_completeness: float  # 0-1 based on section presence
    overall_quality: float
    
    def calculate_overall_quality(self) -> float:
        """Calculate quality based on actual content presence and richness."""
        # Equal weight to major components
        bio_score = 0.3 * (1.0 if self.has_biographical_data else 0.0) + 0.2 * self.biographical_data_richness
        bib_score = 0.25 * (1.0 if self.has_bibliography else 0.0) + 0.1 * min(self.bibliography_item_count / 10.0, 1.0)
        analysis_score = 0.15 * (1.0 if self.has_literary_analysis else 0.0) + 0.1 * self.analysis_depth_score
        
        self.overall_quality = bio_score + bib_score + analysis_score
        return self.overall_quality


@dataclass
class RealPerformanceReport:
    """Performance report based on actual measurements."""
    author_name: str
    evaluation_timestamp: datetime
    system_metrics: RealSystemMetrics
    agent_metrics: List[RealAgentMetrics]
    quality_metrics: Optional[RealQualityMetrics] = None
    recommendations: List[str] = None
    
    def __post_init__(self):
        if self.recommendations is None:
            self.recommendations = []
    
    def generate_summary(self) -> str:
        """Generate human-readable performance summary."""
        summary = f"Performance Report: {self.author_name}\n"
        summary += f"Generated: {self.evaluation_timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        summary += "=== SYSTEM PERFORMANCE ===\n"
        summary += f"Execution Time: {self.system_metrics.total_execution_time_seconds:.2f}s\n"
        summary += f"Success Rate: {self.system_metrics.success_rate:.1%}\n"
        summary += f"Agents: {self.system_metrics.successful_agents}/{self.system_metrics.total_agents} successful\n"
        summary += f"Final Report Generated: {'Yes' if self.system_metrics.has_final_report else 'No'}\n"
        summary += f"Report Length: {self.system_metrics.final_report_length:,} characters\n"
        summary += f"Errors Encountered: {self.system_metrics.error_count}\n\n"
        
        summary += "=== AGENT PERFORMANCE ===\n"
        for agent in self.agent_metrics:
            summary += f"• {agent.agent_name}\n"
            summary += f"  Status: {'✓ Success' if agent.success else '✗ Failed'}\n"
            summary += f"  Time: {agent.execution_time_seconds:.2f}s\n"
            summary += f"  Output: {agent.output_length:,} chars\n"
            summary += f"  Structured Data: {'Yes' if agent.has_structured_data else 'No'}\n"
            if agent.error_message:
                summary += f"  Error: {agent.error_message[:100]}...\n"
            summary += "\n"
        
        if self.quality_metrics:
            summary += "=== CONTENT QUALITY ===\n"
            summary += f"Overall Quality: {self.quality_metrics.overall_quality:.1%}\n"
            summary += f"Has Biographical Data: {'Yes' if self.quality_metrics.has_biographical_data else 'No'}\n"
            summary += f"Has Bibliography: {'Yes' if self.quality_metrics.has_bibliography else 'No'} ({self.quality_metrics.bibliography_item_count} items)\n"
            summary += f"Has Literary Analysis: {'Yes' if self.quality_metrics.has_literary_analysis else 'No'}\n"
            summary += f"Report Completeness: {self.quality_metrics.final_report_completeness:.1%}\n\n"
        
        if self.recommendations:
            summary += "=== RECOMMENDATIONS ===\n"
            for i, rec in enumerate(self.recommendations[:3], 1):  # Top 3 recommendations
                summary += f"{i}. {rec}\n"
        
        return summary


class RealPerformanceEvaluator:
    """Performance evaluator that measures actual execution and content quality."""
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.agent_timings: Dict[str, Dict[str, float]] = {}
        
    def start_evaluation(self) -> None:
        """Start overall system evaluation."""
        self.start_time = time.time()
        logger.info("Real performance evaluation started")
    
    def start_agent_timing(self, agent_name: str) -> None:
        """Start timing for specific agent."""
        if agent_name not in self.agent_timings:
            self.agent_timings[agent_name] = {}
        self.agent_timings[agent_name]['start'] = time.time()
    
    def end_agent_timing(self, agent_name: str) -> None:
        """End timing for specific agent."""
        if agent_name in self.agent_timings:
            self.agent_timings[agent_name]['end'] = time.time()
    
    def evaluate_system_performance(self, result: Dict[str, Any], parallel_execution: bool = True) -> RealPerformanceReport:
        """Evaluate actual system performance based on real results."""
        if self.start_time is None:
            logger.warning("Evaluation timing not started properly")
            total_time = 0.0
        else:
            total_time = time.time() - self.start_time
        
        # Analyze actual results structure
        agent_statuses = result.get('agent_statuses', {})
        results_data = result.get('results', {})
        errors = result.get('errors', [])
        final_report = result.get('final_report', '')
        
        # Calculate real system metrics
        total_agents = len(agent_statuses) if agent_statuses else 3  # Default expectation
        successful_agents = 0
        
        # Count actual successes based on presence of data
        for agent_name in ['contextual_historian', 'literary_cartographer', 'legacy_connector']:
            agent_data = results_data.get(agent_name) if results_data else None
            if agent_data is not None:
                successful_agents += 1
        
        success_rate = successful_agents / total_agents if total_agents > 0 else 0.0
        
        system_metrics = RealSystemMetrics(
            total_execution_time_seconds=total_time,
            parallel_execution=parallel_execution,
            total_agents=total_agents,
            successful_agents=successful_agents,
            failed_agents=total_agents - successful_agents,
            success_rate=success_rate,
            has_final_report=bool(final_report and len(final_report) > 100),
            final_report_length=len(final_report) if final_report else 0,
            error_count=len(errors)
        )
        
        # Evaluate individual agents based on actual output
        agent_metrics = self._evaluate_real_agents(results_data, errors)
        
        # Evaluate content quality based on actual generated content
        quality_metrics = self._evaluate_real_content_quality(results_data, final_report)
        
        # Generate realistic recommendations
        recommendations = self._generate_real_recommendations(system_metrics, agent_metrics, quality_metrics)
        
        report = RealPerformanceReport(
            author_name=result.get('author_name', 'Unknown'),
            evaluation_timestamp=datetime.now(),
            system_metrics=system_metrics,
            agent_metrics=agent_metrics,
            quality_metrics=quality_metrics,
            recommendations=recommendations
        )
        
        logger.info(f"Real performance evaluation completed - Success rate: {success_rate:.1%}")
        return report
    
    def _evaluate_real_agents(self, results_data: Dict[str, Any], errors: List[str]) -> List[RealAgentMetrics]:
        """Evaluate agents based on actual output data."""
        agent_metrics = []
        
        agent_roles = {
            'contextual_historian': 'Biographical Research Specialist',
            'literary_cartographer': 'Bibliography Compilation Expert',
            'legacy_connector': 'Literary Analysis Specialist'
        }
        
        for agent_name, role in agent_roles.items():
            # Get actual timing if available
            execution_time = 0.0
            if agent_name in self.agent_timings:
                timing = self.agent_timings[agent_name]
                if 'start' in timing and 'end' in timing:
                    execution_time = timing['end'] - timing['start']
            
            # Check if agent produced actual output
            agent_data = results_data.get(agent_name) if results_data else None
            success = agent_data is not None
            
            # Analyze output content
            output_length = 0
            has_structured_data = False
            content_indicators = {}
            
            if agent_data:
                # Try to measure actual content
                if hasattr(agent_data, '__dict__'):
                    # Structured object
                    has_structured_data = True
                    non_none_attrs = [attr for attr in dir(agent_data) 
                                    if not attr.startswith('_') and getattr(agent_data, attr) is not None]
                    content_indicators['structured_attributes'] = len(non_none_attrs)
                    
                    # Estimate content richness
                    text_content = ""
                    for attr in non_none_attrs:
                        value = getattr(agent_data, attr)
                        if isinstance(value, str):
                            text_content += value
                    output_length = len(text_content)
                elif isinstance(agent_data, str):
                    output_length = len(agent_data)
                else:
                    output_length = len(str(agent_data))
            
            # Find relevant errors
            error_message = None
            agent_errors = [err for err in errors if agent_name.lower() in err.lower()]
            if agent_errors:
                error_message = agent_errors[0]
            elif not success:
                error_message = f"No output data generated for {agent_name}"
            
            agent_metric = RealAgentMetrics(
                agent_name=agent_name,
                agent_role=role,
                execution_time_seconds=execution_time,
                success=success,
                error_message=error_message,
                output_length=output_length,
                has_structured_data=has_structured_data,
                content_quality_indicators=content_indicators
            )
            
            agent_metrics.append(agent_metric)
        
        return agent_metrics
    
    def _evaluate_real_content_quality(self, results_data: Dict[str, Any], final_report: str) -> RealQualityMetrics:
        """Evaluate quality based on actual content analysis."""
        
        # Analyze biographical data
        historian_data = results_data.get('contextual_historian')
        has_biographical_data = historian_data is not None
        biographical_richness = 0.0
        
        if historian_data:
            # Check for actual biographical indicators
            bio_indicators = 0
            if hasattr(historian_data, 'birth_year') and historian_data.birth_year:
                bio_indicators += 1
            if hasattr(historian_data, 'death_year') and historian_data.death_year:
                bio_indicators += 1
            if hasattr(historian_data, 'nationality') and historian_data.nationality:
                bio_indicators += 1
            if hasattr(historian_data, 'biographical_summary') and historian_data.biographical_summary:
                # Score based on content length and richness
                summary_length = len(historian_data.biographical_summary)
                bio_indicators += min(summary_length / 500.0, 2.0)  # Up to 2 points for rich content
            
            biographical_richness = min(bio_indicators / 5.0, 1.0)  # Normalize to 0-1
        
        # Analyze bibliography data
        cartographer_data = results_data.get('literary_cartographer')
        has_bibliography = cartographer_data is not None
        bibliography_count = 0
        
        if cartographer_data:
            # Count actual bibliography items
            if hasattr(cartographer_data, 'chronological') and cartographer_data.chronological:
                bibliography_count += len(cartographer_data.chronological)
            if hasattr(cartographer_data, 'start_here') and cartographer_data.start_here:
                bibliography_count += len(cartographer_data.start_here)
        
        # Analyze literary analysis
        legacy_data = results_data.get('legacy_connector')
        has_literary_analysis = legacy_data is not None
        analysis_depth = 0.0
        
        if legacy_data:
            depth_indicators = 0
            if hasattr(legacy_data, 'stylistic_innovations') and legacy_data.stylistic_innovations:
                depth_indicators += len(legacy_data.stylistic_innovations) / 3.0  # Normalize
            if hasattr(legacy_data, 'recurring_themes') and legacy_data.recurring_themes:
                depth_indicators += len(legacy_data.recurring_themes) / 3.0  # Normalize
            if hasattr(legacy_data, 'literary_significance') and legacy_data.literary_significance:
                depth_indicators += min(len(legacy_data.literary_significance) / 200.0, 1.0)
            
            analysis_depth = min(depth_indicators / 3.0, 1.0)
        
        # Analyze final report completeness
        report_completeness = 0.0
        if final_report:
            required_sections = [
                "# The Literary Finder:",
                "## 📚 Author Biography",
                "## 📖 Reading Map",
                "## 🎯 Literary Legacy"
            ]
            present_sections = sum(1 for section in required_sections if section in final_report)
            report_completeness = present_sections / len(required_sections)
        
        quality_metrics = RealQualityMetrics(
            has_biographical_data=has_biographical_data,
            biographical_data_richness=biographical_richness,
            has_bibliography=has_bibliography,
            bibliography_item_count=bibliography_count,
            has_literary_analysis=has_literary_analysis,
            analysis_depth_score=analysis_depth,
            final_report_completeness=report_completeness,
            overall_quality=0.0  # Will be calculated
        )
        
        quality_metrics.calculate_overall_quality()
        return quality_metrics
    
    def _generate_real_recommendations(
        self, 
        system_metrics: RealSystemMetrics,
        agent_metrics: List[RealAgentMetrics],
        quality_metrics: RealQualityMetrics
    ) -> List[str]:
        """Generate actionable recommendations based on real performance data."""
        recommendations = []
        
        # System-level recommendations
        if system_metrics.success_rate < 0.8:
            failed_agents = [agent.agent_name for agent in agent_metrics if not agent.success]
            recommendations.append(
                f"Only {system_metrics.success_rate:.0%} of agents succeeded. "
                f"Failed agents: {', '.join(failed_agents)}. Check API keys and network connectivity."
            )
        
        if not system_metrics.has_final_report:
            recommendations.append(
                "No final report was generated. Check report synthesis logic and agent outputs."
            )
        elif system_metrics.final_report_length < 1000:
            recommendations.append(
                f"Final report is very short ({system_metrics.final_report_length} chars). "
                "Agents may not be producing sufficient content."
            )
        
        if system_metrics.total_execution_time_seconds > 120:
            recommendations.append(
                f"Execution took {system_metrics.total_execution_time_seconds:.0f}s. "
                "Consider optimizing API calls or implementing caching."
            )
        
        # Agent-specific recommendations
        slow_agents = [agent for agent in agent_metrics if agent.execution_time_seconds > 60]
        if slow_agents:
            agent_names = [agent.agent_name for agent in slow_agents]
            recommendations.append(
                f"Slow agents detected: {', '.join(agent_names)}. "
                "Review search queries and API response times."
            )
        
        empty_output_agents = [agent for agent in agent_metrics if agent.success and agent.output_length == 0]
        if empty_output_agents:
            agent_names = [agent.agent_name for agent in empty_output_agents]
            recommendations.append(
                f"Agents producing no content: {', '.join(agent_names)}. "
                "Check data processing and extraction logic."
            )
        
        # Quality-based recommendations
        if quality_metrics:
            if not quality_metrics.has_biographical_data:
                recommendations.append(
                    "No biographical data found. Check Contextual Historian agent and search APIs."
                )
            elif quality_metrics.biographical_data_richness < 0.5:
                recommendations.append(
                    "Biographical data is sparse. Improve search queries for life details and context."
                )
            
            if not quality_metrics.has_bibliography:
                recommendations.append(
                    "No bibliography generated. Check Literary Cartographer and Google Books API."
                )
            elif quality_metrics.bibliography_item_count < 3:
                recommendations.append(
                    f"Only {quality_metrics.bibliography_item_count} bibliography items found. "
                    "Expand search criteria for more comprehensive book discovery."
                )
            
            if not quality_metrics.has_literary_analysis:
                recommendations.append(
                    "No literary analysis generated. Check Legacy Connector agent functionality."
                )
            elif quality_metrics.analysis_depth_score < 0.5:
                recommendations.append(
                    "Literary analysis lacks depth. Enhance search for criticism and thematic content."
                )
        
        # Positive feedback
        if not recommendations:
            if system_metrics.success_rate >= 0.8 and quality_metrics and quality_metrics.overall_quality >= 0.7:
                recommendations.append(
                    "System performance is good. All agents succeeded and content quality is satisfactory."
                )
            else:
                recommendations.append(
                    "System executed successfully but content quality could be improved."
                )
        
        return recommendations[:5]  # Limit to top 5 recommendations
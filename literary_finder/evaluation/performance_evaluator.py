"""Performance evaluation system for the Literary Finder multi-agent system."""

import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional
from .metrics import (
    AgentMetrics, 
    SystemMetrics, 
    QualityMetrics, 
    PerformanceReport
)

logger = logging.getLogger(__name__)


class PerformanceEvaluator:
    """
    Comprehensive performance evaluation system for the Literary Finder.
    
    Evaluates:
    - System-level performance (execution time, success rates, throughput)
    - Agent-level performance (individual agent success, timing, quality)
    - Content quality (completeness, accuracy, coherence)
    - Recommendations for optimization
    """
    
    def __init__(self):
        self.start_time: Optional[float] = None
        self.agent_start_times: Dict[str, float] = {}
        self.agent_end_times: Dict[str, float] = {}
        
    def start_evaluation(self) -> None:
        """Start overall system evaluation timing."""
        self.start_time = time.time()
        logger.info("Performance evaluation started")
    
    def start_agent_evaluation(self, agent_name: str) -> None:
        """Start timing for a specific agent."""
        self.agent_start_times[agent_name] = time.time()
        logger.debug(f"Started evaluation for agent: {agent_name}")
    
    def end_agent_evaluation(self, agent_name: str) -> None:
        """End timing for a specific agent."""
        self.agent_end_times[agent_name] = time.time()
        logger.debug(f"Ended evaluation for agent: {agent_name}")
    
    def evaluate_system_performance(
        self, 
        result: Dict[str, Any],
        parallel_execution: bool = True
    ) -> PerformanceReport:
        """
        Evaluate overall system performance and generate comprehensive report.
        
        Args:
            result: The complete system output from LiteraryFinderGraph
            parallel_execution: Whether agents ran in parallel
            
        Returns:
            PerformanceReport with comprehensive metrics and recommendations
        """
        if self.start_time is None:
            logger.warning("Evaluation not properly started - using current time")
            self.start_time = time.time()
        
        end_time = time.time()
        total_execution_time = end_time - self.start_time
        
        # Extract agent statuses from result
        agent_statuses = result.get('agent_statuses', {})
        
        # Calculate system metrics
        total_agents = len(agent_statuses)
        successful_agents = sum(1 for status in agent_statuses.values() 
                               if str(status).lower() == 'completed')
        failed_agents = total_agents - successful_agents
        success_rate = successful_agents / total_agents if total_agents > 0 else 0.0
        
        # Calculate throughput score (agents per second, normalized)
        throughput_score = (successful_agents / total_execution_time 
                           if total_execution_time > 0 else 0.0)
        
        system_metrics = SystemMetrics(
            total_execution_time_seconds=total_execution_time,
            parallel_execution=parallel_execution,
            total_agents=total_agents,
            successful_agents=successful_agents,
            failed_agents=failed_agents,
            success_rate=success_rate,
            throughput_score=throughput_score
        )
        
        # Evaluate individual agents
        agent_metrics = self._evaluate_agents(result, agent_statuses)
        
        # Evaluate content quality
        quality_metrics = self._evaluate_content_quality(result)
        
        # Update system metrics with quality score
        system_metrics.overall_quality_score = quality_metrics.overall_quality if quality_metrics else None
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            system_metrics, agent_metrics, quality_metrics
        )
        
        # Create comprehensive report
        report = PerformanceReport(
            author_name=result.get('author_name', 'Unknown'),
            evaluation_timestamp=datetime.now(),
            system_metrics=system_metrics,
            agent_metrics=agent_metrics,
            quality_metrics=quality_metrics,
            recommendations=recommendations
        )
        
        logger.info(f"Performance evaluation completed - Success rate: {success_rate:.1%}")
        return report
    
    def _evaluate_agents(
        self, 
        result: Dict[str, Any], 
        agent_statuses: Dict[str, Any]
    ) -> List[AgentMetrics]:
        """Evaluate individual agent performance."""
        agent_metrics = []
        
        agent_roles = {
            'contextual_historian': 'Biographical and Historical Research Specialist',
            'literary_cartographer': 'Bibliography Compilation and Reading Map Expert',
            'legacy_connector': 'Literary Analysis and Critical Assessment Specialist'
        }
        
        for agent_name, status in agent_statuses.items():
            # Calculate execution time
            execution_time = 0.0
            if (agent_name in self.agent_start_times and 
                agent_name in self.agent_end_times):
                execution_time = (self.agent_end_times[agent_name] - 
                                self.agent_start_times[agent_name])
            
            # Determine success and error
            success = str(status).lower() == 'completed'
            error_message = None
            if not success:
                errors = result.get('errors', [])
                agent_errors = [err for err in errors if agent_name.lower() in err.lower()]
                error_message = agent_errors[0] if agent_errors else f"Agent {agent_name} failed"
            
            # Evaluate output quality
            output_quality_score = self._evaluate_agent_output_quality(
                result, agent_name
            )
            
            # Evaluate data completeness
            data_completeness_score = self._evaluate_agent_data_completeness(
                result, agent_name
            )
            
            agent_metric = AgentMetrics(
                agent_name=agent_name,
                agent_role=agent_roles.get(agent_name, 'Unknown Role'),
                execution_time_seconds=execution_time,
                success=success,
                error_message=error_message,
                tools_used=self._get_agent_tools_used(agent_name),
                output_quality_score=output_quality_score,
                data_completeness_score=data_completeness_score
            )
            
            agent_metrics.append(agent_metric)
        
        return agent_metrics
    
    def _evaluate_content_quality(self, result: Dict[str, Any]) -> Optional[QualityMetrics]:
        """Evaluate the quality of generated content."""
        try:
            results_data = result.get('results', {})
            
            # Evaluate biographical completeness
            biographical_completeness = self._evaluate_biographical_completeness(
                results_data.get('contextual_historian')
            )
            
            # Evaluate bibliography coverage  
            bibliography_coverage = self._evaluate_bibliography_coverage(
                results_data.get('literary_cartographer')
            )
            
            # Evaluate analysis depth
            analysis_depth = self._evaluate_analysis_depth(
                results_data.get('legacy_connector')
            )
            
            # Evaluate citation quality
            citation_quality = self._evaluate_citation_quality(result)
            
            # Evaluate narrative coherence
            narrative_coherence = self._evaluate_narrative_coherence(
                result.get('final_report', '')
            )
            
            quality_metrics = QualityMetrics(
                biographical_completeness=biographical_completeness,
                bibliography_coverage=bibliography_coverage,
                analysis_depth=analysis_depth,
                citation_quality=citation_quality,
                narrative_coherence=narrative_coherence,
                overall_quality=0.0  # Will be calculated
            )
            
            # Calculate overall quality
            quality_metrics.calculate_overall_quality()
            
            return quality_metrics
            
        except Exception as e:
            logger.error(f"Error evaluating content quality: {e}")
            return None
    
    def _evaluate_biographical_completeness(self, historian_data: Any) -> float:
        """Evaluate completeness of biographical information."""
        if not historian_data:
            return 0.0
        
        score = 0.0
        total_criteria = 5
        
        # Check for basic biographical facts
        if hasattr(historian_data, 'birth_year') and historian_data.birth_year:
            score += 0.2
        if hasattr(historian_data, 'death_year') and historian_data.death_year:
            score += 0.2
        if hasattr(historian_data, 'nationality') and historian_data.nationality:
            score += 0.2
        if (hasattr(historian_data, 'biographical_summary') and 
            historian_data.biographical_summary and 
            len(historian_data.biographical_summary) > 100):
            score += 0.4
        
        return min(score, 1.0)
    
    def _evaluate_bibliography_coverage(self, cartographer_data: Any) -> float:
        """Evaluate comprehensiveness of bibliography."""
        if not cartographer_data:
            return 0.0
        
        score = 0.0
        
        # Check for chronological works
        if (hasattr(cartographer_data, 'chronological') and 
            cartographer_data.chronological and 
            len(cartographer_data.chronological) >= 3):
            score += 0.4
        
        # Check for starter recommendations
        if (hasattr(cartographer_data, 'start_here') and 
            cartographer_data.start_here and 
            len(cartographer_data.start_here) >= 2):
            score += 0.3
        
        # Check for thematic groups
        if (hasattr(cartographer_data, 'thematic_groups') and 
            cartographer_data.thematic_groups and 
            len(cartographer_data.thematic_groups) >= 1):
            score += 0.3
        
        return min(score, 1.0)
    
    def _evaluate_analysis_depth(self, legacy_data: Any) -> float:
        """Evaluate depth of literary analysis."""
        if not legacy_data:
            return 0.0
        
        score = 0.0
        
        # Check for stylistic innovations
        if (hasattr(legacy_data, 'stylistic_innovations') and 
            legacy_data.stylistic_innovations and 
            len(legacy_data.stylistic_innovations) >= 2):
            score += 0.4
        
        # Check for recurring themes
        if (hasattr(legacy_data, 'recurring_themes') and 
            legacy_data.recurring_themes and 
            len(legacy_data.recurring_themes) >= 2):
            score += 0.4
        
        # Check for literary significance
        if (hasattr(legacy_data, 'literary_significance') and 
            legacy_data.literary_significance and 
            len(legacy_data.literary_significance) > 100):
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_citation_quality(self, result: Dict[str, Any]) -> float:
        """Evaluate quality of sources and citations."""
        # Simple heuristic based on presence of final report and lack of errors
        final_report = result.get('final_report', '')
        errors = result.get('errors', [])
        
        if not final_report:
            return 0.0
        
        score = 0.8  # Base score for having a report
        
        # Penalize for errors
        error_penalty = min(len(errors) * 0.1, 0.5)
        score -= error_penalty
        
        # Check for Google Books links (indicator of source quality)
        if 'google.com/books' in final_report:
            score += 0.2
        
        return max(min(score, 1.0), 0.0)
    
    def _evaluate_narrative_coherence(self, final_report: str) -> float:
        """Evaluate coherence and structure of final narrative."""
        if not final_report:
            return 0.0
        
        score = 0.0
        
        # Check for basic structure elements
        if '# The Literary Finder:' in final_report:
            score += 0.2
        if '## 📚 Author Biography' in final_report:
            score += 0.2
        if '## 📖 Reading Map' in final_report:
            score += 0.2
        if '## 🎯 Literary Legacy' in final_report:
            score += 0.2
        
        # Check for minimum content length
        if len(final_report) > 1000:
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_agent_output_quality(self, result: Dict[str, Any], agent_name: str) -> Optional[float]:
        """Evaluate the quality of a specific agent's output."""
        results_data = result.get('results', {})
        agent_data = results_data.get(agent_name)
        
        if not agent_data:
            return 0.0
        
        # Agent-specific quality evaluation
        if agent_name == 'contextual_historian':
            return self._evaluate_biographical_completeness(agent_data)
        elif agent_name == 'literary_cartographer':
            return self._evaluate_bibliography_coverage(agent_data)
        elif agent_name == 'legacy_connector':
            return self._evaluate_analysis_depth(agent_data)
        
        return 0.5  # Default score for unknown agents
    
    def _evaluate_agent_data_completeness(self, result: Dict[str, Any], agent_name: str) -> Optional[float]:
        """Evaluate completeness of agent data."""
        results_data = result.get('results', {})
        agent_data = results_data.get(agent_name)
        
        if not agent_data:
            return 0.0
        
        # Simple completeness check based on presence of key attributes
        if hasattr(agent_data, '__dict__'):
            attributes = [attr for attr in dir(agent_data) 
                         if not attr.startswith('_') and getattr(agent_data, attr) is not None]
            # Normalize to 0-1 scale, assuming 5+ attributes indicates good completeness
            return min(len(attributes) / 5.0, 1.0)
        
        return 0.5  # Default for non-object data
    
    def _get_agent_tools_used(self, agent_name: str) -> List[str]:
        """Get list of tools used by an agent (placeholder implementation)."""
        # This would ideally track actual tool usage during execution
        tool_mappings = {
            'contextual_historian': ['search_author_biography', 'search_historical_context', 'search_literary_influences'],
            'literary_cartographer': ['search_author_books', 'analyze_book_chronology', 'categorize_works'],
            'legacy_connector': ['search_literary_criticism', 'search_themes_and_style']
        }
        return tool_mappings.get(agent_name, [])
    
    def _generate_recommendations(
        self, 
        system_metrics: SystemMetrics,
        agent_metrics: List[AgentMetrics],
        quality_metrics: Optional[QualityMetrics]
    ) -> List[str]:
        """Generate performance optimization recommendations."""
        recommendations = []
        
        # System-level recommendations
        if system_metrics.success_rate < 0.8:
            recommendations.append(
                f"System success rate is {system_metrics.success_rate:.1%}. "
                "Consider improving error handling and retry mechanisms."
            )
        
        if system_metrics.total_execution_time_seconds > 60:
            recommendations.append(
                f"Execution time is {system_metrics.total_execution_time_seconds:.1f}s. "
                "Consider optimizing API calls or implementing caching."
            )
        
        # Agent-level recommendations
        failed_agents = [agent for agent in agent_metrics if not agent.success]
        if failed_agents:
            agent_names = [agent.agent_name for agent in failed_agents]
            recommendations.append(
                f"Agents {', '.join(agent_names)} failed. "
                "Review error logs and improve error recovery."
            )
        
        slow_agents = [agent for agent in agent_metrics 
                      if agent.execution_time_seconds > 30]
        if slow_agents:
            agent_names = [agent.agent_name for agent in slow_agents]
            recommendations.append(
                f"Agents {', '.join(agent_names)} are slow. "
                "Consider optimizing search queries and API usage."
            )
        
        # Quality-based recommendations
        if quality_metrics:
            if quality_metrics.biographical_completeness < 0.7:
                recommendations.append(
                    "Biographical data is incomplete. Enhance search strategies for "
                    "birth/death dates, nationality, and biographical details."
                )
            
            if quality_metrics.bibliography_coverage < 0.7:
                recommendations.append(
                    "Bibliography coverage is limited. Improve Google Books API "
                    "queries and result processing."
                )
            
            if quality_metrics.analysis_depth < 0.7:
                recommendations.append(
                    "Literary analysis lacks depth. Enhance search for academic "
                    "criticism and thematic analysis."
                )
        
        # Default recommendation if everything looks good
        if not recommendations:
            recommendations.append(
                "System performance is optimal. Continue monitoring for consistency."
            )
        
        return recommendations
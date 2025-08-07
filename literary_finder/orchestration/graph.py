"""LangGraph orchestration for the Literary Finder system."""

from typing import Dict, Any, List, Optional
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langsmith import traceable
from ..models import LiteraryFinderState, AgentStatus
from ..agents import ContextualHistorian, LiteraryCartographer, LegacyConnector
from ..evaluation import PerformanceEvaluator, PerformanceReport
from ..config import LangSmithConfig
import logging
from datetime import datetime
import asyncio

logger = logging.getLogger(__name__)


class LiteraryFinderGraph:
    """LangGraph orchestration for the Literary Finder system."""

    def __init__(
            self,
            model_name: str = None,
            enable_parallel: bool = True,
            enable_evaluation: bool = True
    ):
        self.model_name = model_name
        self.enable_parallel = enable_parallel
        self.enable_evaluation = enable_evaluation
        
        # Setup LangSmith tracing if not already configured
        if not LangSmithConfig.is_enabled():
            LangSmithConfig.setup_tracing()

        # Initialize performance evaluator
        self.evaluator = PerformanceEvaluator() if enable_evaluation else None

        # Initialize agents with OpenAI only
        self.historian = ContextualHistorian(
            model_name=model_name
        )
        # self.book_recommender removed
        self.cartographer = LiteraryCartographer(
            model_name=model_name
        )
        self.legacy_connector = LegacyConnector(
            model_name=model_name
        )

        # Build graph
        self.graph = self._build_graph()

        logger.info("Literary Finder Graph initialized")

    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""

        workflow = StateGraph(LiteraryFinderState)

        workflow.add_node("start", self._start_processing)

        if self.enable_parallel:
            workflow.add_node("run_agents_parallel", self._run_agents_parallel)
            workflow.add_edge("start", "run_agents_parallel")
            workflow.add_edge("run_agents_parallel", "synthesize_report")
        else:
            workflow.add_node("contextual_historian", self._run_historian)
            workflow.add_node("literary_cartographer", self._run_cartographer)
            workflow.add_node("legacy_connector", self._run_legacy_connector)

            workflow.add_edge("start", "contextual_historian")
            workflow.add_edge("contextual_historian", "literary_cartographer")
            workflow.add_edge("literary_cartographer", "legacy_connector")
            workflow.add_edge("legacy_connector", "synthesize_report")

        workflow.add_node("synthesize_report", self._synthesize_final_report)
        workflow.add_edge("synthesize_report", END)

        workflow.set_entry_point("start")

        return workflow.compile(checkpointer=MemorySaver())

    def _start_processing(self, state: LiteraryFinderState) -> Dict[str, Any]:
        """Initialize processing."""
        logger.info(f"Starting Literary Finder processing for: {state.author_name}")

        return {
            "processing_started_at": datetime.now().isoformat(),
            "agent_statuses": {
                "contextual_historian": AgentStatus.PENDING,
                "literary_cartographer": AgentStatus.PENDING,
                "legacy_connector": AgentStatus.PENDING
            }
        }

    def _run_agents_parallel(self, state: LiteraryFinderState) -> Dict[str, Any]:
        """Run all agents in parallel."""
        logger.info("Running agents in parallel")

        results = {}

        try:
            # Start evaluation timing for each agent
            if self.evaluator:
                self.evaluator.start_agent_timing("contextual_historian")
            
            logger.info("Starting Contextual Historian")
            historian_result = self.historian.process(state.author_name)
            
            if self.evaluator:
                self.evaluator.end_agent_timing("contextual_historian")
            
            if historian_result["success"]:
                results["contextual_historian"] = historian_result["data"]
                logger.info("Contextual Historian completed successfully")
            else:
                logger.error(f"Contextual Historian failed: {historian_result.get('error')}")
                results["errors"] = state.errors + [f"Historian: {historian_result.get('error')}"]

            if self.evaluator:
                self.evaluator.start_agent_timing("literary_cartographer")
            
            logger.info("Starting Literary Cartographer")
            cartographer_result = self.cartographer.process(state.author_name)
            
            if self.evaluator:
                self.evaluator.end_agent_timing("literary_cartographer")
                
            if cartographer_result["success"]:
                results["literary_cartographer"] = cartographer_result["data"]
                logger.info("Literary Cartographer completed successfully")
            else:
                logger.error(f"Literary Cartographer failed: {cartographer_result.get('error')}")
                results["errors"] = results.get("errors", state.errors) + [
                    f"Cartographer: {cartographer_result.get('error')}"]

            if self.evaluator:
                self.evaluator.start_agent_timing("legacy_connector")
                
            logger.info("Starting Legacy Connector")
            legacy_result = self.legacy_connector.process(state.author_name)
            
            if self.evaluator:
                self.evaluator.end_agent_timing("legacy_connector")
                
            if legacy_result["success"]:
                results["legacy_connector"] = legacy_result["data"]
                logger.info("Legacy Connector completed successfully")
            else:
                logger.error(f"Legacy Connector failed: {legacy_result.get('error')}")
                results["errors"] = results.get("errors", state.errors) + [f"Legacy: {legacy_result.get('error')}"]

            agent_statuses = {}
            for agent_name in ["contextual_historian", "literary_cartographer", "legacy_connector"]:
                if agent_name in results:
                    agent_statuses[agent_name] = AgentStatus.COMPLETED
                else:
                    agent_statuses[agent_name] = AgentStatus.FAILED

            return {
                "results": {
                    "contextual_historian": results.get("contextual_historian"),
                    "literary_cartographer": results.get("literary_cartographer"),
                    "legacy_connector": results.get("legacy_connector")
                },
                "agent_statuses": agent_statuses,
                "errors": results.get("errors", state.errors)
            }

        except Exception as e:
            logger.error(f"Error in parallel agent execution: {e}")
            return {
                "errors": state.errors + [f"Parallel execution error: {str(e)}"],
                "agent_statuses": {
                    "contextual_historian": AgentStatus.FAILED,
                    "literary_cartographer": AgentStatus.FAILED,
                    "legacy_connector": AgentStatus.FAILED
                }
            }

    def _run_historian(self, state: LiteraryFinderState) -> Dict[str, Any]:
        """Run the Contextual Historian agent."""
        logger.info("Running Contextual Historian")

        try:
            result = self.historian.process(state.author_name)

            if result["success"]:
                return {
                    "results": {
                        **state.results.model_dump(),
                        "contextual_historian": result["data"]
                    },
                    "agent_statuses": {
                        **state.agent_statuses,
                        "contextual_historian": AgentStatus.COMPLETED
                    }
                }
            else:
                return {
                    "agent_statuses": {
                        **state.agent_statuses,
                        "contextual_historian": AgentStatus.FAILED
                    },
                    "errors": state.errors + [f"Historian: {result.get('error')}"]
                }

        except Exception as e:
            logger.error(f"Error in historian: {e}")
            return {
                "agent_statuses": {
                    **state.agent_statuses,
                    "contextual_historian": AgentStatus.FAILED
                },
                "errors": state.errors + [f"Historian error: {str(e)}"]
            }

    def _run_cartographer(self, state: LiteraryFinderState) -> Dict[str, Any]:
        """Run the Literary Cartographer agent."""
        logger.info("Running Literary Cartographer")

        try:
            context = {}
            if state.results.contextual_historian:
                context["author_context"] = state.results.contextual_historian

            result = self.cartographer.process(state.author_name, context)

            if result["success"]:
                return {
                    "results": {
                        **state.results.model_dump(),
                        "literary_cartographer": result["data"]
                    },
                    "agent_statuses": {
                        **state.agent_statuses,
                        "literary_cartographer": AgentStatus.COMPLETED
                    }
                }
            else:
                return {
                    "agent_statuses": {
                        **state.agent_statuses,
                        "literary_cartographer": AgentStatus.FAILED
                    },
                    "errors": state.errors + [f"Cartographer: {result.get('error')}"]
                }

        except Exception as e:
            logger.error(f"Error in cartographer: {e}")
            return {
                "agent_statuses": {
                    **state.agent_statuses,
                    "literary_cartographer": AgentStatus.FAILED
                },
                "errors": state.errors + [f"Cartographer error: {str(e)}"]
            }

    def _run_legacy_connector(self, state: LiteraryFinderState) -> Dict[str, Any]:
        """Run the Legacy Connector agent."""
        logger.info("Running Legacy Connector")

        try:
            context = {}
            if state.results.contextual_historian:
                context["author_context"] = state.results.contextual_historian
            if state.results.literary_cartographer:
                context["reading_map"] = state.results.literary_cartographer

            result = self.legacy_connector.process(state.author_name, context)

            if result["success"]:
                return {
                    "results": {
                        **state.results.model_dump(),
                        "legacy_connector": result["data"]
                    },
                    "agent_statuses": {
                        **state.agent_statuses,
                        "legacy_connector": AgentStatus.COMPLETED
                    }
                }
            else:
                return {
                    "agent_statuses": {
                        **state.agent_statuses,
                        "legacy_connector": AgentStatus.FAILED
                    },
                    "errors": state.errors + [f"Legacy: {result.get('error')}"]
                }

        except Exception as e:
            logger.error(f"Error in legacy connector: {e}")
            return {
                "agent_statuses": {
                    **state.agent_statuses,
                    "legacy_connector": AgentStatus.FAILED
                },
                "errors": state.errors + [f"Legacy error: {str(e)}"]
            }

    def _synthesize_final_report(self, state: LiteraryFinderState) -> Dict[str, Any]:
        """Synthesize the final report from all agent results."""
        logger.info("Synthesizing final report")

        try:
            report = self._generate_markdown_report(
                author_name=state.author_name,
                context=state.results.contextual_historian,
                # book_recommendations removed,
                reading_map=state.results.literary_cartographer,
                legacy=state.results.legacy_connector
            )

            return {
                "final_report": report,
                "processing_completed_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error synthesizing report: {e}")
            return {
                "errors": state.errors + [f"Report synthesis error: {str(e)}"],
                "processing_completed_at": datetime.now().isoformat()
            }

    def _generate_markdown_report(
            self,
            author_name: str,
            context=None,
            book_recommendations=None,
            reading_map=None,
            legacy=None
    ) -> str:
        """Generate the final Markdown report."""

        report = f"# The Literary Finder: {author_name}\n\n"
        report += "_A comprehensive guide to the author's life, works, and literary legacy_\n\n"
        report += "---\n\n"

        # Biographical Context
        if context:
            report += "## 📚 Author Biography & Historical Context\n\n"
            if context.biographical_summary:
                report += f"{context.biographical_summary}\n\n"

            if context.birth_year or context.death_year:
                years = ""
                if context.birth_year:
                    years += str(context.birth_year)
                if context.death_year:
                    years += f" - {context.death_year}"
                if years:
                    report += f"**Years:** {years}\n\n"

            if context.nationality:
                report += f"**Nationality:** {context.nationality}\n\n"

        if reading_map:
            report += "## 📖 Reading Map & Bibliography\n\n"

            # Start Here
            if reading_map.start_here:
                report += "### 🌟 Start Here\n"
                report += "_Essential works for new readers_\n\n"
                for entry in reading_map.start_here:
                    report += f"- **{entry.title}**"
                    if entry.year:
                        report += f" ({entry.year})"
                    if entry.google_books_link:
                        report += f" - [📖 View on Google Books]({entry.google_books_link})"
                    if entry.preview_link:
                        report += f" - [🔍 Preview]({entry.preview_link})"
                    if entry.description:
                        report += f"\n  - {entry.description}"
                    report += "\n\n"

            # Chronological
            if reading_map.chronological:
                report += "### 📅 Chronological Bibliography\n"
                report += "_Complete works in order of publication_\n\n"
                for entry in reading_map.chronological[:15]:  # Limit for readability
                    report += f"- **{entry.title}**"
                    if entry.year:
                        report += f" ({entry.year})"
                    if entry.google_books_link:
                        report += f" - [📖 Link]({entry.google_books_link})"
                    report += "\n"
                if len(reading_map.chronological) > 15:
                    report += f"- ... and {len(reading_map.chronological) - 15} more works\n"
                report += "\n"

            # Thematic Groups
            if reading_map.thematic_groups:
                report += "### 🎭 Thematic Collections\n\n"
                for theme, entries in reading_map.thematic_groups.items():
                    if entries:
                        report += f"**{theme}:**\n"
                        for entry in entries[:5]:  # Limit per theme
                            report += f"- {entry.title}"
                            if entry.year:
                                report += f" ({entry.year})"
                            if entry.google_books_link:
                                report += f" - [📖 Link]({entry.google_books_link})"
                            report += "\n"
                        report += "\n"

        # Legacy Analysis
        if legacy:
            report += "## 🎯 Literary Legacy & Analysis\n\n"

            if legacy.stylistic_innovations:
                report += "### ✨ Stylistic Innovations\n"
                for innovation in legacy.stylistic_innovations:
                    report += f"- {innovation}\n"
                report += "\n"

            if legacy.recurring_themes:
                report += "### 🔍 Recurring Themes\n"
                for theme in legacy.recurring_themes:
                    report += f"- {theme}\n"
                report += "\n"

            if legacy.similar_authors:
                report += "### 🔗 If You Like This Author, Try...\n\n"
                for author in legacy.similar_authors:
                    report += f"- **{author['name']}** - {author.get('reason', 'Similar style or themes')}\n"
                report += "\n"

            if legacy.literary_significance:
                report += "### 📜 Critical Assessment\n\n"
                report += f"{legacy.literary_significance}\n\n"

        # Footer
        report += "---\n\n"
        report += "_Generated by The Literary Finder - A Multi-Agent System for Deep Literary Discovery_\n"

        return report

    @traceable(name="literary_finder_process_author")
    def process_author(self, author_name: str) -> Dict[str, Any]:
        """Process an author through the complete Literary Finder pipeline."""
        try:
            # Start performance evaluation
            if self.evaluator:
                self.evaluator.start_evaluation()
            
            initial_state = LiteraryFinderState(author_name=author_name)

            import uuid
            thread_id = str(uuid.uuid4())

            config = {"configurable": {"thread_id": thread_id}}
            result = self.graph.invoke(initial_state, config=config)

            # Add author name to result for evaluation
            result["author_name"] = author_name

            response = {
                "success": True,
                "data": result,
                "final_report": result.get("final_report"),
                "errors": result.get("errors", [])
            }

            # Generate performance evaluation if enabled
            if self.evaluator:
                performance_report = self.evaluator.evaluate_system_performance(
                    result, parallel_execution=self.enable_parallel
                )
                response["performance_report"] = performance_report
                logger.info(f"Performance evaluation completed for {author_name}")

            return response

        except Exception as e:
            logger.error(f"Error processing author {author_name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None
            }
    
    def get_performance_summary(self, result: Dict[str, Any]) -> Optional[str]:
        """Get a human-readable performance summary from the result."""
        performance_report = result.get("performance_report")
        if performance_report:
            return performance_report.generate_summary()
        return None

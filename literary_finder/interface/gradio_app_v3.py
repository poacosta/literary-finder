"""Gradio 3.x compatible web interface for the Literary Finder."""

import gradio as gr
import logging
import time
import os
from typing import Tuple, Optional
from ..orchestration import LiteraryFinderGraph
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global graph instance
literary_graph: Optional[LiteraryFinderGraph] = None


def initialize_graph() -> str:
    """Initialize the Literary Finder graph with OpenAI gpt-4o-mini."""
    global literary_graph

    try:
        # Check for required environment variables
        required_vars = ["OPENAI_API_KEY"]

        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)

        if missing_vars:
            return f"❌ Missing required environment variables: {', '.join(missing_vars)}"

        literary_graph = LiteraryFinderGraph(
            model_name="gpt-4o-mini",
            enable_parallel=True,
            enable_evaluation=True
        )

        return f"✅ Literary Finder initialized with OpenAI gpt-4o-mini"

    except Exception as e:
        logger.error(f"Failed to initialize Literary Finder: {e}")
        return f"❌ Initialization failed: {str(e)}"


def analyze_author(
        author_name: str,
        enable_parallel: bool = True
) -> Tuple[str, str, str]:
    """Analyze an author and return the results."""

    if not author_name or not author_name.strip():
        return "❌ Please enter an author name", "", ""

    author_name = author_name.strip()

    try:
        # Initialize or update graph if needed
        global literary_graph
        if not literary_graph:
            init_msg = initialize_graph()
            if "❌" in init_msg:
                return init_msg, "", ""

        # Create a custom graph if parallel setting is different
        graph = literary_graph
        if not enable_parallel:
            graph = LiteraryFinderGraph(
                model_name="gpt-4o-mini",
                enable_parallel=False,
                enable_evaluation=True
            )

        start_time = time.time()

        # Process the author
        result = graph.process_author(author_name)

        processing_time = time.time() - start_time

        if result["success"]:
            final_report = result.get("final_report", "No report generated")

            # Create status message with performance evaluation
            status_msg = f"✅ Analysis completed successfully in {processing_time:.1f} seconds"
            if result.get("errors"):
                status_msg += f"\n⚠️ {len(result['errors'])} warnings encountered"
            
            # Add performance evaluation summary
            if "performance_report" in result:
                performance_report = result["performance_report"]
                if performance_report:
                    status_msg += f"\n\n📊 PERFORMANCE EVALUATION:"
                    status_msg += f"\n• System Success Rate: {performance_report.system_metrics.success_rate:.1%}"
                    status_msg += f"\n• Successful Agents: {performance_report.system_metrics.successful_agents}/{performance_report.system_metrics.total_agents}"
                    status_msg += f"\n• Execution Mode: {'Parallel' if performance_report.system_metrics.parallel_execution else 'Sequential'}"
                    status_msg += f"\n• Final Report Generated: {'Yes' if performance_report.system_metrics.has_final_report else 'No'}"
                    status_msg += f"\n• Report Length: {performance_report.system_metrics.final_report_length:,} chars"
                    
                    if performance_report.quality_metrics:
                        status_msg += f"\n• Overall Quality Score: {performance_report.quality_metrics.overall_quality:.1%}"
                        status_msg += f"\n• Has Biographical Data: {'Yes' if performance_report.quality_metrics.has_biographical_data else 'No'}"
                        status_msg += f"\n• Bibliography Items: {performance_report.quality_metrics.bibliography_item_count}"
                        status_msg += f"\n• Has Literary Analysis: {'Yes' if performance_report.quality_metrics.has_literary_analysis else 'No'}"
                    
                    # Add top recommendation if available
                    if performance_report.recommendations:
                        status_msg += f"\n• Key Insight: {performance_report.recommendations[0]}"

            # Create error summary
            error_summary = ""
            if result.get("errors"):
                error_summary = "**Warnings/Issues encountered:**\n"
                for error in result["errors"]:
                    error_summary += f"- {error}\n"

            return status_msg, final_report, error_summary

        else:
            error_msg = f"❌ Analysis failed: {result.get('error', 'Unknown error')}"
            error_details = ""
            if result.get("errors"):
                error_details = "**Error details:**\n"
                for error in result["errors"]:
                    error_details += f"- {error}\n"

            return error_msg, "", error_details

    except Exception as e:
        logger.error(f"Unexpected error analyzing {author_name}: {e}")
        return f"❌ Unexpected error: {str(e)}", "", ""


def create_gradio_app_v3() -> gr.Blocks:
    """Create a Gradio 3.x compatible application."""

    # Example authors
    examples = [
        "Virginia Woolf", "Gabriel García Márquez", "Toni Morrison", "Jorge Luis Borges",
        "Maya Angelou", "James Baldwin", "Octavia Butler", "Haruki Murakami"
    ]

    # Custom CSS for Gradio 3.x
    custom_css = """
    .gradio-container { 
        max-width: 1200px; 
        margin: 0 auto; 
        font-family: system-ui, -apple-system, sans-serif; 
    }
    .main-header { 
        text-align: center; 
        padding: 24px; 
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
        color: white; 
        border-radius: 12px; 
        margin-bottom: 24px; 
    }
    """

    # Create the interface using Gradio 3.x API
    with gr.Blocks(css=custom_css, title="The Literary Finder") as app:
        # Header
        gr.HTML("""
        <div class="main-header">
            <h1>📚 The Literary Finder</h1>
            <p><em>A Multi-Agent System for Deep Literary Discovery</em></p>
            <p>Discover comprehensive insights about your favorite authors through OpenAI gpt-4o-mini</p>
        </div>
        """)

        with gr.Row():
            with gr.Column(scale=1):
                # Input section
                gr.Markdown("## 🔍 Author Analysis")

                author_input = gr.Textbox(
                    label="Author Name",
                    placeholder="Enter the name of an author (e.g., Virginia Woolf)",
                    lines=1
                )

                with gr.Row():
                    parallel_processing = gr.Checkbox(
                        label="Parallel Processing",
                        value=True,
                        info="Uses OpenAI gpt-4o-mini model"
                    )

                analyze_btn = gr.Button(
                    "🔍 Analyze Author",
                    variant="primary"
                )

                # Example authors as text
                gr.Markdown("### 💡 Try These Examples:")
                gr.Markdown(", ".join(examples))

                # Instructions
                gr.Markdown("""
                ## 📋 How to Use

                ### Instructions:
                1. **Enter an author name** in the text box above
                2. **Click "Analyze Author"** to start the research process
                3. **Wait 1-5 minutes** for the comprehensive analysis
                4. **Review the generated report** with biography, reading maps, and literary analysis

                ### What You'll Get:
                - 📚 **Biographical Context**: Life story and historical background
                - 🗺️ **Reading Map**: Strategic guide through the author's works
                - 🎯 **Literary Analysis**: Style, themes, and significance
                - 📊 **Performance Metrics**: Quality assessment and system evaluation

                ### Requirements:
                - Valid OpenAI API key (required for gpt-4o-mini model and web search)
                - Google API key (optional for web search)
                - Internet connection for research
                - Patience - quality analysis takes time! ⏱️

                ### AI Model:
                - **OpenAI gpt-4o-mini**: Cost-effective, fast model optimized for literary analysis
                """)

            with gr.Column(scale=2):
                # Results section
                gr.Markdown("## 📖 Literary Analysis Report")

                report_output = gr.Markdown(
                    value="*Your comprehensive literary analysis will appear here...*"
                )

                # Error details
                gr.Markdown("### ⚠️ Technical Details")
                error_output = gr.Markdown(
                    value="*No issues to report*"
                )

        # Status section
        gr.Markdown("### 📊 Analysis Status & Performance Metrics")
        status_output = gr.Textbox(
            label="Analysis Status & Performance Evaluation",
            lines=6,
            interactive=False
        )

        # Setup main event handler
        analyze_btn.click(
            fn=analyze_author,
            inputs=[author_input, parallel_processing],
            outputs=[status_output, report_output, error_output]
        )

        # Footer
        gr.HTML("""
        <div style="text-align: center; padding: 20px; color: #6c757d; border-top: 1px solid #dee2e6; margin-top: 40px;">
            <p>🤖 <strong>The Literary Finder</strong> - Powered by AI agents working together</p>
            <p><em>Built with LangChain, LangGraph, and Gradio</em></p>
        </div>
        """)

    return app


def launch_app_v3(
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
        share: bool = False,
        debug: bool = False
) -> None:
    """Launch the Gradio 3.x application."""

    required_vars = ["OPENAI_API_KEY", "GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these in your .env file or environment.")
        return

    print("🚀 Starting The Literary Finder (Gradio 3.x)...")
    print(f"📍 Server will be available at: http://{server_name}:{server_port}")
    print("📚 Ready to discover literary insights!")

    app = create_gradio_app_v3()

    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        debug=debug,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    launch_app_v3()

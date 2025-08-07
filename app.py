#!/usr/bin/env python3
"""
Main entry point for Hugging Face Spaces deployment.
"""

import os
import logging
from literary_finder.interface.gradio_app_v3 import create_gradio_app_v3
from literary_finder.config import LangSmithConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Main entry point for Hugging Face Spaces."""
    
    # Initialize LangSmith tracing for production
    LangSmithConfig.setup_tracing("literary-finder-prod")
    
    if LangSmithConfig.is_enabled():
        logger.info("🔍 LangSmith tracing enabled for production monitoring")
    else:
        logger.info("📊 LangSmith tracing disabled (API key not configured)")
    
    # Set production defaults for Hugging Face Spaces
    host = "0.0.0.0"
    port = 7860
    
    logger.info("🚀 Starting The Literary Finder for Hugging Face Spaces...")
    logger.info(f"📍 Server will be available at: http://{host}:{port}")
    logger.info("📚 Ready to discover literary insights!")
    
    # Create the Gradio app
    app = create_gradio_app_v3()
    
    # Launch with Hugging Face Spaces compatible settings
    app.launch(
        server_name=host,
        server_port=port,
        share=False,  # Hugging Face handles sharing
        debug=False,
        show_error=True,
        quiet=False
    )

if __name__ == "__main__":
    main()
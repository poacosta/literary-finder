"""Main application entry point for the Literary Finder Gradio interface."""

import argparse
import os
from dotenv import load_dotenv
from .interface import create_gradio_app


def main():
    """Main entry point for the Gradio application."""
    parser = argparse.ArgumentParser(
        description="The Literary Finder: Gradio Web Interface"
    )
    
    parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Host to bind the server to (default: 127.0.0.1)"
    )
    
    parser.add_argument(
        "--port",
        type=int,
        default=7860,
        help="Port to bind the server to (default: 7860)"
    )
    
    parser.add_argument(
        "--share",
        action="store_true",
        help="Create a public link via Gradio's sharing service"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--env-file",
        type=str,
        default=".env",
        help="Path to environment file (default: .env)"
    )
    
    args = parser.parse_args()
    
    # Load environment variables
    if os.path.exists(args.env_file):
        load_dotenv(args.env_file)
        print(f"✅ Loaded environment from: {args.env_file}")
    else:
        print(f"⚠️ Environment file not found: {args.env_file}")
        print("Make sure to set your API keys as environment variables")
    
    # Check for required environment variables
    required_vars = ["OPENAI_API_KEY"]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print(f"\nPlease set them in your {args.env_file} file or environment.")
        print("\nExample .env file:")
        print("OPENAI_API_KEY=sk-your_openai_key_here")
        return
    
    # Display startup information
    print("🚀 Starting The Literary Finder Web Interface...")
    print(f"📍 Server: http://{args.host}:{args.port}")
    
    if args.share:
        print("🌐 Public sharing enabled - a public URL will be generated")
    
    if args.debug:
        print("🔧 Debug mode enabled")
    
    print("📚 Ready to discover literary insights!")
    print("\n" + "="*50)
    
    try:
        # Create and launch the Gradio app
        app = create_gradio_app()
        
        app.launch(
            server_name=args.host,
            server_port=args.port,
            share=args.share,
            debug=args.debug,
            show_error=True,
            quiet=False
        )
        
    except KeyboardInterrupt:
        print("\n👋 Literary Finder stopped by user")
    except Exception as e:
        print(f"❌ Error starting application: {e}")


if __name__ == "__main__":
    main()
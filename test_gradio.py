#!/usr/bin/env python3
"""Simple test to verify Gradio 5.x compatibility"""

import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import gradio as gr
    print(f"✅ Gradio version: {gr.__version__}")
    
    # Test creating a simple interface
    def test_function(text):
        return f"Echo: {text}"
    
    with gr.Blocks() as demo:
        gr.Markdown("# Test Interface")
        text_input = gr.Textbox(label="Input")
        text_output = gr.Textbox(label="Output")
        btn = gr.Button("Test")
        
        btn.click(fn=test_function, inputs=[text_input], outputs=[text_output])
    
    print("✅ Basic Gradio interface created successfully")
    
    # Test importing our interface
    try:
        from literary_finder.interface import create_gradio_app
        print("✅ Literary Finder interface import successful")
        
        # Test creating our interface
        app = create_gradio_app()
        print("✅ Literary Finder interface created successfully")
        
    except ImportError as e:
        print(f"❌ Failed to import Literary Finder interface: {e}")
    except Exception as e:
        print(f"❌ Failed to create Literary Finder interface: {e}")
        
except ImportError as e:
    print(f"❌ Failed to import Gradio: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
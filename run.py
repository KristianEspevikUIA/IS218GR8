#!/usr/bin/env python
"""
Main entry point for the Flask application
Run this file to start the web map server
"""
import os
import sys
from app import app, controller


if __name__ == '__main__':
    print("=" * 50)
    print("Interactive Web Map - Python Flask + MVC")
    print("=" * 50)
    print()
    print("✓ Starting Flask server on http://localhost:5000")
    print("✓ Press Ctrl+C to stop the server")
    print()
    
    try:
        controller.initialize()
        app.run(debug=True, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\n✓ Server stopped")
        sys.exit(0)

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
    print("OK Starting Flask server on http://localhost:3000")
    print("OK Press Ctrl+C to stop the server")
    print()
    
    try:
        controller.initialize()
        app.run(debug=True, port=3000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nOK Server stopped")
        sys.exit(0)

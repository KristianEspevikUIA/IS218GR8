#!/bin/bash
# Run Python Flask Web Map Application (Mac/Linux)

echo ""
echo "========================================"
echo "Interactive Web Map - Python Flask"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "✗ Python3 is not installed"
    echo "Please install Python from https://www.python.org/"
    exit 1
fi

# Navigate to python_app directory
cd "$(dirname "$0")/python_app"

# Check if requirements are installed
if ! python3 -c "import flask" &> /dev/null; then
    echo "Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "✗ Failed to install dependencies"
        exit 1
    fi
fi

echo ""
echo "✓ Starting Flask server..."
echo "✓ Open http://localhost:5000 in your browser"
echo "✓ Press Ctrl+C to stop"
echo ""

python3 run.py

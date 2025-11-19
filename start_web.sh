#!/bin/bash
# Quick start script for AI Agent Pipeline Web Interface

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║        AI Agent Pipeline - Web Interface Launcher           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import flask, flask_socketio" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  Web dependencies not found. Installing..."
    pip3 install flask flask-socketio python-socketio
fi

# Check if config.json exists
if [ ! -f "./config.json" ]; then
    echo "⚠️  Configuration file not found. Creating default config..."
    python3 main.py init
    echo ""
    echo "⚠️  Please edit config.json and add your API keys before continuing."
    echo "    Press Enter to continue or Ctrl+C to exit and edit config..."
    read -r
fi

# Start the web server
echo ""
echo "🚀 Starting web server..."
echo ""
python3 web/app.py

#!/bin/bash
# Development script for AI Agent Platform (without Docker)

set -e

echo "========================================="
echo "  AI Agent Platform - Dev Mode"
echo "========================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Error: .env file not found!"
    echo "Please create a .env file from .env.example:"
    echo "  cp .env.example .env"
    echo "Then edit .env to add your API keys."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Update DATABASE_URL and REDIS_URL for local development
export DATABASE_URL="postgresql://agent_user:agent_password@localhost:5432/agent_platform"
export REDIS_URL="redis://localhost:6379/0"

echo "Starting development services..."
echo ""
echo "Prerequisites:"
echo "  - PostgreSQL running on localhost:5432"
echo "  - Redis running on localhost:6379"
echo ""
echo "Database: $DATABASE_URL"
echo "Redis: $REDIS_URL"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

echo ""
echo "You can now run:"
echo ""
echo "  Terminal 1 - API Server:"
echo "    source venv/bin/activate"
echo "    uvicorn services.api.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "  Terminal 2 - Worker:"
echo "    source venv/bin/activate"
echo "    python services/worker/main.py"
echo ""
echo "  Terminal 3 - Frontend:"
echo "    cd frontend"
echo "    npm install"
echo "    npm run dev"
echo ""
echo "========================================="

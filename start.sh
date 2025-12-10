#!/bin/bash
# Start script for AI Agent Platform

set -e

echo "========================================="
echo "  AI Agent Platform - Startup Script"
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

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "Error: docker-compose is not installed!"
    echo "Please install Docker and Docker Compose first."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | xargs)

# Check if at least one API key is set
if [ -z "$ANTHROPIC_API_KEY" ] && [ -z "$OPENAI_API_KEY" ] && [ -z "$GOOGLE_API_KEY" ] && [ -z "$GROQ_API_KEY" ]; then
    echo "Warning: No API keys found in .env file!"
    echo "Please add at least one API key to .env:"
    echo "  - ANTHROPIC_API_KEY"
    echo "  - OPENAI_API_KEY"
    echo "  - GOOGLE_API_KEY"
    echo "  - GROQ_API_KEY"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo "Starting services with Docker Compose..."
echo ""

# Start services
docker-compose -f docker-compose.v2.yml up --build -d

echo ""
echo "========================================="
echo "  Services Started!"
echo "========================================="
echo ""
echo "Services running:"
echo "  - PostgreSQL: localhost:5432"
echo "  - Redis: localhost:6379"
echo "  - API Server: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.v2.yml logs -f"
echo ""
echo "To stop services:"
echo "  docker-compose -f docker-compose.v2.yml down"
echo ""
echo "Next steps:"
echo "  1. Start the frontend:"
echo "     cd frontend && npm install && npm run dev"
echo "  2. Access the UI at http://localhost:5173"
echo ""
echo "========================================="

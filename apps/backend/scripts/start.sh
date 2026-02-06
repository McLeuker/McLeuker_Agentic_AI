#!/bin/bash
# McLeuker Agentic AI Platform - Startup Script
# Usage: ./scripts/start.sh [dev|prod]

set -e

MODE=${1:-dev}

echo "🚀 Starting McLeuker Agentic AI Platform..."
echo "Mode: $MODE"

# Create directories if they don't exist
mkdir -p outputs temp

# Check for .env file
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found. Copying from .env.example..."
    cp .env.example .env
    echo "📝 Please edit .env and add your API keys."
fi

# Install dependencies if needed
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
if [ "$MODE" = "prod" ]; then
    echo "🌐 Starting production server..."
    uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000}
else
    echo "🔧 Starting development server with auto-reload..."
    uvicorn src.api.main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
fi

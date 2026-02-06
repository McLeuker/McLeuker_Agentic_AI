#!/bin/bash
# McLeuker Agentic AI Platform - Setup Script
# Run this once to set up the development environment

set -e

echo "🔧 Setting up McLeuker Agentic AI Platform..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
REQUIRED_VERSION="3.11"

echo "📌 Python version: $PYTHON_VERSION"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p outputs temp

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env and add your API keys!"
    echo "   Required keys:"
    echo "   - OPENAI_API_KEY (for GPT-4)"
    echo "   - GROK_API_KEY (for Grok)"
    echo "   - GOOGLE_SEARCH_API_KEY (for search)"
    echo ""
else
    echo "✅ .env file already exists"
fi

# Make scripts executable
chmod +x scripts/*.sh

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server, run:"
echo "  ./scripts/start.sh"
echo ""
echo "Or with Docker:"
echo "  docker-compose up"
echo ""

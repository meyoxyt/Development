#!/bin/bash
# Quick setup script for Minimax AI Assistant

set -e

echo "========================================"
echo "Minimax 2.1 AI Assistant Setup"
echo "========================================"
echo ""

# Check Python version
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
echo "✓ Python $PYTHON_VERSION detected"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
echo "Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source venv/Scripts/activate
else
    source venv/bin/activate
fi

# Upgrade pip
echo "Upgrading pip..."
python -m pip install --upgrade pip > /dev/null 2>&1
echo "✓ pip upgraded"

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt > /dev/null 2>&1
echo "✓ Dependencies installed"

# Create workspace directory
if [ ! -d "workspace" ]; then
    mkdir workspace
    echo "✓ Workspace directory created"
fi

# Create logs directory
if [ ! -d "logs" ]; then
    mkdir logs
    echo "✓ Logs directory created"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✓ .env file created from template"
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your API credentials:"
    echo "   - MINIMAX_API_KEY"
    echo "   - MINIMAX_GROUP_ID"
    echo ""
else
    echo "✓ .env file already exists"
fi

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your API credentials"
echo "2. Run: python main.py --interactive"
echo ""
echo "For help: python main.py --help"
echo ""

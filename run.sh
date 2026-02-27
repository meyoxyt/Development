#!/bin/bash
# Quick run script for Minimax AI Assistant

set -e

# Activate virtual environment
if [ -d "venv" ]; then
    if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
        source venv/Scripts/activate
    else
        source venv/bin/activate
    fi
fi

# Run the assistant
python main.py "$@"

# Quick run script for Windows PowerShell

# Activate virtual environment if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    .\venv\Scripts\Activate.ps1
}

# Run the assistant
python main.py $args

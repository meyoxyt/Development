# Quick setup script for Windows PowerShell
# Minimax 2.1 AI Assistant Setup

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Minimax 2.1 AI Assistant Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "[OK] $pythonVersion detected" -ForegroundColor Green
} catch {
    Write-Host "[ERROR] Python is not installed or not in PATH" -ForegroundColor Red
    exit 1
}

# Create virtual environment
if (-not (Test-Path "venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "[OK] Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
Write-Host "[OK] pip upgraded" -ForegroundColor Green

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt --quiet
Write-Host "[OK] Dependencies installed" -ForegroundColor Green

# Create workspace directory
if (-not (Test-Path "workspace")) {
    New-Item -ItemType Directory -Path "workspace" | Out-Null
    Write-Host "[OK] Workspace directory created" -ForegroundColor Green
}

# Create logs directory
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" | Out-Null
    Write-Host "[OK] Logs directory created" -ForegroundColor Green
}

# Create .env file if it doesn't exist
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "[OK] .env file created from template" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Using Ollama with minimax-2.1:cloud model" -ForegroundColor Yellow
    Write-Host "Make sure you have:" -ForegroundColor Yellow
    Write-Host "  1. Ollama installed and running" -ForegroundColor White
    Write-Host "  2. Model pulled: ollama pull minimax-2.1:cloud" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host "[OK] .env file already exists" -ForegroundColor Green
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:"
Write-Host "1. Make sure Ollama is running: ollama serve"
Write-Host "2. Pull model: ollama pull minimax-2.1:cloud"
Write-Host "3. Run: python main.py --interactive"
Write-Host ""
Write-Host "For help: python main.py --help"
Write-Host ""

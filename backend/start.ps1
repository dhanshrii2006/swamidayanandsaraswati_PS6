# PowerShell Quick Start Script for Roadside Assistance Backend

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Roadside Assistance Backend - Quick Start" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (-not (Test-Path "venv\Scripts\python.exe")) {
    Write-Host "[ERROR] Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please create it first with: python -m venv venv" -ForegroundColor Yellow
    exit 1
}

Write-Host "Using Python: venv\Scripts\python.exe" -ForegroundColor Green
Write-Host ""

# Check if database exists
if (-not (Test-Path "roadside_assistance.db")) {
    Write-Host "[INFO] Database not found. Initializing..." -ForegroundColor Yellow
    & venv\Scripts\python.exe init_db.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERROR] Database initialization failed!" -ForegroundColor Red
        exit 1
    }
    Write-Host ""
}

Write-Host "[INFO] Starting API server..." -ForegroundColor Green
Write-Host "Server will be available at: http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

& venv\Scripts\python.exe api.py

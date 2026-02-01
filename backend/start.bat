@echo off
REM Quick Start Script for Roadside Assistance Backend

echo ============================================================
echo Roadside Assistance Backend - Quick Start
echo ============================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found!
    echo Please create it first with: python -m venv venv
    exit /b 1
)

echo Using Python: venv\Scripts\python.exe
echo.

REM Check if database exists
if not exist "roadside_assistance.db" (
    echo [INFO] Database not found. Initializing...
    venv\Scripts\python.exe init_db.py
    if errorlevel 1 (
        echo [ERROR] Database initialization failed!
        exit /b 1
    )
    echo.
)

echo [INFO] Starting API server...
echo Server will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ============================================================
echo.

venv\Scripts\python.exe api.py

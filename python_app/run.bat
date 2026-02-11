@echo off
REM Run Python Flask Web Map Application

echo.
echo ========================================
echo Interactive Web Map - Python Flask
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ✗ Python is not installed or not in PATH
    echo Please install Python from https://www.python.org/
    pause
    exit /b 1
)

REM Navigate to python_app directory
cd /d "%~dp0python_app"

REM Check if requirements are installed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ✗ Failed to install dependencies
        pause
        exit /b 1
    )
)

echo.
echo ✓ Starting Flask server...
echo ✓ Open http://localhost:5000 in your browser
echo ✓ Press Ctrl+C to stop
echo.

python run.py

pause

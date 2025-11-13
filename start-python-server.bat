@echo off
chcp 949 >nul 2>&1
REM Python HTTP Server (Port 3002) Startup Script

echo ========================================
echo Python HTTP Server Startup (Port 3002)
echo ========================================
echo.

REM Check Python Installation
echo [1/3] Checking Python Installation...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)
echo.

REM Check Playwright Installation
echo [2/3] Checking Playwright Installation...
pip show playwright >nul 2>&1
if errorlevel 1 (
    echo Playwright is not installed. Installing...
    pip install playwright
    if errorlevel 1 (
        echo Error: Failed to install Playwright.
        pause
        exit /b 1
    )
    echo Installing Playwright browsers...
    playwright install chromium
) else (
    echo Playwright is already installed.
)
echo.

REM Check Server File
echo [3/3] Checking Server File...
if not exist "mcp-screen-validator-http-server.py" (
    echo Error: mcp-screen-validator-http-server.py file not found.
    pause
    exit /b 1
)
echo Server file found.
echo.

REM Start Server
echo ========================================
echo Python HTTP Server is starting.
echo URL: http://localhost:3002
echo Press Ctrl+C to stop the server.
echo ========================================
echo.

python mcp-screen-validator-http-server.py

pause

@echo off
chcp 949 >nul 2>&1
REM Unified MCP Server Build and Run Script

echo ========================================
echo Unified MCP Server Build and Run
echo ========================================
echo.

REM Check Python Installation
echo [1/4] Checking Python Installation...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b 1
)
echo.

REM Check MCP SDK Installation
echo [2/4] Checking MCP SDK Installation...
pip show mcp >nul 2>&1
if errorlevel 1 (
    echo MCP SDK is not installed. Installing...
    pip install mcp
    if errorlevel 1 (
        echo Error: Failed to install MCP SDK.
        pause
        exit /b 1
    )
) else (
    echo MCP SDK is already installed.
)
echo.

REM Check Server File
echo [3/4] Checking Server File...
if not exist "mcp-unified-server.py" (
    echo Error: mcp-unified-server.py file not found.
    pause
    exit /b 1
)
echo Server file found.
echo.

REM Start Server
echo [4/4] Starting Unified MCP Server...
echo.
echo ========================================
echo Unified MCP Server is starting.
echo Press Ctrl+C to stop the server.
echo ========================================
echo.

python mcp-unified-server.py

pause

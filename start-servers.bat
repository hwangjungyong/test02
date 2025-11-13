@echo off
REM ========================================
REM All Servers Startup Script (Single Terminal)
REM All servers run in current terminal window
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Starting All Servers in Current Terminal
echo ========================================
echo.

REM Check and kill processes using required ports
echo [0/5] Checking ports and closing existing processes...
call scripts\check-ports.bat
echo.

echo Servers to start:
echo   1. API Server (Port 3001)
echo   2. MCP Server (Node.js)
echo   3. Python HTTP Server (Port 3002)
echo   4. Unified MCP Server (Python)
echo   5. Vite Dev Server (Port 5173)
echo.
echo Press Ctrl+C to stop all servers
echo ========================================
echo.

REM Check if concurrently is installed locally
if not exist node_modules\.bin\concurrently.cmd (
    echo Installing concurrently...
    call npm install concurrently --save-dev
    if errorlevel 1 (
        echo Error: Failed to install concurrently
        echo Please run: npm install concurrently --save-dev
        pause
        exit /b 1
    )
)

REM Use concurrently to run all servers in one terminal
echo Starting all servers in current terminal...
echo.
call npm run start:all

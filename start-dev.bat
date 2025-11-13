@echo off
REM ========================================
REM Development Environment Server Startup Script
REM Encoding: ANSI (CP949)
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Development Environment Server Startup
echo ========================================
echo.

REM Check API Server
echo [1/4] Checking API Server...
netstat -ano | findstr :3001 >nul 2>&1
if errorlevel 1 (
    echo API Server is not running. Starting...
    start "API Server (Port 3001)" cmd /k "chcp 949 >nul && npm run api-server"
    echo Waiting for API Server to start...
    timeout /t 3 /nobreak >nul
    
    REM Check again
    netstat -ano | findstr :3001 >nul 2>&1
    if errorlevel 1 (
        echo Warning: API Server may not have started.
        echo Please run manually: npm run api-server
    ) else (
        echo API Server started successfully.
    )
) else (
    echo API Server is already running.
)
echo.

REM Check Python HTTP Server
echo [2/4] Checking Python HTTP Server...
netstat -ano | findstr :3002 >nul 2>&1
if errorlevel 1 (
    echo Python HTTP Server is not running. Starting...
    start "Python HTTP Server (Port 3002)" cmd /k "chcp 949 >nul && npm run screen-validator-server"
    echo Waiting for Python HTTP Server to start...
    timeout /t 3 /nobreak >nul
    
    REM Check again
    netstat -ano | findstr :3002 >nul 2>&1
    if errorlevel 1 (
        echo Warning: Python HTTP Server may not have started.
        echo Please run manually: npm run screen-validator-server
        echo Or: python mcp-screen-validator-http-server.py
    ) else (
        echo Python HTTP Server started successfully.
    )
) else (
    echo Python HTTP Server is already running.
)
echo.

REM Server Status Summary
echo [3/4] Server Status Summary:
netstat -ano | findstr ":3001 :3002" | findstr LISTENING
echo.

REM Check if concurrently is installed
if not exist node_modules\.bin\concurrently.cmd (
    echo Installing concurrently...
    call npm install concurrently --save-dev
)

REM Start all servers in current terminal using concurrently
echo [4/4] Starting all servers in current terminal...
echo.
echo ========================================
echo All servers are starting in this terminal.
echo Please open http://localhost:5173 in your browser.
echo Press Ctrl+C to stop all servers.
echo ========================================
echo.
echo Server URLs:
echo   - API Server: http://localhost:3001
echo   - Python HTTP Server: http://localhost:3002
echo   - Vite Dev Server: http://localhost:5173
echo.
echo Notes:
echo   - All servers run in this terminal window
echo   - Each server output is color-coded
echo   - Press Ctrl+C to stop all servers at once
echo.

REM Use concurrently to run API, Python HTTP, and Vite servers
call npm run dev:all

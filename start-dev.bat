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
set API_RUNNING=0
if errorlevel 1 (
    echo API Server is not running. Will start in concurrently...
    set API_RUNNING=1
) else (
    echo API Server is already running. Skipping...
    set API_RUNNING=0
)
echo.

REM Check Python HTTP Server
echo [2/4] Checking Python HTTP Server...
netstat -ano | findstr :3002 >nul 2>&1
set PYTHON_RUNNING=0
if errorlevel 1 (
    echo Python HTTP Server is not running. Will start in concurrently...
    set PYTHON_RUNNING=1
) else (
    echo Python HTTP Server is already running. Skipping...
    set PYTHON_RUNNING=0
)
echo.

REM Check Vite Dev Server
echo [3/5] Checking Vite Dev Server...
netstat -ano | findstr :5173 >nul 2>&1
set VITE_RUNNING=0
if errorlevel 1 (
    echo Vite Dev Server is not running. Will start in concurrently...
    set VITE_RUNNING=1
) else (
    echo Vite Dev Server is already running. Killing existing process...
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
        echo Killing process %%a on port 5173...
        taskkill /F /PID %%a >nul 2>&1
    )
    set VITE_RUNNING=1
)
echo.

REM Server Status Summary
echo [4/5] Server Status Summary:
netstat -ano | findstr ":3001 :3002 :5173" | findstr LISTENING
echo.

REM Check if concurrently is installed
if not exist node_modules\.bin\concurrently.cmd (
    echo Installing concurrently...
    call npm install concurrently --save-dev
)

REM Start servers in current terminal using concurrently
echo [5/5] Starting servers in current terminal...
echo.
echo ========================================
echo Servers are starting in this terminal.
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

REM Use concurrently to run only servers that are not already running
if %API_RUNNING%==1 (
    if %PYTHON_RUNNING%==1 (
        if %VITE_RUNNING%==1 (
            echo Starting API Server, Python HTTP Server, and Vite dev server...
            call concurrently "npm run api-server" "npm run screen-validator-server" "npm run dev"
        ) else (
            echo Starting API Server and Python HTTP Server...
            call concurrently "npm run api-server" "npm run screen-validator-server"
        )
    ) else (
        if %VITE_RUNNING%==1 (
            echo Starting API Server and Vite dev server...
            call concurrently "npm run api-server" "npm run dev"
        ) else (
            echo Starting API Server only...
            call npm run api-server
        )
    )
) else (
    if %PYTHON_RUNNING%==1 (
        if %VITE_RUNNING%==1 (
            echo Starting Python HTTP Server and Vite dev server...
            call concurrently "npm run screen-validator-server" "npm run dev"
        ) else (
            echo Starting Python HTTP Server only...
            call npm run screen-validator-server
        )
    ) else (
        if %VITE_RUNNING%==1 (
            echo Starting Vite dev server...
            call npm run dev
        ) else (
            echo All servers are already running!
            echo.
            echo Server URLs:
            echo   - API Server: http://localhost:3001
            echo   - Python HTTP Server: http://localhost:3002
            echo   - Vite Dev Server: http://localhost:5173
            pause
        )
    )
)

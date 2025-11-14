@echo off
REM ========================================
REM Stop All Servers Script
REM 모든 서버를 종료합니다
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Stopping All Servers
echo ========================================
echo.

REM Kill processes on port 3001 (API Server)
echo [1/4] Stopping API Server (Port 3001)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Process %%a not found or already stopped.
    ) else (
        echo API Server stopped.
    )
)
echo.

REM Kill processes on port 3002 (Python HTTP Server)
echo [2/4] Stopping Python HTTP Server (Port 3002)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3002 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Process %%a not found or already stopped.
    ) else (
        echo Python HTTP Server stopped.
    )
)
echo.

REM Kill processes on port 5173 (Vite Dev Server)
echo [3/4] Stopping Vite Dev Server (Port 5173)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
    echo Killing process %%a...
    taskkill /F /PID %%a >nul 2>&1
    if errorlevel 1 (
        echo Process %%a not found or already stopped.
    ) else (
        echo Vite Dev Server stopped.
    )
)
echo.

REM Kill Node.js processes (MCP Server)
echo [4/4] Stopping Node.js MCP Server...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq MCP*" >nul 2>&1
taskkill /F /IM node.exe /FI "COMMANDLINE eq *mcp-server.js*" >nul 2>&1
echo.

echo ========================================
echo All servers stopped!
echo ========================================
echo.
echo To start servers again:
echo   Run: start-dev.bat
echo   Or: auto-start-servers.bat
echo.
pause


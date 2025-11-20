@echo off
REM ========================================
REM MCP Server Status Check Script
REM ========================================

chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo MCP Server Status Check
echo ========================================
echo.

REM 1. Check Node.js MCP Server
echo [1/4] Checking Node.js MCP Server (mcp-server.js)...
tasklist /FI "IMAGENAME eq node.exe" 2>nul | findstr /I "node.exe" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Node.js processes found:
    tasklist /FI "IMAGENAME eq node.exe" /FO TABLE | findstr /I "node.exe"
) else (
    echo   [STOPPED] No Node.js processes found
)
echo.

REM 2. Check Python MCP Servers
echo [2/4] Checking Python MCP Servers...
tasklist /FI "IMAGENAME eq python.exe" 2>nul | findstr /I "python.exe" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Python processes found:
    tasklist /FI "IMAGENAME eq python.exe" /FO TABLE | findstr /I "python.exe"
) else (
    echo   [STOPPED] No Python processes found
)
echo.

REM 3. Check Python HTTP Server (Port 3002)
echo [3/4] Checking Python HTTP Server (Port 3002)...
netstat -ano 2>nul | findstr ":3002" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Port 3002 is LISTENING
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3002" ^| findstr "LISTENING"') do (
        echo   PID: %%a
        tasklist /FI "PID eq %%a" /FO TABLE 2>nul | findstr /I "python.exe"
    )
) else (
    echo   [STOPPED] Port 3002 is not in use
)
echo.

REM 4. Check API Server (Port 3001)
echo [4/4] Checking API Server (Port 3001)...
netstat -ano 2>nul | findstr ":3001" | findstr "LISTENING" >nul
if %errorlevel% equ 0 (
    echo   [RUNNING] Port 3001 is LISTENING
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":3001" ^| findstr "LISTENING"') do (
        echo   PID: %%a
        tasklist /FI "PID eq %%a" /FO TABLE 2>nul | findstr /I "node.exe"
    )
) else (
    echo   [STOPPED] Port 3001 is not in use
)
echo.

echo ========================================
echo Check Complete
echo ========================================
echo.
echo Notes:
echo - MCP servers communicate via stdio (no ports)
echo - Python HTTP Server uses port 3002
echo - API Server uses port 3001
echo.

pause


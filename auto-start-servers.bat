@echo off
REM ========================================
REM Auto-Start Servers Script (Always Running)
REM 서버가 종료되면 자동으로 재시작합니다
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

:LOOP
echo ========================================
echo [%date% %time%] Starting servers...
echo ========================================
echo.

REM Check if API Server is running
netstat -ano | findstr :3001 >nul 2>&1
if errorlevel 1 (
    echo [%time%] API Server is not running. Starting...
    start "API Server (Port 3001)" /min cmd /k "chcp 949 >nul && cd /d %~dp0 && npm run api-server"
    timeout /t 2 /nobreak >nul
) else (
    echo [%time%] API Server is already running.
)

REM Check if Python HTTP Server is running
netstat -ano | findstr :3002 >nul 2>&1
if errorlevel 1 (
    echo [%time%] Python HTTP Server is not running. Starting...
    start "Python HTTP Server (Port 3002)" /min cmd /k "chcp 949 >nul && cd /d %~dp0 && npm run screen-validator-server"
    timeout /t 2 /nobreak >nul
) else (
    echo [%time%] Python HTTP Server is already running.
)

REM Check if Vite Dev Server is running
netstat -ano | findstr :5173 >nul 2>&1
if errorlevel 1 (
    echo [%time%] Vite Dev Server is not running. Starting...
    start "Vite Dev Server (Port 5173)" /min cmd /k "chcp 949 >nul && cd /d %~dp0 && npm run dev"
    timeout /t 2 /nobreak >nul
) else (
    echo [%time%] Vite Dev Server is already running.
)

echo.
echo [%time%] All servers checked. Waiting 30 seconds before next check...
echo Press Ctrl+C to stop monitoring
echo.

REM Wait 30 seconds before checking again
timeout /t 30 /nobreak >nul

goto LOOP


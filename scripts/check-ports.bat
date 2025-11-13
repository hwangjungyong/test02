@echo off
REM 포트 사용 여부 확인 및 프로세스 종료 스크립트

echo Checking ports...
echo.

REM Check port 3001 (API Server)
netstat -ano | findstr :3001 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 3001 is already in use (API Server)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3001 ^| findstr LISTENING') do (
        echo Killing process %%a...
        taskkill /F /PID %%a >nul 2>&1
        if errorlevel 1 (
            echo Failed to kill process %%a. Please close it manually.
        ) else (
            echo Process %%a killed successfully.
        )
    )
    timeout /t 1 /nobreak >nul
)

REM Check port 3002 (Python HTTP Server)
netstat -ano | findstr :3002 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 3002 is already in use (Python HTTP Server)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3002 ^| findstr LISTENING') do (
        echo Killing process %%a...
        taskkill /F /PID %%a >nul 2>&1
        if errorlevel 1 (
            echo Failed to kill process %%a. Please close it manually.
        ) else (
            echo Process %%a killed successfully.
        )
    )
    timeout /t 1 /nobreak >nul
)

REM Check port 5173 (Vite Dev Server)
netstat -ano | findstr :5173 | findstr LISTENING >nul 2>&1
if not errorlevel 1 (
    echo [WARNING] Port 5173 is already in use (Vite Dev Server)
    for /f "tokens=5" %%a in ('netstat -ano ^| findstr :5173 ^| findstr LISTENING') do (
        echo Killing process %%a...
        taskkill /F /PID %%a >nul 2>&1
        if errorlevel 1 (
            echo Failed to kill process %%a. Please close it manually.
        ) else (
            echo Process %%a killed successfully.
        )
    )
    timeout /t 1 /nobreak >nul
)

echo Port check completed.
echo.


@echo off
REM ========================================
REM Docker Build Script (Windows)
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Docker Build Script
echo ========================================
echo.

REM Check if Docker is installed
where docker >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
where docker-compose >nul 2>&1
if errorlevel 1 (
    echo Warning: docker-compose command not found
    echo Trying docker compose instead...
    set DOCKER_COMPOSE_CMD=docker compose
) else (
    set DOCKER_COMPOSE_CMD=docker-compose
)

REM Build mode selection
set BUILD_MODE=%1
if "%BUILD_MODE%"=="" set BUILD_MODE=production

echo Build mode: %BUILD_MODE%
echo.

if "%BUILD_MODE%"=="dev" (
    echo Building development images...
    %DOCKER_COMPOSE_CMD% -f docker-compose.dev.yml build
    echo.
    echo Build complete! Run with: %DOCKER_COMPOSE_CMD% -f docker-compose.dev.yml up
) else (
    echo Building production images...
    %DOCKER_COMPOSE_CMD% build
    echo.
    echo Build complete! Run with: %DOCKER_COMPOSE_CMD% up -d
)

echo.
echo ========================================
echo Build completed successfully!
echo ========================================
pause


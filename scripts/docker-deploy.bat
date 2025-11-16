@echo off
REM ========================================
REM Docker Deployment Script (Windows)
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Docker Deployment Script
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

REM Check Docker Compose command (v2 우선)
docker compose version >nul 2>&1
if errorlevel 1 (
    where docker-compose >nul 2>&1
    if errorlevel 1 (
        echo Error: Docker Compose is not installed
        echo Please install Docker Desktop: https://www.docker.com/products/docker-desktop
        pause
        exit /b 1
    ) else (
        set DOCKER_COMPOSE_CMD=docker-compose
    )
) else (
    set DOCKER_COMPOSE_CMD=docker compose
)

REM Check .env file
if not exist .env (
    echo Warning: .env file not found
    echo Please create .env file with required environment variables
    echo.
)

REM Build
echo [1/3] Building Docker images...
%DOCKER_COMPOSE_CMD% build
if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

REM Stop existing containers
echo [2/3] Stopping existing containers...
%DOCKER_COMPOSE_CMD% down

REM Start containers
echo [3/3] Starting containers...
%DOCKER_COMPOSE_CMD% up -d
if errorlevel 1 (
    echo Error: Failed to start containers
    pause
    exit /b 1
)

REM Status check
echo.
echo ========================================
echo Deployment completed!
echo ========================================
echo.
echo Container status:
%DOCKER_COMPOSE_CMD% ps
echo.
echo Services:
echo   - Frontend: http://localhost:5173
echo   - Backend API: http://localhost:3001
echo   - Python HTTP: http://localhost:3002
echo.
echo View logs: %DOCKER_COMPOSE_CMD% logs -f
echo Stop services: %DOCKER_COMPOSE_CMD% down
echo.
pause


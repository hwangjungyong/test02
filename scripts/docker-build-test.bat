@echo off
REM ========================================
REM Docker Build Test Script (Windows)
REM 빌드 테스트 및 검증
REM ========================================

REM Set code page to Korean (CP949)
chcp 949 >nul 2>&1
if errorlevel 1 chcp 949

echo ========================================
echo Docker Build Test Script
echo ========================================
echo.

REM Check Docker
where docker >nul 2>&1
if errorlevel 1 (
    echo Error: Docker is not installed
    pause
    exit /b 1
)

REM Check Docker Compose (v2 우선)
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

echo [1/4] Building Docker images...
%DOCKER_COMPOSE_CMD% build --no-cache
if errorlevel 1 (
    echo Error: Build failed
    pause
    exit /b 1
)

echo.
echo [2/4] Checking image sizes...
docker images test02* --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo.
echo [3/4] Validating docker-compose configuration...
%DOCKER_COMPOSE_CMD% config
if errorlevel 1 (
    echo Error: Configuration validation failed
    pause
    exit /b 1
)

echo.
echo [4/4] Build test completed successfully!
echo.
echo Next steps:
echo   1. Run: scripts\docker-deploy.bat
echo   2. Or: %DOCKER_COMPOSE_CMD% up -d
echo.
pause


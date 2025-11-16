#!/bin/bash
# Docker Build Test Script
# 빌드 테스트 및 검증

set -e

echo "=========================================="
echo "Docker Build Test Script"
echo "=========================================="
echo ""

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# Docker Compose 확인 (v2 우선)
if docker compose version &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE_CMD="docker-compose"
else
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Desktop or Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "[1/4] Building Docker images..."
$DOCKER_COMPOSE_CMD build --no-cache
if [ $? -ne 0 ]; then
    echo "Error: Build failed"
    exit 1
fi

echo ""
echo "[2/4] Checking image sizes..."
docker images test02* --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

echo ""
echo "[3/4] Validating docker-compose configuration..."
$DOCKER_COMPOSE_CMD config
if [ $? -ne 0 ]; then
    echo "Error: Configuration validation failed"
    exit 1
fi

echo ""
echo "[4/4] Build test completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Run: ./scripts/docker-deploy.sh"
echo "  2. Or: $DOCKER_COMPOSE_CMD up -d"
echo ""


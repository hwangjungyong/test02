#!/bin/bash
# Docker 빌드 스크립트

set -e

echo "=========================================="
echo "Docker Build Script"
echo "=========================================="
echo ""

# 환경 확인
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Please install Docker: https://www.docker.com/get-started"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed"
    echo "Please install Docker Compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# 빌드 모드 선택
BUILD_MODE=${1:-production}

echo "Build mode: $BUILD_MODE"
echo ""

if [ "$BUILD_MODE" = "dev" ]; then
    echo "Building development images..."
    docker-compose -f docker-compose.dev.yml build
    echo ""
    echo "Build complete! Run with: docker-compose -f docker-compose.dev.yml up"
else
    echo "Building production images..."
    docker-compose build
    echo ""
    echo "Build complete! Run with: docker-compose up -d"
fi

echo ""
echo "=========================================="
echo "Build completed successfully!"
echo "=========================================="


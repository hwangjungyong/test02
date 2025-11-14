#!/bin/bash
# Docker 배포 스크립트

set -e

echo "=========================================="
echo "Docker Deployment Script"
echo "=========================================="
echo ""

# 환경 변수 확인
if [ ! -f .env ]; then
    echo "Warning: .env file not found"
    echo "Creating .env.example..."
    cp .env.example .env 2>/dev/null || echo "Please create .env file manually"
fi

# Docker 확인
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    exit 1
fi

# 빌드
echo "[1/3] Building Docker images..."
docker-compose build

# 중지 (이미 실행 중인 경우)
echo "[2/3] Stopping existing containers..."
docker-compose down

# 시작
echo "[3/3] Starting containers..."
docker-compose up -d

# 상태 확인
echo ""
echo "=========================================="
echo "Deployment completed!"
echo "=========================================="
echo ""
echo "Container status:"
docker-compose ps
echo ""
echo "Services:"
echo "  - Frontend: http://localhost:5173"
echo "  - Backend API: http://localhost:3001"
echo "  - Python HTTP: http://localhost:3002"
echo ""
echo "View logs: docker-compose logs -f"
echo "Stop services: docker-compose down"


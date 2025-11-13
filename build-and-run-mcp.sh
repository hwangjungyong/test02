#!/bin/bash
# 통합 MCP 서버 빌드 및 실행 스크립트 (Linux/macOS)

echo "========================================"
echo "통합 MCP 서버 빌드 및 실행"
echo "========================================"
echo ""

# Python 버전 확인
echo "[1/4] Python 버전 확인 중..."
python3 --version || python --version
if [ $? -ne 0 ]; then
    echo "오류: Python이 설치되어 있지 않습니다."
    exit 1
fi
echo ""

# 의존성 설치 확인
echo "[2/4] 의존성 확인 및 설치 중..."
if ! pip3 show mcp > /dev/null 2>&1 && ! pip show mcp > /dev/null 2>&1; then
    echo "MCP SDK가 설치되지 않았습니다. 설치 중..."
    pip3 install mcp || pip install mcp
    if [ $? -ne 0 ]; then
        echo "오류: MCP SDK 설치에 실패했습니다."
        exit 1
    fi
else
    echo "MCP SDK가 이미 설치되어 있습니다."
fi
echo ""

# 서버 파일 확인
echo "[3/4] 서버 파일 확인 중..."
if [ ! -f "mcp-unified-server.py" ]; then
    echo "오류: mcp-unified-server.py 파일을 찾을 수 없습니다."
    exit 1
fi
echo "서버 파일 확인 완료."
echo ""

# 실행 권한 부여
chmod +x mcp-unified-server.py

# 서버 실행
echo "[4/4] 통합 MCP 서버 시작 중..."
echo ""
echo "========================================"
echo "통합 MCP 서버가 실행 중입니다."
echo "종료하려면 Ctrl+C를 누르세요."
echo "========================================"
echo ""

python3 mcp-unified-server.py || python mcp-unified-server.py


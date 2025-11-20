#!/bin/bash
# 모든 MCP 서버 빌드 및 검증 스크립트 (Linux/macOS)

echo "========================================"
echo "모든 MCP 서버 빌드 및 검증"
echo "========================================"
echo ""

# Python 버전 확인
echo "[1/5] Python 설치 확인 중..."
if ! python3 --version && ! python --version; then
    echo "오류: Python이 설치되어 있지 않습니다."
    exit 1
fi
echo ""

# Node.js 버전 확인
echo "[2/5] Node.js 설치 확인 중..."
NODE_AVAILABLE=0
if command -v node &> /dev/null; then
    echo "Node.js가 설치되어 있습니다."
    NODE_AVAILABLE=1
else
    echo "경고: Node.js가 설치되어 있지 않습니다. Node.js MCP 서버는 건너뜁니다."
fi
echo ""

# Python MCP SDK 확인
echo "[3/5] Python MCP SDK 설치 확인 중..."
if ! pip3 show mcp > /dev/null 2>&1 && ! pip show mcp > /dev/null 2>&1; then
    echo "MCP SDK가 설치되어 있지 않습니다. 설치 중..."
    pip3 install mcp || pip install mcp
    if [ $? -ne 0 ]; then
        echo "오류: MCP SDK 설치에 실패했습니다."
        exit 1
    fi
else
    echo "MCP SDK가 이미 설치되어 있습니다."
fi
echo ""

# Node.js MCP SDK 확인
if [ $NODE_AVAILABLE -eq 1 ]; then
    echo "[4/5] Node.js MCP SDK 설치 확인 중..."
    if [ ! -d "node_modules/@modelcontextprotocol" ]; then
        echo "Node.js MCP SDK가 설치되어 있지 않습니다. 설치 중..."
        npm install
        if [ $? -ne 0 ]; then
            echo "경고: Node.js MCP SDK 설치에 실패했습니다. Node.js MCP 서버는 건너뜁니다."
            NODE_AVAILABLE=0
        fi
    else
        echo "Node.js MCP SDK가 이미 설치되어 있습니다."
    fi
    echo ""
else
    echo "[4/5] Node.js MCP SDK 확인 건너뜀 (Node.js 미설치)"
    echo ""
fi

# 서버 파일 확인
echo "[5/5] MCP 서버 파일 확인 중..."
echo ""

SERVER_COUNT=0
MISSING_SERVERS=""

# Python MCP Servers
if [ -f "mcp-unified-server.py" ]; then
    echo "[OK] mcp-unified-server.py 발견"
    SERVER_COUNT=$((SERVER_COUNT + 1))
else
    echo "[경고] mcp-unified-server.py를 찾을 수 없습니다."
    MISSING_SERVERS="$MISSING_SERVERS mcp-unified-server.py"
fi

if [ -f "mcp-error-log-analyzer.py" ]; then
    echo "[OK] mcp-error-log-analyzer.py 발견"
    SERVER_COUNT=$((SERVER_COUNT + 1))
else
    echo "[경고] mcp-error-log-analyzer.py를 찾을 수 없습니다."
    MISSING_SERVERS="$MISSING_SERVERS mcp-error-log-analyzer.py"
fi

if [ -f "mcp-screen-validator-server.py" ]; then
    echo "[OK] mcp-screen-validator-server.py 발견"
    SERVER_COUNT=$((SERVER_COUNT + 1))
else
    echo "[정보] mcp-screen-validator-server.py를 찾을 수 없습니다 (선택사항)."
fi

if [ -f "mcp-screen-validator-http-server.py" ]; then
    echo "[OK] mcp-screen-validator-http-server.py 발견"
    SERVER_COUNT=$((SERVER_COUNT + 1))
else
    echo "[정보] mcp-screen-validator-http-server.py를 찾을 수 없습니다 (선택사항)."
fi

if [ -f "mcp-book-server.py" ]; then
    echo "[OK] mcp-book-server.py 발견"
    SERVER_COUNT=$((SERVER_COUNT + 1))
else
    echo "[정보] mcp-book-server.py를 찾을 수 없습니다 (선택사항)."
fi

# Node.js MCP Server
if [ $NODE_AVAILABLE -eq 1 ]; then
    if [ -f "mcp-server.js" ]; then
        echo "[OK] mcp-server.js 발견"
        SERVER_COUNT=$((SERVER_COUNT + 1))
    else
        echo "[경고] mcp-server.js를 찾을 수 없습니다."
        MISSING_SERVERS="$MISSING_SERVERS mcp-server.js"
    fi
else
    echo "[정보] mcp-server.js 확인 건너뜀 (Node.js 미설치)"
fi

echo ""
echo "========================================"
echo "빌드 요약"
echo "========================================"
echo "발견된 서버: ${SERVER_COUNT}개"

if [ -n "$MISSING_SERVERS" ]; then
    echo ""
    echo "누락된 필수 서버:"
    echo "$MISSING_SERVERS"
    echo ""
    read -p "계속하시겠습니까? (Y/N): " CONTINUE
    if [ "$CONTINUE" != "Y" ] && [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
fi

echo ""
echo "========================================"
echo "MCP 서버 파일 검증 완료"
echo "========================================"
echo ""
echo "다음 단계:"
echo "1. cursor-mcp-config.json 파일이 올바르게 설정되어 있는지 확인하세요."
echo "2. Cursor AI를 재시작하여 MCP 서버를 로드하세요."
echo ""
echo "개별 서버를 실행하려면:"
echo "- Python 서버: python3 mcp-서버명.py"
echo "- Node.js 서버: node mcp-server.js"
echo ""


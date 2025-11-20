@echo off
chcp 949 >nul 2>&1
REM 모든 MCP 서버 빌드 및 검증 스크립트

echo ========================================
echo 모든 MCP 서버 빌드 및 검증
echo ========================================
echo.

REM Check Python Installation
echo [1/5] Python 설치 확인 중...
python --version
if errorlevel 1 (
    echo 오류: Python이 설치되어 있지 않거나 PATH에 없습니다.
    pause
    exit /b 1
)
echo.

REM Check Node.js Installation
echo [2/5] Node.js 설치 확인 중...
node --version >nul 2>&1
if errorlevel 1 (
    echo 경고: Node.js가 설치되어 있지 않습니다. Node.js MCP 서버는 건너뜁니다.
    set NODE_AVAILABLE=0
) else (
    echo Node.js가 설치되어 있습니다.
    set NODE_AVAILABLE=1
)
echo.

REM Check MCP SDK Installation (Python)
echo [3/5] Python MCP SDK 설치 확인 중...
pip show mcp >nul 2>&1
if errorlevel 1 (
    echo MCP SDK가 설치되어 있지 않습니다. 설치 중...
    pip install mcp
    if errorlevel 1 (
        echo 오류: MCP SDK 설치에 실패했습니다.
        pause
        exit /b 1
    )
) else (
    echo MCP SDK가 이미 설치되어 있습니다.
)
echo.

REM Check Node.js MCP SDK
if %NODE_AVAILABLE%==1 (
    echo [4/5] Node.js MCP SDK 설치 확인 중...
    if not exist "node_modules\@modelcontextprotocol" (
        echo Node.js MCP SDK가 설치되어 있지 않습니다. 설치 중...
        call npm install
        if errorlevel 1 (
            echo 경고: Node.js MCP SDK 설치에 실패했습니다. Node.js MCP 서버는 건너뜁니다.
            set NODE_AVAILABLE=0
        )
    ) else (
        echo Node.js MCP SDK가 이미 설치되어 있습니다.
    )
    echo.
) else (
    echo [4/5] Node.js MCP SDK 확인 건너뜀 (Node.js 미설치)
    echo.
)

REM Check Server Files
echo [5/5] MCP 서버 파일 확인 중...
echo.

set SERVER_COUNT=0
set MISSING_SERVERS=

REM Python MCP Servers
if exist "mcp-unified-server.py" (
    echo [OK] mcp-unified-server.py 발견
    set /a SERVER_COUNT+=1
) else (
    echo [경고] mcp-unified-server.py를 찾을 수 없습니다.
    set MISSING_SERVERS=%MISSING_SERVERS% mcp-unified-server.py
)

if exist "mcp-error-log-analyzer.py" (
    echo [OK] mcp-error-log-analyzer.py 발견
    set /a SERVER_COUNT+=1
) else (
    echo [경고] mcp-error-log-analyzer.py를 찾을 수 없습니다.
    set MISSING_SERVERS=%MISSING_SERVERS% mcp-error-log-analyzer.py
)

if exist "mcp-screen-validator-server.py" (
    echo [OK] mcp-screen-validator-server.py 발견
    set /a SERVER_COUNT+=1
) else (
    echo [정보] mcp-screen-validator-server.py를 찾을 수 없습니다 (선택사항).
)

if exist "mcp-screen-validator-http-server.py" (
    echo [OK] mcp-screen-validator-http-server.py 발견
    set /a SERVER_COUNT+=1
) else (
    echo [정보] mcp-screen-validator-http-server.py를 찾을 수 없습니다 (선택사항).
)

if exist "mcp-book-server.py" (
    echo [OK] mcp-book-server.py 발견
    set /a SERVER_COUNT+=1
) else (
    echo [정보] mcp-book-server.py를 찾을 수 없습니다 (선택사항).
)

REM Node.js MCP Server
if %NODE_AVAILABLE%==1 (
    if exist "mcp-server.js" (
        echo [OK] mcp-server.js 발견
        set /a SERVER_COUNT+=1
    ) else (
        echo [경고] mcp-server.js를 찾을 수 없습니다.
        set MISSING_SERVERS=%MISSING_SERVERS% mcp-server.js
    )
) else (
    echo [정보] mcp-server.js 확인 건너뜀 (Node.js 미설치)
)

echo.
echo ========================================
echo 빌드 요약
echo ========================================
echo 발견된 서버: %SERVER_COUNT%개

if not "%MISSING_SERVERS%"=="" (
    echo.
    echo 누락된 필수 서버:
    echo %MISSING_SERVERS%
    echo.
    echo 계속하시겠습니까? (Y/N)
    set /p CONTINUE=
    if /i not "%CONTINUE%"=="Y" (
        exit /b 1
    )
)

echo.
echo ========================================
echo MCP 서버 파일 검증 완료
echo ========================================
echo.
echo 다음 단계:
echo 1. cursor-mcp-config.json 파일이 올바르게 설정되어 있는지 확인하세요.
echo 2. Cursor AI를 재시작하여 MCP 서버를 로드하세요.
echo.
echo 개별 서버를 실행하려면:
echo - Python 서버: python mcp-서버명.py
echo - Node.js 서버: node mcp-server.js
echo.

pause


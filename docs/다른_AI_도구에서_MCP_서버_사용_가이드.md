# 🤖 다른 AI 도구에서 MCP 서버 사용 가이드

**작성일**: 2025년 1월  
**목적**: Cursor AI 외의 다른 AI 도구(AIPRO, Claude Desktop 등)에서 프로젝트의 MCP 서버를 사용하는 방법

---

## 📋 목차

1. [MCP 서버란?](#mcp-서버란)
2. [사전 요구사항](#사전-요구사항)
3. [각 AI 도구별 설정 방법](#각-ai-도구별-설정-방법)
4. [설정 확인 및 테스트](#설정-확인-및-테스트)
5. [문제 해결](#문제-해결)

---

## 🤖 MCP 서버란?

**MCP (Model Context Protocol)**는 AI 도구가 외부 도구와 서비스를 사용할 수 있게 해주는 표준 프로토콜입니다.

### 간단한 비유

```
일반적인 상황:
👤 사용자: "5와 7을 더해줘"
🤖 AI: "음... 계산기를 사용할 수 없어서 모르겠어요"

MCP 서버가 있는 상황:
👤 사용자: "5와 7을 더해줘"
🤖 AI: "MCP 서버를 사용해서 계산해드릴게요!"
📡 MCP 서버: "5 + 7 = 12"
🤖 AI: "답은 12입니다!"
```

**MCP 서버는 AI의 손과 발**이라고 생각하면 됩니다!

---

## 📦 사전 요구사항

### 1. 프로젝트 파일 확인

프로젝트에 다음 MCP 서버 파일들이 있어야 합니다:

**Python MCP 서버:**
- `mcp-unified-server.py` - 도서 추천, 계산기
- `mcp-error-log-analyzer.py` - 에러 로그 분석
- `mcp-sql-query-analyzer.py` - SQL 쿼리 분석
- `mcp-impact-analyzer.py` - 영향도 분석
- `mcp-voc-server.py` - VOC 자동 대응

**Node.js MCP 서버:**
- `mcp-server.js` - AI 뉴스 검색, 라디오 음악 정보

### 2. 의존성 설치

**Python 패키지:**
```bash
pip install mcp sqlparse
```

또는:
```bash
pip install -r requirements.txt
```

**Node.js 패키지:**
```bash
npm install
```

### 3. 프로젝트 경로 확인

현재 프로젝트 경로를 확인하세요:
- Windows: `C:\test\test02`
- Linux/macOS: `/path/to/test02`

설정 파일에서 이 경로를 사용합니다.

---

## 🔧 각 AI 도구별 설정 방법

### 1️⃣ Cursor AI (기본 설정)

**설정 파일 위치:**
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- 또는 프로젝트 루트의 `cursor-mcp-config.json`

**설정 파일 내용:**
```json
{
  "mcpServers": {
    "ai-articles-radio-server": {
      "command": "node",
      "args": ["C:/test/test02/mcp-server.js"],
      "cwd": "C:/test/test02",
      "description": "AI 기사 검색 및 라디오 방송 음악 정보 서버"
    },
    "unified-mcp-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-unified-server.py"],
      "cwd": "C:/test/test02",
      "description": "덧셈 계산기 및 도서 검색/추천 통합 서버"
    },
    "error-log-analyzer": {
      "command": "python",
      "args": ["C:/test/test02/mcp-error-log-analyzer.py"],
      "cwd": "C:/test/test02",
      "description": "에러 로그 자동 분석 서버"
    },
    "sql-query-analyzer": {
      "command": "python",
      "args": ["C:/test/test02/mcp-sql-query-analyzer.py"],
      "cwd": "C:/test/test02",
      "description": "SQL 쿼리 자동 분석 서버"
    },
    "voc-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-voc-server.py"],
      "cwd": "C:/test/test02",
      "description": "VOC 자동 대응 MCP 서버"
    }
  }
}
```

**경로 수정:**
- `C:/test/test02`를 실제 프로젝트 경로로 변경하세요
- Linux/macOS: `/path/to/test02` 형식 사용

---

### 2️⃣ AIPRO

**AIPRO는 MCP 프로토콜을 지원하는 AI 도구입니다.**

#### 설정 방법

**1단계: 설정 파일 찾기**

AIPRO의 설정 파일 위치를 확인하세요:
- Windows: `%APPDATA%\AIPRO\config.json`
- macOS: `~/Library/Application Support/AIPRO/config.json`
- Linux: `~/.config/AIPRO/config.json`

**2단계: MCP 서버 설정 추가**

설정 파일에 다음 내용을 추가하세요:

```json
{
  "mcp": {
    "servers": {
      "ai-articles-radio-server": {
        "command": "node",
        "args": ["C:/test/test02/mcp-server.js"],
        "cwd": "C:/test/test02"
      },
      "unified-mcp-server": {
        "command": "python",
        "args": ["C:/test/test02/mcp-unified-server.py"],
        "cwd": "C:/test/test02"
      },
      "error-log-analyzer": {
        "command": "python",
        "args": ["C:/test/test02/mcp-error-log-analyzer.py"],
        "cwd": "C:/test/test02"
      },
      "sql-query-analyzer": {
        "command": "python",
        "args": ["C:/test/test02/mcp-sql-query-analyzer.py"],
        "cwd": "C:/test/test02"
      },
      "voc-server": {
        "command": "python",
        "args": ["C:/test/test02/mcp-voc-server.py"],
        "cwd": "C:/test/test02"
      }
    }
  }
}
```

**3단계: AIPRO 재시작**

설정을 적용하려면 AIPRO를 완전히 종료하고 다시 시작하세요.

---

### 3️⃣ Claude Desktop (Anthropic)

**Claude Desktop은 공식적으로 MCP를 지원합니다.**

#### 설정 방법

**1단계: 설정 파일 찾기**

Claude Desktop의 설정 파일 위치:
- Windows: `%APPDATA%\Claude\claude_desktop_config.json`
- macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Linux: `~/.config/Claude/claude_desktop_config.json`

**2단계: MCP 서버 설정 추가**

설정 파일에 다음 내용을 추가하세요:

```json
{
  "mcpServers": {
    "ai-articles-radio-server": {
      "command": "node",
      "args": ["C:/test/test02/mcp-server.js"],
      "cwd": "C:/test/test02"
    },
    "unified-mcp-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-unified-server.py"],
      "cwd": "C:/test/test02"
    },
    "error-log-analyzer": {
      "command": "python",
      "args": ["C:/test/test02/mcp-error-log-analyzer.py"],
      "cwd": "C:/test/test02"
    },
    "sql-query-analyzer": {
      "command": "python",
      "args": ["C:/test/test02/mcp-sql-query-analyzer.py"],
      "cwd": "C:/test/test02"
    },
    "voc-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-voc-server.py"],
      "cwd": "C:/test/test02"
    }
  }
}
```

**3단계: Claude Desktop 재시작**

설정을 적용하려면 Claude Desktop을 완전히 종료하고 다시 시작하세요.

---

### 4️⃣ 기타 MCP 지원 도구

MCP 프로토콜을 지원하는 다른 AI 도구들도 비슷한 방식으로 설정할 수 있습니다.

#### 일반적인 설정 형식

대부분의 MCP 지원 도구는 다음과 같은 형식을 사용합니다:

```json
{
  "mcpServers": {
    "서버이름": {
      "command": "실행명령어",
      "args": ["인자1", "인자2"],
      "cwd": "작업디렉토리"
    }
  }
}
```

#### 주요 설정 항목 설명

- **command**: MCP 서버를 실행할 명령어 (`python`, `node` 등)
- **args**: 명령어에 전달할 인자 (MCP 서버 파일 경로)
- **cwd**: 작업 디렉토리 (프로젝트 루트 경로)

---

## ✅ 설정 확인 및 테스트

### 1. MCP 서버 직접 실행 테스트

설정 전에 MCP 서버가 정상적으로 실행되는지 확인하세요:

**Python 서버 테스트:**
```bash
python mcp-unified-server.py
```

**Node.js 서버 테스트:**
```bash
node mcp-server.js
```

정상적으로 실행되면 아무 출력 없이 대기 상태가 됩니다 (stdio 통신).

### 2. AI 도구에서 테스트

설정 후 AI 도구에서 다음 명령어로 테스트하세요:

**덧셈 계산기 테스트:**
```
"5와 7을 더해줘"
```

**도서 추천 테스트:**
```
"인공지능 관련 책을 추천해줘"
```

**SQL 쿼리 분석 테스트:**
```
"queries/complex_query.sql 파일의 SQL 쿼리를 분석해줘"
```

**에러 로그 분석 테스트:**
```
"logs/sample-error.log 파일의 에러를 분석해줘"
```

### 3. 로그 확인

AI 도구에서 MCP 서버 연결 오류가 발생하면:
- AI 도구의 로그 파일 확인
- MCP 서버 파일의 경로가 정확한지 확인
- Python/Node.js가 올바르게 설치되어 있는지 확인

---

## 🔍 문제 해결

### 문제 1: "MCP 서버를 찾을 수 없습니다"

**원인:** 설정 파일의 경로가 잘못되었습니다.

**해결 방법:**
1. 프로젝트 경로 확인
2. 설정 파일의 `args`와 `cwd` 경로 수정
3. Windows: 백슬래시(`\`) 대신 슬래시(`/`) 사용 권장
4. 경로에 공백이 있으면 따옴표로 감싸기

**예시:**
```json
{
  "args": ["C:/Users/My Name/test02/mcp-server.js"],  // ❌ 공백 있음
  "args": ["\"C:/Users/My Name/test02/mcp-server.js\""]  // ✅ 따옴표로 감싸기
}
```

---

### 문제 2: "Python을 찾을 수 없습니다" 또는 "Node를 찾을 수 없습니다"

**원인:** Python 또는 Node.js가 설치되지 않았거나 PATH에 등록되지 않았습니다.

**해결 방법:**

**Python 확인:**
```bash
python --version
# 또는
python3 --version
```

**Node.js 확인:**
```bash
node --version
```

설치되어 있지 않다면:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/

**전체 경로 사용:**
설정 파일에서 전체 경로를 사용할 수도 있습니다:

```json
{
  "command": "C:/Python312/python.exe",  // Windows
  "command": "/usr/bin/python3",  // Linux/macOS
}
```

---

### 문제 3: "의존성 패키지를 찾을 수 없습니다"

**원인:** 필요한 Python 패키지가 설치되지 않았습니다.

**해결 방법:**
```bash
pip install mcp sqlparse
# 또는
pip install -r requirements.txt
```

---

### 문제 4: "권한 오류" 또는 "접근 거부"

**원인:** 파일 또는 디렉토리에 대한 접근 권한이 없습니다.

**해결 방법:**
- Windows: 관리자 권한으로 AI 도구 실행
- Linux/macOS: 파일 권한 확인 및 수정

```bash
chmod +x mcp-unified-server.py
chmod +x mcp-server.js
```

---

### 문제 5: AI 도구가 MCP 서버를 인식하지 못함

**원인:** 설정 파일 형식이 잘못되었거나 AI 도구를 재시작하지 않았습니다.

**해결 방법:**
1. 설정 파일의 JSON 형식 확인 (JSON 유효성 검사)
2. AI 도구를 완전히 종료하고 다시 시작
3. AI 도구의 로그 파일에서 오류 메시지 확인

---

## 📝 경로 변환 가이드

### Windows 경로 → Linux/macOS 경로

**Windows:**
```json
{
  "args": ["C:/test/test02/mcp-server.js"],
  "cwd": "C:/test/test02"
}
```

**Linux/macOS:**
```json
{
  "args": ["/home/user/test02/mcp-server.js"],
  "cwd": "/home/user/test02"
}
```

### 상대 경로 사용

일부 AI 도구는 상대 경로를 지원합니다:

```json
{
  "args": ["./mcp-server.js"],
  "cwd": "."
}
```

---

## 🎯 요약

**다른 AI 도구에서 MCP 서버 사용하기:**

1. ✅ 프로젝트 파일 확인
2. ✅ 의존성 설치 (`pip install mcp sqlparse`, `npm install`)
3. ✅ AI 도구의 설정 파일 찾기
4. ✅ MCP 서버 설정 추가 (경로 수정 필수!)
5. ✅ AI 도구 재시작
6. ✅ 테스트 명령어로 확인

**주요 포인트:**
- 설정 파일의 경로를 실제 프로젝트 경로로 수정해야 합니다
- Windows는 슬래시(`/`) 사용 권장
- AI 도구를 재시작해야 설정이 적용됩니다
- MCP 서버가 정상 실행되는지 먼저 확인하세요

---

## 📚 관련 문서

- [`MCP_서버_완전_가이드.md`](../MCP_서버_완전_가이드.md) - MCP 서버 상세 가이드
- [`docs/에러_로그_분석_MCP_서버_가이드.md`](./에러_로그_분석_MCP_서버_가이드.md) - 에러 로그 분석 서버 가이드
- [`docs/SQL_쿼리_분석_MCP_서버_가이드.md`](./SQL_쿼리_분석_MCP_서버_가이드.md) - SQL 쿼리 분석 서버 가이드
- [`docs/VOC_자동_대응_MCP_서버_가이드.md`](./VOC_자동_대응_MCP_서버_가이드.md) - VOC 자동 대응 서버 가이드

---

**마지막 업데이트**: 2025년 1월


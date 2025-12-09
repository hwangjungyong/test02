# 🔍 AI 에러 로그 분석 MCP 서버 가이드

**작성일**: 2025년 12월  
**버전**: 2.0.0  
**서버명**: AI Error Log Analyzer MCP Server  
**대상**: 개발자 및 기술 담당자

> 워크스페이스의 에러 로그를 자동으로 분석하고, 각 에러별로 개별 해결방안과 재발 방지책을 제안하는 지능형 MCP 서버

> **📖 사용자/관리자 메뉴얼**: 웹 UI 사용법이 필요하시면 [`AI_에러로그분석_사용자_메뉴얼.md`](./AI_에러로그분석_사용자_메뉴얼.md)를 참조하세요.

---

## 📋 목차

1. [서버 개요](#서버-개요)
2. [주요 기능](#주요-기능)
3. [시스템 아키텍처](#시스템-아키텍처)
4. [설치 및 설정](#설치-및-설정)
5. [사용 방법](#사용-방법)
6. [데이터 구조](#데이터-구조)
7. [MCP 서버 등록 및 사용 가이드](#mcp-서버-등록-및-사용-가이드)
8. [실제 사용 예시](#실제-사용-예시)
9. [API 연동](#api-연동)
10. [문제 해결](#문제-해결)

---

## 서버 개요

### 🎯 서버 소개

**AI 에러 로그 분석 MCP 서버**는 개발자가 작성한 코드의 에러 로그를 자동으로 분석하고, 각 에러마다 개별적인 해결방안과 재발 방지책을 제안하는 지능형 분석 도구입니다.

### ✨ 핵심 기능

- **자동화**: 수동으로 로그를 분석할 필요 없이 자동으로 에러를 감지하고 분류
- **지능형 분석**: 각 에러의 타입, 심각도, 영향도를 자동으로 분석
- **개별 해결방안**: 각 에러마다 맞춤형 해결방안과 단계별 가이드 제공
- **재발 방지**: 에러 타입별 재발 방지 전략 제안
- **발생일자별 그룹화**: 에러를 발생일자별로 그룹화하여 추적 용이

### 🎁 제공 데이터

각 에러 분석 시 다음 정보를 제공합니다:

1. **에러 기본 정보**
   - 발생일시 (타임스탬프)
   - 심각도 (ERROR, WARNING, CRITICAL)
   - 에러 타입 (Database, Network, Authentication 등)
   - 에러 카테고리
   - 영향도 (HIGH, MEDIUM, LOW)

2. **에러 상세 정보**
   - 에러 메시지
   - 발생 위치 (파일 경로, 라인 번호)
   - 관련 프로그램/서비스
   - 스택 트레이스 (있는 경우)

3. **분석 결과**
   - 원인 분석 (Root Cause)
   - 해결방안 (Solutions) - 각 에러별 개별 제공
   - 재발 방지책 (Prevention Strategies)

---

## 주요 기능

### 1. 🚀 자동 로그 파일 검색

워크스페이스에서 다음 위치에서 로그 파일을 자동으로 찾습니다:

- `logs/` 디렉토리
- `log/` 디렉토리
- `var/log/` 디렉토리
- `tmp/` 디렉토리
- 루트 디렉토리의 `*.log`, `*.err`, `*.error` 파일

### 2. 🧠 지능형 로그 파싱

#### 지원하는 로그 형식

- **GCP Cloud Logging** 형식
- **ISO8601** 형식 (`2024-01-15T10:30:45.123Z`)
- **Standard** 형식 (`2024-01-15 10:30:45`)
- **Simple** 형식 (`01/15/2024 10:30:45`)
- **대괄호 형식** (`[2024-01-15 11:00:15]`)

#### 자동 감지 기능

- 로그 형식 자동 감지 및 파싱
- 여러 줄에 걸친 스택 트레이스 처리
- 빈 줄 기준 에러 블록 분리
- 타임스탬프별 에러 분리

### 3. 📊 에러 타입 자동 분류

다음과 같은 에러 타입을 자동으로 분류합니다:

| 에러 타입 | 키워드 예시 | 설명 |
|---------|-----------|------|
| **Database Error** | database, connection, sql, query, mysql, postgresql, mongodb | 데이터베이스 관련 오류 |
| **Network Error** | network, timeout, refused, socket, dns | 네트워크 관련 오류 |
| **Authentication Error** | auth, unauthorized, token, credential, jwt, session | 인증/권한 관련 오류 |
| **Memory Error** | memory, out of memory, oom, heap, memory leak | 메모리 관련 오류 |
| **File System Error** | file, not found, permission denied, disk space | 파일 관련 오류 |
| **Syntax Error** | syntax, parse, invalid, unexpected token | 문법/파싱 오류 |
| **Performance Error** | cpu, overload, load average | 성능 관련 오류 |
| **Service Error** | redis, rabbitmq, elasticsearch, cache | 외부 서비스 오류 |
| **SSL Error** | ssl, certificate, tls | SSL/TLS 관련 오류 |
| **Configuration Error** | environment, env, missing | 설정 관련 오류 |

### 4. 💡 개별 해결방안 생성

**각 에러마다 개별적인 해결방안을 생성합니다:**

- **우선순위별 해결방안**: 가장 효과적인 해결방법부터 제시
- **단계별 가이드**: 구체적인 실행 단계 제공
- **코드 예시**: 실제 구현 가능한 코드 예시 포함
- **에러 타입별 맞춤**: 에러 타입에 따라 최적화된 해결방안

### 5. 🛡️ 재발 방지책 제안

각 에러 타입에 맞는 재발 방지 전략을 제안합니다:

- **구현 예시**: 재발 방지를 위한 코드 구현 예시
- **기대 효과**: 각 전략의 효과 설명
- **모니터링 방법**: 지속적인 모니터링 방법 제안

### 6. 📅 발생일자별 그룹화

- 에러를 발생일자(`timestamp`)별로 자동 그룹화
- 같은 날 발생한 에러들을 한눈에 확인 가능
- 시간순 정렬로 최신 에러부터 확인

### 7. 💾 데이터베이스 저장

- 각 에러를 별도의 데이터베이스 row로 저장
- 발생일시(`occurred_at`) 기준으로 조회 및 그룹화 가능
- 해결방안과 재발 방지책도 함께 저장

---

## 시스템 아키텍처

### 구동 방식

```
┌─────────────────┐
│   Cursor AI     │
│  (MCP Client)   │
└────────┬────────┘
         │ MCP Protocol
         │ (stdin/stdout)
         ▼
┌─────────────────┐
│  MCP Server     │
│ (Python Script) │
└────────┬────────┘
         │
         ├──► LogParser (로그 파싱)
         │    ├── GCP 로그 파싱
         │    ├── 일반 로그 파싱
         │    └── 에러 분리 및 분류
         │
         ├──► ErrorAnalyzer (에러 분석)
         │    ├── 에러 타입 분류
         │    ├── 해결방안 생성
         │    └── 재발 방지책 생성
         │
         └──► Database (저장)
              ├── 각 에러별 개별 저장
              └── 발생일자별 그룹화
```

### 데이터 흐름

1. **로그 입력**
   - 워크스페이스에서 로그 파일 자동 검색
   - 또는 직접 로그 내용 입력

2. **파싱 및 분리**
   - 로그 형식 자동 감지
   - 각 에러를 개별 객체로 분리
   - 타임스탬프, 심각도, 메시지 추출

3. **분석 및 분류**
   - 에러 타입 자동 분류
   - 영향도 분석
   - 각 에러별 해결방안 생성

4. **저장 및 반환**
   - 각 에러를 데이터베이스에 개별 저장
   - 발생일자별 그룹화 정보 포함
   - 분석 결과 반환

---

## 설치 및 설정

### 1. 시스템 요구사항

- **Python**: 3.8 이상
- **운영체제**: Windows, macOS, Linux
- **의존성**: MCP SDK

### 2. 의존성 설치

```bash
pip install mcp
```

또는 `requirements.txt`가 있는 경우:

```bash
pip install -r requirements.txt
```

### 3. 파일 확인

다음 파일이 프로젝트 루트에 있는지 확인:

- `mcp-error-log-analyzer.py` - MCP 서버 메인 파일

### 4. ⚠️ VDI 환경에서의 자동 실행 주의사항

**VDI 재부팅 시 자동 실행이 설정되어 있는 경우:**

- ✅ **자동 실행이 활성화되어 있으면 `start-dev.bat`를 수동으로 실행할 필요가 없습니다**
- ✅ `auto-start-servers.bat`가 이미 서버를 시작하고 있습니다
- ✅ 두 스크립트 모두 포트 체크를 하므로 중복 실행은 방지되지만, 불필요한 실행은 피하는 것이 좋습니다

**확인 방법:**

1. **자동 실행이 활성화되어 있는지 확인**
   - Windows 시작 프로그램 폴더 (`Win + R → shell:startup`)에서 `Auto-Start-Servers.lnk` 파일 확인

2. **서버가 이미 실행 중인지 확인**
   ```bash
   netstat -ano | findstr ":3001 :3002 :5173"
   ```

3. **서버가 실행 중이면 `start-dev.bat` 실행 불필요**
   - 자동 실행이 정상 작동 중이면 별도로 `start-dev.bat`를 실행할 필요가 없습니다
   - 서버가 실행 중이지 않은 경우에만 `start-dev.bat`를 실행하세요

**권장 사항:**

- VDI 환경에서는 `install-auto-start.bat`를 한 번만 실행하여 자동 실행을 설정하세요
- 재부팅 후 서버가 자동으로 시작되므로 `start-dev.bat`를 수동으로 실행할 필요가 없습니다
- 서버 상태를 확인하려면 포트 체크 명령어를 사용하세요

자세한 내용은 [`자동_실행_가이드.md`](./자동_실행_가이드.md)를 참조하세요.

---

## 사용 방법

### 방법 1: Cursor AI에서 직접 사용 (MCP 서버)

Cursor AI 채팅에서 자연어로 요청:

```
"워크스페이스의 에러 로그를 분석해줘"
```

또는:

```
"이 로그 파일을 분석해줘: logs/error.log"
```

### 방법 2: API 서버를 통한 사용

HTTP POST 요청으로 에러 로그 분석:

```bash
curl -X POST http://localhost:3001/api/error-log/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "log_content": "2024-01-15T10:30:45.123Z ERROR Database connection failed"
  }'
```

### 방법 3: Python 스크립트 직접 실행

```bash
python mcp-error-log-analyzer.py --log-file logs/error.log --workspace C:/test/test02
```

또는 로그 내용 직접 입력:

```bash
python mcp-error-log-analyzer.py --log-content "2024-01-15T10:30:45.123Z ERROR Database connection failed"
```

---

## 데이터 구조

### 입력 데이터

#### 로그 파일 형식 예시

```
2024-01-15T10:30:45.123Z ERROR Database connection failed: Connection timeout after 30 seconds
2024-01-15T10:31:12.456Z ERROR Network timeout occurred while connecting to external API

[2024-01-15 11:00:15] ERROR: Node.js Express Application Error
TypeError: Cannot read property 'id' of undefined
    at /app/routes/users.js:45:12
    at async Promise.all (index 0)
```

### 출력 데이터

#### 각 에러별 데이터 구조

```json
{
  "index": 1,
  "log_content": "2024-01-15T10:30:45.123Z ERROR Database connection failed...",
  "timestamp": "2024-01-15T10:30:45.123Z",
  "log_type": "iso8601",
  "system_type": "iso8601",
  "error_type": "Database Error",
  "error_category": "Database",
  "severity": "ERROR",
  "impact_level": "HIGH",
  "parsed_data": {
    "error_type": "Database Error",
    "error_category": "Database",
    "severity": "ERROR",
    "impact_level": "HIGH",
    "solutions": [
      {
        "priority": 1,
        "title": "데이터베이스 연결 상태 확인",
        "description": "데이터베이스 서버가 실행 중인지 확인합니다.",
        "steps": [
          "서버 프로세스 확인",
          "포트 리스닝 확인",
          "서버 로그 확인"
        ],
        "code_example": "async function checkDbHealth() { ... }"
      }
    ],
    "prevention": [
      {
        "title": "연결 풀링 구현",
        "description": "데이터베이스 연결을 재사용하여 성능을 최적화합니다.",
        "implementation": "const pool = new Pool({ ... });",
        "benefits": ["연결 재사용", "성능 향상"]
      }
    ],
    "root_cause": "데이터베이스 연결에 실패했습니다. 데이터베이스 서버가 응답하지 않거나 네트워크 지연이 발생했습니다.",
    "occurred_at": "2024-01-15T10:30:45.123Z"
  },
  "metadata": {
    "total_errors": 10,
    "occurred_at": "2024-01-15T10:30:45.123Z"
  },
  "analysis": {
    "error_type": "database",
    "matched_keywords": ["database", "connection"],
    "solutions": [...],
    "prevention": [...]
  }
}
```

### 데이터베이스 저장 구조

각 에러는 다음 테이블에 저장됩니다:

#### `error_logs` 테이블

- `id`: 고유 ID
- `log_content`: 에러 로그 내용
- `log_type`: 로그 타입
- `parsed_data`: 파싱된 데이터 (JSON)
- `system_type`: 시스템 타입
- `severity`: 심각도
- `error_type`: 에러 타입
- `error_category`: 에러 카테고리
- `timestamp`: 발생일시
- `created_at`: 저장일시
- `updated_at`: 수정일시

#### `error_log_metadata` 테이블

- `id`: 고유 ID
- `error_log_id`: 에러 로그 ID (외래키)
- `error_type`: 에러 타입
- `error_category`: 에러 카테고리
- `impact_level`: 영향도
- `occurred_at`: 발생일시
- `analysis_data`: 분석 데이터 (JSON) - 해결방안, 재발 방지책 포함

---

## MCP 서버 등록 및 사용 가이드

### 1. Cursor AI에 MCP 서버 등록

#### 설정 파일 위치

**Windows:**
```
%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
```

또는 프로젝트 루트의 `cursor-mcp-config.json` 파일 사용

#### 설정 파일 내용

`cursor-mcp-config.json` 파일에 다음 내용 추가:

```json
{
  "mcpServers": {
    "error-log-analyzer": {
      "command": "python",
      "args": ["C:/test/test02/mcp-error-log-analyzer.py"],
      "cwd": "C:/test/test02",
      "description": "에러 로그 자동 분석 서버 - GCP 및 일반 로그 분석, 조치 방법 및 재발 방지책 제안",
      "tools": [
        "analyze_error_logs"
      ]
    }
  }
}
```

**경로 수정:**
- `C:/test/test02`를 실제 프로젝트 경로로 변경
- Linux/macOS: `/path/to/project` 형식 사용

#### 설정 적용

1. Cursor AI 완전 종료
2. 설정 파일 저장
3. Cursor AI 재시작
4. MCP 서버 자동 로드 확인

### 2. Claude Desktop에 등록

#### 설정 파일 위치

**Windows:**
```
%APPDATA%\Claude\claude_desktop_config.json
```

**macOS:**
```
~/Library/Application Support/Claude/claude_desktop_config.json
```

**Linux:**
```
~/.config/Claude/claude_desktop_config.json
```

#### 설정 파일 내용

```json
{
  "mcpServers": {
    "error-log-analyzer": {
      "command": "python",
      "args": ["C:/test/test02/mcp-error-log-analyzer.py"],
      "cwd": "C:/test/test02"
    }
  }
}
```

### 3. 사용 방법

#### Cursor AI에서 사용

Cursor AI 채팅에서 자연어로 요청:

```
"워크스페이스의 에러 로그를 분석해줘"
```

또는:

```
"logs 폴더의 에러 로그를 분석하고 각 에러별 해결방안을 제시해줘"
```

#### Claude Desktop에서 사용

Claude Desktop 채팅에서:

```
"에러 로그를 분석해줘"
```

### 4. MCP 도구 확인

MCP 서버가 정상적으로 등록되었는지 확인:

1. Cursor AI 설정에서 MCP 서버 목록 확인
2. 도구 목록에 `analyze_error_logs`가 있는지 확인
3. 채팅에서 에러 로그 분석 요청 시 자동으로 도구 호출되는지 확인

---

## 실제 사용 예시

### 예시 1: 워크스페이스 로그 자동 분석

**요청:**
```
"워크스페이스의 에러 로그를 분석해줘"
```

**처리 과정:**
1. 워크스페이스에서 로그 파일 자동 검색
2. 각 로그 파일 파싱
3. 에러 분리 및 분류
4. 각 에러별 해결방안 생성
5. 결과 반환

**결과:**
- 총 10개의 에러 발견
- 각 에러별 개별 해결방안 제공
- 발생일자별 그룹화 정보 제공

### 예시 2: 특정 로그 파일 분석

**요청:**
```
"logs/sample-error.log 파일을 분석해줘"
```

**처리 과정:**
1. 지정된 로그 파일 읽기
2. 로그 형식 자동 감지
3. 각 에러 분리
4. 개별 분석 및 해결방안 생성

**결과:**
- 파일에서 10개의 에러 발견
- 각 에러의 타입, 심각도, 영향도 분석
- 에러별 맞춤형 해결방안 제공

### 예시 3: 직접 입력된 로그 분석

**요청:**
```
"이 에러를 분석해줘:
2024-01-15T10:30:45.123Z ERROR Database connection failed: Connection timeout after 30 seconds"
```

**처리 과정:**
1. 입력된 로그 내용 파싱
2. 에러 타입 분류 (Database Error)
3. 해결방안 생성
4. 결과 반환

**결과:**
- 에러 타입: Database Error
- 영향도: HIGH
- 해결방안: 데이터베이스 연결 상태 확인, 타임아웃 설정 조정 등

---

## API 연동

### API 엔드포인트

#### 1. 에러 로그 분석

**엔드포인트:** `POST /api/error-log/analyze`

**요청 본문:**
```json
{
  "log_file_path": "logs/error.log",
  "log_content": "2024-01-15T10:30:45.123Z ERROR Database connection failed",
  "workspace_path": "C:/test/test02"
}
```

**응답:**
```json
{
  "success": true,
  "result": {
    "log_type": "iso8601",
    "system_type": "iso8601",
    "error_type": "Database Error",
    "error_category": "Database",
    "severity": "ERROR",
    "summary": "총 10개의 에러가 발견되었습니다.",
    "root_cause": "데이터베이스 연결에 실패했습니다...",
    "solutions": [...],
    "metadata": {
      "total_errors": 10,
      "all_errors": [...]
    }
  }
}
```

#### 2. 에러 로그 저장

**엔드포인트:** `POST /api/error-log/save`

**요청 본문:**
```json
{
  "log_content": "2024-01-15T10:30:45.123Z ERROR Database connection failed",
  "log_type": "iso8601"
}
```

**응답:**
```json
{
  "success": true,
  "result": [...],
  "count": 10
}
```

각 에러가 개별적으로 저장되며, `count`는 저장된 에러 개수를 나타냅니다.

#### 3. 에러 로그 이력 조회

**엔드포인트:** `GET /api/error-log/history?limit=100`

**쿼리 파라미터:**
- `limit`: 조회할 최대 개수 (기본값: 100)
- `system_type`: 시스템 타입 필터
- `severity`: 심각도 필터
- `error_type`: 에러 타입 필터
- `start_date`: 시작 날짜
- `end_date`: 종료 날짜
- `group_by_date`: 발생일자별 그룹화 (true/false)

**응답:**
```json
{
  "success": true,
  "result": [
    {
      "date": "2024-01-15",
      "errors": [
        {
          "id": 1,
          "log_content": "...",
          "timestamp": "2024-01-15T10:30:45.123Z",
          "error_type": "Database Error",
          "severity": "ERROR",
          ...
        }
      ],
      "count": 10
    }
  ],
  "count": 10
}
```

### 발생일자별 그룹화 조회

에러 로그를 발생일자별로 그룹화하여 조회하려면:

```javascript
// 발생일자별로 그룹화
const logs = errorLogsDB.findAll(100, {}, true);
// 반환 형식: [{ date: "2024-01-15", errors: [...], count: 10 }, ...]
```

---

## 문제 해결

### 문제 1: MCP 서버가 인식되지 않음

**증상:**
- Cursor AI에서 MCP 서버가 보이지 않음
- 도구 목록에 `analyze_error_logs`가 없음

**해결 방법:**

1. **설정 파일 확인**
   ```bash
   # Windows
   type %APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json
   
   # macOS/Linux
   cat ~/Library/Application\ Support/Cursor/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json
   ```

2. **Python 경로 확인**
   ```bash
   python --version
   which python  # Linux/macOS
   where python  # Windows
   ```

3. **MCP SDK 설치 확인**
   ```bash
   pip show mcp
   ```

4. **서버 직접 실행 테스트**
   ```bash
   python mcp-error-log-analyzer.py
   ```

5. **Cursor AI 재시작**

### 문제 2: 로그 파일을 찾을 수 없음

**증상:**
```
워크스페이스(C:/test/test02)에서 로그 파일을 찾을 수 없습니다.
```

**해결 방법:**

1. **로그 파일 위치 확인**
   - `logs/` 디렉토리 확인
   - `log/` 디렉토리 확인
   - 루트 디렉토리의 `*.log` 파일 확인

2. **로그 파일 경로 직접 지정**
   ```
   "이 로그 파일을 분석해줘: C:/path/to/error.log"
   ```

3. **로그 내용 직접 입력**
   ```
   "이 에러를 분석해줘:
   2024-01-15T10:30:45.123Z ERROR Database connection failed"
   ```

### 문제 3: 에러가 하나로만 저장됨

**증상:**
- 여러 에러가 있는데 하나의 row로만 저장됨

**해결 방법:**

1. **로그 형식 확인**
   - 각 에러가 타임스탬프로 시작하는지 확인
   - 빈 줄로 구분되어 있는지 확인

2. **Python 파서 확인**
   - `mcp-error-log-analyzer.py`의 `_parse_common_logs()` 메서드 확인
   - 로그 형식이 지원되는 형식인지 확인

3. **API 서버 로그 확인**
   ```bash
   # API 서버 콘솔에서 다음 메시지 확인
   [API 서버] Python 파서에서 10개의 에러 발견
   [API 서버] 10개의 에러를 개별적으로 저장합니다.
   ```

### 문제 4: 해결방안이 생성되지 않음

**증상:**
- 에러는 분석되지만 해결방안이 없음

**해결 방법:**

1. **에러 타입 확인**
   - 에러 메시지에 키워드가 포함되어 있는지 확인
   - 지원되는 에러 타입인지 확인

2. **ErrorAnalyzer 확인**
   - `mcp-error-log-analyzer.py`의 `ErrorAnalyzer` 클래스 확인
   - 에러 타입별 해결방안이 정의되어 있는지 확인

### 문제 5: 발생일자별 그룹화가 안 됨

**증상:**
- 에러가 발생일자별로 그룹화되지 않음

**해결 방법:**

1. **타임스탬프 형식 확인**
   - 로그에 타임스탬프가 포함되어 있는지 확인
   - 지원되는 형식인지 확인

2. **데이터베이스 확인**
   ```sql
   SELECT timestamp, COUNT(*) 
   FROM error_logs 
   GROUP BY DATE(timestamp);
   ```

3. **UI에서 그룹화 로직 확인**
   - `src/App.vue`의 에러 로그 현황 표시 부분 확인
   - 발생일자별 그룹화 로직이 구현되어 있는지 확인

---

## 추가 정보

### 로그 형식 권장사항

가장 정확한 분석을 위해 다음 형식을 권장합니다:

```
YYYY-MM-DD HH:MM:SS [LEVEL] Message
```

또는:

```
YYYY-MM-DDTHH:MM:SS.sssZ [LEVEL] Message
```

### 에러 메시지 작성 권장사항

- 에러 메시지에 구체적인 정보 포함 (파일 경로, 라인 번호 등)
- 에러 타입을 명확히 표시 (ERROR, WARNING 등)
- 컨텍스트 정보 포함 (서비스 이름, 리소스 타입 등)

### 성능 최적화

- 대용량 로그 파일의 경우 청크 단위로 처리
- 최대 5개 파일까지만 자동 분석
- 필요시 특정 파일만 지정하여 분석

---

## 관련 문서

- [`AI_에러로그분석_사용자_메뉴얼.md`](./AI_에러로그분석_사용자_메뉴얼.md) - 웹 UI 사용자/관리자 메뉴얼 ⭐
- [`MCP_서버_완전_가이드.md`](../MCP_서버_완전_가이드.md) - MCP 서버 전체 가이드
- [`에러_로그_분석_MCP_서버_가이드.md`](./에러_로그_분석_MCP_서버_가이드.md) - 상세 기술 가이드
- [`다른_AI_도구에서_MCP_서버_사용_가이드.md`](./다른_AI_도구에서_MCP_서버_사용_가이드.md) - 다양한 AI 도구에서 사용 방법

---

## 버전 히스토리

### v2.0.0 (2025-01)
- ✨ 각 에러별 개별 해결방안 생성 기능 추가
- ✨ 발생일자별 그룹화 기능 추가
- ✨ 각 에러를 별도 데이터베이스 row로 저장
- 🐛 로그 파싱 개선 (빈 줄 기준 분리)
- 🐛 에러 타입 분류 정확도 향상

### v1.0.0 (2025-01)
- 🎉 초기 릴리스
- 기본 에러 로그 분석 기능
- GCP 및 일반 로그 형식 지원

---

**마지막 업데이트**: 2025년 12월  
**작성자**: AI 개발팀  
**문의**: 프로젝트 이슈 트래커 또는 팀 채널

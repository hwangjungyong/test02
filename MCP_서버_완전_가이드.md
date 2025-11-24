# 📚 MCP 서버 완전 가이드

**작성일**: 2025년 1월  
**버전**: 3.0.0 (완전 MCP 서버화 버전)

> MCP 서버 설정부터 사용법, 테스트까지 모든 내용을 한 곳에 모았습니다.
> 
> **✅ 모든 기능이 MCP 서버화되었습니다!** 뉴스 검색, 에러 로그 분석, SQL 쿼리 분석, 도서 추천 등 모든 기능이 MCP 서버를 통해 제공됩니다.

---

## 📋 목차

1. [MCP 서버란?](#1-mcp-서버란)
2. [프로젝트의 MCP 서버 목록](#2-프로젝트의-mcp-서버-목록)
3. [각 MCP 서버 상세 설명](#3-각-mcp-서버-상세-설명)
4. [MCP 서버 설정 방법](#4-mcp-서버-설정-방법)
5. [도구 테스트 가이드](#5-도구-테스트-가이드)
6. [문제 해결](#6-문제-해결)

---

## 1. MCP 서버란?

**MCP 서버는 AI와 대화할 수 있게 해주는 특별한 프로그램**입니다.

### 간단한 비유로 이해하기

```
일반적인 상황:
👤 사람: "5와 7을 더해줘"
🤖 AI: "음... 계산기를 사용할 수 없어서 모르겠어요"

MCP 서버가 있는 상황:
👤 사람: "5와 7을 더해줘"
🤖 AI: "MCP 서버를 사용해서 계산해드릴게요!"
📡 MCP 서버: "5 + 7 = 12"
🤖 AI: "답은 12입니다!"
```

**MCP 서버는 AI의 손과 발**이라고 생각하면 됩니다. AI가 직접 할 수 없는 일들을 MCP 서버가 대신 해줍니다!

---

## 2. 프로젝트의 MCP 서버 목록

우리 프로젝트에는 **6개의 MCP 서버**가 있습니다 (모든 주요 기능이 MCP 서버화됨):

### 1️⃣ **mcp-server.js** (Node.js 서버)
- **역할**: AI 기사 검색 및 라디오 방송 음악 정보
- **언어**: JavaScript (Node.js)
- **파일 위치**: `mcp-server.js`
- **✅ MCP 서버화 완료**: API 서버(`api-server.js`)에서도 이 MCP 서버의 뉴스 검색 함수를 직접 호출하여 사용합니다.

### 2️⃣ **mcp-unified-server.py** (Python 통합 서버)
- **역할**: 덧셈 계산기 + 도서 검색/추천
- **언어**: Python
- **파일 위치**: `mcp-unified-server.py`

### 3️⃣ **mcp-error-log-analyzer.py** (Python 에러 로그 분석 서버)
- **역할**: 에러 로그 자동 분석, 조치 방법 및 재발 방지책 제안
- **언어**: Python
- **파일 위치**: `mcp-error-log-analyzer.py`
- **특징**: GCP 및 일반 로그 형식 자동 감지 및 파싱

### 4️⃣ **mcp-sql-query-analyzer.py** (Python SQL 쿼리 분석 서버)
- **역할**: PostgreSQL 쿼리 구조, 성능, 최적화, 복잡도, 보안 분석
- **언어**: Python
- **파일 위치**: `mcp-sql-query-analyzer.py`
- **특징**: 3000-4000라인 복잡한 쿼리 분석 지원, JSON 및 마크다운 리포트 생성

### 5️⃣ **mcp-impact-analyzer.py** (Python 영향도 분석 서버)
- **역할**: 테이블/컬럼 변경 시 워크스페이스 전체 영향도 분석
- **언어**: Python
- **파일 위치**: `mcp-impact-analyzer.py`
- **특징**: 데이터베이스 스키마 변경 시 영향받는 코드 자동 검색

### 6️⃣ **mcp-screen-validator-http-server.py** (Python HTTP 서버)
- **역할**: 웹 페이지 화면 검증 (스크린샷, 요소 확인)
- **언어**: Python
- **파일 위치**: `mcp-screen-validator-http-server.py`
- **특징**: HTTP 서버 (MCP 프로토콜이 아닌 일반 HTTP)

---

## 3. 각 MCP 서버 상세 설명

### 1️⃣ mcp-server.js (Node.js 서버)

#### 제공하는 기능 (도구)

1. **`search_ai_articles`** - AI 뉴스 검색
   - 키워드로 AI 관련 뉴스 검색
   - News API 사용
   - **✅ MCP 서버화 완료**: `searchNewsArticles` 함수가 export되어 API 서버에서도 직접 호출 가능

2. **`get_radio_song`** - 현재 재생 중인 노래
   - 한국 라디오 방송 (KBS, MBC, SBS) 현재 노래 정보

3. **`get_radio_recent_songs`** - 최근 재생된 노래
   - 라디오 방송 최근 재생 목록

4. **`recommend_similar_songs`** - 유사 노래 추천
   - Last.fm API 기반 음악 추천

#### MCP 서버 통합 사용

**API 서버에서의 사용:**
```javascript
import { searchNewsArticles } from './mcp-server.js';

// API 서버의 /api/news 엔드포인트에서 MCP 서버 함수 직접 호출
const result = await searchNewsArticles(keyword, {
  pageSize: 100,
  maxPages: 10,
  fromDate: fromDate,
  language: 'ko',
  sortBy: 'publishedAt'
});
```

이렇게 하면:
- ✅ 코드 중복 제거
- ✅ 일관된 뉴스 검색 로직
- ✅ MCP 서버와 API 서버 간 기능 공유

#### 사용 예시

```
"ChatGPT에 대한 최신 뉴스를 찾아줘"
→ search_ai_articles 도구 사용
→ 결과: ChatGPT 관련 뉴스 기사 10개 반환
```

---

### 2️⃣ mcp-error-log-analyzer.py (Python 에러 로그 분석 서버)

#### 제공하는 기능 (도구)

1. **`analyze_error_logs`** - 에러 로그 분석
   - 워크스페이스에서 로그 파일 자동 검색
   - GCP 및 일반 로그 형식 자동 감지 및 파싱
   - 에러 정보를 테이블 형태로 출력
   - 조치 방법 및 재발 방지책 제안

#### 사용 예시

```
"워크스페이스의 에러 로그를 분석해줘"
→ analyze_error_logs 도구 사용
→ 결과: 에러 로그 요약, 분석, 조치 방법, 재발 방지책 제공
```

#### 주요 기능

- **자동 로그 파일 검색**: `logs/`, `log/` 디렉토리 및 루트 디렉토리에서 자동 검색
- **지능형 로그 파싱**: GCP 로그 및 일반 로그 형식 자동 감지
- **에러 타입 분류**: database, network, authentication, memory, file, syntax 등
- **조치 방법 제안**: 에러 타입별 구체적인 조치 방법 제시
- **재발 방지책 제안**: 에러 타입별 재발 방지 방법 제시

**상세 가이드**: [`docs/에러_로그_분석_MCP_서버_가이드.md`](./docs/에러_로그_분석_MCP_서버_가이드.md)

---

### 4️⃣ mcp-sql-query-analyzer.py (Python SQL 쿼리 분석 서버)

#### 제공하는 기능 (도구)

1. **`analyze_sql_query`** - SQL 쿼리 분석
   - PostgreSQL 쿼리 구조 분석 (테이블, 컬럼, JOIN, 서브쿼리 등)
   - 성능 분석 (인덱스 사용, 풀 스캔 위험도 등)
   - 복잡도 분석 (중첩도, 테이블 수 등)
   - 보안 분석 (SQL Injection 취약점 등)
   - 최적화 제안 (인덱스 제안, 쿼리 리팩토링 등)
   - JSON 및 마크다운 리포트 생성

#### 사용 예시

```
"queries/complex_query.sql 파일의 쿼리를 분석해줘"
→ analyze_sql_query 도구 사용 (query_file: "queries/complex_query.sql")
→ 결과: 구조 분석, 성능 분석, 복잡도 분석, 보안 분석, 최적화 제안 제공

"다음 쿼리를 분석해줘: SELECT * FROM users WHERE id = 1;"
→ analyze_sql_query 도구 사용 (query_text: "SELECT * FROM users WHERE id = 1;")
→ 결과: 분석 리포트 생성
```

#### 주요 기능

- **쿼리 구조 분석**: 테이블, 컬럼, JOIN, 서브쿼리, CTE 등 추출
- **성능 분석**: 인덱스 사용 가능성, 풀 스캔 위험도, 비효율적인 JOIN 패턴 감지
- **복잡도 분석**: 쿼리 길이, 테이블 수, JOIN 수, 서브쿼리 깊이 등 평가
- **보안 분석**: SQL Injection 취약점, 권한 이슈, 데이터 노출 위험 검사
- **최적화 제안**: 인덱스 제안, 쿼리 리팩토링, 조건 최적화 등 구체적 제안
- **리포트 생성**: JSON 및 마크다운 형식으로 상세 리포트 생성

**상세 가이드**: [`docs/SQL_쿼리_분석_MCP_서버_가이드.md`](./docs/SQL_쿼리_분석_MCP_서버_가이드.md)

---

### 5️⃣ mcp-impact-analyzer.py (Python 영향도 분석 서버)

#### 제공하는 기능 (도구)

1. **`analyze_impact`** - 테이블/컬럼 영향도 분석
   - 테이블 또는 컬럼 변경 시 워크스페이스 전체 영향도 분석
   - 영향받는 파일, 함수, 코드 위치 자동 검색
   - 변경 사항에 대한 상세 리포트 생성

#### 사용 예시

```
"users 테이블을 변경할 때 영향받는 코드를 찾아줘"
→ analyze_impact 도구 사용 (table_name: "users")
→ 결과: 영향받는 파일 목록, 함수 목록, 코드 스니펫 제공
```

**상세 가이드**: [`docs/영향도_분석_가이드.md`](./docs/영향도_분석_가이드.md)

---

### 6️⃣ mcp-unified-server.py (Python 통합 서버)

#### 제공하는 기능 (도구)

1. **`add_numbers`** - 덧셈 계산기
   - 두 개의 숫자를 더함

2. **`recommend_books`** - 도서 추천
   - 키워드나 장르로 도서 검색
   - Google Books API 사용

3. **`get_popular_books`** - 인기 도서 목록
   - 베스트셀러 정보

4. **`get_book_details`** - 도서 상세 정보
   - 특정 도서의 상세 정보

#### 사용 예시

```
"5와 7을 더해줘"
→ add_numbers 도구 사용 (a: 5, b: 7)
→ 결과: "5 + 7 = 12"

"인공지능 관련 책을 추천해줘"
→ recommend_books 도구 사용 (query: "인공지능")
→ 결과: 인공지능 관련 도서 10개 반환
```

---

## 4. MCP 서버 아키텍처

### 전체 시스템 구조

```
┌─────────────────────────────────────────────────────────┐
│                    Vue 프론트엔드                        │
│              (src/App.vue, src/services/)               │
└────────────────────┬────────────────────────────────────┘
                     │ HTTP 요청
                     ▼
┌─────────────────────────────────────────────────────────┐
│              API 서버 (api-server.js)                    │
│  ┌──────────────────────────────────────────────────┐  │
│  │  /api/news → MCP 서버 함수 호출                  │  │
│  │  /api/news/economy → MCP 서버 함수 호출          │  │
│  └──────────────────────────────────────────────────┘  │
└────────────────────┬────────────────────────────────────┘
                     │ import/호출
                     ▼
┌─────────────────────────────────────────────────────────┐
│         MCP 서버들 (모듈화된 함수 제공)                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  mcp-server.js                                   │  │
│  │  - searchNewsArticles() [export]                │  │
│  │  - search_ai_articles [MCP tool]               │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  mcp-error-log-analyzer.py                       │  │
│  │  - analyze_error_logs [MCP tool]                │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  mcp-sql-query-analyzer.py                       │  │
│  │  - analyze_sql_query [MCP tool]                 │  │
│  └──────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────┐  │
│  │  mcp-unified-server.py                           │  │
│  │  - recommend_books [MCP tool]                   │  │
│  │  - add_numbers [MCP tool]                      │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│              외부 API (News API, Last.fm 등)             │
└─────────────────────────────────────────────────────────┘
```

### MCP 서버의 이중 역할

1. **MCP 프로토콜 서버**: Cursor AI와 통신하여 도구 제공
2. **모듈화된 함수**: API 서버에서 직접 import하여 사용

예시:
- `mcp-server.js`의 `searchNewsArticles` 함수는:
  - ✅ MCP 도구 `search_ai_articles`로 Cursor AI에서 사용 가능
  - ✅ export된 함수로 API 서버에서 직접 호출 가능

## 5. MCP 서버 설정 방법

### Cursor AI에서 MCP 서버 설정

`cursor-mcp-config.json` 파일에 다음 내용 추가:

```json
{
  "mcpServers": {
    "unified-mcp-server": {
      "command": "python",
      "args": ["mcp-unified-server.py"],
      "cwd": "C:/test/test02"
    },
    "news-music-server": {
      "command": "node",
      "args": ["mcp-server.js"],
      "cwd": "C:/test/test02"
    },
    "error-log-analyzer": {
      "command": "python",
      "args": ["mcp-error-log-analyzer.py"],
      "cwd": "C:/test/test02"
    },
    "sql-query-analyzer": {
      "command": "python",
      "args": ["mcp-sql-query-analyzer.py"],
      "cwd": "C:/test/test02"
    },
    "impact-analyzer": {
      "command": "python",
      "args": ["mcp-impact-analyzer.py"],
      "cwd": "C:/test/test02"
    }
  }
}
```

### 의존성 설치

#### 자동 빌드 스크립트 사용 (권장)

**Windows:**
```bash
build-all-mcp-servers.bat
```

**Linux/macOS:**
```bash
chmod +x build-all-mcp-servers.sh
./build-all-mcp-servers.sh
```

이 스크립트는 다음을 자동으로 수행합니다:
- Python 및 Node.js 설치 확인
- MCP SDK 설치 확인 및 자동 설치
- 모든 MCP 서버 파일 검증

#### 수동 설치

**Python 패키지:**
```bash
pip install mcp sqlparse
```

**Node.js 패키지:**
```bash
npm install
```

---

## 6. 도구 테스트 가이드

### 테스트 1: 덧셈 계산기 (`add_numbers`)

**요청:**
```
"5와 7을 더해줘"
```

**예상 동작:**
1. Cursor AI가 `add_numbers` 도구를 자동으로 선택
2. 파라미터: `{ "a": 5, "b": 7 }`
3. MCP 서버가 계산 수행
4. 결과: `"5 + 7 = 12"`

**테스트 방법:**
1. Cursor AI 채팅에서 "5와 7을 더해줘" 입력
2. AI가 자동으로 `add_numbers` 도구 사용
3. 결과 확인: "답은 12입니다" 또는 "5 + 7 = 12"

---

### 테스트 2: AI 기사 검색 (`search_ai_articles`)

**요청:**
```
"ChatGPT에 대한 최신 뉴스를 찾아줘"
```

**예상 동작:**
1. Cursor AI가 `search_ai_articles` 도구를 자동으로 선택
2. 파라미터: `{ "keyword": "ChatGPT" }`
3. MCP 서버가 News API 호출
4. 결과: ChatGPT 관련 뉴스 기사 10개 반환

**테스트 방법:**
1. Cursor AI 채팅에서 "ChatGPT에 대한 최신 뉴스를 찾아줘" 입력
2. AI가 자동으로 `search_ai_articles` 도구 사용
3. 결과 확인: 뉴스 기사 목록 및 링크

---

### 테스트 3: 에러 로그 분석 (`analyze_error_logs`)

**요청:**
```
"워크스페이스의 에러 로그를 분석해줘"
```

**예상 동작:**
1. Cursor AI가 `analyze_error_logs` 도구를 자동으로 선택
2. 워크스페이스에서 로그 파일 자동 검색
3. 로그 형식 자동 감지 및 파싱
4. 결과: 에러 로그 요약 테이블, 분석, 조치 방법, 재발 방지책 제공

**테스트 방법:**
1. Cursor AI 채팅에서 "워크스페이스의 에러 로그를 분석해줘" 입력
2. AI가 자동으로 `analyze_error_logs` 도구 사용
3. 결과 확인: 에러 로그 요약 테이블, 분석 결과, 조치 방법, 재발 방지책

---

### 테스트 4: SQL 쿼리 분석 (`analyze_sql_query`)

**요청:**
```
"queries/complex_query.sql 파일의 쿼리를 분석해줘"
```

**예상 동작:**
1. Cursor AI가 `analyze_sql_query` 도구를 자동으로 선택
2. 파라미터: `{ "query_file": "queries/complex_query.sql", "output_format": "both" }`
3. MCP 서버가 쿼리 분석 수행
4. 결과: 구조 분석, 성능 분석, 복잡도 분석, 보안 분석, 최적화 제안 제공
5. JSON 및 마크다운 리포트 파일 생성

**테스트 방법:**
1. Cursor AI 채팅에서 "queries/complex_query.sql 파일의 쿼리를 분석해줘" 입력
2. AI가 자동으로 `analyze_sql_query` 도구 사용
3. 결과 확인: 분석 요약, 성능 점수, 복잡도 점수, 보안 점수, 최적화 제안
4. 리포트 파일 확인: `logs/sql_analysis/{파일명}_analysis_{타임스탬프}.json`, `.md`

**직접 쿼리 입력 테스트:**
```
"다음 쿼리를 분석해줘: SELECT u.id, u.name FROM users u WHERE u.status = 'active';"
```

---

### 테스트 5: 영향도 분석 (`analyze_impact`)

**요청:**
```
"users 테이블을 변경할 때 영향받는 코드를 찾아줘"
```

**예상 동작:**
1. Cursor AI가 `analyze_impact` 도구를 자동으로 선택
2. 파라미터: `{ "table_name": "users" }`
3. MCP 서버가 워크스페이스 전체를 검색하여 영향받는 코드 찾기
4. 결과: 영향받는 파일 목록, 함수 목록, 코드 스니펫 제공

**테스트 방법:**
1. Cursor AI 채팅에서 "users 테이블을 변경할 때 영향받는 코드를 찾아줘" 입력
2. AI가 자동으로 `analyze_impact` 도구 사용
3. 결과 확인: 영향받는 파일 목록, 함수 목록, 코드 스니펫

---

### 테스트 6: 도서 추천 (`recommend_books`)

**요청:**
```
"인공지능 관련 책을 추천해줘"
```

**예상 동작:**
1. Cursor AI가 `recommend_books` 도구를 자동으로 선택
2. 파라미터: `{ "query": "인공지능", "maxResults": 10 }`
3. MCP 서버가 Google Books API 호출
4. 결과: 인공지능 관련 도서 10개 반환

**테스트 방법:**
1. Cursor AI 채팅에서 "인공지능 관련 책을 추천해줘" 입력
2. AI가 자동으로 `recommend_books` 도구 사용
3. 결과 확인: 도서 목록 (제목, 저자, 출판사, 링크)

---

## 7. 문제 해결

### 문제 1: MCP 서버가 인식되지 않음

**해결:**
1. `cursor-mcp-config.json` 파일 경로 확인
2. Cursor AI 재시작
3. 설정 파일 문법 확인 (JSON 형식)

### 문제 2: Python MCP 서버 실행 오류

**오류:**
```
ModuleNotFoundError: No module named 'mcp'
```

**해결:**
```bash
pip install mcp
```

### 문제 3: Node.js MCP 서버 실행 오류

**오류:**
```
Cannot find module '@modelcontextprotocol/sdk'
```

**해결:**
```bash
npm install
```

### 문제 4: API 호출 실패

**해결:**
1. API 키 확인 (`.env` 파일)
2. 네트워크 연결 확인
3. API 키 권한 확인

---

## 📚 추가 참고 자료

- **MCP 공식 문서**: https://modelcontextprotocol.io
- **Cursor AI 문서**: https://cursor.sh/docs

---

**다음 단계:** Git 사용법은 [`Git_통합_가이드.md`](./Git_통합_가이드.md)를 참조하세요.


# 📚 MCP 서버 완전 가이드

**작성일**: 2025년 1월  
**버전**: 2.0.0 (통합 버전)

> MCP 서버 설정부터 사용법, 테스트까지 모든 내용을 한 곳에 모았습니다.

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

우리 프로젝트에는 **3개의 MCP 서버**가 있습니다:

### 1️⃣ **mcp-server.js** (Node.js 서버)
- **역할**: AI 기사 검색 및 라디오 방송 음악 정보
- **언어**: JavaScript (Node.js)
- **파일 위치**: `mcp-server.js`

### 2️⃣ **mcp-unified-server.py** (Python 통합 서버)
- **역할**: 덧셈 계산기 + 도서 검색/추천
- **언어**: Python
- **파일 위치**: `mcp-unified-server.py`

### 3️⃣ **mcp-screen-validator-http-server.py** (Python HTTP 서버)
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

2. **`get_radio_song`** - 현재 재생 중인 노래
   - 한국 라디오 방송 (KBS, MBC, SBS) 현재 노래 정보

3. **`get_radio_recent_songs`** - 최근 재생된 노래
   - 라디오 방송 최근 재생 목록

4. **`recommend_similar_songs`** - 유사 노래 추천
   - Last.fm API 기반 음악 추천

#### 사용 예시

```
"ChatGPT에 대한 최신 뉴스를 찾아줘"
→ search_ai_articles 도구 사용
→ 결과: ChatGPT 관련 뉴스 기사 10개 반환
```

---

### 2️⃣ mcp-unified-server.py (Python 통합 서버)

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

## 4. MCP 서버 설정 방법

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
    }
  }
}
```

### 의존성 설치

#### Python 패키지
```bash
pip install mcp
```

#### Node.js 패키지
```bash
npm install
```

---

## 5. 도구 테스트 가이드

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

### 테스트 3: 도서 추천 (`recommend_books`)

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

## 6. 문제 해결

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


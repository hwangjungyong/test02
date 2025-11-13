# 📚 MCP 서버 완전 가이드 (초딩도 이해 가능)

## 🎯 MCP 서버란 무엇인가요?

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

## 📦 우리 프로젝트의 MCP 서버 목록

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

## 🔍 각 MCP 서버 상세 설명

### 1️⃣ mcp-server.js (Node.js 서버)

#### 📋 기본 정보
- **이름**: `ai-articles-radio-server`
- **버전**: `3.0.0`
- **실행 방법**: `npm run mcp-server`
- **통신 방식**: 표준 입출력 (stdin/stdout)

#### 🛠️ 제공하는 기능 (도구)

이 서버는 **4가지 도구**를 제공합니다:

##### 1. `search_ai_articles` - AI 기사 검색
**무엇을 하나요?**
- 키워드를 입력하면 AI 관련 뉴스 기사를 검색합니다
- News API를 사용하여 실제 뉴스를 가져옵니다

**사용 예시:**
```
"ChatGPT에 대한 최신 뉴스를 찾아줘"
→ search_ai_articles 도구 사용
→ 결과: ChatGPT 관련 뉴스 기사 10개 반환
```

**입력 파라미터:**
- `keyword` (필수): 검색할 키워드 (예: "ChatGPT", "인공지능", "머신러닝")

**반환 정보:**
- 기사 제목
- 요약
- 날짜
- 출처
- 링크

##### 2. `get_radio_song` - 라디오 현재 재생 노래
**무엇을 하나요?**
- 한국 라디오 방송(KBS, MBC, SBS)에서 현재 재생 중인 노래 정보를 가져옵니다
- Last.fm API를 사용합니다

**사용 예시:**
```
"KBS 쿨FM에서 지금 무슨 노래가 나오고 있어?"
→ get_radio_song 도구 사용 (station: "kbs")
→ 결과: 현재 재생 중인 노래 정보 반환
```

**입력 파라미터:**
- `station` (필수): 방송국 (kbs, mbc, sbs 중 선택)

**반환 정보:**
- 노래 제목
- 아티스트
- 장르
- 시간

##### 3. `get_radio_recent_songs` - 라디오 최근 재생 노래
**무엇을 하나요?**
- 한국 라디오 방송에서 최근 재생된 노래 목록을 가져옵니다
- Last.fm API를 사용합니다

**사용 예시:**
```
"MBC FM4U에서 최근에 재생한 노래 목록을 알려줘"
→ get_radio_recent_songs 도구 사용 (station: "mbc")
→ 결과: 최근 재생된 노래 10개 반환
```

**입력 파라미터:**
- `station` (필수): 방송국 (kbs, mbc, sbs 중 선택)

**반환 정보:**
- 노래 목록 (제목, 아티스트, 재생 횟수)

##### 4. `recommend_similar_songs` - 유사한 노래 추천
**무엇을 하나요?**
- 좋아하는 노래를 입력하면 비슷한 추천 노래 목록을 반환합니다
- Last.fm API를 사용합니다

**사용 예시:**
```
"Dynamite와 비슷한 노래를 추천해줘"
→ recommend_similar_songs 도구 사용 (songTitle: "Dynamite", artist: "BTS")
→ 결과: 유사한 노래 10개 반환
```

**입력 파라미터:**
- `songTitle` (필수): 노래 제목
- `artist` (선택): 아티스트 이름

**반환 정보:**
- 추천 노래 목록 (제목, 아티스트, 재생 횟수)

#### 🔧 기술적 세부사항

**사용하는 외부 API:**
- News API (`https://newsapi.org/v2`)
- Last.fm API (`https://ws.audioscrobbler.com/2.0`)

**프록시 설정:**
- 프록시를 통해 외부 API 호출
- 프록시 URL: `http://70.10.15.10:8080`

**에러 처리:**
- API 호출 실패 시 하드코딩된 데이터 사용 (Fallback)
- 타임아웃: 30초

---

### 2️⃣ mcp-unified-server.py (Python 통합 서버)

#### 📋 기본 정보
- **이름**: `unified-mcp-server`
- **언어**: Python 3
- **실행 방법**: `python mcp-unified-server.py` 또는 `npm run mcp-unified`
- **통신 방식**: 표준 입출력 (stdin/stdout)

#### 🛠️ 제공하는 기능 (도구)

이 서버는 **4가지 도구**를 제공합니다:

##### 1. `add_numbers` - 덧셈 계산기
**무엇을 하나요?**
- 두 개의 숫자를 입력받아 더한 결과를 반환합니다

**사용 예시:**
```
"5와 7을 더해줘"
→ add_numbers 도구 사용 (a: 5, b: 7)
→ 결과: "5 + 7 = 12"
```

**입력 파라미터:**
- `a` (필수): 첫 번째 숫자
- `b` (필수): 두 번째 숫자

**반환 정보:**
- 계산 결과 (예: "5 + 7 = 12")

##### 2. `recommend_books` - 도서 추천
**무엇을 하나요?**
- 키워드나 장르를 입력받아 관련 도서를 추천합니다
- Google Books API를 사용하여 실제 도서 정보를 가져옵니다

**사용 예시:**
```
"인공지능 관련 책을 추천해줘"
→ recommend_books 도구 사용 (query: "인공지능", maxResults: 10)
→ 결과: 인공지능 관련 도서 10개 반환
```

**입력 파라미터:**
- `query` (필수): 검색 키워드 또는 장르 (예: "인공지능", "소설", "경제")
- `maxResults` (선택): 최대 결과 개수 (기본값: 10)

**반환 정보:**
- 도서 제목
- 저자
- 출판사
- 출판일
- 카테고리
- 평점
- 설명
- 링크

##### 3. `get_popular_books` - 인기 도서 목록
**무엇을 하나요?**
- 인기 도서 목록을 가져옵니다
- Google Books API를 사용하여 베스트셀러 정보를 가져옵니다

**사용 예시:**
```
"인기 소설을 알려줘"
→ get_popular_books 도구 사용 (category: "fiction", maxResults: 20)
→ 결과: 인기 소설 20개 반환
```

**입력 파라미터:**
- `category` (선택): 도서 카테고리 (예: "fiction", "nonfiction", "computers")
- `maxResults` (선택): 최대 결과 개수 (기본값: 20)

**반환 정보:**
- 인기 도서 목록 (제목, 저자, 출판사, 카테고리, 평점, 링크)

##### 4. `get_book_details` - 도서 상세 정보
**무엇을 하나요?**
- 특정 도서의 상세 정보를 가져옵니다

**사용 예시:**
```
"이 책의 상세 정보를 알려줘 (bookId: abc123)"
→ get_book_details 도구 사용 (bookId: "abc123")
→ 결과: 도서 상세 정보 반환
```

**입력 파라미터:**
- `bookId` (필수): Google Books API의 도서 ID

**반환 정보:**
- 제목
- 저자
- 출판사
- 출판일
- 페이지 수
- 언어
- 카테고리
- 평점
- 설명
- 링크

#### 🔧 기술적 세부사항

**사용하는 외부 API:**
- Google Books API (`https://www.googleapis.com/books/v1/volumes`)

**의존성:**
- Python MCP SDK (`pip install mcp`)

**에러 처리:**
- API 호출 실패 시 에러 메시지 반환
- 타임아웃: 30초

---

### 3️⃣ mcp-screen-validator-http-server.py (Python HTTP 서버)

#### 📋 기본 정보
- **이름**: 화면 검증 HTTP 서버
- **언어**: Python 3
- **실행 방법**: `python mcp-screen-validator-http-server.py` 또는 `npm run screen-validator-server`
- **포트**: `3002`
- **통신 방식**: HTTP (MCP 프로토콜 아님)
- **특징**: Vue 앱에서 HTTP 요청으로 사용

#### 🛠️ 제공하는 기능 (API 엔드포인트)

이 서버는 **3가지 API 엔드포인트**를 제공합니다:

##### 1. `/api/screen/validate` - 화면 검증
**무엇을 하나요?**
- 웹 페이지의 특정 요소가 예상한 값과 일치하는지 확인합니다
- 스크린샷도 함께 반환합니다

**사용 예시:**
```javascript
// Vue 앱에서 사용
fetch('http://localhost:3002/api/screen/validate', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'http://localhost:5173',
    selector: '#title',
    expectedValue: '환영합니다'
  })
})
```

**입력 파라미터:**
- `url` (필수): 검증할 웹 페이지 URL
- `selector` (선택): CSS 선택자 (예: "#title", ".content")
- `expectedValue` (선택): 예상하는 값

**반환 정보:**
- `success`: 성공 여부
- `url`: 검증한 URL
- `selector`: 사용한 선택자
- `actualValue`: 실제 값
- `expectedValue`: 예상 값
- `passed`: 검증 통과 여부
- `message`: 검증 결과 메시지
- `screenshot`: 스크린샷 (Base64 인코딩)
- `selectorError`: 선택자 오류 메시지 (있는 경우)

##### 2. `/api/screen/capture` - 화면 캡처
**무엇을 하나요?**
- 웹 페이지의 스크린샷을 찍습니다

**사용 예시:**
```javascript
fetch('http://localhost:3002/api/screen/capture', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'http://localhost:5173',
    selector: '#main-content'  // 선택사항: 특정 요소만 캡처
  })
})
```

**입력 파라미터:**
- `url` (필수): 캡처할 웹 페이지 URL
- `selector` (선택): CSS 선택자 (특정 요소만 캡처)

**반환 정보:**
- `success`: 성공 여부
- `url`: 캡처한 URL
- `selector`: 사용한 선택자
- `screenshot`: 스크린샷 (Base64 인코딩)

##### 3. `/api/screen/interact` - 페이지 상호작용
**무엇을 하나요?**
- 웹 페이지에서 입력, 클릭 등의 액션을 수행하고 결과를 가져옵니다

**사용 예시:**
```javascript
fetch('http://localhost:3002/api/screen/interact', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    url: 'http://localhost:5173',
    actions: [
      { type: 'fill', selector: '#input', value: '텍스트' },
      { type: 'click', selector: '#button' }
    ],
    resultSelector: '#result',
    waitAfterActions: 2000
  })
})
```

**입력 파라미터:**
- `url` (필수): 상호작용할 웹 페이지 URL
- `actions` (필수): 수행할 액션 목록
  - `type`: 액션 타입 ("fill", "click", "select", "check", "uncheck", "wait")
  - `selector`: CSS 선택자
  - `value`: 값 (필요한 경우)
- `resultSelector` (선택): 결과를 읽을 요소 선택자
- `waitAfterActions` (선택): 액션 후 대기 시간 (ms, 기본값: 2000)

**반환 정보:**
- `success`: 성공 여부
- `url`: 상호작용한 URL
- `actions`: 수행한 액션 로그
- `resultSelector`: 결과 선택자
- `resultValue`: 결과 값
- `screenshot`: 스크린샷 (Base64 인코딩)

#### 🔧 기술적 세부사항

**사용하는 라이브러리:**
- Playwright (브라우저 자동화)
- Python HTTP Server

**프록시 설정:**
- 프록시를 통해 웹 페이지 접속
- 프록시 URL: `http://70.10.15.10:8080`

**브라우저 설정:**
- Headless 모드 (화면 없이 실행)
- 뷰포트: 1920x1080
- 타임아웃: 60초 (페이지 로드), 10초 (요소 대기)

**에러 처리:**
- 연결 타임아웃, DNS 오류 등 상세한 에러 메시지 제공
- 선택자를 찾지 못할 경우 제안 선택자 제공

---

## 🚀 MCP 서버 실행 방법

### 전체 서버 한 번에 실행

**Windows:**
```bash
start-servers.bat
```

**Linux/macOS:**
```bash
./start-servers.sh
```

이 명령어를 실행하면 모든 서버가 자동으로 시작됩니다:
1. API 서버 (포트 3001)
2. MCP 서버 (Node.js)
3. Python HTTP 서버 (포트 3002)
4. Unified MCP 서버 (Python)
5. Vite Dev 서버 (포트 5173)

### 개별 서버 실행

#### 1. mcp-server.js 실행
```bash
npm run mcp-server
```

#### 2. mcp-unified-server.py 실행
```bash
npm run mcp-unified
# 또는
python mcp-unified-server.py
```

#### 3. mcp-screen-validator-http-server.py 실행
```bash
npm run screen-validator-server
# 또는
python mcp-screen-validator-http-server.py
```

---

## ⚙️ Cursor AI에서 MCP 서버 사용하기

### 설정 파일 위치

Cursor AI는 `cursor-mcp-config.json` 파일을 읽어서 MCP 서버를 등록합니다.

**파일 위치:**
- Windows: `%APPDATA%\Cursor\User\globalStorage\saoudrizwan.claude-dev\settings\cline_mcp_settings.json`
- 또는 프로젝트 루트의 `cursor-mcp-config.json`

### 현재 설정 확인

프로젝트 루트에 `cursor-mcp-config.json` 파일이 있습니다. 이 파일을 열어서 확인할 수 있습니다.

### MCP 서버 등록 방법

#### 방법 1: Cursor 설정에서 직접 등록

1. Cursor AI 설정 열기 (Ctrl+, 또는 Cmd+,)
2. "MCP Servers" 검색
3. "Edit in settings.json" 클릭
4. 다음 형식으로 추가:

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
    }
  }
}
```

#### 방법 2: 프로젝트 설정 파일 사용

프로젝트 루트의 `cursor-mcp-config.json` 파일을 Cursor가 자동으로 읽도록 설정할 수 있습니다.

---

## 🧪 MCP 서버 테스트 방법

### 1. Cursor AI 채팅에서 테스트

Cursor AI 채팅에서 다음과 같이 요청하면 MCP 서버가 자동으로 적절한 도구를 사용합니다:

```
"5와 7을 더해줘"
→ add_numbers 도구 사용

"ChatGPT에 대한 최신 뉴스를 찾아줘"
→ search_ai_articles 도구 사용

"인공지능 관련 책을 추천해줘"
→ recommend_books 도구 사용
```

**실제 사용 예시:**

각 요청에 대해 MCP 서버가 자동으로 적절한 도구를 선택하여 실행합니다. 사용자는 자연어로만 요청하면 되며, AI가 자동으로 도구를 선택하고 실행합니다.

### 2. 직접 도구 목록 확인

Cursor AI 채팅에서:
```
"사용 가능한 MCP 도구 목록을 보여줘"
```

또는 Cursor의 MCP 서버 패널에서 확인할 수 있습니다.

---

## 📊 MCP 서버 비교표

| 서버 | 언어 | 프로토콜 | 포트 | 주요 기능 |
|------|------|----------|------|-----------|
| mcp-server.js | Node.js | MCP (stdio) | - | AI 기사 검색, 라디오 음악 정보 |
| mcp-unified-server.py | Python | MCP (stdio) | - | 덧셈 계산, 도서 검색/추천 |
| mcp-screen-validator-http-server.py | Python | HTTP | 3002 | 화면 검증, 스크린샷 |

---

## 🔧 문제 해결

### MCP 서버가 작동하지 않을 때

1. **서버가 실행 중인지 확인**
   ```bash
   # Windows
   tasklist | findstr node
   tasklist | findstr python
   
   # Linux/macOS
   ps aux | grep node
   ps aux | grep python
   ```

2. **의존성이 설치되어 있는지 확인**
   ```bash
   # Node.js 서버
   npm install
   
   # Python 서버
   pip install mcp playwright
   ```

3. **포트 충돌 확인**
   ```bash
   # Windows
   netstat -ano | findstr :3002
   
   # Linux/macOS
   lsof -i :3002
   ```

4. **로그 확인**
   - 각 서버의 콘솔 출력 확인
   - 에러 메시지 확인

### Cursor AI에서 MCP 서버가 보이지 않을 때

1. Cursor 재시작
2. 설정 파일 확인 (`cursor-mcp-config.json`)
3. 서버 실행 경로 확인 (절대 경로 사용 권장)
4. Cursor 로그 확인

---

## 📝 요약

### 우리 프로젝트의 MCP 서버

1. **mcp-server.js**: AI 기사 검색 + 라디오 음악 정보 (4개 도구)
2. **mcp-unified-server.py**: 덧셈 계산 + 도서 검색/추천 (4개 도구)
3. **mcp-screen-validator-http-server.py**: 화면 검증 (HTTP API, 3개 엔드포인트)

### 총 제공 기능

- **MCP 도구**: 8개
- **HTTP API**: 3개
- **외부 API 연동**: News API, Last.fm API, Google Books API

### 사용 방법

1. `start-servers.bat` 실행하여 모든 서버 시작
2. Cursor AI 채팅에서 자연어로 요청
3. MCP 서버가 자동으로 적절한 도구 사용

---

## 🎓 초보자를 위한 추가 설명

### MCP 프로토콜이란?

**MCP (Model Context Protocol)**는 AI와 외부 프로그램이 대화할 수 있게 해주는 규칙입니다.

**비유:**
- **일반적인 상황**: AI는 혼자서만 생각할 수 있음
- **MCP가 있는 상황**: AI가 외부 프로그램과 대화할 수 있음

### 왜 MCP 서버가 필요한가요?

AI는 텍스트만 다룰 수 있지만, 실제로는:
- 뉴스를 검색해야 할 때
- 계산을 해야 할 때
- 웹 페이지를 확인해야 할 때

이런 일들을 MCP 서버가 대신 해줍니다!

### MCP 서버는 어떻게 작동하나요?

```
1. 사용자가 AI에게 요청
   "5와 7을 더해줘"

2. AI가 MCP 서버에게 요청
   "add_numbers 도구를 사용해서 5와 7을 더해줘"

3. MCP 서버가 계산 수행
   "5 + 7 = 12"

4. MCP 서버가 결과를 AI에게 전달
   "결과: 12"

5. AI가 사용자에게 답변
   "답은 12입니다!"
```

이 과정이 **자동으로** 일어납니다!

---

## 📚 참고 자료

- [MCP 프로토콜 공식 문서](https://modelcontextprotocol.io)
- [News API 문서](https://newsapi.org/docs)
- [Last.fm API 문서](https://www.last.fm/api)
- [Google Books API 문서](https://developers.google.com/books)

---

**작성일**: 2025년 1월
**버전**: 1.0.0
**작성자**: AI Assistant


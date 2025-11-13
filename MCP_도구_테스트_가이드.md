# 🧪 MCP 도구 테스트 가이드

## 📋 테스트할 도구 목록

### ✅ 테스트 1: 덧셈 계산기 (`add_numbers`)

**요청:**
```
"5와 7을 더해줘"
```

---

#### 📋 예상 동작

1. Cursor AI가 `add_numbers` 도구를 자동으로 선택
2. 파라미터: `{ "a": 5, "b": 7 }`
3. MCP 서버 (`mcp-unified-server.py`)가 계산 수행
4. 결과: `"5 + 7 = 12"`

---

#### 🔍 실제 코드 동작

```python
# mcp-unified-server.py의 add_numbers 핸들러
a = 5
b = 7
result = float(a) + float(b)  # 12.0
return "5 + 7 = 12"
```

---

#### 🧪 테스트 방법

1. Cursor AI 채팅에서 "5와 7을 더해줘" 입력
2. AI가 자동으로 `add_numbers` 도구 사용
3. 결과 확인: "답은 12입니다" 또는 "5 + 7 = 12"

---

### ✅ 테스트 2: AI 기사 검색 (`search_ai_articles`)

**요청:**
```
"ChatGPT에 대한 최신 뉴스를 찾아줘"
```

---

#### 📋 예상 동작

1. Cursor AI가 `search_ai_articles` 도구를 자동으로 선택
2. 파라미터: `{ "keyword": "ChatGPT" }`
3. MCP 서버 (`mcp-server.js`)가 News API 호출
4. 결과: ChatGPT 관련 뉴스 기사 10개 반환

---

#### 🔍 세부 처리 현황 (단계별)

**단계 1: 사용자 요청 수신**
```
사용자 입력: "ChatGPT에 대한 최신 뉴스를 찾아줘"
```

**단계 2: AI 도구 선택**
```
✅ Cursor AI가 요청 분석
✅ 적절한 도구 자동 선택: search_ai_articles
✅ 도구 소스: mcp-server.js (Node.js MCP 서버)
```

**단계 3: 파라미터 추출 및 검증**
```javascript
// mcp-server.js:294-308줄
// 요청에서 키워드 추출
const { keyword } = args;  // keyword = "ChatGPT"

// 입력값 검증
if (!keyword || keyword.trim() === '') {
  return {
    content: [{
      type: 'text',
      text: `오류: 검색 키워드를 입력해주세요.`
    }],
    isError: true
  };
}
// ✅ 검증 통과: keyword = "ChatGPT"
```

**단계 4: API URL 생성**
```javascript
// mcp-server.js:312-313줄
// 키워드 URL 인코딩
const searchKeyword = encodeURIComponent(keyword.trim());  // "ChatGPT"

// News API URL 생성
const apiUrl = `${NEWS_API_BASE_URL}/everything?q=${searchKeyword}&language=ko&sortBy=publishedAt&pageSize=10&apiKey=${NEWS_API_KEY}`;
// 결과: "https://newsapi.org/v2/everything?q=ChatGPT&language=ko&sortBy=publishedAt&pageSize=10&apiKey=6944bc431cbf4988857f3cb35b4decc6"

// 로그 출력
console.error(`[MCP 서버] News API 호출: ${apiUrl}`);
```

**단계 5: 프록시를 통한 API 호출**
```javascript
// mcp-server.js:54-55줄 (프록시 설정)
const PROXY_URL = 'http://70.10.15.10:8080';
const proxyAgent = new HttpsProxyAgent(PROXY_URL);

// mcp-server.js:316줄 (API 호출)
const response = await fetchWithProxy(apiUrl);
// fetchWithProxy 함수는 프록시를 통해 HTTPS 요청 생성
// 타임아웃: 30초 (mcp-server.js:87줄)
```

**단계 6: API 응답 처리**
```javascript
// mcp-server.js:318-323줄
// 응답 상태 확인
if (!response.ok) {
  const errorData = await response.json().catch(() => ({}));
  throw new Error(`News API 오류: ${response.status} - ${errorData.message || response.statusText}`);
}

// JSON 파싱
const data = await response.json();
// data 구조: { status: "ok", totalResults: 100, articles: [...] }
```

**단계 7: 결과 검증**
```javascript
// mcp-server.js:326-335줄
// 결과가 없는 경우 처리
if (!data.articles || data.articles.length === 0) {
  return {
    content: [{
      type: 'text',
      text: `"${keyword}"에 대한 뉴스 기사를 찾을 수 없습니다.\n\n다른 키워드로 검색해보세요.`
    }]
  };
}
```

**단계 8: 데이터 필터링 및 포맷팅**
```javascript
// mcp-server.js:338-358줄
// 기사 데이터 필터링 및 포맷팅
const formattedArticles = data.articles
  .filter(article => article.title && article.title !== '[Removed]')
  .slice(0, 10)  // 최대 10개
  .map(article => {
    // 날짜 포맷팅
    const publishedDate = article.publishedAt 
      ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
          year: 'numeric',
          month: 'long',
          day: 'numeric'
        })
      : '날짜 정보 없음';

    return {
      title: article.title || '제목 없음',
      summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
      date: publishedDate,
      source: article.source?.name || '출처 정보 없음',
      category: '뉴스',
      url: article.url || '#'
    };
  });
```

**단계 9: 결과 문자열 생성**
```javascript
// mcp-server.js:361-370줄
// 결과 포맷팅
let articlesList = `🔍 "${keyword}"에 대한 뉴스 기사 검색 결과 (${formattedArticles.length}건)\n\n`;

formattedArticles.forEach((article, index) => {
  articlesList += `${index + 1}. ${article.title}\n`;
  articlesList += `   📝 요약: ${article.summary}\n`;
  articlesList += `   📅 날짜: ${article.date}\n`;
  articlesList += `   📰 출처: ${article.source}\n`;
  articlesList += `   🏷️ 카테고리: ${article.category}\n`;
  articlesList += `   🔗 링크: ${article.url}\n\n`;
});
```

**단계 10: 최종 결과 반환**
```javascript
// mcp-server.js:372-379줄
return {
  content: [{
    type: 'text',
    text: articlesList
  }]
};
```

**단계 11: 오류 처리 (발생 시)**
```javascript
// mcp-server.js:380-389줄
catch (error) {
  console.error('News API 오류:', error);
  return {
    content: [{
      type: 'text',
      text: `뉴스 검색 중 오류가 발생했습니다: ${error.message}\n\n잠시 후 다시 시도해주세요.`
    }],
    isError: true
  };
}
```

---

#### 📊 전체 처리 흐름 요약

```
1. 사용자 요청 수신
   ↓
2. AI 도구 선택 (search_ai_articles)
   ↓
3. 파라미터 추출 (keyword: "ChatGPT")
   ↓
4. 입력값 검증
   ↓
5. API URL 생성
   ↓
6. 프록시를 통한 API 호출
   ↓
7. 응답 상태 확인
   ↓
8. JSON 파싱
   ↓
9. 결과 검증 (기사 존재 여부)
   ↓
10. 데이터 필터링 및 포맷팅
   ↓
11. 결과 문자열 생성
   ↓
12. 최종 결과 반환
```

---

#### 🧪 테스트 방법

1. Cursor AI 채팅에서 "ChatGPT에 대한 최신 뉴스를 찾아줘" 입력
2. AI가 자동으로 `search_ai_articles` 도구 사용
3. 결과 확인: ChatGPT 관련 뉴스 기사 목록 표시

**예상 결과 형식:**
```
🔍 "ChatGPT"에 대한 뉴스 기사 검색 결과 (10건)

1. [기사 제목]
   📝 요약: [기사 요약]
   📅 날짜: 2025년 1월 15일
   📰 출처: [출처명]
   🏷️ 카테고리: 뉴스
   🔗 링크: [URL]

2. [기사 제목]
   ...
```

---

#### ⚠️ 참고 사항

**필수 요구사항:**
- News API 키가 필요합니다 (`NEWS_API_KEY`)
- 인터넷 연결이 필요합니다
- 프록시 설정이 되어 있어야 합니다 (`http://70.10.15.10:8080`)

**주요 설정 위치:**
- 프록시 설정: `mcp-server.js:54줄`
- API 키 설정: `mcp-server.js:37줄`
- 타임아웃 설정: `mcp-server.js:87줄` (30초)

**가능한 오류:**
- SSL 인증서 검증 실패: 프록시 인증서 설정 확인 필요
- API 키 오류: News API 키 유효성 확인
- 네트워크 오류: 인터넷 연결 및 프록시 설정 확인
- 결과 없음: 다른 키워드로 재시도

**오류 해결 방법:**
- SSL 인증서 오류: Node.js를 `--use-system-ca` 옵션으로 실행
- 프록시 오류: 프록시 서버 상태 확인
- API 키 오류: News API 웹사이트에서 키 재발급

---

### ✅ 테스트 3: 도서 추천 (`recommend_books`)

**요청:**
```
"인공지능 관련 책을 추천해줘"
```

---

#### 📋 예상 동작

1. Cursor AI가 `recommend_books` 도구를 자동으로 선택
2. 파라미터: `{ "query": "인공지능", "maxResults": 10 }`
3. MCP 서버 (`mcp-unified-server.py`)가 Google Books API 호출
4. 결과: 인공지능 관련 도서 10개 반환

---

#### 🔍 실제 코드 동작

```python
# mcp-unified-server.py의 recommend_books 핸들러
query = "인공지능"
max_results = 10
api_url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=10&langRestrict=ko"
data = fetch_google_books_api(api_url)

# 결과 포맷팅
return "'인공지능'에 대한 도서 추천 결과 (10건):\n\n1. [도서 제목]\n   저자: ...\n   출판사: ...\n   카테고리: ...\n   평점: ...\n   설명: ...\n   링크: ...\n\n..."
```

---

#### 🧪 테스트 방법

1. Cursor AI 채팅에서 "인공지능 관련 책을 추천해줘" 입력
2. AI가 자동으로 `recommend_books` 도구 사용
3. 결과 확인: 인공지능 관련 도서 목록 표시

---

#### ⚠️ 참고 사항

- Google Books API는 API 키가 필요 없습니다 (무료)
- 인터넷 연결이 필요합니다

---

### ✅ 테스트 4: MCP 도구 목록 조회

**요청:**
```
"사용 가능한 MCP 도구 목록을 보여줘"
```

---

#### 📋 예상 동작

1. Cursor AI가 등록된 모든 MCP 서버의 도구 목록을 조회
2. 결과: 8개 도구 목록 표시

---

#### 🔍 예상 결과

```
사용 가능한 MCP 도구 목록:

📦 ai-articles-radio-server (Node.js):
  1. search_ai_articles - AI 기사 검색
  2. get_radio_song - 라디오 현재 재생 노래
  3. get_radio_recent_songs - 라디오 최근 재생 노래
  4. recommend_similar_songs - 유사한 노래 추천

📦 unified-mcp-server (Python):
  5. add_numbers - 덧셈 계산기
  6. recommend_books - 도서 추천
  7. get_popular_books - 인기 도서 조회
  8. get_book_details - 도서 상세 정보 조회
```

---

#### 🧪 테스트 방법

1. Cursor AI 채팅에서 "사용 가능한 MCP 도구 목록을 보여줘" 입력
2. AI가 등록된 MCP 서버의 도구 목록 표시

---

## 🔧 MCP 서버 실행 확인

테스트 전에 MCP 서버가 실행 중인지 확인하세요:

### 방법 1: 자동 실행 (권장)
```bash
start-servers.bat
```
이 명령어로 모든 서버가 자동으로 시작됩니다.

### 방법 2: 개별 실행
```bash
# Node.js MCP 서버
npm run mcp-server

# Python MCP 서버
npm run mcp-unified
```

### 확인 방법
서버가 정상적으로 실행되면:
- `mcp-server.js`: "MCP AI 기사 검색 및 라디오 방송 서버가 시작되었습니다."
- `mcp-unified-server.py`: "통합 MCP 서버가 시작되었습니다."

---

## ⚠️ 문제 해결

### 문제 1: MCP 도구가 사용되지 않아요

**원인:**
- MCP 서버가 실행되지 않음
- Cursor 설정 파일이 잘못됨
- Cursor가 재시작되지 않음

**해결 방법:**
1. MCP 서버 실행 확인
2. `cursor-mcp-config.json` 파일 경로 확인
3. Cursor 완전히 재시작

### 문제 2: "도구를 찾을 수 없습니다" 오류

**원인:**
- MCP 서버가 등록되지 않음
- 서버 이름이 잘못됨

**해결 방법:**
1. `cursor-mcp-config.json` 파일 확인
2. 서버 이름이 정확한지 확인:
   - `ai-articles-radio-server`
   - `unified-mcp-server`

### 문제 3: API 호출 실패

**원인:**
- 인터넷 연결 문제
- API 키 문제
- 프록시 설정 문제

**해결 방법:**
1. 인터넷 연결 확인
2. API 키 확인 (News API, Last.fm API)
3. 프록시 설정 확인

---

## 📊 테스트 체크리스트

- [ ] MCP 서버 실행 확인
- [ ] Cursor 재시작 완료
- [ ] 덧셈 계산기 테스트 성공
- [ ] AI 기사 검색 테스트 성공
- [ ] 도서 추천 테스트 성공
- [ ] 도구 목록 조회 성공

---

## 🎯 추가 테스트 예시

### 더 많은 테스트 케이스:

```
"10과 20을 더해줘"
→ add_numbers (10, 20) = 30

"머신러닝 뉴스를 찾아줘"
→ search_ai_articles ("머신러닝")

"소설 책을 추천해줘"
→ recommend_books ("소설")

"KBS 쿨FM에서 지금 무슨 노래가 나오고 있어?"
→ get_radio_song ("kbs")

"Dynamite와 비슷한 노래를 추천해줘"
→ recommend_similar_songs ("Dynamite", "BTS")

"인기 도서 목록 보여줘"
→ get_popular_books ()

"도서 ID abc123의 상세 정보를 알려줘"
→ get_book_details ("abc123")
```

---

**작성일**: 2025년 1월
**버전**: 1.0.0



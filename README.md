# AI 기반 뉴스/음악/도서 추천 시스템

Vue 3 + Vite 기반의 실시간 뉴스 검색, 음악 추천, 도서 추천 및 MCP 서버를 포함한 통합 시스템입니다.

## 🚀 빠른 시작

### 1. 의존성 설치

```bash
# Node.js 패키지
npm install

# Python 패키지
pip install mcp playwright
playwright install chromium
```

### 2. 환경 변수 설정

`.env` 파일을 생성하고 API 키를 설정하세요:

```env
NEWS_API_KEY=your_news_api_key_here
LASTFM_API_KEY=your_lastfm_api_key_here
JWT_SECRET=your_secret_key_here
JWT_EXPIRES_IN=7d
```

### 3. 모든 서버 실행

**Windows (권장):**
```bash
start-dev.bat
```

또는 개발 환경만 실행:
```bash
start-dev.bat
```

### 4. 브라우저 접속

```
http://localhost:5173
```

## 📋 주요 기능

- ✅ **AI 뉴스 검색**: 키워드 기반 AI 관련 뉴스 검색 및 분석
- ✅ **경제 뉴스 검색**: 최신 경제 뉴스 자동 검색 및 중요도 분석
- ✅ **음악 추천**: Last.fm API를 활용한 음악 추천
- ✅ **라디오 수집**: 실시간 라디오 방송 노래 수집 및 현황 관리
- ✅ **도서 추천**: Google Books API를 활용한 도서 검색 및 추천
- ✅ **사용자 인증**: 회원가입, 로그인, JWT 토큰 기반 인증
- ✅ **사용자 관리**: 프로필 수정, 데이터 조회, API 키 관리
- ✅ **API 키 인증**: 외부에서 API를 사용할 수 있는 API 키 시스템
- ✅ **MCP 서버**: Cursor AI에서 사용 가능한 MCP 서버 제공

## 🏗️ 프로젝트 구조

```
test02/
├── src/                          # Vue 프론트엔드
│   ├── App.vue                   # 메인 화면
│   ├── stores/auth.js            # 인증 상태 관리
│   └── style.css                 # 스타일
├── api-server.js                 # 백엔드 API 서버 (포트 3001)
├── database.js                   # SQLite 데이터베이스 관리
├── mcp-unified-server.py         # 통합 MCP 서버 (Python)
├── mcp-server.js                 # Node.js MCP 서버
├── start-dev.bat                 # 개발 환경 실행
└── 가이드.md                      # 상세 가이드 문서
```

## 🔧 서버 포트

| 서버 | 포트 | 실행 명령어 |
|------|------|------------|
| API 서버 | 3001 | `npm run api-server` |
| Python HTTP 서버 | 3002 | `npm run screen-validator-server` |
| Vite 개발 서버 | 5173 | `npm run dev` |

## 📚 상세 가이드

**통합 가이드:** [`가이드.md`](./가이드.md) - 모든 기능과 설정 방법 포함

## 🛠️ npm 스크립트

```bash
npm run dev                    # Vite 개발 서버
npm run api-server             # API 서버 실행
npm run mcp-server             # Node.js MCP 서버 실행
npm run mcp-unified            # Python MCP 서버 실행
npm run screen-validator-server # Python HTTP 서버 실행
```

## 🔑 API 키 사용

1. 웹사이트에 로그인
2. "사용자 관리하기" → "API 키 관리" 탭
3. "➕ 새 API 키 생성" 버튼 클릭
4. 생성된 API 키로 외부에서 API 호출 가능

**예제:**
```bash
curl -H "X-API-Key: YOUR_API_KEY" \
  "http://localhost:3001/api/news?q=AI"
```

## 📖 API 문서

Swagger UI: `http://localhost:3001/api-docs`

## 🐍 MCP 서버 설정

`cursor-mcp-config.json` 파일에 MCP 서버 설정:

```json
{
  "mcpServers": {
    "unified-mcp-server": {
      "command": "python",
      "args": ["mcp-unified-server.py"],
      "cwd": "C:/test/test02"
    }
  }
}
```

## 💾 데이터 저장

- **localStorage**: 브라우저 임시 저장
- **SQLite**: `data/database.db` (영구 저장)

## ❓ 문제 해결

자세한 문제 해결 방법은 [`가이드.md`](./가이드.md)의 "문제 해결" 섹션을 참조하세요.

## 📄 라이선스

이 프로젝트는 개인 사용 목적으로 제작되었습니다.

---

**마지막 업데이트**: 2024년 12월

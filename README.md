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

**자동 실행 설정 (부팅 시 자동 시작):**
```bash
install-auto-start.bat
```
이 스크립트를 실행하면 Windows 시작 프로그램에 등록되어 컴퓨터 부팅 시 자동으로 서버가 시작됩니다.

**VDI 환경에서 재부팅 시 자동 시작:**
- VDI 재부팅 후 자동으로 서버가 시작됩니다
- "autostarting?" 메시지가 나타날 수 있습니다 (정상 동작)
- 자세한 내용: [`docs/자동_실행_가이드.md`](./docs/자동_실행_가이드.md)

**서버 자동 재시작 (항상 실행 유지):**
```bash
auto-start-servers.bat
```
서버가 종료되면 자동으로 재시작합니다.

**모든 서버 종료:**
```bash
stop-all-servers.bat
```

### 4. 브라우저 접속

```
http://localhost:5173
```

## 📋 주요 기능

- ✅ **AI 뉴스 검색**: 키워드 기반 AI 관련 뉴스 검색 및 분석 (MCP 서버 통합)
- ✅ **경제 뉴스 검색**: 최신 경제 뉴스 자동 검색 및 중요도 분석 (MCP 서버 통합)
- ✅ **음악 추천**: Last.fm API를 활용한 음악 추천
- ✅ **라디오 수집**: 실시간 라디오 방송 노래 수집 및 현황 관리
- ✅ **도서 추천**: Google Books API를 활용한 도서 검색 및 추천 (MCP 서버 통합)
- ✅ **에러 로그 분석**: 자동 에러 로그 분석 및 조치 방법 제안 (MCP 서버)
- ✅ **SQL 쿼리 분석**: PostgreSQL 쿼리 구조, 성능, 보안 분석 (MCP 서버)
- ✅ **테이블 영향도 분석**: 데이터베이스 스키마 변경 영향도 분석 (MCP 서버)
- ✅ **VOC 자동 대응**: Confluence 연동, Git 기반 유사 SR 검색, DB 변경 분석 (MCP 서버)
- ✅ **사용자 인증**: 회원가입, 로그인, JWT 토큰 기반 인증
- ✅ **사용자 관리**: 프로필 수정, 데이터 조회, API 키 관리, DB 스키마 조회, Docker 상태 관리
- ✅ **API 키 인증**: 외부에서 API를 사용할 수 있는 API 키 시스템
- ✅ **MCP 서버 통합**: 모든 주요 기능이 MCP 서버로 제공되어 Cursor AI와 통합 가능
- ✅ **VDI 환경 지원**: VDI 재부팅 시 자동 서버 시작 기능

## 🏗️ 프로젝트 구조

```
test02/
├── src/                          # Vue 프론트엔드
│   ├── App.vue                   # 메인 화면
│   ├── components/               # 컴포넌트
│   │   ├── features/             # 기능별 컴포넌트 (리팩토링 진행 중)
│   │   ├── modals/               # 모달 컴포넌트
│   │   ├── LoginModal.vue        # 로그인 모달
│   │   └── SignupModal.vue       # 회원가입 모달
│   ├── services/                 # API 서비스 레이어 (신규)
│   │   ├── api.js                # 기본 API 호출 함수
│   │   └── newsService.js        # 뉴스 관련 API 서비스
│   ├── stores/                   # 상태 관리
│   │   └── auth.js               # 인증 상태 관리
│   ├── utils/                    # 유틸리티 함수 (신규)
│   │   └── helpers.js            # 공통 헬퍼 함수
│   └── style.css                 # 스타일
├── api-server.js                 # 백엔드 API 서버 (포트 3001)
├── database.js                   # SQLite 데이터베이스 관리
├── mcp-unified-server.py         # 통합 MCP 서버 (Python)
├── mcp-server.js                 # Node.js MCP 서버
├── start-dev.bat                 # 개발 환경 실행
└── 가이드.md                      # 통합 가이드 문서
```

> **💡 리팩토링 진행 중**: 코드 구조 개선을 위해 컴포넌트와 서비스를 모듈화하고 있습니다. 자세한 내용은 [`코드_구조_개선_계획.md`](./코드_구조_개선_계획.md)를 참조하세요.

## 🔧 서버 포트

| 서버 | 포트 | 실행 명령어 |
|------|------|------------|
| API 서버 | 3001 | `npm run api-server` |
| Python HTTP 서버 | 3002 | `npm run screen-validator-server` |
| Vite 개발 서버 | 5173 | `npm run dev` |

## 📚 상세 가이드

**통합 가이드:** [`가이드.md`](./가이드.md) - 모든 기능과 설정 방법 포함

### 주요 가이드 문서
- 📖 [`가이드.md`](./가이드.md) - 프로젝트 완전 가이드 (통합 가이드)
- 🤖 [`MCP_서버_완전_가이드.md`](./MCP_서버_완전_가이드.md) - MCP 서버 상세 가이드
- 🚀 [`docs/자동_실행_가이드.md`](./docs/자동_실행_가이드.md) - 서버 자동 실행 가이드 (VDI 재부팅 포함)
- 🌿 [`docs/VOC_자동_대응_MCP_서버_가이드.md`](./docs/VOC_자동_대응_MCP_서버_가이드.md) - VOC 자동 대응 가이드
- 🐳 [`docs/VDI_환경_Docker_설치_가이드.md`](./docs/VDI_환경_Docker_설치_가이드.md) - VDI 환경 Docker 설치 가이드
- 🔗 [`Git_통합_가이드.md`](./Git_통합_가이드.md) - Git 사용법
- 🌐 [`GitHub_통합_가이드.md`](./GitHub_통합_가이드.md) - GitHub 사용법

## 🛠️ npm 스크립트

```bash
npm run dev                    # Vite 개발 서버
npm run api-server             # API 서버 실행
npm run mcp-server             # Node.js MCP 서버 실행
npm run mcp-unified            # Python MCP 서버 실행
npm run screen-validator-server # Python HTTP 서버 실행
npm run build                  # 프론트엔드 빌드
```

## 🐳 Docker 빌드 및 배포

> **✅ MCP 서버 통합 완료**: Docker 이미지에 모든 MCP 서버가 포함되어 있습니다.

### 빠른 시작

```bash
# 빌드 및 배포
scripts\docker-build.bat       # Windows
scripts\docker-deploy.bat      # Windows

./scripts/docker-build.sh      # Linux/macOS
./scripts/docker-deploy.sh     # Linux/macOS
```

**Docker 이미지 구성:**
- **Backend 이미지**: `mcp-server.js` 포함 (뉴스 검색 등)
- **Python 이미지**: 모든 Python MCP 서버 포함 (에러 로그, SQL 쿼리, 영향도 분석 등)

### Docker 명령어

```bash
# 프로덕션 빌드 및 실행
docker-compose up -d --build

# 개발 환경 실행
docker-compose -f docker-compose.dev.yml up -d

# 서비스 중지
docker-compose down

# 로그 확인
docker-compose logs -f
```

> **📖 상세 가이드**: [`docs/Docker_빌드_배포_가이드.md`](./docs/Docker_빌드_배포_가이드.md) - Docker 빌드 및 배포 완전 가이드

## 🎯 다음 작업 가이드

프로젝트 개선을 위한 우선순위별 작업 목록:

- 🔴 **긴급**: 보안 강화 (하드코딩된 API 키 제거, Rate Limiting)
- 🟡 **중요**: 컴포넌트 분리 계속, 테스트 추가
- 🟢 **중간**: 성능 최적화, 백엔드 모듈화

> **📋 상세 가이드**: [`가이드.md`](./가이드.md) - 프로젝트 완전 가이드

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

**마지막 업데이트**: 2025년 1월

---

## 🔄 최근 변경사항

### 2025년 1월 - 완전 MCP 서버화 완료 ✅
- ✅ **뉴스 기능 MCP 서버화**: API 서버가 MCP 서버의 뉴스 검색 함수를 직접 호출
- ✅ **에러 로그 분석 MCP 서버화**: 발생시간별로 별도 row 저장, 원본 로그 표시 개선
- ✅ **모든 주요 기능 MCP 서버화 완료**: 뉴스, 에러 로그, SQL 쿼리, 도서 추천 등
- ✅ 코드 중복 제거 및 일관성 향상
- 📝 자세한 내용: [`MCP_서버_완전_가이드.md`](./MCP_서버_완전_가이드.md)

### 2025년 1월 - 코드 구조 개선
- ✅ 유틸리티 함수 분리 (`src/utils/helpers.js`)
- ✅ API 서비스 레이어 생성 (`src/services/`)
- ✅ 컴포넌트 구조 개선 진행 중

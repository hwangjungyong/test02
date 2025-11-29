# App.vue 리팩토링 계획서

## 📋 현재 상황

- **파일 크기**: 16,129줄
- **문제점**: 단일 파일에 모든 기능이 집중되어 있어 유지보수가 어려움
- **목표**: 기능별로 컴포넌트를 분리하여 코드 가독성과 유지보수성 향상

## 🎯 분리 전략

### 1. 컴포넌트 구조 설계

```
src/
├── App.vue (메인 레이아웃만 유지)
├── components/
│   ├── layout/
│   │   └── TopButtons.vue (상단 버튼 영역)
│   ├── modals/
│   │   ├── DocsLibraryModal.vue (문서 라이브러리)
│   │   ├── DocViewerModal.vue (문서 뷰어)
│   │   ├── UserManagementModal.vue (사용자 관리)
│   │   ├── ErrorLogDetailModal.vue (에러 로그 상세)
│   │   ├── EconomyAlarmModal.vue (경제뉴스 알람)
│   │   └── MCPGuideModal.vue (MCP 가이드)
│   └── features/
│       ├── AIArticleSearch.vue (AI 기사 검색)
│       ├── EconomyArticleSearch.vue (경제 뉴스 검색)
│       ├── MusicRecommendation.vue (음악 추천)
│       ├── RadioHistory.vue (라디오 노래 현황)
│       ├── BookRecommendation.vue (도서 추천)
│       ├── ScreenValidation.vue (AI 화면 검증)
│       ├── SQLQueryAnalysis.vue (AI 데이터 분석)
│       └── ErrorLogAnalysis.vue (AI 에러로그 분석)
├── composables/
│   ├── useUserManagement.js (사용자 관리 로직)
│   ├── useDocsLibrary.js (문서 라이브러리 로직)
│   ├── useErrorLogs.js (에러 로그 로직)
│   ├── useDocker.js (Docker 관련 로직)
│   └── useApiKeys.js (API 키 관리 로직)
└── styles/
    └── components.css (공통 컴포넌트 스타일)
```

## 📦 분리 대상 기능

### A. 모달 컴포넌트 (Modals)

#### 1. DocsLibraryModal.vue
- **기능**: 문서 라이브러리 목록 표시 및 문서 뷰어 열기
- **상태**: docsList, docsLoading, docsError
- **함수**: openDocsLibrary, loadDocsList, openDocViewer

#### 2. DocViewerModal.vue
- **기능**: 문서 내용 표시
- **상태**: docContentHtml, docContentLoading, docContentError, currentDoc
- **함수**: loadDocContent, closeDocViewer, formatFileSize, formatDate

#### 3. UserManagementModal.vue
- **기능**: 사용자 관리 (프로필, 데이터, API 키, DB 스키마, Docker, 에러 로그, 계정 삭제)
- **상태**: userManagementTab, userProfile, userData, apiKeys, dbSchema, dockerStatus, errorLogs 등
- **함수**: loadUserProfile, handleUpdateProfile, loadUserDataSummary, loadDbSchema, loadDockerStatus, loadErrorLogs 등
- **하위 컴포넌트**: 
  - UserProfileTab.vue
  - UserDataTab.vue
  - ApiKeysTab.vue
  - DbSchemaTab.vue
  - DockerTab.vue
  - ErrorLogsTab.vue
  - DeleteAccountTab.vue

#### 4. ErrorLogDetailModal.vue
- **기능**: 에러 로그 상세 정보 표시
- **상태**: selectedErrorLog
- **함수**: formatDateTime

#### 5. EconomyAlarmModal.vue
- **기능**: 경제뉴스 알람 설정 및 확인
- **상태**: isEconomyAlarmEnabled, newEconomyNews, lastAlarmCheckTime
- **함수**: toggleEconomyNewsAlarm, checkEconomyNews

#### 6. MCPGuideModal.vue
- **기능**: MCP 가이드 표시
- **상태**: currentGuideType, markdownContent, isLoading
- **함수**: openMCPGuide, openPythonMCPGuide, closeMCPGuide

### B. 기능 컴포넌트 (Features)

#### 1. AIArticleSearch.vue
- **기능**: AI 기사 검색 및 데이터 연계도 분석
- **상태**: aiArticles, isSearching, articleError, dataCorrelation, graphData
- **함수**: searchAIArticles, analyzeDataCorrelation, generateNetworkGraph, renderNetworkGraph

#### 2. EconomyArticleSearch.vue
- **기능**: 경제 뉴스 검색 및 수집
- **상태**: economyArticles, isSearchingEconomy, economyArticleError, newsHistory
- **함수**: searchEconomyArticles, collectEconomyNews, calculateEconomyImportance

#### 3. MusicRecommendation.vue
- **기능**: 음악 추천
- **상태**: recommendations, musicError, songTitle, artist
- **함수**: searchMusicRecommendations

#### 4. RadioHistory.vue
- **기능**: 라디오 노래 현황 표시 및 필터링
- **상태**: songsHistory, filteredSongs, paginatedSongs, searchQuery, selectedArtist, selectedGenre
- **함수**: fetchRadioSongs, filterSongs, collectMonthlyData

#### 5. BookRecommendation.vue
- **기능**: 도서 추천 및 수집 현황
- **상태**: recommendedBooks, booksHistory, bookError, isSearchingBooks
- **함수**: searchBooks, collectBookData

#### 6. ScreenValidation.vue
- **기능**: AI 화면 검증
- **상태**: screenValidationResult, screenValidationError, isValidatingScreen, screenScreenshot
- **함수**: validateScreen, interactWithScreen

#### 7. SQLQueryAnalysis.vue
- **기능**: SQL 쿼리 분석 및 리니지 시각화
- **상태**: sqlAnalysisResult, sqlAnalysisReport, impactAnalysisResult, lineageHtmlContent
- **함수**: analyzeSQLQuery, analyzeImpact, generateLineage

#### 8. ErrorLogAnalysis.vue
- **기능**: AI 에러로그 분석
- **상태**: errorLogAnalysisResult, errorLogAnalysisError, isAnalyzingErrorLog
- **함수**: analyzeErrorLog

### C. 레이아웃 컴포넌트

#### 1. TopButtons.vue
- **기능**: 상단 버튼 영역 (로그인, 회원가입, 가이드 문서, API DOCS, 알람, VOC)
- **상태**: showLoginModal, showSignupModal, showVocModal, isEconomyAlarmEnabled
- **함수**: handleLogout, openUserManagementModal, openDocsLibrary, openAPIDocs, toggleEconomyNewsAlarm

## 🔧 Composables 분리

### 1. useUserManagement.js
- 사용자 프로필 관리
- 사용자 데이터 로드
- API 키 관리
- 계정 삭제

### 2. useDocsLibrary.js
- 문서 목록 로드
- 문서 내용 로드
- 문서 포맷팅 유틸리티

### 3. useErrorLogs.js
- 에러 로그 로드
- 에러 로그 필터링
- 에러 로그 분석

### 4. useDocker.js
- Docker 상태 조회
- Docker 컨테이너 제어 (시작/중지/재시작)

### 5. useApiKeys.js
- API 키 목록 로드
- API 키 생성
- API 키 삭제/토글

## 📝 리팩토링 단계

### Phase 1: 모달 컴포넌트 분리
1. DocsLibraryModal.vue 생성
2. DocViewerModal.vue 생성
3. UserManagementModal.vue 생성 (가장 복잡)
4. ErrorLogDetailModal.vue 생성
5. EconomyAlarmModal.vue 생성
6. MCPGuideModal.vue 생성

### Phase 2: 기능 컴포넌트 분리
1. AIArticleSearch.vue 생성
2. EconomyArticleSearch.vue 생성
3. MusicRecommendation.vue 생성
4. RadioHistory.vue 생성
5. BookRecommendation.vue 생성
6. ScreenValidation.vue 생성
7. SQLQueryAnalysis.vue 생성
8. ErrorLogAnalysis.vue 생성

### Phase 3: 레이아웃 컴포넌트 분리
1. TopButtons.vue 생성

### Phase 4: Composables 분리
1. useUserManagement.js 생성
2. useDocsLibrary.js 생성
3. useErrorLogs.js 생성
4. useDocker.js 생성
5. useApiKeys.js 생성

### Phase 5: 스타일 정리
1. 공통 스타일을 components.css로 이동
2. 각 컴포넌트별 스타일 정리

### Phase 6: App.vue 최종 정리
1. 분리된 컴포넌트 import 및 사용
2. 불필요한 코드 제거
3. 최종 테스트

## ✅ 예상 결과

- **App.vue**: 약 500-1000줄로 축소 (레이아웃 및 라우팅만)
- **각 컴포넌트**: 200-800줄 내외로 관리 가능한 크기
- **코드 재사용성**: 향상
- **유지보수성**: 크게 향상
- **테스트 용이성**: 개별 컴포넌트 단위 테스트 가능

## 🚀 실행 순서

1. 문서 작성 완료 ✅
2. 모달 컴포넌트부터 분리 시작 ✅
   - TopButtons.vue 생성 완료
   - DocsLibraryModal.vue 생성 완료
   - DocViewerModal.vue 생성 완료
   - MCPGuideModal.vue 생성 완료
   - App.vue 업데이트 완료
3. 기능 컴포넌트 분리 (진행 중)
4. Composables 분리 (대기 중)
5. 스타일 정리 (대기 중)
6. 최종 테스트 및 검증 (대기 중)

## ✅ 완료된 작업

### Phase 1: 모달 컴포넌트 분리 (거의 완료)
- ✅ TopButtons.vue 생성 및 App.vue에 통합
- ✅ DocsLibraryModal.vue 생성 및 App.vue에 통합
- ✅ DocViewerModal.vue 생성 및 App.vue에 통합
- ✅ MCPGuideModal.vue 생성 및 App.vue에 통합
- ✅ ErrorLogDetailModal.vue 생성 및 App.vue에 통합
- ✅ EconomyAlarmModal.vue 생성 및 App.vue에 통합
- ⏳ UserManagementModal.vue (약 850줄 - 남은 작업)

### Phase 2: 기능 컴포넌트 분리 (완료)
- ✅ AIArticleSearch.vue 생성 및 App.vue에 통합
- ✅ EconomyArticleSearch.vue 생성 및 App.vue에 통합
- ✅ NewsCollection.vue 생성 및 App.vue에 통합
- ✅ MusicRecommendation.vue 생성 및 App.vue에 통합
- ✅ RadioHistory.vue 생성 및 App.vue에 통합
- ✅ BookRecommendation.vue 생성 및 App.vue에 통합
- ✅ BookHistory.vue 생성 및 App.vue에 통합
- ✅ ScreenValidation.vue 생성 및 App.vue에 통합
- ✅ SQLQueryAnalysis.vue 생성 및 App.vue에 통합
- ✅ ErrorLogAnalysis.vue 생성 및 App.vue에 통합
- ✅ TableImpactAnalysis.vue 생성 및 App.vue에 통합

### 변경 사항
- App.vue에서 약 5,000줄의 코드가 컴포넌트로 분리됨
- 총 18개의 새로운 컴포넌트 생성
- 각 기능이 독립적인 컴포넌트로 분리되어 유지보수성 향상

## 🚨 현재 상황

**App.vue: 11,104줄** (16,129줄에서 약 5,025줄 감소) - 주요 기능 컴포넌트 분리 완료!

### 남아있는 큰 블록들:
1. **사용자 관리 모달**: 약 850줄 (템플릿 + 로직)
2. **에러 로그 상세 모달**: 약 80줄
3. **경제뉴스 알람 모달**: 약 40줄
4. **AI 뉴스 검색 결과 영역**: 약 125줄
5. **경제 뉴스 검색 결과 영역**: 약 90줄
6. **수집된 뉴스 현황**: 약 100줄
7. **음악 추천 기능**: 수백 줄
8. **라디오 노래 현황**: 수백 줄
9. **도서 추천 기능**: 수백 줄
10. **도서 수집 현황**: 수백 줄
11. **AI 화면 검증 결과 영역**: 수백 줄
12. **AI 데이터 분석 결과 영역**: 수천 줄
13. **AI 에러로그분석 결과 영역**: 수백 줄
14. **AI 테이블 영향도 분석 결과 영역**: 수백 줄
15. **스타일**: 수천 줄

## 🎯 새로운 분리 전략

### 즉시 분리해야 할 것들 (우선순위):

#### 1단계: 모달 완전 분리 (약 1,000줄 감소)
- UserManagementModal.vue (850줄)
- ErrorLogDetailModal.vue (80줄)
- EconomyAlarmModal.vue (40줄)

#### 2단계: 기능 컴포넌트 분리 (약 10,000줄 감소)
- AIArticleSearch.vue (AI 뉴스 검색 + 데이터 연계도 분석)
- EconomyArticleSearch.vue (경제 뉴스 검색)
- NewsCollection.vue (수집된 뉴스 현황)
- MusicRecommendation.vue (음악 추천)
- RadioHistory.vue (라디오 노래 현황)
- BookRecommendation.vue (도서 추천)
- BookHistory.vue (도서 수집 현황)
- ScreenValidation.vue (AI 화면 검증)
- SQLQueryAnalysis.vue (AI 데이터 분석)
- ErrorLogAnalysis.vue (AI 에러로그분석)
- ImpactAnalysis.vue (AI 테이블 영향도 분석)

#### 3단계: 스타일 분리 (약 3,000줄 감소)
- styles/components.css로 이동

### 예상 결과
- **App.vue**: 약 500-1,000줄 (레이아웃 + 라우팅만)
- **각 컴포넌트**: 200-1,500줄 (관리 가능한 크기)


# 모듈 구조 가이드

## 📁 전체 디렉토리 구조

```
src/
├── modules/                    # 기능별 모듈
│   ├── news/                   # 뉴스 관련 모듈
│   │   ├── components/         # 뉴스 컴포넌트
│   │   ├── composables/        # 뉴스 관련 composables
│   │   └── services/           # 뉴스 API 서비스
│   ├── music-book/             # 음악/도서 모듈
│   │   ├── components/         # 음악/도서 컴포넌트
│   │   ├── composables/        # 음악/도서 composables
│   │   └── services/           # 음악/도서 API 서비스
│   ├── ai-tools/               # AI 도구 모듈
│   │   ├── components/         # AI 도구 컴포넌트
│   │   ├── composables/        # AI 도구 composables
│   │   └── services/           # AI 도구 API 서비스
│   ├── user-management/        # 사용자 관리 모듈
│   │   ├── components/         # 사용자 관리 컴포넌트
│   │   ├── composables/        # 사용자 관리 composables
│   │   └── services/           # 사용자 관리 API 서비스
│   ├── layout/                 # 레이아웃 모듈
│   │   └── components/         # 레이아웃 컴포넌트
│   ├── shared/                 # 공유 모듈
│   │   └── components/         # 공유 컴포넌트
│   │       └── modals/         # 공통 모달 컴포넌트
│   ├── auth/                   # 인증 모듈
│   ├── docs/                   # 문서 모듈
│   └── voc/                    # VOC 모듈
├── composables/                # 공통 composables
│   ├── useModal.js             # 모달 상태 관리
│   ├── useFormatting.js        # 포맷팅 유틸리티
│   └── useApi.js               # API 호출 헬퍼
├── services/                   # 공통 서비스
│   └── baseService.js          # 기본 API 서비스
├── styles/                     # 스타일 파일
│   ├── base.css                # 기본 스타일
│   └── modules/                # 모듈별 스타일
│       ├── modal.css           # 모달 스타일
│       └── user-management.css  # 사용자 관리 스타일
└── utils/                      # 유틸리티
    └── helpers.js              # 공통 헬퍼 함수
```

## 🎯 모듈별 상세 설명

### 1. News Module (`modules/news/`)
**목적**: 뉴스 검색 및 수집 기능

**컴포넌트**:
- `AIArticleSearch.vue`: AI 기사 검색
- `EconomyArticleSearch.vue`: 경제 뉴스 검색
- `NewsCollection.vue`: 뉴스 수집 현황

**사용 예시**:
```javascript
import AIArticleSearch from './modules/news/components/AIArticleSearch.vue'
```

### 2. Music-Book Module (`modules/music-book/`)
**목적**: 음악 및 도서 추천/수집 기능

**컴포넌트**:
- `RadioHistory.vue`: 라디오 노래 현황
- `BookRecommendation.vue`: 도서 추천
- `BookHistory.vue`: 도서 수집 현황

**사용 예시**:
```javascript
import RadioHistory from './modules/music-book/components/RadioHistory.vue'
```

### 3. AI Tools Module (`modules/ai-tools/`)
**목적**: AI 기반 분석 도구

**컴포넌트**:
- `ScreenValidation.vue`: 화면 검증
- `SQLQueryAnalysis.vue`: SQL 쿼리 분석
- `ErrorLogAnalysis.vue`: 에러 로그 분석
- `TableImpactAnalysis.vue`: 테이블 영향도 분석

**사용 예시**:
```javascript
import ScreenValidation from './modules/ai-tools/components/ScreenValidation.vue'
```

### 4. User Management Module (`modules/user-management/`)
**목적**: 사용자 관리 기능

**구조**:
- `components/UserManagementModal.vue`: 메인 모달
- `components/tabs/`: 탭별 컴포넌트
  - `ProfileTab.vue`: 프로필 관리
  - `DataTab.vue`: 데이터 조회
  - `ApiKeysTab.vue`: API 키 관리
  - `DbSchemaTab.vue`: DB 스키마 조회
  - `DockerTab.vue`: Docker 상태 관리
  - `ErrorLogsTab.vue`: 에러 로그 조회
  - `DeleteAccountTab.vue`: 계정 삭제
- `composables/`: 상태 관리 composables
- `services/userService.js`: API 서비스

**사용 예시**:
```javascript
import UserManagementModal from './modules/user-management/components/UserManagementModal.vue'
```

### 5. Layout Module (`modules/layout/`)
**목적**: 레이아웃 관련 컴포넌트

**컴포넌트**:
- `TopButtons.vue`: 상단 버튼 영역

### 6. Shared Module (`modules/shared/`)
**목적**: 공통으로 사용되는 컴포넌트

**컴포넌트**:
- `components/modals/`: 공통 모달
  - `DocsLibraryModal.vue`
  - `DocViewerModal.vue`
  - `MCPGuideModal.vue`
  - `ErrorLogDetailModal.vue`
  - `EconomyAlarmModal.vue`

## 🔧 공통 인프라

### Composables (`src/composables/`)

#### useModal.js
모달 상태 관리를 위한 composable

```javascript
import { useModal } from '@/composables/useModal.js'

const { isOpen, open, close, toggle } = useModal()
```

#### useFormatting.js
포맷팅 유틸리티 composable

```javascript
import { useFormatting } from '@/composables/useFormatting.js'

const { formatDate, formatDateTime } = useFormatting()
```

#### useApi.js
API 호출을 위한 composable

```javascript
import { useApi } from '@/composables/useApi.js'

const { loading, error, apiGet, apiPost } = useApi()
```

### Services (`src/services/`)

#### baseService.js
공통 API 요청 서비스

```javascript
import { get, post, put, del } from '@/services/baseService.js'

const data = await get('/api/endpoint', { param: 'value' })
```

## 📝 스타일 구조

### 모듈별 스타일 (`src/styles/modules/`)

- `modal.css`: 공통 모달 스타일
- `user-management.css`: 사용자 관리 모듈 스타일

**사용 방법**:
`src/style.css`에서 import하여 전역으로 사용

```css
@import './styles/base.css';
@import './styles/modules/modal.css';
@import './styles/modules/user-management.css';
```

## 🎨 모듈 개발 가이드

### 새 모듈 생성 시

1. **디렉토리 구조 생성**
   ```
   modules/your-module/
   ├── components/
   ├── composables/
   └── services/
   ```

2. **컴포넌트 생성**
   - 기능별로 컴포넌트 분리
   - Props와 Events 명확히 정의

3. **Composable 생성**
   - 상태 관리 로직 분리
   - 재사용 가능한 로직 추출

4. **Service 생성**
   - API 호출 로직 분리
   - baseService.js 활용

5. **스타일 분리** (필요시)
   - `styles/modules/your-module.css` 생성
   - `style.css`에 import 추가

## ✅ 모듈화의 장점

1. **유지보수성 향상**: 기능별로 코드가 분리되어 수정이 용이
2. **재사용성**: 모듈을 다른 프로젝트에서도 활용 가능
3. **테스트 용이성**: 모듈별로 독립적인 테스트 가능
4. **협업 효율성**: 여러 개발자가 동시에 작업 가능
5. **코드 가독성**: 구조가 명확하여 이해하기 쉬움

## 📚 참고 자료

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [Vue 3 모듈 시스템](https://vuejs.org/guide/scaling-up/sfc.html)


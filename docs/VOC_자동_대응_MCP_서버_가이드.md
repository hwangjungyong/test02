# VOC 자동 대응 MCP 서버 가이드

**작성일**: 2025년 11월  
**버전**: 1.0.0

> VOC(Voice of Customer) 자동 대응을 위한 MCP 서버 시스템 사용 가이드

---

## 📋 목차

1. [VOC 자동 대응 시스템 개요](#1-voc-자동-대응-시스템-개요)
2. [주요 기능](#2-주요-기능)
3. [시스템 구성](#3-시스템-구성)
4. [사용 방법](#4-사용-방법)
5. [API 엔드포인트](#5-api-엔드포인트)
6. [환경 설정](#6-환경-설정)
7. [샘플 데이터](#7-샘플-데이터)

---

## 1. VOC 자동 대응 시스템 개요

VOC 자동 대응 시스템은 고객의 SR(Service Request)을 자동으로 처리하고 관리하는 통합 시스템입니다.

### 주요 특징

- **Confluence 연동**: Confluence 페이지에서 SR을 자동으로 추출
- **Git 기반 검색**: 유사한 SR 처리 내역을 Git 저장소에서 검색
- **DB 변경 분석**: 테이블/컬럼 변경 사항을 자동으로 감지 및 분석
- **에러 로그 연동**: AI 에러 로그 분석 결과와 연동하여 SR 이력 자동 생성

---

## 2. 주요 기능

### 2.1 SR 입력 및 관리

- Confluence URL을 통한 자동 SR 생성
- 수동 SR 입력
- SR 상태 관리 (열림, 진행중, 해결됨, 닫힘)
- 우선순위 설정 (낮음, 보통, 높음, 긴급)

### 2.2 SR 이력 조회

- 상태별 필터링
- 우선순위별 필터링
- 생성일시 기준 정렬
- 상세 정보 조회

### 2.3 Git 기반 유사 SR 검색

- 키워드 기반 커밋 검색
- 유사한 SR 처리 내역 찾기
- 커밋 메시지, 작성자, 변경 파일 정보 제공

### 2.4 DB 변경 분석

- SQL 쿼리 분석
- 테이블 생성/삭제 감지
- 컬럼 추가/삭제/수정 감지
- 변경 사항 상세 정보 제공

---

## 3. 시스템 구성

### 3.1 데이터베이스 테이블

- `sr_requests`: SR 요청 정보 저장
- `sr_history`: SR 처리 이력 저장
- `confluence_cache`: Confluence 페이지 캐시
- `git_commits`: Git 커밋 정보 저장
- `db_changes`: DB 변경 이력 저장

### 3.2 MCP 서버

**파일**: `mcp-voc-server.py`

**도구 목록**:
- `register_sr`: SR 등록
- `search_sr_history`: SR 이력 조회
- `search_similar_sr`: 유사 SR 검색
- `analyze_db_changes`: DB 변경 분석
- `get_confluence_page`: Confluence 페이지 가져오기

### 3.3 프론트엔드 컴포넌트

**위치**: `src/components/voc/VocManagement.vue`

**기능**:
- SR 입력 폼
- SR 이력 조회 화면
- 유사 SR 검색 화면
- DB 변경 분석 화면

---

## 4. 사용 방법

### 4.1 VOC 관리 화면 접근

1. 메인 화면 상단의 **"🌿 VOC 자동 대응"** 버튼 클릭
2. VOC 관리 모달이 열립니다

### 4.2 SR 등록

#### Confluence URL을 통한 등록

1. **SR 입력** 탭 선택
2. Confluence URL 입력 (선택사항)
   - 예: `https://confluence.example.com/pages/viewpage.action?pageId=123456`
3. SR 제목 입력 (필수)
4. 요구사항 설명 입력
5. 우선순위, 카테고리, 태그 설정
6. **SR 등록** 버튼 클릭

#### 수동 등록

1. Confluence URL 없이 제목과 설명만 입력하여 등록 가능

### 4.3 SR 이력 조회

1. **SR 이력 조회** 탭 선택
2. 상태/우선순위 필터 선택
3. **검색** 버튼 클릭
4. 등록된 SR 목록 확인

### 4.4 유사 SR 검색

1. **유사 SR 검색** 탭 선택
2. 검색 키워드 입력 (쉼표로 구분)
   - 예: `에러, 로그인, 데이터베이스`
3. 최대 결과 수 설정
4. **검색** 버튼 클릭
5. Git 커밋 결과 확인

### 4.5 DB 변경 분석

1. **DB 변경 분석** 탭 선택
2. 분석할 SQL 쿼리 입력
   - 예: `ALTER TABLE users ADD COLUMN phone TEXT;`
3. **분석** 버튼 클릭
4. 변경 사항 분석 결과 확인

---

## 5. API 엔드포인트

### 5.1 SR 등록

```http
POST /api/voc/sr
Content-Type: application/json

{
  "title": "SR 제목",
  "description": "요구사항 설명",
  "confluence_url": "https://confluence.example.com/...",
  "priority": "medium",
  "category": "기능개선",
  "tags": ["태그1", "태그2"]
}
```

### 5.2 SR 목록 조회

```http
GET /api/voc/sr?status=open&priority=high&limit=50
```

### 5.3 SR 상세 조회

```http
GET /api/voc/sr/:id
```

### 5.4 Git 유사 SR 검색

```http
GET /api/voc/git/search?keywords=에러,로그인&limit=10
```

### 5.5 DB 변경 분석

```http
POST /api/voc/db/analyze
Content-Type: application/json

{
  "sql_query": "ALTER TABLE users ADD COLUMN phone TEXT;"
}
```

---

## 6. 환경 설정

### 6.1 Confluence 설정

환경 변수 설정:

```bash
CONFLUENCE_URL=https://your-confluence-instance.atlassian.net
CONFLUENCE_USERNAME=your-username
CONFLUENCE_API_TOKEN=your-api-token
```

**API 토큰 생성 방법**:
1. Confluence 계정 설정 → 보안 → API 토큰
2. 토큰 생성 및 복사
3. 환경 변수에 설정

### 6.2 Git 저장소 설정

환경 변수 설정:

```bash
GIT_REPOSITORY_PATH=C:/path/to/your/repository
```

또는 기본값으로 현재 워크스페이스 사용

### 6.3 MCP 서버 설정

`cursor-mcp-config.json`에 VOC 서버 추가:

```json
{
  "mcpServers": {
    "voc-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-voc-server.py"],
      "cwd": "C:/test/test02",
      "description": "VOC 자동 대응 MCP 서버",
      "tools": [
        "register_sr",
        "search_sr_history",
        "search_similar_sr",
        "analyze_db_changes",
        "get_confluence_page"
      ]
    }
  }
}
```

### 6.4 의존성 설치

```bash
# Python 패키지
pip install mcp requests gitpython

# Node.js 패키지 (이미 설치되어 있음)
npm install
```

---

## 7. 샘플 데이터

### 7.1 샘플 데이터 생성

```bash
node create-sample-voc-data.js
```

### 7.2 생성되는 샘플 데이터

#### Confluence VOC (3개)

1. **사용자 로그인 기능 개선 요청**
   - 우선순위: 높음
   - 상태: 열림
   - 카테고리: 기능개선

2. **데이터베이스 성능 최적화 요청**
   - 우선순위: 긴급
   - 상태: 진행중
   - 카테고리: 성능개선

3. **에러 로그 모니터링 시스템 구축**
   - 우선순위: 보통
   - 상태: 열림
   - 카테고리: 시스템구축

#### 데이터 변경 VOC (3개)

1. **users 테이블에 phone 컬럼 추가**
   - 변경 타입: 컬럼 추가
   - 테이블: users
   - 컬럼: phone

2. **orders 테이블 생성 및 관련 스키마 변경**
   - 변경 타입: 테이블 생성
   - 테이블: orders

3. **products 테이블의 price 컬럼 타입 변경**
   - 변경 타입: 컬럼 수정
   - 테이블: products
   - 컬럼: price

---

## 8. 문제 해결

### 8.1 Confluence 연결 실패

- Confluence URL이 올바른지 확인
- API 토큰이 유효한지 확인
- 네트워크 연결 확인

### 8.2 Git 저장소 접근 실패

- Git 저장소 경로가 올바른지 확인
- GitPython이 설치되어 있는지 확인
- 저장소 권한 확인

### 8.3 데이터베이스 오류

- 데이터베이스 파일이 존재하는지 확인
- 테이블이 생성되었는지 확인
- 데이터베이스 권한 확인

---

## 9. 참고 자료

- [MCP 서버 완전 가이드](./MCP_서버_완전_가이드.md)
- [에러 로그 분석 MCP 서버 가이드](./에러_로그_분석_MCP_서버_가이드.md)
- [SQL 쿼리 분석 MCP 서버 가이드](./SQL_쿼리_분석_MCP_서버_가이드.md)

---

**작성자**: AI Assistant  
**최종 수정일**: 2025년 11월 22일


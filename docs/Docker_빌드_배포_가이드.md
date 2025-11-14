# 🐳 Docker 빌드 및 배포 완전 가이드

**작성일**: 2025년 1월  
**목적**: Docker를 사용한 프로젝트 빌드 및 배포 방법

---

## 📋 목차

1. [Docker란?](#docker란)
2. [사전 준비](#사전-준비)
3. [프로젝트 구조](#프로젝트-구조)
4. [빌드 방법](#빌드-방법)
5. [배포 방법](#배포-방법)
6. [개발 환경 사용](#개발-환경-사용)
7. [문제 해결](#문제-해결)

---

## 🐳 Docker란?

**Docker는 컨테이너 기반 가상화 기술**입니다.

### 간단한 비유

```
일반적인 상황:
- 각 개발자의 컴퓨터 환경이 다름
- "내 컴퓨터에서는 되는데..." 문제 발생
- 배포 환경 설정이 복잡함

Docker를 사용하면:
- 모든 환경이 동일한 컨테이너에서 실행
- "어디서든 똑같이 작동" 보장
- 배포가 간단해짐
```

**Docker의 장점:**
- ✅ 환경 일관성 보장
- ✅ 쉬운 배포
- ✅ 확장성
- ✅ 격리된 실행 환경

---

## 📦 사전 준비

### 1. Docker 설치

#### Windows
1. **Docker Desktop 다운로드**
   - https://www.docker.com/products/docker-desktop
   - Windows용 설치 파일 다운로드

2. **설치 및 실행**
   - 설치 파일 실행
   - 설치 완료 후 Docker Desktop 실행
   - 시스템 트레이에서 Docker 아이콘 확인

3. **설치 확인**
   ```bash
   docker --version
   docker-compose --version
   ```

#### Linux / macOS
```bash
# Linux (Ubuntu/Debian)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# macOS
brew install --cask docker
```

### 2. 환경 변수 설정

`.env` 파일 생성 (프로젝트 루트):
```env
# API Keys (필수)
NEWS_API_KEY=your_news_api_key_here
LASTFM_API_KEY=your_lastfm_api_key_here

# JWT 설정
JWT_SECRET=your_secret_key_here
JWT_EXPIRES_IN=7d

# 서버 포트
API_SERVER_PORT=3001

# Node Environment
NODE_ENV=production

# Frontend API Base URL (Docker 내부 네트워크)
VITE_API_BASE_URL=http://backend:3001
```

> **참고**: `.env.docker` 파일을 참고하여 `.env` 파일을 생성할 수 있습니다.

---

## 🏗️ 프로젝트 구조

### Docker 파일 구조

```
test02/
├── Dockerfile.frontend          # 프론트엔드 프로덕션 빌드
├── Dockerfile.frontend.dev      # 프론트엔드 개발 빌드
├── Dockerfile.backend           # 백엔드 프로덕션 빌드
├── Dockerfile.backend.dev       # 백엔드 개발 빌드
├── Dockerfile.python           # Python 서버 빌드
├── docker-compose.yml          # 프로덕션 환경 설정
├── docker-compose.dev.yml      # 개발 환경 설정
├── .dockerignore              # Docker 빌드 제외 파일
└── docker/
    └── nginx.conf             # Nginx 설정 파일
```

### 서비스 구성

1. **Frontend** (포트 5173)
   - Vue.js 프론트엔드
   - Nginx로 서빙

2. **Backend** (포트 3001)
   - Node.js API 서버
   - RESTful API 제공

3. **Python MCP** (내부 통신)
   - Python MCP 통합 서버
   - Cursor AI와 통신

4. **Python HTTP** (포트 3002)
   - 화면 검증 HTTP 서버
   - Playwright 사용

---

## 🔨 빌드 방법

### 방법 1: 스크립트 사용 (권장)

#### Windows
```bash
# 프로덕션 빌드
scripts\docker-build.bat

# 빌드 테스트 (캐시 없이)
scripts\docker-build-test.bat

# 개발 환경 빌드
scripts\docker-build.bat dev
```

#### Linux / macOS
```bash
# 실행 권한 부여
chmod +x scripts/docker-build.sh scripts/docker-build-test.sh

# 프로덕션 빌드
./scripts/docker-build.sh

# 빌드 테스트 (캐시 없이)
./scripts/docker-build-test.sh

# 개발 환경 빌드
./scripts/docker-build.sh dev
```

### 방법 2: 직접 명령어 사용

#### 프로덕션 빌드
```bash
# 일반 빌드
docker-compose build

# 캐시 없이 빌드 (완전 재빌드)
docker-compose build --no-cache

# 특정 서비스만 빌드
docker-compose build frontend
docker-compose build backend
```

#### 개발 환경 빌드
```bash
docker-compose -f docker-compose.dev.yml build
```

### 빌드 최적화

#### 멀티 스테이지 빌드
- 프론트엔드는 멀티 스테이지 빌드 사용
- 최종 이미지 크기 최소화

#### 빌드 캐시 활용
```bash
# 캐시 사용 (빠른 빌드)
docker-compose build

# 캐시 없이 빌드 (완전 재빌드)
docker-compose build --no-cache
```

### 개별 서비스 빌드

```bash
# 프론트엔드만 빌드
docker build -f Dockerfile.frontend -t test02-frontend .

# 백엔드만 빌드
docker build -f Dockerfile.backend -t test02-backend .

# Python 서버만 빌드
docker build -f Dockerfile.python -t test02-python .
```

---

## 🚀 배포 방법

### 방법 1: 스크립트 사용 (권장)

#### Windows
```bash
scripts\docker-deploy.bat
```

#### Linux / macOS
```bash
chmod +x scripts/docker-deploy.sh
./scripts/docker-deploy.sh
```

### 방법 2: 직접 명령어 사용

#### 프로덕션 배포
```bash
# 빌드 및 시작
docker-compose up -d --build

# 또는 단계별
docker-compose build
docker-compose up -d
```

#### 개발 환경 배포
```bash
docker-compose -f docker-compose.dev.yml up -d --build
```

### 배포 후 확인

```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f frontend
docker-compose logs -f backend
```

---

## 💻 개발 환경 사용

### 개발 모드 실행

개발 모드는 **핫 리로드**와 **디버깅**을 지원합니다.

```bash
# 개발 환경 시작
docker-compose -f docker-compose.dev.yml up

# 백그라운드 실행
docker-compose -f docker-compose.dev.yml up -d
```

### 개발 모드 특징

- ✅ 코드 변경 시 자동 재시작
- ✅ 소스 코드 볼륨 마운트
- ✅ 개발 도구 포함
- ✅ 상세한 로그 출력

---

## 🛠️ 유용한 명령어

### 컨테이너 관리

```bash
# 모든 서비스 시작
docker-compose up -d

# 모든 서비스 중지
docker-compose down

# 서비스 재시작
docker-compose restart

# 특정 서비스만 재시작
docker-compose restart backend
```

### 로그 확인

```bash
# 모든 로그 확인
docker-compose logs -f

# 특정 서비스 로그만 확인
docker-compose logs -f frontend
docker-compose logs -f backend

# 최근 100줄만 확인
docker-compose logs --tail=100
```

### 컨테이너 접속

```bash
# 백엔드 컨테이너 접속
docker-compose exec backend sh

# 프론트엔드 컨테이너 접속
docker-compose exec frontend sh

# Python 서버 컨테이너 접속
docker-compose exec python-mcp bash
```

### 이미지 관리

```bash
# 이미지 목록 확인
docker images

# 사용하지 않는 이미지 삭제
docker image prune

# 모든 이미지 삭제 (주의!)
docker rmi $(docker images -q)
```

### 볼륨 관리

```bash
# 볼륨 목록 확인
docker volume ls

# 볼륨 삭제
docker volume rm test02_data
```

---

## 🔍 문제 해결

### 포트 충돌

**문제**: 포트가 이미 사용 중입니다.

**해결 방법**:
```bash
# 포트를 사용하는 프로세스 확인
netstat -ano | findstr :3001  # Windows
lsof -i :3001                 # Linux/macOS

# docker-compose.yml에서 포트 변경
ports:
  - "3002:3001"  # 외부:내부
```

### 빌드 실패

**문제**: Docker 빌드가 실패합니다.

**해결 방법**:
1. **Dockerfile 확인**
   ```bash
   # Dockerfile 문법 확인
   docker build -f Dockerfile.backend --no-cache .
   ```

2. **캐시 없이 빌드**
   ```bash
   docker-compose build --no-cache
   ```

3. **로그 확인**
   ```bash
   docker-compose build 2>&1 | tee build.log
   ```

### 컨테이너가 시작되지 않음

**문제**: 컨테이너가 계속 재시작됩니다.

**해결 방법**:
1. **로그 확인**
   ```bash
   docker-compose logs backend
   ```

2. **환경 변수 확인**
   ```bash
   docker-compose config
   ```

3. **의존성 확인**
   ```bash
   docker-compose up --no-deps backend
   ```

### 데이터베이스 문제

**문제**: 데이터베이스가 초기화되지 않습니다.

**해결 방법**:
1. **볼륨 확인**
   ```bash
   docker-compose down -v  # 볼륨 삭제
   docker-compose up -d    # 재시작
   ```

2. **데이터 디렉토리 권한 확인**
   ```bash
   chmod -R 777 data/  # Linux/macOS
   ```

### 네트워크 문제

**문제**: 서비스 간 통신이 안 됩니다.

**해결 방법**:
1. **네트워크 확인**
   ```bash
   docker network ls
   docker network inspect test02_test02-network
   ```

2. **서비스 이름으로 접근**
   ```javascript
   // api-server.js에서
   const API_URL = 'http://backend:3001'  // localhost 대신 서비스 이름 사용
   ```

---

## 📊 프로덕션 배포 체크리스트

### 배포 전 확인

- [ ] `.env` 파일 설정 완료
- [ ] API 키 설정 확인
- [ ] 데이터베이스 백업
- [ ] 포트 충돌 확인
- [ ] Docker 이미지 빌드 성공
- [ ] 모든 서비스 정상 작동 확인

### 배포 후 확인

- [ ] 프론트엔드 접속 확인 (http://localhost:5173)
- [ ] 백엔드 API 확인 (http://localhost:3001/api-docs)
- [ ] 데이터베이스 연결 확인
- [ ] 로그 에러 확인
- [ ] 성능 모니터링

---

## 🔐 보안 고려사항

### 프로덕션 환경

1. **환경 변수 보호**
   - `.env` 파일을 Git에 커밋하지 않음
   - Docker Secrets 사용 고려

2. **네트워크 보안**
   - 필요한 포트만 노출
   - 방화벽 설정

3. **이미지 보안**
   - 최신 베이스 이미지 사용
   - 정기적인 보안 업데이트

---

## 📚 관련 문서

- [`README.md`](../README.md) - 프로젝트 개요
- [`가이드.md`](../가이드.md) - 프로젝트 완전 가이드
- [Docker 공식 문서](https://docs.docker.com/)
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)

---

## 🎯 빠른 시작 요약

```bash
# 1. Docker 설치 확인
docker --version

# 2. 환경 변수 설정
cp .env.example .env
# .env 파일 편집

# 3. 빌드 및 배포
scripts/docker-build.bat        # Windows
./scripts/docker-build.sh       # Linux/macOS

scripts/docker-deploy.bat       # Windows
./scripts/docker-deploy.sh      # Linux/macOS

# 4. 확인
docker-compose ps
# 브라우저에서 http://localhost:5173 접속
```

---

**마지막 업데이트**: 2025년 1월


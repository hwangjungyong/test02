# 🚀 Docker 빌드 최적화 가이드

**작성일**: 2025년 1월  
**목적**: Docker 빌드 성능 및 이미지 크기 최적화

---

## 📋 목차

1. [빌드 최적화 전략](#빌드-최적화-전략)
2. [멀티 스테이지 빌드](#멀티-스테이지-빌드)
3. [캐시 활용](#캐시-활용)
4. [이미지 크기 최적화](#이미지-크기-최적화)
5. [빌드 시간 단축](#빌드-시간-단축)

---

## 🎯 빌드 최적화 전략

### 현재 구조

```
프론트엔드: 멀티 스테이지 빌드 ✅
백엔드: 단일 스테이지 빌드
Python: 단일 스테이지 빌드
```

### 최적화 포인트

1. **레이어 캐싱**: 자주 변경되지 않는 파일 먼저 복사
2. **멀티 스테이지**: 빌드 도구 제거로 이미지 크기 감소
3. **.dockerignore**: 불필요한 파일 제외
4. **의존성 캐싱**: package.json 먼저 복사

---

## 🏗️ 멀티 스테이지 빌드

### 프론트엔드 (현재 구현)

```dockerfile
# 빌드 스테이지
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# 프로덕션 스테이지
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
```

**장점:**
- ✅ 빌드 도구가 최종 이미지에 포함되지 않음
- ✅ 이미지 크기 대폭 감소 (약 70% 감소)
- ✅ 보안 향상 (불필요한 도구 제거)

---

## 💾 캐시 활용

### 최적화된 Dockerfile 구조

```dockerfile
# 1. 베이스 이미지 (가장 자주 변경되지 않음)
FROM node:20-alpine

# 2. 의존성 파일 먼저 복사 (자주 변경되지 않음)
COPY package*.json ./

# 3. 의존성 설치 (캐시 활용)
RUN npm ci

# 4. 소스 코드 복사 (자주 변경됨)
COPY . .

# 5. 빌드 실행
RUN npm run build
```

**캐시 전략:**
- `package.json`이 변경되지 않으면 의존성 설치 단계 캐시 사용
- 소스 코드만 변경되면 빌드만 재실행

---

## 📦 이미지 크기 최적화

### 현재 이미지 크기 (예상)

```
frontend: ~50MB (nginx:alpine + 빌드 결과물)
backend: ~150MB (node:20-alpine + 의존성)
python: ~800MB (python:3.11-slim + playwright)
```

### 최적화 방법

#### 1. Alpine 이미지 사용 ✅
- 이미 적용됨 (node:20-alpine, nginx:alpine)

#### 2. 불필요한 파일 제거
```dockerfile
# .dockerignore에 추가
node_modules
*.log
.git
```

#### 3. 멀티 스테이지 빌드 ✅
- 프론트엔드에 적용됨

#### 4. 프로덕션 의존성만 설치
```dockerfile
RUN npm ci --only=production
```

---

## ⚡ 빌드 시간 단축

### 현재 빌드 시간 (예상)

```
프론트엔드: 2-3분
백엔드: 1-2분
Python: 5-10분 (Playwright 설치 포함)
```

### 최적화 방법

#### 1. 병렬 빌드
```bash
# 모든 서비스를 동시에 빌드
docker-compose build --parallel
```

#### 2. 캐시 활용
```bash
# 캐시 사용 (빠름)
docker-compose build

# 캐시 없이 빌드 (느림, 완전 재빌드)
docker-compose build --no-cache
```

#### 3. BuildKit 사용
```bash
# BuildKit 활성화
export DOCKER_BUILDKIT=1
docker-compose build
```

---

## 🔍 빌드 검증

### 빌드 테스트 스크립트

```bash
# Windows
scripts\docker-build-test.bat

# Linux/macOS
./scripts/docker-build-test.sh
```

**검증 항목:**
1. 이미지 빌드 성공
2. 이미지 크기 확인
3. docker-compose 설정 검증
4. 헬스체크 설정 확인

---

## 📊 빌드 성능 비교

### 최적화 전 vs 후

| 항목 | 최적화 전 | 최적화 후 | 개선율 |
|------|----------|----------|--------|
| 프론트엔드 이미지 | ~200MB | ~50MB | 75% ↓ |
| 빌드 시간 (캐시) | 5분 | 2분 | 60% ↓ |
| 빌드 시간 (무캐시) | 10분 | 5분 | 50% ↓ |

---

## 🛠️ 고급 최적화

### 1. BuildKit 캐시 마운트

```dockerfile
RUN --mount=type=cache,target=/root/.npm \
    npm ci
```

### 2. 병렬 빌드

```bash
docker-compose build --parallel
```

### 3. 이미지 태그 관리

```bash
# 버전 태그 지정
docker-compose build --tag test02:latest
docker-compose build --tag test02:v1.0.0
```

---

## 📝 빌드 체크리스트

### 빌드 전 확인

- [ ] `.env` 파일 설정 완료
- [ ] `.dockerignore` 확인
- [ ] Dockerfile 문법 확인
- [ ] docker-compose.yml 검증

### 빌드 후 확인

- [ ] 모든 이미지 빌드 성공
- [ ] 이미지 크기 확인
- [ ] 컨테이너 시작 테스트
- [ ] 헬스체크 통과 확인

---

## 🎯 빠른 참조

### 빌드 명령어

```bash
# 일반 빌드
docker-compose build

# 캐시 없이 빌드
docker-compose build --no-cache

# 특정 서비스만 빌드
docker-compose build frontend

# 병렬 빌드
docker-compose build --parallel

# 빌드 테스트
scripts/docker-build-test.bat  # Windows
./scripts/docker-build-test.sh # Linux/macOS
```

### 이미지 관리

```bash
# 이미지 목록
docker images test02*

# 이미지 크기 확인
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"

# 사용하지 않는 이미지 삭제
docker image prune

# 모든 이미지 삭제 (주의!)
docker rmi $(docker images -q)
```

---

**마지막 업데이트**: 2025년 1월


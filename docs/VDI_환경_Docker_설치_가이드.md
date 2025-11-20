# 🐳 VDI 환경에서 Docker 사용 가이드

**작성일**: 2025년 1월  
**목적**: VDI 환경에서 Docker Desktop 대신 Docker Engine을 사용하는 방법 안내

---

## 📋 목차

1. [VDI 환경이란?](#vdi-환경이란)
2. [왜 Docker Desktop을 사용할 수 없나요?](#왜-docker-desktop을-사용할-수-없나요)
3. [해결 방법: WSL 2 내 Docker Engine 설치](#해결-방법-wsl-2-내-docker-engine-설치)
4. [설치 후 확인](#설치-후-확인)
5. [사용 방법](#사용-방법)
6. [문제 해결](#문제-해결)

---

## 🖥️ VDI 환경이란?

**VDI (Virtual Desktop Infrastructure)**는 가상 데스크톱 인프라를 의미합니다.

**비유로 설명하면:**
- 일반 컴퓨터 = 내 집에서 직접 사용하는 컴퓨터
- VDI 환경 = 회사나 학교에서 제공하는 가상 컴퓨터
- 여러 사람이 같은 서버를 공유해서 사용하는 환경

**VDI 환경의 특징:**
- 가상화 환경에서 실행됨
- Docker Desktop 라이센스 제약이 있음
- 하지만 Docker Engine은 사용 가능!

---

## ❌ 왜 Docker Desktop을 사용할 수 없나요?

**Docker Desktop의 라이센스 제약:**
- Docker Desktop은 상업적 사용 시 유료 라이센스가 필요합니다
- VDI 환경은 상업적 환경으로 간주될 수 있습니다
- 따라서 Docker Desktop 사용이 제한될 수 있습니다

**하지만 좋은 소식:**
- ✅ **Docker Engine은 무료입니다!**
- ✅ WSL 2 내에서 Docker Engine을 직접 설치할 수 있습니다
- ✅ Docker Desktop 없이도 모든 기능을 사용할 수 있습니다!

**비유로 설명하면:**
- Docker Desktop = 유료 프랜차이즈 가게
- Docker Engine = 무료로 사용할 수 있는 기본 가게
- 둘 다 같은 기능을 제공하지만, Docker Engine은 무료예요!

---

## ✅ 해결 방법: WSL 2 내 Docker Engine 설치

### 전제 조건

1. **WSL 2가 설치되어 있어야 합니다**
   ```powershell
   wsl --status
   ```
   - "기본 버전: 2"라고 나오면 성공! ✅

2. **WSL 2가 없다면 설치하세요:**
   ```powershell
   wsl --install
   ```

### 단계별 설치 가이드

#### 1단계: WSL 2에 Ubuntu 배포판 설치 (없는 경우)

```powershell
# PowerShell에서 실행
wsl --install -d Ubuntu
```

**설치 후:**
- Ubuntu가 자동으로 실행됩니다
- 사용자 이름과 비밀번호를 설정하세요

#### 2단계: WSL 2 내에서 Docker 설치

**Ubuntu 터미널에서 실행:**

```bash
# 1. 시스템 업데이트
sudo apt update
sudo apt upgrade -y

# 2. Docker 설치 스크립트 다운로드 및 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 3. 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# 4. Docker 서비스 시작
sudo service docker start

# 5. Docker가 정상 작동하는지 확인
docker --version
docker ps
```

**설정 완료!** ✅

#### 3단계: Docker Compose 설치 (필요한 경우)

```bash
# Docker Compose 설치
sudo apt install docker-compose-plugin -y

# 또는 별도 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 확인
docker compose version
```

---

## 🔍 설치 후 확인

### WSL 2 내에서 확인

```bash
# WSL 2 진입
wsl

# Docker 버전 확인
docker --version

# Docker 서비스 상태 확인
sudo service docker status

# Docker가 정상 작동하는지 확인
docker ps
```

### Windows에서 확인

```powershell
# PowerShell에서 실행
wsl docker --version
wsl docker ps
```

**결과:**
- Docker 버전이 표시되면 성공! ✅
- `docker ps`가 오류 없이 실행되면 성공! ✅

---

## 🎮 사용 방법

### 방법 1: WSL 2 내에서 직접 실행 (권장)

```bash
# 1. WSL 2 진입
wsl

# 2. 프로젝트 디렉토리로 이동
cd /mnt/c/test/test02

# 3. Docker Compose 실행
docker-compose up -d

# 4. 컨테이너 상태 확인
docker ps
```

### 방법 2: Windows에서 WSL 명령어 사용

```powershell
# PowerShell에서 실행
# 프로젝트 디렉토리로 이동
cd C:\test\test02

# WSL을 통해 Docker Compose 실행
wsl docker-compose up -d

# 상태 확인
wsl docker ps
```

### 방법 3: 환경 변수 설정 (선택사항)

**Windows에서 WSL의 Docker를 기본으로 사용하려면:**

```powershell
# PowerShell 프로필에 추가 (한 번만 실행)
notepad $PROFILE

# 다음 내용 추가:
$env:DOCKER_HOST="npipe:////./pipe/docker_engine"

# 또는 임시로 설정:
$env:DOCKER_HOST="npipe:////./pipe/docker_engine"
docker ps
```

---

## 🛠️ 문제 해결

### 문제 1: "Cannot connect to the Docker daemon"

**원인:** Docker 서비스가 실행되지 않았습니다.

**해결 방법:**

```bash
# WSL 2 내에서 실행
sudo service docker start

# 자동 시작 설정 (선택사항)
sudo systemctl enable docker
```

### 문제 2: "Permission denied"

**원인:** 사용자가 docker 그룹에 속해있지 않습니다.

**해결 방법:**

```bash
# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER

# WSL 2 재시작 (Windows에서)
wsl --shutdown
wsl
```

### 문제 3: "docker-compose: command not found"

**원인:** Docker Compose가 설치되지 않았습니다.

**해결 방법:**

```bash
# Docker Compose 플러그인 설치
sudo apt install docker-compose-plugin -y

# 또는 별도 설치
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### 문제 4: Windows에서 `docker` 명령어가 작동하지 않음

**원인:** Windows에서 직접 Docker를 사용하려고 합니다.

**해결 방법:**

```powershell
# WSL 접두사를 붙여서 실행
wsl docker ps

# 또는 WSL 내에서 실행
wsl
docker ps
```

---

## 📝 자주 묻는 질문 (FAQ)

### Q1: Docker Desktop과 Docker Engine의 차이는 뭔가요?

**답변:**
- **Docker Desktop**: GUI가 있는 통합 도구 (유료 라이센스 필요)
- **Docker Engine**: 명령어로 사용하는 기본 도구 (무료)

**기능 차이:**
- 둘 다 같은 Docker 기능을 제공합니다
- Docker Desktop은 GUI가 있어서 편리하지만, Docker Engine도 모든 기능을 사용할 수 있어요!

### Q2: WSL 2 내 Docker가 Windows 파일에 접근할 수 있나요?

**답변: 네! 가능합니다!**

```bash
# Windows 파일 시스템은 /mnt/c/ 경로로 접근 가능
cd /mnt/c/test/test02
docker-compose up -d
```

### Q3: Docker Desktop을 제거해도 되나요?

**답변:**
- VDI 환경에서는 Docker Desktop을 사용하지 않으므로 제거해도 됩니다
- 하지만 WSL 2 내 Docker Engine이 정상 작동하는지 먼저 확인하세요!

### Q4: 성능 차이가 있나요?

**답변:**
- Docker Engine도 Docker Desktop과 거의 동일한 성능을 제공합니다
- WSL 2를 통해 실행되므로 약간의 오버헤드가 있을 수 있지만, 실사용에서는 차이가 거의 없어요!

---

## 🎯 요약

**VDI 환경에서 Docker 사용하기:**

1. ✅ WSL 2 설치 확인
2. ✅ WSL 2 내에서 Docker Engine 설치
3. ✅ Docker 서비스 시작
4. ✅ `wsl docker-compose up -d` 명령어로 컨테이너 실행

**비유로 정리:**
- Docker Desktop = 유료 프랜차이즈 가게 (VDI에서 사용 불가)
- Docker Engine = 무료 기본 가게 (VDI에서 사용 가능)
- WSL 2 = 가게를 운영할 수 있는 공간
- 같은 기능을 제공하지만, Docker Engine은 무료예요!

---

**마지막 업데이트**: 2025년 1월


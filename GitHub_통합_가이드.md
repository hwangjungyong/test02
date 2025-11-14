# 🔗 GitHub 완전 가이드

**작성일**: 2025년 1월  
**버전**: 2.0.0 (통합 버전)

> GitHub 연동부터 토큰 관리, 문제 해결까지 모든 내용을 한 곳에 모았습니다.

---

## 📋 목차

1. [GitHub 연동하기](#1-github-연동하기)
2. [파일 업로드 및 관리](#2-파일-업로드-및-관리)
3. [Personal Access Token 관리](#3-personal-access-token-관리)
4. [파일 링크 공유하기](#4-파일-링크-공유하기)
5. [문제 해결](#5-문제-해결)
6. [자주 사용하는 명령어](#6-자주-사용하는-명령어)

---

## 1. GitHub 연동하기

### 1단계: GitHub에서 새 저장소 생성

#### A. GitHub 웹사이트 접속
- 링크: https://github.com
- 로그인

#### B. 새 저장소 생성
1. 우측 상단 **"+"** 버튼 클릭
2. **"New repository"** 선택

#### C. 저장소 정보 입력
- **Repository name**: `test02` (또는 원하는 이름)
- **Description**: `AI 뉴스/음악/도서 추천 시스템` (선택사항)
- **Public** 또는 **Private** 선택
- ⚠️ **"Initialize this repository with a README" 체크 해제** (이미 로컬에 파일이 있으므로)
- **"Create repository"** 버튼 클릭

#### D. 저장소 URL 복사
생성된 저장소 페이지에서 URL 복사:
```
https://github.com/사용자명/test02.git
```

---

### 2단계: 로컬 Git과 GitHub 연동

#### A. 기존 원격 저장소 제거 (예시 URL이 설정된 경우)
```bash
cd C:\test\test02
git remote remove origin
```

#### B. 실제 GitHub 저장소 URL로 연결
```bash
# HTTPS 사용 (권장)
git remote add origin https://github.com/사용자명/test02.git

# 또는 SSH 사용 (SSH 키 설정된 경우)
git remote add origin git@github.com:사용자명/test02.git
```

#### C. 원격 저장소 확인
```bash
git remote -v
```

---

### 3단계: 파일 추가 및 커밋

```bash
# 모든 파일 추가
git add .

# 커밋 생성
git commit -m "Initial commit: AI 뉴스/음악/도서 추천 시스템"
```

---

### 4단계: GitHub에 업로드 (푸시)

```bash
# 브랜치 이름을 main으로 설정
git branch -M main

# GitHub에 푸시
git push -u origin main
```

**첫 푸시 시 인증 요청:**
- **사용자 이름**: GitHub 사용자명 입력
- **비밀번호**: GitHub Personal Access Token 입력 (비밀번호 아님!)

---

## 2. 파일 업로드 및 관리

### 변경사항 업로드 (가장 자주 사용)

```bash
# 변경사항 확인
git status

# 변경된 파일 추가
git add .

# 커밋 생성
git commit -m "변경 내용 설명"

# GitHub에 푸시
git push origin main
```

**커밋 메시지 예시:**
```bash
git commit -m "feat: 새로운 기능 추가"
git commit -m "fix: 버그 수정"
git commit -m "docs: 문서 업데이트"
git commit -m "refactor: 코드 리팩토링"
```

### 원격 저장소에서 최신 변경사항 가져오기

```bash
# 원격 저장소의 변경사항 가져오기
git pull origin main

# 또는 fetch + merge
git fetch origin
git merge origin/main
```

### 새 브랜치 생성 및 작업

```bash
# 새 브랜치 생성 및 전환
git checkout -b feature/새기능

# 브랜치에서 작업 후
git add .
git commit -m "feat: 새 기능 구현"
git push origin feature/새기능

# main 브랜치로 병합
git checkout main
git merge feature/새기능
git push origin main
```

---

## 3. Personal Access Token 관리

### 토큰 생성 방법

#### 1단계: GitHub 접속
**링크:** https://github.com/settings/tokens

또는:
1. GitHub 로그인
2. 우측 상단 프로필 아이콘 클릭
3. **Settings** 클릭
4. 좌측 메뉴에서 **Developer settings** 클릭
5. **Personal access tokens** → **Tokens (classic)** 클릭

#### 2단계: 새 토큰 생성
1. **"Generate new token"** 버튼 클릭
2. **"Generate new token (classic)"** 선택

#### 3단계: 토큰 설정
- **Note**: 토큰 이름 입력 (예: `test02-project`, `My PC`)
- **Expiration**: 만료일 선택
  - 30 days, 60 days, 90 days
  - Custom (사용자 지정)
  - No expiration (만료 없음) - ⚠️ 보안상 권장하지 않음

#### 4단계: 권한 선택 (Scopes)
필수 권한:
- ✅ **repo** (전체 체크)

선택 권한:
- ✅ **workflow** (GitHub Actions 사용 시)
- ✅ **write:packages** (패키지 업로드 시)

#### 5단계: 토큰 생성
1. **"Generate token"** 버튼 클릭
2. ⚠️ **토큰 복사** (한 번만 표시됨!)
3. 안전한 곳에 저장

### 토큰 사용 방법

#### 푸시 시 사용
```bash
git push origin main
```
- 사용자 이름: GitHub 사용자명
- 비밀번호: 생성한 Personal Access Token 입력

#### Windows 자격 증명 관리자에 저장
- Windows가 자동으로 저장할 수 있음
- 제어판 → 자격 증명 관리자 → Windows 자격 증명에서 확인 가능

### 토큰 관리

**토큰 목록 확인:**
- 링크: https://github.com/settings/tokens

**토큰 삭제:**
1. https://github.com/settings/tokens 접속
2. 삭제할 토큰 옆 **"Delete"** 클릭
3. 확인

**토큰 권한 수정:**
1. 토큰 목록에서 토큰 클릭
2. 권한 수정 후 저장

### 안전한 토큰 저장 방법

#### 방법 1: Windows 자격 증명 관리자 (권장)
Git이 자동으로 Windows 자격 증명 관리자에 토큰을 저장합니다.

**확인 방법:**
1. 제어판 → 자격 증명 관리자
2. Windows 자격 증명
3. `git:https://github.com` 항목 확인

#### 방법 2: .env 파일에 저장 (선택사항)
⚠️ `.env` 파일은 이미 `.gitignore`에 포함되어 있어 Git에 업로드되지 않습니다.

```bash
# .env 파일에 추가
GITHUB_TOKEN=your_github_token_here
```

---

## 4. 파일 링크 공유하기

### GitHub 파일 링크 형식

```
https://github.com/[사용자명]/[저장소명]/blob/[브랜치명]/[파일경로]
```

### 기본 링크 (권장)

**파일 보기:**
```
https://github.com/hwangjungyong/test02/blob/main/README.md
```

**Raw 파일 (텍스트만):**
```
https://github.com/hwangjungyong/test02/raw/main/README.md
```

**특정 커밋 버전:**
```
https://github.com/hwangjungyong/test02/blob/커밋해시/파일명.md
```

### 동료에게 공유하는 방법

#### 방법 1: 직접 링크 복사
1. GitHub 저장소 접속
2. 파일 클릭
3. 브라우저 주소창에서 URL 복사
4. 이메일/메신저에 링크 붙여넣기

#### 방법 2: Markdown 형식으로 공유
```markdown
코드 리뷰 리포트를 확인해주세요:

[코드 리뷰 리포트 보기](https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md)
```

### 주요 파일 링크 모음

**메인 가이드:**
```
https://github.com/hwangjungyong/test02/blob/main/가이드.md
```

**README:**
```
https://github.com/hwangjungyong/test02/blob/main/README.md
```

**코드 리뷰 리포트:**
```
https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md
```

---

## 5. 문제 해결

### 문제 1: "remote origin already exists"

```bash
# 해결: 기존 원격 저장소 제거 후 재추가
git remote remove origin
git remote add origin https://github.com/사용자명/test02.git
```

### 문제 2: "Authentication failed"

**해결:**
1. Personal Access Token 생성 확인
2. 비밀번호 대신 토큰 사용
3. Windows 자격 증명 관리자 확인:
   - 제어판 → 자격 증명 관리자 → Windows 자격 증명
   - `git:https://github.com` 항목 삭제 후 재시도

### 문제 3: "error: failed to push some refs"

```bash
# 해결: 원격 저장소의 변경사항 먼저 가져오기
git pull origin main --rebase
git push origin main
```

### 문제 4: 네트워크 연결 실패

**오류 메시지:**
```
fatal: unable to access 'https://github.com/...': 
Failed to connect to github.com port 443
```

**해결 방법:**

#### 방법 1: 네트워크 연결 확인
```bash
ping github.com
```

#### 방법 2: 프록시 설정 (회사/학교 네트워크인 경우)
```bash
# 프록시 설정
git config --global http.proxy http://프록시주소:포트
git config --global https.proxy http://프록시주소:포트

# 프록시 제거
git config --global --unset http.proxy
git config --global --unset https.proxy
```

#### 방법 3: SSH 사용 (프록시 문제 우회)
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your.email@example.com"

# 공개 키 복사 (Windows)
type C:\Users\사용자명\.ssh\id_ed25519.pub | clip

# GitHub에 추가: https://github.com/settings/keys

# 원격 저장소를 SSH로 변경
git remote remove origin
git remote add origin git@github.com:사용자명/test02.git
git push -u origin main
```

### 문제 5: "Permission denied"

**해결:**
- SSH 키 설정 확인: https://github.com/settings/keys
- 또는 HTTPS + Personal Access Token 사용

---

## 6. 자주 사용하는 명령어

### 기본 작업
```bash
# 상태 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "메시지"

# 푸시
git push origin main

# 풀
git pull origin main
```

### 브랜치 작업
```bash
# 브랜치 목록
git branch

# 새 브랜치 생성
git checkout -b 브랜치명

# 브랜치 전환
git checkout 브랜치명

# 브랜치 병합
git merge 브랜치명
```

### 히스토리 확인
```bash
# 간단한 히스토리
git log --oneline

# 그래프
git log --oneline --graph --all

# 특정 파일 히스토리
git log -- 파일명
```

---

## 🔐 보안 주의사항

### 1. 토큰 보안
- ✅ 토큰을 코드에 직접 작성하지 마세요
- ✅ `.env` 파일이나 환경 변수로 관리하세요
- ✅ `.gitignore`에 `.env` 파일 추가되어 있는지 확인
- ✅ 토큰을 공유하지 마세요
- ✅ 정기적으로 토큰 갱신

### 2. .gitignore 확인
현재 프로젝트의 `.gitignore`에 다음이 포함되어 있습니다:
- `.env` 파일
- `data/` 폴더 (데이터베이스 파일)
- `node_modules/` 폴더

### 3. 민감한 정보 확인
업로드 전 확인:
- API 키가 코드에 하드코딩되지 않았는지
- 비밀번호가 포함되지 않았는지
- 개인 정보가 포함되지 않았는지

---

## 🔗 유용한 링크

- **GitHub 저장소**: https://github.com/hwangjungyong/test02
- **Personal Access Tokens**: https://github.com/settings/tokens
- **GitHub 설정**: https://github.com/settings/profile
- **SSH 키 설정**: https://github.com/settings/keys
- **Git 공식 문서**: https://git-scm.com/doc
- **GitHub 가이드**: https://guides.github.com

---

## ✅ 체크리스트

### 초기 설정
- [x] Git 저장소 초기화
- [x] GitHub 저장소 생성
- [x] 원격 저장소 연결
- [x] 첫 업로드 완료

### 추후 작업
- [ ] Personal Access Token 생성
- [ ] .gitignore 확인
- [ ] 민감한 정보 제외 확인
- [ ] 정기적인 백업 (푸시)

---

**다음 단계:** Git 기본 사용법은 [`Git_통합_가이드.md`](./Git_통합_가이드.md)를 참조하세요.


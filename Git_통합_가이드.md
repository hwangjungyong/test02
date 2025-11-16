# 📚 Git 완전 가이드

**작성일**: 2025년 1월  
**버전**: 2.0.0 (통합 버전)

> Git 설치부터 사용법까지 모든 내용을 한 곳에 모았습니다.

---

## 📋 목차

1. [Git 설치하기](#1-git-설치하기)
2. [Git 기본 설정](#2-git-기본-설정)
3. [Git 계정 정보 확인](#3-git-계정-정보-확인)
4. [로컬 저장소에 업로드](#4-로컬-저장소에-업로드)
5. [자주 사용하는 명령어](#5-자주-사용하는-명령어)
6. [문제 해결](#6-문제-해결)

---

## 1. Git 설치하기

### 현재 상태 확인

```bash
git --version
```

**Git이 설치되어 있지 않은 경우:**
```
'git'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

### 설치 방법

#### 방법 1: 공식 웹사이트에서 다운로드 (권장)

1. **Git 공식 웹사이트 접속**
   - URL: https://git-scm.com/download/win
   - 또는 https://git-scm.com/downloads 에서 Windows 버전 선택

2. **다운로드 및 설치**
   - 자동으로 최신 버전 다운로드 시작
   - 다운로드한 `.exe` 파일 실행
   - 설치 마법사 따라하기

3. **설치 옵션 (권장 설정)**
   - ✅ Git Bash Here
   - ✅ Git GUI Here
   - ✅ Associate .git* configuration files with the default text editor

4. **설치 확인**
   ```bash
   git --version
   # 예상 출력: git version 2.xx.x
   ```

#### 방법 2: 패키지 관리자 사용

**Chocolatey 사용:**
```bash
choco install git
```

**Winget 사용:**
```bash
winget install Git.Git
```

---

## 2. Git 기본 설정

### 사용자 정보 설정 (최초 1회)

```bash
# 사용자 이름 설정
git config --global user.name "Your Name"

# 이메일 설정
git config --global user.email "your.email@example.com"
```

**현재 프로젝트 설정:**
- 사용자 이름: `DarkPoni`
- 이메일: `darkponier@naver.com`

### 설정 확인

```bash
# 사용자 이름 확인
git config --global user.name

# 이메일 확인
git config --global user.email

# 모든 설정 확인
git config --list --global
```

----------

## 3. Git 계정 정보 확인

### 로컬 Git 계정 정보 확인

```bash
# 사용자 이름 확인
git config --global user.name

# 이메일 확인
git config --global user.email

# 모든 설정 확인
git config --list --global
```

### 인터넷상에서 Git 계정 확인

#### GitHub에서 확인

**주요 링크:**
- **프로필 페이지**: https://github.com/settings/profile
- **이메일 설정**: https://github.com/settings/emails
- **계정 설정**: https://github.com/settings/account
- **Personal Access Tokens**: https://github.com/settings/tokens
- **SSH 키 설정**: https://github.com/settings/keys

**확인 가능한 정보:**
- 프로필 이름
- 사용자 이름 (Username)
- 이메일 주소
- 등록된 이메일 목록
- SSH 키 목록
- Personal Access Token 목록

---

## 4. 로컬 저장소에 업로드

### 새 저장소 생성 (처음 업로드하는 경우)

#### 1단계: Git 저장소 초기화

```bash
cd C:\test\test02
git init
```

#### 2단계: 파일 추가

```bash
# 모든 파일 추가
git add .

# 또는 특정 파일만 추가
git add 파일명1 파일명2
```

#### 3단계: 커밋 생성

```bash
git commit -m "Initial commit: 프로젝트 초기 설정"
```

**커밋 메시지 예시:**
```bash
git commit -m "feat: AI 뉴스 검색 기능 추가"
git commit -m "fix: 로그인 오류 수정"
git commit -m "docs: README 파일 업데이트"
```

#### 4단계: 브랜치 이름 설정

```bash
# 브랜치 이름을 main으로 설정
git branch -M main
```

### 기존 저장소에 업로드

```bash
# 변경사항 확인
git status

# 변경된 파일 추가
git add .

# 커밋 생성
git commit -m "변경 내용 설명"

# 브랜치 확인
git branch
```

---

## 5. 자주 사용하는 명령어

### 기본 작업

```bash
# 상태 확인
git status

# 변경사항 추가
git add .

# 커밋
git commit -m "메시지"

# 브랜치 확인
git branch

# 커밋 히스토리 확인
git log --oneline
```

### 브랜치 작업

```bash
# 브랜치 목록
git branch

# 새 브랜치 생성 및 전환
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

# 상세한 히스토리
git log

# 그래프로 확인
git log --oneline --graph --all

# 특정 파일의 히스토리
git log -- 파일명
```

---

## 6. 문제 해결

### 문제 1: "fatal: not a git repository"

**원인:** Git 저장소가 초기화되지 않음

**해결:**
```bash
git init
```

### 문제 2: "Please tell me who you are"

**원인:** Git 사용자 정보가 설정되지 않음

**해결:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### 문제 3: 커밋 취소

```bash
# 마지막 커밋 취소 (파일은 유지)
git reset --soft HEAD~1

# 마지막 커밋 취소 (파일 변경도 취소)
git reset --hard HEAD~1
```

### 문제 4: 특정 파일만 커밋에서 제외

```bash
# 파일을 스테이징에서 제거 (커밋은 유지)
git restore --staged 파일명

# 파일 변경사항 취소
git restore 파일명
```

---

## 📚 추가 참고 자료

- **Git 공식 문서**: https://git-scm.com/doc
- **GitHub 공식 문서**: https://docs.github.com
- **Git 튜토리얼**: https://git-scm.com/docs/gittutorial

---

**다음 단계:** GitHub와 연동하려면 [`GitHub_통합_가이드.md`](./GitHub_통합_가이드.md)를 참조하세요.


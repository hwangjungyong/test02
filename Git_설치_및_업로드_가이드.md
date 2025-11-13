# 🚀 Git 설치 및 업로드 완전 가이드

## ❌ 현재 상황
```
'git'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```
→ **Git이 설치되어 있지 않습니다.**

---

## 📥 1단계: Git 설치하기

### 방법 1: 공식 웹사이트에서 다운로드 (권장)

1. **Git 공식 웹사이트 접속**
   - URL: https://git-scm.com/download/win
   - 또는 https://git-scm.com/downloads 에서 Windows 버전 선택

2. **다운로드**
   - 자동으로 최신 버전 다운로드 시작
   - 또는 "64-bit Git for Windows Setup" 클릭

3. **설치 실행**
   - 다운로드한 `.exe` 파일 실행
   - 설치 마법사 따라하기

4. **설치 옵션 (권장 설정)**
   - ✅ Git Bash Here
   - ✅ Git GUI Here
   - ✅ Associate .git* configuration files with the default text editor
   - ✅ Use Git and optional Unix tools from the Command Prompt
   - ✅ Use the OpenSSL library
   - ✅ Checkout Windows-style, commit Unix-style line endings
   - ✅ Use MinTTY (the default terminal of MSYS2)
   - ✅ Enable file system caching
   - ✅ Enable Git Credential Manager

5. **설치 완료 후 확인**
   - 명령 프롬프트(CMD) 또는 PowerShell을 **완전히 종료** 후 다시 실행
   - 다음 명령어로 확인:
   ```bash
   git --version
   ```
   - 예상 출력: `git version 2.xx.x.windows.x`

### 방법 2: Chocolatey를 사용한 설치 (고급 사용자)

```bash
choco install git
```

### 방법 3: Winget을 사용한 설치 (Windows 10/11)

```bash
winget install --id Git.Git -e --source winget
```

---

## ⚙️ 2단계: Git 사용자 정보 설정

Git 설치 후 **최초 1회만** 설정하면 됩니다:

```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

**예시:**
```bash
git config --global user.name "홍길동"
git config --global user.email "hong@example.com"
```

**설정 확인:**
```bash
git config --global user.name
git config --global user.email
```

---

## 🎯 3단계: 프로젝트를 Git에 업로드하기

### A. 로컬 Git 저장소 초기화

```bash
# 프로젝트 폴더로 이동 (이미 해당 폴더에 있다면 생략)
cd C:\test\test02

# Git 저장소 초기화
git init
```

**예상 출력:**
```
Initialized empty Git repository in C:/test/test02/.git/
```

### B. 파일 추가

```bash
# 모든 파일 추가
git add .

# 또는 특정 파일만 추가
git add 파일명1 파일명2
```

**현재 프로젝트의 .gitignore 확인:**
- `data/` 폴더 (데이터베이스 파일)는 자동으로 제외됩니다
- `.env` 파일은 자동으로 제외됩니다
- `node_modules/` 폴더는 자동으로 제외됩니다

### C. 첫 커밋 생성

```bash
git commit -m "Initial commit: AI 뉴스/음악/도서 추천 시스템"
```

**커밋 메시지 예시:**
```bash
git commit -m "Initial commit: 프로젝트 초기 설정"
git commit -m "feat: AI 뉴스 검색 기능 추가"
git commit -m "docs: README 및 가이드 문서 추가"
```

### D. GitHub에서 새 저장소 생성

1. **GitHub 웹사이트 접속**
   - https://github.com 로그인

2. **새 저장소 생성**
   - 우측 상단 "+" 버튼 → "New repository" 클릭
   - Repository name 입력 (예: `test02`)
   - Description 입력 (선택사항)
   - Public 또는 Private 선택
   - **"Initialize this repository with a README" 체크 해제** (이미 로컬에 파일이 있으므로)
   - "Create repository" 클릭

3. **저장소 URL 복사**
   - 생성된 저장소 페이지에서 URL 복사
   - 예: `https://github.com/사용자명/test02.git`

### E. 원격 저장소 연결

```bash
# 원격 저장소 추가
git remote add origin https://github.com/사용자명/저장소명.git

# 원격 저장소 확인
git remote -v
```

**예시:**
```bash
git remote add origin https://github.com/honggildong/test02.git
```

### F. 브랜치 이름 설정 및 업로드

```bash
# 브랜치 이름을 main으로 설정 (GitHub 기본값)
git branch -M main

# 원격 저장소에 푸시
git push -u origin main
```

**인증 요청 시:**
- GitHub Personal Access Token 사용 (비밀번호 대신)
- 토큰 생성 방법: GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic) → Generate new token

---

## 📝 4단계: 이후 업데이트 방법

변경사항이 있을 때마다:

```bash
# 1. 변경사항 확인
git status

# 2. 변경된 파일 추가
git add .

# 3. 커밋 생성
git commit -m "변경 내용 설명"

# 4. 원격 저장소에 푸시
git push origin main
```

---

## 🔍 현재 상태 확인 명령어

```bash
# Git 버전 확인
git --version

# 현재 상태 확인
git status

# 커밋 히스토리 확인
git log
git log --oneline

# 원격 저장소 확인
git remote -v

# 브랜치 확인
git branch
```

---

## ⚠️ 문제 해결

### 문제 1: "git: command not found" 또는 "'git'은(는) 내부 또는 외부 명령..."

**원인:** Git이 설치되지 않았거나 PATH에 추가되지 않음

**해결 방법:**
1. Git 재설치
2. 설치 시 "Use Git and optional Unix tools from the Command Prompt" 옵션 선택
3. 명령 프롬프트/PowerShell 완전히 재시작

### 문제 2: "fatal: not a git repository"

**해결:**
```bash
git init
```

### 문제 3: "Authentication failed"

**해결:**
- GitHub Personal Access Token 사용
- Windows 자격 증명 관리자에서 Git 자격 증명 확인/수정

### 문제 4: "error: failed to push some refs"

**해결:**
```bash
git pull origin main --rebase
git push origin main
```

---

## 📚 빠른 참조 명령어

### 처음부터 끝까지 (한 번에)
```bash
cd C:\test\test02
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/사용자명/저장소명.git
git branch -M main
git push -u origin main
```

### 업데이트 (한 번에)
```bash
git add .
git commit -m "변경 내용"
git push origin main
```

---

## ✅ 체크리스트

- [ ] Git 설치 완료 (`git --version` 확인)
- [ ] Git 사용자 정보 설정 (`git config`)
- [ ] 프로젝트 폴더로 이동 (`cd C:\test\test02`)
- [ ] Git 저장소 초기화 (`git init`)
- [ ] 파일 추가 (`git add .`)
- [ ] 첫 커밋 생성 (`git commit`)
- [ ] GitHub에서 저장소 생성
- [ ] 원격 저장소 연결 (`git remote add`)
- [ ] 업로드 완료 (`git push`)

---

## 🎓 추가 학습 자료

- **Git 공식 문서**: https://git-scm.com/doc
- **GitHub 가이드**: https://guides.github.com
- **Git 명령어 치트시트**: https://education.github.com/git-cheat-sheet-education.pdf
- **GitHub Personal Access Token 생성**: https://github.com/settings/tokens

---

**작성일**: 2025년 1월  
**버전**: 1.0.0


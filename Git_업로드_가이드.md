# 📤 Git에 소스 업로드 가이드

## 🎯 목표
로컬 프로젝트를 Git 저장소(GitHub, GitLab 등)에 업로드하는 방법을 단계별로 설명합니다.

---

## 📋 사전 준비

### 1. Git 설치 확인
```bash
git --version
```

**Git이 설치되어 있지 않은 경우:**
- Windows: https://git-scm.com/download/win 에서 다운로드
- 설치 후 명령 프롬프트나 PowerShell을 재시작

### 2. Git 사용자 정보 설정 (최초 1회)
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

---

## 🚀 Git 저장소에 업로드하는 방법

### 방법 1: 새 저장소 생성 (처음 업로드하는 경우)

#### 1단계: 로컬 Git 저장소 초기화
```bash
cd C:\test\test02
git init
```

#### 2단계: 파일 추가
```bash
# 모든 파일 추가
git add .

# 또는 특정 파일만 추가
git add 파일명
```

#### 3단계: 첫 커밋 생성
```bash
git commit -m "Initial commit: 프로젝트 초기 설정"
```

#### 4단계: 원격 저장소 추가
```bash
# GitHub 예시
git remote add origin https://github.com/사용자명/저장소명.git

# 또는 SSH 사용
git remote add origin git@github.com:사용자명/저장소명.git
```

#### 5단계: 원격 저장소에 푸시
```bash
# 기본 브랜치가 main인 경우
git branch -M main
git push -u origin main

# 기본 브랜치가 master인 경우
git branch -M master
git push -u origin master
```

---

### 방법 2: 기존 저장소에 연결 (이미 Git 저장소가 있는 경우)

#### 1단계: 원격 저장소 확인
```bash
git remote -v
```

#### 2단계: 변경사항 확인
```bash
git status
```

#### 3단계: 변경된 파일 추가
```bash
# 모든 변경사항 추가
git add .

# 또는 특정 파일만 추가
git add 파일명1 파일명2
```

#### 4단계: 커밋 생성
```bash
git commit -m "커밋 메시지: 변경 내용 설명"
```

#### 5단계: 원격 저장소에 푸시
```bash
git push origin main
# 또는
git push origin master
```

---

## 📝 자주 사용하는 Git 명령어

### 상태 확인
```bash
# 현재 상태 확인
git status

# 변경사항 확인 (간단히)
git status -s

# 커밋 히스토리 확인
git log
git log --oneline  # 한 줄로 표시
```

### 파일 추가/제거
```bash
# 모든 파일 추가
git add .

# 특정 파일 추가
git add 파일명

# 특정 폴더 추가
git add 폴더명/

# 파일 제거 (스테이징 영역에서)
git reset 파일명

# 모든 변경사항 취소 (주의!)
git reset
```

### 커밋
```bash
# 커밋 생성
git commit -m "커밋 메시지"

# 이전 커밋 메시지 수정
git commit --amend -m "새로운 메시지"

# 파일 추가와 커밋을 한 번에
git commit -am "커밋 메시지"
```

### 원격 저장소 관리
```bash
# 원격 저장소 목록 확인
git remote -v

# 원격 저장소 추가
git remote add origin URL

# 원격 저장소 URL 변경
git remote set-url origin 새_URL

# 원격 저장소 삭제
git remote remove origin
```

### 푸시/풀
```bash
# 원격 저장소에 푸시
git push origin main

# 강제 푸시 (주의! 사용 시 신중하게)
git push -f origin main

# 원격 저장소에서 가져오기
git pull origin main

# 원격 저장소 정보만 가져오기
git fetch origin
```

---

## ⚠️ 주의사항

### 1. .gitignore 확인
업로드하기 전에 `.gitignore` 파일을 확인하세요:
- 민감한 정보 (API 키, 비밀번호 등)는 업로드하지 마세요
- `data/` 폴더 (데이터베이스 파일)는 제외됩니다
- `.env` 파일은 제외됩니다

### 2. 커밋 메시지 작성 가이드
```bash
# 좋은 예시
git commit -m "feat: AI 뉴스 검색 기능 추가"
git commit -m "fix: 로그인 오류 수정"
git commit -m "docs: README 파일 업데이트"

# 나쁜 예시
git commit -m "수정"
git commit -m "asdf"
```

### 3. 브랜치 관리
```bash
# 새 브랜치 생성
git checkout -b feature/새기능

# 브랜치 전환
git checkout 브랜치명

# 브랜치 목록 확인
git branch

# 브랜치 삭제
git branch -d 브랜치명
```

---

## 🔐 인증 설정

### HTTPS 사용 시 (토큰 필요)
```bash
# GitHub Personal Access Token 사용
# GitHub → Settings → Developer settings → Personal access tokens
# 토큰 생성 후 비밀번호 대신 토큰 사용
```

### SSH 사용 시 (키 설정 필요)
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "your.email@example.com"

# 공개 키 복사 (Windows)
type C:\Users\사용자명\.ssh\id_ed25519.pub | clip

# GitHub → Settings → SSH and GPG keys → New SSH key
# 공개 키 추가
```

---

## 🐛 문제 해결

### 문제 1: "fatal: not a git repository"
```bash
# 해결: Git 저장소 초기화
git init
```

### 문제 2: "fatal: remote origin already exists"
```bash
# 해결: 기존 원격 저장소 제거 후 재추가
git remote remove origin
git remote add origin 새_URL
```

### 문제 3: "error: failed to push some refs"
```bash
# 해결: 원격 저장소의 변경사항 먼저 가져오기
git pull origin main --rebase
git push origin main
```

### 문제 4: "Authentication failed"
```bash
# 해결: 인증 정보 확인
# Windows: 제어판 → 자격 증명 관리자 → Git 자격 증명 확인/수정
```

### 문제 5: "Large files" 오류
```bash
# 해결: 큰 파일은 Git LFS 사용 또는 .gitignore에 추가
# .gitignore에 추가 예시:
*.db
*.sqlite
data/
```

---

## 📚 실전 예시

### 예시 1: 처음부터 끝까지
```bash
# 1. 프로젝트 폴더로 이동
cd C:\test\test02

# 2. Git 초기화
git init

# 3. 파일 추가
git add .

# 4. 첫 커밋
git commit -m "Initial commit: AI 뉴스/음악/도서 추천 시스템"

# 5. GitHub에서 새 저장소 생성 후 URL 복사

# 6. 원격 저장소 추가
git remote add origin https://github.com/사용자명/저장소명.git

# 7. 브랜치 이름 설정
git branch -M main

# 8. 푸시
git push -u origin main
```

### 예시 2: 기존 저장소에 업데이트
```bash
# 1. 변경사항 확인
git status

# 2. 변경된 파일 추가
git add .

# 3. 커밋
git commit -m "feat: MCP 도구 테스트 가이드 추가"

# 4. 푸시
git push origin main
```

---

## 🎓 추가 학습 자료

- **Git 공식 문서**: https://git-scm.com/doc
- **GitHub 가이드**: https://guides.github.com
- **Git 명령어 치트시트**: https://education.github.com/git-cheat-sheet-education.pdf

---

## ✅ 체크리스트

업로드 전 확인사항:

- [ ] Git 설치 확인 (`git --version`)
- [ ] 사용자 정보 설정 (`git config`)
- [ ] `.gitignore` 파일 확인
- [ ] 민감한 정보 제외 확인 (API 키, 비밀번호 등)
- [ ] 데이터베이스 파일 제외 확인 (`data/` 폴더)
- [ ] 원격 저장소 URL 확인
- [ ] 커밋 메시지 작성
- [ ] 푸시 성공 확인

---

**작성일**: 2025년 1월  
**버전**: 1.0.0


# 🔗 GitHub 연동 완전 가이드

## ✅ 현재 상태 확인

```
✅ Git 저장소 초기화됨 (main 브랜치)
✅ Git 사용자 정보 설정됨 (DarkPoni <darkponier@naver.com>)
⚠️ 원격 저장소 URL이 예시로 설정되어 있음 (변경 필요)
```

---

## 🚀 GitHub 연동 단계별 가이드

### 1단계: GitHub에서 새 저장소 생성

#### A. GitHub 웹사이트 접속
- 링크: https://github.com
- 로그인 (darkponier@naver.com 계정)

#### B. 새 저장소 생성
1. 우측 상단 **"+"** 버튼 클릭
2. **"New repository"** 선택

#### C. 저장소 정보 입력
- **Repository name**: `test02` (또는 원하는 이름)
- **Description**: `AI 뉴스/음악/도서 추천 시스템` (선택사항)
- **Public** 또는 **Private** 선택
- ⚠️ **"Initialize this repository with a README" 체크 해제** (이미 로컬에 파일이 있으므로)
- **"Add .gitignore"** 선택 안 함 (이미 있음)
- **"Choose a license"** 선택 안 함 (선택사항)

#### D. 저장소 생성
- **"Create repository"** 버튼 클릭

#### E. 저장소 URL 복사
생성된 저장소 페이지에서 URL 복사:
```
https://github.com/사용자명/test02.git
```
또는 SSH:
```
git@github.com:사용자명/test02.git
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

**예시:**
```bash
git remote add origin https://github.com/DarkPoni/test02.git
```

#### C. 원격 저장소 확인
```bash
git remote -v
```

**예상 출력:**
```
origin  https://github.com/사용자명/test02.git (fetch)
origin  https://github.com/사용자명/test02.git (push)
```

---

### 3단계: 파일 추가 및 커밋

#### A. 모든 파일 추가
```bash
git add .
```

#### B. 커밋 생성
```bash
git commit -m "Initial commit: AI 뉴스/음악/도서 추천 시스템"
```

**커밋 메시지 예시:**
```bash
git commit -m "Initial commit: 프로젝트 초기 설정"
git commit -m "feat: AI 뉴스 검색, 음악 추천, 도서 추천 기능"
git commit -m "docs: README 및 가이드 문서 추가"
```

---

### 4단계: GitHub에 업로드 (푸시)

#### A. 브랜치 이름 확인 및 설정
```bash
# 현재 브랜치 확인
git branch

# 브랜치 이름을 main으로 설정 (이미 main이면 생략 가능)
git branch -M main
```

#### B. GitHub에 푸시
```bash
git push -u origin main
```

**첫 푸시 시 인증 요청:**
- **사용자 이름**: GitHub 사용자명 입력
- **비밀번호**: GitHub Personal Access Token 입력 (비밀번호 아님!)

---

### 5단계: Personal Access Token 생성 (필요한 경우)

#### A. GitHub에서 토큰 생성
1. 링크: https://github.com/settings/tokens
2. **"Generate new token"** → **"Generate new token (classic)"** 클릭
3. **Note**: `test02-project` (토큰 이름)
4. **Expiration**: 원하는 만료일 선택
5. **Select scopes**: 
   - ✅ `repo` (전체 체크)
   - ✅ `workflow` (선택사항)
6. **"Generate token"** 클릭
7. ⚠️ **토큰 복사** (한 번만 표시됨! 저장해두세요)

#### B. 푸시 시 토큰 사용
```bash
git push -u origin main
```
- 사용자 이름: GitHub 사용자명
- 비밀번호: 방금 생성한 Personal Access Token

---

## 📋 전체 명령어 (한 번에 실행)

```bash
# 1. 프로젝트 폴더로 이동
cd C:\test\test02

# 2. 기존 원격 저장소 제거 (예시 URL인 경우)
git remote remove origin

# 3. 실제 GitHub 저장소 URL로 연결
git remote add origin https://github.com/사용자명/test02.git

# 4. 원격 저장소 확인
git remote -v

# 5. 모든 파일 추가
git add .

# 6. 커밋 생성
git commit -m "Initial commit: AI 뉴스/음악/도서 추천 시스템"

# 7. 브랜치 이름 확인
git branch

# 8. GitHub에 푸시
git push -u origin main
```

---

## 🔍 현재 상태 확인 명령어

```bash
# Git 상태 확인
git status

# 원격 저장소 확인
git remote -v

# 브랜치 확인
git branch

# 커밋 히스토리 확인
git log --oneline

# 사용자 정보 확인
git config --global user.name
git config --global user.email
```

---

## ⚠️ 문제 해결

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

### 문제 4: "fatal: not a git repository"
```bash
# 해결: Git 저장소 초기화
git init
```

### 문제 5: "Permission denied"
**해결:**
- SSH 키 설정 확인: https://github.com/settings/keys
- 또는 HTTPS + Personal Access Token 사용

---

## 🔐 인증 방법 선택

### 방법 1: HTTPS + Personal Access Token (권장)
- ✅ 설정 간단
- ✅ 보안 좋음
- ⚠️ 토큰 관리 필요

### 방법 2: SSH 키
- ✅ 한 번 설정하면 편리
- ⚠️ 초기 설정 복잡

**SSH 키 설정:**
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "darkponier@naver.com"

# 공개 키 복사 (Windows)
type C:\Users\사용자명\.ssh\id_ed25519.pub | clip

# GitHub에 추가: https://github.com/settings/keys
```

---

## ✅ 연동 확인 체크리스트

- [ ] GitHub에서 새 저장소 생성 완료
- [ ] 저장소 URL 복사 완료
- [ ] 로컬에서 원격 저장소 연결 (`git remote add`)
- [ ] 원격 저장소 확인 (`git remote -v`)
- [ ] 파일 추가 (`git add .`)
- [ ] 커밋 생성 (`git commit`)
- [ ] Personal Access Token 생성 (필요한 경우)
- [ ] GitHub에 푸시 성공 (`git push`)
- [ ] GitHub 웹사이트에서 파일 확인

---

## 🎯 다음 단계

연동 완료 후:

### 1. 변경사항 업로드
```bash
git add .
git commit -m "변경 내용 설명"
git push origin main
```

### 2. README.md 작성
GitHub 저장소에 프로젝트 설명 추가

### 3. .gitignore 확인
민감한 정보가 업로드되지 않았는지 확인

---

## 📚 참고 자료

- **GitHub 공식 문서**: https://docs.github.com
- **Git 공식 문서**: https://git-scm.com/doc
- **Personal Access Token 가이드**: https://docs.github.com/ko/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

**작성일**: 2025년 1월  
**버전**: 1.0.0


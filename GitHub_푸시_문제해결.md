# 🔧 GitHub 푸시 문제 해결 가이드

## ❌ 현재 발생한 문제

```
fatal: unable to access 'https://github.com/hwangjungyong/test02.git/': 
Failed to connect to github.com port 443 after 21107 ms: Could not connect to server
```

**원인:** GitHub 서버에 연결할 수 없음 (네트워크/프록시 문제)

---

## ✅ 현재 완료된 작업

- ✅ Git 저장소 초기화 완료
- ✅ 원격 저장소 연결 완료: `https://github.com/hwangjungyong/test02.git`
- ✅ 파일 추가 완료 (`git add .`)
- ✅ 커밋 완료 (`git commit`)
- ⚠️ 푸시 실패 (네트워크 문제)

---

## 🔧 해결 방법

### 방법 1: 네트워크 연결 확인

```bash
# GitHub 연결 테스트
ping github.com

# 또는 브라우저에서 접속 테스트
# https://github.com 접속 가능한지 확인
```

### 방법 2: 프록시 설정 (회사/학교 네트워크인 경우)

```bash
# 프록시 설정 확인
git config --global http.proxy
git config --global https.proxy

# 프록시 설정 (필요한 경우)
git config --global http.proxy http://프록시주소:포트
git config --global https.proxy http://프록시주소:포트

# 프록시 제거 (필요한 경우)
git config --global --unset http.proxy
git config --global --unset https.proxy
```

### 방법 3: SSH 사용 (프록시 문제 우회)

#### A. SSH 키 생성
```bash
# SSH 키 생성
ssh-keygen -t ed25519 -C "darkponier@naver.com"

# 엔터 3번 (기본 경로 사용, 비밀번호 없음)
```

#### B. 공개 키 복사
```bash
# Windows PowerShell
type C:\Users\사용자명\.ssh\id_ed25519.pub | clip

# 또는 직접 확인
type C:\Users\사용자명\.ssh\id_ed25519.pub
```

#### C. GitHub에 SSH 키 추가
1. 링크: https://github.com/settings/keys
2. "New SSH key" 클릭
3. Title: `My PC` (원하는 이름)
4. Key: 복사한 공개 키 붙여넣기
5. "Add SSH key" 클릭

#### D. 원격 저장소를 SSH로 변경
```bash
# 기존 HTTPS 제거
git remote remove origin

# SSH로 추가
git remote add origin git@github.com:hwangjungyong/test02.git

# 확인
git remote -v

# 푸시
git push -u origin main
```

### 방법 4: VPN 사용

회사/학교 네트워크에서 GitHub 접근이 차단된 경우:
- VPN 연결 후 다시 시도
- 개인 네트워크로 변경 후 시도

### 방법 5: 방화벽 확인

Windows 방화벽이나 안티바이러스가 차단하는지 확인:
- 방화벽 예외 추가
- 안티바이러스 일시 중지 후 테스트

---

## 🚀 네트워크 문제 해결 후 푸시

연결 문제가 해결되면:

```bash
cd C:\test\test02

# 현재 상태 확인
git status
git remote -v

# GitHub에 푸시
git push -u origin main
```

**인증 요청 시:**
- 사용자 이름: `hwangjungyong`
- 비밀번호: GitHub Personal Access Token (비밀번호 아님!)

---

## 📋 Personal Access Token 생성 (필요한 경우)

1. 링크: https://github.com/settings/tokens
2. "Generate new token" → "Generate new token (classic)"
3. Note: `test02-project`
4. Expiration: 원하는 기간 선택
5. Select scopes: ✅ `repo` 체크
6. "Generate token" 클릭
7. ⚠️ 토큰 복사 (한 번만 표시됨!)

---

## ✅ 현재 상태 요약

### 완료된 작업
- ✅ Git 저장소 초기화
- ✅ 원격 저장소 연결: `https://github.com/hwangjungyong/test02.git`
- ✅ 파일 커밋 완료

### 남은 작업
- ⚠️ GitHub에 푸시 (네트워크 문제 해결 후)

### 커밋된 내용
```
커밋 ID: e230216
메시지: Initial commit: AI News/Music/Book Recommendation System
파일: 2개 (GitHub_연동_가이드.md, Git_계정_확인_가이드.md)
```

---

## 🔍 확인 명령어

```bash
# 원격 저장소 확인
git remote -v

# 커밋 히스토리 확인
git log --oneline

# 현재 상태 확인
git status

# 브랜치 확인
git branch
```

---

## 📚 참고 자료

- **GitHub 연결 문제 해결**: https://docs.github.com/ko/get-started/getting-started-with-git/troubleshooting
- **SSH 키 설정**: https://docs.github.com/ko/authentication/connecting-to-github-with-ssh
- **Personal Access Token**: https://docs.github.com/ko/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token

---

**작성일**: 2025년 1월  
**버전**: 1.0.0


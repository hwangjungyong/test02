# 🔍 Git 계정 정보 확인 가이드

## 📋 로컬 Git 계정 정보 확인

### 명령어로 확인
```bash
# 사용자 이름 확인
git config --global user.name

# 이메일 확인
git config --global user.email

# 모든 설정 확인
git config --list --global
```

**현재 설정:**
- 사용자 이름: `DarkPoni`
- 이메일: `darkponier@naver.com`

---

## 🌐 인터넷상에서 Git 계정 확인

### 1. GitHub에서 확인

#### GitHub 프로필 페이지
**링크:** https://github.com/settings/profile

**확인 가능한 정보:**
- 프로필 이름
- 사용자 이름 (Username)
- 이메일 주소
- 프로필 사진
- Bio (소개)

#### GitHub 이메일 설정 확인
**링크:** https://github.com/settings/emails

**확인 가능한 정보:**
- 등록된 이메일 주소 목록
- 공개/비공개 설정
- 기본 이메일 설정

#### GitHub 계정 설정
**링크:** https://github.com/settings/account

**확인 가능한 정보:**
- 계정 정보
- 계정 삭제 옵션
- 데이터 내보내기

---

### 2. GitLab에서 확인

#### GitLab 프로필 설정
**링크:** https://gitlab.com/-/profile

**확인 가능한 정보:**
- 사용자 이름
- 이메일 주소
- 프로필 정보

#### GitLab 이메일 설정
**링크:** https://gitlab.com/-/profile/emails

---

### 3. Bitbucket에서 확인

#### Bitbucket 계정 설정
**링크:** https://bitbucket.org/account/settings/

**확인 가능한 정보:**
- 사용자 이름
- 이메일 주소
- 프로필 정보

---

## 🔗 주요 Git 서비스 링크

### GitHub
- **메인 페이지:** https://github.com
- **프로필 설정:** https://github.com/settings/profile
- **이메일 설정:** https://github.com/settings/emails
- **계정 설정:** https://github.com/settings/account
- **Personal Access Tokens:** https://github.com/settings/tokens
- **SSH 키 설정:** https://github.com/settings/keys

### GitLab
- **메인 페이지:** https://gitlab.com
- **프로필 설정:** https://gitlab.com/-/profile
- **이메일 설정:** https://gitlab.com/-/profile/emails
- **SSH 키 설정:** https://gitlab.com/-/profile/keys

### Bitbucket
- **메인 페이지:** https://bitbucket.org
- **계정 설정:** https://bitbucket.org/account/settings/

---

## 📧 이메일로 계정 확인

### GitHub 이메일 확인
1. https://github.com/settings/emails 접속
2. 로그인 필요
3. 등록된 이메일 주소 목록 확인
4. `darkponier@naver.com`이 등록되어 있는지 확인

### 이메일로 GitHub 계정 찾기
- 이메일 주소로 GitHub 계정 검색: https://github.com/search?q=darkponier@naver.com&type=Users
- (공개 설정된 경우에만 표시됨)

---

## 🔐 Personal Access Token 확인 (GitHub)

**링크:** https://github.com/settings/tokens

**확인 가능한 정보:**
- 생성된 토큰 목록
- 토큰 권한
- 토큰 만료일
- 토큰 사용 이력

**토큰 생성 방법:**
1. https://github.com/settings/tokens 접속
2. "Generate new token" → "Generate new token (classic)" 클릭
3. 토큰 이름 입력
4. 권한 선택 (repo, workflow 등)
5. "Generate token" 클릭
6. **토큰 복사 (한 번만 표시됨!)**

---

## 🔑 SSH 키 확인 (GitHub)

**링크:** https://github.com/settings/keys

**확인 가능한 정보:**
- 등록된 SSH 공개 키 목록
- 키 제목
- 키 생성일
- 마지막 사용일

**로컬 SSH 키 확인:**
```bash
# SSH 키 목록 확인
ls -la ~/.ssh

# 공개 키 확인 (Windows)
type C:\Users\사용자명\.ssh\id_ed25519.pub
# 또는
cat ~/.ssh/id_ed25519.pub
```

---

## 📊 커밋 히스토리에서 확인

### GitHub 저장소에서 확인
1. 저장소 페이지 접속
2. "Commits" 탭 클릭
3. 커밋 작성자 정보 확인
4. 커밋 클릭하여 상세 정보 확인

**예시 링크 형식:**
```
https://github.com/사용자명/저장소명/commits/main
```

---

## 🛠️ Git 설정 확인 명령어 모음

```bash
# 로컬 사용자 이름 확인
git config --global user.name

# 로컬 이메일 확인
git config --global user.email

# 모든 글로벌 설정 확인
git config --list --global

# 특정 저장소의 설정 확인
git config --list --local

# 원격 저장소 URL 확인
git remote -v

# 커밋 작성자 정보 확인
git log --format='%an <%ae>' | head -1

# 최근 커밋의 작성자 확인
git log -1 --format='%an <%ae>'
```

---

## 🔍 계정 정보 확인 체크리스트

### 로컬 확인
- [ ] `git config --global user.name` 실행
- [ ] `git config --global user.email` 실행
- [ ] 현재 설정: `DarkPoni <darkponier@naver.com>`

### GitHub 확인
- [ ] https://github.com/settings/profile 접속
- [ ] 프로필 이름 확인
- [ ] https://github.com/settings/emails 접속
- [ ] 이메일 주소 확인 (`darkponier@naver.com`)
- [ ] 이메일이 공개/비공개로 설정되어 있는지 확인

### 커밋 확인
- [ ] GitHub 저장소의 커밋 히스토리 확인
- [ ] 커밋 작성자 정보 확인
- [ ] 이메일이 올바르게 표시되는지 확인

---

## ⚠️ 주의사항

1. **이메일 공개 설정**
   - GitHub에서 이메일을 공개로 설정하면 누구나 볼 수 있습니다
   - 비공개 설정을 권장합니다

2. **커밋 이메일 일치**
   - 로컬 Git 설정의 이메일과 GitHub 계정의 이메일이 일치해야 커밋이 계정에 연결됩니다

3. **Personal Access Token 보안**
   - 토큰은 비밀번호처럼 관리하세요
   - 토큰을 코드에 직접 작성하지 마세요
   - `.env` 파일이나 환경 변수로 관리하세요

---

## 📚 추가 참고 자료

- **GitHub 공식 문서:** https://docs.github.com
- **Git 공식 문서:** https://git-scm.com/doc
- **GitHub 계정 설정 가이드:** https://docs.github.com/ko/get-started/getting-started-with-git/setting-your-username-in-git

---

**작성일**: 2025년 1월  
**버전**: 1.0.0


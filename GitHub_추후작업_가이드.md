# 🚀 GitHub 추후 작업 가이드

## ✅ 현재 상태

**성공적으로 업로드 완료!**
- 저장소: https://github.com/hwangjungyong/test02
- 브랜치: `main`
- 총 56개 객체 업로드 완료
- 원격 저장소와 로컬 저장소 연결 완료

---

## 📝 추후 작업 방법

### 1. 변경사항 업로드 (가장 자주 사용)

#### A. 변경사항 확인
```bash
cd C:\test\test02
git status
```

#### B. 변경된 파일 추가
```bash
# 모든 변경사항 추가
git add .

# 또는 특정 파일만 추가
git add 파일명1 파일명2
```

#### C. 커밋 생성
```bash
git commit -m "커밋 메시지: 변경 내용 설명"
```

**커밋 메시지 예시:**
```bash
git commit -m "feat: 새로운 기능 추가"
git commit -m "fix: 버그 수정"
git commit -m "docs: 문서 업데이트"
git commit -m "style: 코드 포맷팅"
git commit -m "refactor: 코드 리팩토링"
```

#### D. GitHub에 푸시
```bash
git push origin main
```

**전체 과정 (한 번에):**
```bash
git add .
git commit -m "변경 내용 설명"
git push origin main
```

---

### 2. 원격 저장소에서 최신 변경사항 가져오기

#### A. 다른 컴퓨터에서 작업한 경우
```bash
# 원격 저장소의 변경사항 가져오기
git pull origin main

# 또는 fetch + merge
git fetch origin
git merge origin/main
```

#### B. 충돌 해결
```bash
# 충돌 발생 시
git pull origin main
# 충돌 파일 수정 후
git add .
git commit -m "Merge: 충돌 해결"
git push origin main
```

---

### 3. 새 브랜치 생성 및 작업

#### A. 새 브랜치 생성
```bash
# 새 브랜치 생성 및 전환
git checkout -b feature/새기능

# 또는
git branch feature/새기능
git checkout feature/새기능
```

#### B. 브랜치에서 작업
```bash
# 파일 수정 후
git add .
git commit -m "feat: 새 기능 구현"
git push origin feature/새기능
```

#### C. 브랜치 병합
```bash
# main 브랜치로 전환
git checkout main

# 새 브랜치 병합
git merge feature/새기능

# GitHub에 푸시
git push origin main
```

---

### 4. 파일 삭제

#### A. 파일 삭제 후 커밋
```bash
# 파일 삭제
git rm 파일명

# 또는 폴더 삭제
git rm -r 폴더명

# 커밋
git commit -m "remove: 불필요한 파일 삭제"
git push origin main
```

---

### 5. 커밋 히스토리 확인

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

### 6. 이전 커밋으로 되돌리기

#### A. 커밋 취소 (로컬만)
```bash
# 마지막 커밋 취소 (파일은 유지)
git reset --soft HEAD~1

# 마지막 커밋 취소 (파일 변경도 취소)
git reset --hard HEAD~1
```

#### B. 특정 커밋으로 되돌리기
```bash
# 커밋 ID 확인
git log --oneline

# 특정 커밋으로 되돌리기
git reset --hard 커밋ID
```

---

## 🔐 Personal Access Token 생성 방법

### 1단계: GitHub 접속
**링크:** https://github.com/settings/tokens

또는:
1. GitHub 로그인
2. 우측 상단 프로필 아이콘 클릭
3. **Settings** 클릭
4. 좌측 메뉴에서 **Developer settings** 클릭
5. **Personal access tokens** → **Tokens (classic)** 클릭

### 2단계: 새 토큰 생성
1. **"Generate new token"** 버튼 클릭
2. **"Generate new token (classic)"** 선택

### 3단계: 토큰 설정
- **Note**: 토큰 이름 입력 (예: `test02-project`, `My PC`)
- **Expiration**: 만료일 선택
  - 30 days (30일)
  - 60 days (60일)
  - 90 days (90일)
  - Custom (사용자 지정)
  - No expiration (만료 없음) - ⚠️ 보안상 권장하지 않음

### 4단계: 권한 선택 (Scopes)
필수 권한:
- ✅ **repo** (전체 체크)
  - `repo:status`
  - `repo_deployment`
  - `public_repo`
  - `repo:invite`
  - `security_events`

선택 권한:
- ✅ **workflow** (GitHub Actions 사용 시)
- ✅ **write:packages** (패키지 업로드 시)
- ✅ **delete:packages** (패키지 삭제 시)

### 5단계: 토큰 생성
1. **"Generate token"** 버튼 클릭
2. ⚠️ **토큰 복사** (한 번만 표시됨!)
   - 예: `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`
3. 안전한 곳에 저장 (비밀번호 관리자 권장)

### 6단계: 토큰 사용
#### A. 푸시 시 사용
```bash
git push origin main
```
- 사용자 이름: `hwangjungyong`
- 비밀번호: 생성한 Personal Access Token 입력

#### B. Windows 자격 증명 관리자에 저장
- Windows가 자동으로 저장할 수 있음
- 제어판 → 자격 증명 관리자 → Windows 자격 증명에서 확인 가능

---

## 🔑 Personal Access Token 관리

### 토큰 목록 확인
**링크:** https://github.com/settings/tokens

### 토큰 삭제
1. https://github.com/settings/tokens 접속
2. 삭제할 토큰 옆 **"Delete"** 클릭
3. 확인

### 토큰 권한 수정
1. 토큰 목록에서 토큰 클릭
2. 권한 수정 후 저장

---

## ⚠️ 보안 주의사항

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

## 📋 자주 사용하는 명령어 모음

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

## 🎯 실전 예시

### 예시 1: 새 기능 추가 후 업로드
```bash
# 1. 파일 수정
# 2. 변경사항 확인
git status

# 3. 파일 추가
git add .

# 4. 커밋
git commit -m "feat: AI 뉴스 검색 기능 개선"

# 5. 푸시
git push origin main
```

### 예시 2: 버그 수정 후 업로드
```bash
git add .
git commit -m "fix: 로그인 오류 수정"
git push origin main
```

### 예시 3: 문서 업데이트
```bash
git add .
git commit -m "docs: README 파일 업데이트"
git push origin main
```

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

**작성일**: 2025년 1월  
**버전**: 1.0.0


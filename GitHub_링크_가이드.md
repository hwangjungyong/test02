# 🔗 GitHub 파일 링크 공유 가이드

## 📋 코드 리뷰 리포트 공유 링크

### 방법 1: GitHub 웹사이트 링크 (권장)

**기본 링크:**
```
https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md
```

**특정 커밋 버전 링크:**
```
https://github.com/hwangjungyong/test02/blob/8d3fd41/코드_리뷰_리포트.md
```

**Raw 파일 링크 (텍스트만):**
```
https://github.com/hwangjungyong/test02/raw/main/코드_리뷰_리포트.md
```

---

## 📤 동료에게 공유하는 방법

### 방법 1: 직접 링크 복사

1. **GitHub 저장소 접속**
   - https://github.com/hwangjungyong/test02

2. **파일 찾기**
   - `코드_리뷰_리포트.md` 파일 클릭

3. **링크 복사**
   - 우측 상단 "Raw" 버튼 옆의 링크 아이콘 클릭
   - 또는 브라우저 주소창에서 URL 복사

4. **공유**
   - 이메일, 메신저, 슬랙 등에 링크 붙여넣기

---

### 방법 2: Markdown 형식으로 공유

```markdown
코드 리뷰 리포트를 확인해주세요:

[코드 리뷰 리포트 보기](https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md)
```

---

### 방법 3: GitHub Gist 사용 (선택사항)

1. **Gist 생성**
   - https://gist.github.com 접속
   - 파일 내용 복사하여 Gist 생성
   - 공개/비공개 설정

2. **Gist 링크 공유**
   - 생성된 Gist 링크 공유

**장점:**
- 저장소와 독립적으로 공유 가능
- 댓글 기능 사용 가능
- 수정 이력 관리

---

## 🔗 주요 파일 링크 모음

### 프로젝트 문서

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

**MCP 서버 가이드:**
```
https://github.com/hwangjungyong/test02/blob/main/MCP_서버_완전가이드.md
```

**GitHub 연동 가이드:**
```
https://github.com/hwangjungyong/test02/blob/main/GitHub_연동_가이드.md
```

---

## 📝 링크 형식 설명

### GitHub 파일 링크 구조

```
https://github.com/[사용자명]/[저장소명]/blob/[브랜치명]/[파일경로]
```

**예시:**
```
https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md
         └─────────┘ └─────┘ └───┘ └────┘ └──────────────────┘
         사용자명    저장소  blob  브랜치      파일명
```

### 링크 타입

1. **blob 링크** (기본)
   - 파일을 GitHub 웹사이트에서 보기
   - 형식: `.../blob/main/파일명`

2. **raw 링크** (원본 텍스트)
   - 파일의 원본 텍스트만 보기
   - 형식: `.../raw/main/파일명`

3. **특정 커밋 링크**
   - 특정 버전의 파일 보기
   - 형식: `.../blob/커밋해시/파일명`

---

## 🎯 빠른 공유 템플릿

### 이메일/메신저용

```
안녕하세요,

코드 리뷰 리포트를 작성했습니다. 확인 부탁드립니다.

📊 코드 리뷰 리포트:
https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md

주요 내용:
- 종합 점수: 3.2/5.0
- 문서화: ⭐⭐⭐⭐⭐
- 코드 구조: 개선 필요
- 보안: 강화 필요

피드백 부탁드립니다!
```

### 슬랙/디스코드용

```
코드 리뷰 리포트 작성 완료! 📊

링크: https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md

주요 개선 사항:
🔴 긴급: 코드 구조 개선 (App.vue 9,533줄)
🔴 긴급: 보안 강화 (API 키 하드코딩 제거)
🟡 중요: 테스트 추가

리뷰 부탁드립니다!
```

---

## 🔍 링크 확인 방법

### 링크가 제대로 작동하는지 확인

1. **브라우저에서 직접 접속**
   ```
   https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md
   ```

2. **파일이 보이는지 확인**
   - 파일 내용이 표시되어야 함
   - 404 에러가 나오면 파일명이나 경로 확인

3. **권한 확인**
   - Public 저장소: 누구나 접근 가능
   - Private 저장소: 저장소 접근 권한 필요

---

## ⚠️ 주의사항

### 한글 파일명

한글 파일명은 URL 인코딩되어 표시될 수 있습니다:
- `코드_리뷰_리포트.md` → `%EC%BD%94%EB%93%9C_%EB%A6%AC%EB%B7%B0_%EB%A6%AC%ED%8F%AC%ED%8A%B8.md`

하지만 GitHub는 자동으로 처리하므로 걱정하지 않아도 됩니다.

### Private 저장소

Private 저장소의 경우:
- 링크를 받은 사람도 저장소 접근 권한이 있어야 함
- 또는 Public으로 변경 필요

---

## 📚 추가 팁

### 링크를 더 예쁘게 만들기

**GitHub 단축 링크 (선택사항):**
- GitHub는 자동으로 단축 링크를 제공하지 않음
- bit.ly, tinyurl 등 사용 가능

**Markdown 링크:**
```markdown
[코드 리뷰 리포트](https://github.com/hwangjungyong/test02/blob/main/코드_리뷰_리포트.md)
```

---

## ✅ 체크리스트

링크 공유 전 확인:
- [ ] 저장소가 Public인지 확인 (또는 공유 대상에게 권한 부여)
- [ ] 파일이 최신 커밋에 포함되어 있는지 확인
- [ ] 링크가 정상 작동하는지 테스트
- [ ] 공유할 내용 요약 준비

---

**작성일**: 2025년 1월  
**버전**: 1.0.0


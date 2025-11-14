# 🐍 Python MCP 서버 완전 가이드

## 🎯 Python MCP 서버란?

**Python MCP 서버는 Python으로 작성된 MCP (Model Context Protocol) 서버**입니다.

### 간단한 설명

```
Python MCP 서버 = Python으로 만든 AI 도구 제공 서버

예시:
👤 사용자: "5와 7을 더해줘"
🤖 AI: Python MCP 서버의 add_numbers 도구 사용
🐍 Python 서버: "5 + 7 = 12" 반환
🤖 AI: "답은 12입니다!"
```

---

## 📦 프로젝트의 Python MCP 서버

### 1️⃣ **mcp-unified-server.py** (통합 서버)

**기본 정보:**
- **이름**: `unified-mcp-server`
- **언어**: Python 3
- **파일 위치**: `mcp-unified-server.py`
- **실행 방법**: `python mcp-unified-server.py` 또는 `npm run mcp-unified`
- **통신 방식**: 표준 입출력 (stdin/stdout)

---

## 🛠️ 제공하는 기능 (도구)

이 서버는 **4가지 도구**를 제공합니다:

### 1. `add_numbers` - 덧셈 계산기

**무엇을 하나요?**
- 두 개의 숫자를 입력받아 더한 결과를 반환합니다

**사용 예시:**
```
"5와 7을 더해줘"
→ add_numbers 도구 사용 (a: 5, b: 7)
→ 결과: "5 + 7 = 12"
```

**입력 파라미터:**
- `a` (필수): 첫 번째 숫자
- `b` (필수): 두 번째 숫자

**반환 정보:**
- 계산 결과 (예: "5 + 7 = 12")

**코드 예시:**
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    if name == "add_numbers":
        a = float(arguments.get("a", 0))
        b = float(arguments.get("b", 0))
        result = a + b
        return [TextContent(type="text", text=f"{a} + {b} = {result}")]
```

---

### 2. `recommend_books` - 도서 추천

**무엇을 하나요?**
- 키워드나 장르를 입력받아 관련 도서를 추천합니다
- Google Books API를 사용하여 실제 도서 정보를 가져옵니다

**사용 예시:**
```
"인공지능 관련 책을 추천해줘"
→ recommend_books 도구 사용 (query: "인공지능", maxResults: 10)
→ 결과: 인공지능 관련 도서 10개 반환
```

**입력 파라미터:**
- `query` (필수): 검색 키워드 또는 장르 (예: "인공지능", "소설", "경제")
- `maxResults` (선택): 최대 결과 개수 (기본값: 10)

**반환 정보:**
- 도서 제목
- 저자
- 출판사
- 출판일
- 카테고리
- 평점
- 설명
- 링크

**API 사용:**
- Google Books API: `https://www.googleapis.com/books/v1/volumes`

---

### 3. `get_popular_books` - 인기 도서 목록

**무엇을 하나요?**
- 인기 도서 목록을 가져옵니다
- Google Books API를 사용하여 베스트셀러 정보를 가져옵니다

**사용 예시:**
```
"인기 소설을 알려줘"
→ get_popular_books 도구 사용 (category: "fiction", maxResults: 20)
→ 결과: 인기 소설 20개 반환
```

**입력 파라미터:**
- `category` (선택): 도서 카테고리 (예: "fiction", "nonfiction", "computers")
- `maxResults` (선택): 최대 결과 개수 (기본값: 20)

**반환 정보:**
- 인기 도서 목록 (제목, 저자, 출판사, 카테고리, 평점, 링크)

---

### 4. `get_book_details` - 도서 상세 정보

**무엇을 하나요?**
- 특정 도서의 상세 정보를 가져옵니다

**사용 예시:**
```
"이 책의 상세 정보를 알려줘 (bookId: abc123)"
→ get_book_details 도구 사용 (bookId: "abc123")
→ 결과: 도서 상세 정보 반환
```

**입력 파라미터:**
- `bookId` (필수): Google Books API의 도서 ID

**반환 정보:**
- 제목
- 저자
- 출판사
- 출판일
- 페이지 수
- 언어
- 카테고리
- 평점
- 설명
- 링크

---

## 🚀 설치 및 실행

### 1단계: Python 설치 확인

```bash
python --version
# 또는
python3 --version
```

**Python이 설치되어 있지 않은 경우:**
- Windows: https://www.python.org/downloads/
- Mac: `brew install python3`
- Linux: `sudo apt install python3`

### 2단계: 의존성 설치

```bash
# MCP SDK 설치
pip install mcp

# 또는 requirements.txt 사용
pip install -r requirements.txt
```

**requirements.txt 내용:**
```
mcp>=0.1.0
```

### 3단계: 서버 실행

```bash
# 직접 실행
python mcp-unified-server.py

# 또는 npm 스크립트 사용
npm run mcp-unified
```

**실행 확인:**
서버가 정상적으로 실행되면 표준 입출력을 통해 MCP 프로토콜로 통신을 시작합니다.

---

## ⚙️ Cursor AI 설정

### cursor-mcp-config.json 설정

```json
{
  "mcpServers": {
    "unified-mcp-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-unified-server.py"],
      "cwd": "C:/test/test02",
      "description": "덧셈 계산기 및 도서 검색/추천 통합 서버"
    }
  }
}
```

**경로 설정:**
- `command`: Python 실행 파일 경로 (보통 "python" 또는 "python3")
- `args`: 실행할 Python 스크립트 파일
- `cwd`: 작업 디렉토리 (절대 경로 권장)

**Windows 예시:**
```json
{
  "mcpServers": {
    "unified-mcp-server": {
      "command": "python",
      "args": ["C:/test/test02/mcp-unified-server.py"],
      "cwd": "C:/test/test02"
    }
  }
}
```

**Mac/Linux 예시:**
```json
{
  "mcpServers": {
    "unified-mcp-server": {
      "command": "python3",
      "args": ["/Users/username/projects/test02/mcp-unified-server.py"],
      "cwd": "/Users/username/projects/test02"
    }
  }
}
```

---

## 🧪 테스트 방법

### 1. Cursor AI 채팅에서 테스트

Cursor AI 채팅에서 다음과 같이 요청하면 Python MCP 서버가 자동으로 사용됩니다:

```
"5와 7을 더해줘"
→ add_numbers 도구 사용
→ 결과: 12

"인공지능 관련 책을 추천해줘"
→ recommend_books 도구 사용
→ 결과: 인공지능 관련 도서 목록

"인기 소설을 알려줘"
→ get_popular_books 도구 사용
→ 결과: 인기 소설 목록
```

### 2. 수동 실행 테스트

```bash
# 서버 실행
python mcp-unified-server.py

# 서버가 정상적으로 시작되면 stdin/stdout을 통해 통신합니다
```

---

## 🔧 기술적 세부사항

### 사용하는 라이브러리

- **MCP SDK**: `mcp` 패키지
  - 설치: `pip install mcp`
  - 역할: MCP 프로토콜 구현

- **표준 라이브러리**:
  - `asyncio`: 비동기 처리
  - `json`: JSON 파싱
  - `urllib`: HTTP 요청

### 통신 방식

- **StdioServerTransport**: 표준 입출력 (stdin/stdout) 사용
- Cursor AI와 직접 통신
- JSON 형식으로 메시지 교환

### 에러 처리

- API 호출 실패 시 에러 메시지 반환
- 타임아웃: 30초
- 예외 처리 포함

---

## ⚠️ 문제 해결

### 문제 1: "MCP SDK가 설치되지 않았습니다"

**증상:**
```
MCP SDK가 설치되지 않았습니다. 다음 명령어로 설치하세요:
pip install mcp
```

**해결 방법:**
```bash
pip install mcp
# 또는
pip3 install mcp
```

### 문제 2: "Python을 찾을 수 없습니다"

**증상:**
- Cursor에서 Python MCP 서버 실행 실패
- "command not found" 오류

**해결 방법:**
1. Python 설치 확인:
   ```bash
   python --version
   ```

2. cursor-mcp-config.json에서 Python 경로 확인:
   ```json
   {
     "command": "python"  // 또는 "python3", "C:/Python/python.exe"
   }
   ```

### 문제 3: "모듈을 찾을 수 없습니다"

**증상:**
```
ModuleNotFoundError: No module named 'mcp'
```

**해결 방법:**
```bash
# MCP SDK 재설치
pip install --upgrade mcp

# 또는 가상 환경 사용
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install mcp
```

### 문제 4: "권한 오류"

**증상:**
- 파일 실행 권한 없음
- 접근 거부 오류

**해결 방법:**
```bash
# Windows: 관리자 권한으로 실행
# Mac/Linux: 실행 권한 부여
chmod +x mcp-unified-server.py
```

### 문제 5: "포트 충돌" (해당 없음)

**참고:** Python MCP 서버는 포트를 사용하지 않습니다. 표준 입출력(stdin/stdout)을 사용합니다.

---

## 📚 코드 구조 이해하기

### 주요 함수

#### 1. `list_tools()` - 도구 목록 제공
```python
@server.list_tools()
async def list_tools() -> list[Tool]:
    """사용 가능한 도구 목록 반환"""
    return [
        Tool(name="add_numbers", ...),
        Tool(name="recommend_books", ...),
        ...
    ]
```

#### 2. `call_tool()` - 도구 실행
```python
@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """도구 실행 및 결과 반환"""
    if name == "add_numbers":
        # 덧셈 계산 로직
    elif name == "recommend_books":
        # 도서 추천 로직
    ...
```

#### 3. `main()` - 서버 시작
```python
async def main():
    """서버 시작"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )
```

---

## 🔍 디버깅 방법

### 1. 로그 확인

Python MCP 서버는 표준 에러 출력(stderr)에 로그를 출력합니다.

```bash
# 로그 확인
python mcp-unified-server.py 2>&1 | tee mcp-server.log
```

### 2. 수동 테스트

```python
# test_mcp.py 파일 생성
import asyncio
from mcp_unified_server import server

async def test():
    # 도구 목록 확인
    tools = await server.list_tools()
    print("도구 목록:", tools)
    
    # 도구 실행 테스트
    result = await server.call_tool("add_numbers", {"a": 5, "b": 7})
    print("결과:", result)

asyncio.run(test())
```

### 3. Cursor 로그 확인

- Cursor → View → Output → "MCP" 선택
- MCP 서버 로그 확인

---

## 📊 성능 최적화

### 1. API 호출 최적화

- Google Books API 호출 최소화
- 결과 캐싱 고려
- 타임아웃 설정 (30초)

### 2. 메모리 관리

- 대용량 데이터 처리 시 스트리밍 고려
- 불필요한 데이터 제거

---

## 🔐 보안 고려사항

### 1. 입력 검증

- 모든 입력값 검증
- SQL Injection 방지 (현재는 API 호출만 사용)

### 2. API 키 관리

- Google Books API는 API 키가 필요 없음 (무료)
- 향후 API 키 필요 시 환경 변수 사용

### 3. 에러 메시지

- 민감한 정보 노출 방지
- 사용자 친화적인 에러 메시지

---

## 🎯 사용 예시

### 예시 1: 덧셈 계산

```
사용자: "10과 20을 더해줘"
AI: add_numbers 도구 사용
Python 서버: "10 + 20 = 30"
AI: "답은 30입니다!"
```

### 예시 2: 도서 추천

```
사용자: "머신러닝 관련 책 추천해줘"
AI: recommend_books 도구 사용 (query: "머신러닝")
Python 서버: Google Books API 호출 → 도서 목록 반환
AI: "머신러닝 관련 도서 10권을 추천드립니다: ..."
```

### 예시 3: 인기 도서 조회

```
사용자: "인기 도서 목록 보여줘"
AI: get_popular_books 도구 사용
Python 서버: Google Books API 호출 → 인기 도서 반환
AI: "인기 도서 목록입니다: ..."
```

---

## 📖 추가 학습 자료

- **MCP 프로토콜 공식 문서**: https://modelcontextprotocol.io
- **Google Books API 문서**: https://developers.google.com/books
- **Python asyncio 문서**: https://docs.python.org/3/library/asyncio.html
- **MCP Python SDK**: https://github.com/modelcontextprotocol/python-sdk

---

## ✅ 체크리스트

Python MCP 서버 설정 확인:

- [ ] Python 설치 확인 (`python --version`)
- [ ] MCP SDK 설치 확인 (`pip list | grep mcp`)
- [ ] `mcp-unified-server.py` 파일 존재 확인
- [ ] `cursor-mcp-config.json` 설정 확인
- [ ] Cursor 재시작 완료
- [ ] 서버 수동 실행 테스트 성공
- [ ] Cursor AI에서 도구 사용 테스트 성공

---

## 🔗 관련 파일

- **서버 파일**: `mcp-unified-server.py`
- **설정 파일**: `cursor-mcp-config.json`
- **의존성 파일**: `requirements.txt`
- **통합 가이드**: `MCP_서버_완전가이드.md`

---

**작성일**: 2025년 1월  
**버전**: 1.0.0  
**마지막 업데이트**: 2025년 1월


#!/usr/bin/env python3
"""
MCP 서버 - 도서 추천 및 수집 (Python 버전)

역할:
- MCP 프로토콜을 통해 AI 클라이언트와 통신하는 서버
- Google Books API를 통한 도서 검색 및 추천
- 실시간 도서 정보 수집

실행 방법:
  python mcp-book-server.py

참고:
- Python MCP SDK를 사용하여 구현
- Google Books API를 사용하여 도서 정보를 가져옵니다
- StdioServerTransport를 사용하여 표준 입출력(stdin/stdout)으로 통신합니다
"""

import asyncio
import json
import sys
from typing import Any, Sequence
import urllib.request
import urllib.parse
from urllib.error import URLError, HTTPError

# MCP SDK import (설치 필요: pip install mcp)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install mcp", file=sys.stderr)
    sys.exit(1)

# ============================================
# API 설정
# ============================================

# Google Books API 설정
# - API 키 없이도 사용 가능 (하루 1000회 제한)
# - API 키를 사용하면 하루 100만회까지 사용 가능
GOOGLE_BOOKS_API_BASE_URL = "https://www.googleapis.com/books/v1/volumes"

# ============================================
# MCP 서버 생성
# ============================================

server = Server("book-recommendation-server")

# ============================================
# 도구 목록 제공
# ============================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    사용 가능한 도구 목록을 반환합니다.
    
    반환값:
        list[Tool]: 사용 가능한 도구 목록
    """
    return [
        Tool(
            name="recommend_books",
            description="키워드나 장르를 입력받아 관련 도서를 추천합니다. Google Books API를 사용하여 실제 도서 정보를 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "검색 키워드 또는 장르 (예: '인공지능', '소설', '경제')"
                    },
                    "maxResults": {
                        "type": "integer",
                        "description": "최대 결과 개수 (기본값: 10)",
                        "default": 10
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_popular_books",
            description="인기 도서 목록을 가져옵니다. Google Books API를 사용하여 베스트셀러 정보를 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "도서 카테고리 (예: 'fiction', 'nonfiction', 'computers')",
                        "default": ""
                    },
                    "maxResults": {
                        "type": "integer",
                        "description": "최대 결과 개수 (기본값: 20)",
                        "default": 20
                    }
                }
            }
        ),
        Tool(
            name="get_book_details",
            description="특정 도서의 상세 정보를 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bookId": {
                        "type": "string",
                        "description": "Google Books API의 도서 ID"
                    }
                },
                "required": ["bookId"]
            }
        )
    ]

# ============================================
# 헬퍼 함수
# ============================================

def fetch_google_books_api(url: str) -> dict:
    """
    Google Books API를 호출하는 헬퍼 함수
    
    Args:
        url: 호출할 API URL
        
    Returns:
        dict: API 응답 데이터
        
    Raises:
        Exception: API 호출 실패 시
    """
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode('utf-8'))
            return data
    except HTTPError as e:
        raise Exception(f"Google Books API 오류: {e.code} - {e.reason}")
    except URLError as e:
        raise Exception(f"네트워크 오류: {e.reason}")
    except Exception as e:
        raise Exception(f"API 호출 오류: {str(e)}")

# ============================================
# 도구 실행 핸들러
# ============================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """
    도구 실행 핸들러
    
    Args:
        name: 도구 이름
        arguments: 도구 인자
        
    Returns:
        Sequence[TextContent]: 실행 결과
    """
    try:
        if name == "recommend_books":
            query = arguments.get("query", "")
            max_results = arguments.get("maxResults", 10)
            
            if not query:
                return [TextContent(
                    type="text",
                    text="오류: 검색 키워드가 필요합니다."
                )]
            
            # Google Books API 호출
            params = {
                "q": query,
                "maxResults": min(max_results, 40),  # 최대 40개
                "langRestrict": "ko"  # 한국어 도서만
            }
            api_url = f"{GOOGLE_BOOKS_API_BASE_URL}?{urllib.parse.urlencode(params)}"
            
            data = fetch_google_books_api(api_url)
            
            if not data.get("items"):
                return [TextContent(
                    type="text",
                    text=f"'{query}'에 대한 도서를 찾을 수 없습니다."
                )]
            
            # 결과 포맷팅
            books = []
            for item in data["items"][:max_results]:
                volume_info = item.get("volumeInfo", {})
                book_info = {
                    "제목": volume_info.get("title", "제목 없음"),
                    "저자": ", ".join(volume_info.get("authors", ["저자 정보 없음"])),
                    "출판사": volume_info.get("publisher", "출판사 정보 없음"),
                    "출판일": volume_info.get("publishedDate", "날짜 정보 없음"),
                    "설명": volume_info.get("description", "설명 없음")[:200] + "..." if volume_info.get("description") else "설명 없음",
                    "카테고리": ", ".join(volume_info.get("categories", ["카테고리 없음"])),
                    "평점": volume_info.get("averageRating", "평점 없음"),
                    "평가 수": volume_info.get("ratingsCount", 0),
                    "링크": volume_info.get("infoLink", "#"),
                    "이미지": volume_info.get("imageLinks", {}).get("thumbnail", "")
                }
                books.append(book_info)
            
            result_text = f"'{query}'에 대한 도서 추천 결과 ({len(books)}건):\n\n"
            for i, book in enumerate(books, 1):
                result_text += f"{i}. {book['제목']}\n"
                result_text += f"   저자: {book['저자']}\n"
                result_text += f"   출판사: {book['출판사']} ({book['출판일']})\n"
                result_text += f"   카테고리: {book['카테고리']}\n"
                if book['평점'] != "평점 없음":
                    result_text += f"   평점: {book['평점']}/5.0 (평가 {book['평가 수']}건)\n"
                result_text += f"   설명: {book['설명']}\n"
                result_text += f"   링크: {book['링크']}\n\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_popular_books":
            category = arguments.get("category", "")
            max_results = arguments.get("maxResults", 20)
            
            # Google Books API 호출 (인기 도서)
            params = {
                "q": "subject:bestseller" if not category else f"subject:{category}",
                "maxResults": min(max_results, 40),
                "orderBy": "relevance",
                "langRestrict": "ko"
            }
            api_url = f"{GOOGLE_BOOKS_API_BASE_URL}?{urllib.parse.urlencode(params)}"
            
            data = fetch_google_books_api(api_url)
            
            if not data.get("items"):
                return [TextContent(
                    type="text",
                    text="인기 도서를 찾을 수 없습니다."
                )]
            
            # 결과 포맷팅
            books = []
            for item in data["items"][:max_results]:
                volume_info = item.get("volumeInfo", {})
                book_info = {
                    "제목": volume_info.get("title", "제목 없음"),
                    "저자": ", ".join(volume_info.get("authors", ["저자 정보 없음"])),
                    "출판사": volume_info.get("publisher", "출판사 정보 없음"),
                    "출판일": volume_info.get("publishedDate", "날짜 정보 없음"),
                    "카테고리": ", ".join(volume_info.get("categories", ["카테고리 없음"])),
                    "평점": volume_info.get("averageRating", "평점 없음"),
                    "평가 수": volume_info.get("ratingsCount", 0),
                    "링크": volume_info.get("infoLink", "#")
                }
                books.append(book_info)
            
            result_text = f"인기 도서 목록 ({len(books)}건):\n\n"
            for i, book in enumerate(books, 1):
                result_text += f"{i}. {book['제목']}\n"
                result_text += f"   저자: {book['저자']}\n"
                result_text += f"   출판사: {book['출판사']} ({book['출판일']})\n"
                result_text += f"   카테고리: {book['카테고리']}\n"
                if book['평점'] != "평점 없음":
                    result_text += f"   평점: {book['평점']}/5.0 (평가 {book['평가 수']}건)\n"
                result_text += f"   링크: {book['링크']}\n\n"
            
            return [TextContent(type="text", text=result_text)]
        
        elif name == "get_book_details":
            book_id = arguments.get("bookId", "")
            
            if not book_id:
                return [TextContent(
                    type="text",
                    text="오류: 도서 ID가 필요합니다."
                )]
            
            # Google Books API 호출 (도서 상세 정보)
            api_url = f"{GOOGLE_BOOKS_API_BASE_URL}/{book_id}"
            
            data = fetch_google_books_api(api_url)
            
            volume_info = data.get("volumeInfo", {})
            if not volume_info:
                return [TextContent(
                    type="text",
                    text="도서 정보를 찾을 수 없습니다."
                )]
            
            # 상세 정보 포맷팅
            result_text = f"도서 상세 정보:\n\n"
            result_text += f"제목: {volume_info.get('title', '제목 없음')}\n"
            result_text += f"저자: {', '.join(volume_info.get('authors', ['저자 정보 없음']))}\n"
            result_text += f"출판사: {volume_info.get('publisher', '출판사 정보 없음')}\n"
            result_text += f"출판일: {volume_info.get('publishedDate', '날짜 정보 없음')}\n"
            result_text += f"페이지 수: {volume_info.get('pageCount', '정보 없음')}\n"
            result_text += f"언어: {volume_info.get('language', '정보 없음')}\n"
            result_text += f"카테고리: {', '.join(volume_info.get('categories', ['카테고리 없음']))}\n"
            if volume_info.get('averageRating'):
                result_text += f"평점: {volume_info.get('averageRating')}/5.0 (평가 {volume_info.get('ratingsCount', 0)}건)\n"
            result_text += f"\n설명:\n{volume_info.get('description', '설명 없음')}\n"
            result_text += f"\n링크: {volume_info.get('infoLink', '#')}\n"
            
            return [TextContent(type="text", text=result_text)]
        
        else:
            return [TextContent(
                type="text",
                text=f"알 수 없는 도구: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"오류 발생: {str(e)}"
        )]

# ============================================
# 서버 시작
# ============================================

async def main():
    """
    서버 시작 함수
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    print("MCP 도서 추천 서버가 시작되었습니다.", file=sys.stderr)
    asyncio.run(main())

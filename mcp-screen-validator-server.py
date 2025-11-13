#!/usr/bin/env python3
"""
MCP 서버 - AI 화면 검증 (Python 버전)

역할:
- MCP 프로토콜을 통해 AI 클라이언트와 통신하는 서버
- Playwright를 사용하여 웹 페이지 화면 캡처
- 특정 요소의 값을 읽어서 검증
- 화면 검증 결과를 반환

실행 방법:
  python mcp-screen-validator-server.py

의존성 설치:
  pip install mcp playwright
  playwright install chromium

참고:
- Python MCP SDK를 사용하여 구현
- Playwright를 사용하여 브라우저 자동화
- StdioServerTransport를 사용하여 표준 입출력(stdin/stdout)으로 통신합니다
"""

import asyncio
import json
import sys
import base64
from typing import Any, Sequence
from pathlib import Path
import tempfile

# MCP SDK import (설치 필요: pip install mcp)
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent, ImageContent
except ImportError:
    print("MCP SDK가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install mcp", file=sys.stderr)
    sys.exit(1)

# Playwright import (설치 필요: pip install playwright)
try:
    from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install playwright", file=sys.stderr)
    print("playwright install chromium", file=sys.stderr)
    sys.exit(1)

# ============================================
# MCP 서버 생성
# ============================================

server = Server("screen-validator-server")

# ============================================
# 브라우저 인스턴스 관리
# ============================================

_browser: Browser | None = None
_playwright_context = None

async def get_browser() -> Browser:
    """브라우저 인스턴스를 가져오거나 생성합니다."""
    global _browser, _playwright_context
    
    if _browser is None:
        _playwright_context = await async_playwright().start()
        _browser = await _playwright_context.chromium.launch(headless=True)
    
    return _browser

async def close_browser():
    """브라우저 인스턴스를 종료합니다."""
    global _browser, _playwright_context
    
    if _browser:
        await _browser.close()
        _browser = None
    
    if _playwright_context:
        await _playwright_context.stop()
        _playwright_context = None

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
            name="capture_screen",
            description="URL에 접속하여 화면을 캡처하고 이미지로 반환합니다. 전체 페이지 또는 특정 요소만 캡처할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "접속할 URL (예: https://example.com)"
                    },
                    "selector": {
                        "type": "string",
                        "description": "캡처할 요소의 CSS 선택자 (선택사항, 없으면 전체 페이지 캡처)"
                    },
                    "waitTime": {
                        "type": "integer",
                        "description": "페이지 로딩 대기 시간(밀리초, 기본값: 3000)",
                        "default": 3000
                    },
                    "viewportWidth": {
                        "type": "integer",
                        "description": "뷰포트 너비 (기본값: 1920)",
                        "default": 1920
                    },
                    "viewportHeight": {
                        "type": "integer",
                        "description": "뷰포트 높이 (기본값: 1080)",
                        "default": 1080
                    }
                },
                "required": ["url"]
            }
        ),
        Tool(
            name="read_element_value",
            description="URL에 접속하여 특정 요소의 텍스트 값을 읽어옵니다. CSS 선택자 또는 XPath를 사용할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "접속할 URL (예: https://example.com)"
                    },
                    "selector": {
                        "type": "string",
                        "description": "읽을 요소의 CSS 선택자 (예: #price, .title, h1)"
                    },
                    "selectorType": {
                        "type": "string",
                        "description": "선택자 타입 (css 또는 xpath, 기본값: css)",
                        "enum": ["css", "xpath"],
                        "default": "css"
                    },
                    "waitTime": {
                        "type": "integer",
                        "description": "페이지 로딩 대기 시간(밀리초, 기본값: 3000)",
                        "default": 3000
                    },
                    "attribute": {
                        "type": "string",
                        "description": "읽을 속성 이름 (선택사항, 없으면 텍스트 내용 읽기)"
                    }
                },
                "required": ["url", "selector"]
            }
        ),
        Tool(
            name="validate_screen_element",
            description="URL에 접속하여 특정 요소의 값을 읽고 검증합니다. 화면 캡처와 함께 검증 결과를 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "접속할 URL (예: https://example.com)"
                    },
                    "selector": {
                        "type": "string",
                        "description": "검증할 요소의 CSS 선택자 (예: #price, .title)"
                    },
                    "expectedValue": {
                        "type": "string",
                        "description": "예상되는 값 (선택사항, 있으면 값 비교 수행)"
                    },
                    "selectorType": {
                        "type": "string",
                        "description": "선택자 타입 (css 또는 xpath, 기본값: css)",
                        "enum": ["css", "xpath"],
                        "default": "css"
                    },
                    "waitTime": {
                        "type": "integer",
                        "description": "페이지 로딩 대기 시간(밀리초, 기본값: 3000)",
                        "default": 3000
                    },
                    "captureScreenshot": {
                        "type": "boolean",
                        "description": "화면 캡처 포함 여부 (기본값: true)",
                        "default": true
                    }
                },
                "required": ["url", "selector"]
            }
        )
    ]

# ============================================
# 헬퍼 함수
# ============================================

async def navigate_and_wait(page: Page, url: str, wait_time: int = 3000):
    """
    페이지를 로드하고 대기합니다.
    
    Args:
        page: Playwright Page 객체
        url: 접속할 URL
        wait_time: 대기 시간(밀리초)
    """
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(wait_time / 1000.0)  # 밀리초를 초로 변환
    except PlaywrightTimeoutError:
        # 타임아웃이 발생해도 계속 진행 (일부 페이지는 완전히 로드되지 않을 수 있음)
        await asyncio.sleep(wait_time / 1000.0)
    except Exception as e:
        raise Exception(f"페이지 로드 실패: {str(e)}")

async def capture_screenshot(page: Page, selector: str | None = None) -> bytes:
    """
    화면을 캡처합니다.
    
    Args:
        page: Playwright Page 객체
        selector: 캡처할 요소의 CSS 선택자 (None이면 전체 페이지)
        
    Returns:
        bytes: PNG 이미지 바이트 데이터
    """
    if selector:
        try:
            element = await page.wait_for_selector(selector, timeout=10000)
            if element:
                return await element.screenshot(type="png")
        except PlaywrightTimeoutError:
            raise Exception(f"요소를 찾을 수 없습니다: {selector}")
    
    return await page.screenshot(type="png", full_page=True)

async def read_element_text(page: Page, selector: str, selector_type: str = "css", attribute: str | None = None) -> str:
    """
    요소의 텍스트 또는 속성 값을 읽습니다.
    
    Args:
        page: Playwright Page 객체
        selector: 선택자
        selector_type: 선택자 타입 (css 또는 xpath)
        attribute: 읽을 속성 이름 (None이면 텍스트 내용)
        
    Returns:
        str: 읽은 값
    """
    try:
        if selector_type == "xpath":
            element = await page.wait_for_selector(f"xpath={selector}", timeout=10000)
        else:
            element = await page.wait_for_selector(selector, timeout=10000)
        
        if not element:
            raise Exception(f"요소를 찾을 수 없습니다: {selector}")
        
        if attribute:
            value = await element.get_attribute(attribute)
            return value or ""
        else:
            return await element.inner_text()
    
    except PlaywrightTimeoutError:
        raise Exception(f"요소를 찾을 수 없습니다: {selector}")
    except Exception as e:
        raise Exception(f"요소 읽기 실패: {str(e)}")

# ============================================
# 도구 실행 핸들러
# ============================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent | ImageContent]:
    """
    도구 실행 핸들러
    
    Args:
        name: 도구 이름
        arguments: 도구 인자
        
    Returns:
        Sequence[TextContent | ImageContent]: 실행 결과
    """
    try:
        if name == "capture_screen":
            url = arguments.get("url", "")
            selector = arguments.get("selector")
            wait_time = arguments.get("waitTime", 3000)
            viewport_width = arguments.get("viewportWidth", 1920)
            viewport_height = arguments.get("viewportHeight", 1080)
            
            if not url:
                return [TextContent(
                    type="text",
                    text="오류: URL이 필요합니다."
                )]
            
            browser = await get_browser()
            context = await browser.new_context(
                viewport={"width": viewport_width, "height": viewport_height}
            )
            page = await context.new_page()
            
            try:
                await navigate_and_wait(page, url, wait_time)
                screenshot_bytes = await capture_screenshot(page, selector)
                
                # Base64로 인코딩하여 반환
                screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                
                result_text = f"화면 캡처 완료\n"
                result_text += f"URL: {url}\n"
                if selector:
                    result_text += f"선택자: {selector}\n"
                result_text += f"이미지 크기: {len(screenshot_bytes)} bytes\n"
                
                return [
                    TextContent(type="text", text=result_text),
                    ImageContent(
                        type="image",
                        data=screenshot_base64,
                        mimeType="image/png"
                    )
                ]
            
            finally:
                await page.close()
                await context.close()
        
        elif name == "read_element_value":
            url = arguments.get("url", "")
            selector = arguments.get("selector", "")
            selector_type = arguments.get("selectorType", "css")
            wait_time = arguments.get("waitTime", 3000)
            attribute = arguments.get("attribute")
            
            if not url:
                return [TextContent(
                    type="text",
                    text="오류: URL이 필요합니다."
                )]
            
            if not selector:
                return [TextContent(
                    type="text",
                    text="오류: 선택자가 필요합니다."
                )]
            
            browser = await get_browser()
            context = await browser.new_context()
            page = await context.new_page()
            
            try:
                await navigate_and_wait(page, url, wait_time)
                value = await read_element_text(page, selector, selector_type, attribute)
                
                result_text = f"요소 값 읽기 완료\n"
                result_text += f"URL: {url}\n"
                result_text += f"선택자: {selector} ({selector_type})\n"
                if attribute:
                    result_text += f"속성: {attribute}\n"
                result_text += f"\n읽은 값:\n{value}\n"
                
                return [TextContent(type="text", text=result_text)]
            
            finally:
                await page.close()
                await context.close()
        
        elif name == "validate_screen_element":
            url = arguments.get("url", "")
            selector = arguments.get("selector", "")
            expected_value = arguments.get("expectedValue")
            selector_type = arguments.get("selectorType", "css")
            wait_time = arguments.get("waitTime", 3000)
            capture_screenshot_flag = arguments.get("captureScreenshot", True)
            
            if not url:
                return [TextContent(
                    type="text",
                    text="오류: URL이 필요합니다."
                )]
            
            if not selector:
                return [TextContent(
                    type="text",
                    text="오류: 선택자가 필요합니다."
                )]
            
            browser = await get_browser()
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            
            try:
                await navigate_and_wait(page, url, wait_time)
                
                # 요소 값 읽기
                actual_value = await read_element_text(page, selector, selector_type)
                
                # 검증 결과
                validation_passed = True
                validation_message = "검증 성공"
                
                if expected_value:
                    if actual_value.strip() == expected_value.strip():
                        validation_passed = True
                        validation_message = f"값 일치: '{actual_value}'"
                    else:
                        validation_passed = False
                        validation_message = f"값 불일치\n예상값: '{expected_value}'\n실제값: '{actual_value}'"
                
                result_contents = []
                
                # 결과 텍스트
                result_text = f"화면 검증 결과\n"
                result_text += f"URL: {url}\n"
                result_text += f"선택자: {selector} ({selector_type})\n"
                result_text += f"읽은 값: {actual_value}\n"
                if expected_value:
                    result_text += f"예상 값: {expected_value}\n"
                result_text += f"\n검증 결과: {'✅ ' if validation_passed else '❌ '}{validation_message}\n"
                
                result_contents.append(TextContent(type="text", text=result_text))
                
                # 화면 캡처 (요청된 경우)
                if capture_screenshot_flag:
                    screenshot_bytes = await capture_screenshot(page, selector)
                    screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
                    result_contents.append(ImageContent(
                        type="image",
                        data=screenshot_base64,
                        mimeType="image/png"
                    ))
                
                return result_contents
            
            finally:
                await page.close()
                await context.close()
        
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
    try:
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    finally:
        # 서버 종료 시 브라우저 정리
        await close_browser()

if __name__ == "__main__":
    print("MCP 화면 검증 서버가 시작되었습니다.", file=sys.stderr)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n서버를 종료합니다.", file=sys.stderr)
        asyncio.run(close_browser())
        sys.exit(0)


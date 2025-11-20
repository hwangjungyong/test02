#!/usr/bin/env python3
"""
HTTP 서버 - AI 화면 검증 (Python 버전)

역할:
- Playwright를 사용하여 웹 페이지 화면 캡처 및 요소 검증
- Vue 앱에서 HTTP 요청으로 화면 검증 기능 사용 가능

실행 방법:
  python mcp-screen-validator-http-server.py

포트: http://localhost:3002
"""

import asyncio
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import base64

# Playwright import
try:
    from playwright.async_api import async_playwright, Browser, Page, TimeoutError as PlaywrightTimeoutError
except ImportError:
    print("Playwright가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install playwright", file=sys.stderr)
    print("playwright install chromium", file=sys.stderr)
    sys.exit(1)

# 프록시 설정
PROXY_URL = 'http://70.10.15.10:8080'

# 브라우저 인스턴스 관리
_browser: Browser | None = None
_playwright_context = None
_browser_lock = None

def get_browser_lock():
    """브라우저 락을 가져오거나 생성합니다."""
    global _browser_lock
    if _browser_lock is None:
        try:
            # 현재 이벤트 루프 확인
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                # 실행 중인 이벤트 루프가 없으면 새로 생성
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            _browser_lock = asyncio.Lock()
        except Exception:
            # 실패 시 새 이벤트 루프 생성
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            _browser_lock = asyncio.Lock()
    return _browser_lock

def run_async_safely(coro, timeout=120.0):
    """안전하게 비동기 함수를 실행합니다."""
    try:
        # 실행 중인 이벤트 루프 확인
        loop = asyncio.get_running_loop()
        # 이미 실행 중인 루프가 있으면 새 스레드에서 실행
        import concurrent.futures
        import threading
        
        def run_in_thread():
            new_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(new_loop)
            try:
                return new_loop.run_until_complete(
                    asyncio.wait_for(coro, timeout=timeout)
                )
            finally:
                new_loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result(timeout=timeout + 10)
    except RuntimeError:
        # 실행 중인 루프가 없으면 직접 실행
        return asyncio.run(asyncio.wait_for(coro, timeout=timeout))

async def get_browser() -> Browser:
    """브라우저 인스턴스를 가져오거나 생성합니다."""
    global _browser, _playwright_context
    
    lock = get_browser_lock()
    async with lock:
        if _browser is None or not _browser.is_connected():
            try:
                # 기존 브라우저가 있으면 정리
                if _browser:
                    try:
                        await _browser.close()
                    except:
                        pass
                if _playwright_context:
                    try:
                        await _playwright_context.stop()
                    except:
                        pass
                
                # 새 브라우저 생성
                _playwright_context = await async_playwright().start()
                _browser = await _playwright_context.chromium.launch(
                    headless=True,
                    args=['--no-sandbox', '--disable-setuid-sandbox']
                )
                
                if _browser is None:
                    raise Exception("브라우저 초기화 실패")
                    
            except Exception as e:
                _browser = None
                _playwright_context = None
                raise Exception(f"브라우저 초기화 오류: {str(e)}")
    
    return _browser

async def navigate_and_wait(page: Page, url: str, wait_time: int = 3000):
    """페이지를 로드하고 대기합니다."""
    try:
        await page.goto(url, wait_until="networkidle", timeout=60000)
        await asyncio.sleep(wait_time / 1000.0)
    except PlaywrightTimeoutError as e:
        error_msg = str(e)
        # 더 자세한 에러 정보 추출
        if "ERR_CONNECTION_TIMED_OUT" in error_msg:
            raise Exception(f"❌ 연결 타임아웃: URL({url})에 접속할 수 없습니다. 네트워크 연결 또는 프록시 설정을 확인해주세요.\n상세: {error_msg}")
        elif "ERR_NAME_NOT_RESOLVED" in error_msg:
            raise Exception(f"❌ DNS 오류: URL({url})의 도메인을 찾을 수 없습니다.\n상세: {error_msg}")
        elif "ERR_CONNECTION_REFUSED" in error_msg:
            raise Exception(f"❌ 연결 거부: URL({url})에 연결이 거부되었습니다.\n상세: {error_msg}")
        else:
            raise Exception(f"❌ 페이지 로드 실패: {error_msg}\nURL: {url}")
    except Exception as e:
        error_msg = str(e)
        raise Exception(f"❌ 페이지 로드 실패: {error_msg}\nURL: {url}")

async def capture_screenshot(page: Page, selector: str | None = None) -> bytes:
    """화면을 캡처합니다."""
    if selector:
        try:
            element = await page.wait_for_selector(selector, timeout=10000, state="visible")
            if element:
                return await element.screenshot(type="png")
        except PlaywrightTimeoutError:
            # 요소를 찾지 못해도 전체 페이지 캡처
            pass
    
    return await page.screenshot(type="png", full_page=True)

async def find_element_by_text(page: Page, text: str) -> str | None:
    """텍스트로 요소를 찾습니다."""
    try:
        # Playwright의 get_by_text 사용
        locator = page.get_by_text(text, exact=False)
        count = await locator.count()
        if count > 0:
            element = locator.first
            return await element.inner_text()
    except Exception as e:
        # 에러 로그 출력 (디버깅용)
        print(f"[디버그] get_by_text 실패: {str(e)}", file=sys.stderr)
        pass
    
    try:
        # XPath로 텍스트 포함 요소 찾기 (대소문자 구분 없음)
        xpath_selector = f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{text.lower()}')]"
        element = await page.wait_for_selector(f"xpath={xpath_selector}", timeout=5000, state="visible")
        if element:
            return await element.inner_text()
    except Exception as e:
        print(f"[디버그] XPath 검색 실패: {str(e)}", file=sys.stderr)
        pass
    
    return None

async def get_suggested_selectors(page: Page) -> str:
    """페이지에서 유용한 선택자를 제안합니다."""
    suggestions = []
    try:
        # 주요 제목 찾기
        h1_elements = await page.query_selector_all("h1")
        if h1_elements:
            for i, h1 in enumerate(h1_elements[:3]):  # 최대 3개
                text = await h1.inner_text()
                id_attr = await h1.get_attribute("id")
                class_attr = await h1.get_attribute("class")
                if id_attr:
                    suggestions.append(f"  - h1#{id_attr} (제목: {text[:30]}...)")
                elif class_attr:
                    suggestions.append(f"  - h1.{class_attr.split()[0]} (제목: {text[:30]}...)")
                else:
                    suggestions.append(f"  - h1 (제목: {text[:30]}...)")
        
        # ID가 있는 요소 찾기
        id_elements = await page.query_selector_all("[id]")
        if id_elements:
            for elem in id_elements[:5]:  # 최대 5개
                id_val = await elem.get_attribute("id")
                tag = await elem.evaluate("el => el.tagName.toLowerCase()")
                text = await elem.inner_text()
                if id_val and text:
                    suggestions.append(f"  - #{id_val} ({tag}, 텍스트: {text[:20]}...)")
    except:
        pass
    
    return "\n".join(suggestions[:8]) if suggestions else "  (페이지 분석 실패)"

async def read_element_text(page: Page, selector: str) -> str:
    """요소의 텍스트 값을 읽습니다."""
    try:
        # CSS 선택자로 먼저 시도
        element = await page.wait_for_selector(selector, timeout=10000, state="visible")
        if element:
            return await element.inner_text()
    except PlaywrightTimeoutError:
        # CSS 선택자가 아닌 것 같으면 텍스트로 찾기 시도
        text_result = await find_element_by_text(page, selector)
        if text_result:
            return text_result
        
        # 여전히 찾지 못하면 페이지에서 제안할 선택자 찾기
        suggested = await get_suggested_selectors(page)
        
        # 여전히 찾지 못하면 에러
        raise Exception(
            f"요소를 찾을 수 없습니다: '{selector}'\n\n"
            f"💡 CSS 선택자 예시:\n"
            f"  - ID: #element-id\n"
            f"  - 클래스: .class-name\n"
            f"  - 태그: h1, p, div\n"
            f"  - 속성: [data-testid='value']\n"
            f"  - 복합: div.container > h1.title\n\n"
            f"📋 이 페이지에서 사용 가능한 선택자:\n{suggested}\n\n"
            f"💻 브라우저 개발자 도구 사용법:\n"
            f"  1. F12 키를 눌러 개발자 도구 열기\n"
            f"  2. 요소 선택 도구(왼쪽 상단 아이콘) 클릭\n"
            f"  3. 원하는 요소 클릭\n"
            f"  4. Elements 탭에서 선택된 요소 우클릭 → Copy → Copy selector"
        )
    except Exception as e:
        error_msg = str(e)
        if "요소를 찾을 수 없습니다" not in error_msg:
            raise Exception(f"요소 읽기 실패: {error_msg}")
        raise

async def interact_and_get_result(
    url: str,
    actions: list[dict],
    result_selector: str | None = None,
    wait_after_actions: int = 2000
) -> dict:
    """
    페이지에서 입력/클릭 등의 액션을 수행하고 결과를 가져옵니다.
    
    Args:
        url: 접속할 URL
        actions: 수행할 액션 목록
            예: [
                {"type": "fill", "selector": "#input", "value": "텍스트"},
                {"type": "click", "selector": "#button"},
                {"type": "select", "selector": "#dropdown", "value": "option1"}
            ]
        result_selector: 결과를 읽을 요소 선택자
        wait_after_actions: 액션 후 대기 시간 (ms)
    """
    playwright_context = None
    browser = None
    context = None
    page = None
    
    try:
        # 브라우저 생성
        playwright_context = await async_playwright().start()
        browser = await playwright_context.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        if browser is None:
            raise Exception("브라우저 인스턴스를 생성할 수 없습니다.")
        
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            proxy={"server": PROXY_URL}
        )
        
        if context is None:
            raise Exception("브라우저 컨텍스트를 생성할 수 없습니다.")
        
        page = await context.new_page()
        
        if page is None:
            raise Exception("페이지를 생성할 수 없습니다.")
        
        # 페이지 로드
        await navigate_and_wait(page, url, 3000)
        
        # 액션 수행
        action_log = []
        for i, action in enumerate(actions):
            action_type = action.get("type", "")
            selector = action.get("selector", "")
            value = action.get("value", "")
            
            try:
                if action_type == "fill":
                    # 텍스트 입력
                    element = await page.wait_for_selector(selector, timeout=10000, state="visible")
                    await element.fill(value)
                    action_log.append(f"✅ {i+1}. 입력 완료: {selector} = '{value}'")
                
                elif action_type == "click":
                    # 버튼/링크 클릭
                    element = await page.wait_for_selector(selector, timeout=10000, state="visible")
                    await element.click()
                    action_log.append(f"✅ {i+1}. 클릭 완료: {selector}")
                
                elif action_type == "select":
                    # 드롭다운 선택
                    element = await page.wait_for_selector(selector, timeout=10000, state="visible")
                    await element.select_option(value)
                    action_log.append(f"✅ {i+1}. 선택 완료: {selector} = '{value}'")
                
                elif action_type == "check":
                    # 체크박스 체크
                    element = await page.wait_for_selector(selector, timeout=10000, state="visible")
                    await element.check()
                    action_log.append(f"✅ {i+1}. 체크 완료: {selector}")
                
                elif action_type == "uncheck":
                    # 체크박스 해제
                    element = await page.wait_for_selector(selector, timeout=10000, state="visible")
                    await element.uncheck()
                    action_log.append(f"✅ {i+1}. 체크 해제 완료: {selector}")
                
                elif action_type == "wait":
                    # 대기
                    wait_time = int(value) if value else 1000
                    await asyncio.sleep(wait_time / 1000.0)
                    action_log.append(f"✅ {i+1}. 대기 완료: {wait_time}ms")
                
                else:
                    action_log.append(f"⚠️ {i+1}. 알 수 없는 액션 타입: {action_type}")
                
                # 액션 간 짧은 대기
                await asyncio.sleep(0.3)
                
            except Exception as e:
                action_log.append(f"❌ {i+1}. 액션 실패 ({action_type}): {str(e)}")
                raise Exception(f"액션 수행 실패: {action_type} - {selector}\n오류: {str(e)}")
        
        # 액션 후 대기
        await asyncio.sleep(wait_after_actions / 1000.0)
        
        # 결과 읽기
        result_value = None
        if result_selector:
            try:
                result_value = await read_element_text(page, result_selector)
            except Exception as e:
                result_value = f"결과 읽기 실패: {str(e)}"
        
        # 화면 캡처
        screenshot_bytes = await capture_screenshot(page, result_selector)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return {
            "success": True,
            "url": url,
            "actions": action_log,
            "resultSelector": result_selector,
            "resultValue": result_value,
            "screenshot": screenshot_base64
        }
    
    finally:
        if page:
            try:
                await page.close()
            except:
                pass
        if context:
            try:
                await context.close()
            except:
                pass
        if browser:
            try:
                await browser.close()
            except:
                pass
        if playwright_context:
            try:
                await playwright_context.stop()
            except:
                pass

async def validate_screen(url: str, selector: str | None, expected_value: str | None) -> dict:
    """화면을 검증합니다."""
    playwright_context = None
    browser = None
    context = None
    page = None
    
    try:
        # 각 요청마다 새로운 브라우저 인스턴스 생성 (안정성을 위해)
        playwright_context = await async_playwright().start()
        browser = await playwright_context.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        if browser is None:
            raise Exception("브라우저 인스턴스를 생성할 수 없습니다.")
        
        # 프록시 설정을 포함한 브라우저 컨텍스트 생성
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            proxy={"server": PROXY_URL}
        )
        
        if context is None:
            raise Exception("브라우저 컨텍스트를 생성할 수 없습니다.")
        
        page = await context.new_page()
        
        if page is None:
            raise Exception("페이지를 생성할 수 없습니다.")
        
        await navigate_and_wait(page, url, 3000)
        
        actual_value = None
        selector_error = None
        
        # 선택자가 있으면 요소 읽기 시도
        if selector:
            try:
                actual_value = await read_element_text(page, selector)
            except Exception as e:
                # 요소를 찾지 못해도 화면은 캡처하고 에러 메시지 포함
                selector_error = str(e)
                actual_value = None
        
        passed = True
        message = "검증 성공"
        
        # 선택자 에러가 있으면 실패로 처리
        if selector_error:
            passed = False
            # 간단한 메시지만 표시 (상세 정보는 selectorError에)
            message = "요소를 찾을 수 없습니다"
        elif expected_value and actual_value:
            if actual_value.strip() == expected_value.strip():
                passed = True
                message = f"✅ 값 일치: '{actual_value}'"
            else:
                passed = False
                message = f"❌ 값 불일치\n예상값: '{expected_value}'\n실제값: '{actual_value}'"
        elif expected_value and not actual_value:
            passed = False
            message = f"❌ 요소를 찾을 수 없어 값을 비교할 수 없습니다."
        elif actual_value:
            message = f"✅ 요소 값 읽기 성공: '{actual_value}'"
        
        # 화면 캡처 (선택자가 없거나 에러가 있어도 캡처)
        screenshot_bytes = await capture_screenshot(page, selector if not selector_error else None)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return {
            "success": True,
            "url": url,
            "selector": selector or "전체 페이지",
            "actualValue": actual_value,
            "expectedValue": expected_value,
            "passed": passed,
            "message": message,
            "screenshot": screenshot_base64,
            "selectorError": selector_error
        }
    
    finally:
        if page:
            try:
                await page.close()
            except:
                pass
        if context:
            try:
                await context.close()
            except:
                pass
        if browser:
            try:
                await browser.close()
            except:
                pass
        if playwright_context:
            try:
                await playwright_context.stop()
            except:
                pass

async def capture_screen_only(url: str, selector: str | None) -> dict:
    """화면만 캡처합니다."""
    playwright_context = None
    browser = None
    context = None
    page = None
    
    try:
        # 각 요청마다 새로운 브라우저 인스턴스 생성 (안정성을 위해)
        playwright_context = await async_playwright().start()
        browser = await playwright_context.chromium.launch(
            headless=True,
            args=['--no-sandbox', '--disable-setuid-sandbox']
        )
        
        if browser is None:
            raise Exception("브라우저 인스턴스를 생성할 수 없습니다.")
        
        # 프록시 설정을 포함한 브라우저 컨텍스트 생성
        context = await browser.new_context(
            viewport={"width": 1920, "height": 1080},
            proxy={"server": PROXY_URL}
        )
        
        if context is None:
            raise Exception("브라우저 컨텍스트를 생성할 수 없습니다.")
        
        page = await context.new_page()
        
        if page is None:
            raise Exception("페이지를 생성할 수 없습니다.")
        
        await navigate_and_wait(page, url, 3000)
        screenshot_bytes = await capture_screenshot(page, selector)
        screenshot_base64 = base64.b64encode(screenshot_bytes).decode('utf-8')
        
        return {
            "success": True,
            "url": url,
            "selector": selector or "전체 페이지",
            "screenshot": screenshot_base64
        }
    
    finally:
        if page:
            try:
                await page.close()
            except:
                pass
        if context:
            try:
                await context.close()
            except:
                pass
        if browser:
            try:
                await browser.close()
            except:
                pass
        if playwright_context:
            try:
                await playwright_context.stop()
            except:
                pass

# HTTP 요청 핸들러
class ScreenValidationHandler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """CORS preflight 요청 처리"""
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()
    
    def do_GET(self):
        """GET 요청 처리 (헬스체크 등)"""
        if self.path == '/health' or self.path == '/':
            response = json.dumps({
                "status": "ok",
                "service": "screen-validator-http-server",
                "port": 3002
            }, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))
        else:
            self.send_response(404)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Not Found"}).encode('utf-8'))
    
    def do_POST(self):
        """POST 요청 처리"""
        response_sent = False
        try:
            # 요청 본문 읽기
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                raise ValueError("Content-Length가 0입니다.")
            
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            url = data.get('url', '')
            selector = data.get('selector')
            expected_value = data.get('expectedValue')
            
            if not url:
                response = json.dumps({
                    "success": False,
                    "error": "URL이 필요합니다."
                }, ensure_ascii=False)
                response_sent = True
            else:
                # 경로에 따라 처리 (타임아웃 설정)
                try:
                    if self.path == '/api/screen/validate':
                        print(f"[화면 검증 서버] 검증 요청: {url}", file=sys.stderr)
                        try:
                            result = run_async_safely(
                                validate_screen(url, selector, expected_value),
                                timeout=120.0
                            )
                            response = json.dumps(result, ensure_ascii=False)
                        except Exception as func_error:
                            error_msg = f"화면 검증 중 오류 발생: {str(func_error)}"
                            print(f"[화면 검증 서버] 함수 실행 오류: {error_msg}", file=sys.stderr)
                            import traceback
                            print(f"[화면 검증 서버] 상세:\n{traceback.format_exc()}", file=sys.stderr)
                            response = json.dumps({
                                "success": False,
                                "error": error_msg,
                                "errorType": type(func_error).__name__
                            }, ensure_ascii=False)
                    
                    elif self.path == '/api/screen/capture':
                        print(f"[화면 검증 서버] 캡처 요청: {url}", file=sys.stderr)
                        try:
                            result = run_async_safely(
                                capture_screen_only(url, selector),
                                timeout=120.0
                            )
                            response = json.dumps(result, ensure_ascii=False)
                        except Exception as func_error:
                            error_msg = f"화면 캡처 중 오류 발생: {str(func_error)}"
                            print(f"[화면 검증 서버] 함수 실행 오류: {error_msg}", file=sys.stderr)
                            import traceback
                            print(f"[화면 검증 서버] 상세:\n{traceback.format_exc()}", file=sys.stderr)
                            response = json.dumps({
                                "success": False,
                                "error": error_msg,
                                "errorType": type(func_error).__name__
                            }, ensure_ascii=False)
                    
                    elif self.path == '/api/screen/interact':
                        actions = data.get('actions', [])
                        result_selector = data.get('resultSelector')
                        wait_after_actions = data.get('waitAfterActions', 2000)
                        print(f"[화면 검증 서버] 상호작용 요청: {url}", file=sys.stderr)
                        try:
                            result = run_async_safely(
                                interact_and_get_result(url, actions, result_selector, wait_after_actions),
                                timeout=120.0
                            )
                            response = json.dumps(result, ensure_ascii=False)
                        except Exception as func_error:
                            error_msg = f"상호작용 중 오류 발생: {str(func_error)}"
                            print(f"[화면 검증 서버] 함수 실행 오류: {error_msg}", file=sys.stderr)
                            import traceback
                            print(f"[화면 검증 서버] 상세:\n{traceback.format_exc()}", file=sys.stderr)
                            response = json.dumps({
                                "success": False,
                                "error": error_msg,
                                "errorType": type(func_error).__name__
                            }, ensure_ascii=False)
                    
                    else:
                        response = json.dumps({
                            "success": False,
                            "error": f"알 수 없는 경로: {self.path}"
                        }, ensure_ascii=False)
                    
                    response_sent = True
                    
                except asyncio.TimeoutError:
                    error_msg = "요청 처리 시간이 초과되었습니다. (120초)"
                    print(f"[화면 검증 서버] 타임아웃: {error_msg}", file=sys.stderr)
                    response = json.dumps({
                        "success": False,
                        "error": error_msg,
                        "errorType": "TimeoutError"
                    }, ensure_ascii=False)
                    response_sent = True
                except Exception as inner_error:
                    error_msg = f"요청 처리 중 예상치 못한 오류: {str(inner_error)}"
                    print(f"[화면 검증 서버] 내부 오류: {error_msg}", file=sys.stderr)
                    import traceback
                    print(f"[화면 검증 서버] 상세:\n{traceback.format_exc()}", file=sys.stderr)
                    response = json.dumps({
                        "success": False,
                        "error": error_msg,
                        "errorType": type(inner_error).__name__
                    }, ensure_ascii=False)
                    response_sent = True
            
            # CORS 헤더 설정 및 응답 전송
            if not response_sent:
                response = json.dumps({
                    "success": False,
                    "error": "응답을 생성하지 못했습니다."
                }, ensure_ascii=False)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type')
            self.end_headers()
            
            self.wfile.write(response.encode('utf-8'))
            self.wfile.flush()
            print(f"[화면 검증 서버] 응답 전송 완료: {self.path}", file=sys.stderr)
        
        except json.JSONDecodeError as e:
            error_msg = f"JSON 파싱 오류: {str(e)}"
            print(f"[화면 검증 서버] {error_msg}", file=sys.stderr)
            error_response = json.dumps({
                "success": False,
                "error": error_msg,
                "errorType": "JSONDecodeError"
            }, ensure_ascii=False)
            
            self.send_response(400)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(error_response.encode('utf-8'))
            self.wfile.flush()
        
        except Exception as e:
            error_msg = str(e)
            error_type = type(e).__name__
            
            # 에러 로그를 콘솔에도 출력 (상세 정보 포함)
            import traceback
            error_traceback = traceback.format_exc()
            print(f"[화면 검증 서버] 오류 발생 ({error_type}):", file=sys.stderr)
            print(f"[화면 검증 서버] {error_msg}", file=sys.stderr)
            print(f"[화면 검증 서버] 상세:\n{error_traceback}", file=sys.stderr)
            
            error_response = json.dumps({
                "success": False,
                "error": error_msg,
                "errorType": error_type
            }, ensure_ascii=False)
            
            try:
                self.send_response(500)
                self.send_header('Content-Type', 'application/json; charset=utf-8')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(error_response.encode('utf-8'))
                self.wfile.flush()
            except Exception as send_error:
                print(f"[화면 검증 서버] 응답 전송 실패: {send_error}", file=sys.stderr)

def run_server(port=3002):
    """HTTP 서버 실행"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ScreenValidationHandler)
    print(f'화면 검증 HTTP 서버가 http://localhost:{port} 에서 실행 중입니다.', file=sys.stderr)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('\n서버를 종료합니다.', file=sys.stderr)
        asyncio.run(close_browser())
        sys.exit(0)

async def close_browser():
    """브라우저 인스턴스를 종료합니다."""
    global _browser, _playwright_context
    
    if _browser:
        await _browser.close()
        _browser = None
    
    if _playwright_context:
        await _playwright_context.stop()
        _playwright_context = None

if __name__ == '__main__':
    port = 3002
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)

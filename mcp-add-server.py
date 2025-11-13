#!/usr/bin/env python3
"""
MCP 서버 - 간단한 덧셈 계산기

역할:
- MCP 프로토콜을 통해 AI 클라이언트와 통신하는 서버
- 두 수를 입력받아 더한 결과를 반환하는 간단한 계산기

실행 방법:
  python mcp-add-server.py

참고:
- Python MCP SDK를 사용하여 구현
- StdioServerTransport를 사용하여 표준 입출력(stdin/stdout)으로 통신합니다
"""

import asyncio
import sys
from typing import Any

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
# MCP 서버 생성
# ============================================

server = Server("add-calculator-server")

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
            name="add_numbers",
            description="두 개의 숫자를 입력받아 더한 결과를 반환합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {
                        "type": "number",
                        "description": "첫 번째 숫자"
                    },
                    "b": {
                        "type": "number",
                        "description": "두 번째 숫자"
                    }
                },
                "required": ["a", "b"]
            }
        )
    ]

# ============================================
# 도구 실행 핸들러
# ============================================

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> list[TextContent]:
    """
    도구를 실행하는 핸들러입니다.
    
    매개변수:
        name: 도구 이름
        arguments: 도구에 전달할 인수
    
    반환값:
        list[TextContent]: 도구 실행 결과
    """
    if name == "add_numbers":
        # 인수에서 두 숫자 추출
        a = arguments.get("a")
        b = arguments.get("b")
        
        # 숫자 유효성 검사
        if a is None or b is None:
            return [
                TextContent(
                    type="text",
                    text="오류: 두 숫자 모두 제공되어야 합니다."
                )
            ]
        
        try:
            # 덧셈 수행
            result = float(a) + float(b)
            
            # 결과 반환
            return [
                TextContent(
                    type="text",
                    text=f"{a} + {b} = {result}"
                )
            ]
        except (ValueError, TypeError) as e:
            return [
                TextContent(
                    type="text",
                    text=f"오류: 유효한 숫자를 입력해주세요. ({str(e)})"
                )
            ]
    else:
        return [
            TextContent(
                type="text",
                text=f"알 수 없는 도구: {name}"
            )
        ]

# ============================================
# 서버 실행
# ============================================

async def main():
    """
    서버를 시작하고 실행합니다.
    """
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    print("MCP 덧셈 계산기 서버가 시작되었습니다.", file=sys.stderr)
    asyncio.run(main())


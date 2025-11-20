#!/usr/bin/env python3
"""
에러 로그 분석 MCP 서버

역할:
- 워크스페이스에서 에러 로그 파일을 자동으로 찾아 분석
- GCP 에러 로그 및 일반 로그 형태를 자동 감지하여 파싱
- 에러 정보를 테이블 형태로 출력
- 에러 분석, 조치 방법, 재발 방지책 제안

실행 방법:
  python mcp-error-log-analyzer.py

의존성 설치:
  pip install mcp

참고:
- Python MCP SDK를 사용하여 구현
- StdioServerTransport를 사용하여 표준 입출력(stdin/stdout)으로 통신합니다
"""

import asyncio
import json
import sys
import os
import re
from typing import Any, Sequence, List, Dict, Optional
from datetime import datetime
from pathlib import Path

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
# 로그 파서 클래스
# ============================================

class LogParser:
    """다양한 형태의 로그 파일을 파싱하는 클래스"""
    
    # GCP 로그 패턴
    GCP_PATTERNS = {
        'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d\.]*Z?)',
        'severity': r'(ERROR|WARNING|CRITICAL|INFO|DEBUG)',
        'resource': r'resource\.type="([^"]+)"',
        'location': r'location="([^"]+)"',
        'service': r'serviceName="([^"]+)"',
        'message': r'textPayload="([^"]+)"|jsonPayload\.message="([^"]+)"'
    }
    
    # 일반 로그 패턴들
    COMMON_PATTERNS = [
        {
            'name': 'ISO8601',
            'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d\.]*[Z\+\-:]*\d*)',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL|INFO|DEBUG)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:(.+?)(?:\n|$)'
        },
        {
            'name': 'Standard',
            'timestamp': r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL|INFO|DEBUG)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:(.+?)(?:\n|$)'
        },
        {
            'name': 'Simple',
            'timestamp': r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:(.+?)(?:\n|$)'
        }
    ]
    
    def __init__(self, log_content: str):
        self.log_content = log_content
        self.log_type = self._detect_log_type()
    
    def _detect_log_type(self) -> str:
        """로그 타입을 자동 감지"""
        # GCP 로그 감지
        if 'resource.type' in self.log_content or 'serviceName' in self.log_content:
            return 'gcp'
        
        # 일반 로그 패턴 확인
        for pattern in self.COMMON_PATTERNS:
            if re.search(pattern['timestamp'], self.log_content):
                return pattern['name'].lower()
        
        return 'unknown'
    
    def parse_errors(self) -> List[Dict[str, Any]]:
        """에러 로그를 파싱하여 구조화된 데이터로 반환"""
        errors = []
        
        if self.log_type == 'gcp':
            errors = self._parse_gcp_logs()
        else:
            errors = self._parse_common_logs()
        
        return errors
    
    def _parse_gcp_logs(self) -> List[Dict[str, Any]]:
        """GCP 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        current_error = {}
        for line in lines:
            # 타임스탬프 추출
            timestamp_match = re.search(self.GCP_PATTERNS['timestamp'], line)
            if timestamp_match:
                current_error['timestamp'] = timestamp_match.group(1)
            
            # 심각도 추출
            severity_match = re.search(self.GCP_PATTERNS['severity'], line)
            if severity_match and severity_match.group(1) in ['ERROR', 'CRITICAL']:
                current_error['severity'] = severity_match.group(1)
            
            # 리소스 타입 추출
            resource_match = re.search(self.GCP_PATTERNS['resource'], line)
            if resource_match:
                current_error['resource_type'] = resource_match.group(1)
            
            # 위치 추출
            location_match = re.search(self.GCP_PATTERNS['location'], line)
            if location_match:
                current_error['location'] = location_match.group(1)
            
            # 서비스 이름 추출
            service_match = re.search(self.GCP_PATTERNS['service'], line)
            if service_match:
                current_error['service'] = service_match.group(1)
            
            # 메시지 추출
            message_match = re.search(self.GCP_PATTERNS['message'], line)
            if message_match:
                current_error['message'] = message_match.group(1) or message_match.group(2)
            
            # 에러 정보가 완성되면 추가
            if 'message' in current_error and ('severity' in current_error or 'ERROR' in line or 'CRITICAL' in line):
                if not current_error.get('timestamp'):
                    current_error['timestamp'] = datetime.now().isoformat()
                errors.append(current_error.copy())
                current_error = {}
        
        return errors
    
    def _parse_common_logs(self) -> List[Dict[str, Any]]:
        """일반 로그 파싱"""
        errors = []
        
        # 각 패턴으로 시도
        for pattern in self.COMMON_PATTERNS:
            matches = re.finditer(
                rf"{pattern['timestamp']}.*?{pattern['level']}.*?:(.+?)(?=\n{pattern['timestamp']}|\Z)",
                self.log_content,
                re.MULTILINE | re.DOTALL
            )
            
            for match in matches:
                if match.group(2) in ['ERROR', 'WARN', 'WARNING', 'CRITICAL', 'FATAL']:
                    error = {
                        'timestamp': match.group(1),
                        'severity': match.group(2),
                        'message': match.group(3).strip() if len(match.groups()) > 2 else match.group(0)
                    }
                    
                    # 파일 경로 추출 시도
                    file_match = re.search(r'([/\w\\]+\.(py|js|ts|java|cpp|c|go|rs))', error['message'])
                    if file_match:
                        error['file'] = file_match.group(1)
                    
                    # 라인 번호 추출 시도
                    line_match = re.search(r'line\s+(\d+)', error['message'], re.IGNORECASE)
                    if line_match:
                        error['line'] = line_match.group(1)
                    
                    errors.append(error)
            
            if errors:
                break
        
        # 패턴 매칭 실패 시 간단한 에러 라인 추출
        if not errors:
            error_lines = re.findall(r'.*?(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*', self.log_content, re.IGNORECASE)
            for i, line in enumerate(error_lines[:50]):  # 최대 50개
                errors.append({
                    'timestamp': datetime.now().isoformat(),
                    'severity': 'ERROR',
                    'message': line.strip()
                })
        
        return errors

# ============================================
# 에러 분석기 클래스
# ============================================

class ErrorAnalyzer:
    """에러를 분석하고 조치 방법을 제안하는 클래스"""
    
    ERROR_PATTERNS = {
        'database': {
            'keywords': ['database', 'connection', 'sql', 'query', 'db', 'postgresql', 'mysql', 'mongodb'],
            'solutions': [
                '데이터베이스 연결 상태를 확인하세요.',
                '데이터베이스 서버가 실행 중인지 확인하세요.',
                '연결 문자열과 인증 정보를 확인하세요.',
                '데이터베이스 로그를 확인하여 추가 정보를 얻으세요.'
            ],
            'prevention': [
                '연결 풀링을 구현하여 연결 관리를 최적화하세요.',
                '데이터베이스 연결에 재시도 로직을 추가하세요.',
                '연결 타임아웃을 적절히 설정하세요.',
                '정기적으로 데이터베이스 상태를 모니터링하세요.'
            ]
        },
        'network': {
            'keywords': ['network', 'connection', 'timeout', 'refused', 'socket', 'http', 'https'],
            'solutions': [
                '네트워크 연결 상태를 확인하세요.',
                '방화벽 설정을 확인하세요.',
                '서버가 실행 중인지 확인하세요.',
                '타임아웃 설정을 확인하고 필요시 증가시키세요.',
                'DNS 설정을 확인하세요.'
            ],
            'prevention': [
                '네트워크 요청에 재시도 로직을 구현하세요.',
                '서킷 브레이커 패턴을 적용하세요.',
                '네트워크 상태를 모니터링하는 헬스체크를 구현하세요.',
                '타임아웃 값을 환경 변수로 관리하여 쉽게 조정할 수 있게 하세요.'
            ]
        },
        'authentication': {
            'keywords': ['auth', 'unauthorized', 'forbidden', 'token', 'credential', 'permission'],
            'solutions': [
                '인증 토큰이 유효한지 확인하세요.',
                '사용자 권한을 확인하세요.',
                '인증 서버가 정상 작동하는지 확인하세요.',
                '토큰 만료 시간을 확인하세요.'
            ],
            'prevention': [
                '토큰 갱신 로직을 구현하세요.',
                '인증 실패 시 적절한 에러 메시지를 제공하세요.',
                '인증 로그를 기록하여 보안 이슈를 추적하세요.',
                '정기적으로 인증 시스템을 점검하세요.'
            ]
        },
        'memory': {
            'keywords': ['memory', 'out of memory', 'oom', 'heap', 'stack overflow'],
            'solutions': [
                '메모리 사용량을 확인하세요.',
                '메모리 누수를 확인하세요.',
                '애플리케이션의 메모리 제한을 증가시키세요.',
                '불필요한 객체 참조를 제거하세요.'
            ],
            'prevention': [
                '메모리 프로파일링을 정기적으로 수행하세요.',
                '대용량 데이터 처리는 스트리밍 방식으로 변경하세요.',
                '캐시 크기를 제한하고 LRU 같은 정책을 사용하세요.',
                '메모리 사용량을 모니터링하는 알림을 설정하세요.'
            ]
        },
        'file': {
            'keywords': ['file', 'not found', 'permission denied', 'eacces', 'enoent'],
            'solutions': [
                '파일 경로가 올바른지 확인하세요.',
                '파일 접근 권한을 확인하세요.',
                '디렉토리가 존재하는지 확인하세요.',
                '디스크 공간이 충분한지 확인하세요.'
            ],
            'prevention': [
                '파일 경로를 환경 변수로 관리하세요.',
                '파일 접근 전에 존재 여부를 확인하는 로직을 추가하세요.',
                '파일 권한을 적절히 설정하세요.',
                '디스크 공간을 모니터링하세요.'
            ]
        },
        'syntax': {
            'keywords': ['syntax', 'parse', 'invalid', 'unexpected', 'token'],
            'solutions': [
                '코드 문법 오류를 확인하세요.',
                'IDE나 린터를 사용하여 문법 오류를 찾으세요.',
                '최근 변경된 코드를 검토하세요.'
            ],
            'prevention': [
                '코드 포맷터와 린터를 사용하세요.',
                'CI/CD 파이프라인에 문법 검사를 추가하세요.',
                '코드 리뷰를 통해 문법 오류를 사전에 발견하세요.'
            ]
        }
    }
    
    def analyze_error(self, error_message: str) -> Dict[str, Any]:
        """에러 메시지를 분석하여 조치 방법과 재발 방지책을 제안"""
        error_lower = error_message.lower()
        
        # 에러 타입 분류
        error_type = 'unknown'
        matched_keywords = []
        
        for err_type, pattern_info in self.ERROR_PATTERNS.items():
            for keyword in pattern_info['keywords']:
                if keyword in error_lower:
                    error_type = err_type
                    matched_keywords.append(keyword)
                    break
        
        # 조치 방법 및 재발 방지책 가져오기
        if error_type != 'unknown':
            solutions = self.ERROR_PATTERNS[error_type]['solutions']
            prevention = self.ERROR_PATTERNS[error_type]['prevention']
        else:
            solutions = [
                '에러 메시지를 자세히 검토하세요.',
                '관련 로그를 더 확인하세요.',
                '최근 변경 사항을 검토하세요.',
                '공식 문서나 커뮤니티에서 유사한 문제를 찾아보세요.'
            ]
            prevention = [
                '에러 로깅을 강화하여 더 많은 컨텍스트를 기록하세요.',
                '정기적으로 로그를 검토하세요.',
                '모니터링 시스템을 구축하세요.'
            ]
        
        return {
            'error_type': error_type,
            'matched_keywords': matched_keywords,
            'solutions': solutions,
            'prevention': prevention
        }

# ============================================
# MCP 서버 생성
# ============================================

server = Server("error-log-analyzer")

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
            name="analyze_error_logs",
            description="워크스페이스에서 에러 로그 파일을 찾아 분석합니다. GCP 에러 로그 및 일반 로그 형태를 자동으로 감지하여 파싱하고, 에러 정보를 테이블 형태로 출력하며, 조치 방법과 재발 방지책을 제안합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "log_file_path": {
                        "type": "string",
                        "description": "분석할 로그 파일 경로 (선택사항, 제공하지 않으면 워크스페이스에서 자동으로 찾습니다)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "워크스페이스 경로 (선택사항, 기본값: 현재 작업 디렉토리)"
                    }
                }
            }
        )
    ]

# ============================================
# 헬퍼 함수
# ============================================

def find_log_files(workspace_path: str) -> List[str]:
    """워크스페이스에서 로그 파일을 찾습니다"""
    log_files = []
    workspace = Path(workspace_path)
    
    # 일반적인 로그 파일 확장자 및 이름 패턴
    log_patterns = [
        '*.log',
        '*.err',
        '*.error',
        '*error*.log',
        '*error*.txt',
        'error.log',
        'errors.log',
        'app.log',
        'server.log',
        'application.log'
    ]
    
    # 로그 디렉토리들
    log_dirs = ['logs', 'log', 'var/log', 'tmp']
    
    # 로그 디렉토리에서 찾기
    for log_dir in log_dirs:
        log_path = workspace / log_dir
        if log_path.exists() and log_path.is_dir():
            for pattern in log_patterns:
                log_files.extend(list(log_path.glob(pattern)))
    
    # 루트 디렉토리에서 찾기
    for pattern in log_patterns:
        log_files.extend(list(workspace.glob(pattern)))
    
    # 중복 제거 및 문자열 변환
    return list(set(str(f) for f in log_files if f.is_file()))

def format_error_table(errors: List[Dict[str, Any]]) -> str:
    """에러 목록을 테이블 형태로 포맷팅"""
    if not errors:
        return "에러를 찾을 수 없습니다."
    
    table = []
    table.append("=" * 120)
    table.append(f"{'번호':<5} {'발생일시':<25} {'에러사항':<40} {'발생위치':<20} {'관련프로그램':<20}")
    table.append("=" * 120)
    
    for i, error in enumerate(errors, 1):
        timestamp = error.get('timestamp', 'N/A')[:25]
        message = (error.get('message', 'N/A')[:38] + '..') if len(error.get('message', '')) > 40 else error.get('message', 'N/A')
        location = error.get('location', error.get('file', 'N/A'))[:18]
        program = error.get('service', error.get('resource_type', error.get('severity', 'N/A')))[:18]
        
        table.append(f"{i:<5} {timestamp:<25} {message:<40} {location:<20} {program:<20}")
    
    table.append("=" * 120)
    return "\n".join(table)

def format_analysis_table(analysis_results: List[Dict[str, Any]]) -> str:
    """에러 분석 결과를 테이블 형태로 포맷팅"""
    if not analysis_results:
        return "분석 결과가 없습니다."
    
    table = []
    table.append("=" * 120)
    table.append(f"{'번호':<5} {'에러타입':<15} {'에러내용':<50} {'매칭키워드':<30}")
    table.append("=" * 120)
    
    for i, result in enumerate(analysis_results, 1):
        error_type = result.get('error_type', 'unknown')[:13]
        error_content = (result.get('error_message', 'N/A')[:48] + '..') if len(result.get('error_message', '')) > 50 else result.get('error_message', 'N/A')
        keywords = ', '.join(result.get('matched_keywords', [])[:3])[:28]
        
        table.append(f"{i:<5} {error_type:<15} {error_content:<50} {keywords:<30}")
    
    table.append("=" * 120)
    return "\n".join(table)

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
        if name == "analyze_error_logs":
            log_file_path = arguments.get("log_file_path")
            workspace_path = arguments.get("workspace_path", os.getcwd())
            
            # 로그 파일 찾기
            if log_file_path:
                if not os.path.exists(log_file_path):
                    return [TextContent(
                        type="text",
                        text=f"오류: 로그 파일을 찾을 수 없습니다: {log_file_path}"
                    )]
                log_files = [log_file_path]
            else:
                log_files = find_log_files(workspace_path)
                if not log_files:
                    return [TextContent(
                        type="text",
                        text=f"워크스페이스({workspace_path})에서 로그 파일을 찾을 수 없습니다.\n\n"
                             f"로그 파일 경로를 직접 지정하거나, 다음 위치에 로그 파일이 있는지 확인하세요:\n"
                             f"- logs/ 디렉토리\n"
                             f"- log/ 디렉토리\n"
                             f"- *.log 파일"
                    )]
            
            result_parts = []
            
            # 각 로그 파일 분석
            for log_file in log_files[:5]:  # 최대 5개 파일만 분석
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                    
                    if not log_content.strip():
                        continue
                    
                    # 로그 파싱
                    parser = LogParser(log_content)
                    errors = parser.parse_errors()
                    
                    if not errors:
                        continue
                    
                    result_parts.append(f"\n{'='*120}")
                    result_parts.append(f"📁 로그 파일: {log_file}")
                    result_parts.append(f"📊 로그 타입: {parser.log_type.upper()}")
                    result_parts.append(f"{'='*120}\n")
                    
                    # 1. 에러 목록 테이블
                    result_parts.append("## 1. 에러 로그 요약 (테이블)")
                    result_parts.append(format_error_table(errors))
                    result_parts.append("")
                    
                    # 2. 에러 분석
                    analyzer = ErrorAnalyzer()
                    analysis_results = []
                    
                    for error in errors:
                        error_msg = error.get('message', '')
                        analysis = analyzer.analyze_error(error_msg)
                        analysis['error_message'] = error_msg
                        analysis_results.append(analysis)
                    
                    result_parts.append("\n## 2. 에러 분석 (테이블)")
                    result_parts.append(format_analysis_table(analysis_results))
                    result_parts.append("")
                    
                    # 3. 상세 에러 내역
                    result_parts.append("\n## 3. 상세 에러 내역")
                    for i, error in enumerate(errors, 1):
                        result_parts.append(f"\n### 에러 #{i}")
                        result_parts.append(f"- **발생일시**: {error.get('timestamp', 'N/A')}")
                        result_parts.append(f"- **심각도**: {error.get('severity', 'N/A')}")
                        result_parts.append(f"- **에러사항**: {error.get('message', 'N/A')}")
                        result_parts.append(f"- **발생위치**: {error.get('location', error.get('file', 'N/A'))}")
                        result_parts.append(f"- **관련프로그램**: {error.get('service', error.get('resource_type', 'N/A'))}")
                        if error.get('line'):
                            result_parts.append(f"- **라인번호**: {error.get('line')}")
                    
                    # 4. 조치 방법
                    result_parts.append("\n## 4. 조치 방법")
                    unique_analyses = {}
                    for analysis in analysis_results:
                        error_type = analysis['error_type']
                        if error_type not in unique_analyses:
                            unique_analyses[error_type] = analysis
                    
                    for error_type, analysis in unique_analyses.items():
                        result_parts.append(f"\n### {error_type.upper()} 타입 에러 조치 방법:")
                        for j, solution in enumerate(analysis['solutions'], 1):
                            result_parts.append(f"{j}. {solution}")
                    
                    # 5. 재발 방지책
                    result_parts.append("\n## 5. 재발 방지책")
                    for error_type, analysis in unique_analyses.items():
                        result_parts.append(f"\n### {error_type.upper()} 타입 에러 재발 방지책:")
                        for j, prevention in enumerate(analysis['prevention'], 1):
                            result_parts.append(f"{j}. {prevention}")
                    
                except Exception as e:
                    result_parts.append(f"\n⚠️ 로그 파일 분석 중 오류 발생 ({log_file}): {str(e)}")
                    continue
            
            if not result_parts:
                return [TextContent(
                    type="text",
                    text="분석할 에러 로그를 찾을 수 없습니다."
                )]
            
            return [TextContent(
                type="text",
                text="\n".join(result_parts)
            )]
        
        else:
            return [TextContent(
                type="text",
                text=f"알 수 없는 도구: {name}"
            )]
    
    except Exception as e:
        return [TextContent(
            type="text",
            text=f"오류 발생: {str(e)}\n\n상세 정보:\n{type(e).__name__}"
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
    print("에러 로그 분석 MCP 서버가 시작되었습니다.", file=sys.stderr)
    print("사용 가능한 도구: analyze_error_logs", file=sys.stderr)
    asyncio.run(main())


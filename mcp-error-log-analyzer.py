#!/usr/bin/env python3
# -*- coding: utf-8 -*-
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
import argparse
from typing import Any, Sequence, List, Dict, Optional
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Windows 콘솔 인코딩 설정 (UTF-8)
if sys.platform == 'win32':
    import io
    # stdout과 stderr을 UTF-8로 설정
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        # Python 3.6 이하 버전을 위한 대체 방법
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
        # JSON 형식 GCP 로그 감지
        if self.log_content.strip().startswith('{') and ('"resource"' in self.log_content or '"logName"' in self.log_content):
            return 'gcp_json'
        
        # 텍스트 형식 GCP 로그 감지
        if 'resource.type' in self.log_content or 'serviceName' in self.log_content:
            return 'gcp_text'
        
        # AWS CloudWatch 로그 감지
        if '"aws"' in self.log_content.lower() or '"cloudwatch"' in self.log_content.lower() or '"logGroup"' in self.log_content:
            return 'aws'
        
        # Azure Monitor 로그 감지
        if '"azure"' in self.log_content.lower() or '"resourceId"' in self.log_content or ('"time"' in self.log_content and '"category"' in self.log_content):
            return 'azure'
        
        # 일반 로그 패턴 확인
        for pattern in self.COMMON_PATTERNS:
            if re.search(pattern['timestamp'], self.log_content):
                return pattern['name'].lower()
        
        return 'application'
    
    def parse_errors(self) -> List[Dict[str, Any]]:
        """에러 로그를 파싱하여 구조화된 메타데이터를 포함한 데이터로 반환"""
        errors = []
        
        if self.log_type == 'gcp_json':
            errors = self._parse_gcp_json_logs()
        elif self.log_type == 'gcp_text':
            errors = self._parse_gcp_text_logs()
        elif self.log_type == 'aws':
            errors = self._parse_aws_logs()
        elif self.log_type == 'azure':
            errors = self._parse_azure_logs()
        else:
            errors = self._parse_common_logs()
        
        # 각 에러에 메타데이터 구조 추가
        for error in errors:
            error['metadata'] = self._extract_metadata(error)
        
        return errors
    
    def _extract_metadata(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """에러 정보에서 메타데이터 추출"""
        metadata = {
            'system_type': self.log_type,
            'timestamp': error.get('timestamp', datetime.now().isoformat()),
            'severity': error.get('severity', 'ERROR'),
            'resource': {},
            'service': {},
            'location': {},
            'error': {},
            'metadata': {}
        }
        
        # 리소스 정보
        if error.get('resource_type'):
            metadata['resource']['type'] = error['resource_type']
        if error.get('resource_name'):
            metadata['resource']['name'] = error['resource_name']
        if error.get('region') or error.get('location'):
            metadata['resource']['region'] = error.get('region') or error.get('location')
        
        # 서비스 정보
        if error.get('service'):
            metadata['service']['name'] = error['service']
        if error.get('service_version'):
            metadata['service']['version'] = error['service_version']
        
        # 위치 정보
        if error.get('file'):
            metadata['location']['file'] = error['file']
        if error.get('line'):
            metadata['location']['line'] = int(error['line']) if str(error['line']).isdigit() else None
        if error.get('function'):
            metadata['location']['function'] = error['function']
        
        # 에러 정보
        if error.get('message'):
            metadata['error']['message'] = error['message']
        if error.get('error_type'):
            metadata['error']['type'] = error['error_type']
        if error.get('error_category'):
            metadata['error']['category'] = error['error_category']
        
        # 추가 메타데이터
        if error.get('execution_id'):
            metadata['metadata']['execution_id'] = error['execution_id']
        if error.get('request_id'):
            metadata['metadata']['request_id'] = error['request_id']
        if error.get('user_id'):
            metadata['metadata']['user_id'] = error['user_id']
        if error.get('log_name'):
            metadata['metadata']['log_name'] = error['log_name']
        
        return metadata
    
    def _parse_gcp_json_logs(self) -> List[Dict[str, Any]]:
        """GCP JSON 형식 로그 파싱"""
        errors = []
        
        # JSON 객체들을 분리하여 파싱
        json_blocks = []
        current_block = []
        brace_count = 0
        
        for line in self.log_content.split('\n'):
            current_block.append(line)
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and current_block:
                json_blocks.append('\n'.join(current_block))
                current_block = []
        
        # 각 JSON 블록 파싱
        for json_block in json_blocks:
            try:
                log_entry = json.loads(json_block)
                
                # ERROR 또는 CRITICAL 레벨만 처리
                severity = log_entry.get('severity', '').upper()
                if severity not in ['ERROR', 'CRITICAL', 'WARNING']:
                    continue
                
                error = {
                    'timestamp': log_entry.get('timestamp', datetime.now().isoformat()),
                    'severity': severity,
                    'message': log_entry.get('textPayload') or log_entry.get('jsonPayload', {}).get('message', ''),
                }
                
                # 리소스 정보 추출
                resource = log_entry.get('resource', {})
                if resource:
                    error['resource_type'] = resource.get('type', '')
                    labels = resource.get('labels', {})
                    if labels:
                        error['resource_name'] = labels.get('function_name') or labels.get('instance_id') or labels.get('service_name', '')
                        error['region'] = labels.get('region') or labels.get('zone', '')
                
                # 서비스 정보
                if 'serviceName' in log_entry:
                    error['service'] = log_entry['serviceName']
                
                # 위치 정보 추출
                source_location = log_entry.get('sourceLocation', {})
                if source_location:
                    error['file'] = source_location.get('file', '')
                    error['line'] = source_location.get('line', '')
                    error['function'] = source_location.get('function', '')
                
                # 라벨 정보
                labels = log_entry.get('labels', {})
                if labels:
                    error['execution_id'] = labels.get('execution_id', '')
                    error['request_id'] = labels.get('request_id', '')
                
                # logName 추출
                if 'logName' in log_entry:
                    error['log_name'] = log_entry['logName']
                
                # 메시지에서 파일/라인 정보 추출 (fallback)
                if not error.get('file') and error.get('message'):
                    file_match = re.search(r'at\s+([/\w\\]+\.(py|js|ts|java|cpp|c|go|rs)):(\d+)', error['message'])
                    if file_match:
                        error['file'] = file_match.group(1)
                        error['line'] = file_match.group(3)
                
                errors.append(error)
            except json.JSONDecodeError:
                continue
        
        return errors
    
    def _parse_gcp_text_logs(self) -> List[Dict[str, Any]]:
        """GCP 텍스트 형식 로그 파싱"""
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
            if severity_match and severity_match.group(1) in ['ERROR', 'CRITICAL', 'WARNING']:
                current_error['severity'] = severity_match.group(1)
            
            # 리소스 타입 추출
            resource_match = re.search(self.GCP_PATTERNS['resource'], line)
            if resource_match:
                current_error['resource_type'] = resource_match.group(1)
            
            # 위치 추출
            location_match = re.search(self.GCP_PATTERNS['location'], line)
            if location_match:
                current_error['location'] = location_match.group(1)
                current_error['region'] = location_match.group(1)
            
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
    
    def _parse_aws_logs(self) -> List[Dict[str, Any]]:
        """AWS CloudWatch 로그 파싱"""
        errors = []
        
        # JSON 형식 AWS 로그 파싱
        json_blocks = []
        current_block = []
        brace_count = 0
        
        for line in self.log_content.split('\n'):
            current_block.append(line)
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and current_block:
                json_blocks.append('\n'.join(current_block))
                current_block = []
        
        for json_block in json_blocks:
            try:
                log_entry = json.loads(json_block)
                
                # 레벨 확인
                level = log_entry.get('level', '').upper() or log_entry.get('severity', '').upper()
                if level not in ['ERROR', 'CRITICAL', 'WARNING', 'FATAL']:
                    continue
                
                error = {
                    'timestamp': log_entry.get('timestamp') or log_entry.get('@timestamp', datetime.now().isoformat()),
                    'severity': level,
                    'message': log_entry.get('message') or log_entry.get('msg', ''),
                    'system_type': 'aws'
                }
                
                # AWS 특정 필드
                if 'logGroup' in log_entry:
                    error['log_name'] = log_entry['logGroup']
                if 'logStream' in log_entry:
                    error['log_stream'] = log_entry['logStream']
                if 'aws' in log_entry:
                    aws_info = log_entry['aws']
                    if 'region' in aws_info:
                        error['region'] = aws_info['region']
                    if 'accountId' in aws_info:
                        error['account_id'] = aws_info['accountId']
                
                # 리소스 정보
                if 'resource' in log_entry:
                    resource = log_entry['resource']
                    error['resource_type'] = resource.get('type', '')
                    error['resource_name'] = resource.get('name', '')
                
                # 위치 정보 추출
                if 'file' in log_entry:
                    error['file'] = log_entry['file']
                if 'line' in log_entry:
                    error['line'] = log_entry['line']
                if 'function' in log_entry:
                    error['function'] = log_entry['function']
                
                errors.append(error)
            except json.JSONDecodeError:
                # 텍스트 형식 AWS 로그 처리
                if re.search(r'(ERROR|CRITICAL|FATAL)', line, re.IGNORECASE):
                    error = {
                        'timestamp': datetime.now().isoformat(),
                        'severity': 'ERROR',
                        'message': line.strip(),
                        'system_type': 'aws'
                    }
                    errors.append(error)
        
        return errors
    
    def _parse_azure_logs(self) -> List[Dict[str, Any]]:
        """Azure Monitor 로그 파싱"""
        errors = []
        
        # JSON 형식 Azure 로그 파싱
        json_blocks = []
        current_block = []
        brace_count = 0
        
        for line in self.log_content.split('\n'):
            current_block.append(line)
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0 and current_block:
                json_blocks.append('\n'.join(current_block))
                current_block = []
        
        for json_block in json_blocks:
            try:
                log_entry = json.loads(json_block)
                
                # 레벨 확인
                level = log_entry.get('Level', '').upper() or log_entry.get('severity', '').upper()
                if level not in ['ERROR', 'CRITICAL', 'WARNING', 'FATAL']:
                    continue
                
                error = {
                    'timestamp': log_entry.get('TimeGenerated') or log_entry.get('time', datetime.now().isoformat()),
                    'severity': level,
                    'message': log_entry.get('Message') or log_entry.get('message', ''),
                    'system_type': 'azure'
                }
                
                # Azure 특정 필드
                if 'ResourceId' in log_entry:
                    error['resource_id'] = log_entry['ResourceId']
                if 'Category' in log_entry:
                    error['category'] = log_entry['Category']
                if 'ResourceGroup' in log_entry:
                    error['resource_group'] = log_entry['ResourceGroup']
                if 'ResourceProvider' in log_entry:
                    error['resource_provider'] = log_entry['ResourceProvider']
                
                # 위치 정보
                if 'Caller' in log_entry:
                    error['function'] = log_entry['Caller']
                if 'File' in log_entry:
                    error['file'] = log_entry['File']
                if 'Line' in log_entry:
                    error['line'] = log_entry['Line']
                
                errors.append(error)
            except json.JSONDecodeError:
                continue
        
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
                {
                    'priority': 1,
                    'title': '데이터베이스 파일 존재 여부 확인',
                    'description': '데이터베이스 파일이 올바른 위치에 있는지 확인합니다.',
                    'steps': [
                        '파일 경로 확인: C:/test/test02/data/database.db',
                        '파일 존재 여부 확인: `fs.existsSync(DB_FILE)`',
                        '파일 권한 확인: 읽기/쓰기 권한이 있는지 확인'
                    ],
                    'code_example': 'if (!fs.existsSync(DB_FILE)) {\n  console.error("데이터베이스 파일이 없습니다:", DB_FILE);\n}'
                },
                {
                    'priority': 2,
                    'title': '데이터베이스 연결 문자열 검증',
                    'description': '연결 문자열 형식과 인증 정보를 확인합니다.',
                    'steps': [
                        '연결 문자열 형식 확인 (SQLite: sqlite://path, PostgreSQL: postgresql://user:pass@host:port/db)',
                        '환경 변수에서 연결 정보 확인: `process.env.DATABASE_URL`',
                        '인증 정보가 올바른지 확인'
                    ],
                    'code_example': 'const dbUrl = process.env.DATABASE_URL || "sqlite://data/database.db";\nconsole.log("DB URL:", dbUrl);'
                },
                {
                    'priority': 3,
                    'title': '데이터베이스 서버 상태 확인',
                    'description': '데이터베이스 서버가 실행 중인지 확인합니다.',
                    'steps': [
                        '서버 프로세스 확인: `ps aux | grep postgres` (Linux) 또는 작업 관리자 (Windows)',
                        '포트 리스닝 확인: `netstat -an | grep 5432` (PostgreSQL)',
                        '서버 로그 확인: 에러 메시지나 연결 거부 로그 확인'
                    ],
                    'code_example': '// 헬스체크 구현\nasync function checkDbHealth() {\n  try {\n    await db.exec("SELECT 1");\n    return true;\n  } catch (e) {\n    return false;\n  }\n}'
                },
                {
                    'priority': 4,
                    'title': '테이블 스키마 확인',
                    'description': '필요한 테이블과 컬럼이 존재하는지 확인합니다.',
                    'steps': [
                        '테이블 목록 확인: `SELECT name FROM sqlite_master WHERE type="table"`',
                        '컬럼 존재 여부 확인: `PRAGMA table_info(table_name)`',
                        '마이그레이션 실행: 누락된 컬럼이 있으면 ALTER TABLE로 추가'
                    ],
                    'code_example': 'const tables = db.exec("SELECT name FROM sqlite_master WHERE type=\'table\'");\nconsole.log("Tables:", tables);'
                }
            ],
            'prevention': [
                {
                    'title': '연결 풀링 구현',
                    'description': '데이터베이스 연결을 재사용하여 성능을 최적화하고 연결 오류를 줄입니다.',
                    'implementation': 'const pool = new Pool({\n  max: 20,\n  idleTimeoutMillis: 30000,\n  connectionTimeoutMillis: 2000\n});',
                    'benefits': ['연결 재사용으로 성능 향상', '동시 연결 수 제한으로 리소스 관리', '자동 재연결 처리']
                },
                {
                    'title': '재시도 로직 추가',
                    'description': '일시적인 연결 오류 시 자동으로 재시도합니다.',
                    'implementation': 'async function queryWithRetry(query, retries = 3) {\n  for (let i = 0; i < retries; i++) {\n    try {\n      return await db.query(query);\n    } catch (e) {\n      if (i === retries - 1) throw e;\n      await sleep(1000 * (i + 1));\n    }\n  }\n}',
                    'benefits': ['일시적 네트워크 오류 자동 복구', '사용자 경험 개선', '시스템 안정성 향상']
                },
                {
                    'title': '연결 타임아웃 설정',
                    'description': '적절한 타임아웃 값을 설정하여 무한 대기를 방지합니다.',
                    'implementation': 'const dbConfig = {\n  connectionTimeoutMillis: 5000,\n  queryTimeoutMillis: 10000,\n  idleTimeoutMillis: 30000\n};',
                    'benefits': ['무한 대기 방지', '리소스 낭비 방지', '빠른 오류 감지']
                },
                {
                    'title': '헬스체크 모니터링',
                    'description': '정기적으로 데이터베이스 상태를 확인하고 알림을 설정합니다.',
                    'implementation': 'setInterval(async () => {\n  const healthy = await checkDbHealth();\n  if (!healthy) {\n    sendAlert("데이터베이스 연결 실패");\n  }\n}, 60000);',
                    'benefits': ['문제 조기 발견', '자동 알림', '가동 시간 향상']
                }
            ]
        },
        'network': {
            'keywords': ['network', 'connection', 'timeout', 'refused', 'socket', 'http', 'https'],
            'solutions': [
                {
                    'priority': 1,
                    'title': '네트워크 연결 상태 확인',
                    'description': '기본 네트워크 연결이 정상인지 확인합니다.',
                    'steps': [
                        '인터넷 연결 확인: `ping 8.8.8.8`',
                        'DNS 확인: `nslookup api.example.com`',
                        '프록시 설정 확인: `echo $HTTP_PROXY` (Linux) 또는 환경 변수 확인'
                    ],
                    'code_example': '// 연결 테스트\nfetch("https://api.example.com/health")\n  .then(r => console.log("연결 성공"))\n  .catch(e => console.error("연결 실패:", e));'
                },
                {
                    'priority': 2,
                    'title': '방화벽 및 포트 확인',
                    'description': '방화벽 규칙과 포트 접근 권한을 확인합니다.',
                    'steps': [
                        '방화벽 상태 확인: `netsh advfirewall show allprofiles` (Windows)',
                        '포트 리스닝 확인: `netstat -an | findstr :3001`',
                        '방화벽 규칙 추가: 필요한 포트에 대한 인바운드/아웃바운드 규칙 확인'
                    ],
                    'code_example': '// 포트 확인\nconst server = http.createServer();\nserver.listen(3001, () => {\n  console.log("포트 3001 리스닝 중");\n});'
                },
                {
                    'priority': 3,
                    'title': '타임아웃 설정 조정',
                    'description': '네트워크 타임아웃 값을 환경에 맞게 조정합니다.',
                    'steps': [
                        '현재 타임아웃 값 확인: `timeout: 30000` (30초)',
                        '네트워크 환경에 맞게 조정: 느린 네트워크는 증가, 빠른 네트워크는 감소',
                        '환경 변수로 관리: `process.env.REQUEST_TIMEOUT || 30000`'
                    ],
                    'code_example': 'const timeout = parseInt(process.env.REQUEST_TIMEOUT || "30000");\nconst controller = new AbortController();\nsetTimeout(() => controller.abort(), timeout);'
                },
                {
                    'priority': 4,
                    'title': '프록시 설정 확인',
                    'description': '프록시 환경에서 올바른 프록시 설정이 되어 있는지 확인합니다.',
                    'steps': [
                        '프록시 URL 확인: `http://70.10.15.10:8080`',
                        '프록시 인증 정보 확인: 필요시 사용자명/비밀번호 설정',
                        '프록시 우회 설정: localhost는 프록시 우회 설정 확인'
                    ],
                    'code_example': 'const proxyAgent = new HttpsProxyAgent({\n  host: "70.10.15.10",\n  port: 8080,\n  rejectUnauthorized: false\n});'
                }
            ],
            'prevention': [
                {
                    'title': '재시도 로직 구현',
                    'description': '네트워크 오류 시 자동으로 재시도하여 일시적 오류를 복구합니다.',
                    'implementation': 'async function fetchWithRetry(url, options = {}, retries = 3) {\n  for (let i = 0; i < retries; i++) {\n    try {\n      return await fetch(url, options);\n    } catch (e) {\n      if (i === retries - 1) throw e;\n      await sleep(1000 * Math.pow(2, i)); // 지수 백오프\n    }\n  }\n}',
                    'benefits': ['일시적 네트워크 오류 자동 복구', '사용자 경험 개선', '시스템 안정성 향상']
                },
                {
                    'title': '서킷 브레이커 패턴 적용',
                    'description': '연속된 실패 시 요청을 차단하여 리소스를 보호합니다.',
                    'implementation': 'class CircuitBreaker {\n  constructor(threshold = 5, timeout = 60000) {\n    this.failures = 0;\n    this.threshold = threshold;\n    this.timeout = timeout;\n    this.state = "CLOSED";\n  }\n  async call(fn) {\n    if (this.state === "OPEN") throw new Error("Circuit breaker OPEN");\n    try {\n      const result = await fn();\n      this.failures = 0;\n      return result;\n    } catch (e) {\n      this.failures++;\n      if (this.failures >= this.threshold) this.state = "OPEN";\n      throw e;\n    }\n  }\n}',
                    'benefits': ['연속 실패 방지', '리소스 보호', '빠른 실패 처리']
                },
                {
                    'title': '헬스체크 구현',
                    'description': '정기적으로 네트워크 상태를 확인하고 문제를 조기 발견합니다.',
                    'implementation': 'async function healthCheck() {\n  try {\n    const response = await fetch("/api/health", { timeout: 5000 });\n    return response.ok;\n  } catch {\n    return false;\n  }\n}\nsetInterval(healthCheck, 30000);',
                    'benefits': ['문제 조기 발견', '자동 복구', '모니터링 강화']
                },
                {
                    'title': '환경 변수로 타임아웃 관리',
                    'description': '타임아웃 값을 환경 변수로 관리하여 쉽게 조정할 수 있게 합니다.',
                    'implementation': 'const config = {\n  timeout: parseInt(process.env.REQUEST_TIMEOUT || "30000"),\n  retries: parseInt(process.env.MAX_RETRIES || "3"),\n  backoff: parseInt(process.env.BACKOFF_MS || "1000")\n};',
                    'benefits': ['유연한 설정', '환경별 최적화', '운영 편의성']
                }
            ]
        },
        'authentication': {
            'keywords': ['auth', 'unauthorized', 'forbidden', 'token', 'credential', 'permission'],
            'solutions': [
                {
                    'priority': 1,
                    'title': 'JWT 토큰 유효성 검증',
                    'description': '토큰이 유효하고 만료되지 않았는지 확인합니다.',
                    'steps': [
                        '토큰 형식 확인: `Bearer <token>` 형식인지 확인',
                        '토큰 만료 시간 확인: `jwt.decode(token).exp`',
                        '토큰 서명 검증: `jwt.verify(token, secret)`'
                    ],
                    'code_example': 'try {\n  const decoded = jwt.verify(token, JWT_SECRET);\n  if (decoded.exp < Date.now() / 1000) {\n    throw new Error("토큰 만료");\n  }\n} catch (e) {\n  // 토큰 갱신 필요\n}'
                },
                {
                    'priority': 2,
                    'title': '사용자 권한 확인',
                    'description': '요청한 리소스에 대한 접근 권한이 있는지 확인합니다.',
                    'steps': [
                        '사용자 역할 확인: `user.role`',
                        '리소스 권한 확인: 역할 기반 접근 제어 (RBAC)',
                        '권한 부족 시 명확한 에러 메시지 반환'
                    ],
                    'code_example': 'function checkPermission(user, resource, action) {\n  const permissions = user.role.permissions;\n  return permissions.some(p => \n    p.resource === resource && p.actions.includes(action)\n  );\n}'
                },
                {
                    'priority': 3,
                    'title': '인증 서버 상태 확인',
                    'description': '인증 서버가 정상 작동하는지 확인합니다.',
                    'steps': [
                        '인증 서버 헬스체크: `GET /auth/health`',
                        '인증 서버 로그 확인: 에러 메시지 확인',
                        '서버 응답 시간 확인: 타임아웃 발생 여부 확인'
                    ],
                    'code_example': 'async function checkAuthServer() {\n  try {\n    const res = await fetch("http://auth-server/health");\n    return res.ok;\n  } catch {\n    return false;\n  }\n}'
                },
                {
                    'priority': 4,
                    'title': '토큰 갱신 로직 확인',
                    'description': '토큰 만료 전 자동 갱신이 작동하는지 확인합니다.',
                    'steps': [
                        '토큰 만료 시간 확인: 만료 5분 전 갱신 로직 확인',
                        '갱신 토큰(Refresh Token) 확인: 유효한 refresh token이 있는지 확인',
                        '갱신 API 호출: `/api/auth/refresh` 엔드포인트 확인'
                    ],
                    'code_example': 'async function refreshToken(refreshToken) {\n  const response = await fetch("/api/auth/refresh", {\n    method: "POST",\n    body: JSON.stringify({ refreshToken })\n  });\n  return await response.json();\n}'
                }
            ],
            'prevention': [
                {
                    'title': '자동 토큰 갱신 구현',
                    'description': '토큰 만료 전 자동으로 갱신하여 사용자 경험을 개선합니다.',
                    'implementation': 'function setupTokenRefresh() {\n  const token = getToken();\n  const expiresIn = jwt.decode(token).exp * 1000 - Date.now();\n  setTimeout(async () => {\n    const newToken = await refreshToken(getRefreshToken());\n    setToken(newToken.accessToken);\n    setupTokenRefresh();\n  }, expiresIn - 300000); // 5분 전 갱신\n}',
                    'benefits': ['사용자 경험 개선', '인증 오류 감소', '자동화']
                },
                {
                    'title': '명확한 에러 메시지 제공',
                    'description': '인증 실패 시 사용자에게 명확하고 도움이 되는 메시지를 제공합니다.',
                    'implementation': 'if (!token) {\n  return res.status(401).json({\n    error: "인증 토큰이 필요합니다",\n    code: "MISSING_TOKEN",\n    solution: "로그인 후 다시 시도하세요"\n  });\n}',
                    'benefits': ['사용자 이해도 향상', '디버깅 용이', '지원 부담 감소']
                },
                {
                    'title': '인증 로그 기록',
                    'description': '인증 시도와 실패를 로깅하여 보안 이슈를 추적합니다.',
                    'implementation': 'function logAuthAttempt(userId, success, reason) {\n  logger.info({\n    event: "auth_attempt",\n    userId,\n    success,\n    reason,\n    timestamp: new Date().toISOString(),\n    ip: req.ip\n  });\n}',
                    'benefits': ['보안 모니터링', '이상 행위 감지', '감사 추적']
                },
                {
                    'title': '정기적인 인증 시스템 점검',
                    'description': '정기적으로 인증 시스템의 상태를 점검하고 업데이트합니다.',
                    'implementation': '// 매일 자정 인증 통계 확인\ncron.schedule("0 0 * * *", async () => {\n  const stats = await getAuthStats();\n  if (stats.failureRate > 0.1) {\n    sendAlert("인증 실패율이 높습니다");\n  }\n});',
                    'benefits': ['문제 조기 발견', '보안 강화', '시스템 안정성']
                }
            ]
        },
        'memory': {
            'keywords': ['memory', 'out of memory', 'oom', 'heap', 'stack overflow'],
            'solutions': [
                {
                    'priority': 1,
                    'title': '메모리 사용량 모니터링',
                    'description': '현재 메모리 사용량을 확인하고 병목 지점을 찾습니다.',
                    'steps': [
                        '프로세스 메모리 확인: `process.memoryUsage()`',
                        '힙 메모리 확인: `heapUsed`, `heapTotal` 값 확인',
                        '메모리 사용 추이 확인: 시간에 따른 메모리 증가 패턴 분석'
                    ],
                    'code_example': 'const usage = process.memoryUsage();\nconsole.log({\n  heapUsed: `${Math.round(usage.heapUsed / 1024 / 1024)}MB`,\n  heapTotal: `${Math.round(usage.heapTotal / 1024 / 1024)}MB`,\n  rss: `${Math.round(usage.rss / 1024 / 1024)}MB`\n});'
                },
                {
                    'priority': 2,
                    'title': '메모리 누수 확인',
                    'description': '메모리 누수가 발생하는 코드를 찾아 수정합니다.',
                    'steps': [
                        '메모리 프로파일러 실행: `node --inspect app.js`',
                        'Chrome DevTools로 힙 스냅샷 분석',
                        '참조가 남아있는 객체 확인: 클로저, 이벤트 리스너, 타이머 등'
                    ],
                    'code_example': '// 메모리 누수 가능성 있는 코드\nconst listeners = [];\n// 해결: 이벤트 리스너 제거\nfunction cleanup() {\n  listeners.forEach(l => eventEmitter.removeListener(l));\n  listeners = [];\n}'
                },
                {
                    'priority': 3,
                    'title': '메모리 제한 증가',
                    'description': '애플리케이션의 메모리 제한을 증가시킵니다 (임시 조치).',
                    'steps': [
                        'Node.js 힙 크기 증가: `node --max-old-space-size=4096 app.js`',
                        '환경 변수 설정: `NODE_OPTIONS="--max-old-space-size=4096"`',
                        'Docker 메모리 제한 증가: `docker run -m 4g ...`'
                    ],
                    'code_example': '// package.json scripts\n"start": "node --max-old-space-size=4096 app.js"'
                },
                {
                    'priority': 4,
                    'title': '대용량 데이터 처리 최적화',
                    'description': '대용량 데이터를 스트리밍 방식으로 처리하여 메모리 사용을 줄입니다.',
                    'steps': [
                        '스트리밍 방식으로 변경: `fs.createReadStream()` 사용',
                        '배치 처리: 데이터를 작은 청크로 나누어 처리',
                        '불필요한 데이터 캐싱 제거'
                    ],
                    'code_example': '// 스트리밍 처리\nconst stream = fs.createReadStream("large-file.json");\nstream.on("data", chunk => {\n  processChunk(chunk);\n});'
                }
            ],
            'prevention': [
                {
                    'title': '정기적인 메모리 프로파일링',
                    'description': '정기적으로 메모리 프로파일링을 수행하여 문제를 조기 발견합니다.',
                    'implementation': 'const v8 = require("v8");\nsetInterval(() => {\n  const heap = v8.getHeapStatistics();\n  if (heap.used_heap_size / heap.heap_size_limit > 0.8) {\n    sendAlert("메모리 사용량이 80%를 초과했습니다");\n  }\n}, 60000);',
                    'benefits': ['문제 조기 발견', '성능 최적화', '시스템 안정성']
                },
                {
                    'title': '스트리밍 방식으로 데이터 처리',
                    'description': '대용량 데이터를 한 번에 메모리에 로드하지 않고 스트리밍으로 처리합니다.',
                    'implementation': 'async function processLargeData(filePath) {\n  const stream = fs.createReadStream(filePath);\n  for await (const chunk of stream) {\n    await processChunk(chunk);\n  }\n}',
                    'benefits': ['메모리 사용량 감소', '대용량 파일 처리 가능', '성능 향상']
                },
                {
                    'title': '캐시 크기 제한 및 LRU 정책',
                    'description': '캐시 크기를 제한하고 LRU 정책을 사용하여 메모리를 효율적으로 관리합니다.',
                    'implementation': 'const LRU = require("lru-cache");\nconst cache = new LRU({\n  max: 100, // 최대 항목 수\n  maxAge: 1000 * 60 * 60, // 1시간\n  length: (n) => n.length\n});',
                    'benefits': ['메모리 사용량 제어', '자동 정리', '성능 최적화']
                },
                {
                    'title': '메모리 모니터링 알림 설정',
                    'description': '메모리 사용량이 임계값을 초과하면 알림을 보냅니다.',
                    'implementation': 'function checkMemory() {\n  const usage = process.memoryUsage();\n  const threshold = 512 * 1024 * 1024; // 512MB\n  if (usage.heapUsed > threshold) {\n    sendAlert(`메모리 사용량 경고: ${usage.heapUsed / 1024 / 1024}MB`);\n  }\n}\nsetInterval(checkMemory, 30000);',
                    'benefits': ['문제 조기 발견', '자동 알림', '시스템 보호']
                }
            ]
        },
        'file': {
            'keywords': ['file', 'not found', 'permission denied', 'eacces', 'enoent'],
            'solutions': [
                {
                    'priority': 1,
                    'title': '파일 경로 검증',
                    'description': '파일 경로가 올바른지 절대 경로와 상대 경로를 모두 확인합니다.',
                    'steps': [
                        '절대 경로 확인: `path.isAbsolute(filePath)`',
                        '상대 경로 해석: `path.resolve(process.cwd(), filePath)`',
                        '경로 정규화: `path.normalize(filePath)`',
                        '실제 파일 존재 확인: `fs.existsSync(filePath)`'
                    ],
                    'code_example': 'const filePath = path.resolve(__dirname, "../logs/app-error.log");\nif (!fs.existsSync(filePath)) {\n  console.error("파일을 찾을 수 없습니다:", filePath);\n}'
                },
                {
                    'priority': 2,
                    'title': '파일 권한 확인 및 수정',
                    'description': '파일 읽기/쓰기 권한을 확인하고 필요시 수정합니다.',
                    'steps': [
                        '파일 권한 확인: `fs.accessSync(filePath, fs.constants.R_OK | fs.constants.W_OK)`',
                        '권한 부족 시 수정: `chmod 644 file.log` (Linux) 또는 속성 변경 (Windows)',
                        '소유자 확인: 파일 소유자가 현재 사용자와 일치하는지 확인'
                    ],
                    'code_example': 'try {\n  fs.accessSync(filePath, fs.constants.R_OK | fs.constants.W_OK);\n} catch (e) {\n  console.error("파일 권한 오류:", e.message);\n  // Windows: 파일 속성에서 읽기 전용 해제\n  // Linux: chmod 644 file.log\n}'
                },
                {
                    'priority': 3,
                    'title': '디렉토리 생성',
                    'description': '필요한 디렉토리가 없으면 자동으로 생성합니다.',
                    'steps': [
                        '디렉토리 존재 확인: `fs.existsSync(dirPath)`',
                        '디렉토리 생성: `fs.mkdirSync(dirPath, { recursive: true })`',
                        '권한 설정: 생성된 디렉토리에 적절한 권한 부여'
                    ],
                    'code_example': 'const dirPath = path.dirname(filePath);\nif (!fs.existsSync(dirPath)) {\n  fs.mkdirSync(dirPath, { recursive: true, mode: 0o755 });\n  console.log("디렉토리 생성:", dirPath);\n}'
                },
                {
                    'priority': 4,
                    'title': '디스크 공간 확인',
                    'description': '디스크에 충분한 공간이 있는지 확인합니다.',
                    'steps': [
                        '디스크 사용량 확인: `df -h` (Linux) 또는 디스크 속성 (Windows)',
                        '여유 공간 확인: 최소 10% 이상 여유 공간 필요',
                        '디스크 정리: 불필요한 파일 삭제 또는 로그 로테이션 설정'
                    ],
                    'code_example': 'const stats = fs.statSync("/");\nconst freeSpace = stats.blocks * stats.blksize;\nif (freeSpace < 1024 * 1024 * 1024) { // 1GB 미만\n  console.warn("디스크 공간 부족");\n}'
                }
            ],
            'prevention': [
                {
                    'title': '환경 변수로 파일 경로 관리',
                    'description': '파일 경로를 환경 변수로 관리하여 유연성을 높입니다.',
                    'implementation': 'const LOG_DIR = process.env.LOG_DIR || path.join(__dirname, "logs");\nconst LOG_FILE = path.join(LOG_DIR, "app-error.log");\n// .env 파일\n// LOG_DIR=C:/test/test02/logs',
                    'benefits': ['환경별 설정', '유연한 경로 관리', '배포 편의성']
                },
                {
                    'title': '파일 접근 전 존재 여부 확인',
                    'description': '파일을 사용하기 전에 반드시 존재 여부를 확인합니다.',
                    'implementation': 'async function safeReadFile(filePath) {\n  try {\n    await fs.promises.access(filePath, fs.constants.F_OK);\n    return await fs.promises.readFile(filePath, "utf-8");\n  } catch (e) {\n    if (e.code === "ENOENT") {\n      console.error("파일이 없습니다:", filePath);\n      return null;\n    }\n    throw e;\n  }\n}',
                    'benefits': ['에러 방지', '명확한 에러 메시지', '안정성 향상']
                },
                {
                    'title': '파일 권한 자동 설정',
                    'description': '파일 생성 시 적절한 권한을 자동으로 설정합니다.',
                    'implementation': 'function createFileWithPermissions(filePath, content) {\n  const dir = path.dirname(filePath);\n  fs.mkdirSync(dir, { recursive: true, mode: 0o755 });\n  fs.writeFileSync(filePath, content, { mode: 0o644 });\n}',
                    'benefits': ['권한 오류 방지', '자동화', '일관성 유지']
                },
                {
                    'title': '디스크 공간 모니터링',
                    'description': '정기적으로 디스크 공간을 확인하고 부족하면 알림을 보냅니다.',
                    'implementation': 'const diskusage = require("diskusage");\nsetInterval(async () => {\n  const { free, total } = await diskusage.check("/");\n  const usagePercent = ((total - free) / total) * 100;\n  if (usagePercent > 90) {\n    sendAlert(`디스크 사용량이 ${usagePercent.toFixed(1)}%입니다`);\n  }\n}, 3600000); // 1시간마다',
                    'benefits': ['문제 조기 발견', '자동 알림', '시스템 보호']
                }
            ]
        },
        'syntax': {
            'keywords': ['syntax', 'parse', 'invalid', 'unexpected', 'token'],
            'solutions': [
                {
                    'priority': 1,
                    'title': '에러 발생 위치 확인',
                    'description': '에러 메시지에서 파일 경로와 라인 번호를 확인합니다.',
                    'steps': [
                        '에러 메시지 파싱: `File: C:/test/test02/database.js, Line: 45`',
                        '해당 파일 열기: 에디터에서 파일 열기',
                        '라인 번호로 이동: 해당 라인 주변 코드 확인',
                        '문법 오류 확인: 괄호, 따옴표, 세미콜론 등 확인'
                    ],
                    'code_example': '// 에러 예시\n// SyntaxError: Unexpected token }\n// at database.js:45\n// 해당 라인 확인:\nconst stmt = db.prepare(\'SELECT * FROM error_logs WHERE id = ?\'); // 45번 라인'
                },
                {
                    'priority': 2,
                    'title': 'IDE/린터로 문법 검사',
                    'description': 'IDE나 린터를 사용하여 문법 오류를 자동으로 찾습니다.',
                    'steps': [
                        'ESLint 실행: `npm run lint`',
                        'TypeScript 컴파일러 실행: `tsc --noEmit`',
                        'IDE 문법 하이라이트 확인: 빨간 밑줄 표시 확인',
                        '자동 포맷팅: `Prettier` 또는 `ESLint --fix` 실행'
                    ],
                    'code_example': '// package.json\n"scripts": {\n  "lint": "eslint src/**/*.{js,vue}",\n  "lint:fix": "eslint --fix src/**/*.{js,vue}",\n  "type-check": "tsc --noEmit"\n}'
                },
                {
                    'priority': 3,
                    'title': '최근 변경 사항 검토',
                    'description': '최근 변경된 코드를 검토하여 문법 오류를 찾습니다.',
                    'steps': [
                        'Git 변경 이력 확인: `git diff HEAD`',
                        '최근 커밋 확인: `git log --oneline -10`',
                        '변경된 파일만 검사: `git diff --name-only`',
                        '변경 사항 되돌리기: 문제가 있으면 `git revert` 또는 `git reset`'
                    ],
                    'code_example': '// 최근 변경 확인\ngit diff HEAD~1 HEAD -- database.js\n// 특정 라인 확인\ngit blame database.js | grep "45"'
                },
                {
                    'priority': 4,
                    'title': 'JSON/설정 파일 검증',
                    'description': 'JSON이나 설정 파일의 문법 오류를 확인합니다.',
                    'steps': [
                        'JSON 검증: `JSON.parse()` 또는 온라인 JSON 검증기 사용',
                        '설정 파일 검증: YAML, TOML 등의 문법 확인',
                        '인코딩 확인: UTF-8 인코딩이 올바른지 확인',
                        '특수 문자 확인: 따옴표, 이스케이프 문자 등 확인'
                    ],
                    'code_example': 'try {\n  const config = JSON.parse(fs.readFileSync("config.json", "utf-8"));\n} catch (e) {\n  console.error("JSON 파싱 오류:", e.message);\n  console.error("라인:", e.message.match(/line (\\d+)/)?.[1]);\n}'
                }
            ],
            'prevention': [
                {
                    'title': '코드 포맷터 및 린터 자동화',
                    'description': '코드 저장 시 자동으로 포맷팅하고 린터를 실행합니다.',
                    'implementation': '// .vscode/settings.json\n{\n  "editor.formatOnSave": true,\n  "editor.codeActionsOnSave": {\n    "source.fixAll.eslint": true\n  },\n  "eslint.validate": ["javascript", "vue"]\n}',
                    'benefits': ['일관된 코드 스타일', '문법 오류 자동 수정', '코드 품질 향상']
                },
                {
                    'title': 'CI/CD 파이프라인에 문법 검사 추가',
                    'description': '코드 커밋 시 자동으로 문법 검사를 수행합니다.',
                    'implementation': '# .github/workflows/lint.yml\nname: Lint\non: [push, pull_request]\njobs:\n  lint:\n    runs-on: ubuntu-latest\n    steps:\n      - uses: actions/checkout@v2\n      - run: npm install\n      - run: npm run lint\n      - run: npm run type-check',
                    'benefits': ['문법 오류 조기 발견', '코드 품질 보장', '자동화']
                },
                {
                    'title': '코드 리뷰 프로세스',
                    'description': '코드 리뷰를 통해 문법 오류를 사전에 발견합니다.',
                    'implementation': '// Pull Request 템플릿\n## 체크리스트\n- [ ] ESLint 오류 없음\n- [ ] TypeScript 타입 오류 없음\n- [ ] 테스트 통과\n- [ ] 코드 리뷰 완료',
                    'benefits': ['문법 오류 사전 발견', '코드 품질 향상', '지식 공유']
                },
                {
                    'title': '타입스크립트 사용',
                    'description': '타입스크립트를 사용하여 컴파일 타임에 문법 오류를 발견합니다.',
                    'implementation': '// tsconfig.json\n{\n  "compilerOptions": {\n    "strict": true,\n    "noImplicitAny": true,\n    "noUnusedLocals": true\n  }\n}',
                    'benefits': ['컴파일 타임 오류 발견', '타입 안정성', '코드 품질 향상']
                }
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
# 워크스페이스 검색 클래스
# ============================================

class WorkspaceSearcher:
    """워크스페이스에서 에러 발생 위치를 찾는 클래스"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.exclude_dirs = {
            'node_modules', '.git', '__pycache__', '.vscode', 
            'dist', 'build', '.next', 'venv', 'env', '.venv',
            'data', 'logs', 'log', 'tmp', 'samples'
        }
        self.code_extensions = {
            '.py', '.js', '.jsx', '.ts', '.tsx', '.vue', '.java', 
            '.cpp', '.c', '.go', '.rs', '.php', '.rb', '.swift'
        }
    
    def find_error_location(self, error_message: str) -> Dict[str, Any]:
        """
        에러 메시지에서 파일명, 함수명을 추출하여 워크스페이스에서 찾기
        
        Returns:
            Dict with keys: files, functions, code_snippets, suggestions
        """
        result = {
            'files': [],
            'functions': [],
            'code_snippets': [],
            'suggestions': []
        }
        
        # 파일명 패턴 추출 (예: api-server.js:123, src/App.vue, database.js)
        file_patterns = [
            r'([/\w\\]+\.(py|js|jsx|ts|tsx|vue|java|cpp|c|go|rs|php|rb|swift))(?::(\d+))?',
            r'File\s+["\']([^"\']+)["\']',
            r'at\s+([/\w\\]+\.(py|js|jsx|ts|tsx|vue))',
            r'([/\w\\]+\.(py|js|jsx|ts|tsx|vue)):\s*line\s+(\d+)',
        ]
        
        found_files = set()
        found_functions = []
        
        for pattern in file_patterns:
            matches = re.finditer(pattern, error_message, re.IGNORECASE)
            for match in matches:
                file_path = match.group(1)
                line_num = match.group(3) if len(match.groups()) > 2 else None
                
                # 워크스페이스에서 파일 찾기
                workspace_file = self._find_file_in_workspace(file_path)
                if workspace_file:
                    found_files.add((workspace_file, line_num))
        
        # 함수명/클래스명 추출 (예: analyzeErrorLog, ErrorAnalyzer, UserService)
        function_patterns = [
            r'function\s+(\w+)',
            r'def\s+(\w+)',
            r'class\s+(\w+)',
            r'(\w+)\s*\([^)]*\)\s*\{',
            r'(\w+)\s*\([^)]*\)\s*:',
            r'at\s+(\w+)\s*\(',
            r'(\w+)\s*is\s+not\s+defined',
            r'Cannot\s+read\s+property\s+[\'"](\w+)[\'"]',
        ]
        
        for pattern in function_patterns:
            matches = re.finditer(pattern, error_message, re.IGNORECASE)
            for match in matches:
                func_name = match.group(1)
                if len(func_name) > 2 and func_name[0].isupper() or func_name.islower():
                    found_functions.append(func_name)
        
        # 찾은 파일들 처리
        for file_path, line_num in found_files:
            file_info = {
                'path': file_path,
                'line': int(line_num) if line_num else None,
                'relative_path': os.path.relpath(file_path, self.workspace_path)
            }
            
            # 코드 스니펫 추출
            if line_num:
                snippet = self._extract_code_snippet(file_path, int(line_num))
                if snippet:
                    file_info['code_snippet'] = snippet
            
            result['files'].append(file_info)
        
        # 찾은 함수들 처리
        for func_name in set(found_functions):
            func_locations = self._find_function_in_workspace(func_name)
            result['functions'].extend(func_locations)
        
        # 수정 제안 생성
        if result['files'] or result['functions']:
            result['suggestions'] = self._generate_suggestions(error_message, result)
        
        return result
    
    def _find_file_in_workspace(self, file_path: str) -> Optional[str]:
        """워크스페이스에서 파일 찾기"""
        workspace = Path(self.workspace_path)
        
        # 절대 경로인 경우
        if os.path.isabs(file_path):
            if file_path.startswith(self.workspace_path):
                if os.path.exists(file_path):
                    return file_path
            return None
        
        # 상대 경로인 경우
        # 1. 직접 경로 확인
        direct_path = workspace / file_path
        if direct_path.exists() and direct_path.is_file():
            return str(direct_path)
        
        # 2. 파일명만으로 검색
        filename = os.path.basename(file_path)
        for root, dirs, files in os.walk(self.workspace_path):
            # 제외 디렉토리 필터링
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            if filename in files:
                found_path = os.path.join(root, filename)
                if os.path.exists(found_path):
                    return found_path
        
        return None
    
    def _find_function_in_workspace(self, func_name: str) -> List[Dict[str, Any]]:
        """워크스페이스에서 함수/클래스 찾기"""
        locations = []
        workspace = Path(self.workspace_path)
        
        for root, dirs, files in os.walk(self.workspace_path):
            # 제외 디렉토리 필터링
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            
            for file in files:
                if any(file.endswith(ext) for ext in self.code_extensions):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.split('\n')
                            
                            # 함수/클래스 정의 찾기
                            for i, line in enumerate(lines, 1):
                                # Python: def func_name, class ClassName
                                if re.search(rf'\b(def|class)\s+{re.escape(func_name)}\b', line):
                                    locations.append({
                                        'path': file_path,
                                        'line': i,
                                        'relative_path': os.path.relpath(file_path, self.workspace_path),
                                        'code_snippet': self._extract_code_snippet(file_path, i)
                                    })
                                # JavaScript/TypeScript: function funcName, class ClassName
                                elif re.search(rf'\b(function|class|const|let|var)\s+{re.escape(func_name)}\b', line):
                                    locations.append({
                                        'path': file_path,
                                        'line': i,
                                        'relative_path': os.path.relpath(file_path, self.workspace_path),
                                        'code_snippet': self._extract_code_snippet(file_path, i)
                                    })
                    except Exception:
                        continue
        
        return locations
    
    def _extract_code_snippet(self, file_path: str, line_num: int, context_lines: int = 5) -> Optional[str]:
        """파일에서 특정 라인 주변 코드 추출"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
            
            start = max(0, line_num - context_lines - 1)
            end = min(len(lines), line_num + context_lines)
            
            snippet_lines = []
            for i in range(start, end):
                prefix = '>>> ' if i == line_num - 1 else '    '
                snippet_lines.append(f"{prefix}{i+1:4d}: {lines[i].rstrip()}")
            
            return '\n'.join(snippet_lines)
        except Exception:
            return None
    
    def _generate_suggestions(self, error_message: str, locations: Dict[str, Any]) -> List[str]:
        """수정 제안 생성"""
        suggestions = []
        
        if locations['files']:
            suggestions.append(f"발생 위치: {len(locations['files'])}개 파일에서 발견됨")
            for file_info in locations['files'][:3]:  # 최대 3개만 표시
                rel_path = file_info['relative_path']
                if file_info['line']:
                    suggestions.append(f"  - {rel_path}:{file_info['line']}")
                else:
                    suggestions.append(f"  - {rel_path}")
        
        if locations['functions']:
            suggestions.append(f"관련 함수/클래스: {len(locations['functions'])}개 발견됨")
            for func_info in locations['functions'][:3]:  # 최대 3개만 표시
                suggestions.append(f"  - {func_info['relative_path']}:{func_info['line']} ({func_info.get('name', 'N/A')})")
        
        return suggestions

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
                        "description": "분석할 로그 파일 경로 (선택사항, log_content와 함께 사용 불가)"
                    },
                    "log_content": {
                        "type": "string",
                        "description": "직접 입력된 로그 내용 (선택사항, log_file_path와 함께 사용 불가)"
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
    
    # 컬럼 너비 정의
    col_widths = {
        'no': 6,
        'timestamp': 22,
        'severity': 10,
        'message': 50,
        'location': 35,
        'system': 15
    }
    
    total_width = sum(col_widths.values()) + len(col_widths) * 3 + 1  # 3은 구분자 공간, 1은 마지막
    
    table = []
    # 상단 구분선
    table.append("┌" + "─" * (col_widths['no'] + 2) + "┬" + 
                 "─" * (col_widths['timestamp'] + 2) + "┬" +
                 "─" * (col_widths['severity'] + 2) + "┬" +
                 "─" * (col_widths['message'] + 2) + "┬" +
                 "─" * (col_widths['location'] + 2) + "┬" +
                 "─" * (col_widths['system'] + 2) + "┐")
    
    # 헤더
    header = (f"│ {'번호':<{col_widths['no']}} │ "
              f"{'발생일시':<{col_widths['timestamp']}} │ "
              f"{'심각도':<{col_widths['severity']}} │ "
              f"{'에러사항':<{col_widths['message']}} │ "
              f"{'발생위치':<{col_widths['location']}} │ "
              f"{'시스템':<{col_widths['system']}} │")
    table.append(header)
    
    # 헤더 구분선
    table.append("├" + "─" * (col_widths['no'] + 2) + "┼" + 
                 "─" * (col_widths['timestamp'] + 2) + "┼" +
                 "─" * (col_widths['severity'] + 2) + "┼" +
                 "─" * (col_widths['message'] + 2) + "┼" +
                 "─" * (col_widths['location'] + 2) + "┼" +
                 "─" * (col_widths['system'] + 2) + "┤")
    
    # 데이터 행
    for i, error in enumerate(errors, 1):
        # 타임스탬프 포맷팅 (ISO8601 형식 간소화)
        timestamp = error.get('timestamp', 'N/A')
        if timestamp != 'N/A' and 'T' in timestamp:
            try:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
            except:
                timestamp = timestamp[:19] if len(timestamp) > 19 else timestamp
        
        # 심각도
        severity = error.get('severity', 'N/A')
        if severity not in ['ERROR', 'CRITICAL', 'WARNING']:
            severity = 'ERROR' if 'error' in str(error.get('message', '')).lower() else 'N/A'
        
        # 에러 메시지 (첫 줄만, 길이 제한)
        message = error.get('message', 'N/A')
        if message != 'N/A':
            # 첫 줄만 추출
            message_lines = message.split('\n')
            message = message_lines[0].strip()
            if len(message) > col_widths['message']:
                message = message[:col_widths['message']-3] + '...'
        
        # 발생 위치 (파일:라인 형식)
        location = 'N/A'
        file_path = error.get('file') or error.get('location', '')
        line_num = error.get('line') or ''
        if file_path and file_path != 'N/A':
            if line_num:
                location = f"{file_path}:{line_num}"
            else:
                location = file_path
            # 경로가 너무 길면 파일명만 표시
            if len(location) > col_widths['location']:
                if '/' in location or '\\' in location:
                    parts = location.replace('\\', '/').split('/')
                    if len(parts) > 1:
                        location = '.../' + parts[-1]
                    else:
                        location = location[-col_widths['location']+3:]
                else:
                    location = '...' + location[-(col_widths['location']-3):]
        
        # 시스템 타입
        system = error.get('system_type') or error.get('resource_type') or error.get('service') or 'N/A'
        if system != 'N/A' and len(system) > col_widths['system']:
            system = system[:col_widths['system']-3] + '...'
        
        # 행 추가
        row = (f"│ {str(i):<{col_widths['no']}} │ "
               f"{timestamp:<{col_widths['timestamp']}} │ "
               f"{severity:<{col_widths['severity']}} │ "
               f"{message:<{col_widths['message']}} │ "
               f"{location:<{col_widths['location']}} │ "
               f"{system:<{col_widths['system']}} │")
        table.append(row)
    
    # 하단 구분선
    table.append("└" + "─" * (col_widths['no'] + 2) + "┴" + 
                 "─" * (col_widths['timestamp'] + 2) + "┴" +
                 "─" * (col_widths['severity'] + 2) + "┴" +
                 "─" * (col_widths['message'] + 2) + "┴" +
                 "─" * (col_widths['location'] + 2) + "┴" +
                 "─" * (col_widths['system'] + 2) + "┘")
    
    return "\n".join(table)

def format_analysis_table(analysis_results: List[Dict[str, Any]]) -> str:
    """에러 분석 결과를 테이블 형태로 포맷팅"""
    if not analysis_results:
        return "분석 결과가 없습니다."
    
    # 컬럼 너비 정의
    col_widths = {
        'no': 6,
        'error_type': 18,
        'error_content': 55,
        'keywords': 30
    }
    
    table = []
    # 상단 구분선
    table.append("┌" + "─" * (col_widths['no'] + 2) + "┬" + 
                 "─" * (col_widths['error_type'] + 2) + "┬" +
                 "─" * (col_widths['error_content'] + 2) + "┬" +
                 "─" * (col_widths['keywords'] + 2) + "┐")
    
    # 헤더
    header = (f"│ {'번호':<{col_widths['no']}} │ "
              f"{'에러타입':<{col_widths['error_type']}} │ "
              f"{'에러내용':<{col_widths['error_content']}} │ "
              f"{'매칭키워드':<{col_widths['keywords']}} │")
    table.append(header)
    
    # 헤더 구분선
    table.append("├" + "─" * (col_widths['no'] + 2) + "┼" + 
                 "─" * (col_widths['error_type'] + 2) + "┼" +
                 "─" * (col_widths['error_content'] + 2) + "┼" +
                 "─" * (col_widths['keywords'] + 2) + "┤")
    
    # 데이터 행
    for i, result in enumerate(analysis_results, 1):
        error_type = result.get('error_type', 'unknown')
        if len(error_type) > col_widths['error_type']:
            error_type = error_type[:col_widths['error_type']-3] + '...'
        
        error_content = result.get('error_message', 'N/A')
        if error_content != 'N/A':
            # 첫 줄만 추출
            error_lines = error_content.split('\n')
            error_content = error_lines[0].strip()
            if len(error_content) > col_widths['error_content']:
                error_content = error_content[:col_widths['error_content']-3] + '...'
        
        keywords = ', '.join(result.get('matched_keywords', [])[:5])
        if len(keywords) > col_widths['keywords']:
            keywords = keywords[:col_widths['keywords']-3] + '...'
        if not keywords:
            keywords = 'N/A'
        
        row = (f"│ {str(i):<{col_widths['no']}} │ "
               f"{error_type:<{col_widths['error_type']}} │ "
               f"{error_content:<{col_widths['error_content']}} │ "
               f"{keywords:<{col_widths['keywords']}} │")
        table.append(row)
    
    # 하단 구분선
    table.append("└" + "─" * (col_widths['no'] + 2) + "┴" + 
                 "─" * (col_widths['error_type'] + 2) + "┴" +
                 "─" * (col_widths['error_content'] + 2) + "┴" +
                 "─" * (col_widths['keywords'] + 2) + "┘")
    
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
            log_content = arguments.get("log_content")  # 직접 입력된 로그
            workspace_path = arguments.get("workspace_path", os.getcwd())
            
            # 로그 파일 찾기 또는 직접 입력된 로그 사용
            if log_content:
                # 직접 입력된 로그 사용
                log_files = [None]  # 파일 경로 없음 표시
                log_contents = {None: log_content}
            elif log_file_path:
                if not os.path.exists(log_file_path):
                    return [TextContent(
                        type="text",
                        text=f"오류: 로그 파일을 찾을 수 없습니다: {log_file_path}"
                    )]
                log_files = [log_file_path]
                log_contents = {}
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
                log_contents = {}
            
            result_parts = []
            workspace_searcher = WorkspaceSearcher(workspace_path)
            
            # 각 로그 파일 분석
            for log_file in log_files[:5]:  # 최대 5개 파일만 분석
                try:
                    # 로그 내용 가져오기
                    if log_file is None:
                        # 직접 입력된 로그
                        log_content = log_contents[None]
                        log_source = "직접 입력된 로그"
                    else:
                        # 파일에서 읽기
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                        log_source = log_file
                    
                    if not log_content.strip():
                        continue
                    
                    # 로그 파싱
                    parser = LogParser(log_content)
                    errors = parser.parse_errors()
                    
                    if not errors:
                        continue
                    
                    # 에러 분석기로 각 에러 분석
                    analyzer = ErrorAnalyzer()
                    for error in errors:
                        error_msg = error.get('message', '')
                        analysis = analyzer.analyze_error(error_msg)
                        error['error_type'] = analysis['error_type']
                        error['error_category'] = ', '.join(analysis['matched_keywords']) if analysis['matched_keywords'] else None
                        error['analysis'] = analysis
                    
                    # 최신순 정렬 (타임스탬프 기준)
                    errors.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
                    
                    # JSON 형식 결과도 생성 (API에서 사용)
                    json_result = {
                        'log_source': log_source,
                        'log_type': parser.log_type,
                        'errors': errors,
                        'error_count': len(errors)
                    }
                    
                    result_parts.append(f"\n{'='*120}")
                    result_parts.append(f"📁 로그 소스: {log_source}")
                    result_parts.append(f"📊 로그 타입: {parser.log_type.upper()}")
                    result_parts.append(f"{'='*120}\n")
                    
                    # 1. 에러 목록 테이블 (최신순)
                    result_parts.append("## 1. 에러 로그 요약 (테이블) - 최신순")
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
                    
                    # 3. 워크스페이스에서 발생 위치 찾기
                    result_parts.append("\n## 3. 워크스페이스에서 발생 위치 검색")
                    all_locations = {
                        'files': [],
                        'functions': [],
                        'code_snippets': [],
                        'suggestions': []
                    }
                    
                    for error in errors:
                        error_msg = error.get('message', '')
                        locations = workspace_searcher.find_error_location(error_msg)
                        
                        # 파일 정보 병합
                        for file_info in locations['files']:
                            if file_info not in all_locations['files']:
                                all_locations['files'].append(file_info)
                        
                        # 함수 정보 병합
                        for func_info in locations['functions']:
                            if func_info not in all_locations['functions']:
                                all_locations['functions'].append(func_info)
                    
                    if all_locations['files'] or all_locations['functions']:
                        if all_locations['files']:
                            result_parts.append("\n### 발견된 파일:")
                            for file_info in all_locations['files'][:10]:  # 최대 10개
                                rel_path = file_info['relative_path']
                                if file_info['line']:
                                    result_parts.append(f"- **{rel_path}:{file_info['line']}**")
                                    if file_info.get('code_snippet'):
                                        result_parts.append("```")
                                        result_parts.append(file_info['code_snippet'])
                                        result_parts.append("```")
                                else:
                                    result_parts.append(f"- **{rel_path}**")
                        
                        if all_locations['functions']:
                            result_parts.append("\n### 발견된 함수/클래스:")
                            for func_info in all_locations['functions'][:10]:  # 최대 10개
                                result_parts.append(f"- **{func_info['relative_path']}:{func_info['line']}**")
                                if func_info.get('code_snippet'):
                                    result_parts.append("```")
                                    result_parts.append(func_info['code_snippet'])
                                    result_parts.append("```")
                    else:
                        result_parts.append("\n워크스페이스에서 관련 파일이나 함수를 찾을 수 없습니다.")
                    
                    # 4. 상세 에러 내역
                    result_parts.append("\n## 4. 상세 에러 내역")
                    for i, error in enumerate(errors, 1):
                        result_parts.append(f"\n### 에러 #{i}")
                        result_parts.append(f"- **발생일시**: {error.get('timestamp', 'N/A')}")
                        result_parts.append(f"- **심각도**: {error.get('severity', 'N/A')}")
                        result_parts.append(f"- **에러사항**: {error.get('message', 'N/A')}")
                        result_parts.append(f"- **발생위치**: {error.get('location', error.get('file', 'N/A'))}")
                        result_parts.append(f"- **관련프로그램**: {error.get('service', error.get('resource_type', 'N/A'))}")
                        if error.get('line'):
                            result_parts.append(f"- **라인번호**: {error.get('line')}")
                        
                        # 각 에러에 대한 워크스페이스 검색 결과
                        error_msg = error.get('message', '')
                        error_locations = workspace_searcher.find_error_location(error_msg)
                        if error_locations['files'] or error_locations['functions']:
                            result_parts.append(f"\n**워크스페이스 검색 결과:**")
                            if error_locations['files']:
                                for file_info in error_locations['files'][:3]:
                                    rel_path = file_info['relative_path']
                                    if file_info['line']:
                                        result_parts.append(f"  - 파일: {rel_path}:{file_info['line']}")
                                    else:
                                        result_parts.append(f"  - 파일: {rel_path}")
                            if error_locations['functions']:
                                for func_info in error_locations['functions'][:3]:
                                    result_parts.append(f"  - 함수/클래스: {func_info['relative_path']}:{func_info['line']}")
                    
                    # 5. 조치 방법
                    result_parts.append("\n## 5. 조치 방법")
                    unique_analyses = {}
                    for analysis in analysis_results:
                        error_type = analysis['error_type']
                        if error_type not in unique_analyses:
                            unique_analyses[error_type] = analysis
                    
                    for error_type, analysis in unique_analyses.items():
                        result_parts.append(f"\n### {error_type.upper()} 타입 에러 조치 방법:")
                        for j, solution in enumerate(analysis['solutions'], 1):
                            result_parts.append(f"{j}. {solution}")
                    
                    # 6. 수정 가이드
                    result_parts.append("\n## 6. 수정 가이드")
                    if all_locations['files'] or all_locations['functions']:
                        result_parts.append("\n### 발견된 위치에서 수정해야 할 사항:")
                        suggestions = workspace_searcher._generate_suggestions("", all_locations)
                        for suggestion in suggestions:
                            result_parts.append(f"- {suggestion}")
                        
                        result_parts.append("\n### 수정 단계:")
                        result_parts.append("1. 위에서 발견된 파일을 열어 해당 라인을 확인하세요.")
                        result_parts.append("2. 에러 메시지와 코드를 비교하여 문제점을 파악하세요.")
                        result_parts.append("3. 조치 방법 섹션의 제안을 참고하여 수정하세요.")
                        result_parts.append("4. 수정 후 테스트하여 에러가 해결되었는지 확인하세요.")
                    else:
                        result_parts.append("\n워크스페이스에서 관련 코드를 찾을 수 없습니다.")
                        result_parts.append("에러 메시지를 자세히 검토하여 수동으로 문제를 해결해야 합니다.")
                    
                    # 7. 재발 방지책
                    result_parts.append("\n## 7. 재발 방지책")
                    for error_type, analysis in unique_analyses.items():
                        result_parts.append(f"\n### {error_type.upper()} 타입 에러 재발 방지책:")
                        for j, prevention in enumerate(analysis['prevention'], 1):
                            result_parts.append(f"{j}. {prevention}")
                    
                except Exception as e:
                    result_parts.append(f"\n⚠️ 로그 분석 중 오류 발생 ({log_source if 'log_source' in locals() else log_file}): {str(e)}")
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

def run_direct_analysis(log_file_path: Optional[str] = None, workspace_path: Optional[str] = None, log_content: Optional[str] = None):
    """
    명령줄에서 직접 실행하는 함수
    """
    workspace = workspace_path or os.getcwd()
    
    # 로그 파일 찾기 또는 직접 입력된 로그 사용
    if log_content:
        # 직접 입력된 로그 사용
        log_files = [None]
        log_contents = {None: log_content}
    elif log_file_path:
        if not os.path.exists(log_file_path):
            print(f"오류: 로그 파일을 찾을 수 없습니다: {log_file_path}", file=sys.stderr)
            sys.exit(1)
        log_files = [log_file_path]
        log_contents = {}
    else:
        log_files = find_log_files(workspace)
        if not log_files:
            print(f"워크스페이스({workspace})에서 로그 파일을 찾을 수 없습니다.", file=sys.stderr)
            sys.exit(1)
        log_contents = {}
    
    result_parts = []
    workspace_searcher = WorkspaceSearcher(workspace)
    
    # JSON 출력용 결과 저장
    json_results = []
    
    # 각 로그 파일 분석
    for log_file in log_files:
        try:
            # 로그 내용 가져오기
            if log_file is None:
                # 직접 입력된 로그
                log_content = log_contents[None]
                log_source = "직접 입력된 로그"
            else:
                # 파일에서 읽기
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                log_source = log_file
            
            if not log_content.strip():
                continue
            
            # 로그 파싱
            parser = LogParser(log_content)
            errors = parser.parse_errors()
            
            if not errors:
                continue
            
            # JSON 결과에 추가
            for error in errors:
                metadata = parser._extract_metadata(error)
                # 각 에러의 원본 로그 내용 추출
                error_log_content = ''
                if error.get('full_context') and isinstance(error.get('full_context'), list):
                    error_log_content = '\n'.join(error.get('full_context'))
                elif error.get('message'):
                    # 메시지와 타임스탬프를 포함한 로그 라인 생성
                    timestamp = error.get('timestamp', '')
                    severity = error.get('severity', 'ERROR')
                    message = error.get('message', '')
                    error_log_content = f"{timestamp} {severity}: {message}"
                else:
                    # 전체 로그 내용에서 해당 에러 부분 추출 시도
                    error_log_content = log_content.split('\n')[0] if log_content else ''
                
                json_results.append({
                    'log_content': error_log_content,
                    'timestamp': error.get('timestamp', datetime.now().isoformat()),
                    'parsed_data': metadata,
                    'log_type': parser.log_type
                })
            
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
                        result_parts.append(f"\n### 🔧 {error_type.upper()} 타입 에러 조치 방법")
                        solutions = analysis['solutions']
                        
                        # 구조화된 solutions인지 확인
                        if solutions and isinstance(solutions[0], dict):
                            # 우선순위별로 정렬
                            sorted_solutions = sorted(solutions, key=lambda x: x.get('priority', 999))
                            for solution in sorted_solutions:
                                result_parts.append(f"\n#### {solution.get('title', '조치 방법')}")
                                result_parts.append(f"**설명**: {solution.get('description', '')}")
                                
                                if solution.get('steps'):
                                    result_parts.append("\n**단계별 가이드**:")
                                    for step in solution['steps']:
                                        result_parts.append(f"  - {step}")
                                
                                if solution.get('code_example'):
                                    result_parts.append("\n**코드 예시**:")
                                    result_parts.append("```javascript")
                                    result_parts.append(solution['code_example'])
                                    result_parts.append("```")
                        else:
                            # 기존 형식 (문자열 리스트)
                            for j, solution in enumerate(solutions, 1):
                                result_parts.append(f"{j}. {solution}")
                    
                    # 5. 재발 방지책
                    result_parts.append("\n## 5. 재발 방지책")
                    for error_type, analysis in unique_analyses.items():
                        result_parts.append(f"\n### 🛡️ {error_type.upper()} 타입 에러 재발 방지책")
                        prevention = analysis['prevention']
                        
                        # 구조화된 prevention인지 확인
                        if prevention and isinstance(prevention[0], dict):
                            for prev in prevention:
                                result_parts.append(f"\n#### {prev.get('title', '재발 방지책')}")
                                result_parts.append(f"**설명**: {prev.get('description', '')}")
                                
                                if prev.get('implementation'):
                                    result_parts.append("\n**구현 예시**:")
                                    result_parts.append("```javascript")
                                    result_parts.append(prev['implementation'])
                                    result_parts.append("```")
                                
                                if prev.get('benefits'):
                                    result_parts.append("\n**기대 효과**:")
                                    for benefit in prev['benefits']:
                                        result_parts.append(f"  ✓ {benefit}")
                        else:
                            # 기존 형식 (문자열 리스트)
                            for j, prev in enumerate(prevention, 1):
                                result_parts.append(f"{j}. {prev}")
            
        except Exception as e:
            result_parts.append(f"\n⚠️ 로그 파일 분석 중 오류 발생 ({log_file}): {str(e)}")
            continue
    
    if not result_parts:
        print("분석할 에러 로그를 찾을 수 없습니다.", file=sys.stderr)
        sys.exit(1)
    
    # JSON 결과가 있으면 먼저 출력 (API 서버에서 사용)
    if json_results:
        try:
            json_output = json.dumps({
                'errors': json_results,
                'count': len(json_results)
            }, ensure_ascii=False, indent=2)
            print(f"<JSON_START>{json_output}<JSON_END>", file=sys.stderr)
        except Exception as e:
            print(f"JSON 출력 오류: {e}", file=sys.stderr)
    
    # 결과 출력 (UTF-8 인코딩 보장)
    try:
        output = "\n".join(result_parts)
        # Windows에서 안전하게 출력
        if sys.platform == 'win32':
            # stdout이 UTF-8로 설정되어 있지 않으면 다시 설정
            if not hasattr(sys.stdout, 'encoding') or sys.stdout.encoding != 'utf-8':
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        print(output)
    except UnicodeEncodeError:
        # 인코딩 오류 발생 시 이모지를 제거하고 출력
        safe_output = "\n".join(result_parts)
        # 이모지 제거 (유니코드 범위)
        safe_output = re.sub(r'[\U0001F300-\U0001F9FF]', '', safe_output)
        safe_output = re.sub(r'[\U00002600-\U000027BF]', '', safe_output)
        safe_output = re.sub(r'[\U0001F600-\U0001F64F]', '', safe_output)
        print(safe_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='에러 로그 분석 도구')
    parser.add_argument('--log-file', type=str, help='분석할 로그 파일 경로')
    parser.add_argument('--log-content', type=str, help='직접 입력된 로그 내용')
    parser.add_argument('--workspace', type=str, help='워크스페이스 경로')
    
    args = parser.parse_args()
    
    # 명령줄 인자가 있으면 직접 실행
    if args.log_file or args.log_content or args.workspace:
        run_direct_analysis(args.log_file, args.workspace, args.log_content)
    else:
        # MCP 서버 모드로 실행
        print("에러 로그 분석 MCP 서버가 시작되었습니다.", file=sys.stderr)
        print("사용 가능한 도구: analyze_error_logs", file=sys.stderr)
        asyncio.run(main())


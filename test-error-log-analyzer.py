#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
에러 로그 분석 MCP 서버 테스트 스크립트
"""

import sys
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Any, List, Dict
from collections import Counter, defaultdict
import json

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# MCP 서버 파일을 직접 읽어서 클래스 정의를 가져옴
# 또는 직접 클래스를 정의

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
    
    # 일반 로그 패턴들 (확장됨)
    COMMON_PATTERNS = [
        {
            'name': 'JSON',
            'detect': lambda content: content.strip().startswith('{') and '"level"' in content.lower(),
            'timestamp': r'"time":\s*"([^"]+)"|"timestamp":\s*"([^"]+)"|"@timestamp":\s*"([^"]+)"',
            'level': r'"level":\s*"([^"]+)"|"severity":\s*"([^"]+)"|"log_level":\s*"([^"]+)"',
            'message': r'"message":\s*"([^"]+)"|"msg":\s*"([^"]+)"|"error":\s*"([^"]+)"',
            'file': r'"file":\s*"([^"]+)"|"filename":\s*"([^"]+)"',
            'line': r'"line":\s*(\d+)|"lineno":\s*(\d+)',
            'service': r'"service":\s*"([^"]+)"|"serviceName":\s*"([^"]+)"|"app":\s*"([^"]+)"'
        },
        {
            'name': 'Docker',
            'detect': lambda content: re.search(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z\s+', content, re.MULTILINE),
            'timestamp': r'^(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+Z)',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL|INFO|DEBUG)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:\s*(.+?)(?=\n\d{4}|\Z)'
        },
        {
            'name': 'Kubernetes',
            'detect': lambda content: 'kubernetes' in content.lower() or 'k8s' in content.lower() or re.search(r'pod|namespace|container', content, re.IGNORECASE),
            'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d\.]*Z?)',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL|INFO|DEBUG)',
            'pod': r'pod[=:]\s*([^\s,]+)',
            'namespace': r'namespace[=:]\s*([^\s,]+)',
            'container': r'container[=:]\s*([^\s,]+)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:\s*(.+?)(?=\n|\Z)'
        },
        {
            'name': 'Nginx',
            'detect': lambda content: re.search(r'nginx|GET|POST|PUT|DELETE|HTTP/\d\.\d', content, re.IGNORECASE),
            'timestamp': r'\[(\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}\s+[+\-]\d{4})\]',
            'level': r'(error|warn|crit|alert|emerg)',
            'status': r'HTTP/\d\.\d"\s+(\d{3})',
            'method': r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)',
            'url': r'(GET|POST|PUT|DELETE|PATCH|HEAD|OPTIONS)\s+([^\s]+)',
            'message': r'error.*?:\s*(.+?)(?=\n|\Z)'
        },
        {
            'name': 'Apache',
            'detect': lambda content: re.search(r'apache|\[.*\]\s+\[.*\]\s+\[.*\]', content, re.IGNORECASE),
            'timestamp': r'\[(\w{3}\s+\d{2}\s+\d{2}:\d{2}:\d{2}\.\d+\s+\d{4})\]',
            'level': r'\[(error|warn|crit|alert|emerg)\]',
            'status': r'HTTP/\d\.\d"\s+(\d{3})',
            'message': r'\[error\].*?:\s*(.+?)(?=\n|\Z)'
        },
        {
            'name': 'PythonTraceback',
            'detect': lambda content: 'Traceback (most recent call last)' in content or 'File "' in content,
            'timestamp': None,  # 스택 트레이스에는 타임스탬프가 없을 수 있음
            'level': r'(ERROR|Exception|Error|Warning)',
            'file': r'File\s+"([^"]+)"',
            'line': r'line\s+(\d+)',
            'exception': r'(\w+Error|\w+Exception):\s*(.+?)(?=\n|\Z)',
            'message': r'Traceback.*?(?=\n\n|\Z)'
        },
        {
            'name': 'NodeJS',
            'detect': lambda content: re.search(r'Error:|at\s+\w+.*\(.*:\d+:\d+\)|node_modules', content),
            'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d\.]*Z?)',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL)',
            'file': r'at\s+.*?\(([^:]+):(\d+):(\d+)\)',
            'message': r'Error:\s*(.+?)(?=\n\s+at|\Z)'
        },
        {
            'name': 'JavaStackTrace',
            'detect': lambda content: re.search(r'Exception|Error|at\s+\w+\.\w+\.\w+\(.*\.java:\d+\)', content),
            'timestamp': r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            'level': r'(ERROR|WARN|FATAL|SEVERE)',
            'exception': r'(\w+Exception|\w+Error):\s*(.+?)(?=\n\s+at|\Z)',
            'file': r'at\s+\w+\.\w+\.\w+\(([^:]+\.java):(\d+)\)',
            'message': r'(?:Exception|Error).*?(?=\n\n|\Z)'
        },
        {
            'name': 'Winston',
            'detect': lambda content: re.search(r'"level":"(error|warn)"', content),
            'timestamp': r'"timestamp":\s*"([^"]+)"',
            'level': r'"level":\s*"([^"]+)"',
            'message': r'"message":\s*"([^"]+)"',
            'file': r'"filename":\s*"([^"]+)"',
            'line': r'"line":\s*(\d+)'
        },
        {
            'name': 'Bunyan',
            'detect': lambda content: re.search(r'"v":\d+.*"level":\d+', content),
            'timestamp': r'"time":\s*"([^"]+)"',
            'level': r'"level":\s*(\d+)',  # Bunyan은 숫자 레벨 사용
            'message': r'"msg":\s*"([^"]+)"',
            'file': r'"src":\s*\{[^}]*"file":\s*"([^"]+)"',
            'line': r'"src":\s*\{[^}]*"line":\s*(\d+)'
        },
        {
            'name': 'Log4j',
            'detect': lambda content: re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3}', content),
            'timestamp': r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2},\d{3})',
            'level': r'\s+(ERROR|WARN|FATAL|INFO|DEBUG)\s+',
            'class': r'\[([^\]]+)\]',
            'message': r'(?:ERROR|WARN|FATAL).*?-\s*(.+?)(?=\n\d{4}|\Z)'
        },
        {
            'name': 'Syslog',
            'detect': lambda content: re.search(r'^\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2}', content, re.MULTILINE),
            'timestamp': r'^(\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})',
            'hostname': r'(\S+)\s+(?:kernel|systemd|daemon)',
            'level': r'(error|err|warning|warn|crit|alert|emerg)',
            'message': r'(?:error|err|warning|warn|crit|alert|emerg).*?:\s*(.+?)(?=\n\w{3}|\Z)'
        },
        {
            'name': 'ISO8601',
            'detect': lambda content: re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d\.]*[Z\+\-:]*\d*', content),
            'timestamp': r'(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}[\d\.]*[Z\+\-:]*\d*)',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL|INFO|DEBUG)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:(.+?)(?=\n|\Z)'
        },
        {
            'name': 'Standard',
            'detect': lambda content: re.search(r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', content),
            'timestamp': r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL|INFO|DEBUG)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:(.+?)(?=\n|\Z)'
        },
        {
            'name': 'Simple',
            'detect': lambda content: re.search(r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2}', content),
            'timestamp': r'(\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}:\d{2})',
            'level': r'(ERROR|WARN|WARNING|CRITICAL|FATAL)',
            'message': r'(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*?:(.+?)(?=\n|\Z)'
        }
    ]
    
    def __init__(self, log_content: str):
        self.log_content = log_content
        self.log_type = self._detect_log_type()
    
    def _detect_log_type(self) -> str:
        """로그 타입을 자동 감지 (우선순위 순)"""
        # GCP 로그 감지
        if 'resource.type' in self.log_content or 'serviceName' in self.log_content:
            return 'gcp'
        
        # 각 패턴의 detect 함수로 확인
        for pattern in self.COMMON_PATTERNS:
            if 'detect' in pattern and pattern['detect'](self.log_content):
                return pattern['name'].lower()
        
        # 타임스탬프 패턴으로 폴백
        for pattern in self.COMMON_PATTERNS:
            if pattern.get('timestamp') and re.search(pattern['timestamp'], self.log_content):
                return pattern['name'].lower()
        
        return 'unknown'
    
    def parse_errors(self) -> List[Dict[str, Any]]:
        """에러 로그를 파싱하여 구조화된 데이터로 반환"""
        errors = []
        
        if self.log_type == 'gcp':
            errors = self._parse_gcp_logs()
        elif self.log_type == 'json':
            errors = self._parse_json_logs()
        elif self.log_type == 'pythontraceback':
            errors = self._parse_python_traceback()
        elif self.log_type == 'nodejs':
            errors = self._parse_nodejs_logs()
        elif self.log_type == 'javastacktrace':
            errors = self._parse_java_stacktrace()
        elif self.log_type == 'docker':
            errors = self._parse_docker_logs()
        elif self.log_type == 'kubernetes':
            errors = self._parse_kubernetes_logs()
        elif self.log_type == 'nginx':
            errors = self._parse_nginx_logs()
        elif self.log_type == 'apache':
            errors = self._parse_apache_logs()
        elif self.log_type == 'winston':
            errors = self._parse_winston_logs()
        elif self.log_type == 'bunyan':
            errors = self._parse_bunyan_logs()
        elif self.log_type == 'log4j':
            errors = self._parse_log4j_logs()
        elif self.log_type == 'syslog':
            errors = self._parse_syslog_logs()
        else:
            errors = self._parse_common_logs()
        
        return errors
    
    def _parse_gcp_logs(self) -> List[Dict[str, Any]]:
        """GCP 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        current_error = {}
        for line in lines:
            timestamp_match = re.search(self.GCP_PATTERNS['timestamp'], line)
            if timestamp_match:
                current_error['timestamp'] = timestamp_match.group(1)
            
            severity_match = re.search(self.GCP_PATTERNS['severity'], line)
            if severity_match and severity_match.group(1) in ['ERROR', 'CRITICAL']:
                current_error['severity'] = severity_match.group(1)
            
            resource_match = re.search(self.GCP_PATTERNS['resource'], line)
            if resource_match:
                current_error['resource_type'] = resource_match.group(1)
            
            location_match = re.search(self.GCP_PATTERNS['location'], line)
            if location_match:
                current_error['location'] = location_match.group(1)
            
            service_match = re.search(self.GCP_PATTERNS['service'], line)
            if service_match:
                current_error['service'] = service_match.group(1)
            
            message_match = re.search(self.GCP_PATTERNS['message'], line)
            if message_match:
                current_error['message'] = message_match.group(1) or message_match.group(2)
            
            if 'message' in current_error and ('severity' in current_error or 'ERROR' in line or 'CRITICAL' in line):
                if not current_error.get('timestamp'):
                    current_error['timestamp'] = datetime.now().isoformat()
                errors.append(current_error.copy())
                current_error = {}
        
        return errors
    
    def _parse_json_logs(self) -> List[Dict[str, Any]]:
        """JSON 형식 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('{'):
                continue
            
            try:
                log_entry = json.loads(line)
                
                # 레벨 확인
                level = (log_entry.get('level') or log_entry.get('severity') or 
                        log_entry.get('log_level') or '').upper()
                
                if level in ['ERROR', 'WARN', 'WARNING', 'CRITICAL', 'FATAL']:
                    error = {
                        'timestamp': (log_entry.get('time') or log_entry.get('timestamp') or 
                                    log_entry.get('@timestamp') or datetime.now().isoformat()),
                        'severity': level,
                        'message': (log_entry.get('message') or log_entry.get('msg') or 
                                  log_entry.get('error') or str(log_entry)),
                        'full_context': [line]
                    }
                    
                    # 추가 필드 추출
                    if log_entry.get('file') or log_entry.get('filename'):
                        error['file'] = log_entry.get('file') or log_entry.get('filename')
                    if log_entry.get('line') or log_entry.get('lineno'):
                        error['line'] = str(log_entry.get('line') or log_entry.get('lineno'))
                    if log_entry.get('service') or log_entry.get('serviceName') or log_entry.get('app'):
                        error['service'] = (log_entry.get('service') or 
                                          log_entry.get('serviceName') or 
                                          log_entry.get('app'))
                    if log_entry.get('error_code'):
                        error['error_code'] = str(log_entry['error_code'])
                    if log_entry.get('stack'):
                        error['stack_trace'] = log_entry['stack']
                    
                    self._extract_detailed_info(error, error['message'])
                    errors.append(error)
            except json.JSONDecodeError:
                continue
        
        return errors
    
    def _parse_docker_logs(self) -> List[Dict[str, Any]]:
        """Docker 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Docker 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Docker'), None)
        if not pattern:
            return errors
        i = 0
        while i < len(lines):
            line = lines[i]
            timestamp_match = re.search(pattern['timestamp'], line)
            level_match = re.search(pattern['level'], line, re.IGNORECASE)
            
            if timestamp_match and level_match and level_match.group(1).upper() in ['ERROR', 'WARN', 'WARNING', 'CRITICAL', 'FATAL']:
                error = {
                    'timestamp': timestamp_match.group(1),
                    'severity': level_match.group(1).upper(),
                    'message': '',
                    'full_context': []
                }
                
                # 메시지 추출
                message_lines = []
                j = i
                while j < len(lines):
                    current_line = lines[j]
                    if j > i and re.search(pattern['timestamp'], current_line):
                        break
                    message_lines.append(current_line)
                    j += 1
                
                full_message = '\n'.join(message_lines)
                error['message'] = full_message
                error['full_context'] = message_lines
                
                # 컨테이너 정보 추출
                container_match = re.search(r'container[=:]\s*([^\s,]+)', full_message, re.IGNORECASE)
                if container_match:
                    error['container'] = container_match.group(1)
                
                self._extract_detailed_info(error, full_message)
                errors.append(error)
                i = j
            else:
                i += 1
        
        return errors
    
    def _parse_kubernetes_logs(self) -> List[Dict[str, Any]]:
        """Kubernetes 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Kubernetes 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Kubernetes'), None)
        if not pattern:
            return errors
        
        for line in lines:
            level_match = re.search(pattern['level'], line, re.IGNORECASE)
            if level_match and level_match.group(1).upper() in ['ERROR', 'WARN', 'WARNING', 'CRITICAL', 'FATAL']:
                error = {
                    'severity': level_match.group(1).upper(),
                    'message': line,
                    'full_context': [line]
                }
                
                # 타임스탬프
                timestamp_match = re.search(pattern['timestamp'], line)
                if timestamp_match:
                    error['timestamp'] = timestamp_match.group(1)
                else:
                    error['timestamp'] = datetime.now().isoformat()
                
                # Kubernetes 특정 정보 추출
                pod_match = re.search(pattern['pod'], line, re.IGNORECASE)
                if pod_match:
                    error['pod'] = pod_match.group(1)
                
                namespace_match = re.search(pattern['namespace'], line, re.IGNORECASE)
                if namespace_match:
                    error['namespace'] = namespace_match.group(1)
                
                container_match = re.search(pattern['container'], line, re.IGNORECASE)
                if container_match:
                    error['container'] = container_match.group(1)
                
                message_match = re.search(pattern['message'], line, re.IGNORECASE)
                if message_match:
                    error['message'] = message_match.group(1)
                
                self._extract_detailed_info(error, line)
                errors.append(error)
        
        return errors
    
    def _parse_nginx_logs(self) -> List[Dict[str, Any]]:
        """Nginx 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Nginx 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Nginx'), None)
        if not pattern:
            return errors
        
        for line in lines:
            level_match = re.search(pattern['level'], line, re.IGNORECASE)
            if level_match and level_match.group(1).lower() in ['error', 'crit', 'alert', 'emerg']:
                error = {
                    'severity': level_match.group(1).upper(),
                    'message': line,
                    'full_context': [line]
                }
                
                # 타임스탬프
                timestamp_match = re.search(pattern['timestamp'], line)
                if timestamp_match:
                    error['timestamp'] = timestamp_match.group(1)
                else:
                    error['timestamp'] = datetime.now().isoformat()
                
                # HTTP 상태 코드
                status_match = re.search(pattern['status'], line)
                if status_match:
                    status_code = int(status_match.group(1))
                    error['http_status'] = str(status_code)
                    if status_code >= 500:
                        error['severity'] = 'ERROR'
                    elif status_code >= 400:
                        error['severity'] = 'WARNING'
                
                # HTTP 메서드 및 URL
                url_match = re.search(pattern['url'], line)
                if url_match:
                    error['http_method'] = url_match.group(1)
                    error['url'] = url_match.group(2)
                
                message_match = re.search(pattern['message'], line, re.IGNORECASE)
                if message_match:
                    error['message'] = message_match.group(1)
                
                self._extract_detailed_info(error, line)
                errors.append(error)
        
        return errors
    
    def _parse_apache_logs(self) -> List[Dict[str, Any]]:
        """Apache 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Apache 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Apache'), None)
        if not pattern:
            return errors
        
        for line in lines:
            level_match = re.search(pattern['level'], line, re.IGNORECASE)
            if level_match and level_match.group(1).lower() in ['error', 'crit', 'alert', 'emerg']:
                error = {
                    'severity': level_match.group(1).upper(),
                    'message': line,
                    'full_context': [line]
                }
                
                # 타임스탬프
                timestamp_match = re.search(pattern['timestamp'], line)
                if timestamp_match:
                    error['timestamp'] = timestamp_match.group(1)
                else:
                    error['timestamp'] = datetime.now().isoformat()
                
                # HTTP 상태 코드
                status_match = re.search(pattern['status'], line)
                if status_match:
                    status_code = int(status_match.group(1))
                    error['http_status'] = str(status_code)
                
                # 클래스/모듈 정보
                class_match = re.search(pattern['class'], line)
                if class_match:
                    error['module'] = class_match.group(1)
                
                message_match = re.search(pattern['message'], line, re.IGNORECASE)
                if message_match:
                    error['message'] = message_match.group(1)
                
                self._extract_detailed_info(error, line)
                errors.append(error)
        
        return errors
    
    def _parse_python_traceback(self) -> List[Dict[str, Any]]:
        """Python 스택 트레이스 파싱"""
        errors = []
        content = self.log_content
        
        # 스택 트레이스 블록 찾기
        traceback_blocks = re.split(r'\n(?=Traceback)', content)
        
        for block in traceback_blocks:
            if 'Traceback' not in block:
                continue
            
            error = {
                'severity': 'ERROR',
                'message': block,
                'full_context': block.split('\n'),
                'stack_trace': block
            }
            
            # 타임스탬프 찾기 (스택 트레이스 전후)
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}[T\s]\d{2}:\d{2}:\d{2})', block)
            if timestamp_match:
                error['timestamp'] = timestamp_match.group(1)
            else:
                error['timestamp'] = datetime.now().isoformat()
            
            # 파일 및 라인 추출
            file_matches = re.findall(r'File\s+"([^"]+)",\s+line\s+(\d+)', block)
            if file_matches:
                error['file'] = file_matches[-1][0]  # 마지막 파일 (에러 발생 위치)
                error['line'] = file_matches[-1][1]
                error['call_stack'] = [{'file': f[0], 'line': f[1]} for f in file_matches]
            
            # 예외 타입 및 메시지 추출
            exception_match = re.search(r'(\w+Error|\w+Exception):\s*(.+?)(?=\n|$)', block)
            if exception_match:
                error['exception_type'] = exception_match.group(1)
                error['exception_message'] = exception_match.group(2)
                error['message'] = f"{exception_match.group(1)}: {exception_match.group(2)}"
            
            self._extract_detailed_info(error, block)
            errors.append(error)
        
        return errors
    
    def _parse_nodejs_logs(self) -> List[Dict[str, Any]]:
        """Node.js 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # NodeJS 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'NodeJS'), None)
        if not pattern:
            return errors
        
        i = 0
        while i < len(lines):
            line = lines[i]
            
            # Error: 로 시작하는 라인 찾기
            if re.search(r'Error:', line, re.IGNORECASE):
                error = {
                    'severity': 'ERROR',
                    'message': '',
                    'full_context': [],
                    'stack_trace': []
                }
                
                # 타임스탬프
                timestamp_match = re.search(pattern['timestamp'], line)
                if timestamp_match:
                    error['timestamp'] = timestamp_match.group(1)
                else:
                    error['timestamp'] = datetime.now().isoformat()
                
                # 에러 메시지 추출
                message_match = re.search(pattern['message'], line)
                if message_match:
                    error['message'] = message_match.group(1)
                
                # 스택 트레이스 수집
                stack_lines = [line]
                j = i + 1
                while j < len(lines) and re.search(r'^\s+at\s+', lines[j]):
                    stack_lines.append(lines[j])
                    # 파일 및 라인 추출
                    file_match = re.search(pattern['file'], lines[j])
                    if file_match:
                        if not error.get('file'):
                            error['file'] = file_match.group(1)
                            error['line'] = file_match.group(2)
                    j += 1
                
                error['full_context'] = stack_lines
                error['stack_trace'] = '\n'.join(stack_lines)
                
                self._extract_detailed_info(error, '\n'.join(stack_lines))
                errors.append(error)
                i = j
            else:
                i += 1
        
        return errors
    
    def _parse_java_stacktrace(self) -> List[Dict[str, Any]]:
        """Java 스택 트레이스 파싱"""
        errors = []
        content = self.log_content
        
        # 예외 블록 찾기
        exception_blocks = re.split(r'\n(?=\w+Exception|\w+Error)', content)
        
        for block in exception_blocks:
            if not re.search(r'Exception|Error', block):
                continue
            
            error = {
                'severity': 'ERROR',
                'message': block,
                'full_context': block.split('\n'),
                'stack_trace': block
            }
            
            # 타임스탬프
            timestamp_match = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})', block)
            if timestamp_match:
                error['timestamp'] = timestamp_match.group(1)
            else:
                error['timestamp'] = datetime.now().isoformat()
            
            # 예외 타입 및 메시지
            # JavaStackTrace 패턴 찾기
            java_pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'JavaStackTrace'), None)
            if java_pattern and java_pattern.get('exception'):
                exception_match = re.search(java_pattern['exception'], block)
            else:
                exception_match = None
            if exception_match:
                error['exception_type'] = exception_match.group(1)
                error['exception_message'] = exception_match.group(2)
                error['message'] = f"{exception_match.group(1)}: {exception_match.group(2)}"
            
            # 파일 및 라인 추출
            if java_pattern and java_pattern.get('file'):
                file_matches = re.findall(java_pattern['file'], block)
            else:
                file_matches = []
            if file_matches:
                error['file'] = file_matches[-1][0]
                error['line'] = file_matches[-1][1]
                error['call_stack'] = [{'file': f[0], 'line': f[1]} for f in file_matches]
            
            self._extract_detailed_info(error, block)
            errors.append(error)
        
        return errors
    
    def _parse_winston_logs(self) -> List[Dict[str, Any]]:
        """Winston 로그 파싱"""
        return self._parse_json_logs()  # Winston은 JSON 형식
    
    def _parse_bunyan_logs(self) -> List[Dict[str, Any]]:
        """Bunyan 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Bunyan 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Bunyan'), None)
        if not pattern:
            return errors
        
        for line in lines:
            line = line.strip()
            if not line or not line.startswith('{'):
                continue
            
            try:
                log_entry = json.loads(line)
                
                # Bunyan 레벨: 10=TRACE, 20=DEBUG, 30=INFO, 40=WARN, 50=ERROR, 60=FATAL
                level_num = log_entry.get('level', 0)
                if level_num >= 50:  # ERROR or FATAL
                    error = {
                        'timestamp': log_entry.get('time', datetime.now().isoformat()),
                        'severity': 'ERROR' if level_num == 50 else 'FATAL',
                        'message': log_entry.get('msg', str(log_entry)),
                        'full_context': [line]
                    }
                    
                    # 소스 정보 추출
                    src = log_entry.get('src', {})
                    if isinstance(src, dict):
                        if src.get('file'):
                            error['file'] = src['file']
                        if src.get('line'):
                            error['line'] = str(src['line'])
                    
                    self._extract_detailed_info(error, error['message'])
                    errors.append(error)
            except json.JSONDecodeError:
                continue
        
        return errors
    
    def _parse_log4j_logs(self) -> List[Dict[str, Any]]:
        """Log4j 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Log4j 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Log4j'), None)
        if not pattern:
            return errors
        
        for line in lines:
            level_match = re.search(pattern['level'], line)
            if level_match and level_match.group(1) in ['ERROR', 'WARN', 'FATAL']:
                error = {
                    'severity': level_match.group(1),
                    'message': line,
                    'full_context': [line]
                }
                
                # 타임스탬프
                timestamp_match = re.search(pattern['timestamp'], line)
                if timestamp_match:
                    error['timestamp'] = timestamp_match.group(1)
                else:
                    error['timestamp'] = datetime.now().isoformat()
                
                # 클래스 정보
                class_match = re.search(pattern['class'], line)
                if class_match:
                    error['class'] = class_match.group(1)
                
                # 메시지 추출
                message_match = re.search(pattern['message'], line)
                if message_match:
                    error['message'] = message_match.group(1)
                
                self._extract_detailed_info(error, line)
                errors.append(error)
        
        return errors
    
    def _parse_syslog_logs(self) -> List[Dict[str, Any]]:
        """Syslog 형식 로그 파싱"""
        errors = []
        lines = self.log_content.split('\n')
        
        # Syslog 패턴 찾기
        pattern = next((p for p in self.COMMON_PATTERNS if p['name'] == 'Syslog'), None)
        if not pattern:
            return errors
        
        for line in lines:
            level_match = re.search(pattern['level'], line, re.IGNORECASE)
            if level_match and level_match.group(1).lower() in ['error', 'err', 'crit', 'alert', 'emerg']:
                error = {
                    'severity': level_match.group(1).upper(),
                    'message': line,
                    'full_context': [line]
                }
                
                # 타임스탬프
                timestamp_match = re.search(pattern['timestamp'], line)
                if timestamp_match:
                    error['timestamp'] = timestamp_match.group(1)
                else:
                    error['timestamp'] = datetime.now().isoformat()
                
                # 호스트명
                hostname_match = re.search(pattern['hostname'], line)
                if hostname_match:
                    error['hostname'] = hostname_match.group(1)
                
                # 메시지 추출
                message_match = re.search(pattern['message'], line, re.IGNORECASE)
                if message_match:
                    error['message'] = message_match.group(1)
                
                self._extract_detailed_info(error, line)
                errors.append(error)
        
        return errors
    
    def _parse_common_logs(self) -> List[Dict[str, Any]]:
        """일반 로그 파싱 - 상세 정보 추출"""
        errors = []
        lines = self.log_content.split('\n')
        
        for pattern in self.COMMON_PATTERNS:
            i = 0
            while i < len(lines):
                line = lines[i]
                timestamp_match = re.search(pattern['timestamp'], line)
                level_match = re.search(pattern['level'], line)
                
                if timestamp_match and level_match and level_match.group(1) in ['ERROR', 'WARN', 'WARNING', 'CRITICAL', 'FATAL']:
                    error = {
                        'timestamp': timestamp_match.group(1),
                        'severity': level_match.group(1),
                        'message': '',
                        'full_context': []
                    }
                    
                    # 메시지 추출 (다음 타임스탬프까지)
                    message_lines = []
                    j = i
                    while j < len(lines):
                        current_line = lines[j]
                        # 다음 타임스탬프가 있으면 중단
                        if j > i and re.search(pattern['timestamp'], current_line):
                            break
                        message_lines.append(current_line)
                        j += 1
                    
                    full_message = '\n'.join(message_lines)
                    error['message'] = full_message
                    error['full_context'] = message_lines
                    
                    # 상세 정보 추출
                    self._extract_detailed_info(error, full_message)
                    
                    errors.append(error)
                    i = j
                else:
                    i += 1
            
            if errors:
                break
        
        if not errors:
            error_lines = re.findall(r'.*?(?:ERROR|WARN|WARNING|CRITICAL|FATAL).*', self.log_content, re.IGNORECASE)
            for i, line in enumerate(error_lines[:50]):
                error = {
                    'timestamp': datetime.now().isoformat(),
                    'severity': 'ERROR',
                    'message': line.strip(),
                    'full_context': [line.strip()]
                }
                self._extract_detailed_info(error, line)
                errors.append(error)
        
        return errors
    
    def _extract_detailed_info(self, error: Dict[str, Any], message: str):
        """에러 메시지에서 상세 정보 추출"""
        # 파일 경로 추출
        file_patterns = [
            r'([/\w\\\-\.]+\.(py|js|ts|java|cpp|c|go|rs|json|yaml|yml))',
            r'File:\s*([/\w\\\-\.]+)',
            r'at\s+([/\w\\\-\.]+\.(py|js|ts))',
            r'in\s+([/\w\\\-\.]+\.(py|js|ts))'
        ]
        for pattern in file_patterns:
            file_match = re.search(pattern, message, re.IGNORECASE)
            if file_match:
                error['file'] = file_match.group(1) if file_match.lastindex >= 1 else file_match.group(0)
                break
        
        # 라인 번호 추출
        line_patterns = [
            r'line\s+(\d+)',
            r':(\d+):',
            r'\(line\s+(\d+)\)',
            r'at\s+line\s+(\d+)'
        ]
        for pattern in line_patterns:
            line_match = re.search(pattern, message, re.IGNORECASE)
            if line_match:
                error['line'] = line_match.group(1)
                break
        
        # 에러 코드 추출
        error_code_match = re.search(r'(?:error|code|errno)[\s:]+([A-Z0-9_]+)', message, re.IGNORECASE)
        if error_code_match:
            error['error_code'] = error_code_match.group(1)
        
        # HTTP 상태 코드 추출
        http_match = re.search(r'(\d{3})\s+(?:Unauthorized|Forbidden|NotFound|Internal|BadRequest)', message, re.IGNORECASE)
        if http_match:
            error['http_status'] = http_match.group(1)
        
        # 타임아웃 값 추출
        timeout_match = re.search(r'timeout[:\s]+(\d+)\s*(?:ms|seconds?|s|milliseconds?)', message, re.IGNORECASE)
        if timeout_match:
            error['timeout_value'] = timeout_match.group(1)
            error['timeout_unit'] = re.search(r'(\d+)\s*(ms|seconds?|s|milliseconds?)', message, re.IGNORECASE).group(2) if re.search(r'(\d+)\s*(ms|seconds?|s|milliseconds?)', message, re.IGNORECASE) else 'ms'
        
        # 메모리 사용량 추출
        memory_match = re.search(r'(\d+)\s*(MB|GB|KB|bytes?)\s*[/]\s*(\d+)\s*(MB|GB|KB|bytes?)', message, re.IGNORECASE)
        if memory_match:
            error['memory_used'] = f"{memory_match.group(1)} {memory_match.group(2)}"
            error['memory_limit'] = f"{memory_match.group(3)} {memory_match.group(4)}"
        
        # URL 추출
        url_match = re.search(r'(https?://[^\s\)]+)', message)
        if url_match:
            error['url'] = url_match.group(1)
        
        # 사용자 ID 추출
        user_match = re.search(r'(?:user|userid|user_id)[\s:]+(\d+|[a-zA-Z0-9_]+)', message, re.IGNORECASE)
        if user_match:
            error['user_id'] = user_match.group(1)
        
        # 프로세스/서비스 이름 추출
        process_match = re.search(r'(?:process|service|app)[\s:]+([a-zA-Z0-9_\-]+)', message, re.IGNORECASE)
        if process_match:
            error['process_name'] = process_match.group(1)
        
        # 연결 문자열 추출 (일부만)
        conn_match = re.search(r'(postgresql|mysql|mongodb)://[^\s\)]+', message, re.IGNORECASE)
        if conn_match:
            conn_str = conn_match.group(0)
            # 보안을 위해 비밀번호 부분 마스킹
            conn_str = re.sub(r':([^:@]+)@', r':****@', conn_str)
            error['connection_string'] = conn_str

class ErrorAnalyzer:
    """에러를 분석하고 조치 방법을 제안하는 클래스"""
    
    def __init__(self):
        self.error_frequency = Counter()
        self.error_patterns = defaultdict(list)
    
    def calculate_severity_score(self, error: Dict[str, Any]) -> int:
        """에러 심각도 점수 계산 (0-100)"""
        score = 0
        
        # 심각도에 따른 기본 점수
        severity = error.get('severity', '').upper()
        if severity == 'CRITICAL' or severity == 'FATAL':
            score += 50
        elif severity == 'ERROR':
            score += 30
        elif severity == 'WARNING' or severity == 'WARN':
            score += 10
        
        # 에러 타입에 따른 점수
        error_type = self._classify_error_type(error.get('message', ''))
        if error_type == 'database':
            score += 20  # 데이터베이스 에러는 높은 우선순위
        elif error_type == 'authentication':
            score += 25  # 인증 에러는 보안 관련
        elif error_type == 'memory':
            score += 15
        elif error_type == 'syntax':
            score += 10
        
        # HTTP 상태 코드에 따른 점수
        if error.get('http_status'):
            status = int(error['http_status'])
            if status >= 500:
                score += 15
            elif status == 401 or status == 403:
                score += 20
        
        return min(score, 100)
    
    def _classify_error_type(self, message: str) -> str:
        """에러 타입 분류"""
        message_lower = message.lower()
        for err_type, pattern_info in self.ERROR_PATTERNS.items():
            for keyword in pattern_info['keywords']:
                if keyword in message_lower:
                    return err_type
        return 'unknown'
    
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
    
    def analyze_error(self, error: Dict[str, Any]) -> Dict[str, Any]:
        """에러를 상세 분석하여 조치 방법과 재발 방지책을 제안"""
        error_message = error.get('message', '')
        error_lower = error_message.lower()
        
        error_type = 'unknown'
        matched_keywords = []
        
        for err_type, pattern_info in self.ERROR_PATTERNS.items():
            for keyword in pattern_info['keywords']:
                if keyword in error_lower:
                    error_type = err_type
                    matched_keywords.append(keyword)
                    break
        
        # 기본 조치 방법
        if error_type != 'unknown':
            solutions = self.ERROR_PATTERNS[error_type]['solutions'].copy()
            prevention = self.ERROR_PATTERNS[error_type]['prevention'].copy()
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
        
        # 구체적인 조치 방법 추가
        specific_solutions = self._get_specific_solutions(error, error_type)
        solutions.extend(specific_solutions)
        
        # 심각도 점수 계산
        severity_score = self.calculate_severity_score(error)
        
        # 영향 범위 분석
        impact_scope = self._analyze_impact_scope(error, error_type)
        
        return {
            'error_type': error_type,
            'matched_keywords': matched_keywords,
            'solutions': solutions,
            'prevention': prevention,
            'severity_score': severity_score,
            'impact_scope': impact_scope,
            'specific_recommendations': specific_solutions
        }
    
    def _get_specific_solutions(self, error: Dict[str, Any], error_type: str) -> List[str]:
        """에러의 구체적인 정보를 바탕으로 상세한 조치 방법 제안"""
        solutions = []
        
        if error_type == 'database':
            if error.get('timeout_value'):
                solutions.append(f"현재 타임아웃이 {error['timeout_value']} {error.get('timeout_unit', 'ms')}입니다. 데이터베이스 연결 타임아웃을 {int(error['timeout_value']) * 2} {error.get('timeout_unit', 'ms')}로 증가시키세요.")
            if error.get('connection_string'):
                solutions.append(f"연결 문자열 확인: {error['connection_string']}")
                solutions.append("데이터베이스 서버 상태 확인 명령어: `pg_isready` (PostgreSQL) 또는 `mysqladmin ping` (MySQL)")
            if error.get('file'):
                solutions.append(f"에러 발생 파일: {error['file']} (라인 {error.get('line', 'N/A')})")
                solutions.append(f"해당 파일의 데이터베이스 연결 코드를 검토하세요.")
        
        elif error_type == 'network':
            if error.get('timeout_value'):
                solutions.append(f"네트워크 타임아웃이 {error['timeout_value']} {error.get('timeout_unit', 'ms')}로 설정되어 있습니다.")
                solutions.append(f"타임아웃을 {int(error['timeout_value']) * 3} {error.get('timeout_unit', 'ms')}로 증가시키거나 재시도 로직을 추가하세요.")
            if error.get('url'):
                solutions.append(f"문제가 발생한 URL: {error['url']}")
                try:
                    url_match = re.search(r'https?://([^/]+)', error['url'])
                    hostname = url_match.group(1) if url_match else 'N/A'
                    solutions.append(f"URL 접근 가능 여부 확인: `curl -I {error['url']}` 또는 `ping {hostname}`")
                except:
                    solutions.append(f"URL 접근 가능 여부 확인: `curl -I {error['url']}`")
        
        elif error_type == 'authentication':
            if error.get('http_status'):
                solutions.append(f"HTTP 상태 코드: {error['http_status']}")
                if error['http_status'] == '401':
                    solutions.append("인증 토큰이 만료되었거나 유효하지 않습니다. 토큰을 재발급하세요.")
                elif error['http_status'] == '403':
                    solutions.append("권한이 부족합니다. 사용자 권한을 확인하세요.")
            if error.get('user_id'):
                solutions.append(f"문제가 발생한 사용자 ID: {error['user_id']}")
                solutions.append("해당 사용자의 인증 상태 및 권한을 확인하세요.")
        
        elif error_type == 'memory':
            if error.get('memory_used') and error.get('memory_limit'):
                try:
                    used_val = int(error['memory_used'].split()[0])
                    limit_val = int(error['memory_limit'].split()[0])
                    percentage = (used_val / limit_val * 100) if limit_val > 0 else 0
                    solutions.append(f"메모리 사용량: {error['memory_used']} / {error['memory_limit']} ({percentage:.1f}%)")
                except:
                    solutions.append(f"메모리 사용량: {error['memory_used']} / {error['memory_limit']}")
                solutions.append("메모리 프로파일링 도구 사용: `memory_profiler` (Python) 또는 `heapdump` (Node.js)")
            if error.get('process_name'):
                solutions.append(f"메모리 문제가 발생한 프로세스: {error['process_name']}")
                solutions.append(f"프로세스 메모리 사용량 확인: `ps aux | grep {error['process_name']}`")
        
        elif error_type == 'file':
            if error.get('file'):
                solutions.append(f"누락된 파일: {error['file']}")
                solutions.append(f"파일 존재 여부 확인: `ls -la {error['file']}` 또는 `Test-Path {error['file']}` (PowerShell)")
                solutions.append(f"파일이 없다면 생성하거나 경로를 수정하세요.")
        
        elif error_type == 'syntax':
            if error.get('file') and error.get('line'):
                solutions.append(f"문법 오류 위치: {error['file']}:{error['line']}")
                solutions.append(f"해당 파일의 {error['line']}번 라인 주변 코드를 검토하세요.")
                solutions.append(f"린터 실행: `eslint {error['file']}` (JavaScript) 또는 `pylint {error['file']}` (Python)")
        
        return solutions
    
    def _analyze_impact_scope(self, error: Dict[str, Any], error_type: str) -> Dict[str, Any]:
        """에러의 영향 범위 분석"""
        impact = {
            'affected_services': [],
            'affected_users': [],
            'system_impact': 'low',
            'business_impact': 'low'
        }
        
        if error.get('service'):
            impact['affected_services'].append(error['service'])
        
        if error.get('user_id'):
            impact['affected_users'].append(error['user_id'])
        
        # 시스템 영향도 평가
        if error_type in ['database', 'memory']:
            impact['system_impact'] = 'high'
            impact['business_impact'] = 'high'
        elif error_type == 'authentication':
            impact['system_impact'] = 'medium'
            impact['business_impact'] = 'high'  # 보안 관련
        elif error_type == 'network':
            impact['system_impact'] = 'medium'
            impact['business_impact'] = 'medium'
        elif error_type == 'syntax':
            impact['system_impact'] = 'high'  # 서비스 중단 가능
            impact['business_impact'] = 'medium'
        
        return impact

def find_log_files(workspace_path: str):
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

def format_error_table(errors):
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

def main():
    workspace_path = os.getcwd()
    
    # 출력 파일 설정 (명령줄 인자가 있으면 해당 파일만 분석)
    output_file = None
    if len(sys.argv) > 1:
        log_file_arg = sys.argv[1]
        if os.path.isfile(log_file_arg):
            # 단일 파일 분석 시 결과를 파일로 저장
            base_name = os.path.splitext(os.path.basename(log_file_arg))[0]
            output_file = os.path.join(os.path.dirname(log_file_arg) or 'logs', f"{base_name}-analysis-result.txt")
    
    # 출력 리다이렉션 설정
    if output_file:
        # 파일로 출력
        original_stdout = sys.stdout
        try:
            sys.stdout = open(output_file, 'w', encoding='utf-8', errors='replace')
        except Exception as e:
            print(f"[경고] 출력 파일 생성 실패: {e}", file=original_stdout)
            output_file = None
    
    try:
        print(f"워크스페이스: {workspace_path}")
        print("=" * 120)
        print()
        
        # 로그 파일 찾기
        if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
            # 단일 파일만 분석
            log_files = [sys.argv[1]]
        else:
            # 모든 로그 파일 찾기
            log_files = find_log_files(workspace_path)
        
        if not log_files:
            print("로그 파일을 찾을 수 없습니다.")
            return
        
        print(f"발견된 로그 파일: {len(log_files)}개")
        for log_file in log_files:
            print(f"  - {log_file}")
        print()
        
        # 각 로그 파일 분석
        for log_file in log_files[:5]:  # 최대 5개 파일만 분석
            try:
                print("=" * 120)
                print(f"[로그 파일] {log_file}")
                print("=" * 120)
                print()
                
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    log_content = f.read()
                
                if not log_content.strip():
                    print("로그 파일이 비어있습니다.")
                    continue
                
                # 로그 파싱
                parser = LogParser(log_content)
                errors = parser.parse_errors()
                
                print(f"[로그 타입] {parser.log_type.upper()}")
                print(f"[발견된 에러] {len(errors)}개")
                print()
                
                if not errors:
                    print("에러를 찾을 수 없습니다.")
                    continue
                
                # 1. 에러 목록 테이블
                print("## 1. 에러 로그 요약 (테이블)")
                print(format_error_table(errors))
                print()
                
                # 2. 에러 분석
                analyzer = ErrorAnalyzer()
                analysis_results = []
                
                for error in errors:
                    analysis = analyzer.analyze_error(error)
                    analysis['error'] = error
                    analysis_results.append(analysis)
                
                # 에러를 심각도 점수로 정렬
                analysis_results.sort(key=lambda x: x['severity_score'], reverse=True)
                
                # 통계 정보
                print("## 2. 에러 통계 및 패턴 분석")
                error_types = Counter([a['error_type'] for a in analysis_results])
                print(f"\n### 에러 타입별 발생 횟수:")
                for err_type, count in error_types.most_common():
                    print(f"  - {err_type.upper()}: {count}회")
                
                # 시간대별 분포
                time_distribution = defaultdict(int)
                for error in errors:
                    timestamp = error.get('timestamp', '')
                    if timestamp:
                        try:
                            # 시간 추출 시도
                            hour_match = re.search(r'T(\d{2}):', timestamp)
                            if hour_match:
                                hour = int(hour_match.group(1))
                                time_distribution[f"{hour:02d}:00-{hour+1:02d}:00"] += 1
                        except:
                            pass
                
                if time_distribution:
                    print(f"\n### 시간대별 에러 분포:")
                    for time_range, count in sorted(time_distribution.items()):
                        print(f"  - {time_range}: {count}건")
                
                # 3. 상세 에러 내역 (심각도 순으로 정렬)
                print("\n## 3. 상세 에러 내역 (심각도 순)")
                for i, analysis in enumerate(analysis_results, 1):
                    error = analysis['error']
                    severity_icon = "🔴" if analysis['severity_score'] >= 70 else "🟠" if analysis['severity_score'] >= 50 else "🟡"
                    
                    print(f"\n{severity_icon} ### 에러 #{i} [심각도 점수: {analysis['severity_score']}/100]")
                    print(f"- **발생일시**: {error.get('timestamp', 'N/A')}")
                    print(f"- **심각도 레벨**: {error.get('severity', 'N/A')}")
                    print(f"- **에러 타입**: {analysis['error_type'].upper()}")
                    
                    # 전체 에러 메시지 출력
                    full_message = error.get('message', 'N/A')
                    if len(full_message) > 500:
                        print(f"- **에러 메시지 (전체)**:")
                        print(f"```")
                        print(full_message[:500] + "\n... (메시지가 길어 일부만 표시)")
                        print(f"```")
                    else:
                        print(f"- **에러 메시지 (전체)**:")
                        print(f"```")
                        print(full_message)
                        print(f"```")
                    
                    # 전체 컨텍스트 출력
                    if error.get('full_context'):
                        context_lines = error['full_context']
                        if len(context_lines) > 1:
                            print(f"- **에러 컨텍스트 (전체 {len(context_lines)}줄)**:")
                            print(f"```")
                            for ctx_line in context_lines[:10]:  # 최대 10줄
                                print(ctx_line)
                            if len(context_lines) > 10:
                                print(f"... (추가 {len(context_lines) - 10}줄 생략)")
                            print(f"```")
                    
                    # 상세 정보 출력 (구조화)
                    print(f"\n**상세 정보:**")
                    detail_items = []
                    if error.get('file'):
                        detail_items.append(f"  📄 파일: `{error['file']}`")
                    if error.get('line'):
                        detail_items.append(f"  📍 라인: `{error['line']}`")
                        if error.get('file'):
                            detail_items.append(f"  💡 코드 확인: `{error['file']}:{error['line']}`")
                    if error.get('location'):
                        detail_items.append(f"  🌍 위치: `{error['location']}`")
                    if error.get('service'):
                        detail_items.append(f"  🔧 서비스: `{error['service']}`")
                    if error.get('resource_type'):
                        detail_items.append(f"  📦 리소스 타입: `{error['resource_type']}`")
                    if error.get('error_code'):
                        detail_items.append(f"  🏷️ 에러 코드: `{error['error_code']}`")
                    if error.get('http_status'):
                        status_emoji = "🔴" if error['http_status'].startswith('5') else "🟠" if error['http_status'].startswith('4') else "🟡"
                        detail_items.append(f"  {status_emoji} HTTP 상태: `{error['http_status']}`")
                    if error.get('timeout_value'):
                        detail_items.append(f"  ⏱️ 타임아웃: `{error['timeout_value']} {error.get('timeout_unit', 'ms')}`")
                    if error.get('memory_used'):
                        detail_items.append(f"  💾 메모리: `{error['memory_used']} / {error.get('memory_limit', 'N/A')}`")
                    if error.get('url'):
                        detail_items.append(f"  🔗 URL: `{error['url']}`")
                    if error.get('user_id'):
                        detail_items.append(f"  👤 사용자 ID: `{error['user_id']}`")
                    if error.get('process_name'):
                        detail_items.append(f"  ⚙️ 프로세스: `{error['process_name']}`")
                    if error.get('connection_string'):
                        detail_items.append(f"  🔌 연결 문자열: `{error['connection_string']}`")
                    
                    for item in detail_items:
                        print(item)
                    
                    # 영향 범위
                    impact = analysis.get('impact_scope', {})
                    if impact:
                        print(f"\n**영향 범위 분석:**")
                        system_impact_emoji = "🔴" if impact.get('system_impact') == 'high' else "🟠" if impact.get('system_impact') == 'medium' else "🟡"
                        business_impact_emoji = "🔴" if impact.get('business_impact') == 'high' else "🟠" if impact.get('business_impact') == 'medium' else "🟡"
                        print(f"  {system_impact_emoji} 시스템 영향도: `{impact.get('system_impact', 'N/A').upper()}`")
                        print(f"  {business_impact_emoji} 비즈니스 영향도: `{impact.get('business_impact', 'N/A').upper()}`")
                        if impact.get('affected_services'):
                            print(f"  🔧 영향받는 서비스: `{', '.join(impact['affected_services'])}`")
                        if impact.get('affected_users'):
                            print(f"  👥 영향받는 사용자: `{', '.join(impact['affected_users'])}`")
                    
                    # 구체적인 조치 방법 (실행 가능한 명령어 포함)
                    if analysis.get('specific_recommendations'):
                        print(f"\n**구체적인 조치 방법 (실행 가능):**")
                        for j, rec in enumerate(analysis['specific_recommendations'], 1):
                            print(f"  {j}. {rec}")
                    
                    # 추가 진단 명령어
                    print(f"\n**추가 진단 명령어:**")
                    diagnostic_commands = []
                    
                    if error.get('file') and error.get('line'):
                        if error['file'].endswith('.py'):
                            diagnostic_commands.append(f"  • 문법 검사: `python -m py_compile {error['file']}`")
                            diagnostic_commands.append(f"  • 코드 확인: `sed -n '{error['line']},{int(error['line'])+5}p' {error['file']}`")
                        elif error['file'].endswith('.js'):
                            diagnostic_commands.append(f"  • 문법 검사: `node --check {error['file']}`")
                            diagnostic_commands.append(f"  • 코드 확인: `sed -n '{error['line']},{int(error['line'])+5}p' {error['file']}`")
                    
                    if error.get('url'):
                        diagnostic_commands.append(f"  • URL 접근 테스트: `curl -I {error['url']}`")
                        diagnostic_commands.append(f"  • 응답 시간 확인: `curl -o /dev/null -s -w '%{{time_total}}' {error['url']}`")
                    
                    if error.get('file') and error.get('file').startswith('/'):
                        diagnostic_commands.append(f"  • 파일 존재 확인: `ls -la {error['file']}`")
                        diagnostic_commands.append(f"  • 파일 권한 확인: `stat {error['file']}`")
                    
                    if error.get('process_name'):
                        diagnostic_commands.append(f"  • 프로세스 상태: `ps aux | grep {error['process_name']}`")
                        diagnostic_commands.append(f"  • 프로세스 메모리: `ps -o pid,vsz,rss,comm -p $(pgrep {error['process_name']})`")
                    
                    if error.get('connection_string'):
                        if 'postgresql' in error['connection_string']:
                            diagnostic_commands.append(f"  • PostgreSQL 연결 테스트: `pg_isready -h localhost`")
                        elif 'mysql' in error['connection_string']:
                            diagnostic_commands.append(f"  • MySQL 연결 테스트: `mysqladmin ping`")
                    
                    for cmd in diagnostic_commands[:8]:  # 최대 8개
                        print(cmd)
                
                # 4. 우선순위별 조치 방법 (더 구체적으로)
                print("\n## 4. 우선순위별 조치 방법 및 실행 계획")
                
                # 심각도 점수별로 그룹화
                critical_errors = [a for a in analysis_results if a['severity_score'] >= 70]
                high_errors = [a for a in analysis_results if 50 <= a['severity_score'] < 70]
                medium_errors = [a for a in analysis_results if 30 <= a['severity_score'] < 50]
                low_errors = [a for a in analysis_results if a['severity_score'] < 30]
                
                if critical_errors:
                    print("\n### 🔴 긴급 (심각도 70점 이상) - 즉시 조치 필요")
                    print(f"**총 {len(critical_errors)}건의 긴급 에러 발견**")
                    for idx, analysis in enumerate(critical_errors[:5], 1):  # 상위 5개
                        error = analysis['error']
                        print(f"\n#### {idx}. {analysis['error_type'].upper()} 에러 (심각도: {analysis['severity_score']}/100)")
                        print(f"**발생 위치:**")
                        if error.get('file') and error.get('line'):
                            print(f"  - 파일: `{error['file']}:{error['line']}`")
                        elif error.get('file'):
                            print(f"  - 파일: `{error['file']}`")
                        if error.get('location'):
                            print(f"  - 위치: `{error['location']}`")
                        if error.get('service'):
                            print(f"  - 서비스: `{error['service']}`")
                        
                        print(f"\n**즉시 실행할 조치:**")
                        for j, solution in enumerate(analysis['solutions'][:5], 1):
                            print(f"  {j}. {solution}")
                        
                        # 구체적인 실행 명령어
                        if analysis.get('specific_recommendations'):
                            print(f"\n**구체적인 실행 명령어:**")
                            for rec in analysis['specific_recommendations'][:3]:
                                print(f"  • {rec}")
                
                if high_errors:
                    print("\n### 🟠 중요 (심각도 50-69점) - 단기 조치 필요 (24시간 이내)")
                    print(f"**총 {len(high_errors)}건의 중요 에러 발견**")
                    unique_high_types = {}
                    for analysis in high_errors:
                        error_type = analysis['error_type']
                        if error_type not in unique_high_types:
                            unique_high_types[error_type] = []
                        unique_high_types[error_type].append(analysis)
                    
                    for error_type, analyses in unique_high_types.items():
                        print(f"\n#### {error_type.upper()} 타입 에러 ({len(analyses)}건)")
                        analysis = analyses[0]  # 대표 분석 사용
                        print(f"**조치 방법:**")
                        for j, solution in enumerate(analysis['solutions'][:5], 1):
                            print(f"  {j}. {solution}")
                        
                        # 해당 타입의 구체적인 예시
                        if analysis.get('specific_recommendations'):
                            print(f"\n**구체적인 예시:**")
                            for rec in analysis['specific_recommendations'][:2]:
                                print(f"  • {rec}")
                
                if medium_errors or low_errors:
                    print("\n### 🟡 개선 (심각도 30점 미만) - 중기 개선 필요 (1주일 이내)")
                    print(f"**총 {len(medium_errors) + len(low_errors)}건의 개선 필요 에러 발견**")
                    unique_types = {}
                    for analysis in medium_errors + low_errors:
                        error_type = analysis['error_type']
                        if error_type not in unique_types:
                            unique_types[error_type] = analysis
                    
                    for error_type, analysis in unique_types.items():
                        print(f"\n#### {error_type.upper()} 타입 에러")
                        print(f"**개선 방법:**")
                        for j, solution in enumerate(analysis['solutions'][:4], 1):
                            print(f"  {j}. {solution}")
                
                # 5. 재발 방지책
                print("\n## 5. 재발 방지책")
                unique_analyses = {}
                for analysis in analysis_results:
                    error_type = analysis['error_type']
                    if error_type not in unique_analyses:
                        unique_analyses[error_type] = analysis
                
                for error_type, analysis in unique_analyses.items():
                    print(f"\n### {error_type.upper()} 타입 에러 재발 방지책:")
                    for j, prevention in enumerate(analysis['prevention'], 1):
                        print(f"  {j}. {prevention}")
                
                # 6. 종합 권장사항 및 실행 계획
                print("\n## 6. 종합 권장사항 및 실행 계획")
                
                # 에러 패턴 분석
                print("\n### 에러 패턴 분석:")
                error_patterns = defaultdict(list)
                for analysis in analysis_results:
                    error = analysis['error']
                    pattern_key = f"{analysis['error_type']}_{error.get('file', 'unknown')}"
                    error_patterns[pattern_key].append(error)
                
                repeated_errors = {k: v for k, v in error_patterns.items() if len(v) > 1}
                if repeated_errors:
                    print(f"  ⚠️ 반복되는 에러 패턴 {len(repeated_errors)}개 발견:")
                    for pattern_key, errors in list(repeated_errors.items())[:5]:
                        error_type, file = pattern_key.split('_', 1)
                        print(f"    - {error_type.upper()} 에러가 {file or '알 수 없음'}에서 {len(errors)}회 발생")
                
                print("\n### 즉시 실행 가능한 진단 명령어 스크립트:")
                print("```bash")
                command_suggestions = []
                
                for analysis in critical_errors[:5]:
                    error = analysis['error']
                    error_type = analysis['error_type']
                    
                    if error_type == 'database' and error.get('file'):
                        command_suggestions.append(f"# {error['file']} 파일의 데이터베이스 연결 코드 검토")
                        command_suggestions.append(f"grep -n 'connection\\|connect\\|database' {error['file']} || echo '파일 없음'")
                        if error.get('connection_string'):
                            command_suggestions.append(f"# 연결 문자열 확인 (비밀번호는 마스킹됨)")
                    
                    elif error_type == 'syntax' and error.get('file'):
                        command_suggestions.append(f"# {error['file']} 파일 문법 검사")
                        if error['file'].endswith('.py'):
                            command_suggestions.append(f"python -m py_compile {error['file']} 2>&1 || echo '문법 오류 발견'")
                            command_suggestions.append(f"python -m flake8 {error['file']} --select=E999,F999 || true")
                        elif error['file'].endswith('.js'):
                            command_suggestions.append(f"node --check {error['file']} 2>&1 || echo '문법 오류 발견'")
                            command_suggestions.append(f"eslint {error['file']} || true")
                    
                    elif error_type == 'file' and error.get('file'):
                        command_suggestions.append(f"# 파일 존재 여부 및 권한 확인")
                        command_suggestions.append(f"ls -la {error['file']} 2>&1 || echo '파일 없음'")
                        command_suggestions.append(f"stat {error['file']} 2>&1 || echo '파일 없음'")
                    
                    elif error_type == 'network' and error.get('url'):
                        command_suggestions.append(f"# 네트워크 연결 테스트")
                        command_suggestions.append(f"curl -I {error['url']} --max-time 10 || echo '연결 실패'")
                        command_suggestions.append(f"ping -c 3 $(echo {error['url']} | sed 's|https\\?://||' | cut -d/ -f1) || echo '핑 실패'")
                    
                    elif error_type == 'memory' and error.get('process_name'):
                        command_suggestions.append(f"# 프로세스 메모리 사용량 확인")
                        command_suggestions.append(f"ps aux | grep {error['process_name']} | grep -v grep || echo '프로세스 없음'")
                
                if command_suggestions:
                    for cmd in command_suggestions[:15]:  # 최대 15개
                        print(f"{cmd}")
                else:
                    print("# 진단할 수 있는 구체적인 명령어가 없습니다.")
                print("```")
                
                print("\n### 모니터링 및 알림 설정 권장사항:")
                print("```yaml")
                print("# 권장 모니터링 설정 예시")
                print("alerts:")
                print("  - name: critical_error_threshold")
                print("    condition: error_count > 5 in 5min")
                print("    action: send_slack_notification")
                print("  - name: database_connection_failure")
                print("    condition: error_type == 'database'")
                print("    action: send_email + page_oncall")
                print("  - name: memory_usage_high")
                print("    condition: memory_usage > 80%")
                print("    action: send_alert")
                print("```")
                
                print("\n### 코드 개선 예시:")
                print("```python")
                print("# 데이터베이스 연결 개선 예시")
                print("import time")
                print("from functools import wraps")
                print("")
                print("def retry_on_failure(max_retries=3, delay=1):")
                print("    def decorator(func):")
                print("        @wraps(func)")
                print("        def wrapper(*args, **kwargs):")
                print("            for attempt in range(max_retries):")
                print("                try:")
                print("                    return func(*args, **kwargs)")
                print("                except Exception as e:")
                print("                    if attempt == max_retries - 1:")
                print("                        raise")
                print("                    time.sleep(delay * (2 ** attempt))")
                print("            return None")
                print("        return wrapper")
                print("    return decorator")
                print("```")
                
                print("\n### 예상 조치 시간:")
                if critical_errors:
                    print(f"  🔴 긴급 에러: {len(critical_errors)}건 - 예상 조치 시간: {len(critical_errors) * 30}분")
                if high_errors:
                    print(f"  🟠 중요 에러: {len(high_errors)}건 - 예상 조치 시간: {len(high_errors) * 15}분")
                if medium_errors or low_errors:
                    print(f"  🟡 개선 에러: {len(medium_errors) + len(low_errors)}건 - 예상 조치 시간: {len(medium_errors) + len(low_errors) * 5}분")
                
                total_time = len(critical_errors) * 30 + len(high_errors) * 15 + (len(medium_errors) + len(low_errors)) * 5
                print(f"\n  **총 예상 조치 시간: 약 {total_time}분 ({total_time // 60}시간 {total_time % 60}분)**")
                
                print()
                print()
                
            except Exception as e:
                print(f"[경고] 로그 파일 분석 중 오류 발생 ({log_file}): {str(e)}")
                import traceback
                traceback.print_exc()
                continue
    
    finally:
        # 출력 파일이 있으면 닫기
        if output_file and sys.stdout != sys.__stdout__:
            sys.stdout.close()
            sys.stdout = sys.__stdout__
            if output_file:
                print(f"\n[완료] 분석 결과가 저장되었습니다: {output_file}")

if __name__ == "__main__":
    main()


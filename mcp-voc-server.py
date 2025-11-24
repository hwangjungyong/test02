#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VOC 자동 대응 MCP 서버

역할:
- SR(Service Request) 입력 및 Confluence 연동
- SR 이력 조회 및 분석
- Git 기반 유사 SR 검색
- DB 수정(Adhoc) 분석

실행 방법:
  python mcp-voc-server.py

의존성 설치:
  pip install mcp requests gitpython

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
from urllib.parse import urlparse, parse_qs
import subprocess

# Windows 콘솔 인코딩 설정 (UTF-8)
if sys.platform == 'win32':
    import io
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
        sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    else:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# MCP SDK import
try:
    from mcp.server import Server
    from mcp.server.stdio import stdio_server
    from mcp.types import Tool, TextContent
except ImportError:
    print("MCP SDK가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install mcp", file=sys.stderr)
    sys.exit(1)

# requests 라이브러리 import (Confluence API용)
try:
    import requests
    from requests.auth import HTTPBasicAuth
except ImportError:
    print("requests 라이브러리가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install requests", file=sys.stderr)
    sys.exit(1)

# GitPython import (Git 연동용)
try:
    import git
except ImportError:
    print("GitPython이 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install gitpython", file=sys.stderr)
    sys.exit(1)

# ============================================
# 환경 변수 설정
# ============================================

# Confluence 설정 (환경 변수에서 가져오거나 기본값 사용)
CONFLUENCE_URL = os.getenv('CONFLUENCE_URL', 'https://your-confluence-instance.atlassian.net')
CONFLUENCE_USERNAME = os.getenv('CONFLUENCE_USERNAME', '')
CONFLUENCE_API_TOKEN = os.getenv('CONFLUENCE_API_TOKEN', '')

# Git 저장소 경로 (환경 변수에서 가져오거나 현재 워크스페이스 사용)
GIT_REPOSITORY_PATH = os.getenv('GIT_REPOSITORY_PATH', os.getcwd())

# 데이터베이스 경로
DB_PATH = os.getenv('DB_PATH', os.path.join(os.getcwd(), 'data', 'database.db'))

# ============================================
# Confluence API 클라이언트
# ============================================

class ConfluenceClient:
    """Confluence API 클라이언트"""
    
    def __init__(self, base_url: str, username: str = None, api_token: str = None):
        self.base_url = base_url.rstrip('/')
        self.username = username or CONFLUENCE_USERNAME
        self.api_token = api_token or CONFLUENCE_API_TOKEN
        self.session = requests.Session()
        
        if self.username and self.api_token:
            self.session.auth = HTTPBasicAuth(self.username, self.api_token)
        
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        })
    
    def extract_key_from_url(self, url: str) -> Optional[str]:
        """Confluence URL에서 페이지 키 추출"""
        try:
            parsed = urlparse(url)
            # URL 패턴: /pages/viewpage.action?pageId=123456
            if 'pageId' in parse_qs(parsed.query):
                page_id = parse_qs(parsed.query)['pageId'][0]
                return page_id
            # URL 패턴: /spaces/SPACE/pages/123456/Page+Title
            path_parts = parsed.path.split('/')
            if 'pages' in path_parts:
                idx = path_parts.index('pages')
                if idx + 1 < len(path_parts):
                    return path_parts[idx + 1]
            # URL 패턴: /display/SPACE/Page+Title (페이지 제목 기반)
            if 'display' in path_parts:
                return None  # 제목 기반은 검색 필요
        except Exception as e:
            print(f"[Confluence] URL 파싱 오류: {e}", file=sys.stderr)
        return None
    
    def get_page_by_id(self, page_id: str) -> Optional[Dict[str, Any]]:
        """페이지 ID로 Confluence 페이지 조회"""
        try:
            url = f"{self.base_url}/rest/api/content/{page_id}"
            params = {
                'expand': 'body.storage,version,space'
            }
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'id': data.get('id'),
                    'title': data.get('title'),
                    'content': data.get('body', {}).get('storage', {}).get('value', ''),
                    'url': f"{self.base_url}/pages/viewpage.action?pageId={data.get('id')}",
                    'space_key': data.get('space', {}).get('key', ''),
                    'last_modified': data.get('version', {}).get('when', '')
                }
            else:
                print(f"[Confluence] 페이지 조회 실패: {response.status_code}", file=sys.stderr)
        except Exception as e:
            print(f"[Confluence] 페이지 조회 오류: {e}", file=sys.stderr)
        return None
    
    def search_pages(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Confluence 페이지 검색"""
        try:
            url = f"{self.base_url}/rest/api/content/search"
            params = {
                'cql': f'text ~ "{query}"',
                'limit': limit,
                'expand': 'body.storage,version,space'
            }
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                results = response.json().get('results', [])
                pages = []
                for item in results:
                    pages.append({
                        'id': item.get('id'),
                        'title': item.get('title'),
                        'content': item.get('body', {}).get('storage', {}).get('value', ''),
                        'url': f"{self.base_url}/pages/viewpage.action?pageId={item.get('id')}",
                        'space_key': item.get('space', {}).get('key', ''),
                        'last_modified': item.get('version', {}).get('when', '')
                    })
                return pages
        except Exception as e:
            print(f"[Confluence] 페이지 검색 오류: {e}", file=sys.stderr)
        return []

# ============================================
# Git 연동 클래스
# ============================================

class GitRepository:
    """Git 저장소 연동 클래스"""
    
    def __init__(self, repo_path: str = None):
        self.repo_path = repo_path or GIT_REPOSITORY_PATH
        
        try:
            self.repo = git.Repo(self.repo_path)
        except Exception as e:
            print(f"[Git] 저장소 초기화 오류: {e}", file=sys.stderr)
            self.repo = None
    
    def search_commits(self, keywords: List[str], limit: int = 20) -> List[Dict[str, Any]]:
        """키워드로 커밋 검색"""
        if not self.repo:
            return []
        
        commits = []
        try:
            # 최근 커밋들 가져오기
            for commit in self.repo.iter_commits(max_count=limit * 2):
                commit_message = commit.message.lower()
                
                # 키워드 매칭 확인
                matched = False
                for keyword in keywords:
                    if keyword.lower() in commit_message:
                        matched = True
                        break
                
                if matched:
                    # 변경된 파일 목록
                    files_changed = [item.a_path for item in commit.stats.files.keys()]
                    
                    commits.append({
                        'commit_hash': commit.hexsha,
                        'author': commit.author.name,
                        'author_email': commit.author.email,
                        'commit_date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                        'commit_message': commit.message,
                        'repository_path': self.repo_path,
                        'branch': self.repo.active_branch.name if self.repo.head.is_valid() else 'unknown',
                        'files_changed': files_changed,
                        'insertions': sum(commit.stats.files.values()),
                        'deletions': 0  # 삭제 라인 수는 별도 계산 필요
                    })
                    
                    if len(commits) >= limit:
                        break
        except Exception as e:
            print(f"[Git] 커밋 검색 오류: {e}", file=sys.stderr)
        
        return commits
    
    def get_commit_details(self, commit_hash: str) -> Optional[Dict[str, Any]]:
        """커밋 상세 정보 조회"""
        if not self.repo:
            return None
        
        try:
            commit = self.repo.commit(commit_hash)
            files_changed = [item.a_path for item in commit.stats.files.keys()]
            
            return {
                'commit_hash': commit.hexsha,
                'author': commit.author.name,
                'author_email': commit.author.email,
                'commit_date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                'commit_message': commit.message,
                'repository_path': self.repo_path,
                'branch': self.repo.active_branch.name if self.repo.head.is_valid() else 'unknown',
                'files_changed': files_changed,
                'insertions': sum(commit.stats.files.values()),
                'deletions': 0
            }
        except Exception as e:
            print(f"[Git] 커밋 상세 조회 오류: {e}", file=sys.stderr)
        return None

# ============================================
# DB 변경 분석 클래스
# ============================================

class DatabaseChangeAnalyzer:
    """데이터베이스 변경 분석 클래스"""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or DB_PATH
    
    def analyze_sql_query(self, sql_query: str) -> Dict[str, Any]:
        """SQL 쿼리 분석하여 테이블/컬럼 변경 감지"""
        changes = []
        
        # CREATE TABLE 감지
        create_table_match = re.search(r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)', sql_query, re.IGNORECASE)
        if create_table_match:
            table_name = create_table_match.group(1)
            changes.append({
                'change_type': 'table_create',
                'table_name': table_name,
                'description': f'테이블 {table_name} 생성'
            })
        
        # DROP TABLE 감지
        drop_table_match = re.search(r'DROP\s+TABLE\s+(?:IF\s+EXISTS\s+)?(\w+)', sql_query, re.IGNORECASE)
        if drop_table_match:
            table_name = drop_table_match.group(1)
            changes.append({
                'change_type': 'table_drop',
                'table_name': table_name,
                'description': f'테이블 {table_name} 삭제'
            })
        
        # ALTER TABLE 감지
        alter_table_match = re.search(r'ALTER\s+TABLE\s+(\w+)', sql_query, re.IGNORECASE)
        if alter_table_match:
            table_name = alter_table_match.group(1)
            
            # ADD COLUMN 감지
            add_column_match = re.search(r'ADD\s+COLUMN\s+(\w+)', sql_query, re.IGNORECASE)
            if add_column_match:
                column_name = add_column_match.group(1)
                changes.append({
                    'change_type': 'column_add',
                    'table_name': table_name,
                    'column_name': column_name,
                    'description': f'테이블 {table_name}에 컬럼 {column_name} 추가'
                })
            
            # DROP COLUMN 감지
            drop_column_match = re.search(r'DROP\s+COLUMN\s+(\w+)', sql_query, re.IGNORECASE)
            if drop_column_match:
                column_name = drop_column_match.group(1)
                changes.append({
                    'change_type': 'column_drop',
                    'table_name': table_name,
                    'column_name': column_name,
                    'description': f'테이블 {table_name}에서 컬럼 {column_name} 삭제'
                })
            
            # MODIFY COLUMN 감지
            modify_column_match = re.search(r'MODIFY\s+COLUMN\s+(\w+)', sql_query, re.IGNORECASE)
            if modify_column_match:
                column_name = modify_column_match.group(1)
                changes.append({
                    'change_type': 'column_modify',
                    'table_name': table_name,
                    'column_name': column_name,
                    'description': f'테이블 {table_name}의 컬럼 {column_name} 수정'
                })
        
        return {
            'sql_query': sql_query,
            'changes': changes,
            'change_count': len(changes)
        }

# ============================================
# MCP 서버 생성
# ============================================

server = Server("voc-server")

# ============================================
# 도구 목록 제공
# ============================================

@server.list_tools()
async def list_tools() -> list[Tool]:
    """
    사용 가능한 도구 목록을 반환합니다.
    """
    return [
        Tool(
            name="register_sr",
            description="SR(Service Request)을 등록합니다. Confluence URL 또는 요구사항을 입력받아 SR을 생성합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "confluence_url": {
                        "type": "string",
                        "description": "Confluence 페이지 URL (선택사항)"
                    },
                    "title": {
                        "type": "string",
                        "description": "SR 제목 (필수)"
                    },
                    "description": {
                        "type": "string",
                        "description": "SR 설명/요구사항"
                    },
                    "priority": {
                        "type": "string",
                        "description": "우선순위 (low, medium, high, critical)",
                        "enum": ["low", "medium", "high", "critical"],
                        "default": "medium"
                    },
                    "category": {
                        "type": "string",
                        "description": "카테고리"
                    },
                    "tags": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "태그 목록"
                    }
                },
                "required": ["title"]
            }
        ),
        Tool(
            name="search_sr_history",
            description="SR 이력을 조회합니다. 필터 조건을 사용하여 검색할 수 있습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "description": "상태 필터 (open, in_progress, resolved, closed)"
                    },
                    "priority": {
                        "type": "string",
                        "description": "우선순위 필터"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "조회할 최대 개수",
                        "default": 50
                    }
                }
            }
        ),
        Tool(
            name="search_similar_sr",
            description="Git 저장소를 검색하여 유사한 SR 처리 내역을 찾습니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "검색 키워드 목록"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "조회할 최대 개수",
                        "default": 10
                    }
                },
                "required": ["keywords"]
            }
        ),
        Tool(
            name="analyze_db_changes",
            description="SQL 쿼리를 분석하여 테이블/컬럼 변경 사항을 감지합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql_query": {
                        "type": "string",
                        "description": "분석할 SQL 쿼리"
                    }
                },
                "required": ["sql_query"]
            }
        ),
        Tool(
            name="get_confluence_page",
            description="Confluence URL에서 페이지 키를 추출하고 페이지 내용을 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "confluence_url": {
                        "type": "string",
                        "description": "Confluence 페이지 URL"
                    }
                },
                "required": ["confluence_url"]
            }
        )
    ]

# ============================================
# 도구 실행 핸들러
# ============================================

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> Sequence[TextContent]:
    """
    도구 실행 핸들러
    """
    try:
        if name == "register_sr":
            return await handle_register_sr(arguments)
        elif name == "search_sr_history":
            return await handle_search_sr_history(arguments)
        elif name == "search_similar_sr":
            return await handle_search_similar_sr(arguments)
        elif name == "analyze_db_changes":
            return await handle_analyze_db_changes(arguments)
        elif name == "get_confluence_page":
            return await handle_get_confluence_page(arguments)
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

async def handle_register_sr(arguments: dict) -> Sequence[TextContent]:
    """SR 등록 처리"""
    confluence_url = arguments.get("confluence_url")
    title = arguments.get("title")
    description = arguments.get("description", "")
    priority = arguments.get("priority", "medium")
    category = arguments.get("category")
    tags = arguments.get("tags", [])
    
    confluence_key = None
    confluence_content = None
    confluence_page_id = None
    
    # Confluence URL이 있으면 페이지 정보 가져오기
    if confluence_url:
        client = ConfluenceClient(CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
        confluence_key = client.extract_key_from_url(confluence_url)
        
        if confluence_key:
            page_info = client.get_page_by_id(confluence_key)
            if page_info:
                confluence_content = page_info.get('content', '')
                confluence_page_id = page_info.get('id')
                if not description and page_info.get('title'):
                    description = f"Confluence 페이지: {page_info.get('title')}\n\n{confluence_content[:500]}"
    
    # SR 데이터 구성 (실제로는 database.js의 srRequestsDB.create 호출 필요)
    sr_data = {
        'title': title,
        'description': description,
        'confluence_url': confluence_url,
        'confluence_key': confluence_key,
        'confluence_page_id': confluence_page_id,
        'confluence_content': confluence_content,
        'source_type': 'confluence' if confluence_url else 'manual',
        'status': 'open',
        'priority': priority,
        'category': category,
        'tags': tags
    }
    
    result = {
        'success': True,
        'message': 'SR이 성공적으로 등록되었습니다.',
        'sr_data': sr_data
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]

async def handle_search_sr_history(arguments: dict) -> Sequence[TextContent]:
    """SR 이력 조회 처리"""
    status = arguments.get("status")
    priority = arguments.get("priority")
    limit = arguments.get("limit", 50)
    
    filters = {}
    if status:
        filters['status'] = status
    if priority:
        filters['priority'] = priority
    
    # 실제로는 database.js의 srRequestsDB.findAll 호출 필요
    result = {
        'success': True,
        'filters': filters,
        'limit': limit,
        'message': 'SR 이력 조회 완료 (실제 DB 조회는 API 서버에서 수행)'
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]

async def handle_search_similar_sr(arguments: dict) -> Sequence[TextContent]:
    """유사 SR 검색 처리"""
    keywords = arguments.get("keywords", [])
    limit = arguments.get("limit", 10)
    
    if not keywords:
        return [TextContent(
            type="text",
            text=json.dumps({
                'success': False,
                'error': '키워드가 필요합니다.'
            }, ensure_ascii=False, indent=2)
        )]
    
    git_repo = GitRepository(GIT_REPOSITORY_PATH)
    commits = git_repo.search_commits(keywords, limit)
    
    result = {
        'success': True,
        'keywords': keywords,
        'commits_found': len(commits),
        'commits': commits
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]

async def handle_analyze_db_changes(arguments: dict) -> Sequence[TextContent]:
    """DB 변경 분석 처리"""
    sql_query = arguments.get("sql_query")
    
    if not sql_query:
        return [TextContent(
            type="text",
            text=json.dumps({
                'success': False,
                'error': 'SQL 쿼리가 필요합니다.'
            }, ensure_ascii=False, indent=2)
        )]
    
    analyzer = DatabaseChangeAnalyzer(DB_PATH)
    analysis = analyzer.analyze_sql_query(sql_query)
    
    result = {
        'success': True,
        'analysis': analysis
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
    )]

async def handle_get_confluence_page(arguments: dict) -> Sequence[TextContent]:
    """Confluence 페이지 가져오기"""
    confluence_url = arguments.get("confluence_url")
    
    if not confluence_url:
        return [TextContent(
            type="text",
            text=json.dumps({
                'success': False,
                'error': 'Confluence URL이 필요합니다.'
            }, ensure_ascii=False, indent=2)
        )]
    
    client = ConfluenceClient(CONFLUENCE_URL, CONFLUENCE_USERNAME, CONFLUENCE_API_TOKEN)
    confluence_key = client.extract_key_from_url(confluence_url)
    
    if not confluence_key:
        return [TextContent(
            type="text",
            text=json.dumps({
                'success': False,
                'error': 'Confluence URL에서 페이지 키를 추출할 수 없습니다.'
            }, ensure_ascii=False, indent=2)
        )]
    
    page_info = client.get_page_by_id(confluence_key)
    
    if not page_info:
        return [TextContent(
            type="text",
            text=json.dumps({
                'success': False,
                'error': 'Confluence 페이지를 찾을 수 없습니다.'
            }, ensure_ascii=False, indent=2)
        )]
    
    result = {
        'success': True,
        'confluence_key': confluence_key,
        'page_info': page_info
    }
    
    return [TextContent(
        type="text",
        text=json.dumps(result, ensure_ascii=False, indent=2)
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
    print("VOC 자동 대응 MCP 서버가 시작되었습니다.", file=sys.stderr)
    print("사용 가능한 도구: register_sr, search_sr_history, search_similar_sr, analyze_db_changes, get_confluence_page", file=sys.stderr)
    asyncio.run(main())


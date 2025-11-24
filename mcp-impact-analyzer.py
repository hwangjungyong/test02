#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI 테이블 영향도 분석 MCP 서버

역할:
- 워크스페이스 전체를 스캔하여 테이블/컬럼 변경 시 영향도 분석
- 프로그램 코드, 화면, 배치 프로시저 등 모든 영향도 분석
- PostgreSQL 리니지 분석 포함

실행 방법:
  python mcp-impact-analyzer.py

의존성 설치:
  pip install mcp sqlparse

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
from typing import Any, Sequence, List, Dict, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
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

# sqlparse import
try:
    import sqlparse
    from sqlparse import sql, tokens as T
    from sqlparse.sql import Statement, TokenList
except ImportError:
    print("sqlparse 라이브러리가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install sqlparse", file=sys.stderr)
    sys.exit(1)

# ============================================
# 워크스페이스 스캐너 클래스
# ============================================

class WorkspaceScanner:
    """워크스페이스 코드 파일 스캔 클래스"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.code_files = []
        self.sql_files = []
        self.vue_files = []
        self.table_references = defaultdict(list)  # table_name -> [file_path, line_number]
        self.column_references = defaultdict(list)  # column_name -> [file_path, line_number]
        
    def scan_workspace(self):
        """워크스페이스 전체 스캔"""
        print(f"[스캔] 워크스페이스 경로: {self.workspace_path}", file=sys.stderr)
        
        # 제외할 디렉토리
        exclude_dirs = {
            'node_modules', '.git', '__pycache__', '.vscode', 
            'dist', 'build', '.next', 'venv', 'env', '.venv'
        }
        
        # 제외할 파일 확장자
        exclude_extensions = {'.pyc', '.pyo', '.pyd', '.db', '.sqlite', '.log'}
        
        for root, dirs, files in os.walk(self.workspace_path):
            # 제외 디렉토리 필터링
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, self.workspace_path)
                
                # 제외 파일 필터링
                if any(file.endswith(ext) for ext in exclude_extensions):
                    continue
                
                # 코드 파일 분류
                if file.endswith(('.js', '.ts', '.jsx', '.tsx', '.py')):
                    self.code_files.append(file_path)
                elif file.endswith('.sql'):
                    self.sql_files.append(file_path)
                elif file.endswith('.vue'):
                    self.vue_files.append(file_path)
        
        print(f"[스캔] 코드 파일: {len(self.code_files)}개", file=sys.stderr)
        print(f"[스캔] SQL 파일: {len(self.sql_files)}개", file=sys.stderr)
        print(f"[스캔] Vue 파일: {len(self.vue_files)}개", file=sys.stderr)
    
    def scan_table_references(self, table_name: str):
        """테이블명 참조 스캔"""
        pattern = re.compile(rf'\b{re.escape(table_name)}\b', re.IGNORECASE)
        
        for file_path in self.code_files + self.sql_files + self.vue_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        if pattern.search(line):
                            rel_path = os.path.relpath(file_path, self.workspace_path)
                            self.table_references[table_name].append({
                                'file': rel_path,
                                'line': line_num,
                                'context': line.strip()[:100]
                            })
            except Exception as e:
                print(f"[스캔 오류] {file_path}: {e}", file=sys.stderr)
    
    def scan_column_references(self, column_name: str, table_name: str = None):
        """컬럼명 참조 스캔"""
        # 테이블명이 있으면 테이블.컬럼 형태도 검색
        patterns = [
            re.compile(rf'\b{re.escape(column_name)}\b', re.IGNORECASE)
        ]
        
        if table_name:
            patterns.append(
                re.compile(rf'\b{re.escape(table_name)}\s*\.\s*{re.escape(column_name)}\b', re.IGNORECASE)
            )
        
        for file_path in self.code_files + self.sql_files + self.vue_files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    for line_num, line in enumerate(f, 1):
                        for pattern in patterns:
                            if pattern.search(line):
                                rel_path = os.path.relpath(file_path, self.workspace_path)
                                self.column_references[column_name].append({
                                    'file': rel_path,
                                    'line': line_num,
                                    'context': line.strip()[:100]
                                })
                                break
            except Exception as e:
                print(f"[스캔 오류] {file_path}: {e}", file=sys.stderr)

# ============================================
# 데이터베이스 스키마 추출 클래스
# ============================================

class SchemaExtractor:
    """데이터베이스 스키마 추출 클래스"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.schema = {}
    
    def extract_from_database_js(self):
        """database.js에서 스키마 추출"""
        db_js_path = os.path.join(self.workspace_path, 'database.js')
        
        if not os.path.exists(db_js_path):
            return {}
        
        try:
            with open(db_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # CREATE TABLE 문 찾기
            create_table_pattern = re.compile(
                r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([^)]+)\)',
                re.IGNORECASE | re.DOTALL
            )
            
            for match in create_table_pattern.finditer(content):
                table_name = match.group(1)
                columns_text = match.group(2)
                
                # 컬럼 파싱
                columns = []
                column_pattern = re.compile(
                    r'(\w+)\s+(\w+(?:\(\d+\))?)\s*(?:PRIMARY\s+KEY|UNIQUE|NOT\s+NULL|FOREIGN\s+KEY|DEFAULT|REFERENCES)?',
                    re.IGNORECASE
                )
                
                for col_match in column_pattern.finditer(columns_text):
                    col_name = col_match.group(1)
                    col_type = col_match.group(2)
                    columns.append({
                        'name': col_name,
                        'type': col_type
                    })
                
                self.schema[table_name] = {
                    'columns': columns,
                    'source': 'database.js'
                }
        except Exception as e:
            print(f"[스키마 추출 오류] database.js: {e}", file=sys.stderr)
        
        return self.schema
    
    def extract_from_sql_files(self):
        """SQL 파일에서 스키마 추출"""
        sql_files = []
        for root, dirs, files in os.walk(self.workspace_path):
            for file in files:
                if file.endswith('.sql'):
                    sql_files.append(os.path.join(root, file))
        
        for sql_file in sql_files:
            try:
                with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # CREATE TABLE 문 찾기
                create_table_pattern = re.compile(
                    r'CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(\w+)\s*\(([^)]+)\)',
                    re.IGNORECASE | re.DOTALL
                )
                
                for match in create_table_pattern.finditer(content):
                    table_name = match.group(1)
                    columns_text = match.group(2)
                    
                    columns = []
                    for line in columns_text.split(','):
                        line = line.strip()
                        if not line or line.startswith('FOREIGN KEY'):
                            continue
                        
                        parts = line.split()
                        if len(parts) >= 2:
                            col_name = parts[0].strip('"\'`')
                            col_type = parts[1].strip('"\'`')
                            columns.append({
                                'name': col_name,
                                'type': col_type
                            })
                    
                    if table_name not in self.schema:
                        self.schema[table_name] = {
                            'columns': columns,
                            'source': os.path.relpath(sql_file, self.workspace_path)
                        }
            except Exception as e:
                print(f"[스키마 추출 오류] {sql_file}: {e}", file=sys.stderr)
        
        return self.schema

# ============================================
# 영향도 분석 클래스
# ============================================

class ImpactAnalyzer:
    """영향도 분석 클래스"""
    
    def __init__(self, workspace_path: str = None):
        self.workspace_path = workspace_path or os.getcwd()
        self.scanner = WorkspaceScanner(workspace_path)
        self.schema_extractor = SchemaExtractor(workspace_path)
    
    def analyze(self, table_name: str, column_name: str = None, special_notes: str = None):
        """영향도 분석 수행"""
        print(f"[분석 시작] 테이블: {table_name}, 컬럼: {column_name or '전체'}", file=sys.stderr)
        
        # 워크스페이스 스캔
        self.scanner.scan_workspace()
        
        # 스키마 추출
        schema = self.schema_extractor.extract_from_database_js()
        schema.update(self.schema_extractor.extract_from_sql_files())
        
        # 테이블 참조 스캔
        self.scanner.scan_table_references(table_name)
        
        # 컬럼 참조 스캔
        if column_name:
            self.scanner.scan_column_references(column_name, table_name)
        
        # 분석 결과 구성
        result = {
            'table_name': table_name,
            'column_name': column_name,
            'special_notes': special_notes,
            'table_correlation': self._analyze_table_correlation(table_name, schema),
            'program_table_correlation': self._analyze_program_table_correlation(table_name),
            'program_column_correlation': self._analyze_program_column_correlation(column_name, table_name) if column_name else {},
            'ui_impact': self._analyze_ui_impact(table_name, column_name),
            'batch_procedure_impact': self._analyze_batch_procedure_impact(table_name, column_name),
            'postgresql_lineage': self._analyze_postgresql_lineage(table_name, schema)
        }
        
        return result
    
    def _analyze_table_correlation(self, table_name: str, schema: Dict):
        """테이블 상관도 분석"""
        # SQL 파일에서 JOIN 관계 분석
        join_relations = []
        
        for sql_file in self.scanner.sql_files:
            try:
                with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # JOIN 패턴 찾기
                join_pattern = re.compile(
                    rf'{re.escape(table_name)}\s+(?:INNER|LEFT|RIGHT|FULL)?\s*JOIN\s+(\w+)',
                    re.IGNORECASE
                )
                
                for match in join_pattern.finditer(content):
                    related_table = match.group(1)
                    join_relations.append({
                        'related_table': related_table,
                        'join_type': 'JOIN',
                        'source_file': os.path.relpath(sql_file, self.workspace_path)
                    })
            except Exception as e:
                print(f"[테이블 상관도 오류] {sql_file}: {e}", file=sys.stderr)
        
        direct_refs = len(self.scanner.table_references[table_name])
        join_count = len(join_relations)
        file_count = len(set(ref['file'] for ref in self.scanner.table_references[table_name]))
        
        # 요약 생성
        summary_parts = []
        if direct_refs > 0:
            summary_parts.append(f"직접 참조 {direct_refs}건")
        if join_count > 0:
            related_tables = list(set(r['related_table'] for r in join_relations))
            summary_parts.append(f"{join_count}개 JOIN으로 {len(related_tables)}개 테이블과 연결")
        if file_count > 0:
            summary_parts.append(f"{file_count}개 파일에서 사용")
        
        summary = " | ".join(summary_parts) if summary_parts else "참조 없음"
        
        return {
            'summary': summary,
            'direct_references': direct_refs,
            'join_relations': join_relations,
            'referenced_files': list(set(ref['file'] for ref in self.scanner.table_references[table_name])),
            'related_tables': list(set(r['related_table'] for r in join_relations)) if join_relations else []
        }
    
    def _analyze_program_table_correlation(self, table_name: str):
        """프로그램 테이블 상관도 분석"""
        references = self.scanner.table_references[table_name]
        
        # 파일 타입별 분류
        js_files = [r for r in references if r['file'].endswith(('.js', '.ts', '.jsx', '.tsx'))]
        py_files = [r for r in references if r['file'].endswith('.py')]
        sql_files = [r for r in references if r['file'].endswith('.sql')]
        
        # 요약 생성
        summary_parts = []
        if len(js_files) > 0:
            summary_parts.append(f"JavaScript {len(js_files)}건")
        if len(py_files) > 0:
            summary_parts.append(f"Python {len(py_files)}건")
        if len(sql_files) > 0:
            summary_parts.append(f"SQL {len(sql_files)}건")
        
        summary = f"총 {len(references)}건 참조 ({', '.join(summary_parts)})" if summary_parts else "참조 없음"
        
        return {
            'summary': summary,
            'total_references': len(references),
            'javascript_files': len(js_files),
            'python_files': len(py_files),
            'sql_files': len(sql_files),
            'references': references[:50]  # 최대 50개만 반환
        }
    
    def _analyze_program_column_correlation(self, column_name: str, table_name: str):
        """프로그램 컬럼 상관도 분석"""
        if not column_name:
            return {}
        
        references = self.scanner.column_references[column_name]
        
        # 파일 타입별 분류
        js_files = [r for r in references if r['file'].endswith(('.js', '.ts', '.jsx', '.tsx'))]
        py_files = [r for r in references if r['file'].endswith('.py')]
        sql_files = [r for r in references if r['file'].endswith('.sql')]
        
        # 요약 생성
        summary_parts = []
        if len(js_files) > 0:
            summary_parts.append(f"JavaScript {len(js_files)}건")
        if len(py_files) > 0:
            summary_parts.append(f"Python {len(py_files)}건")
        if len(sql_files) > 0:
            summary_parts.append(f"SQL {len(sql_files)}건")
        
        summary = f"총 {len(references)}건 참조 ({', '.join(summary_parts)})" if summary_parts else "참조 없음"
        
        return {
            'summary': summary,
            'total_references': len(references),
            'javascript_files': len(js_files),
            'python_files': len(py_files),
            'sql_files': len(sql_files),
            'references': references[:50]  # 최대 50개만 반환
        }
    
    def _analyze_ui_impact(self, table_name: str, column_name: str = None):
        """화면 영향 분석"""
        vue_impacts = []
        
        for vue_file in self.scanner.vue_files:
            try:
                with open(vue_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 테이블명 참조 확인
                if re.search(rf'\b{re.escape(table_name)}\b', content, re.IGNORECASE):
                    vue_impacts.append({
                        'file': os.path.relpath(vue_file, self.workspace_path),
                        'type': 'table_reference',
                        'table': table_name
                    })
                
                # 컬럼명 참조 확인
                if column_name and re.search(rf'\b{re.escape(column_name)}\b', content, re.IGNORECASE):
                    vue_impacts.append({
                        'file': os.path.relpath(vue_file, self.workspace_path),
                        'type': 'column_reference',
                        'column': column_name
                    })
            except Exception as e:
                print(f"[UI 영향 분석 오류] {vue_file}: {e}", file=sys.stderr)
        
        impact_count = len(vue_impacts)
        summary = f"{impact_count}개 Vue 컴포넌트에서 사용 중" if impact_count > 0 else "영향 없음"
        
        return {
            'summary': summary,
            'affected_vue_files': impact_count,
            'impacts': vue_impacts
        }
    
    def _analyze_batch_procedure_impact(self, table_name: str, column_name: str = None):
        """배치 프로시저 영향 분석"""
        procedure_impacts = []
        
        for sql_file in self.scanner.sql_files:
            try:
                with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # 프로시저/함수 정의 찾기
                procedure_pattern = re.compile(
                    r'(?:CREATE\s+(?:OR\s+REPLACE\s+)?)?(?:PROCEDURE|FUNCTION)\s+(\w+)',
                    re.IGNORECASE
                )
                
                for match in procedure_pattern.finditer(content):
                    proc_name = match.group(1)
                    
                    # 프로시저 내부에서 테이블/컬럼 참조 확인
                    proc_start = match.start()
                    proc_end = content.find('END', proc_start)
                    if proc_end == -1:
                        proc_end = len(content)
                    
                    proc_body = content[proc_start:proc_end]
                    
                    if re.search(rf'\b{re.escape(table_name)}\b', proc_body, re.IGNORECASE):
                        procedure_impacts.append({
                            'procedure_name': proc_name,
                            'file': os.path.relpath(sql_file, self.workspace_path),
                            'table': table_name,
                            'impact_type': 'table_reference'
                        })
                    
                    if column_name and re.search(rf'\b{re.escape(column_name)}\b', proc_body, re.IGNORECASE):
                        procedure_impacts.append({
                            'procedure_name': proc_name,
                            'file': os.path.relpath(sql_file, self.workspace_path),
                            'column': column_name,
                            'impact_type': 'column_reference'
                        })
            except Exception as e:
                print(f"[배치 프로시저 분석 오류] {sql_file}: {e}", file=sys.stderr)
        
        proc_count = len(procedure_impacts)
        unique_procs = len(set(p['procedure_name'] for p in procedure_impacts))
        summary = f"{unique_procs}개 프로시저/함수에서 {proc_count}건 참조" if proc_count > 0 else "영향 없음"
        
        return {
            'summary': summary,
            'affected_procedures': proc_count,
            'unique_procedures': unique_procs,
            'impacts': procedure_impacts
        }
    
    def _analyze_postgresql_lineage(self, table_name: str, schema: Dict):
        """PostgreSQL 리니지 분석"""
        # SQLite 스키마를 PostgreSQL 스타일로 변환
        lineage = {
            'table': table_name,
            'postgresql_schema': 'public',  # 기본 스키마
            'columns': [],
            'dependencies': [],
            'dependents': []
        }
        
        # 스키마에서 컬럼 정보 추출
        if table_name in schema:
            for col in schema[table_name].get('columns', []):
                # SQLite 타입을 PostgreSQL 타입으로 변환
                pg_type = self._convert_to_postgresql_type(col.get('type', 'TEXT'))
                lineage['columns'].append({
                    'name': col.get('name', ''),
                    'type': pg_type,
                    'nullable': True
                })
        
        # 의존성 분석 (JOIN 관계 기반)
        table_correlation = self._analyze_table_correlation(table_name, schema)
        for join_rel in table_correlation.get('join_relations', []):
            lineage['dependencies'].append({
                'table': join_rel['related_table'],
                'relationship': 'JOIN'
            })
        
        col_count = len(lineage['columns'])
        dep_count = len(lineage['dependencies'])
        summary_parts = []
        if col_count > 0:
            summary_parts.append(f"{col_count}개 컬럼")
        if dep_count > 0:
            summary_parts.append(f"{dep_count}개 테이블 의존성")
        
        summary = " | ".join(summary_parts) if summary_parts else "스키마 정보 없음"
        lineage['summary'] = summary
        
        return lineage
    
    def _convert_to_postgresql_type(self, sqlite_type: str):
        """SQLite 타입을 PostgreSQL 타입으로 변환"""
        type_mapping = {
            'INTEGER': 'INTEGER',
            'TEXT': 'TEXT',
            'REAL': 'REAL',
            'BLOB': 'BYTEA',
            'NUMERIC': 'NUMERIC'
        }
        
        sqlite_type_upper = sqlite_type.upper().split('(')[0]
        return type_mapping.get(sqlite_type_upper, 'TEXT')

# ============================================
# MCP 서버 설정
# ============================================

# MCP 서버 인스턴스 생성
server = Server("impact-analyzer")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """사용 가능한 도구 목록 반환"""
    return [
        Tool(
            name="analyze_impact",
            description="테이블/컬럼 변경 시 워크스페이스 전체 영향도 분석",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "분석할 테이블명"
                    },
                    "column_name": {
                        "type": "string",
                        "description": "분석할 컬럼명 (선택사항)"
                    },
                    "special_notes": {
                        "type": "string",
                        "description": "특이사항 (예: user_id가 int에서 varchar로 변경)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "워크스페이스 경로 (선택사항, 기본값: 현재 디렉토리)"
                    }
                },
                "required": ["table_name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Any) -> List[TextContent]:
    """도구 호출 처리"""
    if name == "analyze_impact":
        table_name = arguments.get("table_name")
        column_name = arguments.get("column_name")
        special_notes = arguments.get("special_notes")
        workspace_path = arguments.get("workspace_path")
        
        try:
            analyzer = ImpactAnalyzer(workspace_path)
            result = analyzer.analyze(table_name, column_name, special_notes)
            
            return [TextContent(
                type="text",
                text=json.dumps(result, ensure_ascii=False, indent=2)
            )]
        except Exception as e:
            return [TextContent(
                type="text",
                text=json.dumps({
                    "error": str(e),
                    "error_type": type(e).__name__
                }, ensure_ascii=False, indent=2)
            )]
    else:
        raise ValueError(f"Unknown tool: {name}")

# ============================================
# 메인 함수
# ============================================

async def main():
    """MCP 서버 실행"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )

if __name__ == "__main__":
    # 명령줄 인자로 실행되는 경우 (API 서버에서 호출)
    if len(sys.argv) > 1:
        parser = argparse.ArgumentParser(description='AI 테이블 영향도 분석')
        parser.add_argument('--table', required=True, help='테이블명')
        parser.add_argument('--column', help='컬럼명 (선택사항)')
        parser.add_argument('--notes', help='특이사항')
        parser.add_argument('--workspace', help='워크스페이스 경로')
        
        args = parser.parse_args()
        
        try:
            analyzer = ImpactAnalyzer(args.workspace)
            result = analyzer.analyze(args.table, args.column, args.notes)
            
            # JSON 출력 (UTF-8 인코딩 보장)
            json_str = json.dumps(result, ensure_ascii=False, indent=2)
            # Windows 콘솔에서 안전하게 출력하기 위해 UTF-8로 인코딩
            if sys.platform == 'win32':
                sys.stdout.buffer.write(json_str.encode('utf-8'))
                sys.stdout.buffer.write(b'\n')
            else:
                print(json_str)
        except Exception as e:
            import traceback
            error_result = {
                "error": str(e),
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc() if sys.platform != 'win32' else None
            }
            json_str = json.dumps(error_result, ensure_ascii=False, indent=2)
            # Windows 콘솔에서 안전하게 출력하기 위해 UTF-8로 인코딩
            if sys.platform == 'win32':
                sys.stdout.buffer.write(json_str.encode('utf-8'))
                sys.stdout.buffer.write(b'\n')
            else:
                print(json_str)
            sys.exit(1)
    else:
        # MCP 서버 모드로 실행
        asyncio.run(main())


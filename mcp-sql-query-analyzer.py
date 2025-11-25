#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 쿼리 분석 MCP 서버

역할:
- PostgreSQL 쿼리(3000-4000라인)를 자동으로 분석
- 구조 분석, 성능 분석, 최적화 제안, 복잡도 분석, 보안 분석 수행
- JSON 및 마크다운 파일로 결과 제공

실행 방법:
  python mcp-sql-query-analyzer.py

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
from typing import Any, Sequence, List, Dict, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
from collections import defaultdict, Counter

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
# SQL 쿼리 파서 클래스
# ============================================

class SQLQueryParser:
    """PostgreSQL 쿼리 파싱 및 구조 추출 클래스"""
    
    def __init__(self, query_text: str):
        self.query_text = query_text.strip()
        self.parsed_statements = []
        self._parse()
    
    def _parse(self):
        """쿼리를 파싱하여 Statement 리스트 생성"""
        # 주석 제거 및 정규화
        normalized = sqlparse.format(self.query_text, reindent=True, strip_comments=True)
        # 여러 쿼리 분리
        statements = sqlparse.split(normalized)
        for stmt in statements:
            if stmt.strip():
                parsed = sqlparse.parse(stmt)[0]
                self.parsed_statements.append(parsed)
    
    def get_query_type(self) -> str:
        """쿼리 타입 반환 (SELECT, INSERT, UPDATE, DELETE 등)"""
        if not self.parsed_statements:
            return "UNKNOWN"
        
        first_token = self.parsed_statements[0].token_first()
        if first_token and first_token.ttype in (T.Keyword.DML, T.Keyword.DDL):
            return str(first_token).upper()
        return "UNKNOWN"
    
    def extract_tables(self) -> List[str]:
        """FROM 절과 JOIN 절에서 테이블명 추출"""
        tables = set()
        
        for stmt in self.parsed_statements:
            # FROM 절 찾기
            from_seen = False
            for token in stmt.flatten():
                if token.ttype is T.Keyword and token.value.upper() == 'FROM':
                    from_seen = True
                    continue
                if from_seen:
                    if token.ttype is None and token.value.strip():
                        # 테이블명 또는 별칭
                        table_name = token.value.strip().split()[0].strip('"\'`')
                        if table_name and table_name.upper() not in ['SELECT', 'WHERE', 'JOIN', 'INNER', 'LEFT', 'RIGHT', 'FULL', 'OUTER', 'ON', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'INTERSECT', 'EXCEPT']:
                            tables.add(table_name)
                    if token.ttype is T.Keyword and token.value.upper() in ['WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT', 'UNION', 'INTERSECT', 'EXCEPT']:
                        from_seen = False
            
            # JOIN 절 찾기
            tokens = list(stmt.flatten())
            for i, token in enumerate(tokens):
                if token.ttype is T.Keyword and 'JOIN' in token.value.upper():
                    # JOIN 다음 토큰 찾기
                    j = i + 1
                    while j < len(tokens) and tokens[j].ttype in (T.Whitespace, T.Newline):
                        j += 1
                    if j < len(tokens) and tokens[j].ttype is None:
                        table_name = tokens[j].value.strip().split()[0].strip('"\'`')
                        if table_name:
                            tables.add(table_name)
        
        return sorted(list(tables))
    
    def extract_columns(self) -> List[str]:
        """SELECT 절에서 컬럼명 추출"""
        columns = []
        
        for stmt in self.parsed_statements:
            select_seen = False
            select_tokens = []
            
            for token in stmt.flatten():
                if token.ttype is T.Keyword and token.value.upper() == 'SELECT':
                    select_seen = True
                    continue
                if select_seen:
                    if token.ttype is T.Keyword and token.value.upper() == 'FROM':
                        break
                    if token.ttype is None and token.value.strip() and token.value != ',':
                        # 컬럼명 추출 (별칭 제거)
                        col = token.value.strip().split()[-1].strip('"\'`')
                        if col and col.upper() not in ['AS', 'SELECT', 'FROM']:
                            columns.append(col)
            
            # SELECT 절 전체를 파싱하여 더 정확하게 추출
            if select_seen:
                select_part = str(stmt).upper()
                if 'SELECT' in select_part and 'FROM' in select_part:
                    select_clause = select_part.split('FROM')[0]
                    # 쉼표로 분리
                    for col in select_clause.replace('SELECT', '').split(','):
                        col_clean = col.strip().split()[-1].strip('"\'`')
                        if col_clean and col_clean not in columns:
                            columns.append(col_clean)
        
        return columns
    
    def extract_joins(self) -> List[Dict[str, Any]]:
        """JOIN 정보 추출"""
        joins = []
        
        for stmt in self.parsed_statements:
            tokens = list(stmt.flatten())
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token.ttype is T.Keyword and 'JOIN' in token.value.upper():
                    join_type = token.value.upper()
                    join_info = {
                        'type': join_type,
                        'table': None,
                        'condition': None
                    }
                    
                    # JOIN 다음 테이블 찾기
                    j = i + 1
                    while j < len(tokens) and tokens[j].ttype in (T.Whitespace, T.Newline):
                        j += 1
                    if j < len(tokens):
                        join_info['table'] = tokens[j].value.strip().split()[0].strip('"\'`')
                    
                    # ON 조건 찾기
                    k = j + 1
                    while k < len(tokens):
                        if tokens[k].ttype is T.Keyword and tokens[k].value.upper() == 'ON':
                            # ON 다음 조건 추출
                            condition_tokens = []
                            k += 1
                            while k < len(tokens) and tokens[k].ttype is not T.Keyword:
                                if tokens[k].ttype not in (T.Whitespace, T.Newline):
                                    condition_tokens.append(tokens[k].value)
                                k += 1
                            join_info['condition'] = ' '.join(condition_tokens).strip()
                            break
                        k += 1
                    
                    if join_info['table']:
                        joins.append(join_info)
                
                i += 1
        
        return joins
    
    def extract_subqueries(self) -> List[Dict[str, Any]]:
        """서브쿼리 추출"""
        subqueries = []
        
        for stmt in self.parsed_statements:
            self._extract_subqueries_recursive(stmt, subqueries, depth=0)
        
        return subqueries
    
    def _extract_subqueries_recursive(self, token_list: TokenList, subqueries: List[Dict], depth: int):
        """재귀적으로 서브쿼리 추출"""
        for token in token_list.tokens:
            if isinstance(token, Statement):
                # SELECT로 시작하는 서브쿼리인지 확인
                first_token = token.token_first()
                if first_token and first_token.ttype is T.Keyword and first_token.value.upper() == 'SELECT':
                    subqueries.append({
                        'depth': depth,
                        'query': str(token),
                        'location': self._get_subquery_location(token)
                    })
                    # 중첩된 서브쿼리 찾기
                    self._extract_subqueries_recursive(token, subqueries, depth + 1)
            elif isinstance(token, TokenList):
                self._extract_subqueries_recursive(token, subqueries, depth)
    
    def _get_subquery_location(self, subquery: Statement) -> str:
        """서브쿼리 위치 반환 (WHERE, FROM, SELECT 등)"""
        # 간단한 위치 추정
        query_str = str(subquery).upper()
        if 'WHERE' in query_str:
            return 'WHERE'
        elif 'FROM' in query_str:
            return 'FROM'
        elif 'SELECT' in query_str:
            return 'SELECT'
        return 'UNKNOWN'
    
    def extract_where_clauses(self) -> List[str]:
        """WHERE 절 조건 추출"""
        where_clauses = []
        
        for stmt in self.parsed_statements:
            where_seen = False
            where_tokens = []
            
            for token in stmt.flatten():
                if token.ttype is T.Keyword and token.value.upper() == 'WHERE':
                    where_seen = True
                    continue
                if where_seen:
                    if token.ttype is T.Keyword and token.value.upper() in ['GROUP', 'ORDER', 'HAVING', 'LIMIT']:
                        break
                    if token.ttype not in (T.Whitespace, T.Newline):
                        where_tokens.append(token.value)
            
            if where_tokens:
                where_clauses.append(' '.join(where_tokens))
        
        return where_clauses
    
    def extract_group_by(self) -> List[str]:
        """GROUP BY 절 추출"""
        group_by = []
        
        for stmt in self.parsed_statements:
            group_seen = False
            
            for token in stmt.flatten():
                if token.ttype is T.Keyword and token.value.upper() == 'GROUP':
                    group_seen = True
                    continue
                if group_seen:
                    if token.ttype is T.Keyword and token.value.upper() == 'BY':
                        continue
                    if token.ttype is T.Keyword and token.value.upper() in ['ORDER', 'HAVING', 'LIMIT']:
                        break
                    if token.ttype is None and token.value.strip() and token.value != ',':
                        group_by.append(token.value.strip().strip('"\'`'))
        
        return group_by
    
    def extract_order_by(self) -> List[str]:
        """ORDER BY 절 추출"""
        order_by = []
        
        for stmt in self.parsed_statements:
            order_seen = False
            
            for token in stmt.flatten():
                if token.ttype is T.Keyword and token.value.upper() == 'ORDER':
                    order_seen = True
                    continue
                if order_seen:
                    if token.ttype is T.Keyword and token.value.upper() == 'BY':
                        continue
                    if token.ttype is T.Keyword and token.value.upper() in ['LIMIT', 'OFFSET']:
                        break
                    if token.ttype is None and token.value.strip() and token.value != ',':
                        order_by.append(token.value.strip().strip('"\'`'))
        
        return order_by
    
    def extract_ctes(self) -> List[Dict[str, Any]]:
        """CTE (WITH 절) 추출"""
        ctes = []
        
        for stmt in self.parsed_statements:
            with_seen = False
            cte_name = None
            cte_query = None
            
            tokens = list(stmt.flatten())
            i = 0
            while i < len(tokens):
                token = tokens[i]
                if token.ttype is T.Keyword and token.value.upper() == 'WITH':
                    with_seen = True
                    i += 1
                    continue
                if with_seen:
                    # CTE 이름 추출
                    if token.ttype is None and token.value.strip():
                        cte_name = token.value.strip().split()[0].strip('"\'`')
                        # AS 키워드 찾기
                        j = i + 1
                        while j < len(tokens) and tokens[j].ttype in (T.Whitespace, T.Newline):
                            j += 1
                        if j < len(tokens) and tokens[j].ttype is T.Keyword and tokens[j].value.upper() == 'AS':
                            # CTE 쿼리 추출
                            k = j + 1
                            query_tokens = []
                            paren_count = 0
                            while k < len(tokens):
                                if tokens[k].value == '(':
                                    paren_count += 1
                                elif tokens[k].value == ')':
                                    paren_count -= 1
                                    if paren_count < 0:
                                        break
                                query_tokens.append(tokens[k].value)
                                k += 1
                            cte_query = ' '.join(query_tokens)
                            ctes.append({'name': cte_name, 'query': cte_query})
                            with_seen = False
                i += 1
        
        return ctes
    
    def get_parsed_structure(self) -> Dict[str, Any]:
        """파싱된 구조 반환"""
        return {
            'query_type': self.get_query_type(),
            'tables': self.extract_tables(),
            'columns': self.extract_columns(),
            'joins': self.extract_joins(),
            'subqueries': self.extract_subqueries(),
            'where_clauses': self.extract_where_clauses(),
            'group_by': self.extract_group_by(),
            'order_by': self.extract_order_by(),
            'ctes': self.extract_ctes(),
            'query_length': len(self.query_text),
            'query_lines': self.query_text.count('\n') + 1
        }

# ============================================
# 쿼리 구조 분석기 클래스
# ============================================

class QueryStructureAnalyzer:
    """쿼리 구조 분석 클래스"""
    
    def __init__(self, parser: SQLQueryParser):
        self.parser = parser
        self.structure = parser.get_parsed_structure()
    
    def analyze(self) -> Dict[str, Any]:
        """구조 분석 수행"""
        return {
            'query_type': self.structure['query_type'],
            'table_count': len(self.structure['tables']),
            'tables': self.structure['tables'],
            'column_count': len(self.structure['columns']),
            'join_count': len(self.structure['joins']),
            'join_types': [j['type'] for j in self.structure['joins']],
            'subquery_count': len(self.structure['subqueries']),
            'max_subquery_depth': max([sq['depth'] for sq in self.structure['subqueries']], default=0),
            'where_clause_count': len(self.structure['where_clauses']),
            'group_by_count': len(self.structure['group_by']),
            'order_by_count': len(self.structure['order_by']),
            'cte_count': len(self.structure['ctes']),
            'query_length': self.structure['query_length'],
            'query_lines': self.structure['query_lines']
        }

# ============================================
# 성능 분석기 클래스
# ============================================

class PerformanceAnalyzer:
    """성능 분석 클래스"""
    
    def __init__(self, parser: SQLQueryParser):
        self.parser = parser
        self.structure = parser.get_parsed_structure()
        self.issues = []
        self.recommendations = []
    
    def analyze(self) -> Dict[str, Any]:
        """성능 분석 수행"""
        self.issues = []
        self.recommendations = []
        
        # 인덱스 사용 가능성 검토
        self._check_index_usage()
        
        # 풀 테이블 스캔 위험도
        self._check_full_table_scan()
        
        # 비효율적인 JOIN 패턴
        self._check_inefficient_joins()
        
        # 서브쿼리 성능 이슈
        self._check_subquery_issues()
        
        # 집계 함수 최적화
        self._check_aggregation_optimization()
        
        # LIMIT/OFFSET 효율성
        self._check_limit_offset()
        
        # 함수 사용으로 인한 인덱스 미사용
        self._check_function_usage()
        
        # 성능 점수 계산
        score = self._calculate_performance_score()
        level = self._get_performance_level(score)
        
        return {
            'score': score,
            'level': level,
            'issues': self.issues,
            'recommendations': self.recommendations
        }
    
    def _check_index_usage(self):
        """인덱스 사용 가능성 검토"""
        where_clauses = self.structure['where_clauses']
        joins = self.structure['joins']
        order_by = self.structure['order_by']
        
        # WHERE 절 컬럼 분석
        for clause in where_clauses:
            # 함수 사용 감지
            if re.search(r'\w+\s*\(', clause):
                self.issues.append({
                    'type': 'FUNCTION_IN_WHERE',
                    'severity': 'MEDIUM',
                    'message': f'WHERE 절에서 함수 사용: {clause[:50]}...',
                    'impact': '인덱스 사용 불가능'
                })
                self.recommendations.append({
                    'type': 'INDEX',
                    'priority': 'MEDIUM',
                    'message': '함수 사용을 피하고 컬럼 자체를 사용하도록 쿼리 수정'
                })
        
        # JOIN 조건 분석
        for join in joins:
            if join.get('condition'):
                condition = join['condition']
                if re.search(r'\w+\s*\(', condition):
                    self.issues.append({
                        'type': 'FUNCTION_IN_JOIN',
                        'severity': 'HIGH',
                        'message': f'JOIN 조건에서 함수 사용: {condition[:50]}...',
                        'impact': '인덱스 사용 불가능, 성능 저하'
                    })
        
        # ORDER BY 컬럼 분석
        for col in order_by:
            if re.search(r'\w+\s*\(', col):
                self.issues.append({
                    'type': 'FUNCTION_IN_ORDER_BY',
                    'severity': 'MEDIUM',
                    'message': f'ORDER BY 절에서 함수 사용: {col}',
                    'impact': '인덱스 사용 불가능'
                })
    
    def _check_full_table_scan(self):
        """풀 테이블 스캔 위험도 검사"""
        # WHERE 절이 없는 SELECT 쿼리
        if self.structure['query_type'] == 'SELECT' and not self.structure['where_clauses']:
            self.issues.append({
                'type': 'NO_WHERE_CLAUSE',
                'severity': 'HIGH',
                'message': 'WHERE 절이 없는 SELECT 쿼리',
                'impact': '전체 테이블 스캔 발생 가능성'
            })
            self.recommendations.append({
                'type': 'QUERY_REFACTOR',
                'priority': 'HIGH',
                'message': '필요한 경우 WHERE 절 추가하여 데이터 범위 제한'
            })
    
    def _check_inefficient_joins(self):
        """비효율적인 JOIN 패턴 감지"""
        joins = self.structure['joins']
        
        for join in joins:
            # CROSS JOIN 감지
            if 'CROSS' in join['type']:
                self.issues.append({
                    'type': 'CROSS_JOIN',
                    'severity': 'HIGH',
                    'message': f'CROSS JOIN 사용: {join["table"]}',
                    'impact': '카티션 곱 발생, 성능 저하'
                })
                self.recommendations.append({
                    'type': 'JOIN_OPTIMIZATION',
                    'priority': 'HIGH',
                    'message': 'CROSS JOIN을 적절한 JOIN 조건이 있는 JOIN으로 변경'
                })
            
            # JOIN 조건 없음
            if not join.get('condition'):
                self.issues.append({
                    'type': 'JOIN_WITHOUT_CONDITION',
                    'severity': 'HIGH',
                    'message': f'JOIN 조건 없음: {join["table"]}',
                    'impact': '의도치 않은 카티션 곱 발생 가능'
                })
    
    def _check_subquery_issues(self):
        """서브쿼리 성능 이슈 검사"""
        subqueries = self.structure['subqueries']
        
        # 중첩 서브쿼리
        max_depth = max([sq['depth'] for sq in subqueries], default=0)
        if max_depth > 2:
            self.issues.append({
                'type': 'DEEP_NESTED_SUBQUERY',
                'severity': 'MEDIUM',
                'message': f'깊은 중첩 서브쿼리 (최대 깊이: {max_depth})',
                'impact': '성능 저하, 가독성 저하'
            })
            self.recommendations.append({
                'type': 'QUERY_REFACTOR',
                'priority': 'MEDIUM',
                'message': '서브쿼리를 JOIN이나 CTE로 변환 고려'
            })
        
        # 서브쿼리 개수
        if len(subqueries) > 5:
            self.issues.append({
                'type': 'TOO_MANY_SUBQUERIES',
                'severity': 'MEDIUM',
                'message': f'과도한 서브쿼리 사용 ({len(subqueries)}개)',
                'impact': '성능 저하 가능성'
            })
    
    def _check_aggregation_optimization(self):
        """집계 함수 최적화 검사"""
        query_text = self.parser.query_text.upper()
        
        # COUNT(column) vs COUNT(*)
        if re.search(r'COUNT\s*\(\s*\w+\s*\)', query_text):
            self.recommendations.append({
                'type': 'AGGREGATION_OPTIMIZATION',
                'priority': 'LOW',
                'message': 'NULL 값을 고려하여 COUNT(*) 또는 COUNT(column) 선택 검토'
            })
        
        # DISTINCT 사용
        if 'DISTINCT' in query_text:
            distinct_count = query_text.count('DISTINCT')
            if distinct_count > 3:
                self.issues.append({
                    'type': 'TOO_MANY_DISTINCT',
                    'severity': 'MEDIUM',
                    'message': f'과도한 DISTINCT 사용 ({distinct_count}회)',
                    'impact': '성능 저하'
                })
    
    def _check_limit_offset(self):
        """LIMIT/OFFSET 효율성 검사"""
        query_text = self.parser.query_text.upper()
        
        if 'OFFSET' in query_text and 'LIMIT' in query_text:
            # OFFSET이 큰 경우
            offset_match = re.search(r'OFFSET\s+(\d+)', query_text)
            if offset_match:
                offset_value = int(offset_match.group(1))
                if offset_value > 1000:
                    self.issues.append({
                        'type': 'LARGE_OFFSET',
                        'severity': 'MEDIUM',
                        'message': f'큰 OFFSET 값 사용 ({offset_value})',
                        'impact': 'OFFSET이 클수록 성능 저하'
                    })
                    self.recommendations.append({
                        'type': 'PAGINATION_OPTIMIZATION',
                        'priority': 'MEDIUM',
                        'message': '커서 기반 페이지네이션 고려'
                    })
    
    def _check_function_usage(self):
        """함수 사용으로 인한 인덱스 미사용 검사"""
        query_text = self.parser.query_text
        
        # 일반적인 함수 패턴
        function_patterns = [
            (r'UPPER\s*\(', 'UPPER'),
            (r'LOWER\s*\(', 'LOWER'),
            (r'TRIM\s*\(', 'TRIM'),
            (r'SUBSTRING\s*\(', 'SUBSTRING'),
            (r'CAST\s*\(', 'CAST'),
            (r'::\s*\w+', '타입 변환'),
        ]
        
        for pattern, func_name in function_patterns:
            matches = re.findall(pattern, query_text, re.IGNORECASE)
            if matches:
                count = len(matches)
                if count > 3:
                    self.issues.append({
                        'type': 'FUNCTION_USAGE',
                        'severity': 'MEDIUM',
                        'message': f'{func_name} 함수 다수 사용 ({count}회)',
                        'impact': '인덱스 사용 불가능 가능성'
                    })
    
    def _calculate_performance_score(self) -> int:
        """성능 점수 계산 (0-100)"""
        base_score = 100
        
        # 이슈별 점수 감점
        for issue in self.issues:
            if issue['severity'] == 'HIGH':
                base_score -= 15
            elif issue['severity'] == 'MEDIUM':
                base_score -= 8
            else:
                base_score -= 3
        
        return max(0, min(100, base_score))
    
    def _get_performance_level(self, score: int) -> str:
        """성능 레벨 반환"""
        if score >= 80:
            return 'LOW'
        elif score >= 60:
            return 'MEDIUM'
        else:
            return 'HIGH'

# ============================================
# 최적화 제안기 클래스
# ============================================

class OptimizationAdvisor:
    """최적화 제안 클래스"""
    
    def __init__(self, parser: SQLQueryParser, performance_analyzer: PerformanceAnalyzer):
        self.parser = parser
        self.performance_analyzer = performance_analyzer
        self.structure = parser.get_parsed_structure()
        self.suggestions = []
    
    def analyze(self) -> Dict[str, Any]:
        """최적화 제안 생성"""
        self.suggestions = []
        
        # 인덱스 제안
        self._suggest_indexes()
        
        # 쿼리 리팩토링 제안
        self._suggest_refactoring()
        
        # 조건 최적화 제안
        self._suggest_condition_optimization()
        
        # JOIN 최적화 제안
        self._suggest_join_optimization()
        
        # 집계 최적화 제안
        self._suggest_aggregation_optimization()
        
        # 우선순위별 정렬
        self.suggestions.sort(key=lambda x: {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}[x['priority']], reverse=True)
        
        return {
            'suggestions': self.suggestions,
            'total_count': len(self.suggestions),
            'high_priority_count': len([s for s in self.suggestions if s['priority'] == 'HIGH']),
            'medium_priority_count': len([s for s in self.suggestions if s['priority'] == 'MEDIUM']),
            'low_priority_count': len([s for s in self.suggestions if s['priority'] == 'LOW'])
        }
    
    def _suggest_indexes(self):
        """인덱스 제안"""
        where_clauses = self.structure['where_clauses']
        joins = self.structure['joins']
        order_by = self.structure['order_by']
        
        # WHERE 절 컬럼 인덱스 제안
        indexed_columns = set()
        for clause in where_clauses:
            # 컬럼명 추출 (간단한 패턴)
            col_matches = re.findall(r'\b(\w+)\s*[=<>!]', clause)
            for col in col_matches:
                if col.upper() not in ['AND', 'OR', 'NOT', 'IN', 'LIKE', 'BETWEEN']:
                    indexed_columns.add(col)
        
        if indexed_columns:
            self.suggestions.append({
                'type': 'INDEX',
                'priority': 'HIGH',
                'message': f'WHERE 절 컬럼에 인덱스 추가 고려: {", ".join(list(indexed_columns)[:5])}',
                'example': f'CREATE INDEX idx_name ON table_name ({", ".join(list(indexed_columns)[:3])});',
                'expected_improvement': '30-50%'
            })
        
        # JOIN 조건 인덱스 제안
        join_columns = set()
        for join in joins:
            if join.get('condition'):
                condition = join['condition']
                col_matches = re.findall(r'\b(\w+)\s*=', condition)
                for col in col_matches:
                    if col.upper() not in ['AND', 'OR', 'ON']:
                        join_columns.add(col)
        
        if join_columns:
            self.suggestions.append({
                'type': 'INDEX',
                'priority': 'HIGH',
                'message': f'JOIN 조건 컬럼에 인덱스 추가 고려: {", ".join(list(join_columns)[:5])}',
                'example': f'CREATE INDEX idx_join ON table_name ({", ".join(list(join_columns)[:3])});',
                'expected_improvement': '40-60%'
            })
        
        # ORDER BY 컬럼 인덱스 제안
        if order_by:
            self.suggestions.append({
                'type': 'INDEX',
                'priority': 'MEDIUM',
                'message': f'ORDER BY 컬럼에 인덱스 추가 고려: {", ".join(order_by[:3])}',
                'example': f'CREATE INDEX idx_order ON table_name ({", ".join(order_by[:2])});',
                'expected_improvement': '20-40%'
            })
    
    def _suggest_refactoring(self):
        """쿼리 리팩토링 제안"""
        subqueries = self.structure['subqueries']
        
        # 서브쿼리 → JOIN 변환 제안
        if len(subqueries) > 0:
            self.suggestions.append({
                'type': 'QUERY_REFACTOR',
                'priority': 'MEDIUM',
                'message': f'서브쿼리({len(subqueries)}개)를 JOIN으로 변환 고려',
                'example': '# 서브쿼리: SELECT * FROM table1 WHERE id IN (SELECT id FROM table2)\n# JOIN 변환: SELECT t1.* FROM table1 t1 INNER JOIN table2 t2 ON t1.id = t2.id',
                'expected_improvement': '20-40%'
            })
        
        # IN → EXISTS 변환 제안
        query_text = self.parser.query_text.upper()
        if ' IN (' in query_text and 'SELECT' in query_text:
            self.suggestions.append({
                'type': 'QUERY_REFACTOR',
                'priority': 'LOW',
                'message': 'IN 서브쿼리를 EXISTS로 변환 고려 (NULL 처리 개선)',
                'example': '# IN: WHERE id IN (SELECT id FROM table)\n# EXISTS: WHERE EXISTS (SELECT 1 FROM table WHERE table.id = main.id)',
                'expected_improvement': '10-20%'
            })
        
        # DISTINCT 제거 가능 여부
        if 'DISTINCT' in query_text:
            distinct_count = query_text.count('DISTINCT')
            if distinct_count > 2:
                self.suggestions.append({
                    'type': 'QUERY_REFACTOR',
                    'priority': 'MEDIUM',
                    'message': f'DISTINCT 사용({distinct_count}회) 최소화 고려',
                    'example': 'GROUP BY를 사용하여 DISTINCT 대체 가능 여부 검토',
                    'expected_improvement': '15-30%'
                })
    
    def _suggest_condition_optimization(self):
        """조건 최적화 제안"""
        where_clauses = self.structure['where_clauses']
        
        if where_clauses:
            # 인덱스 사용 가능한 조건 우선 배치
            self.suggestions.append({
                'type': 'CONDITION_OPTIMIZATION',
                'priority': 'LOW',
                'message': 'WHERE 절 조건 순서 최적화: 인덱스 사용 가능한 조건을 앞에 배치',
                'example': 'WHERE indexed_column = value AND function(column) = value',
                'expected_improvement': '5-15%'
            })
    
    def _suggest_join_optimization(self):
        """JOIN 최적화 제안"""
        joins = self.structure['joins']
        
        if len(joins) > 3:
            self.suggestions.append({
                'type': 'JOIN_OPTIMIZATION',
                'priority': 'MEDIUM',
                'message': f'다중 JOIN({len(joins)}개) 순서 최적화 고려: 작은 테이블을 먼저 JOIN',
                'example': '작은 테이블을 FROM 절에 배치하고 큰 테이블을 나중에 JOIN',
                'expected_improvement': '10-25%'
            })
    
    def _suggest_aggregation_optimization(self):
        """집계 최적화 제안"""
        query_text = self.parser.query_text.upper()
        
        # HAVING → WHERE 이동 가능 여부
        if 'HAVING' in query_text and 'GROUP BY' in query_text:
            self.suggestions.append({
                'type': 'AGGREGATION_OPTIMIZATION',
                'priority': 'LOW',
                'message': 'HAVING 절의 조건 중 WHERE 절로 이동 가능한 것 검토',
                'example': '집계 함수를 사용하지 않는 조건은 WHERE 절로 이동',
                'expected_improvement': '5-15%'
            })

# ============================================
# 복잡도 분석기 클래스
# ============================================

class ComplexityAnalyzer:
    """복잡도 분석 클래스"""
    
    def __init__(self, parser: SQLQueryParser):
        self.parser = parser
        self.structure = parser.get_parsed_structure()
    
    def analyze(self) -> Dict[str, Any]:
        """복잡도 분석 수행"""
        metrics = {
            'query_length': self.structure['query_length'],
            'query_lines': self.structure['query_lines'],
            'table_count': len(self.structure['tables']),
            'join_count': len(self.structure['joins']),
            'subquery_count': len(self.structure['subqueries']),
            'max_subquery_depth': max([sq['depth'] for sq in self.structure['subqueries']], default=0),
            'where_clause_count': len(self.structure['where_clauses']),
            'column_count': len(self.structure['columns']),
            'group_by_count': len(self.structure['group_by']),
            'order_by_count': len(self.structure['order_by']),
            'cte_count': len(self.structure['ctes']),
            'union_count': self.parser.query_text.upper().count('UNION')
        }
        
        # 복잡도 점수 계산
        score = self._calculate_complexity_score(metrics)
        level = self._get_complexity_level(score)
        
        return {
            'score': score,
            'level': level,
            'metrics': metrics
        }
    
    def _calculate_complexity_score(self, metrics: Dict[str, Any]) -> int:
        """복잡도 점수 계산 (0-100, 높을수록 복잡)"""
        score = 0
        
        # 쿼리 길이 (라인 수)
        if metrics['query_lines'] > 3000:
            score += 30
        elif metrics['query_lines'] > 1000:
            score += 20
        elif metrics['query_lines'] > 500:
            score += 10
        
        # 테이블 수
        if metrics['table_count'] > 10:
            score += 15
        elif metrics['table_count'] > 5:
            score += 10
        elif metrics['table_count'] > 3:
            score += 5
        
        # JOIN 수
        if metrics['join_count'] > 10:
            score += 15
        elif metrics['join_count'] > 5:
            score += 10
        elif metrics['join_count'] > 3:
            score += 5
        
        # 서브쿼리 수 및 깊이
        if metrics['max_subquery_depth'] > 3:
            score += 15
        elif metrics['max_subquery_depth'] > 2:
            score += 10
        elif metrics['max_subquery_depth'] > 1:
            score += 5
        
        if metrics['subquery_count'] > 10:
            score += 10
        elif metrics['subquery_count'] > 5:
            score += 5
        
        # WHERE 조건 수
        if metrics['where_clause_count'] > 10:
            score += 5
        
        # UNION 수
        if metrics['union_count'] > 3:
            score += 5
        
        return min(100, score)
    
    def _get_complexity_level(self, score: int) -> str:
        """복잡도 레벨 반환"""
        if score >= 70:
            return 'VERY_HIGH'
        elif score >= 50:
            return 'HIGH'
        elif score >= 30:
            return 'MEDIUM'
        else:
            return 'LOW'

# ============================================
# 보안 분석기 클래스
# ============================================

class SecurityAnalyzer:
    """보안 분석 클래스"""
    
    def __init__(self, parser: SQLQueryParser):
        self.parser = parser
        self.query_text = parser.query_text
        self.vulnerabilities = []
    
    def analyze(self) -> Dict[str, Any]:
        """보안 분석 수행"""
        self.vulnerabilities = []
        
        # SQL Injection 취약점 검사
        self._check_sql_injection()
        
        # 권한 관련 이슈
        self._check_permission_issues()
        
        # 데이터 노출 위험
        self._check_data_exposure()
        
        # 인젝션 패턴 감지
        self._check_injection_patterns()
        
        # 보안 점수 계산
        score = self._calculate_security_score()
        level = self._get_security_level(score)
        
        return {
            'score': score,
            'level': level,
            'vulnerabilities': self.vulnerabilities
        }
    
    def _check_sql_injection(self):
        """SQL Injection 취약점 검사"""
        # 문자열 연결 사용 감지
        if re.search(r'\+\s*["\']', self.query_text) or re.search(r'["\']\s*\+', self.query_text):
            self.vulnerabilities.append({
                'type': 'STRING_CONCATENATION',
                'severity': 'HIGH',
                'message': '문자열 연결 연산자 사용 감지',
                'impact': 'SQL Injection 취약점 가능성',
                'recommendation': '파라미터화된 쿼리 사용'
            })
        
        # 동적 쿼리 생성 감지 (간단한 패턴)
        dynamic_patterns = [
            r'EXEC\s*\(',
            r'EXECUTE\s+IMMEDIATE',
            r'PREPARE\s+\w+\s+FROM',
        ]
        for pattern in dynamic_patterns:
            if re.search(pattern, self.query_text, re.IGNORECASE):
                self.vulnerabilities.append({
                    'type': 'DYNAMIC_QUERY',
                    'severity': 'CRITICAL',
                    'message': f'동적 쿼리 생성 패턴 감지: {pattern}',
                    'impact': 'SQL Injection 취약점',
                    'recommendation': '정적 쿼리 사용 또는 입력 검증 강화'
                })
        
        # 사용자 입력 직접 사용 감지 (간단한 패턴)
        # 주석 처리된 코드나 변수명 패턴
        if re.search(r'\$\{?\w+\}?', self.query_text) or re.search(r'%s|%d', self.query_text):
            self.vulnerabilities.append({
                'type': 'DIRECT_INPUT',
                'severity': 'HIGH',
                'message': '변수 치환 패턴 감지',
                'impact': 'SQL Injection 취약점 가능성',
                'recommendation': '파라미터화된 쿼리 사용'
            })
    
    def _check_permission_issues(self):
        """권한 관련 이슈 검사"""
        query_upper = self.query_text.upper()
        
        # 과도한 권한 사용
        if 'GRANT ALL' in query_upper:
            self.vulnerabilities.append({
                'type': 'EXCESSIVE_PERMISSION',
                'severity': 'MEDIUM',
                'message': 'GRANT ALL 사용 감지',
                'impact': '과도한 권한 부여',
                'recommendation': '최소 권한 원칙 적용'
            })
    
    def _check_data_exposure(self):
        """데이터 노출 위험 검사"""
        query_upper = self.query_text.upper()
        
        # SELECT * 사용
        if 'SELECT *' in query_upper:
            count = query_upper.count('SELECT *')
            if count > 2:
                self.vulnerabilities.append({
                    'type': 'SELECT_ALL',
                    'severity': 'LOW',
                    'message': f'SELECT * 다수 사용 ({count}회)',
                    'impact': '불필요한 데이터 노출 가능성',
                    'recommendation': '필요한 컬럼만 명시적으로 선택'
                })
    
    def _check_injection_patterns(self):
        """인젝션 패턴 감지"""
        query_upper = self.query_text.upper()
        
        # UNION 기반 인젝션 패턴
        if 'UNION' in query_upper and 'SELECT' in query_upper:
            # 의심스러운 패턴
            if re.search(r'UNION\s+SELECT\s+NULL', query_upper):
                self.vulnerabilities.append({
                    'type': 'UNION_INJECTION_PATTERN',
                    'severity': 'MEDIUM',
                    'message': 'UNION SELECT NULL 패턴 감지',
                    'impact': '인젝션 시도 가능성',
                    'recommendation': '입력 검증 및 화이트리스트 적용'
                })
    
    def _calculate_security_score(self) -> int:
        """보안 점수 계산 (0-100, 높을수록 안전)"""
        base_score = 100
        
        for vuln in self.vulnerabilities:
            if vuln['severity'] == 'CRITICAL':
                base_score -= 30
            elif vuln['severity'] == 'HIGH':
                base_score -= 20
            elif vuln['severity'] == 'MEDIUM':
                base_score -= 10
            else:
                base_score -= 5
        
        return max(0, min(100, base_score))
    
    def _get_security_level(self, score: int) -> str:
        """보안 레벨 반환"""
        if score >= 90:
            return 'SAFE'
        elif score >= 70:
            return 'LOW'
        elif score >= 50:
            return 'MEDIUM'
        elif score >= 30:
            return 'HIGH'
        else:
            return 'CRITICAL'

# ============================================
# 데이터 리니지 분석기 클래스
# ============================================

class DataLineageAnalyzer:
    """데이터 리니지(Data Lineage) 분석 클래스 - 테이블 간 관계 시각화"""
    
    def __init__(self, parser: SQLQueryParser, structure_analysis: Dict[str, Any]):
        self.parser = parser
        self.structure = parser.get_parsed_structure()
        self.structure_analysis = structure_analysis
        self.join_relationships = []
        self.cte_dependencies = []
        self.subquery_relationships = []
        self.all_tables = set()
        self.all_ctes = set()
    
    def analyze(self) -> Dict[str, Any]:
        """리니지 분석 수행"""
        # JOIN 관계 추출
        self.join_relationships = self.extract_join_relationships()
        
        # CTE 의존성 추출
        self.cte_dependencies = self.extract_cte_dependencies()
        
        # 서브쿼리 관계 추출
        self.subquery_relationships = self.extract_subquery_relationships()
        
        # 모든 테이블 및 CTE 수집
        self.all_tables = set(self.structure['tables'])
        
        # JOIN 관계에서 테이블 추가
        for join_rel in self.join_relationships:
            left_table = join_rel.get('left_table')
            right_table = join_rel.get('right_table')
            if left_table and left_table != 'unknown':
                self.all_tables.add(left_table)
            if right_table and right_table != 'unknown':
                self.all_tables.add(right_table)
        
        # CTE 의존성에서 테이블 추가
        for cte_dep in self.cte_dependencies:
            referenced_tables = cte_dep.get('referenced_tables', [])
            self.all_tables.update(referenced_tables)
        
        # 서브쿼리 관계에서 테이블 추가
        for subq_rel in self.subquery_relationships:
            referenced_tables = subq_rel.get('referenced_tables', [])
            self.all_tables.update(referenced_tables)
        
        # CTE 처리
        for cte in self.structure['ctes']:
            self.all_ctes.add(cte['name'])
            # CTE가 참조하는 테이블도 추가
            cte_parser = SQLQueryParser(cte['query'])
            self.all_tables.update(cte_parser.extract_tables())
        
        return {
            'tables': sorted(list(self.all_tables)),
            'ctes': sorted(list(self.all_ctes)),
            'join_relationships': self.join_relationships,
            'cte_dependencies': self.cte_dependencies,
            'subquery_relationships': self.subquery_relationships
        }
    
    def extract_join_relationships(self) -> List[Dict[str, Any]]:
        """JOIN 관계 추출"""
        relationships = []
        joins = self.structure['joins']
        tables = self.structure['tables']
        
        # FROM 절의 첫 번째 테이블 찾기
        main_table = None
        if tables:
            main_table = tables[0]
        
        for join_info in joins:
            join_table = join_info.get('table')
            if not join_table:
                continue
            
            # JOIN 조건에서 테이블 추출 시도
            condition = join_info.get('condition', '')
            left_table = main_table
            right_table = join_table
            
            # JOIN 조건에서 테이블명 추출
            if condition:
                # table1.column = table2.column 패턴 찾기
                parts = re.split(r'[=<>!]+', condition)
                for part in parts:
                    part = part.strip()
                    if '.' in part:
                        table_name = part.split('.')[0].strip().strip('"\'`')
                        if table_name in tables:
                            if not left_table or left_table == main_table:
                                left_table = table_name
                            else:
                                right_table = table_name
            
            relationships.append({
                'left_table': left_table or 'unknown',
                'right_table': right_table,
                'join_type': join_info.get('type', 'JOIN'),
                'condition': condition
            })
            
            # 다음 JOIN을 위한 메인 테이블 업데이트
            main_table = right_table
        
        return relationships
    
    def extract_cte_dependencies(self) -> List[Dict[str, Any]]:
        """CTE 의존성 추출"""
        dependencies = []
        ctes = self.structure['ctes']
        
        for cte in ctes:
            cte_name = cte['name']
            cte_query = cte['query']
            
            # CTE 쿼리 파싱
            try:
                cte_parser = SQLQueryParser(cte_query)
                referenced_tables = cte_parser.extract_tables()
                referenced_ctes = []
                
                # 다른 CTE 참조 확인
                for other_cte in ctes:
                    if other_cte['name'] != cte_name:
                        # CTE 쿼리에 다른 CTE 이름이 포함되어 있는지 확인
                        if other_cte['name'].lower() in cte_query.lower():
                            referenced_ctes.append(other_cte['name'])
                
                dependencies.append({
                    'cte_name': cte_name,
                    'referenced_tables': referenced_tables,
                    'referenced_ctes': referenced_ctes
                })
            except Exception as e:
                # 파싱 실패 시 기본 정보만 저장
                dependencies.append({
                    'cte_name': cte_name,
                    'referenced_tables': [],
                    'referenced_ctes': [],
                    'error': str(e)
                })
        
        return dependencies
    
    def extract_subquery_relationships(self) -> List[Dict[str, Any]]:
        """서브쿼리 관계 추출"""
        relationships = []
        subqueries = self.structure['subqueries']
        
        for idx, subquery_info in enumerate(subqueries):
            subquery_query = subquery_info.get('query', '')
            location = subquery_info.get('location', 'UNKNOWN')
            depth = subquery_info.get('depth', 0)
            
            # 서브쿼리 파싱
            try:
                subquery_parser = SQLQueryParser(subquery_query)
                referenced_tables = subquery_parser.extract_tables()
                
                relationships.append({
                    'subquery_index': idx + 1,
                    'depth': depth,
                    'location': location,
                    'referenced_tables': referenced_tables
                })
            except Exception as e:
                relationships.append({
                    'subquery_index': idx + 1,
                    'depth': depth,
                    'location': location,
                    'referenced_tables': [],
                    'error': str(e)
                })
        
        return relationships
    
    def generate_mermaid_diagram(self) -> str:
        """Mermaid 다이어그램 생성"""
        lines = ['graph TD']
        
        # 노드 정의
        node_id_map = {}
        node_counter = 1
        
        # 테이블 노드
        for table in sorted(self.all_tables):
            node_id = f'T{node_counter}'
            node_id_map[table] = node_id
            lines.append(f'    {node_id}["{table}"]')
            node_counter += 1
        
        # CTE 노드
        for cte in sorted(self.all_ctes):
            node_id = f'C{node_counter}'
            node_id_map[cte] = node_id
            lines.append(f'    {node_id}["{cte}<br/>(CTE)"]')
            node_counter += 1
        
        lines.append('')
        
        # JOIN 관계
        for join_rel in self.join_relationships:
            left = join_rel.get('left_table', 'unknown')
            right = join_rel.get('right_table', 'unknown')
            join_type = join_rel.get('join_type', 'JOIN')
            
            if left in node_id_map and right in node_id_map:
                label = join_type.replace('JOIN', '').strip() or 'JOIN'
                lines.append(f'    {node_id_map[left]} -->|"{label}"| {node_id_map[right]}')
        
        # CTE 의존성
        for cte_dep in self.cte_dependencies:
            cte_name = cte_dep.get('cte_name', '')
            if cte_name not in node_id_map:
                continue
            
            # CTE가 참조하는 테이블
            for table in cte_dep.get('referenced_tables', []):
                if table in node_id_map:
                    lines.append(f'    {node_id_map[table]} -->|"CTE 참조"| {node_id_map[cte_name]}')
            
            # CTE가 참조하는 다른 CTE
            for ref_cte in cte_dep.get('referenced_ctes', []):
                if ref_cte in node_id_map:
                    lines.append(f'    {node_id_map[ref_cte]} -->|"CTE 의존"| {node_id_map[cte_name]}')
        
        # 서브쿼리 관계 (간단히 표시)
        for subq_rel in self.subquery_relationships:
            location = subq_rel.get('location', 'UNKNOWN')
            depth = subq_rel.get('depth', 0)
            for table in subq_rel.get('referenced_tables', []):
                if table in node_id_map:
                    # 서브쿼리 노드는 생성하지 않고 주석으로 표시
                    # 필요시 서브쿼리 노드도 추가 가능
                    pass
        
        return '\n'.join(lines)
    
    def generate_lineage_json(self) -> Dict[str, Any]:
        """JSON 형식 리니지 데이터 생성"""
        return {
            'metadata': {
                'total_tables': len(self.all_tables),
                'total_ctes': len(self.all_ctes),
                'total_joins': len(self.join_relationships),
                'total_cte_dependencies': len(self.cte_dependencies),
                'total_subqueries': len(self.subquery_relationships)
            },
            'tables': sorted(list(self.all_tables)),
            'ctes': sorted(list(self.all_ctes)),
            'relationships': {
                'joins': self.join_relationships,
                'cte_dependencies': self.cte_dependencies,
                'subquery_relationships': self.subquery_relationships
            }
        }

# ============================================
# 영향도 분석기 클래스
# ============================================

class ImpactAnalyzer:
    """영향도 분석 클래스 - 특정 테이블/컬럼 이슈 발생 시 영향받는 쿼리 분석"""
    
    def __init__(self, parser: SQLQueryParser, lineage_analyzer: DataLineageAnalyzer, 
                 structure_analyzer: QueryStructureAnalyzer):
        self.parser = parser
        self.lineage_analyzer = lineage_analyzer
        self.structure_analyzer = structure_analyzer
        self.structure = parser.get_parsed_structure()
        self.lineage_data = lineage_analyzer.analyze()
        self.query_text = parser.query_text
        self.query_lines = self.query_text.split('\n')
        
    def analyze(self, target_table: str, target_column: Optional[str] = None) -> Dict[str, Any]:
        """영향도 분석 수행"""
        target_table = target_table.strip().lower()
        target_column = target_column.strip().lower() if target_column else None
        
        # 직접 영향 분석
        direct_impacts = self._analyze_direct_impacts(target_table, target_column)
        
        # 간접 영향 분석
        indirect_impacts = self._analyze_indirect_impacts(target_table, target_column)
        
        # 영향받는 테이블 및 CTE 추출
        affected_tables = self._extract_affected_tables(target_table, direct_impacts, indirect_impacts)
        affected_ctes = self._extract_affected_ctes(target_table, target_column, direct_impacts, indirect_impacts)
        
        # 영향도 점수 계산
        impact_score = self._calculate_impact_score(direct_impacts, indirect_impacts)
        impact_level = self._get_impact_level(impact_score)
        
        # 권장사항 생성
        recommendations = self._generate_recommendations(target_table, target_column, 
                                                         direct_impacts, indirect_impacts, impact_level)
        
        return {
            'target': {
                'table': target_table,
                'column': target_column
            },
            'impact_level': impact_level,
            'impact_score': impact_score,
            'direct_impacts': direct_impacts,
            'indirect_impacts': indirect_impacts,
            'affected_tables': sorted(list(affected_tables)),
            'affected_ctes': sorted(list(affected_ctes)),
            'statistics': {
                'total_direct_impacts': len(direct_impacts),
                'total_indirect_impacts': len(indirect_impacts),
                'total_affected_tables': len(affected_tables),
                'total_affected_ctes': len(affected_ctes)
            },
            'recommendations': recommendations
        }
    
    def _analyze_direct_impacts(self, target_table: str, target_column: Optional[str]) -> List[Dict[str, Any]]:
        """직접 영향 분석"""
        impacts = []
        query_upper = self.query_text.upper()
        
        # 테이블 사용 위치 찾기
        table_patterns = [
            (r'FROM\s+' + re.escape(target_table) + r'\b', 'FROM'),
            (r'JOIN\s+' + re.escape(target_table) + r'\b', 'JOIN'),
            (r'UPDATE\s+' + re.escape(target_table) + r'\b', 'UPDATE'),
            (r'INSERT\s+INTO\s+' + re.escape(target_table) + r'\b', 'INSERT'),
            (r'DELETE\s+FROM\s+' + re.escape(target_table) + r'\b', 'DELETE')
        ]
        
        for pattern, impact_type in table_patterns:
            matches = re.finditer(pattern, query_upper, re.IGNORECASE)
            for match in matches:
                line_num = self._get_line_number(match.start())
                snippet = self._get_snippet(match.start(), match.end())
                
                impact_level = 'HIGH' if impact_type in ['FROM', 'JOIN'] else 'MEDIUM'
                impacts.append({
                    'type': impact_type,
                    'location': f'line {line_num}',
                    'line_number': line_num,
                    'query_snippet': snippet,
                    'impact_level': impact_level,
                    'impact_type': 'direct'
                })
        
        # 컬럼 사용 위치 찾기
        if target_column:
            column_patterns = [
                (r'\b' + re.escape(target_table) + r'\.' + re.escape(target_column) + r'\b', 'TABLE_COLUMN'),
                (r'\b' + re.escape(target_column) + r'\b', 'COLUMN')
            ]
            
            for pattern, pattern_type in column_patterns:
                matches = re.finditer(pattern, query_upper, re.IGNORECASE)
                for match in matches:
                    line_num = self._get_line_number(match.start())
                    snippet = self._get_snippet(match.start(), match.end())
                    
                    # 컬럼이 사용된 위치 확인
                    context = self._get_context(match.start())
                    impact_type = self._determine_column_usage_type(context)
                    
                    if impact_type == 'SELECT':
                        impact_level = 'CRITICAL'
                    elif impact_type in ['WHERE', 'JOIN']:
                        impact_level = 'HIGH'
                    elif impact_type in ['GROUP_BY', 'ORDER_BY']:
                        impact_level = 'MEDIUM'
                    else:
                        impact_level = 'LOW'
                    
                    impacts.append({
                        'type': impact_type,
                        'location': f'line {line_num}',
                        'line_number': line_num,
                        'query_snippet': snippet,
                        'impact_level': impact_level,
                        'impact_type': 'direct',
                        'column': target_column
                    })
        
        return impacts
    
    def _analyze_indirect_impacts(self, target_table: str, target_column: Optional[str]) -> List[Dict[str, Any]]:
        """간접 영향 분석"""
        impacts = []
        
        # JOIN 관계를 통한 간접 영향
        for join_rel in self.lineage_data.get('join_relationships', []):
            left_table = join_rel.get('left_table', '').lower()
            right_table = join_rel.get('right_table', '').lower()
            
            if target_table in [left_table, right_table]:
                # JOIN으로 연결된 다른 테이블 찾기
                related_table = right_table if left_table == target_table else left_table
                if related_table != target_table:
                    impacts.append({
                        'type': 'JOIN_RELATIONSHIP',
                        'related_table': related_table,
                        'join_type': join_rel.get('join_type', 'JOIN'),
                        'condition': join_rel.get('condition', ''),
                        'impact_level': 'MEDIUM',
                        'impact_type': 'indirect',
                        'path': f'{target_table} -> {related_table} (JOIN)'
                    })
        
        # CTE 의존성을 통한 간접 영향
        for cte_dep in self.lineage_data.get('cte_dependencies', []):
            cte_name = cte_dep.get('cte_name', '')
            referenced_tables = [t.lower() for t in cte_dep.get('referenced_tables', [])]
            
            if target_table in referenced_tables:
                impacts.append({
                    'type': 'CTE_DEPENDENCY',
                    'cte_name': cte_name,
                    'referenced_tables': referenced_tables,
                    'impact_level': 'LOW',
                    'impact_type': 'indirect',
                    'path': f'{target_table} -> {cte_name} (CTE)'
                })
        
        # 서브쿼리 관계를 통한 간접 영향
        for subq_rel in self.lineage_data.get('subquery_relationships', []):
            referenced_tables = [t.lower() for t in subq_rel.get('referenced_tables', [])]
            
            if target_table in referenced_tables:
                impacts.append({
                    'type': 'SUBQUERY_RELATIONSHIP',
                    'subquery_index': subq_rel.get('subquery_index', 0),
                    'depth': subq_rel.get('depth', 0),
                    'location': subq_rel.get('location', 'UNKNOWN'),
                    'referenced_tables': referenced_tables,
                    'impact_level': 'LOW',
                    'impact_type': 'indirect',
                    'path': f'{target_table} -> Subquery #{subq_rel.get("subquery_index", 0)}'
                })
        
        return impacts
    
    def _extract_affected_tables(self, target_table: str, direct_impacts: List[Dict], 
                                  indirect_impacts: List[Dict]) -> Set[str]:
        """영향받는 테이블 추출"""
        affected_tables = set()
        
        # JOIN 관계에서 영향받는 테이블
        for join_rel in self.lineage_data.get('join_relationships', []):
            left_table = join_rel.get('left_table', '').lower()
            right_table = join_rel.get('right_table', '').lower()
            
            if target_table in [left_table, right_table]:
                affected_tables.add(left_table)
                affected_tables.add(right_table)
        
        # 간접 영향에서 영향받는 테이블
        for impact in indirect_impacts:
            if 'related_table' in impact:
                affected_tables.add(impact['related_table'])
            if 'referenced_tables' in impact:
                affected_tables.update([t.lower() for t in impact['referenced_tables']])
        
        # 타겟 테이블 제거
        affected_tables.discard(target_table.lower())
        
        return affected_tables
    
    def _extract_affected_ctes(self, target_table: str, target_column: Optional[str],
                               direct_impacts: List[Dict], indirect_impacts: List[Dict]) -> Set[str]:
        """영향받는 CTE 추출"""
        affected_ctes = set()
        
        # CTE 의존성에서 영향받는 CTE
        for cte_dep in self.lineage_data.get('cte_dependencies', []):
            referenced_tables = [t.lower() for t in cte_dep.get('referenced_tables', [])]
            
            if target_table in referenced_tables:
                affected_ctes.add(cte_dep.get('cte_name', ''))
        
        # 간접 영향에서 영향받는 CTE
        for impact in indirect_impacts:
            if impact.get('type') == 'CTE_DEPENDENCY':
                affected_ctes.add(impact.get('cte_name', ''))
        
        return affected_ctes
    
    def _calculate_impact_score(self, direct_impacts: List[Dict], indirect_impacts: List[Dict]) -> int:
        """영향도 점수 계산 (0-100)"""
        max_score = 0
        
        # 직접 영향 점수
        for impact in direct_impacts:
            level = impact.get('impact_level', 'LOW')
            if level == 'CRITICAL':
                score = 100
            elif level == 'HIGH':
                score = 80
            elif level == 'MEDIUM':
                score = 60
            else:
                score = 40
            
            max_score = max(max_score, score)
        
        # 간접 영향 점수
        for impact in indirect_impacts:
            level = impact.get('impact_level', 'LOW')
            if level == 'MEDIUM':
                score = 50
            else:
                score = 30
            
            max_score = max(max_score, score)
        
        return max_score
    
    def _get_impact_level(self, score: int) -> str:
        """영향도 수준 반환"""
        if score >= 90:
            return 'CRITICAL'
        elif score >= 70:
            return 'HIGH'
        elif score >= 50:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _generate_recommendations(self, target_table: str, target_column: Optional[str],
                                 direct_impacts: List[Dict], indirect_impacts: List[Dict],
                                 impact_level: str) -> List[Dict[str, Any]]:
        """권장사항 생성"""
        recommendations = []
        
        if impact_level == 'CRITICAL':
            recommendations.append({
                'priority': 'CRITICAL',
                'message': f'{target_table} 테이블 변경 시 모든 관련 쿼리를 반드시 검토해야 합니다.',
                'action': '변경 전 모든 영향받는 쿼리 수정 필요'
            })
        elif impact_level == 'HIGH':
            recommendations.append({
                'priority': 'HIGH',
                'message': f'{target_table} 테이블 변경 시 주요 쿼리들을 검토해야 합니다.',
                'action': '변경 전 영향받는 쿼리 검토 및 수정 필요'
            })
        
        if target_column:
            direct_column_impacts = [i for i in direct_impacts if i.get('column') == target_column]
            if direct_column_impacts:
                select_impacts = [i for i in direct_column_impacts if i.get('type') == 'SELECT']
                if select_impacts:
                    recommendations.append({
                        'priority': 'HIGH',
                        'message': f'{target_column} 컬럼이 SELECT 절에서 사용되고 있습니다.',
                        'action': '컬럼 삭제 시 쿼리 결과에 영향을 미칩니다.'
                    })
        
        if len(direct_impacts) + len(indirect_impacts) > 10:
            recommendations.append({
                'priority': 'MEDIUM',
                'message': f'영향받는 쿼리가 많습니다 ({len(direct_impacts) + len(indirect_impacts)}개).',
                'action': '단계별로 변경을 진행하는 것을 권장합니다.'
            })
        
        return recommendations
    
    def _get_line_number(self, position: int) -> int:
        """문자 위치에서 라인 번호 반환"""
        return self.query_text[:position].count('\n') + 1
    
    def _get_snippet(self, start: int, end: int, context: int = 50) -> str:
        """쿼리 스니펫 추출"""
        snippet_start = max(0, start - context)
        snippet_end = min(len(self.query_text), end + context)
        snippet = self.query_text[snippet_start:snippet_end]
        return snippet.strip()
    
    def _get_context(self, position: int, context: int = 100) -> str:
        """컬럼 사용 컨텍스트 추출"""
        context_start = max(0, position - context)
        context_end = min(len(self.query_text), position + context)
        return self.query_text[context_start:context_end].upper()
    
    def _determine_column_usage_type(self, context: str) -> str:
        """컬럼 사용 타입 결정"""
        context_upper = context.upper()
        
        # SELECT 절 확인
        if 'SELECT' in context_upper and 'FROM' in context_upper:
            try:
                select_pos = context_upper.index('SELECT')
                from_pos = context_upper.index('FROM')
                if select_pos < from_pos:
                    return 'SELECT'
            except ValueError:
                pass
        
        # WHERE 절 확인
        if 'WHERE' in context_upper:
            return 'WHERE'
        
        # JOIN 절 확인
        if 'JOIN' in context_upper and 'ON' in context_upper:
            return 'JOIN'
        elif 'GROUP BY' in context_upper:
            return 'GROUP_BY'
        elif 'ORDER BY' in context_upper:
            return 'ORDER_BY'
        elif 'HAVING' in context_upper:
            return 'HAVING'
        else:
            return 'OTHER'

# ============================================
# 리포트 생성기 클래스
# ============================================

class ReportGenerator:
    """JSON 및 마크다운 리포트 생성 클래스"""
    
    def __init__(self, parser: SQLQueryParser, structure_analyzer: QueryStructureAnalyzer,
                 performance_analyzer: PerformanceAnalyzer, optimization_advisor: OptimizationAdvisor,
                 complexity_analyzer: ComplexityAnalyzer, security_analyzer: SecurityAnalyzer,
                 query_file: Optional[str] = None, lineage_analyzer: Optional[Any] = None):
        self.parser = parser
        self.structure_analyzer = structure_analyzer
        self.performance_analyzer = performance_analyzer
        self.optimization_advisor = optimization_advisor
        self.complexity_analyzer = complexity_analyzer
        self.security_analyzer = security_analyzer
        self.query_file = query_file
        self.lineage_analyzer = lineage_analyzer
        
        # 분석 결과 수집
        self.structure_result = structure_analyzer.analyze()
        self.performance_result = performance_analyzer.analyze()
        self.optimization_result = optimization_advisor.analyze()
        self.complexity_result = complexity_analyzer.analyze()
        self.security_result = security_analyzer.analyze()
        
        # 리니지 분석 결과 (선택사항)
        self.lineage_result = None
        if self.lineage_analyzer:
            self.lineage_result = self.lineage_analyzer.analyze()
    
    def generate_json(self) -> Dict[str, Any]:
        """JSON 리포트 생성"""
        result = {
            'metadata': {
                'query_file': self.query_file or 'N/A',
                'analyzed_at': datetime.now().isoformat(),
                'query_length': self.structure_result['query_length'],
                'query_lines': self.structure_result['query_lines'],
                'query_type': self.structure_result['query_type']
            },
            'structure': self.structure_result,
            'performance': self.performance_result,
            'complexity': self.complexity_result,
            'security': self.security_result,
            'optimization': self.optimization_result
        }
        
        # 리니지 분석 결과 추가 (있는 경우)
        if self.lineage_result:
            result['lineage'] = self.lineage_result
        
        return result
    
    def generate_lineage_markdown(self) -> str:
        """리니지 전용 마크다운 리포트 생성"""
        if not self.lineage_result:
            return "# 데이터 리니지 분석\n\n리니지 분석 결과가 없습니다.\n"
        
        md_lines = []
        md_lines.append('# 데이터 리니지 분석 리포트')
        md_lines.append('')
        md_lines.append(f'**분석 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        md_lines.append(f'**쿼리 파일**: {self.query_file or "직접 입력"}')
        md_lines.append('')
        
        # 요약 정보
        md_lines.append('## 요약')
        md_lines.append('')
        md_lines.append(f'- **총 테이블 수**: {len(self.lineage_result.get("tables", []))}개')
        md_lines.append(f'- **총 CTE 수**: {len(self.lineage_result.get("ctes", []))}개')
        md_lines.append(f'- **JOIN 관계 수**: {len(self.lineage_result.get("join_relationships", []))}개')
        md_lines.append(f'- **CTE 의존성 수**: {len(self.lineage_result.get("cte_dependencies", []))}개')
        md_lines.append(f'- **서브쿼리 수**: {len(self.lineage_result.get("subquery_relationships", []))}개')
        md_lines.append('')
        
        # Mermaid 다이어그램
        if self.lineage_analyzer:
            md_lines.append('## 테이블 관계 다이어그램')
            md_lines.append('')
            md_lines.append('```mermaid')
            md_lines.append(self.lineage_analyzer.generate_mermaid_diagram())
            md_lines.append('```')
            md_lines.append('')
        
        # 테이블 목록
        if self.lineage_result.get('tables'):
            md_lines.append('## 테이블 목록')
            md_lines.append('')
            for table in self.lineage_result['tables']:
                md_lines.append(f'- `{table}`')
            md_lines.append('')
        
        # CTE 목록
        if self.lineage_result.get('ctes'):
            md_lines.append('## CTE 목록')
            md_lines.append('')
            for cte in self.lineage_result['ctes']:
                md_lines.append(f'- `{cte}`')
            md_lines.append('')
        
        # JOIN 관계 상세
        if self.lineage_result.get('join_relationships'):
            md_lines.append('## JOIN 관계')
            md_lines.append('')
            md_lines.append('| 왼쪽 테이블 | JOIN 타입 | 오른쪽 테이블 | 조건 |')
            md_lines.append('|------------|----------|-------------|------|')
            for join_rel in self.lineage_result['join_relationships']:
                left = join_rel.get('left_table', 'unknown')
                join_type = join_rel.get('join_type', 'JOIN')
                right = join_rel.get('right_table', 'unknown')
                condition = join_rel.get('condition', '')[:50]  # 최대 50자
                md_lines.append(f'| `{left}` | {join_type} | `{right}` | `{condition}` |')
            md_lines.append('')
        
        # CTE 의존성 상세
        if self.lineage_result.get('cte_dependencies'):
            md_lines.append('## CTE 의존성')
            md_lines.append('')
            for cte_dep in self.lineage_result['cte_dependencies']:
                cte_name = cte_dep.get('cte_name', '')
                md_lines.append(f'### CTE: `{cte_name}`')
                md_lines.append('')
                
                ref_tables = cte_dep.get('referenced_tables', [])
                if ref_tables:
                    md_lines.append('**참조하는 테이블**:')
                    for table in ref_tables:
                        md_lines.append(f'- `{table}`')
                    md_lines.append('')
                
                ref_ctes = cte_dep.get('referenced_ctes', [])
                if ref_ctes:
                    md_lines.append('**참조하는 CTE**:')
                    for cte in ref_ctes:
                        md_lines.append(f'- `{cte}`')
                    md_lines.append('')
        
        # 서브쿼리 관계 상세
        if self.lineage_result.get('subquery_relationships'):
            md_lines.append('## 서브쿼리 관계')
            md_lines.append('')
            for subq_rel in self.lineage_result['subquery_relationships']:
                idx = subq_rel.get('subquery_index', 0)
                depth = subq_rel.get('depth', 0)
                location = subq_rel.get('location', 'UNKNOWN')
                ref_tables = subq_rel.get('referenced_tables', [])
                
                md_lines.append(f'### 서브쿼리 #{idx}')
                md_lines.append('')
                md_lines.append(f'- **위치**: {location}')
                md_lines.append(f'- **깊이**: {depth}')
                if ref_tables:
                    md_lines.append('**참조하는 테이블**:')
                    for table in ref_tables:
                        md_lines.append(f'- `{table}`')
                md_lines.append('')
        
        return '\n'.join(md_lines)
    
    def generate_lineage_json(self) -> Dict[str, Any]:
        """리니지 JSON 리포트 생성"""
        if not self.lineage_analyzer:
            return {}
        
        return self.lineage_analyzer.generate_lineage_json()
    
    def generate_markdown(self) -> str:
        """마크다운 리포트 생성"""
        md_lines = []
        
        # 제목 및 메타 정보
        md_lines.append('# SQL 쿼리 분석 리포트')
        md_lines.append('')
        md_lines.append(f'**분석 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        md_lines.append(f'**쿼리 파일**: {self.query_file or "직접 입력"}')
        md_lines.append(f'**쿼리 타입**: {self.structure_result["query_type"]}')
        md_lines.append(f'**쿼리 길이**: {self.structure_result["query_length"]} 문자, {self.structure_result["query_lines"]} 라인')
        md_lines.append('')
        
        # 실행 요약
        md_lines.append('## 실행 요약 (Executive Summary)')
        md_lines.append('')
        md_lines.append('| 항목 | 점수 | 레벨 |')
        md_lines.append('|------|------|------|')
        md_lines.append(f'| 성능 | {self.performance_result["score"]}/100 | {self.performance_result["level"]} |')
        md_lines.append(f'| 복잡도 | {self.complexity_result["score"]}/100 | {self.complexity_result["level"]} |')
        md_lines.append(f'| 보안 | {self.security_result["score"]}/100 | {self.security_result["level"]} |')
        md_lines.append('')
        
        # 쿼리 구조 분석
        md_lines.append('## 1. 쿼리 구조 분석')
        md_lines.append('')
        md_lines.append('### 기본 정보')
        md_lines.append('')
        md_lines.append(f'- **테이블 수**: {self.structure_result["table_count"]}개')
        md_lines.append(f'- **컬럼 수**: {self.structure_result["column_count"]}개')
        md_lines.append(f'- **JOIN 수**: {self.structure_result["join_count"]}개')
        md_lines.append(f'- **서브쿼리 수**: {self.structure_result["subquery_count"]}개')
        md_lines.append(f'- **최대 서브쿼리 깊이**: {self.structure_result["max_subquery_depth"]}')
        md_lines.append(f'- **CTE 수**: {self.structure_result["cte_count"]}개')
        md_lines.append('')
        
        if self.structure_result['tables']:
            md_lines.append('### 테이블 목록')
            md_lines.append('')
            for table in self.structure_result['tables']:
                md_lines.append(f'- `{table}`')
            md_lines.append('')
        
        if self.structure_result['join_types']:
            md_lines.append('### JOIN 타입')
            md_lines.append('')
            for join_type in self.structure_result['join_types']:
                md_lines.append(f'- {join_type}')
            md_lines.append('')
        
        # 성능 분석
        md_lines.append('## 2. 성능 분석')
        md_lines.append('')
        md_lines.append(f'**성능 점수**: {self.performance_result["score"]}/100')
        md_lines.append(f'**성능 레벨**: {self.performance_result["level"]}')
        md_lines.append('')
        
        if self.performance_result['issues']:
            md_lines.append('### 성능 이슈')
            md_lines.append('')
            for i, issue in enumerate(self.performance_result['issues'], 1):
                md_lines.append(f'#### {i}. {issue["type"]} ({issue["severity"]})')
                md_lines.append('')
                md_lines.append(f'- **메시지**: {issue["message"]}')
                md_lines.append(f'- **영향**: {issue["impact"]}')
                md_lines.append('')
        
        # 복잡도 분석
        md_lines.append('## 3. 복잡도 분석')
        md_lines.append('')
        md_lines.append(f'**복잡도 점수**: {self.complexity_result["score"]}/100')
        md_lines.append(f'**복잡도 레벨**: {self.complexity_result["level"]}')
        md_lines.append('')
        md_lines.append('### 복잡도 지표')
        md_lines.append('')
        metrics = self.complexity_result['metrics']
        md_lines.append(f'- 쿼리 길이: {metrics["query_length"]} 문자, {metrics["query_lines"]} 라인')
        md_lines.append(f'- 테이블 수: {metrics["table_count"]}개')
        md_lines.append(f'- JOIN 수: {metrics["join_count"]}개')
        md_lines.append(f'- 서브쿼리 수: {metrics["subquery_count"]}개')
        md_lines.append(f'- 최대 서브쿼리 깊이: {metrics["max_subquery_depth"]}')
        md_lines.append(f'- WHERE 조건 수: {metrics["where_clause_count"]}개')
        md_lines.append(f'- UNION 수: {metrics["union_count"]}개')
        md_lines.append('')
        
        # 보안 분석
        md_lines.append('## 4. 보안 분석')
        md_lines.append('')
        md_lines.append(f'**보안 점수**: {self.security_result["score"]}/100')
        md_lines.append(f'**보안 레벨**: {self.security_result["level"]}')
        md_lines.append('')
        
        if self.security_result['vulnerabilities']:
            md_lines.append('### 보안 취약점')
            md_lines.append('')
            for i, vuln in enumerate(self.security_result['vulnerabilities'], 1):
                md_lines.append(f'#### {i}. {vuln["type"]} ({vuln["severity"]})')
                md_lines.append('')
                md_lines.append(f'- **메시지**: {vuln["message"]}')
                md_lines.append(f'- **영향**: {vuln["impact"]}')
                md_lines.append(f'- **권장사항**: {vuln["recommendation"]}')
                md_lines.append('')
        else:
            md_lines.append('보안 취약점이 발견되지 않았습니다.')
            md_lines.append('')
        
        # 최적화 제안
        md_lines.append('## 5. 최적화 제안')
        md_lines.append('')
        md_lines.append(f'**총 제안 수**: {self.optimization_result["total_count"]}개')
        md_lines.append(f'- HIGH 우선순위: {self.optimization_result["high_priority_count"]}개')
        md_lines.append(f'- MEDIUM 우선순위: {self.optimization_result["medium_priority_count"]}개')
        md_lines.append(f'- LOW 우선순위: {self.optimization_result["low_priority_count"]}개')
        md_lines.append('')
        
        if self.optimization_result['suggestions']:
            # 우선순위별 그룹화
            high_priority = [s for s in self.optimization_result['suggestions'] if s['priority'] == 'HIGH']
            medium_priority = [s for s in self.optimization_result['suggestions'] if s['priority'] == 'MEDIUM']
            low_priority = [s for s in self.optimization_result['suggestions'] if s['priority'] == 'LOW']
            
            if high_priority:
                md_lines.append('### HIGH 우선순위')
                md_lines.append('')
                for i, suggestion in enumerate(high_priority, 1):
                    md_lines.append(f'#### {i}. {suggestion["type"]}')
                    md_lines.append('')
                    md_lines.append(f'- **제안**: {suggestion["message"]}')
                    if 'example' in suggestion:
                        md_lines.append(f'- **예시**: {suggestion["example"]}')
                    if 'expected_improvement' in suggestion:
                        md_lines.append(f'- **예상 개선율**: {suggestion["expected_improvement"]}')
                    md_lines.append('')
            
            if medium_priority:
                md_lines.append('### MEDIUM 우선순위')
                md_lines.append('')
                for i, suggestion in enumerate(medium_priority, 1):
                    md_lines.append(f'#### {i}. {suggestion["type"]}')
                    md_lines.append('')
                    md_lines.append(f'- **제안**: {suggestion["message"]}')
                    if 'example' in suggestion:
                        md_lines.append(f'- **예시**: {suggestion["example"]}')
                    if 'expected_improvement' in suggestion:
                        md_lines.append(f'- **예상 개선율**: {suggestion["expected_improvement"]}')
                    md_lines.append('')
            
            if low_priority:
                md_lines.append('### LOW 우선순위')
                md_lines.append('')
                for i, suggestion in enumerate(low_priority[:5], 1):  # 최대 5개만
                    md_lines.append(f'#### {i}. {suggestion["type"]}')
                    md_lines.append('')
                    md_lines.append(f'- **제안**: {suggestion["message"]}')
                    if 'example' in suggestion:
                        md_lines.append(f'- **예시**: {suggestion["example"]}')
                    if 'expected_improvement' in suggestion:
                        md_lines.append(f'- **예상 개선율**: {suggestion["expected_improvement"]}')
                    md_lines.append('')
        
        # 우선순위별 액션 플랜
        md_lines.append('## 6. 우선순위별 액션 플랜')
        md_lines.append('')
        
        if high_priority:
            md_lines.append('### 즉시 조치 (HIGH 우선순위)')
            md_lines.append('')
            for i, suggestion in enumerate(high_priority[:3], 1):
                md_lines.append(f'{i}. {suggestion["message"]}')
            md_lines.append('')
        
        if medium_priority:
            md_lines.append('### 단기 조치 (MEDIUM 우선순위)')
            md_lines.append('')
            for i, suggestion in enumerate(medium_priority[:3], 1):
                md_lines.append(f'{i}. {suggestion["message"]}')
            md_lines.append('')
        
        # 부록
        md_lines.append('## 부록')
        md_lines.append('')
        md_lines.append('### 원본 쿼리')
        md_lines.append('')
        md_lines.append('```sql')
        # 쿼리가 너무 길면 일부만 표시
        query_preview = self.parser.query_text[:2000] + ('\n... (쿼리가 길어 일부만 표시)' if len(self.parser.query_text) > 2000 else '')
        md_lines.append(query_preview)
        md_lines.append('```')
        md_lines.append('')
        
        return '\n'.join(md_lines)

# ============================================
# MCP 서버 생성
# ============================================

server = Server("sql-query-analyzer")

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
            name="analyze_sql_query",
            description="PostgreSQL 쿼리를 분석하여 구조, 성능, 최적화, 복잡도, 보안을 평가하고 JSON 및 마크다운 파일로 결과를 제공합니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query_file": {
                        "type": "string",
                        "description": "분석할 SQL 파일 경로 (선택사항)"
                    },
                    "query_text": {
                        "type": "string",
                        "description": "직접 입력한 쿼리 텍스트 (선택사항)"
                    },
                    "workspace_path": {
                        "type": "string",
                        "description": "워크스페이스 경로 (기본값: 현재 디렉토리)"
                    },
                    "output_format": {
                        "type": "string",
                        "description": "출력 형식: 'both' (JSON + 마크다운), 'json', 'markdown' (기본값: 'both')",
                        "enum": ["both", "json", "markdown"],
                        "default": "both"
                    },
                    "output_dir": {
                        "type": "string",
                        "description": "출력 디렉토리 (기본값: 'logs')"
                    }
                }
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
    
    Args:
        name: 도구 이름
        arguments: 도구 인자
        
    Returns:
        Sequence[TextContent]: 실행 결과
    """
    try:
        if name == "analyze_sql_query":
            query_file = arguments.get("query_file")
            query_text = arguments.get("query_text")
            workspace_path = arguments.get("workspace_path", os.getcwd())
            output_format = arguments.get("output_format", "both")
            output_dir = arguments.get("output_dir", "logs")
            
            # 쿼리 텍스트 가져오기
            if query_text:
                sql_content = query_text
                query_file_path = None
            elif query_file:
                if not os.path.exists(query_file):
                    return [TextContent(
                        type="text",
                        text=f"오류: SQL 파일을 찾을 수 없습니다: {query_file}"
                    )]
                with open(query_file, 'r', encoding='utf-8', errors='ignore') as f:
                    sql_content = f.read()
                query_file_path = query_file
            else:
                # 워크스페이스에서 SQL 파일 찾기
                sql_files = list(Path(workspace_path).glob("*.sql"))
                if not sql_files:
                    return [TextContent(
                        type="text",
                        text=f"워크스페이스({workspace_path})에서 SQL 파일을 찾을 수 없습니다.\n\n"
                             f"SQL 파일 경로를 직접 지정하거나 query_text 파라미터로 쿼리를 직접 입력하세요."
                    )]
                # 첫 번째 SQL 파일 사용
                query_file_path = str(sql_files[0])
                with open(query_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    sql_content = f.read()
            
            if not sql_content.strip():
                return [TextContent(
                    type="text",
                    text="오류: 쿼리 내용이 비어있습니다."
                )]
            
            # 쿼리 분석 수행
            try:
                parser = SQLQueryParser(sql_content)
                structure_analyzer = QueryStructureAnalyzer(parser)
                structure_result = structure_analyzer.analyze()
                performance_analyzer = PerformanceAnalyzer(parser)
                optimization_advisor = OptimizationAdvisor(parser, performance_analyzer)
                complexity_analyzer = ComplexityAnalyzer(parser)
                security_analyzer = SecurityAnalyzer(parser)
                
                # 리니지 분석 추가
                lineage_analyzer = DataLineageAnalyzer(parser, structure_result)
                
                report_generator = ReportGenerator(
                    parser, structure_analyzer, performance_analyzer,
                    optimization_advisor, complexity_analyzer, security_analyzer,
                    query_file_path, lineage_analyzer
                )
                
                # 출력 디렉토리 생성
                os.makedirs(output_dir, exist_ok=True)
                
                # 파일명 생성
                base_name = os.path.splitext(os.path.basename(query_file_path))[0] if query_file_path else "query"
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                result_parts = []
                
                # JSON 리포트 생성
                if output_format in ["both", "json"]:
                    json_report = report_generator.generate_json()
                    json_file = os.path.join(output_dir, f"{base_name}_analysis_{timestamp}.json")
                    with open(json_file, 'w', encoding='utf-8') as f:
                        json.dump(json_report, f, ensure_ascii=False, indent=2)
                    result_parts.append(f"JSON 리포트 저장: {json_file}")
                
                # 마크다운 리포트 생성
                if output_format in ["both", "markdown"]:
                    md_report = report_generator.generate_markdown()
                    md_file = os.path.join(output_dir, f"{base_name}_analysis_{timestamp}.md")
                    with open(md_file, 'w', encoding='utf-8') as f:
                        f.write(md_report)
                    result_parts.append(f"마크다운 리포트 저장: {md_file}")
                
                # 리니지 리포트 생성 (항상 생성)
                lineage_md_report = report_generator.generate_lineage_markdown()
                lineage_md_file = os.path.join(output_dir, f"{base_name}_lineage_{timestamp}.md")
                with open(lineage_md_file, 'w', encoding='utf-8') as f:
                    f.write(lineage_md_report)
                result_parts.append(f"리니지 마크다운 리포트 저장: {lineage_md_file}")
                
                lineage_json_report = report_generator.generate_lineage_json()
                lineage_json_file = os.path.join(output_dir, f"{base_name}_lineage_{timestamp}.json")
                with open(lineage_json_file, 'w', encoding='utf-8') as f:
                    json.dump(lineage_json_report, f, ensure_ascii=False, indent=2)
                result_parts.append(f"리니지 JSON 리포트 저장: {lineage_json_file}")
                
                # 요약 정보 반환
                summary = f"""SQL 쿼리 분석 완료

쿼리 정보:
- 타입: {structure_analyzer.structure['query_type']}
- 길이: {structure_analyzer.structure['query_length']} 문자, {structure_analyzer.structure['query_lines']} 라인
- 테이블 수: {len(structure_analyzer.structure['tables'])}개

분석 결과:
- 성능 점수: {performance_analyzer.performance_result['score']}/100 ({performance_analyzer.performance_result['level']})
- 복잡도 점수: {complexity_analyzer.complexity_result['score']}/100 ({complexity_analyzer.complexity_result['level']})
- 보안 점수: {security_analyzer.security_result['score']}/100 ({security_analyzer.security_result['level']})
- 최적화 제안: {optimization_advisor.optimization_result['total_count']}개

출력 파일:
{chr(10).join(result_parts)}
"""
                
                return [TextContent(type="text", text=summary)]
                
            except Exception as e:
                import traceback
                error_msg = f"쿼리 분석 중 오류 발생: {str(e)}\n\n{traceback.format_exc()}"
                return [TextContent(type="text", text=error_msg)]
        
        else:
            return [TextContent(
                type="text",
                text=f"알 수 없는 도구: {name}"
            )]
    
    except Exception as e:
        import traceback
        return [TextContent(
            type="text",
            text=f"도구 실행 중 오류 발생: {str(e)}\n\n{traceback.format_exc()}"
        )]

# ============================================
# 서버 실행
# ============================================

async def main():
    """서버 실행"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())


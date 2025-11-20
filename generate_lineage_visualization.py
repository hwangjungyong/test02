#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 쿼리 데이터 리니지 시각화 생성기

SQL 쿼리를 분석하여 데이터 리니지 JSON 구조체를 생성하고,
시각화 HTML 페이지를 생성합니다.
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Any, Tuple
from datetime import datetime

# sqlparse import
try:
    import sqlparse
    from sqlparse import tokens as T
    from sqlparse.sql import Statement, TokenList
except ImportError:
    print("sqlparse 라이브러리가 설치되지 않았습니다. 다음 명령어로 설치하세요:", file=sys.stderr)
    print("pip install sqlparse", file=sys.stderr)
    sys.exit(1)


class SQLLineageExtractor:
    """SQL 쿼리에서 데이터 리니지 정보 추출"""
    
    def __init__(self, query_text: str):
        self.query_text = query_text.strip()
        self.tables = set()
        self.ctes = {}  # CTE 이름 -> CTE 정보
        self.joins = []
        self.column_mappings = []  # 컬럼 매핑 정보
        
    def extract(self) -> Dict[str, Any]:
        """리니지 정보 추출"""
        # CTE 추출
        self._extract_ctes()
        
        # 테이블 추출
        self._extract_tables()
        
        # JOIN 관계 추출 (전체 쿼리에서)
        self._extract_joins()
        
        # CTE 내부의 JOIN도 추출
        for cte_name, cte_info in self.ctes.items():
            cte_extractor = SQLLineageExtractor(cte_info['query'])
            # CTE 내부 JOIN 추출
            cte_extractor._extract_joins()
            cte_joins = cte_extractor.joins
            # CTE 내부 JOIN을 메인 JOIN 목록에 추가 (CTE 이름을 포함)
            for join in cte_joins:
                # CTE 내부 JOIN이므로 왼쪽이나 오른쪽이 CTE 이름일 수 있음
                self.joins.append({
                    'left_table': join['left_table'],
                    'right_table': join['right_table'],
                    'join_type': join['join_type'],
                    'condition': join['condition'],
                    'cte_context': cte_name  # 어떤 CTE 내부의 JOIN인지 표시
                })
        
        # 중복 JOIN 제거 (left_table, right_table, join_type이 동일한 경우)
        seen_joins = set()
        unique_joins = []
        for join in self.joins:
            join_key = (join['left_table'], join['right_table'], join['join_type'])
            if join_key not in seen_joins:
                seen_joins.add(join_key)
                unique_joins.append(join)
        self.joins = unique_joins
        
        # 컬럼 매핑 추출
        self._extract_column_mappings()
        
        return {
            'tables': sorted(list(self.tables)),
            'ctes': list(self.ctes.keys()),
            'joins': self.joins,
            'column_mappings': self.column_mappings,
            'cte_details': self.ctes
        }
    
    def _extract_ctes(self):
        """CTE 추출"""
        # WITH 절 찾기 - 첫 번째 메인 SELECT 전까지
        # 주석 제거 후 검색
        query_clean = re.sub(r'--.*?$', '', self.query_text, flags=re.MULTILINE)
        
        # WITH로 시작하는지 확인
        if not re.search(r'^\s*WITH\s+', query_clean, re.IGNORECASE | re.MULTILINE):
            return
        
        # 첫 번째 메인 SELECT 찾기 (WITH 절 밖의 SELECT)
        select_positions = []
        for match in re.finditer(r'\bSELECT\b', query_clean, re.IGNORECASE):
            # 이 SELECT가 WITH 절 안에 있는지 확인
            before_select = query_clean[:match.start()]
            with_count = len(re.findall(r'\bWITH\b', before_select, re.IGNORECASE))
            select_count = len(re.findall(r'\bSELECT\b', before_select, re.IGNORECASE))
            
            # WITH 절 밖의 SELECT 찾기 (WITH 개수보다 SELECT가 많으면)
            if select_count >= with_count:
                select_positions.append(match.start())
        
        if not select_positions:
            return
        
        # 첫 번째 메인 SELECT 전까지가 CTE 블록
        main_select_pos = select_positions[0]
        cte_block = query_clean[:main_select_pos]
        
        # WITH 키워드 제거
        cte_block = re.sub(r'^\s*WITH\s+', '', cte_block, flags=re.IGNORECASE)
        
        # 각 CTE 추출 (이름 AS (쿼리) 형식) - 중첩 괄호 처리
        pos = 0
        while pos < len(cte_block):
            # CTE 이름 찾기
            name_match = re.search(r'(\w+)\s+AS\s*\(', cte_block[pos:], re.IGNORECASE)
            if not name_match:
                break
            
            cte_name = name_match.group(1).strip()
            start_pos = pos + name_match.end()
            
            # 괄호 매칭하여 쿼리 추출
            paren_count = 1
            end_pos = start_pos
            while end_pos < len(cte_block) and paren_count > 0:
                if cte_block[end_pos] == '(':
                    paren_count += 1
                elif cte_block[end_pos] == ')':
                    paren_count -= 1
                end_pos += 1
            
            if paren_count == 0:
                cte_query = cte_block[start_pos:end_pos-1].strip()
                
                # CTE 쿼리에서 테이블 추출
                cte_tables = self._extract_tables_from_text(cte_query)
                
                self.ctes[cte_name] = {
                    'name': cte_name,
                    'query': cte_query,
                    'tables': cte_tables
                }
                
                # CTE 목록에 추가
                self.tables.add(cte_name)  # CTE도 테이블로 취급 (나중에 구분)
            
            # 다음 CTE 찾기 (닫는 괄호 다음의 쉼표)
            # 닫는 괄호 다음에 오는 쉼표 찾기
            next_comma = cte_block.find(',', end_pos)
            if next_comma == -1:
                break
            
            # 쉼표 다음 공백/줄바꿈 건너뛰기
            pos = next_comma + 1
            while pos < len(cte_block) and cte_block[pos] in [' ', '\n', '\r', '\t']:
                pos += 1
    
    def _extract_tables(self):
        """테이블 추출"""
        # FROM 절에서 테이블 추출
        from_pattern = r'FROM\s+(\w+)(?:\s+\w+)?'
        from_matches = re.finditer(from_pattern, self.query_text, re.IGNORECASE)
        for match in from_matches:
            table = match.group(1).strip()
            if table.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER', 'HAVING', 'LIMIT']:
                self.tables.add(table)
        
        # JOIN 절에서 테이블 추출
        join_pattern = r'JOIN\s+(\w+)(?:\s+\w+)?'
        join_matches = re.finditer(join_pattern, self.query_text, re.IGNORECASE)
        for match in join_matches:
            table = match.group(1).strip()
            if table.upper() not in ['ON', 'USING', 'WHERE', 'GROUP', 'ORDER']:
                self.tables.add(table)
        
        # CTE에서 참조하는 테이블도 추가
        for cte_info in self.ctes.values():
            self.tables.update(cte_info['tables'])
    
    def _extract_tables_from_text(self, text: str) -> List[str]:
        """텍스트에서 테이블명 추출"""
        tables = set()
        
        # FROM 절
        from_pattern = r'FROM\s+(\w+)(?:\s+\w+)?'
        for match in re.finditer(from_pattern, text, re.IGNORECASE):
            table = match.group(1).strip()
            if table.upper() not in ['SELECT', 'WHERE', 'GROUP', 'ORDER']:
                tables.add(table)
        
        # JOIN 절
        join_pattern = r'JOIN\s+(\w+)(?:\s+\w+)?'
        for match in re.finditer(join_pattern, text, re.IGNORECASE):
            table = match.group(1).strip()
            if table.upper() not in ['ON', 'USING']:
                tables.add(table)
        
        return sorted(list(tables))
    
    def _extract_joins(self):
        """JOIN 관계 추출 - 개선된 버전"""
        # JOIN 패턴 찾기 - 단계별로 처리
        # 1단계: JOIN 키워드 찾기
        join_keyword_pattern = r'\b(LEFT|RIGHT|INNER|FULL\s+OUTER|OUTER)?\s*JOIN\b'
        join_positions = []
        for match in re.finditer(join_keyword_pattern, self.query_text, re.IGNORECASE):
            join_positions.append({
                'start': match.start(),
                'end': match.end(),
                'type': match.group(1).strip() if match.group(1) else 'INNER'
            })
        
        for join_pos in join_positions:
            # JOIN 다음 부분 추출
            after_join = self.query_text[join_pos['end']:]
            
            # 테이블명 추출 (JOIN 다음 단어)
            table_match = re.match(r'\s+(\w+)(?:\s+(\w+))?\s+ON\s+', after_join, re.IGNORECASE)
            if not table_match:
                continue
            
            right_table = table_match.group(1).strip()
            right_alias = table_match.group(2).strip() if table_match.group(2) else right_table
            
            # ON 조건 추출
            on_start = table_match.end()
            on_condition = ''
            paren_count = 0
            i = on_start
            while i < len(after_join):
                char = after_join[i]
                if char == '(':
                    paren_count += 1
                elif char == ')':
                    paren_count -= 1
                elif paren_count == 0:
                    # WHERE, GROUP, ORDER, HAVING, LIMIT, UNION, SELECT, FROM 등으로 끝남
                    if re.match(r'\s+(WHERE|GROUP|ORDER|HAVING|LIMIT|UNION|SELECT|FROM|\))', after_join[i:], re.IGNORECASE):
                        break
                on_condition += char
                i += 1
            
            on_condition = on_condition.strip()
            
            # JOIN 조건에서 왼쪽 테이블 추출
            left_table = None
            
            # 조건에서 테이블명 추출
            if '.' in on_condition:
                # table.column 패턴 찾기
                table_col_pattern = r'(\w+)\.\w+'
                matches = re.findall(table_col_pattern, on_condition)
                if matches:
                    # 첫 번째 테이블을 왼쪽으로
                    left_table = matches[0]
                    # 오른쪽 테이블이 별칭인 경우 실제 테이블명 찾기
                    if right_alias not in self.tables and right_alias not in self.ctes:
                        if len(matches) > 1 and matches[1] in self.tables:
                            right_table = matches[1]
                        elif right_table in self.tables or right_table in self.ctes:
                            pass  # 이미 올바른 테이블명
                        else:
                            right_table = right_alias
            
            # FROM 절의 첫 번째 테이블을 기본으로 사용
            if not left_table:
                before_join = self.query_text[:join_pos['start']]
                from_matches = list(re.finditer(r'FROM\s+(\w+)(?:\s+(\w+))?', before_join, re.IGNORECASE))
                if from_matches:
                    from_match = from_matches[-1]
                    left_table = from_match.group(1).strip()
                    left_alias = from_match.group(2).strip() if from_match.group(2) else left_table
                    # 별칭이면 실제 테이블명 사용
                    if left_alias in self.tables or left_alias in self.ctes:
                        left_table = left_alias
            
            # 테이블명이 유효한지 확인
            if left_table and right_table:
                # 별칭 매핑 확인
                left_actual = self._resolve_table_alias(left_table)
                right_actual = self._resolve_table_alias(right_table)
                
                # 유효한 테이블/CTE인지 확인
                if (left_actual in self.tables or left_actual in self.ctes) and \
                   (right_actual in self.tables or right_actual in self.ctes):
                    self.joins.append({
                        'left_table': left_actual,
                        'right_table': right_actual,
                        'join_type': join_pos['type'].upper() or 'INNER',
                        'condition': on_condition[:100]
                    })
    
    def _resolve_table_alias(self, table_name):
        """별칭을 실제 테이블명으로 변환"""
        # CTE 목록 확인
        if table_name in self.ctes:
            return table_name
        
        # 테이블 목록 확인
        if table_name in self.tables:
            return table_name
        
        # 별칭 매핑 찾기 (FROM table alias 패턴)
        alias_pattern = rf'FROM\s+(\w+)\s+{re.escape(table_name)}\b'
        match = re.search(alias_pattern, self.query_text, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return table_name
    
    def _extract_column_mappings(self):
        """컬럼 매핑 추출 (SELECT 절에서)"""
        # SELECT 절 찾기
        select_pattern = r'SELECT\s+(.+?)\s+FROM'
        match = re.search(select_pattern, self.query_text, re.IGNORECASE | re.DOTALL)
        if not match:
            return
        
        select_clause = match.group(1)
        
        # 컬럼 추출 (간단한 패턴)
        column_pattern = r'(\w+\.\w+|\w+)\s+(?:AS\s+)?(\w+)?'
        matches = re.finditer(column_pattern, select_clause, re.IGNORECASE)
        
        for match in matches:
            source = match.group(1).strip()
            alias = match.group(2).strip() if match.group(2) else source
            
            if '.' in source:
                table, column = source.split('.')
                self.column_mappings.append({
                    'source_table': table,
                    'source_column': column,
                    'target_column': alias
                })


class LineageVisualizationGenerator:
    """데이터 리니지 시각화 JSON 및 HTML 생성"""
    
    def __init__(self, lineage_data: Dict[str, Any]):
        self.lineage_data = lineage_data
    
    def generate_visualization_json(self) -> Dict[str, Any]:
        """시각화용 JSON 구조체 생성"""
        nodes = []
        edges = []
        node_id_map = {}
        node_counter = 0
        
        # 테이블 노드 추가
        for table in self.lineage_data['tables']:
            node_id = f"node_{node_counter}"
            node_id_map[table] = node_id
            nodes.append({
                'id': node_id,
                'label': table,
                'type': 'table',
                'group': 'table'
            })
            node_counter += 1
        
        # CTE 노드 추가 (테이블과 구분)
        cte_names = set(self.lineage_data['ctes'])
        for cte_name in cte_names:
            # 이미 테이블로 추가된 경우 제외
            if cte_name not in [t for t in self.lineage_data['tables']]:
                node_id = f"node_{node_counter}"
                node_id_map[cte_name] = node_id
                nodes.append({
                    'id': node_id,
                    'label': cte_name,
                    'type': 'cte',
                    'group': 'cte'
                })
                node_counter += 1
            else:
                # 테이블로 이미 추가된 경우, 타입을 CTE로 변경
                if cte_name in node_id_map:
                    # 노드 찾아서 타입 변경
                    for node in nodes:
                        if node['id'] == node_id_map[cte_name]:
                            node['type'] = 'cte'
                            node['group'] = 'cte'
                            break
        
        # JOIN 엣지 추가
        for join in self.lineage_data['joins']:
            left = join['left_table']
            right = join['right_table']
            join_type = join['join_type']
            
            # 별칭 처리: 실제 테이블명 찾기
            left_actual = self._find_actual_table(left, self.lineage_data)
            right_actual = self._find_actual_table(right, self.lineage_data)
            
            if left_actual in node_id_map and right_actual in node_id_map:
                edges.append({
                    'from': node_id_map[left_actual],
                    'to': node_id_map[right_actual],
                    'label': join_type,
                    'type': 'join',
                    'arrows': 'to'
                })
        
        # CTE 의존성 엣지 추가
        for cte_name, cte_info in self.lineage_data.get('cte_details', {}).items():
            if cte_name not in node_id_map:
                continue
            
            for table in cte_info.get('tables', []):
                if table in node_id_map:
                    edges.append({
                        'from': node_id_map[table],
                        'to': node_id_map[cte_name],
                        'label': 'CTE',
                        'type': 'cte_dependency',
                        'arrows': 'to',
                        'dashes': True
                    })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'total_tables': len(self.lineage_data['tables']),
                'total_ctes': len(self.lineage_data['ctes']),
                'generated_at': datetime.now().isoformat()
            }
        }
    
    def _find_actual_table(self, table_name: str, lineage_data: Dict[str, Any]) -> str:
        """별칭이나 CTE 이름에서 실제 테이블명 찾기"""
        # CTE 목록 확인
        if table_name in lineage_data['ctes']:
            return table_name
        
        # 테이블 목록 확인
        if table_name in lineage_data['tables']:
            return table_name
        
        # 별칭 매핑 확인 (간단한 처리)
        # 실제로는 더 복잡한 별칭 매핑이 필요할 수 있음
        return table_name
    
    def generate_html(self, output_path: str):
        """시각화 HTML 페이지 생성"""
        vis_json = self.generate_visualization_json()
        
        # JSON 데이터를 JavaScript 문자열로 변환
        nodes_json = json.dumps(vis_json['nodes'], ensure_ascii=False)
        edges_json = json.dumps(vis_json['edges'], ensure_ascii=False)
        
        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline';">
    <title>데이터 리니지 시각화</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js" 
            onerror="console.error('vis-network 로드 실패. 인터넷 연결을 확인하거나 서버를 통해 열어주세요.'); document.body.innerHTML='<div style=\\'padding:20px;text-align:center;\\'><h2>리소스 로드 실패</h2><p>이 파일을 직접 열 때는 외부 리소스를 로드할 수 없습니다.</p><p>웹 서버를 통해 열거나 인터넷 연결을 확인해주세요.</p></div>';"></script>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            padding: 20px;
        }}
        h1 {{
            color: #333;
            margin-bottom: 10px;
        }}
        .info {{
            background-color: #e8f4f8;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 20px;
        }}
        .info-item {{
            margin: 5px 0;
            color: #555;
        }}
        #network {{
            width: 100%;
            height: 800px;
            border: 1px solid #ddd;
            border-radius: 5px;
            background-color: #fafafa;
        }}
        .legend {{
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 5px;
        }}
        .legend-item {{
            display: inline-block;
            margin-right: 20px;
            margin-bottom: 10px;
        }}
        .legend-color {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 3px;
            margin-right: 5px;
            vertical-align: middle;
        }}
        .table-color {{
            background-color: #4CAF50;
        }}
        .cte-color {{
            background-color: #2196F3;
        }}
        .btn-open-browser, .btn-copy-path {{
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 12px 24px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            margin-right: 10px;
            margin-bottom: 10px;
            transition: background-color 0.3s;
        }}
        .btn-open-browser:hover, .btn-copy-path:hover {{
            background-color: #45a049;
        }}
        .btn-copy-path {{
            background-color: #2196F3;
        }}
        .btn-copy-path:hover {{
            background-color: #1976D2;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 데이터 리니지 시각화</h1>
        
        <div class="info">
            <div class="info-item"><strong>총 노드 수:</strong> {vis_json['metadata']['total_nodes']}개</div>
            <div class="info-item"><strong>총 엣지 수:</strong> {vis_json['metadata']['total_edges']}개</div>
            <div class="info-item"><strong>테이블 수:</strong> {vis_json['metadata']['total_tables']}개</div>
            <div class="info-item"><strong>CTE 수:</strong> {vis_json['metadata']['total_ctes']}개</div>
            <div class="info-item"><strong>생성 일시:</strong> {vis_json['metadata']['generated_at']}</div>
        </div>
        
        <div style="margin-bottom: 20px;">
            <button onclick="openInBrowser()" class="btn-open-browser">🌐 브라우저에서 열기</button>
            <button onclick="copyFilePath()" class="btn-copy-path">📋 파일 경로 복사</button>
        </div>
        
        <div id="network"></div>
        
        <div class="legend">
            <h3>범례</h3>
            <div class="legend-item">
                <span class="legend-color table-color"></span>
                <span>테이블</span>
            </div>
            <div class="legend-item">
                <span class="legend-color cte-color"></span>
                <span>CTE (Common Table Expression)</span>
            </div>
            <div class="legend-item">
                <span>실선</span> - JOIN 관계
            </div>
            <div class="legend-item">
                <span>점선</span> - CTE 의존성
            </div>
        </div>
    </div>
    
    <script type="text/javascript">
        // 파일을 직접 열 때 경고 표시
        if (window.location.protocol === 'file:') {{
            document.addEventListener('DOMContentLoaded', function() {{
                const warningDiv = document.createElement('div');
                warningDiv.style.cssText = 'background-color: #fff3cd; border: 2px solid #ffc107; padding: 15px; margin: 20px; border-radius: 5px; text-align: center;';
                warningDiv.innerHTML = '<h3 style="color: #856404; margin-top: 0;">⚠️ 파일 직접 열기 모드</h3><p style="color: #856404;">이 파일을 직접 열면 외부 리소스를 로드할 수 없어 시각화가 작동하지 않을 수 있습니다.</p><p style="color: #856404;"><strong>권장:</strong> 웹 서버를 통해 열어주세요. (예: http://localhost:5173에서 리니지 시각화 보기 버튼 클릭)</p>';
                document.body.insertBefore(warningDiv, document.body.firstChild);
            }});
        }}
        
        // 데이터 준비
        let nodes, edges;
        try {{
            nodes = new vis.DataSet({nodes_json});
            edges = new vis.DataSet({edges_json});
        }} catch (error) {{
            console.error('데이터셋 생성 실패:', error);
            document.getElementById('network').innerHTML = '<div style="padding:20px;text-align:center;"><h3>데이터 로드 실패</h3><p>데이터를 불러올 수 없습니다.</p></div>';
        }}
        
        // 노드 스타일 설정
        const nodeOptions = {{
            shape: 'box',
            font: {{
                size: 14,
                face: 'Segoe UI'
            }},
            borderWidth: 2,
            shadow: true
        }};
        
        // 엣지 스타일 설정
        const edgeOptions = {{
            font: {{
                size: 12,
                align: 'middle'
            }},
            arrows: {{
                to: {{
                    enabled: true,
                    scaleFactor: 0.8
                }}
            }},
            smooth: {{
                type: 'continuous',
                roundness: 0.5
            }}
        }};
        
        // 노드 색상 설정
        nodes.forEach(function(node) {{
            if (node.type === 'table') {{
                node.color = {{
                    background: '#4CAF50',
                    border: '#2E7D32',
                    highlight: {{
                        background: '#66BB6A',
                        border: '#2E7D32'
                    }}
                }};
            }} else if (node.type === 'cte') {{
                node.color = {{
                    background: '#2196F3',
                    border: '#1565C0',
                    highlight: {{
                        background: '#42A5F5',
                        border: '#1565C0'
                    }}
                }};
            }}
        }});
        
        // 엣지 색상 및 스타일 설정
        edges.forEach(function(edge) {{
            if (edge.type === 'join') {{
                edge.color = {{
                    color: '#666',
                    highlight: '#000'
                }};
                edge.width = 2;
            }} else if (edge.type === 'cte_dependency') {{
                edge.color = {{
                    color: '#2196F3',
                    highlight: '#1565C0'
                }};
                edge.width = 1.5;
                edge.dashes = true;
            }}
        }});
        
        // 네트워크 옵션
        const options = {{
            nodes: nodeOptions,
            edges: edgeOptions,
            layout: {{
                hierarchical: {{
                    enabled: false
                }},
                improvedLayout: true
            }},
            physics: {{
                enabled: true,
                stabilization: {{
                    iterations: 200
                }},
                barnesHut: {{
                    gravitationalConstant: -2000,
                    centralGravity: 0.3,
                    springLength: 200,
                    springConstant: 0.04,
                    damping: 0.09
                }}
            }},
            interaction: {{
                hover: true,
                tooltipDelay: 100,
                zoomView: true,
                dragView: true
            }}
        }};
        
        // 네트워크 생성
        const container = document.getElementById('network');
        if (!container) {{
            console.error('네트워크 컨테이너를 찾을 수 없습니다.');
            return;
        }}
        
        // vis-network가 로드되었는지 확인
        if (typeof vis === 'undefined' || !vis.Network) {{
            console.error('vis-network 라이브러리가 로드되지 않았습니다.');
            container.innerHTML = '<div style="padding:20px;text-align:center;"><h3>라이브러리 로드 실패</h3><p>vis-network를 로드할 수 없습니다. 인터넷 연결을 확인하거나 서버를 통해 열어주세요.</p></div>';
            return;
        }}
        
        const data = {{
            nodes: nodes,
            edges: edges
        }};
        const network = new vis.Network(container, data, options);
        
        // 노드 클릭 이벤트
        network.on('click', function(params) {{
            if (params.nodes.length > 0) {{
                const nodeId = params.nodes[0];
                const node = nodes.get(nodeId);
                alert('노드: ' + node.label + '\\n타입: ' + node.type);
            }}
        }});
        
        // 엣지 클릭 이벤트
        network.on('click', function(params) {{
            if (params.edges.length > 0) {{
                const edgeId = params.edges[0];
                const edge = edges.get(edgeId);
                alert('관계: ' + edge.label + '\\n타입: ' + edge.type);
            }}
        }});
        
        // 브라우저에서 열기 함수
        function openInBrowser() {{
            const filePath = window.location.href;
            // file:// 프로토콜인 경우
            if (filePath.startsWith('file://')) {{
                // Windows에서 파일 경로 추출
                const path = filePath.replace('file:///', '').replace(/\\//g, '\\\\');
                // 브라우저 기본 앱으로 열기
                if (navigator.userAgent.indexOf('Windows') > -1) {{
                    // Windows에서는 직접 파일 경로를 사용할 수 없으므로 현재 페이지를 새 창으로 열기
                    window.open(filePath, '_blank');
                }} else {{
                    window.open(filePath, '_blank');
                }}
            }} else {{
                // HTTP 프로토콜인 경우
                window.open(filePath, '_blank');
            }}
        }}
        
        // 파일 경로 복사 함수
        function copyFilePath() {{
            const filePath = window.location.href;
            if (navigator.clipboard) {{
                navigator.clipboard.writeText(filePath).then(function() {{
                    alert('파일 경로가 클립보드에 복사되었습니다!\\n\\n' + filePath);
                }}).catch(function(err) {{
                    console.error('복사 실패:', err);
                    // 대체 방법: 텍스트 영역 사용
                    const textArea = document.createElement('textarea');
                    textArea.value = filePath;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    alert('파일 경로가 클립보드에 복사되었습니다!\\n\\n' + filePath);
                }});
            }} else {{
                // 대체 방법
                const textArea = document.createElement('textarea');
                textArea.value = filePath;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('파일 경로가 클립보드에 복사되었습니다!\\n\\n' + filePath);
            }}
        }}
    </script>
</body>
</html>"""
        
        # f-string에서 변수 치환
        html_content = html_content.replace('{nodes_json}', nodes_json)
        html_content = html_content.replace('{edges_json}', edges_json)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)


def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용법: python generate_lineage_visualization.py <sql_file>")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    
    # SQL 파일 읽기
    with open(sql_file, 'r', encoding='utf-8') as f:
        query_text = f.read()
    
    # 리니지 추출
    extractor = SQLLineageExtractor(query_text)
    lineage_data = extractor.extract()
    
    # JSON 파일 저장
    output_dir = Path(sql_file).parent / 'sql_analysis'
    output_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = Path(sql_file).stem
    
    # 리니지 JSON 저장
    lineage_json_file = output_dir / f"{base_name}_lineage_{timestamp}.json"
    with open(lineage_json_file, 'w', encoding='utf-8') as f:
        json.dump(lineage_data, f, ensure_ascii=False, indent=2)
    print(f"리니지 JSON 저장: {lineage_json_file}")
    
    # 시각화 JSON 생성 및 저장
    generator = LineageVisualizationGenerator(lineage_data)
    vis_json = generator.generate_visualization_json()
    
    vis_json_file = output_dir / f"{base_name}_lineage_visualization_{timestamp}.json"
    with open(vis_json_file, 'w', encoding='utf-8') as f:
        json.dump(vis_json, f, ensure_ascii=False, indent=2)
    print(f"시각화 JSON 저장: {vis_json_file}")
    
    # HTML 시각화 생성
    html_file = output_dir / f"{base_name}_lineage_visualization_{timestamp}.html"
    generator.generate_html(str(html_file))
    print(f"시각화 HTML 저장: {html_file}")
    
    # 브라우저에서 자동으로 열기
    try:
        import webbrowser
        html_path = html_file.resolve()
        webbrowser.open(f'file:///{html_path.as_posix()}')
        print(f"\n[SUCCESS] 브라우저에서 자동으로 열었습니다: {html_path}")
    except Exception as e:
        print(f"\n[WARNING] 브라우저 자동 열기 실패: {e}")
        print(f"수동으로 열기: {html_file}")
    
    print("\n완료! HTML 파일을 브라우저에서 열어 시각화를 확인하세요.")


if __name__ == "__main__":
    main()


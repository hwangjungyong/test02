#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
영향도 시각화 생성 스크립트

사용 방법:
  python generate_impact_visualization.py <SQL 파일> <테이블명> [컬럼명]
  
예시:
  python generate_impact_visualization.py queries/complex_query.sql users
  python generate_impact_visualization.py queries/complex_query.sql users email
"""

import sys
import os
import json
import re
from pathlib import Path
from datetime import datetime

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# MCP 서버 모듈에서 클래스 import
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("mcp_sql_query_analyzer", "mcp-sql-query-analyzer.py")
    mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_module)
    
    SQLQueryParser = mcp_module.SQLQueryParser
    QueryStructureAnalyzer = mcp_module.QueryStructureAnalyzer
    DataLineageAnalyzer = mcp_module.DataLineageAnalyzer
    ImpactAnalyzer = mcp_module.ImpactAnalyzer
except Exception as e:
    print(f"[오류] MCP 서버 모듈을 불러올 수 없습니다: {e}", file=sys.stderr)
    print("mcp-sql-query-analyzer.py 파일이 같은 디렉토리에 있는지 확인하세요.", file=sys.stderr)
    sys.exit(1)

def generate_impact_html(impact_result: dict, sql_file_path: str) -> str:
    """영향도 분석 결과를 HTML로 변환"""
    
    target_table = impact_result.get('target', {}).get('table', 'unknown')
    target_column = impact_result.get('target', {}).get('column')
    impact_level = impact_result.get('impact_level', 'MEDIUM')
    impact_score = impact_result.get('impact_score', 0)
    
    # 노드 및 엣지 데이터 생성
    nodes = []
    edges = []
    
    # 중심 노드 (타겟 테이블)
    center_node_id = 'target'
    nodes.append({
        'id': center_node_id,
        'label': target_table + ('\n(' + target_column + ')' if target_column else ''),
        'color': {
            'background': '#d32f2f' if impact_level == 'CRITICAL' else
                         '#f57c00' if impact_level == 'HIGH' else
                         '#fbc02d' if impact_level == 'MEDIUM' else '#388e3c',
            'border': '#000',
            'highlight': {'background': '#ff0000'}
        },
        'font': {'size': 20, 'color': '#fff', 'face': 'Arial'},
        'shape': 'box',
        'size': 30
    })
    
    # 영향받는 테이블 노드
    affected_tables = impact_result.get('affected_tables', [])
    for idx, table in enumerate(affected_tables):
        node_id = f'table_{idx}'
        nodes.append({
            'id': node_id,
            'label': table,
            'color': {
                'background': '#e3f2fd',
                'border': '#1976d2',
                'highlight': {'background': '#90caf9'}
            },
            'font': {'size': 16, 'color': '#1976d2'},
            'shape': 'box',
            'size': 20
        })
        edges.append({
            'from': center_node_id,
            'to': node_id,
            'color': {'color': '#1976d2'},
            'arrows': {'to': {'enabled': True}},
            'label': '영향'
        })
    
    # 영향받는 CTE 노드
    affected_ctes = impact_result.get('affected_ctes', [])
    for idx, cte in enumerate(affected_ctes):
        node_id = f'cte_{idx}'
        nodes.append({
            'id': node_id,
            'label': cte + '\n(CTE)',
            'color': {
                'background': '#f3e5f5',
                'border': '#7b1fa2',
                'highlight': {'background': '#ce93d8'}
            },
            'font': {'size': 14, 'color': '#7b1fa2'},
            'shape': 'ellipse',
            'size': 18
        })
        edges.append({
            'from': center_node_id,
            'to': node_id,
            'color': {'color': '#7b1fa2'},
            'arrows': {'to': {'enabled': True}},
            'label': 'CTE 영향',
            'dashes': True
        })
    
    # 직접 영향 노드
    direct_impacts = impact_result.get('direct_impacts', [])
    for idx, impact in enumerate(direct_impacts[:10]):  # 최대 10개만 표시
        node_id = f'direct_{idx}'
        impact_type = impact.get('type', 'UNKNOWN')
        impact_level_local = impact.get('impact_level', 'MEDIUM')
        
        nodes.append({
            'id': node_id,
            'label': f'{impact_type}\n{impact.get("location", "")}',
            'color': {
                'background': '#ffebee' if impact_level_local == 'CRITICAL' else
                             '#fff3e0' if impact_level_local == 'HIGH' else
                             '#fffde7' if impact_level_local == 'MEDIUM' else '#e8f5e9',
                'border': '#d32f2f' if impact_level_local == 'CRITICAL' else
                         '#f57c00' if impact_level_local == 'HIGH' else
                         '#fbc02d' if impact_level_local == 'MEDIUM' else '#388e3c',
                'highlight': {'background': '#ffcdd2'}
            },
            'font': {'size': 12, 'color': '#333'},
            'shape': 'diamond',
            'size': 15
        })
        edges.append({
            'from': center_node_id,
            'to': node_id,
            'color': {
                'color': '#d32f2f' if impact_level_local == 'CRITICAL' else
                        '#f57c00' if impact_level_local == 'HIGH' else
                        '#fbc02d' if impact_level_local == 'MEDIUM' else '#388e3c'
            },
            'arrows': {'to': {'enabled': True}},
            'label': impact_type,
            'width': 3 if impact_level_local == 'CRITICAL' else 2
        })
    
    # HTML 생성
    html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="Content-Security-Policy" content="default-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://unpkg.com https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline';">
    <title>영향도 분석 시각화</title>
    <script type="text/javascript" src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"
            onerror="console.error('vis-network 로드 실패');"></script>
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
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            padding: 24px;
        }}
        h1 {{
            color: #333;
            margin-top: 0;
            border-bottom: 3px solid #667eea;
            padding-bottom: 12px;
        }}
        .impact-summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin: 20px 0;
            padding: 20px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .summary-item {{
            text-align: center;
        }}
        .summary-label {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 8px;
        }}
        .summary-value {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #333;
        }}
        .summary-value.critical {{ color: #d32f2f; }}
        .summary-value.high {{ color: #f57c00; }}
        .summary-value.medium {{ color: #fbc02d; }}
        .summary-value.low {{ color: #388e3c; }}
        #impactNetwork {{
            width: 100%;
            height: 600px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            background: #fafafa;
            margin: 20px 0;
        }}
        .legend {{
            display: flex;
            flex-wrap: wrap;
            gap: 20px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 8px;
            margin-top: 20px;
        }}
        .legend-item {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .legend-color {{
            width: 24px;
            height: 24px;
            border-radius: 4px;
            border: 1px solid rgba(0,0,0,0.1);
        }}
        .impact-details {{
            margin-top: 24px;
        }}
        .impact-section {{
            margin-bottom: 24px;
            padding: 16px;
            background: #f8f9fa;
            border-radius: 8px;
        }}
        .impact-section h3 {{
            margin-top: 0;
            color: #333;
        }}
        .impact-item {{
            padding: 12px;
            margin-bottom: 8px;
            background: white;
            border-radius: 6px;
            border-left: 4px solid #ddd;
        }}
        .impact-item.critical {{ border-left-color: #d32f2f; }}
        .impact-item.high {{ border-left-color: #f57c00; }}
        .impact-item.medium {{ border-left-color: #fbc02d; }}
        .impact-item.low {{ border-left-color: #388e3c; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 영향도 분석 시각화</h1>
        
        <div class="impact-summary">
            <div class="summary-item">
                <div class="summary-label">타겟 테이블</div>
                <div class="summary-value">{{ target_table }}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">영향도 수준</div>
                <div class="summary-value {impact_level.lower()}">{{ impact_level }}</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">영향도 점수</div>
                <div class="summary-value">{{ impact_score }}/100</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">직접 영향</div>
                <div class="summary-value">{{ len(direct_impacts) }}개</div>
            </div>
            <div class="summary-item">
                <div class="summary-label">영향받는 테이블</div>
                <div class="summary-value">{{ len(affected_tables) }}개</div>
            </div>
        </div>
        
        <div id="impactNetwork"></div>
        
        <div class="legend">
            <div class="legend-item">
                <div class="legend-color" style="background: #d32f2f;"></div>
                <span>CRITICAL</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f57c00;"></div>
                <span>HIGH</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #fbc02d;"></div>
                <span>MEDIUM</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #388e3c;"></div>
                <span>LOW</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #e3f2fd; border: 2px solid #1976d2;"></div>
                <span>영향받는 테이블</span>
            </div>
            <div class="legend-item">
                <div class="legend-color" style="background: #f3e5f5; border: 2px solid #7b1fa2;"></div>
                <span>영향받는 CTE</span>
            </div>
        </div>
        
        <div class="impact-details">
            <div class="impact-section">
                <h3>직접 영향 ({{ len(direct_impacts) }}개)</h3>
                <div id="directImpacts"></div>
            </div>
            
            <div class="impact-section">
                <h3>영향받는 테이블 ({{ len(affected_tables) }}개)</h3>
                <div id="affectedTables"></div>
            </div>
        </div>
    </div>
    
    <script type="text/javascript">
        // vis-network가 로드되었는지 확인
        if (typeof vis === 'undefined' || !vis.Network) {{
            console.error('vis-network 라이브러리가 로드되지 않았습니다.');
            document.getElementById('impactNetwork').innerHTML = '<div style="padding:20px;text-align:center;"><h3>라이브러리 로드 실패</h3><p>vis-network를 로드할 수 없습니다. 인터넷 연결을 확인하거나 서버를 통해 열어주세요.</p></div>';
        }} else {{
            // 노드 및 엣지 데이터
            const nodes = new vis.DataSet({json.dumps(nodes, ensure_ascii=False)});
            const edges = new vis.DataSet({json.dumps(edges, ensure_ascii=False)});
            
            // 네트워크 생성
            const container = document.getElementById('impactNetwork');
            const data = {{ nodes: nodes, edges: edges }};
            const options = {{
                nodes: {{
                    borderWidth: 2,
                    shadow: true,
                    font: {{ size: 14, face: 'Arial' }}
                }},
                edges: {{
                    width: 2,
                    shadow: true,
                    smooth: {{ type: 'curvedCW', roundness: 0.2 }},
                    font: {{ size: 10, align: 'middle' }}
                }},
                physics: {{
                    enabled: true,
                    stabilization: {{ enabled: true, iterations: 200 }},
                    barnesHut: {{
                        gravitationalConstant: -2000,
                        centralGravity: 0.1,
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
            
            const network = new vis.Network(container, data, options);
            
            // 노드 클릭 이벤트
            network.on('click', function(params) {{
                if (params.nodes.length > 0) {{
                    const nodeId = params.nodes[0];
                    const node = nodes.get(nodeId);
                    if (node) {{
                        console.log('노드 클릭:', node.label);
                        alert('노드: ' + node.label + '\\n영향도 분석 상세 정보를 확인하세요.');
                    }}
                }}
            }});
        }}
        
        // 직접 영향 목록 표시
        const directImpacts = {json.dumps(direct_impacts[:20], ensure_ascii=False)};
        const directImpactsHtml = directImpacts.map(impact => `
            <div class="impact-item ${{impact.impact_level.toLowerCase()}}">
                <strong>${{impact.type}}</strong> - ${{impact.location}}<br>
                <small>${{impact.query_snippet}}</small>
            </div>
        `).join('');
        document.getElementById('directImpacts').innerHTML = directImpactsHtml;
        
        // 영향받는 테이블 목록 표시
        const affectedTables = {json.dumps(affected_tables, ensure_ascii=False)};
        const affectedTablesHtml = affectedTables.map(table => `
            <span style="display:inline-block;padding:8px 16px;margin:4px;background:#e3f2fd;color:#1976d2;border-radius:6px;">${{table}}</span>
        `).join('');
        document.getElementById('affectedTables').innerHTML = affectedTablesHtml;
    </script>
</body>
</html>"""
    
    return html_content

def main():
    """메인 함수"""
    if len(sys.argv) < 3:
        print("사용 방법: python generate_impact_visualization.py <SQL 파일> <테이블명> [컬럼명]", file=sys.stderr)
        sys.exit(1)
    
    sql_file = sys.argv[1]
    target_table = sys.argv[2]
    target_column = sys.argv[3] if len(sys.argv) > 3 else None
    
    if not os.path.exists(sql_file):
        print(f"[오류] SQL 파일을 찾을 수 없습니다: {sql_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # SQL 파일 읽기
        with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()
        
        # 쿼리 분석
        parser = SQLQueryParser(sql_content)
        structure_analyzer = QueryStructureAnalyzer(parser)
        structure_result = structure_analyzer.analyze()
        lineage_analyzer = DataLineageAnalyzer(parser, structure_result)
        
        # 영향도 분석
        impact_analyzer = ImpactAnalyzer(parser, lineage_analyzer, structure_analyzer)
        impact_result = impact_analyzer.analyze(target_table, target_column)
        
        # HTML 생성
        html_content = generate_impact_html(impact_result, sql_file)
        
        # 출력 파일 경로 생성
        base_name = os.path.splitext(os.path.basename(sql_file))[0]
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.join(os.path.dirname(sql_file) or '.', 'sql_analysis')
        os.makedirs(output_dir, exist_ok=True)
        
        output_file = os.path.join(output_dir, f"{base_name}_impact_{target_table}_{timestamp}.html")
        if target_column:
            output_file = os.path.join(output_dir, f"{base_name}_impact_{target_table}_{target_column}_{timestamp}.html")
        
        # HTML 파일 저장
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"시각화 HTML 저장: {output_file}")
        print(f"영향도 수준: {impact_result.get('impact_level', 'UNKNOWN')}")
        print(f"영향도 점수: {impact_result.get('impact_score', 0)}/100")
        print(f"직접 영향: {len(impact_result.get('direct_impacts', []))}개")
        print(f"간접 영향: {len(impact_result.get('indirect_impacts', []))}개")
        
    except Exception as e:
        print(f"[오류] 영향도 시각화 생성 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


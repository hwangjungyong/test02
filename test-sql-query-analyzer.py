#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 쿼리 분석 독립 실행 스크립트

사용 방법:
  python test-sql-query-analyzer.py [SQL 파일 경로]
  
예시:
  python test-sql-query-analyzer.py queries/complex_query.sql
  python test-sql-query-analyzer.py  # 워크스페이스에서 .sql 파일 자동 찾기
"""

import sys
import os
from pathlib import Path
from datetime import datetime
import json

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# MCP 서버 모듈에서 클래스 import
try:
    # 직접 import가 안되면 파일을 읽어서 실행
    import importlib.util
    spec = importlib.util.spec_from_file_location("mcp_sql_query_analyzer", "mcp-sql-query-analyzer.py")
    mcp_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mcp_module)
    
    SQLQueryParser = mcp_module.SQLQueryParser
    QueryStructureAnalyzer = mcp_module.QueryStructureAnalyzer
    PerformanceAnalyzer = mcp_module.PerformanceAnalyzer
    OptimizationAdvisor = mcp_module.OptimizationAdvisor
    ComplexityAnalyzer = mcp_module.ComplexityAnalyzer
    SecurityAnalyzer = mcp_module.SecurityAnalyzer
    DataLineageAnalyzer = mcp_module.DataLineageAnalyzer
    ImpactAnalyzer = mcp_module.ImpactAnalyzer
    ReportGenerator = mcp_module.ReportGenerator
except Exception as e:
    print(f"[오류] MCP 서버 모듈을 불러올 수 없습니다: {e}")
    print("mcp-sql-query-analyzer.py 파일이 같은 디렉토리에 있는지 확인하세요.")
    sys.exit(1)

def find_sql_files(workspace_path: str) -> list:
    """워크스페이스에서 SQL 파일 찾기"""
    sql_files = []
    workspace = Path(workspace_path)
    
    # .sql 파일 찾기
    sql_files.extend(list(workspace.glob("**/*.sql")))
    
    # 중복 제거 및 문자열 변환
    return list(set(str(f) for f in sql_files if f.is_file()))

def main():
    """메인 함수"""
    workspace_path = os.getcwd()
    
    # 출력 파일 설정
    output_file = None
    sql_file_path = None
    
    # 명령줄 인자 처리
    if len(sys.argv) > 1:
        sql_file_arg = sys.argv[1]
        if os.path.isfile(sql_file_arg):
            sql_file_path = sql_file_arg
            # 단일 파일 분석 시 결과를 파일로 저장
            base_name = os.path.splitext(os.path.basename(sql_file_path))[0]
            output_dir = os.path.join(os.path.dirname(sql_file_path) or 'logs', 'sql_analysis')
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"{base_name}_analysis_{timestamp}.txt")
    
    # 출력 리다이렉션 설정
    if output_file:
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
        
        # SQL 파일 찾기
        if sql_file_path:
            sql_files = [sql_file_path]
        else:
            sql_files = find_sql_files(workspace_path)
        
        if not sql_files:
            print("SQL 파일을 찾을 수 없습니다.")
            print("\n사용 방법:")
            print("  python test-sql-query-analyzer.py [SQL 파일 경로]")
            print("\n또는 워크스페이스에 .sql 파일을 배치하세요.")
            return
        
        print(f"발견된 SQL 파일: {len(sql_files)}개")
        for sql_file in sql_files:
            print(f"  - {sql_file}")
        print()
        
        # 각 SQL 파일 분석
        for sql_file in sql_files[:5]:  # 최대 5개 파일만 분석
            try:
                print("=" * 120)
                print(f"[SQL 파일] {sql_file}")
                print("=" * 120)
                print()
                
                with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
                    sql_content = f.read()
                
                if not sql_content.strip():
                    print("SQL 파일이 비어있습니다.")
                    continue
                
                # 쿼리 분석
                print("[분석 시작]")
                print()
                
                parser = SQLQueryParser(sql_content)
                structure_analyzer = QueryStructureAnalyzer(parser)
                structure_result = structure_analyzer.analyze()
                performance_analyzer = PerformanceAnalyzer(parser)
                optimization_advisor = OptimizationAdvisor(parser, performance_analyzer)
                complexity_analyzer = ComplexityAnalyzer(parser)
                security_analyzer = SecurityAnalyzer(parser)
                
                # 리니지 분석 추가
                lineage_analyzer = DataLineageAnalyzer(parser, structure_result)
                lineage_result = lineage_analyzer.analyze()
                
                # 분석 수행
                performance_result = performance_analyzer.analyze()
                optimization_result = optimization_advisor.analyze()
                complexity_result = complexity_analyzer.analyze()
                security_result = security_analyzer.analyze()
                
                # 리포트 생성
                report_generator = ReportGenerator(
                    parser, structure_analyzer, performance_analyzer,
                    optimization_advisor, complexity_analyzer, security_analyzer,
                    sql_file, lineage_analyzer
                )
                
                # 결과 출력
                print("## 쿼리 분석 결과")
                print()
                
                # 1. 기본 정보
                print("### 1. 기본 정보")
                print(f"- 쿼리 타입: {structure_result['query_type']}")
                print(f"- 쿼리 길이: {structure_result['query_length']} 문자, {structure_result['query_lines']} 라인")
                print(f"- 테이블 수: {structure_result['table_count']}개")
                print(f"- 컬럼 수: {structure_result['column_count']}개")
                print(f"- JOIN 수: {structure_result['join_count']}개")
                print(f"- 서브쿼리 수: {structure_result['subquery_count']}개")
                print(f"- 최대 서브쿼리 깊이: {structure_result['max_subquery_depth']}")
                print()
                
                # 2. 성능 분석
                print("### 2. 성능 분석")
                print(f"- 성능 점수: {performance_result['score']}/100")
                print(f"- 성능 레벨: {performance_result['level']}")
                print(f"- 성능 이슈 수: {len(performance_result['issues'])}개")
                print()
                
                if performance_result['issues']:
                    print("#### 성능 이슈:")
                    for i, issue in enumerate(performance_result['issues'][:5], 1):  # 최대 5개
                        print(f"{i}. [{issue['severity']}] {issue['type']}")
                        print(f"   - {issue['message']}")
                        print(f"   - 영향: {issue['impact']}")
                        print()
                
                # 3. 복잡도 분석
                print("### 3. 복잡도 분석")
                print(f"- 복잡도 점수: {complexity_result['score']}/100")
                print(f"- 복잡도 레벨: {complexity_result['level']}")
                print()
                
                metrics = complexity_result['metrics']
                print("#### 복잡도 지표:")
                print(f"- 쿼리 길이: {metrics['query_length']} 문자, {metrics['query_lines']} 라인")
                print(f"- 테이블 수: {metrics['table_count']}개")
                print(f"- JOIN 수: {metrics['join_count']}개")
                print(f"- 서브쿼리 수: {metrics['subquery_count']}개")
                print(f"- 최대 서브쿼리 깊이: {metrics['max_subquery_depth']}")
                print(f"- WHERE 조건 수: {metrics['where_clause_count']}개")
                print(f"- UNION 수: {metrics['union_count']}개")
                print()
                
                # 4. 보안 분석
                print("### 4. 보안 분석")
                print(f"- 보안 점수: {security_result['score']}/100")
                print(f"- 보안 레벨: {security_result['level']}")
                print(f"- 보안 취약점 수: {len(security_result['vulnerabilities'])}개")
                print()
                
                if security_result['vulnerabilities']:
                    print("#### 보안 취약점:")
                    for i, vuln in enumerate(security_result['vulnerabilities'], 1):
                        print(f"{i}. [{vuln['severity']}] {vuln['type']}")
                        print(f"   - {vuln['message']}")
                        print(f"   - 영향: {vuln['impact']}")
                        print(f"   - 권장사항: {vuln['recommendation']}")
                        print()
                else:
                    print("보안 취약점이 발견되지 않았습니다.")
                    print()
                
                # 5. 최적화 제안
                print("### 5. 최적화 제안")
                print(f"- 총 제안 수: {optimization_result['total_count']}개")
                print(f"  - HIGH 우선순위: {optimization_result['high_priority_count']}개")
                print(f"  - MEDIUM 우선순위: {optimization_result['medium_priority_count']}개")
                print(f"  - LOW 우선순위: {optimization_result['low_priority_count']}개")
                print()
                
                if optimization_result['suggestions']:
                    # HIGH 우선순위 제안
                    high_priority = [s for s in optimization_result['suggestions'] if s['priority'] == 'HIGH']
                    if high_priority:
                        print("#### HIGH 우선순위 제안:")
                        for i, suggestion in enumerate(high_priority[:3], 1):  # 최대 3개
                            print(f"{i}. [{suggestion['type']}] {suggestion['message']}")
                            if 'example' in suggestion:
                                print(f"   예시: {suggestion['example']}")
                            if 'expected_improvement' in suggestion:
                                print(f"   예상 개선율: {suggestion['expected_improvement']}")
                            print()
                    
                    # MEDIUM 우선순위 제안
                    medium_priority = [s for s in optimization_result['suggestions'] if s['priority'] == 'MEDIUM']
                    if medium_priority:
                        print("#### MEDIUM 우선순위 제안:")
                        for i, suggestion in enumerate(medium_priority[:3], 1):  # 최대 3개
                            print(f"{i}. [{suggestion['type']}] {suggestion['message']}")
                            if 'example' in suggestion:
                                print(f"   예시: {suggestion['example']}")
                            if 'expected_improvement' in suggestion:
                                print(f"   예상 개선율: {suggestion['expected_improvement']}")
                            print()
                
                # 리포트 파일 저장
                # 항상 프로젝트 루트의 logs/sql_analysis 디렉토리 사용
                workspace_root = os.path.dirname(os.path.abspath(__file__))
                output_dir = os.path.join(workspace_root, 'logs', 'sql_analysis')
                os.makedirs(output_dir, exist_ok=True)
                
                # 파일명 결정
                if sql_file:
                    base_name = os.path.splitext(os.path.basename(sql_file))[0]
                else:
                    base_name = 'inline_query'
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                
                # JSON 리포트 저장
                json_report = report_generator.generate_json()
                json_file = os.path.join(output_dir, f"{base_name}_analysis_{timestamp}.json")
                with open(json_file, 'w', encoding='utf-8') as f:
                    json.dump(json_report, f, ensure_ascii=False, indent=2)
                print(f"[JSON 리포트 저장] {json_file}")
                
                # 마크다운 리포트 저장
                md_report = report_generator.generate_markdown()
                md_file = os.path.join(output_dir, f"{base_name}_analysis_{timestamp}.md")
                with open(md_file, 'w', encoding='utf-8') as f:
                    f.write(md_report)
                print(f"[마크다운 리포트 저장] {md_file}")
                
                # 리니지 마크다운 리포트 저장
                lineage_md_report = report_generator.generate_lineage_markdown()
                lineage_md_file = os.path.join(output_dir, f"{base_name}_lineage_{timestamp}.md")
                with open(lineage_md_file, 'w', encoding='utf-8') as f:
                    f.write(lineage_md_report)
                print(f"[리니지 마크다운 리포트 저장] {lineage_md_file}")
                
                # 리니지 JSON 리포트 저장
                lineage_json_report = report_generator.generate_lineage_json()
                lineage_json_file = os.path.join(output_dir, f"{base_name}_lineage_{timestamp}.json")
                with open(lineage_json_file, 'w', encoding='utf-8') as f:
                    json.dump(lineage_json_report, f, ensure_ascii=False, indent=2)
                print(f"[리니지 JSON 리포트 저장] {lineage_json_file}")
                print()
                print()
                
            except Exception as e:
                print(f"[경고] SQL 파일 분석 중 오류 발생 ({sql_file}): {str(e)}")
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

def analyze_impact(sql_file_path: str, target_table: str, target_column: str = None) -> dict:
    """영향도 분석 함수 (API에서 호출용)"""
    try:
        with open(sql_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            sql_content = f.read()
        
        if not sql_content.strip():
            return {'success': False, 'error': 'SQL 파일이 비어있습니다.'}
        
        # 쿼리 분석
        parser = SQLQueryParser(sql_content)
        structure_analyzer = QueryStructureAnalyzer(parser)
        structure_result = structure_analyzer.analyze()
        lineage_analyzer = DataLineageAnalyzer(parser, structure_result)
        
        # 영향도 분석
        impact_analyzer = ImpactAnalyzer(parser, lineage_analyzer, structure_analyzer)
        impact_result = impact_analyzer.analyze(target_table, target_column)
        
        return {
            'success': True,
            'impact_analysis': impact_result
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == "__main__":
    # 영향도 분석 모드 확인 (환경 변수 또는 명령줄 인자)
    if len(sys.argv) >= 3 and sys.argv[1] == '--impact':
        # 영향도 분석 모드
        sql_file = sys.argv[2]
        target_table = sys.argv[3] if len(sys.argv) > 3 else None
        target_column = sys.argv[4] if len(sys.argv) > 4 else None
        
        if not target_table:
            print('{"success": false, "error": "테이블명이 필요합니다."}')
            sys.exit(1)
        
        result = analyze_impact(sql_file, target_table, target_column)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        # 일반 분석 모드
        main()


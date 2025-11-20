#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 분석기 비교 스크립트

현재 구현과 업계 표준 도구(PostgreSQL EXPLAIN ANALYZE)를 비교 분석합니다.

사용 방법:
  python compare_sql_analyzers.py <SQL 파일>
  
예시:
  python compare_sql_analyzers.py queries/complex_query_500.sql
"""

import sys
import os
import json
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
    PerformanceAnalyzer = mcp_module.PerformanceAnalyzer
    OptimizationAdvisor = mcp_module.OptimizationAdvisor
    ComplexityAnalyzer = mcp_module.ComplexityAnalyzer
    SecurityAnalyzer = mcp_module.SecurityAnalyzer
    DataLineageAnalyzer = mcp_module.DataLineageAnalyzer
    ReportGenerator = mcp_module.ReportGenerator
except Exception as e:
    print(f"[오류] MCP 서버 모듈을 불러올 수 없습니다: {e}", file=sys.stderr)
    sys.exit(1)

def analyze_with_current_implementation(sql_file: str) -> dict:
    """현재 구현으로 분석"""
    print(f"\n[1/2] 현재 구현으로 분석 중...")
    
    with open(sql_file, 'r', encoding='utf-8', errors='ignore') as f:
        sql_content = f.read()
    
    # 쿼리 분석
    parser = SQLQueryParser(sql_content)
    structure_analyzer = QueryStructureAnalyzer(parser)
    structure_result = structure_analyzer.analyze()
    performance_analyzer = PerformanceAnalyzer(parser)
    optimization_advisor = OptimizationAdvisor(parser, performance_analyzer)
    complexity_analyzer = ComplexityAnalyzer(parser)
    security_analyzer = SecurityAnalyzer(parser)
    lineage_analyzer = DataLineageAnalyzer(parser, structure_result)
    
    # 분석 수행
    performance_result = performance_analyzer.analyze()
    optimization_result = optimization_advisor.analyze()
    complexity_result = complexity_analyzer.analyze()
    security_result = security_analyzer.analyze()
    lineage_result = lineage_analyzer.analyze()
    
    # 리포트 생성
    report_generator = ReportGenerator(
        parser, structure_analyzer, performance_analyzer,
        optimization_advisor, complexity_analyzer, security_analyzer,
        sql_file, lineage_analyzer
    )
    
    result = {
        'analysis_method': 'static_analysis',
        'structure': structure_result,
        'performance': performance_result,
        'complexity': complexity_result,
        'security': security_result,
        'optimization': optimization_result,
        'lineage': lineage_result,
        'metadata': {
            'query_length': structure_result.get('query_length', 0),
            'query_lines': structure_result.get('query_lines', 0),
            'query_type': structure_result.get('query_type', 'UNKNOWN'),
            'table_count': len(structure_result.get('tables', [])),
            'join_count': len(structure_result.get('joins', [])),
            'subquery_count': len(structure_result.get('subqueries', []))
        }
    }
    
    print(f"✓ 분석 완료")
    print(f"  - 테이블 수: {result['metadata']['table_count']}개")
    print(f"  - JOIN 수: {result['metadata']['join_count']}개")
    print(f"  - 성능 점수: {performance_result['score']}/100")
    print(f"  - 복잡도: {complexity_result['level']}")
    
    return result

def analyze_with_postgresql_explain(sql_file: str) -> dict:
    """PostgreSQL EXPLAIN ANALYZE로 분석 (시뮬레이션)"""
    print(f"\n[2/2] PostgreSQL EXPLAIN ANALYZE 분석 (시뮬레이션)...")
    
    # 실제 PostgreSQL 연결 없이 시뮬레이션
    # 실제 환경에서는 psycopg2를 사용하여 연결해야 함
    
    result = {
        'analysis_method': 'postgresql_explain_analyze',
        'note': '실제 PostgreSQL 데이터베이스 연결이 필요합니다.',
        'simulation': True,
        'explain_plan': {
            'note': 'EXPLAIN ANALYZE 결과는 실제 데이터베이스에서 실행해야 합니다.',
            'example_command': f'EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <쿼리>',
            'expected_output': [
                '실행 계획 트리',
                '각 연산자의 비용',
                '실제 실행 시간',
                '처리된 행 수',
                '인덱스 사용 여부',
                '조인 방식 (Nested Loop, Hash Join 등)'
            ]
        },
        'comparison_note': '현재 구현은 정적 분석만 수행하므로 실제 실행 계획과 비교가 필요합니다.'
    }
    
    print(f"⚠ 시뮬레이션 모드 (실제 PostgreSQL 연결 필요)")
    print(f"  실제 분석을 위해서는:")
    print(f"  1. PostgreSQL 데이터베이스에 테이블 생성")
    print(f"  2. EXPLAIN (ANALYZE, BUFFERS, VERBOSE) <쿼리> 실행")
    print(f"  3. 결과를 JSON 형식으로 저장")
    
    return result

def compare_results(current_result: dict, postgresql_result: dict) -> dict:
    """두 분석 결과 비교"""
    print(f"\n[비교 분석]")
    
    comparison = {
        'comparison_date': datetime.now().isoformat(),
        'current_implementation': {
            'method': '정적 분석 (Static Analysis)',
            'tools': ['sqlparse'],
            'strengths': [
                '데이터베이스 연결 불필요',
                '빠른 분석 속도',
                '쿼리 구조 분석',
                '패턴 기반 성능 분석',
                '보안 취약점 감지'
            ],
            'limitations': [
                '실제 실행 계획 없음',
                '실제 성능 측정 불가',
                '인덱스 사용 여부 추정만 가능',
                '비용 계산 없음'
            ]
        },
        'postgresql_explain': {
            'method': '동적 분석 (Dynamic Analysis)',
            'tools': ['PostgreSQL EXPLAIN ANALYZE'],
            'strengths': [
                '실제 실행 계획 제공',
                '정확한 비용 계산',
                '실제 실행 시간 측정',
                '인덱스 사용 여부 확인',
                '조인 방식 분석'
            ],
            'limitations': [
                '데이터베이스 연결 필요',
                '실제 쿼리 실행 필요',
                '데이터가 있어야 함'
            ]
        },
        'recommendations': [
            {
                'priority': 'HIGH',
                'title': '하이브리드 분석 방식 도입',
                'description': '정적 분석 + 동적 분석을 결합하여 더 정확한 분석 제공',
                'action': 'PostgreSQL 연결 옵션 추가 및 EXPLAIN ANALYZE 결과 통합'
            },
            {
                'priority': 'MEDIUM',
                'title': '실행 요약 추가',
                'description': '실제 실행 시간, 비용, 처리된 행 수 정보 제공',
                'action': 'EXPLAIN ANALYZE 결과 파싱 및 통합'
            },
            {
                'priority': 'MEDIUM',
                'title': '인덱스 사용 여부 확인',
                'description': '실제 인덱스 사용 여부를 확인하여 더 정확한 성능 분석',
                'action': 'PostgreSQL pg_indexes 시스템 테이블 조회'
            }
        ],
        'current_analysis_summary': {
            'performance_score': current_result.get('performance', {}).get('score', 0),
            'performance_level': current_result.get('performance', {}).get('level', 'UNKNOWN'),
            'complexity_score': current_result.get('complexity', {}).get('score', 0),
            'complexity_level': current_result.get('complexity', {}).get('level', 'UNKNOWN'),
            'security_score': current_result.get('security', {}).get('score', 0),
            'security_level': current_result.get('security', {}).get('level', 'UNKNOWN'),
            'total_issues': len(current_result.get('performance', {}).get('issues', [])) + 
                          len(current_result.get('security', {}).get('vulnerabilities', [])),
            'optimization_suggestions': len(current_result.get('optimization', {}).get('suggestions', []))
        }
    }
    
    print(f"✓ 비교 완료")
    print(f"\n현재 구현 분석 결과:")
    print(f"  - 성능 점수: {comparison['current_analysis_summary']['performance_score']}/100 ({comparison['current_analysis_summary']['performance_level']})")
    print(f"  - 복잡도: {comparison['current_analysis_summary']['complexity_score']}/100 ({comparison['current_analysis_summary']['complexity_level']})")
    print(f"  - 보안 점수: {comparison['current_analysis_summary']['security_score']}/100 ({comparison['current_analysis_summary']['security_level']})")
    print(f"  - 발견된 이슈: {comparison['current_analysis_summary']['total_issues']}개")
    print(f"  - 최적화 제안: {comparison['current_analysis_summary']['optimization_suggestions']}개")
    
    return comparison

def generate_comparison_report(current_result: dict, postgresql_result: dict, comparison: dict, sql_file: str) -> str:
    """비교 리포트 생성"""
    base_name = os.path.splitext(os.path.basename(sql_file))[0]
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = 'comparison'
    os.makedirs(output_dir, exist_ok=True)
    
    # JSON 리포트 저장
    json_file = os.path.join(output_dir, f"{base_name}_comparison_{timestamp}.json")
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'current_result': current_result,
            'postgresql_result': postgresql_result,
            'comparison': comparison
        }, f, ensure_ascii=False, indent=2)
    
    # 마크다운 리포트 생성
    md_file = os.path.join(output_dir, f"{base_name}_comparison_{timestamp}.md")
    md_content = f"""# SQL 분석기 비교 리포트

**생성 일시**: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**분석 대상**: {sql_file}

## 1. 분석 방법 비교

### 1.1 현재 구현 (정적 분석)

**방식**: 정적 분석 (Static Analysis)  
**도구**: sqlparse 라이브러리

**장점**:
- 데이터베이스 연결 불필요
- 빠른 분석 속도
- 쿼리 구조 분석
- 패턴 기반 성능 분석
- 보안 취약점 감지

**제한사항**:
- 실제 실행 계획 없음
- 실제 성능 측정 불가
- 인덱스 사용 여부 추정만 가능
- 비용 계산 없음

### 1.2 PostgreSQL EXPLAIN ANALYZE (동적 분석)

**방식**: 동적 분석 (Dynamic Analysis)  
**도구**: PostgreSQL EXPLAIN ANALYZE

**장점**:
- 실제 실행 계획 제공
- 정확한 비용 계산
- 실제 실행 시간 측정
- 인덱스 사용 여부 확인
- 조인 방식 분석

**제한사항**:
- 데이터베이스 연결 필요
- 실제 쿼리 실행 필요
- 데이터가 있어야 함

## 2. 현재 구현 분석 결과

### 2.1 성능 분석
- **점수**: {comparison['current_analysis_summary']['performance_score']}/100
- **수준**: {comparison['current_analysis_summary']['performance_level']}
- **이슈 수**: {len(current_result.get('performance', {}).get('issues', []))}개

### 2.2 복잡도 분석
- **점수**: {comparison['current_analysis_summary']['complexity_score']}/100
- **수준**: {comparison['current_analysis_summary']['complexity_level']}

### 2.3 보안 분석
- **점수**: {comparison['current_analysis_summary']['security_score']}/100
- **수준**: {comparison['current_analysis_summary']['security_level']}
- **취약점 수**: {len(current_result.get('security', {}).get('vulnerabilities', []))}개

### 2.4 최적화 제안
- **제안 수**: {comparison['current_analysis_summary']['optimization_suggestions']}개

## 3. 비교 분석

### 3.1 분석 방식 차이

| 항목 | 현재 구현 | PostgreSQL EXPLAIN ANALYZE |
|------|----------|---------------------------|
| 분석 방식 | 정적 분석 | 동적 분석 |
| 데이터베이스 연결 | 불필요 | 필요 |
| 실행 계획 | 없음 | 제공 |
| 실제 성능 측정 | 불가능 | 가능 |
| 비용 계산 | 없음 | 제공 |

### 3.2 분석 항목 비교

| 분석 항목 | 현재 구현 | PostgreSQL EXPLAIN ANALYZE |
|----------|----------|---------------------------|
| 실행 요약 | 없음 | 실행 시간, 행 수, 비용 |
| 구조 분석 | AST 파싱 | 실행 계획 트리 |
| 성능 분석 | 패턴 매칭 | 실제 실행 통계 |
| 보안 분석 | 패턴 감지 | 동일 (정적 분석) |
| 최적화 제안 | 경험 기반 | 실행 통계 기반 |

## 4. 개선 방안

### 4.1 하이브리드 분석 방식 도입
- 정적 분석 + 동적 분석 결합
- PostgreSQL 연결 옵션 추가
- EXPLAIN ANALYZE 결과 통합

### 4.2 실행 요약 추가
- 실행 시간 측정
- 비용 계산
- 처리된 행 수 확인

### 4.3 인덱스 사용 여부 확인
- 실제 인덱스 사용 여부 확인
- 인덱스 효율성 분석

## 5. 결론

현재 구현은 **정적 분석**에 특화되어 있어 빠른 분석과 보안 검사에 강점이 있습니다.  
하지만 **실제 성능 측정**과 **실행 계획 분석**을 위해서는 PostgreSQL EXPLAIN ANALYZE와 같은 동적 분석 도구가 필요합니다.

**권장사항**: 하이브리드 분석 방식을 도입하여 두 방식의 장점을 결합하는 것이 좋습니다.

---
**생성된 파일**:
- JSON 리포트: `{json_file}`
- 마크다운 리포트: `{md_file}`
"""
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    print(f"\n✓ 리포트 생성 완료")
    print(f"  - JSON: {json_file}")
    print(f"  - 마크다운: {md_file}")
    
    return md_file

def main():
    """메인 함수"""
    if len(sys.argv) < 2:
        print("사용 방법: python compare_sql_analyzers.py <SQL 파일>", file=sys.stderr)
        sys.exit(1)
    
    sql_file = sys.argv[1]
    
    if not os.path.exists(sql_file):
        print(f"[오류] SQL 파일을 찾을 수 없습니다: {sql_file}", file=sys.stderr)
        sys.exit(1)
    
    try:
        print("=" * 80)
        print("SQL 분석기 비교 분석")
        print("=" * 80)
        
        # 현재 구현으로 분석
        current_result = analyze_with_current_implementation(sql_file)
        
        # PostgreSQL EXPLAIN ANALYZE 분석 (시뮬레이션)
        postgresql_result = analyze_with_postgresql_explain(sql_file)
        
        # 결과 비교
        comparison = compare_results(current_result, postgresql_result)
        
        # 리포트 생성
        report_file = generate_comparison_report(current_result, postgresql_result, comparison, sql_file)
        
        print("\n" + "=" * 80)
        print("비교 분석 완료!")
        print("=" * 80)
        
    except Exception as e:
        print(f"[오류] 비교 분석 실패: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


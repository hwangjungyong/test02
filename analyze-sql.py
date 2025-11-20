#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 쿼리 분석 간단 실행 스크립트

사용 방법:
  python analyze-sql.py [SQL 파일 경로]
  
예시:
  python analyze-sql.py queries/complex_query_750.sql
"""

import sys
import os
from pathlib import Path

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    if len(sys.argv) < 2:
        print("사용 방법: python analyze-sql.py <SQL 파일 경로>")
        print("\n예시:")
        print("  python analyze-sql.py queries/complex_query_750.sql")
        sys.exit(1)
    
    sql_file = sys.argv[1]
    
    if not os.path.exists(sql_file):
        print(f"오류: 파일을 찾을 수 없습니다: {sql_file}")
        sys.exit(1)
    
    print(f"SQL 파일 분석 시작: {sql_file}")
    print("=" * 80)
    
    # test-sql-query-analyzer.py 실행
    try:
        import subprocess
        result = subprocess.run(
            [sys.executable, "test-sql-query-analyzer.py", sql_file],
            capture_output=False,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print("\n" + "=" * 80)
            print("분석 완료!")
            
            # 결과 파일 위치 안내
            sql_dir = os.path.dirname(os.path.abspath(sql_file))
            analysis_dir = os.path.join(sql_dir, 'sql_analysis')
            base_name = os.path.splitext(os.path.basename(sql_file))[0]
            
            print(f"\n결과 파일 위치: {analysis_dir}")
            print(f"- JSON 리포트: {base_name}_analysis_*.json")
            print(f"- 마크다운 리포트: {base_name}_analysis_*.md")
            print(f"- 리니지 시각화 HTML: {base_name}_lineage_visualization_*.html")
        else:
            print(f"\n오류: 분석 중 오류가 발생했습니다. (종료 코드: {result.returncode})")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"\n오류: 스크립트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()


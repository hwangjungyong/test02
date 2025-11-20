# -*- coding: utf-8 -*-
import sys
import io

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# test-error-log-analyzer.py에서 클래스 import
import importlib.util
spec = importlib.util.spec_from_file_location("error_analyzer", "test-error-log-analyzer.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

LogParser = module.LogParser
ErrorAnalyzer = module.ErrorAnalyzer

# 로그 파일 읽기
with open('logs/google-error-sample.log', 'r', encoding='utf-8') as f:
    log_content = f.read()

# 분석 실행
print("=" * 60)
print("구글 에러 로그 분석 결과")
print("=" * 60)
print()

parser = LogParser()
analyzer = ErrorAnalyzer()

errors = parser.parse_errors(log_content)
results = analyzer.analyze_errors(errors)

print(f"총 에러 수: {len(errors)}건")
print()

# 에러 유형별 분류
from collections import Counter
error_types = Counter([e.get("type", "UNKNOWN") for e in errors])
print("에러 유형별 분류:")
for et, count in error_types.most_common():
    print(f"  - {et}: {count}건")
print()

# 심각도별 분류
severity_counts = Counter([e.get("severity", "UNKNOWN") for e in errors])
print("심각도별 분류:")
for sev, count in severity_counts.most_common():
    print(f"  - {sev}: {count}건")
print()

# 상위 5개 에러 상세 정보
print("=" * 60)
print("상위 5개 에러 상세 정보")
print("=" * 60)
print()

for i, error in enumerate(errors[:5], 1):
    print(f"에러 #{i}")
    print(f"  발생일시: {error.get('timestamp', 'N/A')}")
    print(f"  에러 유형: {error.get('type', 'UNKNOWN')}")
    print(f"  심각도: {error.get('severity', 'UNKNOWN')}")
    print(f"  메시지: {error.get('message', 'N/A')[:100]}...")
    if error.get('file'):
        print(f"  파일: {error.get('file')}")
    if error.get('line'):
        print(f"  라인: {error.get('line')}")
    print()


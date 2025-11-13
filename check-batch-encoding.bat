@echo off
REM ========================================
REM 배치 파일 인코딩 확인 및 변환 스크립트
REM ========================================

echo 배치 파일 인코딩을 확인하고 변환합니다...
echo.

REM 현재 코드 페이지 확인
chcp
echo.

REM 배치 파일 목록
echo 다음 배치 파일들의 인코딩을 확인합니다:
echo   - start-dev.bat
echo   - build-and-run-mcp.bat
echo   - start-python-server.bat
echo   - start-servers.bat
echo.

echo 중요: 배치 파일은 ANSI(CP949) 인코딩으로 저장되어야 합니다.
echo.
echo 해결 방법:
echo   1. 메모장에서 파일 열기
echo   2. 다른 이름으로 저장
echo   3. 인코딩을 "ANSI"로 선택
echo   4. 저장
echo.

pause


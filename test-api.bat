@echo off
chcp 949 >nul 2>&1
echo === API 서버 테스트 ===
echo.

echo 1. 회원가입 테스트...
curl -X POST http://localhost:3001/api/auth/signup ^
  -H "Content-Type: application/json" ^
  -d "{\"email\":\"test@example.com\",\"password\":\"password123\",\"name\":\"테스트 사용자\"}"

echo.
echo.
echo 테스트 완료!
echo.
pause


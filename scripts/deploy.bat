@echo off
REM 배포 스크립트 (Windows)
REM 사용법: deploy.bat [patch|minor|major]

setlocal enabledelayedexpansion

echo ========================================
echo 배포 스크립트 시작
echo ========================================
echo.

REM 버전 타입 확인
set VERSION_TYPE=%1
if "%VERSION_TYPE%"=="" set VERSION_TYPE=patch

echo [1/6] 버전 업데이트 (%VERSION_TYPE%)...
call npm run version -- %VERSION_TYPE%
if errorlevel 1 (
    echo ❌ 버전 업데이트 실패
    exit /b 1
)
echo ✅ 버전 업데이트 완료
echo.

echo [2/6] Git 상태 확인...
git status --short
if errorlevel 1 (
    echo ❌ Git 상태 확인 실패
    exit /b 1
)
echo ✅ Git 상태 확인 완료
echo.

echo [3/6] 변경사항 커밋...
for /f "tokens=*" %%i in ('node -p "require('./package.json').version"') do set VERSION=%%i
git add .
git commit -m "chore: 버전 업데이트 %VERSION%"
if errorlevel 1 (
    echo ⚠️ 커밋 실패 (변경사항이 없을 수 있음)
)
echo ✅ 커밋 완료
echo.

echo [4/6] Git 태그 생성...
git tag v%VERSION%
if errorlevel 1 (
    echo ⚠️ 태그 생성 실패 (이미 존재할 수 있음)
)
echo ✅ 태그 생성 완료
echo.

echo [5/6] 빌드 테스트...
call npm run build
if errorlevel 1 (
    echo ❌ 빌드 실패
    exit /b 1
)
echo ✅ 빌드 성공
echo.

echo [6/6] 배포 옵션 선택...
echo.
echo 1. 로컬에만 커밋 (태그 생성 안함)
echo 2. 원격 저장소에 푸시 (태그 포함)
echo 3. 취소
echo.
set /p DEPLOY_OPTION="선택 (1-3): "

if "%DEPLOY_OPTION%"=="1" (
    echo 로컬 커밋만 수행합니다...
    echo ✅ 완료
) else if "%DEPLOY_OPTION%"=="2" (
    echo 원격 저장소에 푸시합니다...
    git push
    if errorlevel 1 (
        echo ❌ 푸시 실패
        exit /b 1
    )
    git push --tags
    if errorlevel 1 (
        echo ⚠️ 태그 푸시 실패
    )
    echo ✅ 푸시 완료
) else (
    echo 배포 취소됨
    exit /b 0
)

echo.
echo ========================================
echo 배포 완료!
echo 버전: %VERSION%
echo ========================================


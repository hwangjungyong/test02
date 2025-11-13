#!/bin/bash
# 배포 스크립트 (Linux/Mac)
# 사용법: ./scripts/deploy.sh [patch|minor|major]

set -e

VERSION_TYPE=${1:-patch}

echo "========================================"
echo "배포 스크립트 시작"
echo "========================================"
echo ""

echo "[1/6] 버전 업데이트 ($VERSION_TYPE)..."
npm run version -- $VERSION_TYPE
echo "✅ 버전 업데이트 완료"
echo ""

echo "[2/6] Git 상태 확인..."
git status --short
echo "✅ Git 상태 확인 완료"
echo ""

echo "[3/6] 변경사항 커밋..."
VERSION=$(node -p "require('./package.json').version")
git add .
git commit -m "chore: 버전 업데이트 $VERSION" || echo "⚠️ 커밋 실패 (변경사항이 없을 수 있음)"
echo "✅ 커밋 완료"
echo ""

echo "[4/6] Git 태그 생성..."
git tag v$VERSION || echo "⚠️ 태그 생성 실패 (이미 존재할 수 있음)"
echo "✅ 태그 생성 완료"
echo ""

echo "[5/6] 빌드 테스트..."
npm run build
echo "✅ 빌드 성공"
echo ""

echo "[6/6] 배포 옵션 선택..."
echo ""
echo "1. 로컬에만 커밋 (태그 생성 안함)"
echo "2. 원격 저장소에 푸시 (태그 포함)"
echo "3. 취소"
echo ""
read -p "선택 (1-3): " DEPLOY_OPTION

case $DEPLOY_OPTION in
    1)
        echo "로컬 커밋만 수행합니다..."
        echo "✅ 완료"
        ;;
    2)
        echo "원격 저장소에 푸시합니다..."
        git push
        git push --tags || echo "⚠️ 태그 푸시 실패"
        echo "✅ 푸시 완료"
        ;;
    3)
        echo "배포 취소됨"
        exit 0
        ;;
    *)
        echo "잘못된 선택"
        exit 1
        ;;
esac

echo ""
echo "========================================"
echo "배포 완료!"
echo "버전: $VERSION"
echo "========================================"


#!/usr/bin/env node

/**
 * 자동 버전 관리 스크립트
 * 
 * 사용법:
 *   node scripts/version-bump.js patch   # 0.0.1 -> 0.0.2
 *   node scripts/version-bump.js minor   # 0.0.1 -> 0.1.0
 *   node scripts/version-bump.js major   # 0.0.1 -> 1.0.0
 *   node scripts/version-bump.js         # 현재 버전 표시
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const PROJECT_ROOT = path.join(__dirname, '..');
const PACKAGE_JSON = path.join(PROJECT_ROOT, 'package.json');
const GUIDE_MD = path.join(PROJECT_ROOT, '가이드.md');
const README_MD = path.join(PROJECT_ROOT, 'README.md');

// 버전 파싱 및 증가
function bumpVersion(currentVersion, type) {
  const parts = currentVersion.split('.').map(Number);
  const [major, minor, patch] = parts;

  switch (type) {
    case 'major':
      return `${major + 1}.0.0`;
    case 'minor':
      return `${major}.${minor + 1}.0`;
    case 'patch':
      return `${major}.${minor}.${patch + 1}`;
    default:
      return currentVersion;
  }
}

// 파일에서 버전 읽기
function getCurrentVersion() {
  const packageJson = JSON.parse(fs.readFileSync(PACKAGE_JSON, 'utf8'));
  return packageJson.version;
}

// package.json 업데이트
function updatePackageJson(newVersion) {
  const packageJson = JSON.parse(fs.readFileSync(PACKAGE_JSON, 'utf8'));
  packageJson.version = newVersion;
  fs.writeFileSync(PACKAGE_JSON, JSON.stringify(packageJson, null, 2) + '\n');
  console.log(`✅ package.json 업데이트: ${newVersion}`);
}

// 가이드.md 업데이트
function updateGuideMd(newVersion) {
  let content = fs.readFileSync(GUIDE_MD, 'utf8');
  
  // 버전 정보 업데이트
  content = content.replace(
    /\*\*프로젝트 버전\*\*: \d+\.\d+\.\d+/g,
    `**프로젝트 버전**: ${newVersion}`
  );
  
  // 마지막 업데이트 날짜 업데이트
  const today = new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  content = content.replace(
    /\*\*마지막 업데이트\*\*: \d+년 \d+월/g,
    `**마지막 업데이트**: ${today}`
  );
  
  fs.writeFileSync(GUIDE_MD, content);
  console.log(`✅ 가이드.md 업데이트: ${newVersion}`);
}

// README.md 업데이트
function updateReadmeMd(newVersion) {
  let content = fs.readFileSync(README_MD, 'utf8');
  
  // 마지막 업데이트 날짜 업데이트
  const today = new Date().toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
  
  if (content.includes('**마지막 업데이트**:')) {
    content = content.replace(
      /\*\*마지막 업데이트\*\*: .+/g,
      `**마지막 업데이트**: ${today}`
    );
  } else {
    content += `\n---\n\n**마지막 업데이트**: ${today}\n`;
  }
  
  fs.writeFileSync(README_MD, content);
  console.log(`✅ README.md 업데이트`);
}

// CHANGELOG.md 생성/업데이트
function updateChangelog(newVersion, type) {
  const CHANGELOG = path.join(PROJECT_ROOT, 'CHANGELOG.md');
  const today = new Date().toISOString().split('T')[0];
  
  let changelog = '';
  if (fs.existsSync(CHANGELOG)) {
    changelog = fs.readFileSync(CHANGELOG, 'utf8');
  } else {
    changelog = '# 변경 이력 (Changelog)\n\n';
  }
  
  const versionNote = `## [${newVersion}] - ${today}\n\n`;
  const typeNote = type === 'major' ? '### 주요 변경사항\n' :
                   type === 'minor' ? '### 새로운 기능\n' :
                   '### 수정사항\n';
  
  const newEntry = versionNote + typeNote + '- 버전 업데이트\n\n';
  
  // 기존 버전 정보가 있으면 그 앞에 추가
  if (changelog.includes('## [')) {
    changelog = changelog.replace(/(# 변경 이력.*?\n\n)/, `$1${newEntry}`);
  } else {
    changelog += newEntry;
  }
  
  fs.writeFileSync(CHANGELOG, changelog);
  console.log(`✅ CHANGELOG.md 업데이트: ${newVersion}`);
}

// 메인 함수
function main() {
  const type = process.argv[2];
  const currentVersion = getCurrentVersion();
  
  if (!type) {
    console.log(`현재 버전: ${currentVersion}`);
    console.log('\n사용법:');
    console.log('  node scripts/version-bump.js patch   # 패치 버전 증가 (0.0.1 -> 0.0.2)');
    console.log('  node scripts/version-bump.js minor   # 마이너 버전 증가 (0.0.1 -> 0.1.0)');
    console.log('  node scripts/version-bump.js major   # 메이저 버전 증가 (0.0.1 -> 1.0.0)');
    process.exit(0);
  }
  
  if (!['patch', 'minor', 'major'].includes(type)) {
    console.error(`❌ 잘못된 버전 타입: ${type}`);
    console.error('사용 가능한 타입: patch, minor, major');
    process.exit(1);
  }
  
  const newVersion = bumpVersion(currentVersion, type);
  
  console.log(`\n🔄 버전 업데이트: ${currentVersion} -> ${newVersion}\n`);
  
  try {
    updatePackageJson(newVersion);
    updateGuideMd(newVersion);
    updateReadmeMd(newVersion);
    updateChangelog(newVersion, type);
    
    console.log(`\n✅ 버전 업데이트 완료: ${newVersion}`);
    console.log('\n다음 단계:');
    console.log('  1. 변경사항 확인: git status');
    console.log('  2. 변경사항 커밋: git commit -am "chore: 버전 업데이트 ' + newVersion + '"');
    console.log('  3. 태그 생성: git tag v' + newVersion);
    console.log('  4. 푸시: git push && git push --tags');
  } catch (error) {
    console.error('❌ 오류 발생:', error.message);
    process.exit(1);
  }
}

main();


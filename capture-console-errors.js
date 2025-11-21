#!/usr/bin/env node
/**
 * 브라우저 콘솔 에러 로그 캡처 스크립트
 * 
 * 사용 방법:
 *   node capture-console-errors.js [URL]
 * 
 * 예시:
 *   node capture-console-errors.js http://localhost:5173
 */

import { chromium } from 'playwright';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import { writeFileSync } from 'fs';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// 명령줄 인자에서 URL 가져오기 (기본값: localhost:5173)
const url = process.argv[2] || 'http://localhost:5173';
const waitTime = 10000; // 10초

console.log('='.repeat(80));
console.log('브라우저 콘솔 에러 로그 캡처 시작');
console.log('='.repeat(80));
console.log(`URL: ${url}`);
console.log(`대기 시간: ${waitTime / 1000}초`);
console.log('='.repeat(80));
console.log();

let browser;
let page;

try {
  // 브라우저 시작
  console.log('[1/4] 브라우저 시작 중...');
  browser = await chromium.launch({
    headless: false, // 브라우저 창 표시
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  // 새 페이지 생성
  console.log('[2/4] 새 페이지 생성 중...');
  const context = await browser.newContext({
    viewport: { width: 1920, height: 1080 }
  });
  page = await context.newPage();

  // 콘솔 메시지 수집
  const consoleMessages = [];
  const errors = [];
  const warnings = [];
  const networkErrors = [];

  // 콘솔 메시지 리스너
  page.on('console', msg => {
    const type = msg.type();
    const text = msg.text();
    const location = msg.location();
    
    const message = {
      type,
      text,
      timestamp: new Date().toISOString(),
      location: location ? {
        url: location.url,
        lineNumber: location.lineNumber,
        columnNumber: location.columnNumber
      } : null
    };

    consoleMessages.push(message);

    if (type === 'error') {
      errors.push(message);
      console.log(`[콘솔 에러] ${text}`);
    } else if (type === 'warning') {
      warnings.push(message);
      console.log(`[콘솔 경고] ${text}`);
    }
  });

  // 페이지 에러 리스너
  page.on('pageerror', error => {
    const errorMessage = {
      type: 'pageerror',
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString()
    };
    errors.push(errorMessage);
    console.log(`[페이지 에러] ${error.message}`);
  });

  // 요청 실패 리스너
  page.on('requestfailed', request => {
    const failure = request.failure();
    const errorMessage = {
      type: 'requestfailed',
      url: request.url(),
      method: request.method(),
      failure: failure ? failure.errorText : 'Unknown',
      timestamp: new Date().toISOString()
    };
    networkErrors.push(errorMessage);
    console.log(`[네트워크 에러] ${request.method()} ${request.url()}: ${failure?.errorText || 'Unknown'}`);
  });

  // 응답 에러 리스너 (4xx, 5xx)
  page.on('response', response => {
    const status = response.status();
    if (status >= 400) {
      const errorMessage = {
        type: 'http_error',
        url: response.url(),
        status,
        statusText: response.statusText(),
        timestamp: new Date().toISOString()
      };
      networkErrors.push(errorMessage);
      console.log(`[HTTP 에러] ${status} ${response.statusText()}: ${response.url()}`);
    }
  });

  // 페이지 로드
  console.log(`[3/4] 페이지 로드 중: ${url}`);
  await page.goto(url, {
    waitUntil: 'networkidle',
    timeout: 30000
  });

  console.log(`[4/4] ${waitTime / 1000}초 대기 중... (콘솔 에러 모니터링)`);
  await page.waitForTimeout(waitTime);

  // 결과 정리
  const result = {
    url,
    captureTime: new Date().toISOString(),
    waitTimeSeconds: waitTime / 1000,
    summary: {
      totalConsoleMessages: consoleMessages.length,
      errors: errors.length,
      warnings: warnings.length,
      networkErrors: networkErrors.length
    },
    errors: errors,
    warnings: warnings,
    networkErrors: networkErrors,
    allConsoleMessages: consoleMessages
  };

  // 결과 출력
  console.log();
  console.log('='.repeat(80));
  console.log('캡처 완료');
  console.log('='.repeat(80));
  console.log(`총 콘솔 메시지: ${result.summary.totalConsoleMessages}`);
  console.log(`에러: ${result.summary.errors}`);
  console.log(`경고: ${result.summary.warnings}`);
  console.log(`네트워크 에러: ${result.summary.networkErrors}`);
  console.log('='.repeat(80));
  console.log();

  // 에러가 있으면 상세 출력
  if (errors.length > 0) {
    console.log('📛 에러 목록:');
    console.log('-'.repeat(80));
    errors.forEach((error, index) => {
      console.log(`\n[${index + 1}] ${error.type.toUpperCase()}`);
      console.log(`   메시지: ${error.message || error.text}`);
      if (error.stack) {
        console.log(`   스택:\n${error.stack.split('\n').map(line => `   ${line}`).join('\n')}`);
      }
      if (error.location) {
        console.log(`   위치: ${error.location.url}:${error.location.lineNumber}:${error.location.columnNumber}`);
      }
      console.log(`   시간: ${error.timestamp}`);
    });
    console.log('-'.repeat(80));
    console.log();
  }

  if (warnings.length > 0) {
    console.log('⚠️  경고 목록:');
    console.log('-'.repeat(80));
    warnings.forEach((warning, index) => {
      console.log(`\n[${index + 1}] ${warning.text}`);
      if (warning.location) {
        console.log(`   위치: ${warning.location.url}:${warning.location.lineNumber}`);
      }
      console.log(`   시간: ${warning.timestamp}`);
    });
    console.log('-'.repeat(80));
    console.log();
  }

  if (networkErrors.length > 0) {
    console.log('🌐 네트워크 에러 목록:');
    console.log('-'.repeat(80));
    networkErrors.forEach((error, index) => {
      console.log(`\n[${index + 1}] ${error.type.toUpperCase()}`);
      console.log(`   URL: ${error.url}`);
      if (error.status) {
        console.log(`   상태: ${error.status} ${error.statusText || ''}`);
      }
      if (error.failure) {
        console.log(`   실패 원인: ${error.failure}`);
      }
      console.log(`   시간: ${error.timestamp}`);
    });
    console.log('-'.repeat(80));
    console.log();
  }

  // JSON 파일로 저장
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
  const outputFile = join(__dirname, 'logs', `console-errors-${timestamp}.json`);
  
  // logs 디렉토리 생성
  const logsDir = join(__dirname, 'logs');
  try {
    await import('fs').then(fs => {
      if (!fs.existsSync(logsDir)) {
        fs.mkdirSync(logsDir, { recursive: true });
      }
      writeFileSync(outputFile, JSON.stringify(result, null, 2), 'utf-8');
      console.log(`✅ 결과가 저장되었습니다: ${outputFile}`);
    });
  } catch (saveError) {
    console.error('❌ 파일 저장 실패:', saveError.message);
  }

  // 브라우저 닫기 전에 잠시 대기 (결과 확인용)
  console.log('\n브라우저를 3초 후에 닫습니다...');
  await page.waitForTimeout(3000);

} catch (error) {
  console.error('❌ 오류 발생:', error.message);
  console.error('스택:', error.stack);
  process.exit(1);
} finally {
  if (browser) {
    await browser.close();
  }
}


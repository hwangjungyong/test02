#!/usr/bin/env node
/**
 * 로그인 테스트 스크립트
 * 1. 서버가 실행 중인지 확인
 * 2. 테스트 사용자 생성 (없는 경우)
 * 3. 로그인 시도
 */

import { init, userDB } from './database.js';
import bcrypt from 'bcryptjs';

const TEST_EMAIL = `test${Date.now()}@example.com`;
const TEST_PASSWORD = 'test123';

async function testLogin() {
  try {
    // 데이터베이스 초기화
    console.log('[1/4] 데이터베이스 초기화 중...');
    await init();
    console.log('✓ 데이터베이스 초기화 완료\n');

    // 회원가입 API로 사용자 생성/확인
    console.log('[2/4] 사용자 확인/생성 중...');
    try {
      const signupResponse = await fetch('http://localhost:3001/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          email: TEST_EMAIL,
          password: TEST_PASSWORD,
          name: '테스트 사용자'
        })
      });
      
      const signupData = await signupResponse.json();
      if (signupData.success) {
        console.log(`✓ 사용자 생성/확인 완료: ${signupData.user.email}\n`);
      } else if (signupData.error && signupData.error.includes('이미 사용 중')) {
        console.log(`✓ 기존 사용자 확인: ${TEST_EMAIL}\n`);
      } else {
        console.log(`⚠ 회원가입 응답: ${signupData.error}\n`);
      }
    } catch (error) {
      console.log(`⚠ 회원가입 확인 중 오류 (무시하고 진행): ${error.message}\n`);
    }

    // 로그인 API 테스트
    console.log('[3/4] 로그인 API 테스트 중...');
    const loginResponse = await fetch('http://localhost:3001/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email: TEST_EMAIL,
        password: TEST_PASSWORD
      })
    });

    const loginData = await loginResponse.json();
    
    if (loginData.success) {
      console.log('✓ 로그인 성공!');
      console.log(`  - 사용자: ${loginData.user.email}`);
      console.log(`  - 이름: ${loginData.user.name || '(없음)'}`);
      console.log(`  - 토큰: ${loginData.token.substring(0, 20)}...`);
      console.log('\n[4/4] 로그인 테스트 완료! ✅\n');
    } else {
      console.log('✗ 로그인 실패:', loginData.error);
      console.log('\n[4/4] 로그인 테스트 실패 ❌\n');
      process.exit(1);
    }

  } catch (error) {
    if (error.code === 'ECONNREFUSED') {
      console.error('✗ 서버에 연결할 수 없습니다.');
      console.error('  서버가 실행 중인지 확인하세요: npm run api-server');
    } else {
      console.error('✗ 오류 발생:', error.message);
      console.error(error);
    }
    process.exit(1);
  }
}

testLogin();


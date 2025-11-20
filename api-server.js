#!/usr/bin/env node

/**
 * 백엔드 API 서버 - News API 및 Last.fm API 프록시
 * 
 * 역할:
 * - Vue 앱에서 외부 API를 호출할 때 CORS 문제를 해결하기 위한 프록시 서버
 * - 프록시 환경에서 외부 API를 호출하기 위한 중간 서버
 * - News API와 Last.fm API를 프록시를 통해 호출
 * 
 * 실행 방법:
 *   npm run api-server
 * 
 * 포트: http://localhost:3001
 * 
 * API 엔드포인트:
 *   GET /api/news?q=키워드 - News API 검색
 *   GET /api/news/economy?q=키워드 - 경제 뉴스 검색
 *   GET /api/music/recommend?songTitle=제목&artist=아티스트 - 음악 추천
 *   GET /api/music/radio/current?station=방송국&limit=개수 - 현재 재생 중인 노래
 *   GET /api/music/radio/recent?station=방송국&limit=개수 - 최근 재생된 노래
 *   GET /api/books/search?q=키워드&maxResults=개수 - 도서 검색
 *   GET /api/books/recommend?keyword=키워드&category=카테고리 - 도서 추천
 *   GET /api-docs - Swagger UI (API 문서화 및 테스트)
 *   GET /swagger.json - Swagger OpenAPI 스펙 JSON
 */

import http from 'http';
import https from 'https';
import { URL } from 'url';
import { HttpsProxyAgent } from 'https-proxy-agent';
import { readFileSync, readdirSync, statSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';
import dotenv from 'dotenv';
import jwt from 'jsonwebtoken';
import bcrypt from 'bcryptjs';
import { userDB, newsDB, radioSongsDB, booksDB, apiKeysDB, apiKeyUsageDB, init, getSchema, getTables } from './database.js';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

// 환경 변수 로드
dotenv.config();

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

// ============================================
// API 설정
// ============================================

// News API 설정
// - API 키: newsapi.org에서 발급받은 키
// - Base URL: News API의 기본 URL
const NEWS_API_KEY = process.env.NEWS_API_KEY || '6944bc431cbf4988857f3cb35b4decc6';
const NEWS_API_BASE_URL = 'https://newsapi.org/v2';

// Last.fm API 설정
// - API 키: last.fm에서 발급받은 키
// - Shared Secret: API 인증에 사용되는 시크릿 키
// - Base URL: Last.fm API의 기본 URL
const LASTFM_API_KEY = process.env.LASTFM_API_KEY || '8d8e2e5d0c3b1b95499e94331b8a211e';
const LASTFM_API_BASE_URL = 'https://ws.audioscrobbler.com/2.0';

// 서버 포트 설정
const PORT = process.env.API_SERVER_PORT || 3001;

// JWT 설정
const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key-change-this-in-production';
const JWT_EXPIRES_IN = process.env.JWT_EXPIRES_IN || '7d';

// ============================================
// 헬퍼 함수
// ============================================

/**
 * 도서 관련성 점수 계산
 * @param {Object} book - 도서 객체
 * @param {Array} keywords - 키워드 배열
 * @returns {number} 관련성 점수
 */
function calculateRelevanceScore(book, keywords) {
  let score = 0;
  const searchText = `${book.title} ${book.description} ${(book.categories || []).join(' ')}`.toLowerCase();
  
  for (const keyword of keywords) {
    const keywordLower = keyword.toLowerCase();
    if (searchText.includes(keywordLower)) {
      // 제목에 있으면 높은 점수
      if (book.title.toLowerCase().includes(keywordLower)) {
        score += 3;
      }
      // 카테고리에 있으면 중간 점수
      if (book.categories && book.categories.some(cat => cat.toLowerCase().includes(keywordLower))) {
        score += 2;
      }
      // 설명에 있으면 낮은 점수
      if (book.description && book.description.toLowerCase().includes(keywordLower)) {
        score += 1;
      }
    }
  }
  
  return score;
}

// ============================================
// 프록시 설정
// ============================================

// 프록시 설정 (npmrc에서 가져옴)
// - 프록시 환경에서 외부 API를 호출하기 위해 필요
// - rejectUnauthorized: false - 프록시 환경에서 SSL 인증서 검증 우회
const PROXY_URL = 'http://70.10.15.10:8080';
const proxyAgent = new HttpsProxyAgent(PROXY_URL, {
  rejectUnauthorized: false // 프록시 환경에서 SSL 인증서 검증 우회
});

// ============================================
// 헬퍼 함수
// ============================================

/**
 * 프록시를 사용하여 API 호출하는 헬퍼 함수 (재시도 로직 포함)
 * 
 * @param {string} url - 호출할 API URL
 * @param {object} options - 추가 옵션 (method, headers 등)
 * @param {number} retries - 재시도 횟수 (기본값: 3)
 * @returns {Promise} - API 응답을 Promise로 반환
 * 
 * 기능:
 * - 프록시를 통해 HTTPS 요청 생성
 * - 30초 타임아웃 설정
 * - JSON 응답 파싱
 * - 503, 429 등 일시적 오류 시 자동 재시도 (최대 3회)
 * - 에러 처리
 */
function makeRequest(url, options = {}, retries = 3) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    
    const req = https.request({
      hostname: urlObj.hostname,
      path: urlObj.pathname + urlObj.search,
      method: options.method || 'GET',
      agent: proxyAgent,
      headers: {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        ...options.headers
      },
      timeout: 30000, // 30초 타임아웃
      rejectUnauthorized: false // 프록시 환경에서 SSL 인증서 검증 우회
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        try {
          const jsonData = JSON.parse(data);
          
          // 일시적 오류 (503, 429, 500)인 경우 재시도
          if ((res.statusCode === 503 || res.statusCode === 429 || res.statusCode === 500) && retries > 0) {
            const delay = (4 - retries) * 1000; // 1초, 2초, 3초 대기
            console.log(`[API 서버] 일시적 오류 ${res.statusCode} 발생. ${delay}ms 후 재시도 (남은 횟수: ${retries - 1})`);
            setTimeout(() => {
              makeRequest(url, options, retries - 1).then(resolve).catch(reject);
            }, delay);
            return;
          }
          
          resolve({
            ok: res.statusCode >= 200 && res.statusCode < 300,
            status: res.statusCode,
            statusText: res.statusMessage,
            json: async () => jsonData,
            headers: res.headers
          });
        } catch (error) {
          reject(new Error(`JSON 파싱 오류: ${error.message}`));
        }
      });
    });
    
    req.on('error', (error) => {
      // 네트워크 오류인 경우 재시도
      if (retries > 0 && (error.code === 'ECONNRESET' || error.code === 'ETIMEDOUT' || error.code === 'ENOTFOUND')) {
        const delay = (4 - retries) * 1000;
        console.log(`[API 서버] 네트워크 오류 발생: ${error.code}. ${delay}ms 후 재시도 (남은 횟수: ${retries - 1})`);
        setTimeout(() => {
          makeRequest(url, options, retries - 1).then(resolve).catch(reject);
        }, delay);
        return;
      }
      console.error(`[API 서버] 요청 오류:`, error);
      reject(error);
    });
    
    req.on('timeout', () => {
      // 타임아웃인 경우 재시도
      if (retries > 0) {
        req.destroy();
        const delay = (4 - retries) * 1000;
        console.log(`[API 서버] 타임아웃 발생. ${delay}ms 후 재시도 (남은 횟수: ${retries - 1})`);
        setTimeout(() => {
          makeRequest(url, options, retries - 1).then(resolve).catch(reject);
        }, delay);
        return;
      }
      req.destroy();
      reject(new Error('API 연결 타임아웃 (30초 초과)'));
    });
    
    if (options.body) {
      req.write(options.body);
    }
    
    req.end();
  });
}

// ============================================
// 인증 헬퍼 함수
// ============================================

/**
 * 요청 본문 파싱
 */
function parseBody(req) {
  return new Promise((resolve, reject) => {
    let body = '';
    req.on('data', chunk => { body += chunk.toString(); });
    req.on('end', () => {
      try {
        resolve(body ? JSON.parse(body) : {});
      } catch (error) {
        reject(error);
      }
    });
    req.on('error', reject);
  });
}

/**
 * JWT 토큰 검증 미들웨어
 */
function authenticateToken(req) {
  const authHeader = req.headers['authorization'];
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN

  if (!token) {
    return null;
  }

  try {
    return jwt.verify(token, JWT_SECRET);
  } catch (error) {
    return null;
  }
}

/**
 * API 키 인증 미들웨어
 */
function authenticateApiKey(req) {
  // 방법 1: X-API-Key 헤더
  const apiKeyFromHeader = req.headers['x-api-key'];
  
  // 방법 2: Authorization 헤더 (ApiKey 스키마)
  const authHeader = req.headers['authorization'];
  let apiKeyFromAuth = null;
  if (authHeader && authHeader.startsWith('ApiKey ')) {
    apiKeyFromAuth = authHeader.split(' ')[1];
  }
  
  // 방법 3: 쿼리 파라미터 (보안상 권장하지 않지만 호환성을 위해)
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const apiKeyFromQuery = url.searchParams.get('api_key');
  
  const apiKey = apiKeyFromHeader || apiKeyFromAuth || apiKeyFromQuery;
  
  if (!apiKey) {
    return null;
  }

  const keyInfo = apiKeysDB.findByApiKey(apiKey);
  if (!keyInfo) {
    return null;
  }

  // 사용 시간 업데이트
  apiKeysDB.updateLastUsed(keyInfo.id);

  // 사용 이력 기록
  const clientIp = req.headers['x-forwarded-for'] || req.socket.remoteAddress || 'unknown';
  const userAgent = req.headers['user-agent'] || 'unknown';
  apiKeyUsageDB.create({
    apiKeyId: keyInfo.id,
    endpoint: req.url.split('?')[0],
    method: req.method,
    ipAddress: clientIp,
    userAgent: userAgent,
    statusCode: null // 응답 후 업데이트됨
  });

  return keyInfo;
}

/**
 * API 키 또는 JWT 토큰 인증 (둘 중 하나면 통과)
 * @returns {Object|null} 인증 정보 또는 null
 * @returns {Object.error} API 키가 제공되었지만 유효하지 않을 때 에러 정보
 */
function authenticateApiKeyOrToken(req) {
  // API 키가 제공되었는지 확인
  const apiKeyFromHeader = req.headers['x-api-key'];
  const authHeader = req.headers['authorization'];
  const url = new URL(req.url, `http://localhost:${PORT}`);
  const apiKeyFromQuery = url.searchParams.get('api_key');
  
  const hasApiKeyProvided = apiKeyFromHeader || 
    (authHeader && authHeader.startsWith('ApiKey ')) || 
    apiKeyFromQuery;
  
  // API 키 인증 시도
  const apiKeyInfo = authenticateApiKey(req);
  if (apiKeyInfo) {
    return { type: 'apiKey', userId: apiKeyInfo.userId, apiKeyId: apiKeyInfo.id };
  }
  
  // API 키가 제공되었지만 유효하지 않은 경우
  if (hasApiKeyProvided) {
    return { 
      error: true, 
      message: '유효하지 않은 API 키입니다. API 키를 확인해주세요.' 
    };
  }

  // JWT 토큰 인증 시도
  const tokenInfo = authenticateToken(req);
  if (tokenInfo) {
    return { type: 'token', userId: tokenInfo.userId };
  }

  return null; // 인증 정보 없음 (선택사항인 경우 통과)
}

/**
 * JSON 응답 헬퍼
 */
function sendJSON(res, statusCode, data) {
  res.writeHead(statusCode, { 'Content-Type': 'application/json' });
  res.end(JSON.stringify(data));
}

// ============================================
// HTTP 서버 생성
// ============================================

/**
 * HTTP 서버 생성 및 요청 처리
 * 
 * 주요 기능:
 * - CORS 헤더 설정 (브라우저에서 접근 가능하도록)
 * - OPTIONS 요청 처리 (CORS preflight)
 * - 인증 API 처리 (회원가입, 로그인)
 * - News API 프록시 처리
 * - Last.fm API 프록시 처리 (음악 추천, 라디오 방송 정보)
 */
const server = http.createServer(async (req, res) => {
  // CORS 헤더 설정
  // - Access-Control-Allow-Origin: 모든 도메인에서 접근 허용
  // - Access-Control-Allow-Methods: 허용할 HTTP 메서드
  // - Access-Control-Allow-Headers: 허용할 헤더
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  // OPTIONS 요청 처리 (CORS preflight)
  // - 브라우저가 실제 요청 전에 보내는 사전 요청
  // - 200 OK 응답으로 허용 여부를 알림
  if (req.method === 'OPTIONS') {
    res.writeHead(200);
    res.end();
    return;
  }

  // ============================================
  // 인증 API 처리
  // ============================================

  // 회원가입: POST /api/auth/signup
  if (req.url === '/api/auth/signup' && req.method === 'POST') {
    try {
      const body = await parseBody(req);
      const { email, password, name } = body;

      // 입력값 검증
      if (!email || !password) {
        return sendJSON(res, 400, { 
          success: false, 
          error: '이메일과 비밀번호는 필수입니다.' 
        });
      }

      // 이메일 형식 검증 (간단한 검증)
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        return sendJSON(res, 400, { 
          success: false, 
          error: '유효한 이메일 주소를 입력해주세요.' 
        });
      }

      // 비밀번호 길이 검증
      if (password.length < 6) {
        return sendJSON(res, 400, { 
          success: false, 
          error: '비밀번호는 최소 6자 이상이어야 합니다.' 
        });
      }

      // 중복 이메일 확인
      const existingUser = userDB.findByEmail(email);
      if (existingUser) {
        return sendJSON(res, 409, { 
          success: false, 
          error: '이미 사용 중인 이메일입니다.' 
        });
      }

      // 비밀번호 해싱
      const passwordHash = await bcrypt.hash(password, 10);

      // 사용자 생성
      const newUser = userDB.create({
        email,
        password: passwordHash,
        name: name || email.split('@')[0]
      });

      if (!newUser) {
        return sendJSON(res, 500, { 
          success: false, 
          error: '회원가입 중 오류가 발생했습니다.' 
        });
      }

      // JWT 토큰 생성
      const token = jwt.sign(
        { userId: newUser.id, email: newUser.email },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRES_IN }
      );

      // 비밀번호 해시 제외하고 응답
      const { password: _, ...userResponse } = newUser;

      return sendJSON(res, 201, {
        success: true,
        message: '회원가입이 완료되었습니다.',
        user: userResponse,
        token
      });

    } catch (error) {
      console.error('[API 서버] 회원가입 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 로그인: POST /api/auth/login
  else if (req.url === '/api/auth/login' && req.method === 'POST') {
    try {
      const body = await parseBody(req);
      const { email, password } = body;

      // 입력값 검증
      if (!email || !password) {
        return sendJSON(res, 400, { 
          success: false, 
          error: '이메일과 비밀번호를 입력해주세요.' 
        });
      }

      // 사용자 조회
      const user = userDB.findByEmail(email);
      if (!user) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '이메일 또는 비밀번호가 올바르지 않습니다.' 
        });
      }

      // 비밀번호 확인
      const isValidPassword = await bcrypt.compare(password, user.password);
      if (!isValidPassword) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '이메일 또는 비밀번호가 올바르지 않습니다.' 
        });
      }

      // JWT 토큰 생성
      const token = jwt.sign(
        { userId: user.id, email: user.email },
        JWT_SECRET,
        { expiresIn: JWT_EXPIRES_IN }
      );

      // 비밀번호 해시 제외하고 응답
      const { password: _, ...userResponse } = user;

      return sendJSON(res, 200, {
        success: true,
        message: '로그인 성공',
        user: userResponse,
        token
      });

    } catch (error) {
      console.error('[API 서버] 로그인 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 사용자 정보 조회: GET /api/auth/me
  else if (req.url === '/api/auth/me' && req.method === 'GET') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const user = userDB.findById(decoded.userId);
      if (!user) {
        return sendJSON(res, 404, { 
          success: false, 
          error: '사용자를 찾을 수 없습니다.' 
        });
      }

      // 비밀번호 해시 제외하고 응답
      const { password: _, ...userResponse } = user;

      return sendJSON(res, 200, {
        success: true,
        user: userResponse
      });

    } catch (error) {
      console.error('[API 서버] 사용자 정보 조회 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // ============================================
  // 사용자 관리 API
  // ============================================

  // 사용자 프로필 조회: GET /api/user/profile
  else if (req.url === '/api/user/profile' && req.method === 'GET') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const user = userDB.findById(decoded.userId);
      if (!user) {
        return sendJSON(res, 404, { 
          success: false, 
          error: '사용자를 찾을 수 없습니다.' 
        });
      }

      // 비밀번호 해시 제외하고 응답
      const { password: _, ...userResponse } = user;

      return sendJSON(res, 200, {
        success: true,
        user: userResponse
      });

    } catch (error) {
      console.error('[API 서버] 프로필 조회 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 사용자 프로필 수정: PUT /api/user/profile
  else if (req.url === '/api/user/profile' && req.method === 'PUT') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const body = await parseBody(req);
      const { name, email } = body;

      // 이메일 변경 시 중복 확인
      if (email) {
        const existingUser = userDB.findByEmail(email);
        if (existingUser && existingUser.id !== decoded.userId) {
          return sendJSON(res, 409, { 
            success: false, 
            error: '이미 사용 중인 이메일입니다.' 
          });
        }
      }

      // 프로필 업데이트
      const updatedUser = userDB.update(decoded.userId, { name, email });
      if (!updatedUser) {
        return sendJSON(res, 404, { 
          success: false, 
          error: '사용자를 찾을 수 없습니다.' 
        });
      }

      // 비밀번호 해시 제외하고 응답
      const { password: _, ...userResponse } = updatedUser;

      return sendJSON(res, 200, {
        success: true,
        message: '프로필이 수정되었습니다.',
        user: userResponse
      });

    } catch (error) {
      console.error('[API 서버] 프로필 수정 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 계정 삭제: DELETE /api/user/account
  else if (req.url === '/api/user/account' && req.method === 'DELETE') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      // 사용자 데이터 삭제
      const userId = decoded.userId;
      newsDB.deleteByUserId(userId);
      radioSongsDB.deleteByUserId(userId);
      booksDB.deleteByUserId(userId);

      // 사용자 계정 삭제
      const deleted = userDB.delete(userId);
      if (!deleted) {
        return sendJSON(res, 404, { 
          success: false, 
          error: '사용자를 찾을 수 없습니다.' 
        });
      }

      return sendJSON(res, 200, {
        success: true,
        message: '계정이 삭제되었습니다.'
      });

    } catch (error) {
      console.error('[API 서버] 계정 삭제 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // ============================================
  // API 키 관리 API
  // ============================================

  // API 키 생성: POST /api/api-keys
  else if (req.url === '/api/api-keys' && req.method === 'POST') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const body = await parseBody(req);
      const { name, description, expiresInDays } = body;

      // API 키 생성 (랜덤 문자열)
      const crypto = await import('crypto');
      const apiKey = `sk_${crypto.randomBytes(32).toString('hex')}`;

      // 만료일 계산
      let expiresAt = null;
      if (expiresInDays) {
        const expiresDate = new Date();
        expiresDate.setDate(expiresDate.getDate() + parseInt(expiresInDays));
        expiresAt = expiresDate.toISOString();
      }

      const keyInfo = apiKeysDB.create({
        userId: decoded.userId,
        apiKey,
        name: name || 'My API Key',
        description: description || null,
        expiresAt
      });

      return sendJSON(res, 201, {
        success: true,
        message: 'API 키가 생성되었습니다.',
        apiKey: {
          id: keyInfo.id,
          apiKey: keyInfo.apiKey, // 처음 생성 시에만 전체 키 반환
          name: keyInfo.name,
          description: keyInfo.description,
          createdAt: keyInfo.createdAt,
          expiresAt: keyInfo.expiresAt
        },
        warning: '이 API 키는 이번에만 표시됩니다. 안전한 곳에 저장하세요.'
      });

    } catch (error) {
      console.error('[API 서버] API 키 생성 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // API 키 목록 조회: GET /api/api-keys
  else if (req.url === '/api/api-keys' && req.method === 'GET') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const keys = apiKeysDB.findByUserId(decoded.userId);
      
      // 보안: 전체 API 키는 반환하지 않고 마스킹 처리
      const maskedKeys = keys.map(key => ({
        id: key.id,
        apiKey: `${key.apiKey.substring(0, 10)}...${key.apiKey.substring(key.apiKey.length - 4)}`, // 마스킹
        name: key.name,
        description: key.description,
        isActive: key.isActive,
        lastUsedAt: key.lastUsedAt,
        createdAt: key.createdAt,
        expiresAt: key.expiresAt
      }));

      return sendJSON(res, 200, {
        success: true,
        apiKeys: maskedKeys
      });

    } catch (error) {
      console.error('[API 서버] API 키 목록 조회 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // API 키 삭제: DELETE /api/api-keys/:id
  else if (req.url && req.url.startsWith('/api/api-keys/') && req.method === 'DELETE') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const keyId = parseInt(req.url.split('/').pop());
      const deleted = apiKeysDB.delete(keyId, decoded.userId);

      if (deleted) {
        return sendJSON(res, 200, {
          success: true,
          message: 'API 키가 삭제되었습니다.'
        });
      } else {
        return sendJSON(res, 404, {
          success: false,
          error: 'API 키를 찾을 수 없습니다.'
        });
      }

    } catch (error) {
      console.error('[API 서버] API 키 삭제 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // API 키 활성화/비활성화: PUT /api/api-keys/:id/toggle
  else if (req.url && req.url.match(/\/api\/api-keys\/\d+\/toggle$/) && req.method === 'PUT') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const keyId = parseInt(req.url.split('/')[3]);
      const body = await parseBody(req);
      const { isActive } = body;

      const updated = apiKeysDB.toggleActive(keyId, decoded.userId, isActive);

      if (updated) {
        return sendJSON(res, 200, {
          success: true,
          message: `API 키가 ${isActive ? '활성화' : '비활성화'}되었습니다.`
        });
      } else {
        return sendJSON(res, 404, {
          success: false,
          error: 'API 키를 찾을 수 없습니다.'
        });
      }

    } catch (error) {
      console.error('[API 서버] API 키 토글 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 사용자 데이터 조회: GET /api/user/data
  else if (req.url === '/api/user/data' && req.method === 'GET') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const userId = decoded.userId;
      const news = newsDB.findByUserId(userId);
      const radioSongs = radioSongsDB.findByUserId(userId);
      const books = booksDB.findByUserId(userId);

      return sendJSON(res, 200, {
        success: true,
        data: {
          news: news || [],
          radioSongs: radioSongs || [],
          books: books || [],
          summary: {
            newsCount: news?.length || 0,
            radioSongsCount: radioSongs?.length || 0,
            booksCount: books?.length || 0
          }
        }
      });

    } catch (error) {
      console.error('[API 서버] 사용자 데이터 조회 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 뉴스 저장: POST /api/user/news
  else if (req.url === '/api/user/news' && req.method === 'POST') {
    try {
      const decoded = authenticateToken(req);
      if (!decoded) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다.' 
        });
      }

      const body = await parseBody(req);
      const userId = decoded.userId;
      const savedNews = [];

      // 여러 뉴스를 한 번에 저장할 수 있도록 배열 처리
      const newsArray = Array.isArray(body) ? body : [body];

      for (const newsItem of newsArray) {
        // 중복 확인 (제목과 출처로)
        const existingNews = newsDB.findByUserId(userId).find(
          n => n.title === newsItem.title && n.source === newsItem.source
        );

        if (!existingNews) {
          const saved = newsDB.create({
            userId,
            title: newsItem.title,
            summary: newsItem.summary,
            date: newsItem.date,
            source: newsItem.source,
            category: newsItem.category,
            keyword: newsItem.keyword,
            url: newsItem.url,
            publishedDate: newsItem.publishedDate,
            importanceStars: newsItem.importanceStars,
            importanceValue: newsItem.importanceValue
          });
          if (saved) savedNews.push(saved);
        }
      }

      return sendJSON(res, 200, {
        success: true,
        message: `${savedNews.length}개의 뉴스가 저장되었습니다.`,
        saved: savedNews.length,
        total: newsArray.length
      });

    } catch (error) {
      console.error('[API 서버] 뉴스 저장 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 라디오 노래 저장: POST /api/user/radio-songs
  else if (req.url === '/api/user/radio-songs' && req.method === 'POST') {
    try {
      const auth = authenticateApiKeyOrToken(req);
      if (!auth) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다. API 키 또는 JWT 토큰을 제공해주세요.' 
        });
      }

      const body = await parseBody(req);
      const userId = auth.userId;
      const savedSongs = [];

      // 여러 노래를 한 번에 저장할 수 있도록 배열 처리
      const songsArray = Array.isArray(body) ? body : [body];

      for (const songItem of songsArray) {
        // 중복 확인 (제목과 아티스트로)
        const existingSong = radioSongsDB.findByUserId(userId).find(
          s => s.title === songItem.title && s.artist === songItem.artist
        );

        if (!existingSong) {
          const saved = radioSongsDB.create({
            userId,
            title: songItem.title,
            artist: songItem.artist,
            genre: songItem.genre,
            stations: songItem.station ? [songItem.station] : null,
            count: songItem.count || 1
          });
          if (saved) savedSongs.push(saved);
        }
      }

      return sendJSON(res, 200, {
        success: true,
        message: `${savedSongs.length}개의 라디오 노래가 저장되었습니다.`,
        saved: savedSongs.length,
        total: songsArray.length
      });

    } catch (error) {
      console.error('[API 서버] 라디오 노래 저장 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // 도서 저장: POST /api/user/books
  else if (req.url === '/api/user/books' && req.method === 'POST') {
    try {
      const auth = authenticateApiKeyOrToken(req);
      if (!auth) {
        return sendJSON(res, 401, { 
          success: false, 
          error: '인증이 필요합니다. API 키 또는 JWT 토큰을 제공해주세요.' 
        });
      }

      const body = await parseBody(req);
      const userId = auth.userId;
      const savedBooks = [];

      // 여러 도서를 한 번에 저장할 수 있도록 배열 처리
      const booksArray = Array.isArray(body) ? body : [body];

      for (const bookItem of booksArray) {
        // 중복 확인 (제목과 저자로)
        const bookAuthors = Array.isArray(bookItem.authors) ? bookItem.authors.join(', ') : bookItem.authors
        const existingBook = booksDB.findByUserId(userId).find(b => {
          const existingAuthors = Array.isArray(b.authors) ? b.authors.join(', ') : b.authors
          return b.title === bookItem.title && existingAuthors === bookAuthors
        });

        if (!existingBook) {
          const saved = booksDB.create({
            userId,
            title: bookItem.title,
            authors: Array.isArray(bookItem.authors) ? bookItem.authors : (bookItem.authors ? [bookItem.authors] : []),
            description: bookItem.description,
            imageUrl: bookItem.thumbnail || bookItem.imageUrl,
            previewLink: bookItem.previewLink,
            publishedDate: bookItem.publishedDate,
            categories: Array.isArray(bookItem.categories) ? bookItem.categories : (bookItem.categories ? [bookItem.categories] : [])
          });
          if (saved) savedBooks.push(saved);
        }
      }

      return sendJSON(res, 200, {
        success: true,
        message: `${savedBooks.length}개의 도서가 저장되었습니다.`,
        saved: savedBooks.length,
        total: booksArray.length
      });

    } catch (error) {
      console.error('[API 서버] 도서 저장 오류:', error);
      return sendJSON(res, 500, { 
        success: false, 
        error: '서버 오류가 발생했습니다.' 
      });
    }
  }

  // ============================================
  // Books API 처리 (Google Books API)
  // ============================================
  // 엔드포인트: GET /api/books/recommend?query=사용자입력&category=카테고리
  // 기능: 사용자 입력을 AI가 분석하여 관련 도서 추천
  // 주의: /api/news보다 먼저 체크해야 함 (startsWith 매칭 순서)
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/books/recommend')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const userQuery = url.searchParams.get('query') || url.searchParams.get('keyword'); // 하위 호환성
      const category = url.searchParams.get('category');

      console.log(`[API 서버] ===== 도서 추천 요청 =====`);
      console.log(`[API 서버] 요청 URL: ${req.url}`);
      console.log(`[API 서버] 파싱된 query 파라미터: "${userQuery}"`);
      console.log(`[API 서버] 파싱된 category 파라미터: "${category}"`);

      if (!userQuery || userQuery.trim() === '') {
        console.error('[API 서버] 사용자 입력이 없습니다.');
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '사용자 입력이 필요합니다. query 파라미터를 확인해주세요.' }));
        return;
      }

      const trimmedQuery = userQuery.trim();
      console.log(`[API 서버] AI 도서 추천 요청: "${trimmedQuery}"`);

      // AI 키워드 추출 로직 (사용자 입력 분석)
      // 1. 학습/배우기 관련 키워드 추출
      const learningKeywords = ['배우', '학습', '공부', '이해', '알고 싶', '시작', '입문', '기초', '초보'];
      const isLearning = learningKeywords.some(kw => trimmedQuery.includes(kw));
      
      // 2. 주제 키워드 추출
      const topicKeywords = {
        '머신러닝': ['머신러닝', '기계학습', 'machine learning', 'ML'],
        '딥러닝': ['딥러닝', 'deep learning', '신경망', 'neural network'],
        '인공지능': ['인공지능', 'AI', 'artificial intelligence', '인지능'],
        '파이썬': ['파이썬', 'python', '파이선'],
        '데이터': ['데이터', 'data', '데이터사이언스', 'data science'],
        '소설': ['소설', 'fiction', 'novel', '이야기', '스토리'],
        '경제': ['경제', '경영', 'business', '금융', 'finance', '경영'],
        '과학': ['과학', 'science', '물리', '화학', '생물'],
        '프로그래밍': ['프로그래밍', 'programming', '코딩', 'coding', '개발'],
        '알고리즘': ['알고리즘', 'algorithm', '자료구조'],
        '판타지': ['판타지', 'fantasy', '판타지소설'],
        '무협': ['무협', '무협소설', '무협지'],
        '로맨스': ['로맨스', 'romance', '로맨스소설'],
        '추리': ['추리', '미스터리', 'mystery', '추리소설'],
        '역사': ['역사', '역사소설', 'historical', '사극'],
      };

      // 3. 특정 작품/도서 이름 감지 (짧은 단일 단어이거나 특정 패턴)
      // 작품 이름으로 보이는 경우: 2-4글자 단일 단어, 또는 특정 작품 이름 패턴
      const isSpecificBookTitle = (query) => {
        const words = query.trim().split(/\s+/);
        // 단일 단어이고 2-4글자인 경우 작품 이름일 가능성 높음
        if (words.length === 1 && words[0].length >= 2 && words[0].length <= 4) {
          // 학습/기술 관련 키워드가 아닌 경우
          const technicalTerms = ['AI', 'ML', '파이썬', '자바', 'C++', 'SQL', 'HTML', 'CSS', 'JS'];
          if (!technicalTerms.some(term => query.toLowerCase().includes(term.toLowerCase()))) {
            return true;
          }
        }
        return false;
      };

      const isBookTitle = isSpecificBookTitle(trimmedQuery);

      // 사용자 입력에서 주제 키워드 찾기
      let extractedKeywords = [];
      for (const [topic, keywords] of Object.entries(topicKeywords)) {
        if (keywords.some(kw => trimmedQuery.toLowerCase().includes(kw.toLowerCase()))) {
          extractedKeywords.push(topic);
        }
      }

      // 4. 검색 쿼리 구성
      let searchQuery = '';
      
      // 특정 작품 이름이 감지된 경우: 작품 이름을 제외하고 관련 장르/주제로 검색
      if (isBookTitle && extractedKeywords.length === 0) {
        // 작품 이름을 입력한 경우, 유사한 장르의 다른 작품을 추천
        // 작품 이름 자체는 검색 쿼리에서 완전히 제외
        searchQuery = '소설 판타지 무협'; // 기본적으로 소설 장르로 검색
        console.log(`[API 서버] 특정 작품 이름 감지: "${trimmedQuery}" → 장르 기반 검색으로 변경 (작품 이름 제외)`);
      } else if (isBookTitle && extractedKeywords.length > 0) {
        // 작품 이름이지만 주제 키워드도 있는 경우: 주제 키워드만 사용
        searchQuery = extractedKeywords.join(' ');
        console.log(`[API 서버] 작품 이름 + 주제 키워드: "${trimmedQuery}" → 주제 키워드만 사용`);
      } else {
        // 일반적인 경우: 원본 입력 포함
        searchQuery = trimmedQuery;
        
        // 추출된 키워드가 있으면 추가
        if (extractedKeywords.length > 0) {
          searchQuery += ' ' + extractedKeywords.join(' ');
        }
      }

      // 학습 관련 키워드가 있으면 "입문", "기초" 추가
      if (isLearning && !extractedKeywords.includes('입문')) {
        searchQuery += ' 입문 기초';
      }

      // 특정 작품 이름이 감지된 경우: 검색 쿼리에서 작품 이름 제외 (부정 검색)
      if (isBookTitle) {
        // Google Books API의 부정 검색 (-keyword)을 사용하여 작품 이름 제외
        searchQuery += ` -${trimmedQuery}`;
        console.log(`[API 서버] 검색 쿼리 (작품 이름 제외): "${searchQuery}"`);
      }

      // 카테고리 필터링
      let apiUrl = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(searchQuery)}&maxResults=30&langRestrict=ko`;
      
      if (category) {
        apiUrl += `+subject:${encodeURIComponent(category)}`;
      }
      
      console.log(`[API 서버] AI 분석 결과 - 추출된 키워드: ${extractedKeywords.join(', ') || '없음'}`);
      console.log(`[API 서버] Google Books API (AI 추천) 호출: ${apiUrl}`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`[API 서버] Google Books API 오류: ${response.status}`, errorData);
        
        // 사용자 친화적인 에러 메시지
        let errorMessage = errorData.error?.message || response.statusText;
        if (response.status === 503) {
          errorMessage = 'Google Books API가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.';
        } else if (response.status === 429) {
          errorMessage = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
        } else if (response.status === 500) {
          errorMessage = 'Google Books API 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
        
        res.writeHead(response.status, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: errorMessage, status: response.status }));
        return;
      }

      const data = await response.json();
      console.log(`[API 서버] Google Books API (AI 추천) 응답: ${data.items?.length || 0}개 도서`);

      // 응답 형식 변환
      let books = (data.items || []).map(item => {
        const volumeInfo = item.volumeInfo || {};
        return {
          id: item.id,
          title: volumeInfo.title || '제목 없음',
          authors: volumeInfo.authors || ['저자 정보 없음'],
          publisher: volumeInfo.publisher || '출판사 정보 없음',
          publishedDate: volumeInfo.publishedDate || '출판일 정보 없음',
          description: volumeInfo.description || '설명 없음',
          categories: volumeInfo.categories || [],
          pageCount: volumeInfo.pageCount || 0,
          language: volumeInfo.language || 'ko',
          previewLink: volumeInfo.previewLink || '',
          infoLink: volumeInfo.infoLink || '',
          thumbnail: volumeInfo.imageLinks?.thumbnail || '',
          averageRating: volumeInfo.averageRating || 0,
          ratingsCount: volumeInfo.ratingsCount || 0
        };
      });

      // AI 분석 기반 정렬
      // 특정 작품 이름이 감지된 경우: 입력한 작품 이름을 제외한 도서 우선
      if (isBookTitle) {
        const originalTitleLower = trimmedQuery.toLowerCase();
        const originalTitleWords = originalTitleLower.split(/\s+/);
        
        books = books.filter(book => {
          const bookTitleLower = (book.title || '').toLowerCase();
          const bookDescriptionLower = (book.description || '').toLowerCase();
          
          // 제목이나 설명에 입력한 작품 이름이 포함되어 있으면 제외
          for (const word of originalTitleWords) {
            if (word.length >= 2) { // 2글자 이상인 단어만 체크
              if (bookTitleLower.includes(word) || bookDescriptionLower.includes(word)) {
                return false; // 제외
              }
            }
          }
          return true; // 포함
        });
        console.log(`[API 서버] 작품 이름 필터링 후: ${books.length}개 도서 (원본: ${data.items?.length || 0}개)`);
      }

      // 1. 학습 관련 키워드가 있으면 "입문", "기초", "처음" 등의 단어가 포함된 도서 우선
      if (isLearning) {
        books.sort((a, b) => {
          const aScore = calculateRelevanceScore(a, ['입문', '기초', '처음', '시작', 'first', 'beginner']);
          const bScore = calculateRelevanceScore(b, ['입문', '기초', '처음', '시작', 'first', 'beginner']);
          return bScore - aScore;
        });
      }

      // 2. 추출된 키워드와 관련성이 높은 도서 우선
      if (extractedKeywords.length > 0) {
        books.sort((a, b) => {
          const aScore = calculateRelevanceScore(a, extractedKeywords);
          const bScore = calculateRelevanceScore(b, extractedKeywords);
          return bScore - aScore;
        });
      }

      // 3. 특정 작품 이름이 감지된 경우: 장르/카테고리 관련성이 높은 도서 우선
      if (isBookTitle) {
        books.sort((a, b) => {
          // 카테고리에 "소설", "판타지", "무협" 등이 포함된 도서 우선
          const genreKeywords = ['소설', '판타지', '무협', '로맨스', '추리', '역사'];
          const aGenreScore = calculateRelevanceScore(a, genreKeywords);
          const bGenreScore = calculateRelevanceScore(b, genreKeywords);
          if (bGenreScore !== aGenreScore) {
            return bGenreScore - aGenreScore;
          }
          // 평점이 높은 도서 우선
          return (b.averageRating || 0) - (a.averageRating || 0);
        });
      }

      // 4. 평점이 높은 도서 우선
      books.sort((a, b) => {
        if (b.averageRating !== a.averageRating) {
          return (b.averageRating || 0) - (a.averageRating || 0);
        }
        return (b.ratingsCount || 0) - (a.ratingsCount || 0);
      });

      // 상위 10개만 반환
      books = books.slice(0, 10);

      console.log(`[API 서버] ===== 도서 추천 완료: ${books.length}개 =====`);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        totalItems: books.length,
        books: books,
        analyzedKeywords: extractedKeywords,
        userQuery: trimmedQuery
      }));
    } catch (error) {
      console.error('[API 서버] Google Books API (AI 추천) 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // ============================================
  // News API - AI 뉴스 검색
  // ============================================
  // 엔드포인트: GET /api/news?q=키워드
  // 기능: News API를 통해 AI 관련 뉴스 기사 검색 (최근 일주일)
  // 주의: /api/news/economy보다 먼저 체크해야 함 (startsWith 매칭 순서)
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/news') && !req.url.startsWith('/api/news/economy')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const q = url.searchParams.get('q');

      if (!q) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '검색 키워드가 필요합니다.' }));
        return;
      }

      // 최근 일주일(7일) 날짜 계산
      const today = new Date();
      const weekAgo = new Date(today);
      weekAgo.setDate(today.getDate() - 7);
      const fromDate = weekAgo.toISOString().split('T')[0]; // YYYY-MM-DD 형식

      // News API에서 여러 페이지를 가져와서 합치기 (일주일치 전체)
      let allArticles = [];
      const maxPages = 10; // 최대 10페이지 (100개씩 = 최대 1000개)
      const pageSize = 100;
      
      for (let page = 1; page <= maxPages; page++) {
        // News API 호출 (최근 일주일 필터링)
        const apiUrl = `${NEWS_API_BASE_URL}/everything?q=${encodeURIComponent(q)}&language=ko&sortBy=publishedAt&pageSize=${pageSize}&page=${page}&from=${fromDate}&apiKey=${NEWS_API_KEY}`;
        
        if (page === 1) {
          console.log(`[API 서버] News API 호출 (AI 뉴스): ${apiUrl}`);
          console.log(`[API 서버] 프록시 사용: ${PROXY_URL}`);
          console.log(`[API 서버] 검색 기간: ${fromDate} ~ ${today.toISOString().split('T')[0]} (최근 일주일)`);
        }
        
        const response = await makeRequest(apiUrl);
        
        if (!response.ok) {
          if (page === 1) {
            const errorData = await response.json().catch(() => ({}));
            console.error(`[API 서버] News API 오류: ${response.status}`, errorData);
            res.writeHead(response.status, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ error: errorData.message || response.statusText, status: response.status }));
            return;
          }
          break; // 첫 페이지가 아니면 중단
        }
        
        const pageData = await response.json();
        
        if (!pageData.articles || pageData.articles.length === 0) {
          break; // 더 이상 기사가 없으면 중단
        }
        
        // 일주일 이상 지난 기사 필터링 (추가 안전장치)
        const now = new Date();
        const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000);
        const filteredArticles = pageData.articles.filter(article => {
          if (!article.publishedAt) return false;
          const publishedDate = new Date(article.publishedAt);
          return publishedDate >= oneWeekAgo;
        });
        
        allArticles = allArticles.concat(filteredArticles);
        
        // 전체 결과 수 확인 (첫 페이지에서만)
        if (page === 1 && pageData.totalResults) {
          const totalResults = pageData.totalResults;
          console.log(`[API 서버] News API 전체 결과: ${totalResults}개 기사`);
        }
        
        // 페이지당 기사 수가 pageSize보다 적으면 마지막 페이지
        if (pageData.articles.length < pageSize) {
          break;
        }
      }
      
      // 중복 제거 (URL 기준)
      const uniqueArticles = [];
      const seenUrls = new Set();
      for (const article of allArticles) {
        if (article.url && !seenUrls.has(article.url)) {
          seenUrls.add(article.url);
          uniqueArticles.push(article);
        }
      }
      
      const data = {
        status: 'ok',
        totalResults: uniqueArticles.length,
        articles: uniqueArticles
      };
      
      console.log(`[API 서버] News API 응답 (AI 뉴스): ${uniqueArticles.length}개 기사 (최근 일주일, 중복 제거 후)`);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(data));
    } catch (error) {
      console.error('[API 서버] News API (AI 뉴스) 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // 엔드포인트: GET /api/books/search?q=키워드&maxResults=개수
  // 기능: Google Books API를 통해 도서 검색
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/books/search')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const q = url.searchParams.get('q');
      const maxResults = url.searchParams.get('maxResults') || '10';

      console.log(`[API 서버] 도서 검색 요청 URL: ${req.url}`);
      console.log(`[API 서버] 파싱된 q 파라미터: "${q}"`);

      if (!q || q.trim() === '') {
        console.error('[API 서버] 검색 키워드가 없습니다.');
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '검색 키워드가 필요합니다. q 파라미터를 확인해주세요.' }));
        return;
      }

      // Google Books API 호출
      const apiUrl = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(q)}&maxResults=${maxResults}&langRestrict=ko`;
      
      console.log(`[API 서버] Google Books API 호출: ${apiUrl}`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`[API 서버] Google Books API 오류: ${response.status}`, errorData);
        
        // 사용자 친화적인 에러 메시지
        let errorMessage = errorData.error?.message || response.statusText;
        if (response.status === 503) {
          errorMessage = 'Google Books API가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.';
        } else if (response.status === 429) {
          errorMessage = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
        } else if (response.status === 500) {
          errorMessage = 'Google Books API 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
        
        res.writeHead(response.status, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: errorMessage, status: response.status }));
        return;
      }

      const data = await response.json();
      console.log(`[API 서버] Google Books API 응답: ${data.items?.length || 0}개 도서`);

      // 응답 형식 변환
      const books = (data.items || []).map(item => {
        const volumeInfo = item.volumeInfo || {};
        return {
          id: item.id,
          title: volumeInfo.title || '제목 없음',
          authors: volumeInfo.authors || ['저자 없음'],
          publisher: volumeInfo.publisher || '출판사 없음',
          publishedDate: volumeInfo.publishedDate || '날짜 없음',
          description: volumeInfo.description || '설명 없음',
          categories: volumeInfo.categories || [],
          pageCount: volumeInfo.pageCount || 0,
          language: volumeInfo.language || 'ko',
          previewLink: volumeInfo.previewLink || '',
          infoLink: volumeInfo.infoLink || '',
          thumbnail: volumeInfo.imageLinks?.thumbnail || volumeInfo.imageLinks?.smallThumbnail || '',
          averageRating: volumeInfo.averageRating || 0,
          ratingsCount: volumeInfo.ratingsCount || 0
        };
      });

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({
        totalItems: books.length,
        books: books
      }));
    } catch (error) {
      console.error('[API 서버] Google Books API 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // ============================================
  // News API - 경제 뉴스 검색
  // ============================================
  // 엔드포인트: GET /api/news/economy?q=키워드
  // 기능: News API를 통해 경제 관련 뉴스 기사 검색 (최근 2주)
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/news/economy')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const q = url.searchParams.get('q');

      if (!q) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '검색 키워드가 필요합니다.' }));
        return;
      }

      // 최근 2주(14일) 날짜 계산
      const today = new Date();
      const twoWeeksAgo = new Date(today);
      twoWeeksAgo.setDate(today.getDate() - 14);
      const fromDate = twoWeeksAgo.toISOString().split('T')[0]; // YYYY-MM-DD 형식
      const toDate = today.toISOString().split('T')[0]; // YYYY-MM-DD 형식

      // 경제 관련 키워드 추가 (검색 쿼리 단순화)
      // OR 연산자가 News API에서 제대로 작동하지 않을 수 있으므로 단순화
      const economyKeywords = ['경제', 'economy', '금융', 'finance', '주식', 'stock'];
      // 검색 쿼리를 단순화: 기본 키워드 + 경제 키워드
      const searchQuery = `${q} (${economyKeywords.slice(0, 3).join(' OR ')})`;

      // News API 호출 (최근 2주 필터링, 경제 관련, 최대 50개)
      // from 파라미터를 사용하여 최근 2주 데이터만 가져오고, sortBy=relevancy로 최신/관련성 높은 뉴스 우선
      const apiUrl = `${NEWS_API_BASE_URL}/everything?q=${encodeURIComponent(searchQuery)}&language=ko&sortBy=relevancy&from=${fromDate}&to=${toDate}&pageSize=50&apiKey=${NEWS_API_KEY}`;
      
      console.log(`[API 서버] News API 호출 (경제): ${apiUrl}`);
      console.log(`[API 서버] 프록시 사용: ${PROXY_URL}`);
      console.log(`[API 서버] 검색 기간: ${fromDate} ~ ${toDate} (최근 2주)`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`[API 서버] News API (경제) 오류: ${response.status}`, errorData);
        res.writeHead(response.status, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: errorData.message || response.statusText, status: response.status }));
        return;
      }
      
      const pageData = await response.json();
      
      // 결과가 없으면 더 넓은 검색 시도 (날짜 제한 없이)
      if (!pageData.articles || pageData.articles.length === 0) {
        console.log(`[API 서버] 첫 검색 결과 없음, 더 넓은 검색 시도...`);
        
        // 더 단순한 검색 쿼리로 재시도 (날짜 제한 없이)
        const simpleQuery = '경제 OR economy OR 금융 OR finance';
        const retryApiUrl = `${NEWS_API_BASE_URL}/everything?q=${encodeURIComponent(simpleQuery)}&language=ko&sortBy=relevancy&from=${fromDate}&to=${toDate}&pageSize=50&apiKey=${NEWS_API_KEY}`;
        
        console.log(`[API 서버] 재시도 검색: ${retryApiUrl}`);
        const retryResponse = await makeRequest(retryApiUrl);
        
        if (retryResponse.ok) {
          const retryData = await retryResponse.json();
          if (retryData.articles && retryData.articles.length > 0) {
            pageData.articles = retryData.articles;
            console.log(`[API 서버] 재시도 성공: ${retryData.articles.length}개 기사 발견`);
          }
        }
      }
      
      // 날짜로 필터링 및 최신순 정렬 (이중 체크)
      const now = new Date();
      const twoWeeksAgoDate = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000);
      let filteredArticles = [];
      if (pageData.articles) {
        filteredArticles = pageData.articles
          .filter(article => {
            if (!article.publishedAt) return false;
            const publishedDate = new Date(article.publishedAt);
            return publishedDate >= twoWeeksAgoDate;
          })
          // 최신순으로 정렬 (내림차순)
          .sort((a, b) => {
            const dateA = new Date(a.publishedAt || 0);
            const dateB = new Date(b.publishedAt || 0);
            return dateB - dateA; // 최신 것이 먼저
          });
      }
      
      // 필터링 후 결과가 없으면 날짜 제한 없이 최신 기사 표시
      if (filteredArticles.length === 0 && pageData.articles && pageData.articles.length > 0) {
        console.log(`[API 서버] 2주 필터링 후 결과 없음, 전체 기사 사용 (최신순 정렬)`);
        filteredArticles = pageData.articles
          .filter(article => article.publishedAt) // 날짜가 있는 것만
          .sort((a, b) => {
            const dateA = new Date(a.publishedAt || 0);
            const dateB = new Date(b.publishedAt || 0);
            return dateB - dateA; // 최신 것이 먼저
          })
          .slice(0, 50); // 최대 50개
      }
      
      // 중복 제거 (URL 기준)
      const uniqueArticles = [];
      const seenUrls = new Set();
      for (const article of filteredArticles) {
        if (article.url && !seenUrls.has(article.url)) {
          seenUrls.add(article.url);
          uniqueArticles.push(article);
        }
      }
      
      // 최대 50개로 제한
      const finalArticles = uniqueArticles.slice(0, 50);
      
      const data = {
        status: 'ok',
        totalResults: finalArticles.length,
        articles: finalArticles
      };
      
      console.log(`[API 서버] News API 응답 (경제): ${finalArticles.length}개 기사 (최근 2주, 최대 50개)`);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(data));
    } catch (error) {
      console.error('[API 서버] News API (경제) 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // ============================================
  // Last.fm API - 음악 추천
  // ============================================
  // 엔드포인트: GET /api/music/recommend?songTitle=제목&artist=아티스트
  // 기능: Last.fm API를 통해 유사한 트랙 검색
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/music/recommend')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const songTitle = url.searchParams.get('songTitle');
      const artist = url.searchParams.get('artist');

      if (!songTitle) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '노래 제목이 필요합니다.' }));
        return;
      }

      // 아티스트가 없을 때는 track.search로 먼저 노래를 찾아서 아티스트 정보를 얻음
      let finalArtist = artist;
      let finalTrack = songTitle;
      
      if (!artist || artist.trim() === '') {
        // track.search로 노래 검색하여 아티스트 정보 얻기
        try {
          const searchUrl = `${LASTFM_API_BASE_URL}/?method=track.search&track=${encodeURIComponent(songTitle)}&api_key=${LASTFM_API_KEY}&format=json&limit=1`;
          console.log(`[API 서버] Last.fm API 호출 (검색): ${searchUrl}`);
          
          const searchResponse = await makeRequest(searchUrl);
          if (searchResponse.ok) {
            const searchData = await searchResponse.json();
            if (searchData.results && searchData.results.trackmatches && searchData.results.trackmatches.track && searchData.results.trackmatches.track.length > 0) {
              const firstTrack = searchData.results.trackmatches.track[0];
              finalArtist = firstTrack.artist;
              finalTrack = firstTrack.name;
              console.log(`[API 서버] 검색 결과: "${finalTrack}" by "${finalArtist}"`);
            }
          }
        } catch (searchError) {
          console.warn(`[API 서버] 노래 검색 실패, 원본 값 사용: ${searchError.message}`);
          // 검색 실패 시 원본 값 사용
        }
      }

      const apiUrl = `${LASTFM_API_BASE_URL}/?method=track.getsimilar&artist=${encodeURIComponent(finalArtist || songTitle)}&track=${encodeURIComponent(finalTrack)}&api_key=${LASTFM_API_KEY}&format=json&limit=10`;
      
      console.log(`[API 서버] Last.fm API 호출 (추천): ${apiUrl}`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Last.fm API 오류: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`[API 서버] Last.fm API 응답: ${data.similartracks?.track?.length || 0}개 추천`);

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(data));
    } catch (error) {
      console.error('[API 서버] Last.fm API (추천) 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // ============================================
  // Last.fm API - 라디오 방송 정보 (현재 재생)
  // ============================================
  // 엔드포인트: GET /api/music/radio/current?station=방송국&limit=개수
  // 기능: Last.fm API를 통해 인기 차트에서 현재 재생 중인 노래 조회
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/music/radio/current')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const station = url.searchParams.get('station') || 'kbs';
      const limit = url.searchParams.get('limit') || '1';

      // ⚠️ 주의: Last.fm의 chart.getTopTracks는 글로벌 인기 차트입니다.
      // 실제 한국 라디오 방송국(KBS, MBC, SBS)의 실시간 재생 정보가 아닙니다.
      // station 파라미터는 현재 사용되지 않습니다.
      const apiUrl = `${LASTFM_API_BASE_URL}/?method=chart.getTopTracks&api_key=${LASTFM_API_KEY}&format=json&limit=${limit}`;
      
      console.log(`[API 서버] Last.fm API 호출 (글로벌 인기 차트 - station 파라미터 무시됨): ${apiUrl}`);
      console.log(`[API 서버] ⚠️ 주의: 실제 ${station} 방송국 정보가 아닌 Last.fm 글로벌 차트입니다.`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Last.fm API 오류: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`[API 서버] Last.fm API 응답: ${data.tracks?.track?.length || 0}개 트랙`);

      // 응답에 메타데이터 추가하여 실제 방송국 정보가 아님을 명시
      const responseData = {
        ...data,
        _meta: {
          warning: '이 데이터는 실제 라디오 방송국 정보가 아닌 Last.fm 글로벌 인기 차트입니다.',
          requestedStation: station,
          dataSource: 'Last.fm Global Chart',
          note: '실제 한국 라디오 방송 정보를 얻으려면 해당 방송국의 공식 API가 필요합니다.'
        }
      };

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(responseData));
    } catch (error) {
      console.error('[API 서버] Last.fm API (현재 재생) 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // ============================================
  // Last.fm API - 라디오 방송 정보 (최근 재생)
  // ============================================
  // 엔드포인트: GET /api/music/radio/recent?station=방송국&limit=개수
  // 기능: Last.fm API를 통해 인기 차트에서 최근 재생된 노래 목록 조회
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/music/radio/recent')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const station = url.searchParams.get('station') || 'kbs';
      const limit = url.searchParams.get('limit') || '10';

      // ⚠️ 주의: Last.fm의 chart.getTopTracks는 글로벌 인기 차트입니다.
      // 실제 한국 라디오 방송국(KBS, MBC, SBS)의 실시간 재생 정보가 아닙니다.
      // station 파라미터는 현재 사용되지 않습니다.
      const apiUrl = `${LASTFM_API_BASE_URL}/?method=chart.getTopTracks&api_key=${LASTFM_API_KEY}&format=json&limit=${limit}`;
      
      console.log(`[API 서버] Last.fm API 호출 (글로벌 인기 차트 - station 파라미터 무시됨): ${apiUrl}`);
      console.log(`[API 서버] ⚠️ 주의: 실제 ${station} 방송국 정보가 아닌 Last.fm 글로벌 차트입니다.`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        throw new Error(`Last.fm API 오류: ${response.status}`);
      }
      
      const data = await response.json();
      console.log(`[API 서버] Last.fm API 응답: ${data.tracks?.track?.length || 0}개 트랙`);

      // 응답에 메타데이터 추가하여 실제 방송국 정보가 아님을 명시
      const responseData = {
        ...data,
        _meta: {
          warning: '이 데이터는 실제 라디오 방송국 정보가 아닌 Last.fm 글로벌 인기 차트입니다.',
          requestedStation: station,
          dataSource: 'Last.fm Global Chart',
          note: '실제 한국 라디오 방송 정보를 얻으려면 해당 방송국의 공식 API가 필요합니다.'
        }
      };

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify(responseData));
    } catch (error) {
      console.error('[API 서버] Last.fm API (최근 재생) 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // 엔드포인트: GET /api/books/search?q=키워드&maxResults=개수
  // 기능: Google Books API를 통해 도서 검색
  // 인증: API 키 또는 JWT 토큰 (선택사항)
  else if (req.url && req.url.startsWith('/api/books/search')) {
    try {
      // API 키 또는 JWT 토큰 인증 (선택사항 - 인증 없어도 접근 가능하지만 사용 이력 기록)
      const auth = authenticateApiKeyOrToken(req);
      
      // API 키가 제공되었지만 유효하지 않은 경우
      if (auth && auth.error) {
        res.writeHead(401, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: auth.message }));
        return;
      }
      
      const url = new URL(req.url, `http://localhost:${PORT}`);
      const q = url.searchParams.get('q');
      const maxResults = url.searchParams.get('maxResults') || '10';

      console.log(`[API 서버] 도서 검색 요청 URL: ${req.url}`);
      console.log(`[API 서버] 파싱된 q 파라미터: "${q}"`);

      if (!q || q.trim() === '') {
        console.error('[API 서버] 검색 키워드가 없습니다.');
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: '검색 키워드가 필요합니다. q 파라미터를 확인해주세요.' }));
        return;
      }

      // Google Books API 호출
      const apiUrl = `https://www.googleapis.com/books/v1/volumes?q=${encodeURIComponent(q)}&maxResults=${maxResults}&langRestrict=ko`;
      
      console.log(`[API 서버] Google Books API 호출: ${apiUrl}`);
      
      const response = await makeRequest(apiUrl);
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        console.error(`[API 서버] Google Books API 오류: ${response.status}`, errorData);
        
        // 사용자 친화적인 에러 메시지
        let errorMessage = errorData.error?.message || response.statusText;
        if (response.status === 503) {
          errorMessage = 'Google Books API가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요.';
        } else if (response.status === 429) {
          errorMessage = '요청이 너무 많습니다. 잠시 후 다시 시도해주세요.';
        } else if (response.status === 500) {
          errorMessage = 'Google Books API 서버 오류가 발생했습니다. 잠시 후 다시 시도해주세요.';
        }
        
        res.writeHead(response.status, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: errorMessage, status: response.status }));
        return;
      }

      const data = await response.json();
      console.log(`[API 서버] Google Books API 응답: ${data.items?.length || 0}개 도서`);

      // 응답 형식 변환
      const books = (data.items || []).map(item => {
        const volumeInfo = item.volumeInfo || {};
        return {
          id: item.id,
          title: volumeInfo.title || '제목 없음',
          authors: volumeInfo.authors || ['저자 정보 없음'],
          publisher: volumeInfo.publisher || '출판사 정보 없음',
          publishedDate: volumeInfo.publishedDate || '출판일 정보 없음',
          description: volumeInfo.description || '설명 없음',
          categories: volumeInfo.categories || [],
          pageCount: volumeInfo.pageCount || 0,
          language: volumeInfo.language || 'ko',
          previewLink: volumeInfo.previewLink || '',
          infoLink: volumeInfo.infoLink || '',
          thumbnail: volumeInfo.imageLinks?.thumbnail || '',
          isbn: volumeInfo.industryIdentifiers?.[0]?.identifier || ''
        };
      });

      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ 
        status: 'ok',
        totalItems: data.totalItems || 0,
        books: books
      }));
    } catch (error) {
      console.error('[API 서버] Google Books API 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }

  // ============================================
  // 데이터베이스 스키마 조회 API
  // ============================================
  
  // 데이터베이스 스키마 조회: GET /api/db/schema
  else if (req.url === '/api/db/schema' && req.method === 'GET') {
    try {
      // 데이터베이스가 초기화되었는지 확인
      const schema = getSchema();
      const tables = getTables();
      
      // 빈 결과 체크
      if (!schema || Object.keys(schema).length === 0) {
        console.warn('[API 서버] 스키마가 비어있습니다.');
      }
      
      return sendJSON(res, 200, {
        success: true,
        tables: tables || [],
        schema: schema || {}
      });
    } catch (error) {
      console.error('[API 서버] 데이터베이스 스키마 조회 오류:', error);
      console.error('[API 서버] 오류 상세:', error.stack);
      return sendJSON(res, 500, {
        success: false,
        error: `데이터베이스 스키마 조회 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }

  // ============================================
  // Docker 상태 조회 API
  // ============================================
  
  // Docker 상태 조회: GET /api/docker/status
  else if ((req.url === '/api/docker/status' || req.url.split('?')[0] === '/api/docker/status') && req.method === 'GET') {
    try {
      console.log('[API 서버] Docker 상태 조회 요청:', req.url);
      const dockerStatus = {
        installed: false,
        running: false,
        version: null,
        containers: [],
        useWSL: false,
        wslMessage: null
      };

      // WSL 환경 감지 (Windows 환경에서 WSL 사용 여부 확인)
      try {
        // Windows 환경인지 확인
        if (process.platform === 'win32') {
          // WSL이 설치되어 있는지 확인
          try {
            const { stdout: wslListOutput } = await execAsync('wsl --list --quiet 2>nul || echo ""');
            if (wslListOutput && wslListOutput.trim()) {
              // WSL 내에서 Docker가 작동하는지 확인
              try {
                await execAsync('wsl docker --version 2>nul');
                dockerStatus.useWSL = true;
                dockerStatus.wslMessage = 'WSL 2 환경에서 Docker Engine을 사용 중입니다. 모든 명령어는 WSL을 통해 실행됩니다.';
              } catch {
                // WSL 내에 Docker가 없으면 일반 Docker 사용
                dockerStatus.useWSL = false;
                dockerStatus.wslMessage = null;
              }
            }
          } catch {
            // WSL 확인 실패 시 일반 Docker 사용
            dockerStatus.useWSL = false;
            dockerStatus.wslMessage = null;
          }
        }
      } catch (error) {
        // 환경 감지 실패 시 일반 Docker 사용
        dockerStatus.useWSL = false;
        dockerStatus.wslMessage = null;
        console.log('[API 서버] 환경 감지 실패:', error.message);
      }

      // Docker 설치 확인
      try {
        const { stdout: versionOutput } = await execAsync('docker --version');
        dockerStatus.installed = true;
        dockerStatus.version = versionOutput.trim().replace('Docker version ', '').split(',')[0];
      } catch (error) {
        return sendJSON(res, 200, {
          success: true,
          docker: dockerStatus,
          message: 'Docker가 설치되어 있지 않습니다.'
        });
      }

      // Docker Compose 설치 확인
      let dockerComposeCmd = 'docker compose';
      try {
        await execAsync('docker compose version');
      } catch {
        try {
          await execAsync('docker-compose --version');
          dockerComposeCmd = 'docker-compose';
        } catch {
          dockerStatus.running = false;
          return sendJSON(res, 200, {
            success: true,
            docker: dockerStatus,
            message: 'Docker Compose가 설치되어 있지 않습니다.'
          });
        }
      }

      // 실행 중인 컨테이너 확인
      try {
        const { stdout: psOutput } = await execAsync('docker ps --format "{{.Names}}|{{.Status}}|{{.Image}}|{{.Ports}}"');
        const containers = psOutput.trim().split('\n').filter(line => line.includes('test02-')).map(line => {
          const [name, status, image, ports] = line.split('|');
          return {
            name: name.trim(),
            status: status.trim(),
            image: image.trim(),
            ports: ports.trim() || 'N/A',
            running: status.includes('Up')
          };
        });

        dockerStatus.containers = containers;
        dockerStatus.running = containers.length > 0;
      } catch (error) {
        console.error('[API 서버] Docker 컨테이너 조회 오류:', error);
        dockerStatus.running = false;
      }

      return sendJSON(res, 200, {
        success: true,
        docker: dockerStatus
      });
    } catch (error) {
      console.error('[API 서버] Docker 상태 조회 오류:', error);
      return sendJSON(res, 500, {
        success: false,
        error: `Docker 상태 조회 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }

  // ============================================
  // Docker 컨테이너 제어 API
  // ============================================
  
  // 컨테이너 시작: POST /api/docker/start
  else if ((req.url === '/api/docker/start' || req.url.split('?')[0] === '/api/docker/start') && req.method === 'POST') {
    try {
      console.log('[API 서버] Docker 컨테이너 시작 요청:', req.url);
      
      // Docker Compose 명령어 확인
      let dockerComposeCmd = 'docker compose';
      try {
        await execAsync('docker compose version');
      } catch {
        try {
          await execAsync('docker-compose --version');
          dockerComposeCmd = 'docker-compose';
        } catch {
          return sendJSON(res, 400, {
            success: false,
            error: 'Docker Compose가 설치되어 있지 않습니다.'
          });
        }
      }
      
      // WSL 환경 확인 (WSL이 설치되어 있고 Docker가 WSL 내에 있는 경우만 사용)
      let useWSL = false;
      if (process.platform === 'win32') {
        try {
          // WSL이 설치되어 있는지 확인
          const { stdout: wslListOutput } = await execAsync('wsl --list --quiet 2>nul || echo ""');
          if (wslListOutput && wslListOutput.trim()) {
            // WSL 내에서 Docker가 작동하는지 확인
            try {
              await execAsync('wsl docker --version 2>nul');
              useWSL = true;
            } catch {
              // WSL 내에 Docker가 없으면 일반 명령어 사용
              useWSL = false;
            }
          }
        } catch {
          // WSL 확인 실패 시 일반 명령어 사용
          useWSL = false;
        }
      }
      
      // 컨테이너 시작 명령어 실행
      const command = useWSL ? `wsl ${dockerComposeCmd} up -d` : `${dockerComposeCmd} up -d`;
      console.log('[API 서버] 실행 명령어:', command);
      
      const { stdout, stderr } = await execAsync(command, { cwd: __dirname });
      
        return sendJSON(res, 200, {
          success: true,
          message: '컨테이너가 시작되었습니다.',
          output: stdout,
          useWSL: useWSL
        });
    } catch (error) {
      console.error('[API 서버] Docker 컨테이너 시작 오류:', error);
      return sendJSON(res, 500, {
        success: false,
        error: `컨테이너 시작 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }
  
  // 컨테이너 중지: POST /api/docker/stop
  else if ((req.url === '/api/docker/stop' || req.url.split('?')[0] === '/api/docker/stop') && req.method === 'POST') {
    try {
      console.log('[API 서버] Docker 컨테이너 중지 요청:', req.url);
      
      // Docker Compose 명령어 확인
      let dockerComposeCmd = 'docker compose';
      try {
        await execAsync('docker compose version');
      } catch {
        try {
          await execAsync('docker-compose --version');
          dockerComposeCmd = 'docker-compose';
        } catch {
          return sendJSON(res, 400, {
            success: false,
            error: 'Docker Compose가 설치되어 있지 않습니다.'
          });
        }
      }
      
      // WSL 환경 확인 (WSL이 설치되어 있고 Docker가 WSL 내에 있는 경우만 사용)
      let useWSL = false;
      if (process.platform === 'win32') {
        try {
          // WSL이 설치되어 있는지 확인
          const { stdout: wslListOutput } = await execAsync('wsl --list --quiet 2>nul || echo ""');
          if (wslListOutput && wslListOutput.trim()) {
            // WSL 내에서 Docker가 작동하는지 확인
            try {
              await execAsync('wsl docker --version 2>nul');
              useWSL = true;
            } catch {
              // WSL 내에 Docker가 없으면 일반 명령어 사용
              useWSL = false;
            }
          }
        } catch {
          // WSL 확인 실패 시 일반 명령어 사용
          useWSL = false;
        }
      }
      
      // 컨테이너 중지 명령어 실행
      const command = useWSL ? `wsl ${dockerComposeCmd} down` : `${dockerComposeCmd} down`;
      console.log('[API 서버] 실행 명령어:', command);
      
      const { stdout, stderr } = await execAsync(command, { cwd: __dirname });
      
        return sendJSON(res, 200, {
          success: true,
          message: '컨테이너가 중지되었습니다.',
          output: stdout,
          useWSL: useWSL
        });
    } catch (error) {
      console.error('[API 서버] Docker 컨테이너 중지 오류:', error);
      return sendJSON(res, 500, {
        success: false,
        error: `컨테이너 중지 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }
  
  // 컨테이너 재시작: POST /api/docker/restart
  else if ((req.url === '/api/docker/restart' || req.url.split('?')[0] === '/api/docker/restart') && req.method === 'POST') {
    try {
      console.log('[API 서버] Docker 컨테이너 재시작 요청:', req.url);
      
      // Docker Compose 명령어 확인
      let dockerComposeCmd = 'docker compose';
      try {
        await execAsync('docker compose version');
      } catch {
        try {
          await execAsync('docker-compose --version');
          dockerComposeCmd = 'docker-compose';
        } catch {
          return sendJSON(res, 400, {
            success: false,
            error: 'Docker Compose가 설치되어 있지 않습니다.'
          });
        }
      }
      
      // WSL 환경 확인 (WSL이 설치되어 있고 Docker가 WSL 내에 있는 경우만 사용)
      let useWSL = false;
      if (process.platform === 'win32') {
        try {
          // WSL이 설치되어 있는지 확인
          const { stdout: wslListOutput } = await execAsync('wsl --list --quiet 2>nul || echo ""');
          if (wslListOutput && wslListOutput.trim()) {
            // WSL 내에서 Docker가 작동하는지 확인
            try {
              await execAsync('wsl docker --version 2>nul');
              useWSL = true;
            } catch {
              // WSL 내에 Docker가 없으면 일반 명령어 사용
              useWSL = false;
            }
          }
        } catch {
          // WSL 확인 실패 시 일반 명령어 사용
          useWSL = false;
        }
      }
      
      // 컨테이너 재시작 명령어 실행
      const command = useWSL ? `wsl ${dockerComposeCmd} restart` : `${dockerComposeCmd} restart`;
      console.log('[API 서버] 실행 명령어:', command);
      
      const { stdout, stderr } = await execAsync(command, { cwd: __dirname });
      
        return sendJSON(res, 200, {
          success: true,
          message: '컨테이너가 재시작되었습니다.',
          output: stdout,
          useWSL: useWSL
        });
    } catch (error) {
      console.error('[API 서버] Docker 컨테이너 재시작 오류:', error);
      return sendJSON(res, 500, {
        success: false,
        error: `컨테이너 재시작 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }

  // ============================================
  // 문서 관리 API
  // ============================================
  
  // 문서 목록 조회: GET /api/docs/list
  else if ((req.url === '/api/docs/list' || req.url.split('?')[0] === '/api/docs/list') && req.method === 'GET') {
    try {
      console.log('[API 서버] 문서 목록 조회 요청:', req.url);
      const docsDir = join(__dirname, 'docs');
      const files = readdirSync(docsDir);
      
      const markdownFiles = files
        .filter(file => file.endsWith('.md'))
        .map(file => {
          const filePath = join(docsDir, file);
          const stats = statSync(filePath);
          return {
            name: file,
            title: file.replace('.md', '').replace(/_/g, ' '),
            size: stats.size,
            modified: stats.mtime.toISOString(),
            path: `/api/docs/content/${encodeURIComponent(file)}`
          };
        })
        .sort((a, b) => b.modified.localeCompare(a.modified)); // 최신순 정렬
      
      return sendJSON(res, 200, {
        success: true,
        docs: markdownFiles,
        count: markdownFiles.length
      });
    } catch (error) {
      console.error('[API 서버] 문서 목록 조회 오류:', error);
      return sendJSON(res, 500, {
        success: false,
        error: `문서 목록 조회 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }
  
  // 문서 내용 조회: GET /api/docs/content/:filename
  else if (req.url.startsWith('/api/docs/content/') && req.method === 'GET') {
    try {
      const urlParts = req.url.split('/');
      const encodedFilename = urlParts[urlParts.length - 1];
      const filename = decodeURIComponent(encodedFilename);
      
      // 보안: 파일명에 .. 또는 / 포함 시 차단
      if (filename.includes('..') || filename.includes('/') || filename.includes('\\')) {
        return sendJSON(res, 400, {
          success: false,
          error: '잘못된 파일명입니다.'
        });
      }
      
      console.log('[API 서버] 문서 내용 조회 요청:', filename);
      const filePath = join(__dirname, 'docs', filename);
      
      try {
        const content = readFileSync(filePath, 'utf-8');
        return sendJSON(res, 200, {
          success: true,
          filename: filename,
          title: filename.replace('.md', '').replace(/_/g, ' '),
          content: content
        });
      } catch (fileError) {
        if (fileError.code === 'ENOENT') {
          return sendJSON(res, 404, {
            success: false,
            error: '파일을 찾을 수 없습니다.'
          });
        }
        throw fileError;
      }
    } catch (error) {
      console.error('[API 서버] 문서 내용 조회 오류:', error);
      return sendJSON(res, 500, {
        success: false,
        error: `문서 내용 조회 중 오류가 발생했습니다: ${error.message}`
      });
    }
  }

  // ============================================
  // Swagger UI
  // ============================================
  // 엔드포인트: GET /api-docs
  // 기능: Swagger UI를 제공하여 API 문서화 및 테스트
  else if (req.url === '/api-docs' || req.url === '/api-docs/') {
    try {
      const html = `
<!DOCTYPE html>
<html lang="ko">
<head>
  <meta charset="UTF-8">
  <title>API 문서 - Swagger UI</title>
  <link rel="stylesheet" type="text/css" href="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui.css" />
  <style>
    html {
      box-sizing: border-box;
      overflow: -moz-scrollbars-vertical;
      overflow-y: scroll;
    }
    *, *:before, *:after {
      box-sizing: inherit;
    }
    body {
      margin:0;
      background: #fafafa;
    }
  </style>
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-bundle.js"></script>
  <script src="https://unpkg.com/swagger-ui-dist@5.9.0/swagger-ui-standalone-preset.js"></script>
  <script>
    window.onload = function() {
      const ui = SwaggerUIBundle({
        url: '/swagger.json',
        dom_id: '#swagger-ui',
        deepLinking: true,
        presets: [
          SwaggerUIBundle.presets.apis,
          SwaggerUIStandalonePreset
        ],
        plugins: [
          SwaggerUIBundle.plugins.DownloadUrl
        ],
        layout: "StandaloneLayout"
      });
    };
  </script>
</body>
</html>
      `;
      
      res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
      res.end(html);
    } catch (error) {
      console.error('[API 서버] Swagger UI 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // 리니지 HTML 파일 제공 엔드포인트
  else if (req.url && req.url.startsWith('/api/lineage/')) {
    try {
      // URL에서 파일 경로 추출: /api/lineage/queries/sql_analysis/file.html
      const filePath = req.url.replace('/api/lineage/', '').replace(/^\//, '');
      const fullPath = join(__dirname, filePath);
      
      console.log('[API 서버] 리니지 HTML 파일 요청:', {
        url: req.url,
        filePath: filePath,
        fullPath: fullPath
      });
      
      // 보안: 상위 디렉토리 접근 방지
      if (fullPath.indexOf(__dirname) !== 0) {
        res.writeHead(403, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'Access denied' }));
        return;
      }
      
      if (fs.existsSync(fullPath) && fullPath.endsWith('.html')) {
        const htmlContent = fs.readFileSync(fullPath, 'utf-8');
        res.writeHead(200, { 
          'Content-Type': 'text/html; charset=utf-8',
          'Access-Control-Allow-Origin': '*'
        });
        res.end(htmlContent);
      } else {
        res.writeHead(404, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: 'File not found', path: filePath }));
      }
    } catch (error) {
      console.error('[API 서버] 리니지 HTML 파일 제공 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // Swagger JSON 제공
  else if (req.url === '/swagger.json') {
    try {
      const swaggerJson = readFileSync(join(__dirname, 'swagger.json'), 'utf8');
      res.writeHead(200, { 'Content-Type': 'application/json' });
      res.end(swaggerJson);
    } catch (error) {
      console.error('[API 서버] Swagger JSON 오류:', error);
      res.writeHead(500, { 'Content-Type': 'application/json' });
      res.end(JSON.stringify({ error: error.message }));
    }
  }
  // ============================================
  // 화면 검증 API 프록시 (Python HTTP 서버로 프록시)
  // ============================================
  // 엔드포인트: POST /api/screen/validate
  // 엔드포인트: POST /api/screen/capture
  // 엔드포인트: POST /api/screen/interact
  // 기능: Python HTTP 서버(포트 3002)로 요청을 프록시
  else if (req.url && (req.url.startsWith('/api/screen/validate') || req.url.startsWith('/api/screen/capture') || req.url.startsWith('/api/screen/interact'))) {
    let body = '';
    
    req.on('data', chunk => {
      body += chunk.toString();
    });
    
    req.on('end', async () => {
      try {
        const requestData = JSON.parse(body);
        const pythonServerUrl = `http://localhost:3002${req.url}`;
        
        console.log(`[API 서버] 화면 검증 요청 프록시: ${pythonServerUrl}`);
        
        // Python HTTP 서버로 요청 전달
        const requestOptions = {
          hostname: 'localhost',
          port: 3002,
          path: req.url,
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Content-Length': Buffer.byteLength(body)
          }
        };
        
        // 타임아웃 설정 (130초 - Python 서버 타임아웃보다 길게)
        const timeout = setTimeout(() => {
          if (!res.headersSent) {
            console.error('[API 서버] 화면 검증 프록시 타임아웃 (130초)');
            proxyReq.destroy();
            res.writeHead(504, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
              success: false,
              error: 'Python 서버 응답 타임아웃 (130초 초과). 서버가 응답하지 않습니다.'
            }));
          }
        }, 130000); // 130초
        
        const proxyReq = http.request(requestOptions, (proxyRes) => {
          clearTimeout(timeout);
          let proxyBody = '';
          
          proxyRes.on('data', (chunk) => {
            proxyBody += chunk;
          });
          
          proxyRes.on('end', () => {
            if (!res.headersSent) {
              res.writeHead(proxyRes.statusCode || 200, {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
              });
              res.end(proxyBody);
            }
          });
          
          proxyRes.on('error', (error) => {
            clearTimeout(timeout);
            if (!res.headersSent) {
              console.error('[API 서버] Python 서버 응답 오류:', error);
              res.writeHead(500, { 'Content-Type': 'application/json' });
              res.end(JSON.stringify({ 
                success: false,
                error: `Python 서버 응답 오류: ${error.message}`
              }));
            }
          });
        });
        
        proxyReq.on('error', (error) => {
          clearTimeout(timeout);
          if (!res.headersSent) {
            console.error('[API 서버] 화면 검증 프록시 오류:', error);
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
              success: false,
              error: `Python 서버 연결 실패: ${error.message}. Python HTTP 서버가 실행 중인지 확인하세요. (포트 3002)`
            }));
          }
        });
        
        proxyReq.setTimeout(130000, () => {
          if (!res.headersSent) {
            console.error('[API 서버] 프록시 요청 타임아웃');
            proxyReq.destroy();
            res.writeHead(504, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ 
              success: false,
              error: 'Python 서버 연결 타임아웃 (130초 초과)'
            }));
          }
        });
        
        proxyReq.write(body);
        proxyReq.end();
        
      } catch (error) {
        console.error('[API 서버] 화면 검증 요청 처리 오류:', error);
        res.writeHead(500, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ success: false, error: error.message }));
      }
    });
  }
  
  // SQL 쿼리 분석 API
  // 엔드포인트: POST /api/sql/analyze
  // 기능: MCP SQL 쿼리 분석 서버를 통해 쿼리 분석 수행
  else if ((req.url === '/api/sql/analyze' || req.url.startsWith('/api/sql/analyze')) && req.method === 'POST') {
    console.log('[API 서버] SQL 쿼리 분석 요청 수신:', req.url, req.method);
    
    // 요청 타임아웃 설정 (5분)
    req.setTimeout(300000, () => {
      if (!res.headersSent) {
        console.error('[API 서버] SQL 쿼리 분석 요청 타임아웃 (5분 초과)');
        res.writeHead(504, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: false,
          error: '요청 타임아웃: SQL 쿼리 분석에 시간이 너무 오래 걸립니다. (5분 초과)'
        }));
      }
    });
    
    let body = '';
    const maxBodySize = 50 * 1024 * 1024; // 50MB 제한
    let bodySize = 0;
    
    req.on('data', chunk => {
      bodySize += chunk.length;
      if (bodySize > maxBodySize) {
        console.error('[API 서버] 요청 본문 크기 초과:', bodySize);
        res.writeHead(413, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: false,
          error: '요청 본문이 너무 큽니다. (50MB 초과)'
        }));
        return;
      }
      body += chunk.toString('utf-8');
    });
    
    req.on('end', async () => {
      try {
        const requestData = JSON.parse(body);
        const { query_file, query_text, output_format = 'both' } = requestData;
        
        console.log('[API 서버] SQL 쿼리 분석 요청');
        console.log('[API 서버] 요청 데이터:', { query_file, has_query_text: !!query_text, output_format });
        
        if (!query_file && !query_text) {
          return sendJSON(res, 400, {
            success: false,
            error: 'SQL 쿼리 또는 파일 경로를 제공해야 합니다.'
          });
        }
        
        // Python 스크립트 실행을 위한 명령어 구성
        const pythonScript = join(__dirname, 'test-sql-query-analyzer.py');
        let command = `python "${pythonScript}"`;
        
        // 임시 SQL 파일 생성 (query_text가 있는 경우)
        let tempFile = null;
        const fs = await import('fs');
        const path = await import('path');
        
        if (query_text && !query_file) {
          tempFile = join(__dirname, 'temp_query_' + Date.now() + '.sql');
          fs.writeFileSync(tempFile, query_text, 'utf-8');
          
          // 파일 크기 확인
          const fileSize = fs.statSync(tempFile).size;
          const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2);
          console.log(`[API 서버] 임시 SQL 파일 생성 완료 (크기: ${fileSizeMB}MB)`);
          
          if (fileSize > 10 * 1024 * 1024) { // 10MB 초과
            console.warn(`[API 서버] 큰 파일 경고: ${fileSizeMB}MB`);
          }
          
          command += ` "${tempFile}"`;
        } else if (query_file) {
          // 상대 경로를 절대 경로로 변환
          let filePath = query_file;
          
          // 상대 경로인 경우 프로젝트 루트 기준으로 변환
          if (!path.isAbsolute(query_file)) {
            filePath = join(__dirname, query_file);
          }
          
          // 파일 존재 여부 확인
          if (!fs.existsSync(filePath)) {
            return sendJSON(res, 400, {
              success: false,
              error: `SQL 파일을 찾을 수 없습니다: ${query_file}\n절대 경로: ${filePath}`
            });
          }
          
          // 파일 크기 확인
          const fileSize = fs.statSync(filePath).size;
          const fileSizeMB = (fileSize / (1024 * 1024)).toFixed(2);
          const fileLines = fs.readFileSync(filePath, 'utf-8').split('\n').length;
          console.log(`[API 서버] SQL 파일 정보: ${filePath}`);
          console.log(`[API 서버] 파일 크기: ${fileSizeMB}MB, 라인 수: ${fileLines}`);
          
          if (fileSize > 10 * 1024 * 1024) { // 10MB 초과
            console.warn(`[API 서버] 큰 파일 경고: ${fileSizeMB}MB`);
          }
          
          command += ` "${filePath}"`;
        }
        
        // Python 스크립트 실행
        console.log('[API 서버] 실행 명령어:', command);
        console.log('[API 서버] 큰 파일 분석 시작 (타임아웃: 5분, 버퍼: 50MB)');
        
        const startTime = Date.now();
        let stdout, stderr;
        
        try {
          const result = await execAsync(command, {
            cwd: __dirname,
            maxBuffer: 50 * 1024 * 1024, // 50MB로 증가 (큰 파일 처리)
            timeout: 300000 // 5분 타임아웃
          });
          stdout = result.stdout;
          stderr = result.stderr;
        } catch (execError) {
          // execAsync는 에러가 발생해도 stdout/stderr를 반환할 수 있음
          stdout = execError.stdout || '';
          stderr = execError.stderr || execError.message || '';
          
          console.error('[API 서버] Python 스크립트 실행 오류:', execError.message);
          console.error('[API 서버] stderr:', stderr.substring(0, 1000));
          
          // 타임아웃 오류인지 확인
          if (execError.code === 'TIMEOUT' || execError.signal === 'SIGTERM') {
            return sendJSON(res, 504, {
              success: false,
              error: 'SQL 쿼리 분석 타임아웃: 분석에 시간이 너무 오래 걸립니다. (5분 초과)',
              suggestion: '쿼리를 더 작은 단위로 분할하거나 복잡도를 줄여주세요.'
            });
          }
          
          // 버퍼 오버플로우 오류
          if (execError.code === 'ENOBUFS' || stderr.includes('maxBuffer')) {
            return sendJSON(res, 413, {
              success: false,
              error: '분석 결과가 너무 큽니다. 쿼리를 더 작은 단위로 분할해주세요.',
              suggestion: '큰 쿼리는 여러 개의 작은 쿼리로 나누어 분석하세요.'
            });
          }
          
          // 기타 실행 오류
          return sendJSON(res, 500, {
            success: false,
            error: `Python 스크립트 실행 오류: ${execError.message}`,
            stderr: stderr.substring(0, 2000),
            stdout: stdout.substring(0, 1000)
          });
        }
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`[API 서버] Python 스크립트 실행 완료 (소요 시간: ${elapsedTime}초)`);
        
        console.log('[API 서버] Python 스크립트 stdout:', stdout.substring(0, 500));
        if (stderr) {
          console.log('[API 서버] Python 스크립트 stderr:', stderr.substring(0, 500));
        }
        
        // 임시 파일 삭제 (나중에 삭제 - 결과 파일 찾은 후)
        let tempFileToDelete = tempFile;
        
        // 분석 결과 파일 찾기
        const fs = await import('fs');
        const path = await import('path');
        const logsDir = join(__dirname, 'logs', 'sql_analysis');
        
        // 디렉토리가 없으면 생성
        if (!fs.existsSync(logsDir)) {
          fs.mkdirSync(logsDir, { recursive: true });
        }
        
        // 가장 최근 생성된 분석 결과 파일 찾기 (최대 5초 전까지)
        const now = Date.now();
        const files = fs.readdirSync(logsDir)
          .filter(f => f.endsWith('.json') && !f.includes('lineage'))
          .map(f => {
            const filePath = join(logsDir, f);
            const stats = fs.statSync(filePath);
            return {
              name: f,
              path: filePath,
              time: stats.mtime.getTime()
            };
          })
          .filter(f => (now - f.time) < 5000) // 5초 이내 생성된 파일만
          .sort((a, b) => b.time - a.time);
        
        console.log('[API 서버] 찾은 결과 파일 수:', files.length);
        if (files.length > 0) {
          console.log('[API 서버] 가장 최근 파일:', files[0].name);
        }
        
        // 임시 파일 삭제
        if (tempFileToDelete) {
          try {
            const fs = await import('fs');
            if (fs.existsSync(tempFileToDelete)) {
              fs.unlinkSync(tempFileToDelete);
              console.log('[API 서버] 임시 파일 삭제 완료:', tempFileToDelete);
            }
          } catch (e) {
            console.warn('[API 서버] 임시 파일 삭제 실패:', e.message);
          }
        }
        
        if (files.length === 0) {
          return sendJSON(res, 500, {
            success: false,
            error: '분석 결과 파일을 찾을 수 없습니다. Python 스크립트 실행을 확인하세요.',
            stderr: stderr,
            stdout: stdout.substring(0, 1000)
          });
        }
        
        // 가장 최근 JSON 파일 읽기
        const latestJsonFile = files[0].path;
        const jsonContent = fs.readFileSync(latestJsonFile, 'utf-8');
        const parsedFile = JSON.parse(jsonContent);
        
        // JSON 파일 구조 확인: { "json": {...}, "markdown": "..." } 형태일 수 있음
        const analysisResult = parsedFile.json || parsedFile;
        
        // 디버깅: lineage 데이터 확인
        console.log('[API 서버] 분석 결과 lineage 확인:', {
          fileHasJsonKey: !!parsedFile.json,
          hasLineage: !!analysisResult.lineage,
          lineageKeys: analysisResult.lineage ? Object.keys(analysisResult.lineage) : [],
          joinRelationshipsCount: analysisResult.lineage?.join_relationships?.length || 0
        });
        
        // 마크다운 파일도 찾기
        const mdFile = latestJsonFile.replace('.json', '.md');
        let markdownContent = parsedFile.markdown || null;
        if (!markdownContent && fs.existsSync(mdFile)) {
          markdownContent = fs.readFileSync(mdFile, 'utf-8');
        }
        
        // 리니지 HTML 파일 생성 또는 찾기
        let lineageHtmlPath = null;
        
        // SQL 파일 경로 확인 (리니지 시각화 생성용)
        let sqlFilePathForLineage = null;
        if (query_file) {
          if (!path.isAbsolute(query_file)) {
            sqlFilePathForLineage = join(__dirname, query_file);
          } else {
            sqlFilePathForLineage = query_file;
          }
        } else if (tempFile) {
          sqlFilePathForLineage = tempFile;
        }
        
        // 리니지 시각화 생성 스크립트 실행
        if (sqlFilePathForLineage && fs.existsSync(sqlFilePathForLineage)) {
          try {
            const lineageScript = join(__dirname, 'generate_lineage_visualization.py');
            if (fs.existsSync(lineageScript)) {
              const lineageCommand = `python "${lineageScript}" "${sqlFilePathForLineage}"`;
              console.log('[API 서버] 리니지 시각화 생성 명령어:', lineageCommand);
              
              // 동기적으로 실행하고 결과 대기
              let lineageStdout, lineageStderr;
              try {
                const lineageResult = await execAsync(lineageCommand, {
                  cwd: __dirname,
                  maxBuffer: 50 * 1024 * 1024 // 50MB로 증가
                });
                lineageStdout = lineageResult.stdout;
                lineageStderr = lineageResult.stderr;
                console.log('[API 서버] 리니지 시각화 생성 완료');
              } catch (lineageError) {
                lineageStdout = lineageError.stdout || '';
                lineageStderr = lineageError.stderr || lineageError.message || '';
                console.error('[API 서버] 리니지 시각화 생성 오류:', lineageError.message);
                console.error('[API 서버] 리니지 stderr:', lineageStderr.substring(0, 1000));
                // 리니지 생성 실패해도 분석 결과는 반환
              }
              console.log('[API 서버] 리니지 시각화 stdout:', lineageStdout.substring(0, 1000));
              if (lineageStderr) {
                console.warn('[API 서버] 리니지 시각화 stderr:', lineageStderr.substring(0, 500));
              }
              
              // stdout에서 HTML 파일 경로 추출 시도
              if (lineageStdout) {
                console.log('[API 서버] 리니지 stdout 전체:', lineageStdout);
                // 여러 패턴으로 시도
                const patterns = [
                  /시각화 HTML 저장:\s*(.+\.html)/i,
                  /HTML 저장:\s*(.+\.html)/i,
                  /시각화.*HTML.*:\s*(.+\.html)/i,
                  /시각화.*저장:\s*(.+\.html)/i,
                  /\.html/i  // .html이 포함된 라인 찾기
                ];
                
                let extractedPath = null;
                for (let i = 0; i < patterns.length; i++) {
                  const pattern = patterns[i];
                  const match = lineageStdout.match(pattern);
                  if (match && match[1]) {
                    extractedPath = match[1].trim();
                    // 따옴표 제거
                    extractedPath = extractedPath.replace(/^["']|["']$/g, '');
                    break;
                  } else if (i === 4 && match) {
                    // 마지막 패턴(.html)인 경우 라인별로 검색
                    const lines = lineageStdout.split('\n');
                    for (const line of lines) {
                      if (line.includes('.html') && (line.includes('시각화') || line.includes('HTML') || line.includes('저장'))) {
                        // "시각화 HTML 저장: 경로" 패턴 찾기
                        const pathMatch = line.match(/시각화\s+HTML\s+저장:\s*(.+\.html)/i);
                        if (pathMatch && pathMatch[1]) {
                          extractedPath = pathMatch[1].trim().replace(/^["']|["']$/g, '');
                          break;
                        }
                        // 일반적인 경로 패턴 찾기
                        const generalMatch = line.match(/([^\s]+\.html)/);
                        if (generalMatch) {
                          extractedPath = generalMatch[1].trim().replace(/^["']|["']$/g, '');
                          break;
                        }
                      }
                    }
                    if (extractedPath) break;
                  }
                }
                
                if (extractedPath) {
                  // 절대 경로를 상대 경로로 변환
                  if (path.isAbsolute(extractedPath)) {
                    lineageHtmlPath = path.relative(__dirname, extractedPath).replace(/\\/g, '/');
                  } else {
                    lineageHtmlPath = extractedPath.replace(/\\/g, '/');
                  }
                  console.log('[API 서버] stdout에서 리니지 HTML 파일 경로 추출:', {
                    원본: extractedPath,
                    변환: lineageHtmlPath
                  });
                } else {
                  console.warn('[API 서버] stdout에서 HTML 경로를 추출하지 못했습니다.');
                  console.warn('[API 서버] stdout 내용:', lineageStdout.substring(0, 2000));
                }
              }
              
              // 파일 생성 대기 (더 긴 대기 시간)
              await new Promise(resolve => setTimeout(resolve, 2000));
              
              // stdout에서 경로를 찾지 못했으면 파일 검색으로 찾기 시도
              if (!lineageHtmlPath && sqlFilePathForLineage) {
                const sqlFileDir = path.dirname(sqlFilePathForLineage);
                const sqlAnalysisDir = join(sqlFileDir, 'sql_analysis');
                if (fs.existsSync(sqlAnalysisDir)) {
                  try {
                    const files = fs.readdirSync(sqlAnalysisDir)
                      .filter(f => f.includes('_lineage_visualization_') && f.endsWith('.html'))
                      .map(f => {
                        const filePath = join(sqlAnalysisDir, f);
                        const stats = fs.statSync(filePath);
                        return {
                          name: f,
                          path: filePath,
                          time: stats.mtime.getTime()
                        };
                      })
                      .sort((a, b) => b.time - a.time);
                    
                    if (files.length > 0) {
                      const latestFile = files[0];
                      lineageHtmlPath = path.relative(__dirname, latestFile.path).replace(/\\/g, '/');
                      console.log('[API 서버] 즉시 파일 검색으로 리니지 HTML 파일 찾음:', lineageHtmlPath);
                    }
                  } catch (err) {
                    console.warn('[API 서버] 즉시 파일 검색 실패:', err.message);
                  }
                }
              }
            }
          } catch (err) {
            console.warn('[API 서버] 리니지 시각화 생성 중 오류:', err.message);
          }
        }
        
        // 리니지 HTML 파일 찾기 - stdout에서 찾지 못한 경우에만 파일 검색 수행
        if (!lineageHtmlPath) {
          const searchDirs = [
            logsDir, // logs/sql_analysis
            join(__dirname, 'queries', 'sql_analysis'), // queries/sql_analysis
          ];
          
          // SQL 파일 위치의 sql_analysis 디렉토리 추가
          if (sqlFilePathForLineage) {
            const sqlFileDir = path.dirname(sqlFilePathForLineage);
            const sqlAnalysisDir = join(sqlFileDir, 'sql_analysis');
            if (!searchDirs.includes(sqlAnalysisDir)) {
              searchDirs.push(sqlAnalysisDir);
            }
          }
          
          // temp 파일의 경우 logs/sql_analysis도 확인
          if (tempFile) {
            const tempFileDir = path.dirname(tempFile);
            const tempAnalysisDir = join(tempFileDir, 'sql_analysis');
            if (fs.existsSync(tempAnalysisDir) && !searchDirs.includes(tempAnalysisDir)) {
              searchDirs.push(tempAnalysisDir);
            }
          }
          
          console.log('[API 서버] 리니지 HTML 파일 검색 디렉토리:', searchDirs);
          
          let allHtmlFiles = [];
          for (const searchDir of searchDirs) {
            if (fs.existsSync(searchDir)) {
              try {
                const files = fs.readdirSync(searchDir)
                  .filter(f => f.includes('_lineage_visualization_') && f.endsWith('.html'))
                  .map(f => {
                    const filePath = join(searchDir, f);
                    const stats = fs.statSync(filePath);
                    return {
                      name: f,
                      path: filePath,
                      time: stats.mtime.getTime()
                    };
                  })
                  .filter(f => (now - f.time) < 120000) // 120초(2분) 이내 생성된 파일만
                  .sort((a, b) => b.time - a.time);
                
                allHtmlFiles = allHtmlFiles.concat(files);
              } catch (err) {
                console.warn(`[API 서버] 디렉토리 검색 실패 (${searchDir}):`, err.message);
              }
            }
          }
          
          // 가장 최근 파일 선택
          if (allHtmlFiles.length > 0) {
            allHtmlFiles.sort((a, b) => b.time - a.time);
            const latestFile = allHtmlFiles[0];
            lineageHtmlPath = path.relative(__dirname, latestFile.path).replace(/\\/g, '/');
            console.log('[API 서버] 파일 검색으로 리니지 HTML 파일 찾음:', lineageHtmlPath);
            console.log('[API 서버] 찾은 파일 목록:', allHtmlFiles.map(f => ({ name: f.name, time: new Date(f.time).toISOString() })));
          } else {
            console.log('[API 서버] 리니지 HTML 파일을 찾을 수 없습니다.');
            console.log('[API 서버] 검색한 디렉토리:', searchDirs.map(d => ({ dir: d, exists: fs.existsSync(d) })));
          }
        }
        
        // 리포트 객체 생성 (lineageHtmlPath가 null이어도 포함)
        // lineageHtmlPath가 있으면 API 서버를 통해 접근할 수 있도록 URL 변환
        let finalLineageHtmlPath = null;
        if (lineageHtmlPath) {
          finalLineageHtmlPath = `/api/lineage/${lineageHtmlPath}`;
          console.log('[API 서버] 리니지 경로 변환:', {
            원본: lineageHtmlPath,
            변환: finalLineageHtmlPath
          });
        } else {
          console.warn('[API 서버] lineageHtmlPath가 null입니다. 파일을 찾지 못했습니다.');
        }
        
        const reportData = {
          json: analysisResult,
          markdown: markdownContent,
          lineageHtmlPath: finalLineageHtmlPath  // 항상 포함 (null이어도)
        };
        
        console.log('[API 서버] 리포트 객체 생성:', {
          reportKeys: Object.keys(reportData),
          hasLineageHtmlPath: reportData.hasOwnProperty('lineageHtmlPath'),
          lineageHtmlPath: reportData.lineageHtmlPath,
          lineageHtmlPathType: typeof reportData.lineageHtmlPath
        });
        
        const responseData = {
          success: true,
          result: {
            structure: analysisResult.structure,
            performance: analysisResult.performance,
            complexity: analysisResult.complexity,
            security: analysisResult.security,
            optimization: analysisResult.optimization,
            lineage: analysisResult.lineage || null
          },
          report: reportData
        };
        
        // 디버깅: 응답 데이터 확인
        console.log('[API 서버] 최종 응답 데이터 확인:', {
          hasLineage: !!responseData.result.lineage,
          joinRelationshipsCount: responseData.result.lineage?.join_relationships?.length || 0,
          reportKeys: Object.keys(responseData.report),
          hasLineageHtmlPath: responseData.report.hasOwnProperty('lineageHtmlPath'),
          lineageHtmlPath: responseData.report.lineageHtmlPath,
          lineageHtmlPathType: typeof responseData.report.lineageHtmlPath,
          reportStringified: JSON.stringify(responseData.report).substring(0, 200)
        });
        
        return sendJSON(res, 200, responseData);
        
      } catch (error) {
        console.error('[API 서버] SQL 쿼리 분석 오류:', error);
        console.error('[API 서버] 오류 스택:', error.stack);
        
        // 응답이 이미 전송되었는지 확인
        if (res.headersSent) {
          console.error('[API 서버] 응답이 이미 전송되었습니다. 추가 응답 불가.');
          return;
        }
        
        // 에러 타입에 따른 처리
        let errorMessage = `쿼리 분석 중 오류가 발생했습니다: ${error.message}`;
        let statusCode = 500;
        
        if (error.message.includes('ENOENT') || error.message.includes('파일을 찾을 수 없습니다')) {
          statusCode = 404;
          errorMessage = `SQL 파일을 찾을 수 없습니다: ${error.message}`;
        } else if (error.message.includes('timeout') || error.message.includes('타임아웃') || error.code === 'TIMEOUT') {
          statusCode = 504;
          errorMessage = '쿼리 분석 타임아웃: 분석에 시간이 너무 오래 걸립니다. (5분 초과)';
        } else if (error.message.includes('ENOBUFS') || error.message.includes('maxBuffer')) {
          statusCode = 413;
          errorMessage = '분석 결과가 너무 큽니다. 쿼리를 더 작은 단위로 분할해주세요.';
        }
        
        return sendJSON(res, statusCode, {
          success: false,
          error: errorMessage,
          errorType: error.name || 'UnknownError',
          suggestion: statusCode === 504 ? '쿼리를 더 작은 단위로 분할하거나 복잡도를 줄여주세요.' : 
                     statusCode === 413 ? '큰 쿼리는 여러 개의 작은 쿼리로 나누어 분석하세요.' : 
                     '서버 로그를 확인하거나 관리자에게 문의하세요.'
        });
      }
    });
    return; // 요청 처리 완료
  }
  
  // 영향도 분석 API
  // 엔드포인트: POST /api/sql/impact-analysis
  // 기능: 특정 테이블/컬럼에 이슈 발생 시 영향받는 쿼리 분석
  else if ((req.url === '/api/sql/impact-analysis' || req.url.startsWith('/api/sql/impact-analysis')) && req.method === 'POST') {
    console.log('[API 서버] 영향도 분석 요청 수신:', req.url, req.method);
    
    // 요청 타임아웃 설정 (2분)
    req.setTimeout(120000, () => {
      if (!res.headersSent) {
        console.error('[API 서버] 영향도 분석 요청 타임아웃 (2분 초과)');
        res.writeHead(504, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: false,
          error: '요청 타임아웃: 영향도 분석에 시간이 너무 오래 걸립니다. (2분 초과)'
        }));
      }
    });
    
    let body = '';
    const maxBodySize = 10 * 1024 * 1024; // 10MB 제한
    let bodySize = 0;
    
    req.on('data', chunk => {
      bodySize += chunk.length;
      if (bodySize > maxBodySize) {
        console.error('[API 서버] 요청 본문 크기 초과:', bodySize);
        res.writeHead(413, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ 
          success: false,
          error: '요청 본문이 너무 큽니다. (10MB 초과)'
        }));
        return;
      }
      body += chunk.toString('utf-8');
    });
    
    req.on('end', async () => {
      try {
        const requestData = JSON.parse(body);
        const { query_file, query_text, target_table, target_column } = requestData;
        
        console.log('[API 서버] 영향도 분석 요청');
        console.log('[API 서버] 요청 데이터:', { query_file, has_query_text: !!query_text, target_table, target_column });
        
        if (!target_table) {
          return sendJSON(res, 400, {
            success: false,
            error: '분석 대상 테이블명을 제공해야 합니다.'
          });
        }
        
        if (!query_file && !query_text) {
          return sendJSON(res, 400, {
            success: false,
            error: 'SQL 쿼리 또는 파일 경로를 제공해야 합니다.'
          });
        }
        
        // SQL 쿼리 읽기
        const fs = await import('fs');
        const path = await import('path');
        let sqlContent = '';
        
        if (query_text) {
          sqlContent = query_text;
        } else if (query_file) {
          let filePath = query_file;
          if (!path.isAbsolute(query_file)) {
            filePath = join(__dirname, query_file);
          }
          
          if (!fs.existsSync(filePath)) {
            return sendJSON(res, 400, {
              success: false,
              error: `SQL 파일을 찾을 수 없습니다: ${query_file}`
            });
          }
          
          sqlContent = fs.readFileSync(filePath, 'utf-8');
        }
        
        // Python 스크립트 실행을 위한 명령어 구성 (영향도 분석 모드)
        const pythonScript = join(__dirname, 'test-sql-query-analyzer.py');
        
        // 임시 SQL 파일 생성
        const tempFile = join(__dirname, 'temp_impact_query_' + Date.now() + '.sql');
        fs.writeFileSync(tempFile, sqlContent, 'utf-8');
        
        // 영향도 분석 모드로 실행
        let command = `python "${pythonScript}" --impact "${tempFile}" "${target_table}"`;
        if (target_column) {
          command += ` "${target_column}"`;
        }
        
        console.log('[API 서버] 실행 명령어:', command);
        console.log('[API 서버] 영향도 분석 시작 (타겟 테이블:', target_table, ', 컬럼:', target_column || '전체', ')');
        
        const startTime = Date.now();
        let stdout, stderr;
        
        try {
          const result = await execAsync(command, {
            cwd: __dirname,
            maxBuffer: 50 * 1024 * 1024,
            timeout: 120000
          });
          stdout = result.stdout;
          stderr = result.stderr;
        } catch (execError) {
          stdout = execError.stdout || '';
          stderr = execError.stderr || execError.message || '';
          console.error('[API 서버] Python 스크립트 실행 오류:', execError.message);
          console.error('[API 서버] stderr:', stderr.substring(0, 1000));
          
          // 임시 파일 삭제
          try {
            if (fs.existsSync(tempFile)) {
              fs.unlinkSync(tempFile);
            }
          } catch (e) {}
          
          return sendJSON(res, 500, {
            success: false,
            error: `Python 스크립트 실행 오류: ${execError.message}`,
            stderr: stderr.substring(0, 1000)
          });
        }
        
        const elapsedTime = ((Date.now() - startTime) / 1000).toFixed(2);
        console.log(`[API 서버] Python 스크립트 실행 완료 (소요 시간: ${elapsedTime}초)`);
        console.log('[API 서버] stdout:', stdout.substring(0, 500));
        
        // 임시 파일 삭제
        try {
          if (fs.existsSync(tempFile)) {
            fs.unlinkSync(tempFile);
          }
        } catch (e) {}
        
        // JSON 결과 파싱
        try {
          const impactResult = JSON.parse(stdout.trim());
          
          if (!impactResult.success) {
            return sendJSON(res, 500, {
              success: false,
              error: impactResult.error || '영향도 분석 실패'
            });
          }
          
          return sendJSON(res, 200, {
            success: true,
            impact_analysis: impactResult.impact_analysis
          });
        } catch (parseError) {
          console.error('[API 서버] JSON 파싱 오류:', parseError.message);
          console.error('[API 서버] stdout:', stdout);
          
          return sendJSON(res, 500, {
            success: false,
            error: '영향도 분석 결과 파싱 오류',
            stdout: stdout.substring(0, 2000),
            stderr: stderr.substring(0, 1000)
          });
        }
        
      } catch (error) {
        console.error('[API 서버] 영향도 분석 오류:', error);
        console.error('[API 서버] 오류 스택:', error.stack);
        
        if (res.headersSent) {
          console.error('[API 서버] 응답이 이미 전송되었습니다.');
          return;
        }
        
        return sendJSON(res, 500, {
          success: false,
          error: `영향도 분석 중 오류가 발생했습니다: ${error.message}`,
          errorType: error.name || 'UnknownError'
        });
      }
    });
    return;
  } else {
    // 알 수 없는 경로에 대한 404 응답
    console.log('[API 서버] 404 Not Found:', req.method, req.url);
    res.writeHead(404, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ error: 'Not Found', path: req.url }));
  }
});

// ============================================
// 서버 시작
// ============================================

/**
 * 서버 시작
 * - 데이터베이스 초기화 후 서버 시작
 * - 지정된 포트에서 HTTP 서버 시작
 * - 콘솔에 서버 시작 메시지 출력
 */
async function startServer() {
  try {
    // 데이터베이스 초기화
    await init();
    console.log('[DB] SQLite 데이터베이스 준비 완료');
    
    // 서버 시작
    server.listen(PORT, () => {
      console.log(`백엔드 API 서버가 http://localhost:${PORT} 에서 실행 중입니다.`);
    });
    
    // 포트 충돌 에러 처리
    server.on('error', (error) => {
      if (error.code === 'EADDRINUSE') {
        console.error(`[서버 시작 오류] 포트 ${PORT}가 이미 사용 중입니다.`);
        console.error(`다음 명령어로 포트를 사용하는 프로세스를 확인하세요:`);
        console.error(`  netstat -ano | findstr :${PORT}`);
        console.error(`또는 start-servers.bat를 실행하면 자동으로 포트를 정리합니다.`);
        process.exit(1);
      } else {
        console.error('[서버 시작 오류]:', error);
        process.exit(1);
      }
    });
  } catch (error) {
    console.error('[서버 시작 오류]:', error);
    process.exit(1);
  }
}

startServer();


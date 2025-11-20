/**
 * Vite 설정 파일
 * 
 * 역할:
 * - Vue 앱 개발 서버 설정
 * - 프록시 설정 (Vue 앱 → 백엔드 API 서버)
 * 
 * 프록시 설정:
 * - /api/* 경로로 요청하면 자동으로 http://localhost:3001로 프록시
 * - 이를 통해 CORS 문제를 해결하고 백엔드 API 서버와 통신
 * 
 * 참고:
 * - changeOrigin: true - 호스트 헤더를 타겟 URL로 변경
 * - secure: false - SSL 인증서 검증 비활성화 (개발 환경)
 * - ws: true - WebSocket 프록시 지원
 * - configure: 에러 핸들러 추가
 */

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  // Vue 플러그인 설정
  plugins: [vue()],
  
  // 개발 서버 설정
  server: {
    // 포트 명시적 설정 (항상 5173 사용)
    port: 5173,
    strictPort: true, // 포트가 사용 중이면 에러 발생 (자동 변경 방지)
    host: true, // 네트워크에서 접근 가능하도록 설정
    
    // 프록시 설정
    // - Vue 앱에서 /api/* 경로로 요청하면 백엔드 API 서버로 프록시
    proxy: {
      '/api': {
        target: 'http://localhost:3001', // 백엔드 API 서버 주소
        changeOrigin: true, // 호스트 헤더를 타겟 URL로 변경
        secure: false, // SSL 인증서 검증 비활성화 (개발 환경)
        ws: true, // WebSocket 프록시 지원
        // API 서버가 없을 때 에러 처리 개선
        configure: (proxy, _options) => {
          proxy.on('error', (err, _req, _res) => {
            console.log('프록시 에러:', err.message);
            console.log('💡 해결 방법: API 서버를 실행하세요 - npm run api-server');
          });
          proxy.on('proxyReq', (proxyReq, req, _res) => {
            console.log(`[프록시] ${req.method} ${req.url} → http://localhost:3001${req.url}`);
          });
        },
        // 연결 실패 시 재시도 비활성화 (에러를 빠르게 표시)
        timeout: 5000,
      }
    }
  }
})




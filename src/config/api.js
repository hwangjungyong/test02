/**
 * API 설정 파일
 * 환경에 따라 다른 API URL 사용
 */

// 환경 변수에서 API URL 가져오기 (Docker 환경 변수 지원)
const getApiBaseUrl = () => {
  // 환경 변수에서 우선 가져오기 (Docker, 프로덕션 환경)
  if (import.meta.env.VITE_API_BASE_URL) {
    return import.meta.env.VITE_API_BASE_URL
  }
  
  // 개발 환경에서는 API 서버 URL 직접 사용
  if (import.meta.env.DEV) {
    return 'http://localhost:3001' // API 서버 포트
  }
  
  // 프로덕션 기본값
  return 'http://localhost:3001'
}

export const API_BASE_URL = getApiBaseUrl()

// API 엔드포인트 헬퍼
export const getApiUrl = (endpoint) => {
  if (endpoint.startsWith('http')) {
    return endpoint
  }
  
  // 상대 경로인 경우
  if (endpoint.startsWith('/')) {
    return API_BASE_URL ? `${API_BASE_URL}${endpoint}` : endpoint
  }
  
  // 상대 경로가 아닌 경우
  return API_BASE_URL ? `${API_BASE_URL}/${endpoint}` : `/${endpoint}`
}


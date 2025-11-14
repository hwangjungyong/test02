/**
 * API 호출 기본 함수
 * 공통 에러 처리 및 응답 파싱
 */

import { getApiUrl } from '../config/api.js'

/**
 * 기본 API 요청 함수
 * @param {string} endpoint - API 엔드포인트
 * @param {object} options - fetch 옵션
 * @returns {Promise} API 응답
 */
export async function apiRequest(endpoint, options = {}) {
  const url = getApiUrl(endpoint)
  
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }

  // 인증 토큰 추가
  const token = localStorage.getItem('token')
  if (token) {
    defaultOptions.headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const response = await fetch(url, {
      ...defaultOptions,
      ...options,
      headers: {
        ...defaultOptions.headers,
        ...options.headers
      }
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.message || errorData.error || `HTTP error! status: ${response.status}`)
    }

    return await response.json()
  } catch (error) {
    console.error(`[API] ${endpoint} 요청 실패:`, error)
    throw error
  }
}

/**
 * GET 요청
 * @param {string} endpoint - API 엔드포인트
 * @param {object} params - 쿼리 파라미터
 * @returns {Promise} API 응답
 */
export async function get(endpoint, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${endpoint}?${queryString}` : endpoint
  return apiRequest(url, { method: 'GET' })
}

/**
 * POST 요청
 * @param {string} endpoint - API 엔드포인트
 * @param {object} data - 요청 본문 데이터
 * @returns {Promise} API 응답
 */
export async function post(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

/**
 * PUT 요청
 * @param {string} endpoint - API 엔드포인트
 * @param {object} data - 요청 본문 데이터
 * @returns {Promise} API 응답
 */
export async function put(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

/**
 * DELETE 요청
 * @param {string} endpoint - API 엔드포인트
 * @returns {Promise} API 응답
 */
export async function del(endpoint) {
  return apiRequest(endpoint, { method: 'DELETE' })
}


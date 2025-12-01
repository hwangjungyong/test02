/**
 * 공통 API 요청 서비스
 */
import { getApiUrl } from '../config/api.js'

export async function apiRequest(endpoint, options = {}) {
  const url = getApiUrl(endpoint)

  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers
    }
  }

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

export async function get(endpoint, params = {}) {
  const queryString = new URLSearchParams(params).toString()
  const url = queryString ? `${endpoint}?${queryString}` : endpoint
  return apiRequest(url, { method: 'GET' })
}

export async function post(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'POST',
    body: JSON.stringify(data)
  })
}

export async function put(endpoint, data = {}) {
  return apiRequest(endpoint, {
    method: 'PUT',
    body: JSON.stringify(data)
  })
}

export async function del(endpoint) {
  return apiRequest(endpoint, { method: 'DELETE' })
}


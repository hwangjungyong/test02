/**
 * 사용자 관리 서비스
 * 사용자 관련 API 호출 통합
 */

import { getApiUrl } from '../../../config/api.js'
import { useAuthStore } from '../../../stores/auth.js'

/**
 * 사용자 프로필 조회
 */
export async function getUserProfile() {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch('/api/user/profile', {
    headers: {
      'Authorization': `Bearer ${authStore.token}`
    }
  })

  if (!response.ok) {
    if (response.status === 404) {
      throw new Error('API 엔드포인트를 찾을 수 없습니다. API 서버를 재시작해주세요.')
    } else if (response.status === 401) {
      authStore.logout()
      throw new Error('인증이 필요합니다. 다시 로그인해주세요.')
    }
    throw new Error(`서버 오류 (${response.status})`)
  }

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '프로필 정보를 불러오는데 실패했습니다.')
  }

  return data.user
}

/**
 * 사용자 프로필 수정
 */
export async function updateUserProfile(profileData) {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch('/api/user/profile', {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`
    },
    body: JSON.stringify(profileData)
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '프로필 수정에 실패했습니다.')
  }

  // Auth store 업데이트
  authStore.user = data.user
  localStorage.setItem('authUser', JSON.stringify(data.user))

  return data.user
}

/**
 * 사용자 데이터 조회
 */
export async function getUserData() {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch('/api/user/data', {
    headers: {
      'Authorization': `Bearer ${authStore.token}`
    }
  })

  if (!response.ok) {
    throw new Error(`데이터 로드 실패: ${response.status}`)
  }

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '데이터를 불러오는데 실패했습니다.')
  }

  return {
    data: data.data,
    summary: data.data.summary || { newsCount: 0, radioSongsCount: 0, booksCount: 0 }
  }
}

/**
 * API 키 목록 조회
 */
export async function getApiKeys() {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch('/api/api-keys', {
    headers: {
      'Authorization': `Bearer ${authStore.token}`
    }
  })

  if (!response.ok) {
    throw new Error(`API 키 목록 로드 실패: ${response.status}`)
  }

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || 'API 키 목록을 불러오는데 실패했습니다.')
  }

  return data.apiKeys || []
}

/**
 * API 키 생성
 */
export async function createApiKey(apiKeyData) {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch('/api/api-keys', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`
    },
    body: JSON.stringify({
      name: apiKeyData.name,
      description: apiKeyData.description || null,
      expiresInDays: apiKeyData.expiresInDays ? parseInt(apiKeyData.expiresInDays) : null
    })
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || 'API 키 생성에 실패했습니다.')
  }

  return data.apiKey
}

/**
 * API 키 삭제
 */
export async function deleteApiKey(keyId) {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch(`/api/api-keys/${keyId}`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${authStore.token}`
    }
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || 'API 키 삭제에 실패했습니다.')
  }

  return true
}

/**
 * API 키 활성화/비활성화
 */
export async function toggleApiKey(keyId, isActive) {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch(`/api/api-keys/${keyId}/toggle`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${authStore.token}`
    },
    body: JSON.stringify({ isActive })
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || 'API 키 상태 변경에 실패했습니다.')
  }

  return true
}

/**
 * DB 스키마 조회
 */
export async function getDbSchema() {
  const response = await fetch(getApiUrl('/api/db/schema'))

  if (!response.ok) {
    const errorText = await response.text()
    let errorData
    try {
      errorData = JSON.parse(errorText)
    } catch {
      errorData = { error: errorText || `HTTP ${response.status} ${response.statusText}` }
    }
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '스키마를 불러올 수 없습니다.')
  }

  return data
}

/**
 * Docker 상태 조회
 */
export async function getDockerStatus() {
  const response = await fetch('/api/docker/status')

  if (!response.ok) {
    const errorText = await response.text()
    let errorData
    try {
      errorData = JSON.parse(errorText)
    } catch {
      errorData = { error: errorText || `HTTP ${response.status} ${response.statusText}` }
    }
    throw new Error(errorData.error || `HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || 'Docker 상태를 불러올 수 없습니다.')
  }

  return data
}

/**
 * Docker 컨테이너 시작
 */
export async function startDockerContainers() {
  const response = await fetch('/api/docker/start', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '컨테이너 시작에 실패했습니다.')
  }

  return data.message || '컨테이너가 시작되었습니다.'
}

/**
 * Docker 컨테이너 중지
 */
export async function stopDockerContainers() {
  const response = await fetch('/api/docker/stop', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '컨테이너 중지에 실패했습니다.')
  }

  return data.message || '컨테이너가 중지되었습니다.'
}

/**
 * Docker 컨테이너 재시작
 */
export async function restartDockerContainers() {
  const response = await fetch('/api/docker/restart', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '컨테이너 재시작에 실패했습니다.')
  }

  return data.message || '컨테이너가 재시작되었습니다.'
}

/**
 * 에러 로그 조회
 */
export async function getErrorLogs(filters = {}) {
  const params = new URLSearchParams()
  if (filters.system_type) params.append('system_type', filters.system_type)
  if (filters.severity) params.append('severity', filters.severity)
  if (filters.error_type) params.append('error_type', filters.error_type)
  if (filters.start_date) params.append('start_date', filters.start_date)
  if (filters.end_date) params.append('end_date', filters.end_date)
  params.append('limit', '100')

  const response = await fetch(getApiUrl(`/api/error-log/history?${params.toString()}`))

  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`)
  }

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '에러 로그를 불러올 수 없습니다.')
  }

  return data.result || []
}

/**
 * 계정 삭제
 */
export async function deleteAccount() {
  const authStore = useAuthStore()
  if (!authStore.token) {
    throw new Error('로그인이 필요합니다.')
  }

  const response = await fetch('/api/user/account', {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${authStore.token}`
    }
  })

  const data = await response.json()
  if (!data.success) {
    throw new Error(data.error || '계정 삭제에 실패했습니다.')
  }

  return true
}


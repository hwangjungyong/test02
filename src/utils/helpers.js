/**
 * 공통 유틸리티 함수
 */

/**
 * 날짜 포맷팅 함수
 * @param {string} dateString - 포맷팅할 날짜 문자열
 * @returns {string} 포맷팅된 날짜 문자열
 */
export function formatDate(dateString) {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}

/**
 * 간단한 날짜 포맷팅 (시간 제외)
 * @param {string} dateString - 포맷팅할 날짜 문자열
 * @returns {string} 포맷팅된 날짜 문자열
 */
export function formatDateShort(dateString) {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    })
  } catch (error) {
    return dateString
  }
}

/**
 * URL 인코딩 헬퍼
 * @param {string} str - 인코딩할 문자열
 * @returns {string} 인코딩된 문자열
 */
export function encodeUrl(str) {
  return encodeURIComponent(str || '')
}

/**
 * 에러 메시지 추출
 * @param {Error|any} error - 에러 객체
 * @returns {string} 에러 메시지
 */
export function getErrorMessage(error) {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return '알 수 없는 오류가 발생했습니다.'
}

/**
 * 디바운스 함수
 * @param {Function} func - 실행할 함수
 * @param {number} wait - 대기 시간 (ms)
 * @returns {Function} 디바운스된 함수
 */
export function debounce(func, wait = 300) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 스로틀 함수
 * @param {Function} func - 실행할 함수
 * @param {number} limit - 제한 시간 (ms)
 * @returns {Function} 스로틀된 함수
 */
export function throttle(func, limit = 300) {
  let inThrottle
  return function executedFunction(...args) {
    if (!inThrottle) {
      func.apply(this, args)
      inThrottle = true
      setTimeout(() => inThrottle = false, limit)
    }
  }
}


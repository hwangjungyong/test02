/**
 * 뉴스 관련 API 서비스
 */

import { get } from './api.js'

/**
 * AI 뉴스 검색
 * @param {string} keyword - 검색 키워드
 * @returns {Promise} 뉴스 기사 목록
 */
export async function searchAINews(keyword) {
  if (!keyword || keyword.trim() === '') {
    throw new Error('검색 키워드를 입력해주세요.')
  }

  const searchKeywordEncoded = encodeURIComponent(keyword.trim())
  return get('/api/news', { q: searchKeywordEncoded })
}

/**
 * 최신 AI 뉴스 가져오기
 * @returns {Promise} 최신 뉴스 기사 목록
 */
export async function fetchLatestAINews() {
  return get('/api/news', { q: 'AI OR 인공지능 OR 머신러닝 OR 딥러닝' })
}

/**
 * 경제 뉴스 검색
 * @param {string} keyword - 검색 키워드 (선택사항)
 * @returns {Promise} 경제 뉴스 기사 목록
 */
export async function searchEconomyNews(keyword = '') {
  const params = keyword ? { q: keyword } : {}
  return get('/api/news/economy', params)
}

/**
 * 최신 경제 뉴스 가져오기
 * @returns {Promise} 최신 경제 뉴스 기사 목록
 */
export async function fetchLatestEconomyNews() {
  return get('/api/news/economy')
}

/**
 * 뉴스 저장
 * @param {object} newsData - 저장할 뉴스 데이터
 * @returns {Promise} 저장 결과
 */
export async function saveNews(newsData) {
  const { post } = await import('./api.js')
  return post('/api/user/news', newsData)
}


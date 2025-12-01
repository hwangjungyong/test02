/**
 * 사용자 데이터 관리 Composable
 */

import { ref } from 'vue'
import { getUserData } from '../services/userService.js'

export function useUserData() {
  const userData = ref({ news: [], radioSongs: [], books: [] })
  const userDataSummary = ref({ newsCount: 0, radioSongsCount: 0, booksCount: 0 })
  const loading = ref(false)
  const error = ref('')

  /**
   * 사용자 데이터 요약 로드
   */
  async function loadDataSummary() {
    loading.value = true
    error.value = ''

    try {
      const result = await getUserData()
      userData.value = result.data
      userDataSummary.value = result.summary
    } catch (err) {
      console.error('데이터 로드 오류:', err)
      error.value = err.message || '데이터를 불러오는데 실패했습니다.'
    } finally {
      loading.value = false
    }
  }

  return {
    userData,
    userDataSummary,
    loading,
    error,
    loadDataSummary
  }
}


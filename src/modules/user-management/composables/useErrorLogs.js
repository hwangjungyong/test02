/**
 * 에러 로그 관리 Composable
 */

import { ref } from 'vue'
import { getErrorLogs } from '../services/userService.js'

export function useErrorLogs() {
  const errorLogs = ref([])
  const loading = ref(false)
  const error = ref('')
  const filters = ref({
    system_type: '',
    severity: '',
    error_type: '',
    start_date: '',
    end_date: ''
  })

  /**
   * 에러 로그 로드
   */
  async function loadLogs() {
    loading.value = true
    error.value = ''

    try {
      errorLogs.value = await getErrorLogs(filters.value)
    } catch (err) {
      console.error('[에러 로그 로드] 오류:', err)
      error.value = err.message || '에러 로그를 불러오는 중 오류가 발생했습니다.'
    } finally {
      loading.value = false
    }
  }

  /**
   * 필터 초기화
   */
  function resetFilters() {
    filters.value = {
      system_type: '',
      severity: '',
      error_type: '',
      start_date: '',
      end_date: ''
    }
    loadLogs()
  }

  return {
    errorLogs,
    loading,
    error,
    filters,
    loadLogs,
    resetFilters
  }
}


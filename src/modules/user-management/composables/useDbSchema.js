/**
 * DB 스키마 관리 Composable
 */

import { ref } from 'vue'
import { getDbSchema } from '../services/userService.js'

export function useDbSchema() {
  const dbSchema = ref(null)
  const loading = ref(false)
  const error = ref('')

  /**
   * DB 스키마 로드
   */
  async function loadSchema() {
    loading.value = true
    error.value = ''

    try {
      dbSchema.value = await getDbSchema()
    } catch (err) {
      console.error('[스키마 로드] 상세 오류:', err)
      
      let errorMessage = '스키마를 불러오는 중 오류가 발생했습니다.'
      
      if (err.message) {
        errorMessage += `\n\n오류 내용: ${err.message}`
      }
      
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        errorMessage += '\n\n서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인하세요.'
        errorMessage += '\n확인 방법: http://localhost:3001/api/db/schema'
      }
      
      error.value = errorMessage
    } finally {
      loading.value = false
    }
  }

  return {
    dbSchema,
    loading,
    error,
    loadSchema
  }
}


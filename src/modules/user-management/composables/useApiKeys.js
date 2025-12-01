/**
 * API 키 관리 Composable
 */

import { ref, computed } from 'vue'
import { getApiKeys, createApiKey, deleteApiKey, toggleApiKey } from '../services/userService.js'

export function useApiKeys() {
  const apiKeys = ref([])
  const loading = ref(false)
  const creating = ref(false)
  const error = ref('')
  const createdApiKey = ref(null)
  const showCreateModal = ref(false)
  const newApiKeyForm = ref({
    name: '',
    description: '',
    expiresInDays: null
  })

  // 활성화된 API 키 (예제에 사용)
  const activeApiKey = computed(() => {
    const active = apiKeys.value.find(k => k.isActive)
    return active ? active.apiKey : null
  })

  /**
   * API 키 목록 로드
   */
  async function loadApiKeys() {
    loading.value = true
    error.value = ''

    try {
      apiKeys.value = await getApiKeys()
    } catch (err) {
      console.error('API 키 목록 로드 오류:', err)
      error.value = err.message || 'API 키 목록을 불러오는데 실패했습니다.'
    } finally {
      loading.value = false
    }
  }

  /**
   * API 키 생성
   */
  async function createKey() {
    creating.value = true
    error.value = ''
    createdApiKey.value = null

    try {
      const newKey = await createApiKey(newApiKeyForm.value)
      createdApiKey.value = newKey
      // 목록 새로고침
      await loadApiKeys()
    } catch (err) {
      console.error('API 키 생성 오류:', err)
      error.value = err.message || 'API 키 생성에 실패했습니다.'
    } finally {
      creating.value = false
    }
  }

  /**
   * API 키 삭제
   */
  async function removeApiKey(keyId) {
    if (!confirm('정말 이 API 키를 삭제하시겠습니까?')) {
      return
    }

    try {
      await deleteApiKey(keyId)
      await loadApiKeys()
    } catch (err) {
      console.error('API 키 삭제 오류:', err)
      alert(err.message || 'API 키 삭제에 실패했습니다.')
    }
  }

  /**
   * API 키 활성화/비활성화
   */
  async function toggleKey(keyId, isActive) {
    try {
      await toggleApiKey(keyId, isActive)
      await loadApiKeys()
    } catch (err) {
      console.error('API 키 토글 오류:', err)
      alert(err.message || 'API 키 상태 변경에 실패했습니다.')
    }
  }

  /**
   * API 키 생성 모달 열기
   */
  function openCreateModal() {
    showCreateModal.value = true
    newApiKeyForm.value = {
      name: '',
      description: '',
      expiresInDays: null
    }
    createdApiKey.value = null
    error.value = ''
  }

  /**
   * API 키 생성 모달 닫기
   */
  function closeCreateModal() {
    showCreateModal.value = false
    createdApiKey.value = null
    newApiKeyForm.value = {
      name: '',
      description: '',
      expiresInDays: null
    }
  }

  /**
   * API 키 복사
   */
  function copyApiKey(apiKey) {
    navigator.clipboard.writeText(apiKey).then(() => {
      alert('API 키가 클립보드에 복사되었습니다!')
    }).catch(() => {
      alert('복사에 실패했습니다. 수동으로 복사해주세요.')
    })
  }

  /**
   * 코드 예제 복사
   */
  function copyCode(code) {
    // HTML 엔티티를 실제 문자로 변환
    const decodedCode = code.replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
    navigator.clipboard.writeText(decodedCode).then(() => {
      alert('코드가 클립보드에 복사되었습니다!')
    }).catch(() => {
      alert('복사에 실패했습니다. 수동으로 복사해주세요.')
    })
  }

  return {
    apiKeys,
    loading,
    creating,
    error,
    createdApiKey,
    showCreateModal,
    newApiKeyForm,
    activeApiKey,
    loadApiKeys,
    createKey,
    removeApiKey,
    toggleKey,
    openCreateModal,
    closeCreateModal,
    copyApiKey,
    copyCode
  }
}


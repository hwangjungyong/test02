<template>
  <div class="tab-content">
    <div class="delete-warning">
      <h3>⚠️ 계정 삭제</h3>
      <p>계정을 삭제하면 다음 정보가 모두 삭제됩니다:</p>
      <ul>
        <li>프로필 정보</li>
        <li>저장된 뉴스 ({{ userDataSummary.newsCount }}건)</li>
        <li>저장된 라디오 노래 ({{ userDataSummary.radioSongsCount }}건)</li>
        <li>저장된 도서 ({{ userDataSummary.booksCount }}건)</li>
      </ul>
      <p class="warning-text">이 작업은 되돌릴 수 없습니다!</p>
      <div v-if="error" class="error-message">
        {{ error }}
      </div>
      <div class="form-actions">
        <button 
          @click="handleDeleteAccount" 
          class="btn btn-danger" 
          :disabled="deleting"
        >
          {{ deleting ? '삭제 중...' : '계정 삭제' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { deleteAccount } from '../../services/userService.js'
import { useAuthStore } from '../../../../stores/auth.js'
import { useUserData } from '../../composables/useUserData.js'

const emit = defineEmits(['close'])

const authStore = useAuthStore()
const { userDataSummary } = useUserData()

const deleting = ref(false)
const error = ref('')

async function handleDeleteAccount() {
  if (!confirm('정말 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
    return
  }
  
  deleting.value = true
  error.value = ''
  
  try {
    await deleteAccount()
    alert('계정이 삭제되었습니다.')
    authStore.logout()
    emit('close')
  } catch (err) {
    console.error('계정 삭제 오류:', err)
    error.value = err.message || '계정 삭제에 실패했습니다.'
  } finally {
    deleting.value = false
  }
}
</script>


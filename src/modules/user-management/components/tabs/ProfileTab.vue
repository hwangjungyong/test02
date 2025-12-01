<template>
  <div class="tab-content">
    <div v-if="loading" class="loading">
      <p>프로필 정보를 불러오는 중...</p>
    </div>
    <div v-else>
      <form @submit.prevent="handleUpdateProfile" class="auth-form">
        <div class="form-group">
          <label>이메일</label>
          <input 
            v-model="profileForm.email" 
            type="email" 
            placeholder="이메일을 입력하세요"
            required
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label>이름</label>
          <input 
            v-model="profileForm.name" 
            type="text" 
            placeholder="이름을 입력하세요"
            class="form-input"
          />
        </div>
        <div class="form-group">
          <label>가입일</label>
          <input 
            :value="formatDate(userProfile?.createdAt)" 
            type="text" 
            disabled
            class="form-input"
          />
        </div>
        <div v-if="error" class="error-message">
          {{ error }}
        </div>
        <div v-if="success" class="success-message">
          {{ success }}
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="updating">
            {{ updating ? '수정 중...' : '프로필 수정' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserProfile } from '../../composables/useUserProfile.js'
import { formatDate } from '../../../../utils/helpers.js'

const {
  userProfile,
  profileForm,
  loading,
  updating,
  error,
  success,
  loadProfile,
  updateProfile
} = useUserProfile()

function handleUpdateProfile() {
  updateProfile()
}

onMounted(() => {
  loadProfile()
})
</script>


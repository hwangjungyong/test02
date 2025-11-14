<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
    <div class="modal-content auth-modal" @click.stop>
      <div class="modal-header">
        <h2>📝 회원가입</h2>
        <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="handleSubmit" class="auth-form">
          <div class="form-group">
            <label>이메일</label>
            <input 
              v-model="form.email" 
              type="email" 
              placeholder="이메일을 입력하세요"
              required
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>비밀번호</label>
            <input 
              v-model="form.password" 
              type="password" 
              placeholder="비밀번호를 입력하세요 (최소 6자)"
              required
              minlength="6"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>이름 (선택사항)</label>
            <input 
              v-model="form.name" 
              type="text" 
              placeholder="이름을 입력하세요"
              class="form-input"
            />
          </div>
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="isLoading">
              {{ isLoading ? '가입 중...' : '회원가입' }}
            </button>
            <button type="button" @click="$emit('update:modelValue', false)" class="btn btn-secondary">
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useAuthStore } from '../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'success'])

const authStore = useAuthStore()
const form = ref({ email: '', password: '', name: '' })
const error = ref('')

const isLoading = computed(() => authStore.isLoading)

async function handleSubmit() {
  error.value = ''
  const result = await authStore.signup(
    form.value.email, 
    form.value.password, 
    form.value.name
  )
  
  if (result.success) {
    emit('update:modelValue', false)
    form.value = { email: '', password: '', name: '' }
    emit('success', '회원가입 성공!')
  } else {
    error.value = result.error || '회원가입에 실패했습니다.'
  }
}
</script>


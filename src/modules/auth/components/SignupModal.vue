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
          <div v-if="error" class="error-message" style="white-space: pre-line;">
            {{ error }}
            <div v-if="error.includes('서버에 연결할 수 없습니다')" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #ffcdd2; font-size: 12px;">
              <strong>해결 방법:</strong>
              <ol style="margin: 8px 0; padding-left: 20px;">
                <li>터미널에서 프로젝트 폴더로 이동</li>
                <li><code>npm run api-server</code> 실행</li>
                <li>또는 <code>start-dev.bat</code> 실행</li>
                <li>서버가 시작되면 다시 회원가입 시도</li>
              </ol>
            </div>
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
import { useAuthStore } from '../../../stores/auth.js'

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

<style scoped>
/* 모달 오버레이 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 모달 컨텐츠 */
.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 400px;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.auth-modal {
  max-width: 400px;
}

/* 모달 헤더 */
.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px 12px 0 0;
}

.modal-header h2 {
  color: white;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
  font-weight: 300;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

/* 모달 바디 */
.modal-body {
  padding: 24px;
  overflow-y: auto;
}

/* 폼 스타일 */
.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.form-input {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
  width: 100%;
  box-sizing: border-box;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

/* 버튼 스타일 */
.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

/* 에러 메시지 */
.error-message {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #c62828;
}

/* 반응형 디자인 */
@media (max-width: 480px) {
  .modal-content {
    max-width: 100%;
    margin: 10px;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .btn {
    width: 100%;
  }
}
</style>


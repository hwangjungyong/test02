<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
    <div class="modal-content api-key-modal" @click.stop>
      <div class="modal-header">
        <h2>🔑 새 API 키 생성</h2>
        <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
      </div>
      <div class="modal-body">
        <form @submit.prevent="$emit('create')" class="auth-form">
          <div class="form-group">
            <label>이름</label>
            <input 
              v-model="form.name" 
              type="text" 
              placeholder="예: 프로덕션 키, 개발 키"
              required
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>설명 (선택사항)</label>
            <textarea 
              v-model="form.description" 
              placeholder="이 API 키의 용도를 설명해주세요"
              class="form-input"
              rows="3"
            ></textarea>
          </div>
          <div class="form-group">
            <label>만료일 (선택사항)</label>
            <input 
              v-model.number="form.expiresInDays" 
              type="number" 
              placeholder="예: 30 (30일 후 만료)"
              min="1"
              class="form-input"
            />
            <small>비워두면 만료되지 않습니다.</small>
          </div>
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
          <div v-if="createdApiKey" class="success-message">
            <p><strong>✅ API 키가 생성되었습니다!</strong></p>
            <div class="api-key-display">
              <code>{{ createdApiKey.apiKey }}</code>
              <button @click="$emit('copy', createdApiKey.apiKey)" class="btn btn-sm btn-primary">
                복사
              </button>
            </div>
            <p class="warning-text">⚠️ 이 API 키는 이번에만 표시됩니다. 안전한 곳에 저장하세요!</p>
          </div>
          <div class="form-actions">
            <button type="submit" class="btn btn-primary" :disabled="creating">
              {{ creating ? '생성 중...' : 'API 키 생성' }}
            </button>
            <button type="button" @click="$emit('update:modelValue', false)" class="btn btn-secondary">
              {{ createdApiKey ? '닫기' : '취소' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: Boolean,
  error: String,
  creating: Boolean,
  createdApiKey: Object,
  form: Object
})

defineEmits(['update:modelValue', 'create', 'close', 'copy'])
</script>


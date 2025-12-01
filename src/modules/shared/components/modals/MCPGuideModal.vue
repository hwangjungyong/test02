<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
    <div class="modal-content" @click.stop>
      <div class="modal-header">
        <h2>{{ currentGuideType === 'python' ? 'Python MCP 서버 가이드' : 'MCP 서버 가이드' }}</h2>
        <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
      </div>
      <div class="modal-body">
        <div v-if="isLoading" class="loading">
          <p>가이드를 불러오는 중...</p>
        </div>
        <div v-else v-html="markdownContent"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { marked } from 'marked'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  guideType: {
    type: String,
    default: 'nodejs'
  }
})

defineEmits(['update:modelValue'])

const currentGuideType = ref(props.guideType)
const markdownContent = ref('')
const isLoading = ref(false)

// MCP 가이드 로드
const loadMCPGuide = async (type) => {
  isLoading.value = true
  
  try {
    let fileName
    if (type === 'python') {
      fileName = encodeURIComponent('MCP_가이드_보기_(Python).md')
    } else {
      fileName = encodeURIComponent('MCP_가이드.md')
    }
    
    const response = await fetch(`/${fileName}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const text = await response.text()
    
    if (!text || text.trim() === '') {
      throw new Error('파일 내용이 비어있습니다.')
    }
    
    // 마크다운을 HTML로 변환
    markdownContent.value = marked.parse(text)
  } catch (err) {
    console.error('MCP 가이드 로드 오류:', err)
    markdownContent.value = `
      <div style="padding: 20px; text-align: center;">
        <h3 style="color: #f44336;">⚠️ 가이드 파일을 불러올 수 없습니다</h3>
        <p>오류: ${err.message}</p>
        <p style="margin-top: 20px; color: #666;">
          파일 경로를 확인하거나 개발자 콘솔을 확인해주세요.
        </p>
      </div>
    `
  } finally {
    isLoading.value = false
  }
}

// 모달이 열릴 때 가이드 로드
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    currentGuideType.value = props.guideType
    // 이미 로드된 내용이 있으면 다시 로드하지 않음
    if (!markdownContent.value || currentGuideType.value !== props.guideType) {
      loadMCPGuide(props.guideType)
    }
  } else {
    // 모달이 닫힐 때 내용 초기화 (다음에 다시 로드되도록)
    markdownContent.value = ''
    currentGuideType.value = 'nodejs'
  }
})

watch(() => props.guideType, (newType) => {
  if (props.modelValue && currentGuideType.value !== newType) {
    currentGuideType.value = newType
    loadMCPGuide(newType)
  }
})
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}
</style>


<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
    <div class="modal-content docs-library-modal" @click.stop style="max-width: 1200px; max-height: 90vh;">
      <div class="modal-header">
        <h2>📚 가이드 문서</h2>
        <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
      </div>
      <div class="modal-body" style="overflow-y: auto; max-height: calc(90vh - 120px);">
        <!-- 문서 목록 -->
        <div v-if="docsLoading" class="loading">
          <p>문서 목록을 불러오는 중...</p>
        </div>
        
        <div v-else-if="docsError" class="error-message">
          {{ docsError }}
        </div>
        
        <div v-else-if="docsList && docsList.length > 0" class="docs-list">
          <div class="docs-grid" style="display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 16px;">
            <div 
              v-for="doc in docsList" 
              :key="doc.name"
              @click="$emit('openDoc', doc)"
              class="doc-card"
              style="padding: 16px; border: 1px solid #ddd; border-radius: 8px; cursor: pointer; background: white; transition: all 0.2s;"
              @mouseover="$event.currentTarget.style.boxShadow = '0 4px 8px rgba(0,0,0,0.1)'"
              @mouseleave="$event.currentTarget.style.boxShadow = 'none'"
            >
              <h3 style="margin: 0 0 8px 0; color: #333; font-size: 16px;">
                {{ doc.title }}
              </h3>
              <div style="font-size: 12px; color: #666; margin-bottom: 8px;">
                <div>📄 {{ doc.name }}</div>
                <div style="margin-top: 4px;">
                  📊 {{ formatFileSize(doc.size) }}
                </div>
                <div style="margin-top: 4px;">
                  📅 {{ formatDate(doc.modified) }}
                </div>
              </div>
              <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #eee;">
                <span style="color: #2196f3; font-size: 12px; font-weight: bold;">클릭하여 보기 →</span>
              </div>
            </div>
          </div>
        </div>
        
        <div v-else class="no-docs" style="padding: 40px; text-align: center; color: #666;">
          <p>문서가 없습니다.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

defineEmits(['update:modelValue', 'openDoc'])

const docsList = ref([])
const docsLoading = ref(false)
const docsError = ref('')

// 파일 크기 포맷팅
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}

// 날짜 포맷팅
const formatDate = (dateString) => {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch {
    return dateString
  }
}

// 문서 목록 로드
const loadDocsList = async () => {
  docsLoading.value = true
  docsError.value = ''
  
  try {
    const response = await fetch('/api/docs/list')
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (data.success) {
      docsList.value = data.docs || []
      docsError.value = ''
    } else {
      docsError.value = data.error || '문서 목록을 불러올 수 없습니다.'
    }
  } catch (error) {
    console.error('[문서 목록 로드] 오류:', error)
    docsError.value = `문서 목록을 불러오는 중 오류가 발생했습니다: ${error.message}`
  } finally {
    docsLoading.value = false
  }
}

// 모달이 열릴 때 문서 목록 로드
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    loadDocsList()
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

.loading, .error-message {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error-message {
  color: #f44336;
}

.docs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.doc-card {
  transition: transform 0.2s, box-shadow 0.2s;
}

.doc-card:hover {
  transform: translateY(-2px);
}

.no-docs {
  padding: 40px;
  text-align: center;
  color: #666;
}
</style>


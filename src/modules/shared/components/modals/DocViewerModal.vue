<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)" style="z-index: 2000;">
    <div class="modal-content doc-viewer-modal" @click.stop style="max-width: 1000px; max-height: 90vh; z-index: 2001;">
      <div class="modal-header">
        <h2>{{ currentDoc?.title || '문서 보기' }}</h2>
        <div style="display: flex; gap: 8px;">
          <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
        </div>
      </div>
      <div class="modal-body" style="overflow-y: auto; max-height: calc(90vh - 120px);">
        <div v-if="docContentLoading" class="loading">
          <p>문서를 불러오는 중...</p>
        </div>
        
        <div v-else-if="docContentError" class="error-message">
          {{ docContentError }}
        </div>
        
        <div 
          v-else-if="docContentHtml" 
          class="doc-content"
          v-html="docContentHtml"
          style="padding: 20px; line-height: 1.6; color: #333;"
        ></div>
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
  currentDoc: {
    type: Object,
    default: null
  }
})

defineEmits(['update:modelValue'])

const docContentHtml = ref('')
const docContentLoading = ref(false)
const docContentError = ref('')

// 문서 내용 로드
const loadDocContent = async (filename) => {
  docContentLoading.value = true
  docContentError.value = ''
  docContentHtml.value = ''
  
  try {
    const encodedFilename = encodeURIComponent(filename)
    const response = await fetch(`/api/docs/content/${encodedFilename}`)
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const data = await response.json()
    
    if (data.success) {
      // 마크다운을 HTML로 변환
      docContentHtml.value = marked.parse(data.content)
      docContentError.value = ''
    } else {
      docContentError.value = data.error || '문서를 불러올 수 없습니다.'
    }
  } catch (error) {
    console.error('[문서 내용 로드] 오류:', error)
    docContentError.value = `문서를 불러오는 중 오류가 발생했습니다: ${error.message}`
  } finally {
    docContentLoading.value = false
  }
}

// 모달이 열리고 문서가 변경될 때 내용 로드
watch([() => props.modelValue, () => props.currentDoc], ([isOpen, doc]) => {
  if (isOpen && doc) {
    loadDocContent(doc.name)
  } else if (!isOpen) {
    docContentHtml.value = ''
    docContentError.value = ''
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
  z-index: 2000;
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

.doc-content {
  line-height: 1.8;
  color: #333;
}

.doc-content :deep(h1),
.doc-content :deep(h2),
.doc-content :deep(h3),
.doc-content :deep(h4),
.doc-content :deep(h5),
.doc-content :deep(h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.doc-content :deep(h1) {
  font-size: 2em;
  border-bottom: 2px solid #eaecef;
  padding-bottom: 8px;
}

.doc-content :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 8px;
}

.doc-content :deep(h3) {
  font-size: 1.25em;
}

.doc-content :deep(p) {
  margin-bottom: 16px;
}

.doc-content :deep(ul),
.doc-content :deep(ol) {
  margin-bottom: 16px;
  padding-left: 30px;
}

.doc-content :deep(li) {
  margin-bottom: 8px;
}

.doc-content :deep(code) {
  padding: 2px 6px;
  background: #f6f8fa;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 0.9em;
}

.doc-content :deep(pre) {
  padding: 16px;
  background: #f6f8fa;
  border-radius: 6px;
  overflow-x: auto;
  margin-bottom: 16px;
}

.doc-content :deep(pre code) {
  padding: 0;
  background: transparent;
}

.doc-content :deep(blockquote) {
  padding: 0 16px;
  color: #6a737d;
  border-left: 4px solid #dfe2e5;
  margin-bottom: 16px;
}

.doc-content :deep(table) {
  border-collapse: collapse;
  width: 100%;
  margin-bottom: 16px;
}

.doc-content :deep(table th),
.doc-content :deep(table td) {
  padding: 8px 12px;
  border: 1px solid #dfe2e5;
}

.doc-content :deep(table th) {
  background: #f6f8fa;
  font-weight: 600;
}

.doc-content :deep(a) {
  color: #0366d6;
  text-decoration: none;
}

.doc-content :deep(a:hover) {
  text-decoration: underline;
}

.doc-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
  margin: 16px 0;
}

.doc-content :deep(hr) {
  height: 1px;
  background: #eaecef;
  border: none;
  margin: 24px 0;
}
</style>


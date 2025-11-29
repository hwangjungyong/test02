<template>
  <div v-if="modelValue" class="error-log-analysis-container">
    <h2>🔧 AI 에러로그분석</h2>
    <div class="error-log-analysis-notice">
      <p>ℹ️ GCP 에러 로그를 직접 입력하거나 파일 경로를 지정하여 분석합니다.</p>
      <p>💡 에러 로그를 자동으로 적재하고 최신순으로 테이블 형태로 출력하며, 워크스페이스에서 발생 위치를 찾아 수정 가이드를 제공합니다.</p>
    </div>
    
    <!-- 로그 입력 방식 선택 -->
    <div class="input-group">
      <label>로그 입력 방식:</label>
      <div class="input-mode-selector">
        <label class="radio-label">
          <input type="radio" v-model="errorLogInputMode" value="direct" />
          직접 입력
        </label>
        <label class="radio-label">
          <input type="radio" v-model="errorLogInputMode" value="file" />
          파일 경로
        </label>
      </div>
    </div>
    
    <!-- 직접 입력 모드 -->
    <div v-if="errorLogInputMode === 'direct'" class="input-group">
      <label for="errorLogContent">GCP 에러 로그 내용:</label>
      <textarea
        id="errorLogContent"
        v-model="errorLogContent"
        placeholder="GCP 에러 로그를 여기에 붙여넣으세요..."
        class="input-field"
        rows="15"
      ></textarea>
    </div>
    
    <!-- 파일 경로 모드 -->
    <div v-if="errorLogInputMode === 'file'" class="input-group">
      <label for="errorLogFile">로그 파일 경로 (선택사항):</label>
      <input
        id="errorLogFile"
        v-model="errorLogFile"
        type="text"
        placeholder="예: logs/error.log (비워두면 워크스페이스에서 자동으로 찾습니다)"
        class="input-field"
      />
    </div>
    
    <div class="error-log-analysis-actions">
      <button @click="analyzeErrorLog" class="btn-analyze-error-log" :disabled="isAnalyzingErrorLog || (errorLogInputMode === 'direct' && !errorLogContent.trim())">
        <span class="btn-icon" v-if="!isAnalyzingErrorLog">🔍</span>
        <span class="loading-spinner" v-if="isAnalyzingErrorLog"></span>
        <span class="btn-text">
          <span v-if="!isAnalyzingErrorLog">에러 로그 분석하기</span>
          <span v-else>분석 중...</span>
        </span>
      </button>
      <button @click="saveErrorLog" class="btn-save-error-log" :disabled="isAnalyzingErrorLog || (errorLogInputMode === 'direct' && !errorLogContent.trim())">
        <span class="btn-icon">💾</span>
        <span class="btn-text">저장</span>
      </button>
      <button @click="loadErrorLogHistory" class="btn-load-history">
        <span class="btn-icon">📜</span>
        <span class="btn-text">이력 조회</span>
      </button>
      <button @click="clearErrorLogAnalysis" class="btn-clear-error-log">
        <span class="btn-icon">🗑️</span>
        <span class="btn-text">초기화</span>
      </button>
    </div>
    
    <!-- 로그 이력 모달 -->
    <div v-if="showErrorLogHistory" class="error-log-history-modal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>📜 에러 로그 이력</h3>
          <button @click="showErrorLogHistory = false" class="modal-close">×</button>
        </div>
        <div class="modal-body">
          <div v-if="errorLogHistory.length === 0" class="empty-history">
            저장된 로그가 없습니다.
          </div>
          <div v-else class="history-list">
            <div v-for="log in errorLogHistory" :key="log.id" class="history-item">
              <div class="history-header">
                <span class="history-date">{{ new Date(log.created_at).toLocaleString('ko-KR') }}</span>
                <span class="history-type">{{ log.log_type || 'N/A' }}</span>
                <button @click="loadLogFromHistory(log)" class="btn-load-log">불러오기</button>
                <button @click="deleteErrorLog(log.id)" class="btn-delete-log">삭제</button>
              </div>
              <div class="history-content">{{ log.log_content.substring(0, 200) }}{{ log.log_content.length > 200 ? '...' : '' }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <div v-if="errorLogAnalysisError" class="error">
      <p>{{ errorLogAnalysisError }}</p>
    </div>
    
    <div v-if="errorLogAnalysisResult" class="error-log-analysis-results">
      <h3>📊 에러 로그 분석 결과 (최신순)</h3>
      <div class="error-log-content" v-html="errorLogAnalysisResult"></div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { marked } from 'marked'
import { getApiUrl } from '../../config/api.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

// AI 에러로그분석 관련
const errorLogFile = ref('')
const errorLogContent = ref('')
const errorLogInputMode = ref('direct') // 'direct' or 'file'
const isAnalyzingErrorLog = ref(false)
const errorLogAnalysisError = ref('')
const errorLogAnalysisResult = ref(null)
const showErrorLogHistory = ref(false)
const errorLogHistory = ref([])

/**
 * 에러 로그 분석 함수
 * 
 * 기능:
 * - MCP 서버를 통해 에러 로그 분석 수행
 */
const analyzeErrorLog = async () => {
  isAnalyzingErrorLog.value = true
  errorLogAnalysisError.value = ''
  errorLogAnalysisResult.value = null
  
  try {
    const requestBody = {
      log_file_path: errorLogInputMode.value === 'file' ? (errorLogFile.value.trim() || null) : null,
      log_content: errorLogInputMode.value === 'direct' ? (errorLogContent.value.trim() || null) : null,
      workspace_path: null // 현재 워크스페이스 사용
    }
    
    console.log('[프론트엔드] 에러 로그 분석 요청:', requestBody)
    
    const response = await fetch(getApiUrl('/api/error-log/analyze'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    const data = await response.json()
    console.log('[프론트엔드] 에러 로그 분석 응답:', data)
    
    if (!response.ok || !data.success) {
      const errorMessage = data.error || data.details || `서버 오류 (${response.status} ${response.statusText})`
      console.error('[프론트엔드] 에러 로그 분석 오류:', errorMessage)
      errorLogAnalysisError.value = errorMessage
      errorLogAnalysisResult.value = null
      return
    }
    
    if (data.success && data.result) {
      // 결과를 HTML로 변환 (마크다운 파싱)
      if (typeof data.result === 'string') {
        // 마크다운을 HTML로 변환
        try {
          errorLogAnalysisResult.value = marked.parse(data.result)
        } catch (e) {
          // 마크다운 파싱 실패 시 기본 변환
          errorLogAnalysisResult.value = data.result.replace(/\n/g, '<br>')
        }
      } else {
        errorLogAnalysisResult.value = JSON.stringify(data.result, null, 2).replace(/\n/g, '<br>')
      }
      errorLogAnalysisError.value = ''
      console.log('[프론트엔드] 에러 로그 분석 성공')
      
      // 분석 성공 시 자동으로 DB에 저장
      const logContent = errorLogInputMode.value === 'direct' ? errorLogContent.value.trim() : ''
      if (logContent) {
        try {
          const saveResponse = await fetch(getApiUrl('/api/error-log/save'), {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json'
            },
            body: JSON.stringify({
              log_content: logContent,
              log_type: 'gcp' // 기본값, 나중에 파싱하여 자동 감지 가능
            })
          })
          
          const saveData = await saveResponse.json()
          if (saveData.success) {
            console.log('[프론트엔드] 에러 로그 자동 저장 성공')
          }
        } catch (saveError) {
          console.warn('[프론트엔드] 에러 로그 자동 저장 실패:', saveError)
          // 저장 실패해도 분석 결과는 표시
        }
      }
    } else {
      throw new Error(data.error || '에러 로그 분석 결과를 받을 수 없습니다.')
    }
  } catch (error) {
    console.error('[프론트엔드] 에러 로그 분석 오류:', error)
    errorLogAnalysisError.value = error.message || '에러 로그 분석 중 오류가 발생했습니다.'
    errorLogAnalysisResult.value = null
  } finally {
    isAnalyzingErrorLog.value = false
  }
}

/**
 * 에러 로그 저장 함수
 */
const saveErrorLog = async () => {
  const logContent = errorLogInputMode.value === 'direct' ? errorLogContent.value.trim() : ''
  
  if (!logContent) {
    errorLogAnalysisError.value = '저장할 로그 내용이 없습니다.'
    return
  }
  
  try {
    const response = await fetch(getApiUrl('/api/error-log/save'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        log_content: logContent,
        log_type: 'gcp' // 기본값, 나중에 파싱하여 자동 감지 가능
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      alert('에러 로그가 저장되었습니다.')
    } else {
      errorLogAnalysisError.value = data.error || '로그 저장에 실패했습니다.'
    }
  } catch (error) {
    console.error('[프론트엔드] 에러 로그 저장 오류:', error)
    errorLogAnalysisError.value = error.message || '에러 로그 저장 중 오류가 발생했습니다.'
  }
}

/**
 * 에러 로그 이력 조회 함수
 */
const loadErrorLogHistory = async () => {
  try {
    const response = await fetch(getApiUrl('/api/error-log/history?limit=50'))
    const data = await response.json()
    
    if (data.success) {
      errorLogHistory.value = data.result || []
      showErrorLogHistory.value = true
    } else {
      errorLogAnalysisError.value = data.error || '이력 조회에 실패했습니다.'
    }
  } catch (error) {
    console.error('[프론트엔드] 에러 로그 이력 조회 오류:', error)
    errorLogAnalysisError.value = error.message || '에러 로그 이력 조회 중 오류가 발생했습니다.'
  }
}

/**
 * 이력에서 로그 불러오기 함수
 */
const loadLogFromHistory = (log) => {
  errorLogContent.value = log.log_content
  errorLogInputMode.value = 'direct'
  showErrorLogHistory.value = false
}

/**
 * 에러 로그 삭제 함수
 */
const deleteErrorLog = async (logId) => {
  if (!confirm('이 로그를 삭제하시겠습니까?')) {
    return
  }
  
  try {
    // 삭제 API는 나중에 구현 가능, 지금은 프론트엔드에서만 제거
    errorLogHistory.value = errorLogHistory.value.filter(log => log.id !== logId)
    alert('로그가 삭제되었습니다.')
  } catch (error) {
    console.error('[프론트엔드] 에러 로그 삭제 오류:', error)
    errorLogAnalysisError.value = error.message || '에러 로그 삭제 중 오류가 발생했습니다.'
  }
}

/**
 * 에러 로그 분석 초기화 함수
 */
const clearErrorLogAnalysis = () => {
  errorLogFile.value = ''
  errorLogContent.value = ''
  errorLogAnalysisError.value = ''
  errorLogAnalysisResult.value = null
}
</script>

<style scoped>
.error-log-analysis-container {
  margin-top: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 20px;
  box-shadow: 
    0 10px 40px rgba(255, 107, 107, 0.15),
    0 0 0 1px rgba(255, 107, 107, 0.1);
  border: 1px solid rgba(255, 107, 107, 0.2);
}

.error-log-analysis-notice {
  background: linear-gradient(135deg, #ffe0e0 0%, #ffcccc 100%);
  border-left: 5px solid #ff6b6b;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(255, 107, 107, 0.15);
}

.error-log-analysis-notice p {
  margin: 0.5rem 0;
  color: #c44569;
  font-size: 14px;
  line-height: 1.6;
}

.error-log-analysis-actions {
  display: flex;
  gap: 1.25rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.btn-analyze-error-log {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(255, 107, 107, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-analyze-error-log:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(255, 107, 107, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-analyze-error-log:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-clear-error-log {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(149, 165, 166, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-clear-error-log:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(149, 165, 166, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.error-log-analysis-results {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e9ecef;
  text-align: left;
}

.error-log-analysis-results h3 {
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #333;
  text-align: left;
  font-size: 1.5rem;
  font-weight: 600;
  border-bottom: 2px solid #ff6b6b;
  padding-bottom: 0.75rem;
}

.error-log-content {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  border: 1px solid #dee2e6;
  font-size: 14px;
  line-height: 1.8;
  text-align: left;
  color: #333;
  overflow-x: auto;
}

.error-log-content h1,
.error-log-content h2,
.error-log-content h3,
.error-log-content h4 {
  text-align: left;
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  color: #2c3e50;
  font-weight: 600;
}

.error-log-content h1 {
  font-size: 1.75rem;
  border-bottom: 3px solid #ff6b6b;
  padding-bottom: 0.5rem;
}

.error-log-content h2 {
  font-size: 1.5rem;
  border-bottom: 2px solid #ff6b6b;
  padding-bottom: 0.5rem;
}

.error-log-content h3 {
  font-size: 1.25rem;
  color: #34495e;
}

.error-log-content h4 {
  font-size: 1.1rem;
  color: #555;
}

.error-log-content p {
  text-align: left;
  margin: 0.75rem 0;
  line-height: 1.8;
}

.error-log-content ul,
.error-log-content ol {
  text-align: left;
  margin: 1rem 0;
  padding-left: 2rem;
}

.error-log-content li {
  margin: 0.5rem 0;
  line-height: 1.8;
}

.error-log-content table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.5rem 0;
  text-align: left;
  font-size: 13px;
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.error-log-content table th {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  color: white;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  border: 1px solid #dee2e6;
}

.error-log-content table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border: 1px solid #dee2e6;
  background: #f8f9fa;
}

.error-log-content table tr:nth-child(even) td {
  background: #ffffff;
}

.error-log-content table tr:hover td {
  background: #fff5f5;
}

.error-log-content pre {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 1.25rem;
  border-radius: 8px;
  overflow-x: auto;
  margin: 1rem 0;
  text-align: left;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 13px;
  line-height: 1.6;
}

.error-log-content code {
  background: #f4f4f4;
  color: #e83e8c;
  padding: 0.2rem 0.4rem;
  border-radius: 4px;
  font-family: 'Courier New', 'Consolas', monospace;
  font-size: 13px;
}

.error-log-content pre code {
  background: transparent;
  color: #f8f8f2;
  padding: 0;
}

.error-log-content blockquote {
  border-left: 4px solid #ff6b6b;
  padding-left: 1rem;
  margin: 1rem 0;
  color: #666;
  font-style: italic;
  text-align: left;
}

.error-log-content strong {
  color: #2c3e50;
  font-weight: 600;
}

.error-log-content em {
  color: #555;
  font-style: italic;
}

.error-log-content hr {
  border: none;
  border-top: 2px solid #dee2e6;
  margin: 2rem 0;
}

.error-log-content a {
  color: #ff6b6b;
  text-decoration: none;
}

.error-log-content a:hover {
  text-decoration: underline;
}

.input-mode-selector {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 14px;
}

.radio-label input[type="radio"] {
  cursor: pointer;
}

.btn-save-error-log {
  background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(40, 167, 69, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-save-error-log:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(40, 167, 69, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-save-error-log:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-load-history {
  background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(23, 162, 184, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-load-history:hover {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(23, 162, 184, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.error-log-history-modal {
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
  max-width: 800px;
  width: 90%;
  max-height: 80vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.5rem;
  border-bottom: 1px solid #dee2e6;
}

.modal-header h3 {
  margin: 0;
}

.modal-close {
  background: none;
  border: none;
  font-size: 2rem;
  cursor: pointer;
  color: #6c757d;
  line-height: 1;
}

.modal-close:hover {
  color: #343a40;
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
}

.empty-history {
  text-align: center;
  padding: 3rem;
  color: #6c757d;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.history-item {
  border: 1px solid #dee2e6;
  border-radius: 8px;
  padding: 1rem;
  background: #f8f9fa;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.5rem;
  gap: 1rem;
}

.history-date {
  font-weight: 600;
  color: #333;
}

.history-type {
  padding: 0.25rem 0.75rem;
  background: #ff6b6b;
  color: white;
  border-radius: 4px;
  font-size: 12px;
}

.history-content {
  color: #666;
  font-size: 14px;
  line-height: 1.5;
}

.btn-load-log {
  background: #17a2b8;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-load-log:hover {
  background: #138496;
}

.btn-delete-log {
  background: #dc3545;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  cursor: pointer;
  font-size: 13px;
  transition: all 0.3s;
}

.btn-delete-log:hover {
  background: #c82333;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.btn-icon {
  font-size: 18px;
}

.btn-text {
  font-size: 16px;
}
</style>


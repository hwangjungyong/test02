<template>
  <div v-if="modelValue" class="error-log-analysis-container">
    <h2>🔧 AI 에러로그 분석</h2>
    <div class="analysis-notice">
      <p>ℹ️ 에러 로그 파일을 분석하여 원인 파악 및 해결 방안을 제시합니다.</p>
      <p>💡 MCP Python 서버를 사용하여 에러 로그를 분석합니다.</p>
    </div>
    
    <div class="input-group">
      <label for="errorLogFile">에러 로그 파일 경로 (선택사항):</label>
      <input
        id="errorLogFile"
        v-model="errorLogFile"
        type="text"
        placeholder="예: logs/error.log"
        class="input-field"
      />
    </div>
    
    <div class="input-group">
      <label for="errorLogContent" style="font-size: 16px; font-weight: 600; margin-bottom: 0.75rem; display: block; color: #333;">
        에러 로그 내용:
      </label>
      <textarea
        id="errorLogContent"
        v-model="errorLogContent"
        placeholder="에러 로그 내용을 붙여넣으세요..."
        class="error-log-textarea"
        rows="15"
      ></textarea>
    </div>
    
    <div class="analysis-actions">
      <button @click="analyzeErrorLog" class="btn-analyze-error-log" :disabled="isAnalyzingErrorLog">
        <span class="btn-icon" v-if="!isAnalyzingErrorLog">🔍</span>
        <span class="loading-spinner" v-if="isAnalyzingErrorLog"></span>
        <span class="btn-text">
          <span v-if="!isAnalyzingErrorLog">AI 에러 로그 분석하기</span>
          <span v-else>분석 중...</span>
        </span>
      </button>
      <button @click="clearErrorLogAnalysis" class="btn-clear-error-log">
        <span class="btn-icon">🗑️</span>
        <span class="btn-text">초기화</span>
      </button>
    </div>
    
    <div v-if="errorLogAnalysisError" class="error">
      <p>{{ errorLogAnalysisError }}</p>
    </div>
    
    <div v-if="errorLogAnalysisResult" class="error-log-analysis-results">
      <h3>분석 결과</h3>
      
      <!-- 요약 정보 -->
      <div v-if="errorLogAnalysisResult.summary" class="analysis-section summary-section">
        <h4>📋 요약</h4>
        <div class="summary-content">
          <p>{{ errorLogAnalysisResult.summary }}</p>
        </div>
      </div>
      
      <!-- 에러 유형 -->
      <div v-if="errorLogAnalysisResult.error_type" class="analysis-section">
        <h4>🔍 에러 유형</h4>
        <div class="error-type-info">
          <p><strong>유형:</strong> {{ errorLogAnalysisResult.error_type }}</p>
          <p v-if="errorLogAnalysisResult.error_category"><strong>카테고리:</strong> {{ errorLogAnalysisResult.error_category }}</p>
          <p v-if="errorLogAnalysisResult.severity"><strong>심각도:</strong> 
            <span :class="getSeverityClass(errorLogAnalysisResult.severity)">
              {{ errorLogAnalysisResult.severity }}
            </span>
          </p>
        </div>
      </div>
      
      <!-- 원인 분석 -->
      <div v-if="errorLogAnalysisResult.root_cause" class="analysis-section">
        <h4>🔎 원인 분석</h4>
        <div class="root-cause-content">
          <p>{{ errorLogAnalysisResult.root_cause }}</p>
        </div>
      </div>
      
      <!-- 해결 방안 -->
      <div v-if="errorLogAnalysisResult.solutions && errorLogAnalysisResult.solutions.length > 0" class="analysis-section">
        <h4>💡 해결 방안</h4>
        <ul class="solutions-list">
          <li v-for="(solution, index) in errorLogAnalysisResult.solutions" :key="index" class="solution-item">
            <strong>{{ index + 1 }}.</strong> {{ solution }}
          </li>
        </ul>
      </div>
      
      <!-- 메타데이터 -->
      <div v-if="errorLogAnalysisResult.metadata" class="analysis-section metadata-section">
        <h4>📊 메타데이터</h4>
        <div class="metadata-content">
          <div v-if="errorLogAnalysisResult.metadata.system_type" class="metadata-item">
            <strong>시스템 유형:</strong> {{ errorLogAnalysisResult.metadata.system_type }}
          </div>
          <div v-if="errorLogAnalysisResult.metadata.resource_type" class="metadata-item">
            <strong>리소스 유형:</strong> {{ errorLogAnalysisResult.metadata.resource_type }}
          </div>
          <div v-if="errorLogAnalysisResult.metadata.service_name" class="metadata-item">
            <strong>서비스명:</strong> {{ errorLogAnalysisResult.metadata.service_name }}
          </div>
          <div v-if="errorLogAnalysisResult.metadata.file_path" class="metadata-item">
            <strong>파일 경로:</strong> <code>{{ errorLogAnalysisResult.metadata.file_path }}</code>
          </div>
          <div v-if="errorLogAnalysisResult.metadata.line_number" class="metadata-item">
            <strong>라인 번호:</strong> {{ errorLogAnalysisResult.metadata.line_number }}
          </div>
          <div v-if="errorLogAnalysisResult.metadata.timestamp" class="metadata-item">
            <strong>발생 시간:</strong> {{ errorLogAnalysisResult.metadata.timestamp }}
          </div>
        </div>
      </div>
      
      <!-- 원본 로그 -->
      <div v-if="errorLogAnalysisResult.original_log" class="analysis-section original-log-section">
        <h4>📄 원본 로그</h4>
        <pre class="original-log-content">{{ errorLogAnalysisResult.original_log }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { getApiUrl } from '../../config/api.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const errorLogFile = ref('')
const errorLogContent = ref('')
const isAnalyzingErrorLog = ref(false)
const errorLogAnalysisError = ref('')
const errorLogAnalysisResult = ref(null)

const analyzeErrorLog = async () => {
  if (!errorLogContent.value.trim() && !errorLogFile.value.trim()) {
    errorLogAnalysisError.value = '에러 로그 내용 또는 파일 경로를 입력해주세요.'
    return
  }
  
  isAnalyzingErrorLog.value = true
  errorLogAnalysisError.value = ''
  errorLogAnalysisResult.value = null
  
  try {
    const requestBody = {
      log_file_path: errorLogFile.value.trim() || null,
      log_content: errorLogContent.value.trim() || null,
      workspace_path: null
    }
    
    console.log('[프론트엔드] 에러 로그 분석 요청:', requestBody)
    
    const response = await fetch(getApiUrl('/api/error-log/analyze'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success) {
      errorLogAnalysisResult.value = data.result
    } else {
      errorLogAnalysisError.value = data.error || '에러 로그 분석에 실패했습니다.'
    }
  } catch (error) {
    console.error('에러 로그 분석 오류:', error)
    const errorMessage = error.message || '에러 로그 분석 중 오류가 발생했습니다.'
    errorLogAnalysisError.value = errorMessage
    console.error('[에러 로그 분석] 오류:', errorMessage)
  } finally {
    isAnalyzingErrorLog.value = false
  }
}

const clearErrorLogAnalysis = () => {
  errorLogFile.value = ''
  errorLogContent.value = ''
  errorLogAnalysisError.value = ''
  errorLogAnalysisResult.value = null
}

const getSeverityClass = (severity) => {
  if (!severity) return ''
  const severityLower = severity.toLowerCase()
  if (severityLower === 'critical' || severityLower === 'high') return 'severity-high'
  if (severityLower === 'medium') return 'severity-medium'
  if (severityLower === 'low') return 'severity-low'
  return ''
}
</script>

<style scoped>
.error-log-analysis-container {
  background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
  border-radius: 20px;
  padding: 2.5rem;
  margin-top: 2rem;
  box-shadow: 
    0 10px 40px rgba(255, 140, 66, 0.15),
    0 0 0 1px rgba(255, 140, 66, 0.1);
  border: 1px solid rgba(255, 140, 66, 0.2);
  position: relative;
  overflow: hidden;
}

.error-log-analysis-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #ff6b35 0%, #ff8c42 50%, #f5576c 100%);
}

.analysis-notice {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0cc 100%);
  border-left: 5px solid #ff8c42;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(255, 140, 66, 0.2);
}

.analysis-notice p {
  margin: 0.5rem 0;
  color: #e65100;
  font-size: 14px;
  line-height: 1.6;
}

.error-log-textarea {
  width: 100%;
  min-height: 300px;
  padding: 1.25rem;
  font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
  font-size: 14px;
  line-height: 1.6;
  border: 2px solid rgba(255, 140, 66, 0.3);
  border-radius: 12px;
  background: #ffffff;
  color: #333;
  resize: vertical;
  transition: all 0.3s ease;
}

.error-log-textarea:focus {
  outline: none;
  border-color: #ff8c42;
  box-shadow: 0 4px 20px rgba(255, 140, 66, 0.2);
}

.analysis-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.btn-analyze-error-log {
  flex: 1;
  min-width: 250px;
  background: linear-gradient(135deg, #ff6b35 0%, #ff8c42 50%, #ffa726 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  padding: 1.25rem 2.5rem;
  border-radius: 14px;
  font-size: 18px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 6px 24px rgba(255, 107, 53, 0.45),
    0 2px 8px rgba(255, 140, 66, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.btn-analyze-error-log:hover:not(:disabled) {
  transform: translateY(-4px) scale(1.03);
  box-shadow: 
    0 12px 36px rgba(255, 107, 53, 0.6),
    0 4px 12px rgba(255, 140, 66, 0.4);
}

.btn-analyze-error-log:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-clear-error-log {
  padding: 1.25rem 2.5rem;
  background: linear-gradient(135deg, #fff8f0 0%, #ffe0cc 100%);
  color: #ff6b35;
  border: 2px solid #ff8c42;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.btn-clear-error-log:hover {
  background: linear-gradient(135deg, #ffe0cc 0%, #ffcc99 100%);
  transform: translateY(-3px);
}

.loading-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-log-analysis-results {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fffefb;
  border-radius: 12px;
}

.analysis-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  box-shadow: 
    0 2px 8px rgba(0, 0, 0, 0.08),
    0 0 0 1px rgba(0, 0, 0, 0.05);
}

.analysis-section h4 {
  margin-top: 0;
  margin-bottom: 1rem;
  color: #333;
  font-size: 18px;
  font-weight: 700;
}

.summary-section {
  border-left: 4px solid #4a90e2;
}

.error-type-info p {
  margin: 0.5rem 0;
  color: #333;
}

.severity-high {
  color: #d32f2f;
  font-weight: 700;
}

.severity-medium {
  color: #f57c00;
  font-weight: 600;
}

.severity-low {
  color: #388e3c;
  font-weight: 600;
}

.root-cause-content {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #ff8c42;
}

.root-cause-content p {
  margin: 0;
  color: #333;
  line-height: 1.6;
}

.solutions-list {
  list-style: none;
  padding-left: 0;
}

.solution-item {
  padding: 1rem;
  margin-bottom: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4caf50;
  color: #333;
  line-height: 1.6;
}

.metadata-section {
  background: #f0f8ff;
}

.metadata-content {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.metadata-item {
  padding: 0.75rem;
  background: white;
  border-radius: 6px;
  font-size: 14px;
}

.metadata-item code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
}

.original-log-section {
  background: #2d2d2d;
  color: #f8f8f2;
}

.original-log-content {
  background: #1e1e1e;
  color: #f8f8f2;
  padding: 1rem;
  border-radius: 8px;
  overflow-x: auto;
  font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
}

.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #ffebee;
  border-radius: 8px;
  border: 2px solid #f44336;
  color: #c62828;
  font-weight: 600;
}

.error p {
  margin: 0;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

.input-field:focus {
  outline: none;
  border-color: #ff8c42;
  box-shadow: 0 0 0 3px rgba(255, 140, 66, 0.1);
}
</style>


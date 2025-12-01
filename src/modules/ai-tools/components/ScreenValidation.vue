<template>
  <div v-if="modelValue" class="screen-validation-container">
    <h2>🔍 AI 화면 검증</h2>
    <div class="validation-notice">
      <p>ℹ️ URL을 입력하면 해당 페이지에 접속하여 화면을 캡처하고 특정 요소의 값을 검증합니다.</p>
      <p>💡 MCP Python 서버(Playwright)를 사용하여 브라우저 자동화를 수행합니다.</p>
    </div>
    
    <div class="input-group">
      <label for="screenValidationUrl">접속할 URL:</label>
      <input
        id="screenValidationUrl"
        v-model="screenValidationUrl"
        type="url"
        placeholder="예: https://example.com"
        class="input-field"
      />
    </div>
    
    <div class="input-group">
      <label for="screenValidationSelector">CSS 선택자 (검증할 요소):</label>
      <input
        id="screenValidationSelector"
        v-model="screenValidationSelector"
        type="text"
        placeholder="예: #price, .title, h1, [data-testid='value']"
        class="input-field"
      />
      <small class="input-hint">요소의 텍스트 내용을 읽어옵니다. 비워두면 전체 페이지를 캡처합니다.</small>
    </div>
    
    <div class="input-group">
      <label for="screenValidationExpectedValue">예상 값 (선택사항):</label>
      <input
        id="screenValidationExpectedValue"
        v-model="screenValidationExpectedValue"
        type="text"
        placeholder="예: 1000원, Hello World"
        class="input-field"
      />
      <small class="input-hint">입력하면 읽은 값과 비교하여 검증 결과를 표시합니다.</small>
    </div>
    
    <div class="validation-actions">
      <button 
        @click="validateScreen" 
        class="btn btn-validate" 
        :disabled="isValidatingScreen || !screenValidationUrl"
      >
        {{ isValidatingScreen ? '검증 중...' : '🔍 화면 검증하기' }}
      </button>
      <button 
        @click="captureScreenOnly" 
        class="btn btn-capture" 
        :disabled="isValidatingScreen || !screenValidationUrl"
      >
        📸 화면 캡처만
      </button>
      <button 
        @click="interactAndGetResult" 
        class="btn btn-interact" 
        :disabled="isValidatingScreen || !screenValidationUrl"
      >
        ⚡ 입력/클릭 후 결과 가져오기
      </button>
    </div>
    
    <!-- 입력/클릭 액션 설정 - 간단한 버전 -->
    <div class="interact-actions-section">
      <h3>⚡ 자동 작업 설정</h3>
      <p class="section-description">
        페이지 접속 후 자동으로 수행할 작업을 순서대로 추가하세요.
      </p>
      
      <div v-for="(action, index) in interactActions" :key="index" class="action-item">
        <div class="action-header">
          <span class="action-number">단계 {{ index + 1 }}</span>
          <button 
            v-if="interactActions.length > 1"
            @click="removeAction(index)" 
            class="btn-remove-action"
            type="button"
          >
            ✕ 삭제
          </button>
        </div>
        
        <div class="action-fields">
          <div class="field-group">
            <label>작업 유형</label>
            <select v-model="action.type" class="input-field" @change="onActionTypeChange(action)">
              <option value="fill">텍스트 입력</option>
              <option value="click">버튼/링크 클릭</option>
              <option value="select">드롭다운 선택</option>
              <option value="check">체크박스 체크</option>
              <option value="uncheck">체크박스 해제</option>
              <option value="wait">대기</option>
            </select>
          </div>
          
          <div v-if="action.type !== 'wait'" class="field-group">
            <label>요소 선택자</label>
            <input
              v-model="action.selector"
              type="text"
              :placeholder="getSelectorPlaceholder(action.type)"
              class="input-field"
            />
            <small class="input-hint">
              💡 F12 → 요소 선택 → 우클릭 → Copy selector 또는 간단히 #아이디명, .클래스명
            </small>
          </div>
          
          <div v-if="action.type === 'fill'" class="field-group">
            <label>입력할 텍스트</label>
            <input
              v-model="action.value"
              type="text"
              placeholder="예: 검색어, 사용자명"
              class="input-field"
            />
          </div>
          
          <div v-if="action.type === 'select'" class="field-group">
            <label>선택할 옵션</label>
            <input
              v-model="action.value"
              type="text"
              placeholder="드롭다운에서 선택할 값"
              class="input-field"
            />
          </div>
          
          <div v-if="action.type === 'wait'" class="field-group">
            <label>대기 시간 (초)</label>
            <input
              v-model="action.value"
              type="number"
              placeholder="예: 2"
              class="input-field"
            />
          </div>
        </div>
      </div>
      
      <button @click="addAction" class="btn-add-action" type="button">
        + 다음 단계 추가
      </button>
      
      <div class="input-group" style="margin-top: 1.5rem;">
        <label for="interactResultSelector">결과 확인 (선택사항)</label>
        <input
          id="interactResultSelector"
          v-model="interactResultSelector"
          type="text"
          placeholder="결과를 표시하는 요소의 선택자"
          class="input-field"
        />
        <small class="input-hint">
          모든 작업 완료 후 결과를 읽어올 요소를 지정하세요. 비워두면 화면만 캡처합니다.
        </small>
      </div>
    </div>
    
    <div v-if="screenValidationError" class="validation-error">
      <div class="error-header">
        <span class="error-icon">⚠️</span>
        <strong class="error-title">오류 발생</strong>
      </div>
      <div class="error-content">
        <pre class="error-message">{{ screenValidationError }}</pre>
      </div>
    </div>
    
    <div v-if="screenValidationResult" class="validation-result">
      <h3>검증 결과</h3>
      <div class="result-info">
        <p><strong>URL:</strong> {{ screenValidationResult.url }}</p>
        <p><strong>선택자:</strong> {{ screenValidationResult.selector || '전체 페이지' }}</p>
        <p v-if="screenValidationResult.actualValue"><strong>읽은 값:</strong> {{ screenValidationResult.actualValue }}</p>
        <p v-if="screenValidationResult.expectedValue"><strong>예상 값:</strong> {{ screenValidationResult.expectedValue }}</p>
        <div class="validation-status" :class="{ 'passed': screenValidationResult.passed, 'failed': !screenValidationResult.passed }">
          <strong>검증 결과:</strong> 
          <span v-if="screenValidationResult.passed">✅ {{ screenValidationResult.message }}</span>
          <span v-else-if="screenValidationResult.selectorError">❌ {{ screenValidationResult.message }}</span>
          <span v-else>❌ {{ screenValidationResult.message }}</span>
        </div>
        <div v-if="screenValidationResult.selectorError" class="selector-error-hint">
          <div class="error-hint-header">
            <span class="hint-icon">💡</span>
            <strong>선택자 도움말</strong>
          </div>
          <pre class="error-hint-text">{{ screenValidationResult.selectorError }}</pre>
        </div>
      </div>
      
      <div v-if="screenScreenshot" class="screenshot-container">
        <h4>캡처된 화면</h4>
        <img :src="`data:image/png;base64,${screenScreenshot}`" alt="화면 캡처" class="screenshot-image" />
      </div>
    </div>
    
    <!-- 입력/클릭 결과 -->
    <div v-if="interactResult" class="interact-result">
      <h3>입력/클릭 결과</h3>
      <div class="result-info">
        <p><strong>URL:</strong> {{ interactResult.url }}</p>
        <div v-if="interactResult.actions && interactResult.actions.length > 0" class="actions-log">
          <strong>수행된 액션:</strong>
          <ul>
            <li v-for="(action, index) in interactResult.actions" :key="index">{{ action }}</li>
          </ul>
        </div>
        <p v-if="interactResult.resultSelector"><strong>결과 선택자:</strong> {{ interactResult.resultSelector }}</p>
        <p v-if="interactResult.resultValue"><strong>결과 값:</strong> {{ interactResult.resultValue }}</p>
      </div>
      
      <div v-if="screenScreenshot" class="screenshot-container">
        <h4>캡처된 화면</h4>
        <img :src="`data:image/png;base64,${screenScreenshot}`" alt="화면 캡처" class="screenshot-image" />
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

const screenValidationUrl = ref('')
const screenValidationSelector = ref('')
const screenValidationExpectedValue = ref('')
const screenValidationResult = ref(null)
const screenValidationError = ref('')
const isValidatingScreen = ref(false)
const screenScreenshot = ref(null) // Base64 이미지 데이터
const interactActions = ref([
  { type: 'fill', selector: '', value: '' }
])
const interactResultSelector = ref('')
const interactResult = ref(null)

const validateScreen = async () => {
  if (!screenValidationUrl.value.trim()) {
    screenValidationError.value = 'URL을 입력해주세요.'
    return
  }
  
  isValidatingScreen.value = true
  screenValidationError.value = ''
  screenValidationResult.value = null
  screenScreenshot.value = null
  
  try {
    const response = await fetch(getApiUrl('/api/screen/validate'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: screenValidationUrl.value.trim(),
        selector: screenValidationSelector.value.trim() || null,
        expectedValue: screenValidationExpectedValue.value.trim() || null
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (errorData.success === false && errorData.error) {
        throw new Error(errorData.error)
      }
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success === false) {
      throw new Error(data.error || '화면 검증 실패')
    }
    
    screenValidationResult.value = {
      url: data.url,
      selector: data.selector,
      actualValue: data.actualValue,
      expectedValue: data.expectedValue,
      passed: data.passed,
      message: data.message,
      selectorError: data.selectorError
    }
    
    if (data.screenshot) {
      screenScreenshot.value = data.screenshot
    }
    
  } catch (error) {
    console.error('화면 검증 오류:', error)
    const errorMessage = error.message || '화면 검증 중 오류가 발생했습니다.'
    screenValidationError.value = errorMessage
    console.error('[화면 검증] 오류:', errorMessage)
  } finally {
    isValidatingScreen.value = false
  }
}

const captureScreenOnly = async () => {
  if (!screenValidationUrl.value.trim()) {
    screenValidationError.value = 'URL을 입력해주세요.'
    return
  }
  
  isValidatingScreen.value = true
  screenValidationError.value = ''
  screenValidationResult.value = null
  screenScreenshot.value = null
  
  try {
    const response = await fetch(getApiUrl('/api/screen/capture'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: screenValidationUrl.value.trim(),
        selector: screenValidationSelector.value.trim() || null
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (errorData.success === false && errorData.error) {
        throw new Error(errorData.error)
      }
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success === false) {
      throw new Error(data.error || '화면 캡처 실패')
    }
    
    screenValidationResult.value = {
      url: data.url,
      selector: data.selector || '전체 페이지',
      actualValue: null,
      expectedValue: null,
      passed: true,
      message: '화면 캡처 완료'
    }
    
    if (data.screenshot) {
      screenScreenshot.value = data.screenshot
    }
    
  } catch (error) {
    console.error('화면 캡처 오류:', error)
    const errorMessage = error.message || '화면 캡처 중 오류가 발생했습니다.'
    screenValidationError.value = errorMessage
    console.error('[화면 캡처] 오류:', errorMessage)
  } finally {
    isValidatingScreen.value = false
  }
}

const onActionTypeChange = (action) => {
  // wait 타입이면 selector 초기화
  if (action.type === 'wait') {
    action.selector = ''
  }
  // value 초기화
  if (action.type === 'click' || action.type === 'check' || action.type === 'uncheck') {
    action.value = ''
  }
}

const addAction = () => {
  interactActions.value.push({ type: 'fill', selector: '', value: '' })
}

const removeAction = (index) => {
  interactActions.value.splice(index, 1)
}

const getSelectorPlaceholder = (type) => {
  const placeholders = {
    fill: '예: #search-input, input[name="q"]',
    click: '예: #submit-button, button.search',
    select: '예: #category-select, select[name="category"]',
    check: '예: #agree-checkbox, input[type="checkbox"]',
    uncheck: '예: #agree-checkbox, input[type="checkbox"]',
    wait: '(대기 시간만 입력)'
  }
  return placeholders[type] || 'CSS 선택자 입력'
}

const interactAndGetResult = async () => {
  if (!screenValidationUrl.value.trim()) {
    screenValidationError.value = 'URL을 입력해주세요.'
    return
  }
  
  // 액션 검증 및 변환
  const actions = []
  for (const action of interactActions.value) {
    if (action.type === 'wait') {
      // 대기 시간은 초를 밀리초로 변환
      const seconds = parseInt(action.value) || 0
      if (seconds > 0) {
        actions.push({
          type: 'wait',
          selector: '',
          value: String(seconds * 1000) // 밀리초로 변환
        })
      }
    } else if (action.selector.trim()) {
      // selector가 있는 액션들
      const actionData = {
        type: action.type,
        selector: action.selector.trim()
      }
      if (action.value && action.value.trim()) {
        actionData.value = action.value.trim()
      }
      actions.push(actionData)
    }
  }
  
  if (actions.length === 0) {
    screenValidationError.value = '최소 하나의 액션을 설정해주세요.'
    return
  }
  
  isValidatingScreen.value = true
  screenValidationError.value = ''
  screenValidationResult.value = null
  interactResult.value = null
  
  try {
    const response = await fetch(getApiUrl('/api/screen/interact'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: screenValidationUrl.value.trim(),
        actions: actions,
        resultSelector: interactResultSelector.value.trim() || null,
        waitAfterActions: 2000
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (errorData.success === false && errorData.error) {
        throw new Error(errorData.error)
      }
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success === false) {
      throw new Error(data.error || '입력/클릭 실패')
    }
    
    interactResult.value = {
      url: data.url,
      actions: data.actions,
      resultSelector: data.resultSelector,
      resultValue: data.resultValue
    }
    
    if (data.screenshot) {
      screenScreenshot.value = data.screenshot
    }
    
  } catch (error) {
    console.error('입력/클릭 오류:', error)
    const errorMessage = error.message || '입력/클릭 중 오류가 발생했습니다.'
    screenValidationError.value = errorMessage
    console.error('[입력/클릭] 오류:', errorMessage)
  } finally {
    isValidatingScreen.value = false
  }
}
</script>

<style scoped>
.screen-validation-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 2.5rem;
  margin-top: 2rem;
  box-shadow: 
    0 10px 40px rgba(102, 126, 234, 0.15),
    0 0 0 1px rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  position: relative;
  overflow: hidden;
}

.screen-validation-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

.validation-notice {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-left: 5px solid #2196f3;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
  position: relative;
  overflow: hidden;
}

.validation-notice::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(33, 150, 243, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.validation-notice p {
  margin: 0.5rem 0;
  color: #1565c0;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.validation-actions {
  display: flex;
  gap: 1.25rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.btn-validate {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.btn-validate::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-validate:hover:not(:disabled)::before {
  left: 100%;
}

.btn-validate:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-validate:active:not(:disabled) {
  transform: translateY(-1px) scale(0.98);
}

.btn-validate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-interact {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn-interact:hover:not(:disabled) {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(245, 87, 108, 0.4);
}

.btn-capture {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(79, 172, 254, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.btn-capture::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-capture:hover:not(:disabled)::before {
  left: 100%;
}

.btn-capture:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(245, 87, 108, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-capture:active:not(:disabled) {
  transform: translateY(-1px) scale(0.98);
}

.btn-capture:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.input-hint {
  display: block;
  margin-top: 0.5rem;
  color: #666;
  font-size: 12px;
}

.validation-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.result-info {
  margin-bottom: 1.5rem;
}

.result-info p {
  margin: 0.5rem 0;
  color: #333;
}

.validation-status {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 16px;
}

.validation-status.passed {
  background: #e8f5e9;
  color: #2e7d32;
  border: 2px solid #4caf50;
}

.validation-status.failed {
  background: #ffebee;
  color: #c62828;
  border: 2px solid #f44336;
}

.screenshot-container {
  margin-top: 1.5rem;
}

.screenshot-container h4 {
  margin-bottom: 1rem;
  color: #333;
}

.screenshot-image {
  max-width: 100%;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(102, 126, 234, 0.1);
  transition: transform 0.3s ease;
}

.screenshot-image:hover {
  transform: scale(1.01);
  box-shadow: 
    0 12px 32px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(102, 126, 234, 0.2);
}

.validation-error {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  border-left: 5px solid #f44336;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.2);
  position: relative;
  overflow: hidden;
}

.validation-error::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(244, 67, 54, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.error-icon {
  font-size: 24px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.error-title {
  font-size: 18px;
  color: #c62828;
  font-weight: 700;
}

.error-content {
  position: relative;
  z-index: 1;
}

.error-message {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 1rem;
  margin: 0;
  color: #c62828;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  border: 1px solid rgba(244, 67, 54, 0.2);
}

.selector-error-hint {
  margin-top: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
  border-left: 5px solid #ffc107;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
  text-align: left;
}

.error-hint-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #856404;
  font-weight: 600;
  text-align: left;
}

.hint-icon {
  font-size: 20px;
}

.error-hint-text {
  margin: 0;
  color: #856404;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  background: rgba(255, 255, 255, 0.6);
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 193, 7, 0.3);
  text-align: left;
}

.interact-actions-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.section-description {
  color: #666;
  font-size: 12px;
  margin: 0;
}

.action-item {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 8px;
  border: 1px solid rgba(102, 126, 234, 0.2);
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.action-number {
  font-weight: 600;
  color: #667eea;
}

.btn-remove-action {
  background: #f44336;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-remove-action:hover {
  background: #d32f2f;
  transform: scale(1.05);
}

.action-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-group label {
  font-weight: 500;
  color: #333;
  font-size: 14px;
}

.btn-add-action {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s;
  margin-top: 1rem;
}

.btn-add-action:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.interact-result {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(132, 250, 176, 0.3);
}

.actions-log {
  margin-top: 1rem;
}

.actions-log ul {
  list-style: none;
  padding-left: 0;
  margin-top: 0.5rem;
}

.actions-log li {
  padding: 0.5rem;
  margin: 0.25rem 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  font-size: 13px;
}
</style>


<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
    <div class="modal-content error-log-detail-modal" @click.stop style="max-width: 1000px; max-height: 90vh; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 14px; line-height: 1.5;">
      <div class="modal-header">
        <h2 style="font-size: 20px; font-weight: 600; margin: 0;">🔍 에러 로그 상세 정보</h2>
        <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
      </div>
      <div class="modal-body" style="overflow-y: auto; max-height: calc(90vh - 120px);">
        <div v-if="errorLog">
          <!-- 기본 정보 -->
          <div style="margin-bottom: 24px;">
            <h3 style="margin-top: 0; font-size: 16px; font-weight: 600;">기본 정보</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
              <div>
                <strong style="font-size: 13px; font-weight: 600; color: #666; display: block; margin-bottom: 4px;">발생일시</strong>
                <div style="margin-top: 4px; font-size: 13px; font-family: inherit;">{{ formatDateTime(errorLog.timestamp || errorLog.created_at) }}</div>
              </div>
              <div>
                <strong style="font-size: 13px; font-weight: 600; color: #666; display: block; margin-bottom: 4px;">시스템 타입</strong>
                <div style="margin-top: 4px;">
                  <span style="padding: 4px 8px; border-radius: 4px; background: #e3f2fd; color: #1976d2; font-size: 12px; font-weight: 500; font-family: inherit;">
                    {{ errorLog.system_type || errorLog.log_type || 'N/A' }}
                  </span>
                </div>
              </div>
              <div>
                <strong style="font-size: 13px; font-weight: 600; color: #666; display: block; margin-bottom: 4px;">심각도</strong>
                <div style="margin-top: 4px;">
                  <span :style="{
                    padding: '4px 8px',
                    borderRadius: '4px',
                    fontSize: '12px',
                    fontWeight: '600',
                    fontFamily: 'inherit',
                    color: errorLog.severity === 'CRITICAL' ? '#d32f2f' : errorLog.severity === 'ERROR' ? '#f57c00' : '#fbc02d',
                    background: errorLog.severity === 'CRITICAL' ? '#ffebee' : errorLog.severity === 'ERROR' ? '#fff3e0' : '#fffde7'
                  }">
                    {{ errorLog.severity || 'N/A' }}
                  </span>
                </div>
              </div>
              <div>
                <strong style="font-size: 13px; font-weight: 600; color: #666; display: block; margin-bottom: 4px;">에러 타입</strong>
                <div style="margin-top: 4px; font-size: 13px; font-family: inherit;">{{ errorLog.error_type || 'N/A' }}</div>
              </div>
              <div>
                <strong style="font-size: 13px; font-weight: 600; color: #666; display: block; margin-bottom: 4px;">리소스 타입</strong>
                <div style="margin-top: 4px; font-size: 13px; font-family: inherit;">{{ errorLog.resource_type || 'N/A' }}</div>
              </div>
              <div>
                <strong style="font-size: 13px; font-weight: 600; color: #666; display: block; margin-bottom: 4px;">서비스 이름</strong>
                <div style="margin-top: 4px; font-size: 13px; font-family: inherit;">{{ errorLog.service_name || 'N/A' }}</div>
              </div>
            </div>
          </div>

          <!-- 위치 정보 -->
          <div v-if="errorLog.file_path" style="margin-bottom: 24px;">
            <h3 style="margin-top: 0; font-size: 16px; font-weight: 600;">발생 위치</h3>
            <div style="padding: 12px; background: #f5f5f5; border-radius: 4px; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 13px;">
              {{ errorLog.file_path }}{{ errorLog.line_number ? ':' + errorLog.line_number : '' }}
            </div>
          </div>

          <!-- 메타데이터 -->
          <div v-if="errorLog.parsed_data" style="margin-bottom: 24px;">
            <h3 style="margin-top: 0; font-size: 16px; font-weight: 600;">메타데이터</h3>
            <pre style="padding: 12px; background: #f5f5f5; border-radius: 4px; overflow-x: auto; font-size: 12px; max-height: 300px; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; line-height: 1.4;">{{ JSON.stringify(errorLog.parsed_data, null, 2) }}</pre>
          </div>

          <!-- 원본 로그 -->
          <div style="margin-bottom: 24px;">
            <h3 style="margin-top: 0; font-size: 16px; font-weight: 600;">원본 로그</h3>
            <pre style="padding: 12px; background: #f5f5f5; border-radius: 4px; overflow-x: auto; font-size: 12px; max-height: 300px; white-space: pre-wrap; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; line-height: 1.4;">{{ errorLog.log_content }}</pre>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  errorLog: {
    type: Object,
    default: null
  }
})

defineEmits(['update:modelValue'])

// 날짜 시간 포맷팅
function formatDateTime(dateString) {
  if (!dateString) return 'N/A'
  try {
    const date = new Date(dateString)
    return date.toLocaleString('ko-KR', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    })
  } catch {
    return dateString
  }
}
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
</style>


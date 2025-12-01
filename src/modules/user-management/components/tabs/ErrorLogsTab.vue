<template>
  <div class="tab-content" style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 14px; line-height: 1.5;">
    <h3 style="font-size: 18px; font-weight: 600; margin-top: 0; margin-bottom: 8px;">🔍 AI에러로그현황</h3>
    <p style="margin-bottom: 20px; color: #666; font-size: 14px;">
      저장된 에러 로그를 확인하고 분석할 수 있습니다.
    </p>

    <!-- 필터 영역 -->
    <div style="margin-bottom: 20px; padding: 16px; background: #f5f5f5; border-radius: 8px;">
      <h4 style="margin-top: 0; font-size: 16px; font-weight: 600;">필터</h4>
      <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
        <div>
          <label style="display: block; margin-bottom: 4px; font-size: 13px; font-weight: 500; color: #666;">시스템 타입</label>
          <select v-model="filters.system_type" @change="loadLogs" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; font-family: inherit;">
            <option value="">전체</option>
            <option value="gcp_json">GCP (JSON)</option>
            <option value="gcp_text">GCP (Text)</option>
            <option value="aws">AWS CloudWatch</option>
            <option value="azure">Azure Monitor</option>
            <option value="application">일반 애플리케이션</option>
          </select>
        </div>
        <div>
          <label style="display: block; margin-bottom: 4px; font-size: 13px; font-weight: 500; color: #666;">심각도</label>
          <select v-model="filters.severity" @change="loadLogs" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; font-family: inherit;">
            <option value="">전체</option>
            <option value="CRITICAL">CRITICAL</option>
            <option value="ERROR">ERROR</option>
            <option value="WARNING">WARNING</option>
          </select>
        </div>
        <div>
          <label style="display: block; margin-bottom: 4px; font-size: 13px; font-weight: 500; color: #666;">에러 타입</label>
          <select v-model="filters.error_type" @change="loadLogs" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; font-family: inherit;">
            <option value="">전체</option>
            <option value="database">Database</option>
            <option value="network">Network</option>
            <option value="authentication">Authentication</option>
            <option value="memory">Memory</option>
            <option value="file">File</option>
            <option value="syntax">Syntax</option>
          </select>
        </div>
        <div>
          <label style="display: block; margin-bottom: 4px; font-size: 13px; font-weight: 500; color: #666;">시작 날짜</label>
          <input v-model="filters.start_date" @change="loadLogs" type="date" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; font-family: inherit;">
        </div>
        <div>
          <label style="display: block; margin-bottom: 4px; font-size: 13px; font-weight: 500; color: #666;">종료 날짜</label>
          <input v-model="filters.end_date" @change="loadLogs" type="date" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px; font-size: 13px; font-family: inherit;">
        </div>
      </div>
      <div style="margin-top: 12px;">
        <button @click="resetFilters" class="btn" style="padding: 8px 16px; background: #666; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-family: inherit;">
          필터 초기화
        </button>
      </div>
    </div>

    <!-- 로딩 상태 -->
    <div v-if="loading" class="loading">
      <p>에러 로그를 불러오는 중...</p>
    </div>

    <!-- 에러 메시지 -->
    <div v-else-if="error" class="error-message">
      {{ error }}
    </div>

    <!-- 에러 로그 목록 -->
    <div v-else-if="errorLogs && errorLogs.length > 0">
      <div style="margin-bottom: 12px; display: flex; justify-content: space-between; align-items: center;">
        <h4 style="font-size: 16px; font-weight: 600; margin: 0;">에러 로그 목록 ({{ errorLogs.length }}건)</h4>
        <button @click="loadLogs" class="btn" style="padding: 8px 16px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 13px; font-family: inherit;">
          🔄 새로고침
        </button>
      </div>

      <div style="overflow-x: auto;">
        <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; font-size: 13px;">
          <thead>
            <tr style="background: #f5f5f5;">
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">번호</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">발생일시</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">시스템</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">심각도</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">에러 타입</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">발생 위치</th>
              <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: inherit;">작업</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(log, index) in errorLogs" :key="log.id" style="border-bottom: 1px solid #eee;">
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">{{ index + 1 }}</td>
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">{{ formatDateTime(log.timestamp || log.created_at) }}</td>
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">
                <span style="padding: 4px 8px; border-radius: 4px; background: #e3f2fd; color: #1976d2; font-size: 12px; font-weight: 500; font-family: inherit;">
                  {{ log.system_type || log.log_type || 'N/A' }}
                </span>
              </td>
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">
                <span :style="{
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontWeight: '600',
                  fontFamily: 'inherit',
                  color: log.severity === 'CRITICAL' ? '#d32f2f' : log.severity === 'ERROR' ? '#f57c00' : '#fbc02d',
                  background: log.severity === 'CRITICAL' ? '#ffebee' : log.severity === 'ERROR' ? '#fff3e0' : '#fffde7'
                }">
                  {{ log.severity || 'N/A' }}
                </span>
              </td>
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">{{ log.error_type || 'N/A' }}</td>
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">
                <span v-if="log.file_path" style="font-family: 'Consolas', 'Monaco', 'Courier New', monospace; font-size: 12px;">
                  {{ log.file_path }}{{ log.line_number ? ':' + log.line_number : '' }}
                </span>
                <span v-else style="font-family: inherit;">N/A</span>
              </td>
              <td style="padding: 12px; font-size: 13px; font-family: inherit;">
                <button @click="$emit('show-detail', log)" class="btn" style="padding: 6px 12px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500; font-family: inherit;">
                  상세보기
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 빈 목록 -->
    <div v-else style="padding: 40px; text-align: center; color: #666; font-size: 14px; font-family: inherit;">
      <p style="margin: 0; font-size: 14px;">저장된 에러 로그가 없습니다.</p>
    </div>
  </div>
</template>

<script setup>
import { useErrorLogs } from '../../composables/useErrorLogs.js'
import { onMounted } from 'vue'

const {
  errorLogs,
  loading,
  error,
  filters,
  loadLogs,
  resetFilters
} = useErrorLogs()

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

defineEmits(['show-detail'])

onMounted(() => {
  loadLogs()
})
</script>


<template>
  <div class="tab-content">
    <div v-if="loading" class="loading">
      <p>데이터베이스 스키마를 불러오는 중...</p>
    </div>
    <div v-else>
      <div class="schema-header">
        <h3>📊 데이터베이스 스키마</h3>
        <p class="schema-description">현재 데이터베이스에 구성된 테이블과 컬럼 정보입니다.</p>
      </div>
      
      <div v-if="error" class="error-message" style="white-space: pre-line;">
        {{ error }}
        <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #ffcdd2;">
          <strong>디버깅 정보:</strong>
          <ul style="margin: 8px 0; padding-left: 20px;">
            <li>API 엔드포인트: http://localhost:3001/api/db/schema</li>
            <li>서버 상태 확인: 브라우저 개발자 도구(F12) → Network 탭에서 요청 확인</li>
            <li>서버 콘솔 확인: API 서버 실행 창에서 에러 로그 확인</li>
          </ul>
        </div>
      </div>
      
      <div v-if="dbSchema && dbSchema.tables" class="schema-tables">
        <div class="schema-summary">
          <p><strong>총 {{ dbSchema.tables.length }}개의 테이블</strong></p>
        </div>
        
        <div v-for="tableName in dbSchema.tables" :key="tableName" class="schema-table">
          <div class="table-header">
            <h4>📋 {{ tableName }}</h4>
            <span class="table-column-count">{{ dbSchema.schema[tableName]?.length || 0 }}개 컬럼</span>
          </div>
          
          <div class="table-schema">
            <table class="schema-columns-table">
              <thead>
                <tr>
                  <th>컬럼명</th>
                  <th>타입</th>
                  <th>NULL 허용</th>
                  <th>기본값</th>
                  <th>Primary Key</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="column in dbSchema.schema[tableName]" :key="column.cid">
                  <td><strong>{{ column.name }}</strong></td>
                  <td><code>{{ column.type }}</code></td>
                  <td>{{ column.notnull ? '❌' : '✅' }}</td>
                  <td>{{ column.dflt_value || '-' }}</td>
                  <td>{{ column.pk ? '🔑' : '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
      
      <div v-else-if="!loading && !error" class="no-schema">
        <p>스키마 정보를 불러올 수 없습니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDbSchema } from '../../composables/useDbSchema.js'
import { onMounted } from 'vue'

const {
  dbSchema,
  loading,
  error,
  loadSchema
} = useDbSchema()

onMounted(() => {
  loadSchema()
})
</script>


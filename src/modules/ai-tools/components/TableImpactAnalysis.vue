<template>
  <div v-if="modelValue" class="impact-analysis-container">
    <h2>🔍 AI 테이블 영향도 분석</h2>
    <div class="impact-analysis-notice">
      <p>ℹ️ 테이블/컬럼 변경 시 워크스페이스 전체에 미치는 영향을 종합적으로 분석합니다.</p>
      <p>💡 프로그램 코드, 화면, 배치 프로시저 등 모든 영향도를 분석합니다.</p>
    </div>
    
    <div class="input-group">
      <label for="impactTableName">테이블명:</label>
      <input
        id="impactTableName"
        v-model="impactTableName"
        type="text"
        placeholder="예: users"
        class="input-field"
      />
    </div>
    
    <div class="input-group">
      <label for="impactColumnName">컬럼명 (선택사항):</label>
      <input
        id="impactColumnName"
        v-model="impactColumnName"
        type="text"
        placeholder="예: user_id"
        class="input-field"
      />
    </div>
    
    <div class="input-group">
      <label for="impactSpecialNotes">특이사항:</label>
      <textarea
        id="impactSpecialNotes"
        v-model="impactSpecialNotes"
        placeholder="예: users 테이블의 user_id가 int에서 varchar로 변경되면 어떻게 되는지 영향도 분석을 해줘"
        class="input-field"
        rows="4"
      ></textarea>
    </div>
    
    <div class="impact-analysis-actions">
      <button @click="analyzeImpactNew" class="btn-analyze-impact" :disabled="isAnalyzingImpactNew">
        <span class="btn-icon" v-if="!isAnalyzingImpactNew">🔍</span>
        <span class="loading-spinner" v-if="isAnalyzingImpactNew"></span>
        <span class="btn-text">
          <span v-if="!isAnalyzingImpactNew">영향도 분석하기</span>
          <span v-else>분석 중...</span>
        </span>
      </button>
      <button @click="clearImpactAnalysisNew" class="btn-clear-impact">
        <span class="btn-icon">🗑️</span>
        <span class="btn-text">초기화</span>
      </button>
    </div>
    
    <div v-if="impactAnalysisErrorNew" class="error">
      <p>{{ impactAnalysisErrorNew }}</p>
    </div>
    
    <div v-if="impactAnalysisResultNew" class="impact-analysis-results">
      <h3>📊 영향도 분석 결과</h3>
      
      <!-- 간단한 요약 카드 -->
      <div class="impact-summary-simple">
        <div class="summary-main">
          <div class="summary-target">
            <span class="target-label">분석 대상:</span>
            <span class="target-name">{{ impactAnalysisResultNew.table_name }}</span>
            <span v-if="impactAnalysisResultNew.column_name" class="target-column">.{{ impactAnalysisResultNew.column_name }}</span>
          </div>
        </div>
        
        <!-- 핵심 지표 한눈에 보기 -->
        <div class="impact-overview">
          <div class="overview-item">
            <div class="overview-number">{{ getTotalImpactCount() }}</div>
            <div class="overview-label">총 영향도</div>
          </div>
          <div class="overview-item">
            <div class="overview-number">{{ getAffectedFilesCount() }}</div>
            <div class="overview-label">영향 파일</div>
          </div>
          <div class="overview-item">
            <div class="overview-number">{{ getAffectedTablesCount() }}</div>
            <div class="overview-label">연관 테이블</div>
          </div>
        </div>
      </div>
      
      <!-- 테이블 상관도 - 간단 버전 -->
      <div v-if="impactAnalysisResultNew.table_correlation" class="impact-card-simple">
        <div class="card-header-simple" @click="toggleSection('table_correlation')">
          <div class="card-title-simple">
            <span class="card-icon-simple">📊</span>
            <div>
              <div class="card-title-main">테이블 상관도</div>
              <div class="card-title-sub">{{ impactAnalysisResultNew.table_correlation.summary || '분석 중...' }}</div>
            </div>
          </div>
          <button class="toggle-btn-simple">{{ expandedSections.table_correlation ? '▲' : '▼' }}</button>
        </div>
        <div v-if="expandedSections.table_correlation" class="card-content-simple">
          <div class="simple-section">
            <div class="simple-label">직접 참조</div>
            <div class="simple-stat-badge">{{ impactAnalysisResultNew.table_correlation.direct_references || 0 }}건</div>
          </div>
          
          <div v-if="impactAnalysisResultNew.table_correlation.join_relations && impactAnalysisResultNew.table_correlation.join_relations.length > 0" class="simple-section">
            <div class="simple-label">JOIN 관계 ({{ impactAnalysisResultNew.table_correlation.join_relations.length }}건)</div>
            <div class="detail-list">
              <div v-for="(rel, idx) in impactAnalysisResultNew.table_correlation.join_relations" :key="idx" class="detail-item-clean">
                <span class="detail-item-label">연관 테이블:</span>
                <span class="detail-item-value">{{ rel.related_table }}</span>
                <span class="detail-item-type">{{ rel.join_type }}</span>
                <div class="detail-item-file">{{ rel.source_file }}</div>
              </div>
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.table_correlation.related_tables && impactAnalysisResultNew.table_correlation.related_tables.length > 0" class="simple-section">
            <div class="simple-label">연관 테이블 목록</div>
            <div class="simple-tags">
              <span v-for="(table, idx) in impactAnalysisResultNew.table_correlation.related_tables" :key="idx" class="simple-tag">{{ table }}</span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.table_correlation.referenced_files && impactAnalysisResultNew.table_correlation.referenced_files.length > 0" class="simple-section">
            <div class="simple-label">참조 파일 ({{ impactAnalysisResultNew.table_correlation.referenced_files.length }}개)</div>
            <div class="simple-files">
              <div v-for="(file, idx) in impactAnalysisResultNew.table_correlation.referenced_files" :key="idx" class="simple-file">{{ file }}</div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 프로그램 테이블 상관도 - 간단 버전 -->
      <div v-if="impactAnalysisResultNew.program_table_correlation" class="impact-card-simple">
        <div class="card-header-simple" @click="toggleSection('program_table_correlation')">
          <div class="card-title-simple">
            <span class="card-icon-simple">💻</span>
            <div>
              <div class="card-title-main">프로그램 코드</div>
              <div class="card-title-sub">{{ impactAnalysisResultNew.program_table_correlation.summary || '분석 중...' }}</div>
            </div>
          </div>
          <button class="toggle-btn-simple">{{ expandedSections.program_table_correlation ? '▲' : '▼' }}</button>
        </div>
        <div v-if="expandedSections.program_table_correlation" class="card-content-simple">
          <div class="simple-stats">
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_table_correlation.total_references || 0 }}</span>
              <span class="stat-label">총 참조</span>
            </div>
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_table_correlation.javascript_files || 0 }}</span>
              <span class="stat-label">JS/TS</span>
            </div>
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_table_correlation.python_files || 0 }}</span>
              <span class="stat-label">Python</span>
            </div>
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_table_correlation.sql_files || 0 }}</span>
              <span class="stat-label">SQL</span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.program_table_correlation.references && impactAnalysisResultNew.program_table_correlation.references.length > 0" class="simple-section">
            <div class="simple-label">참조 위치 상세 ({{ impactAnalysisResultNew.program_table_correlation.references.length }}건)</div>
            <div class="detail-list">
              <div v-for="(ref, idx) in impactAnalysisResultNew.program_table_correlation.references" :key="idx" class="detail-item-clean">
                <div class="detail-item-header">
                  <span class="detail-item-file">{{ ref.file }}</span>
                  <span class="detail-item-line">라인 {{ ref.line }}</span>
                </div>
                <div v-if="ref.context" class="detail-item-context">{{ ref.context }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 프로그램 컬럼 상관도 - 간단 버전 -->
      <div v-if="impactAnalysisResultNew.program_column_correlation && Object.keys(impactAnalysisResultNew.program_column_correlation).length > 0" class="impact-card-simple">
        <div class="card-header-simple" @click="toggleSection('program_column_correlation')">
          <div class="card-title-simple">
            <span class="card-icon-simple">🔧</span>
            <div>
              <div class="card-title-main">컬럼 사용</div>
              <div class="card-title-sub">{{ impactAnalysisResultNew.program_column_correlation.summary || '분석 중...' }}</div>
            </div>
          </div>
          <button class="toggle-btn-simple">{{ expandedSections.program_column_correlation ? '▲' : '▼' }}</button>
        </div>
        <div v-if="expandedSections.program_column_correlation" class="card-content-simple">
          <div class="simple-stats">
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_column_correlation.total_references || 0 }}</span>
              <span class="stat-label">총 참조</span>
            </div>
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_column_correlation.javascript_files || 0 }}</span>
              <span class="stat-label">JS/TS</span>
            </div>
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_column_correlation.python_files || 0 }}</span>
              <span class="stat-label">Python</span>
            </div>
            <div class="simple-stat">
              <span class="stat-number">{{ impactAnalysisResultNew.program_column_correlation.sql_files || 0 }}</span>
              <span class="stat-label">SQL</span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.program_column_correlation.references && impactAnalysisResultNew.program_column_correlation.references.length > 0" class="simple-section">
            <div class="simple-label">참조 위치 상세 ({{ impactAnalysisResultNew.program_column_correlation.references.length }}건)</div>
            <div class="detail-list">
              <div v-for="(ref, idx) in impactAnalysisResultNew.program_column_correlation.references" :key="idx" class="detail-item-clean">
                <div class="detail-item-header">
                  <span class="detail-item-file">{{ ref.file }}</span>
                  <span class="detail-item-line">라인 {{ ref.line }}</span>
                </div>
                <div v-if="ref.context" class="detail-item-context">{{ ref.context }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 화면 영향 분석 - 간단 버전 -->
      <div v-if="impactAnalysisResultNew.ui_impact" class="impact-card-simple">
        <div class="card-header-simple" @click="toggleSection('ui_impact')">
          <div class="card-title-simple">
            <span class="card-icon-simple">🖥️</span>
            <div>
              <div class="card-title-main">화면 영향</div>
              <div class="card-title-sub">{{ impactAnalysisResultNew.ui_impact.summary || '분석 중...' }}</div>
            </div>
          </div>
          <button class="toggle-btn-simple">{{ expandedSections.ui_impact ? '▲' : '▼' }}</button>
        </div>
        <div v-if="expandedSections.ui_impact" class="card-content-simple">
          <div class="simple-section">
            <div class="simple-label">영향받는 Vue 컴포넌트</div>
            <div class="simple-stat-badge">{{ impactAnalysisResultNew.ui_impact.affected_vue_files || 0 }}개</div>
          </div>
          
          <div v-if="impactAnalysisResultNew.ui_impact.impacts && impactAnalysisResultNew.ui_impact.impacts.length > 0" class="simple-section">
            <div class="simple-label">영향 상세 ({{ impactAnalysisResultNew.ui_impact.impacts.length }}건)</div>
            <div class="detail-list">
              <div v-for="(impact, idx) in impactAnalysisResultNew.ui_impact.impacts" :key="idx" class="detail-item-clean">
                <div class="detail-item-header">
                  <span class="detail-item-file">{{ impact.file }}</span>
                  <span class="detail-item-type-badge" :class="impact.type === 'table_reference' ? 'type-table' : 'type-column'">
                    {{ impact.type === 'table_reference' ? '테이블 참조' : '컬럼 참조' }}
                  </span>
                </div>
                <div v-if="impact.table" class="detail-item-info">테이블: {{ impact.table }}</div>
                <div v-if="impact.column" class="detail-item-info">컬럼: {{ impact.column }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 배치 프로시저 영향 - 간단 버전 -->
      <div v-if="impactAnalysisResultNew.batch_procedure_impact" class="impact-card-simple">
        <div class="card-header-simple" @click="toggleSection('batch_procedure_impact')">
          <div class="card-title-simple">
            <span class="card-icon-simple">⚙️</span>
            <div>
              <div class="card-title-main">배치/프로시저</div>
              <div class="card-title-sub">{{ impactAnalysisResultNew.batch_procedure_impact.summary || '분석 중...' }}</div>
            </div>
          </div>
          <button class="toggle-btn-simple">{{ expandedSections.batch_procedure_impact ? '▲' : '▼' }}</button>
        </div>
        <div v-if="expandedSections.batch_procedure_impact" class="card-content-simple">
          <div class="simple-section">
            <div class="simple-label">영향받는 프로시저/함수</div>
            <div class="simple-stat-badge">{{ impactAnalysisResultNew.batch_procedure_impact.affected_procedures || 0 }}건</div>
            <div v-if="impactAnalysisResultNew.batch_procedure_impact.unique_procedures" class="simple-stat-badge-secondary">
              고유 프로시저: {{ impactAnalysisResultNew.batch_procedure_impact.unique_procedures }}개
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.batch_procedure_impact.impacts && impactAnalysisResultNew.batch_procedure_impact.impacts.length > 0" class="simple-section">
            <div class="simple-label">프로시저 상세 ({{ impactAnalysisResultNew.batch_procedure_impact.impacts.length }}건)</div>
            <div class="detail-list">
              <div v-for="(impact, idx) in impactAnalysisResultNew.batch_procedure_impact.impacts" :key="idx" class="detail-item-clean">
                <div class="detail-item-header">
                  <span class="detail-item-value procedure-name">{{ impact.procedure_name }}</span>
                  <span class="detail-item-type-badge" :class="impact.impact_type === 'table_reference' ? 'type-table' : 'type-column'">
                    {{ impact.impact_type === 'table_reference' ? '테이블 참조' : '컬럼 참조' }}
                  </span>
                </div>
                <div class="detail-item-file">{{ impact.file }}</div>
                <div v-if="impact.table" class="detail-item-info">테이블: {{ impact.table }}</div>
                <div v-if="impact.column" class="detail-item-info">컬럼: {{ impact.column }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- PostgreSQL 리니지 -->
      <div v-if="impactAnalysisResultNew.postgresql_lineage" class="impact-card-simple">
        <div class="card-header-simple" @click="toggleSection('postgresql_lineage')">
          <div class="card-title-simple">
            <span class="card-icon-simple">🔗</span>
            <div>
              <div class="card-title-main">PostgreSQL 리니지</div>
              <div class="card-title-sub">{{ impactAnalysisResultNew.postgresql_lineage.summary || '분석 중...' }}</div>
            </div>
          </div>
          <button class="toggle-btn-simple">{{ expandedSections.postgresql_lineage ? '▲' : '▼' }}</button>
        </div>
        <div v-if="expandedSections.postgresql_lineage" class="card-content-simple">
          <div class="simple-section">
            <div class="simple-label">스키마 정보</div>
            <div class="detail-item-clean">
              <span class="detail-item-label">스키마:</span>
              <span class="detail-item-value">{{ impactAnalysisResultNew.postgresql_lineage.postgresql_schema || 'public' }}</span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.postgresql_lineage.columns && impactAnalysisResultNew.postgresql_lineage.columns.length > 0" class="simple-section">
            <div class="simple-label">컬럼 정보 ({{ impactAnalysisResultNew.postgresql_lineage.columns.length }}개)</div>
            <div class="detail-list">
              <div v-for="(col, idx) in impactAnalysisResultNew.postgresql_lineage.columns" :key="idx" class="detail-item-clean">
                <div class="detail-item-header">
                  <span class="detail-item-value">{{ col.name }}</span>
                  <span class="detail-item-type">{{ col.type }}</span>
                  <span class="detail-item-nullable" :class="col.nullable ? 'nullable-yes' : 'nullable-no'">
                    {{ col.nullable ? 'NULL' : 'NOT NULL' }}
                  </span>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="impactAnalysisResultNew.postgresql_lineage.dependencies && impactAnalysisResultNew.postgresql_lineage.dependencies.length > 0" class="simple-section">
            <div class="simple-label">의존성 ({{ impactAnalysisResultNew.postgresql_lineage.dependencies.length }}개)</div>
            <div class="detail-list">
              <div v-for="(dep, idx) in impactAnalysisResultNew.postgresql_lineage.dependencies" :key="idx" class="detail-item-clean">
                <span class="detail-item-value">{{ dep.table }}</span>
                <span class="detail-item-type">{{ dep.relationship }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { getApiUrl } from '../../config/api.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

// AI 테이블 영향도 분석 관련
const impactTableName = ref('')
const impactColumnName = ref('')
const impactSpecialNotes = ref('')
const impactAnalysisResultNew = ref(null)
const isAnalyzingImpactNew = ref(false)
const impactAnalysisErrorNew = ref('')
const expandedSections = ref({
  table_correlation: false,
  program_table_correlation: false,
  program_column_correlation: false,
  ui_impact: false,
  batch_procedure_impact: false,
  postgresql_lineage: false
})

const toggleSection = (section) => {
  expandedSections.value[section] = !expandedSections.value[section]
}

const getTotalImpactCount = () => {
  if (!impactAnalysisResultNew.value) return 0
  let count = 0
  if (impactAnalysisResultNew.value.program_table_correlation) {
    count += impactAnalysisResultNew.value.program_table_correlation.total_references || 0
  }
  if (impactAnalysisResultNew.value.program_column_correlation) {
    count += impactAnalysisResultNew.value.program_column_correlation.total_references || 0
  }
  if (impactAnalysisResultNew.value.ui_impact) {
    count += impactAnalysisResultNew.value.ui_impact.affected_vue_files || 0
  }
  if (impactAnalysisResultNew.value.batch_procedure_impact) {
    count += impactAnalysisResultNew.value.batch_procedure_impact.affected_procedures || 0
  }
  return count
}

const getAffectedFilesCount = () => {
  if (!impactAnalysisResultNew.value) return 0
  const files = new Set()
  if (impactAnalysisResultNew.value.table_correlation?.referenced_files) {
    impactAnalysisResultNew.value.table_correlation.referenced_files.forEach(f => files.add(f))
  }
  if (impactAnalysisResultNew.value.ui_impact?.impacts) {
    impactAnalysisResultNew.value.ui_impact.impacts.forEach(i => files.add(i.file))
  }
  return files.size
}

const getAffectedTablesCount = () => {
  if (!impactAnalysisResultNew.value) return 0
  return impactAnalysisResultNew.value.table_correlation?.related_tables?.length || 0
}

const extractTableAndColumnFromNotes = (notes) => {
  if (!notes) return { table: null, column: null }
  
  let table = null
  let column = null
  
  // "users 테이블의 user_id" 패턴 찾기
  const tableMatch = notes.match(/(\w+)\s*테이블/i)
  if (tableMatch) {
    table = tableMatch[1]
  }
  
  // 컬럼명 추출 패턴들
  // "user_id가" 또는 "user_id 가" 패턴
  const columnPattern1 = notes.match(/(\w+)\s*가/i)
  if (columnPattern1) {
    column = columnPattern1[1]
  }
  
  // "테이블의 user_id" 패턴
  if (!column) {
    const columnPattern2 = notes.match(/테이블의\s+(\w+)/i)
    if (columnPattern2) {
      column = columnPattern2[1]
    }
  }
  
  // "컬럼 user_id" 또는 "항목 user_id" 패턴
  if (!column) {
    const columnPattern3 = notes.match(/(?:컬럼|항목|필드|column)\s+(\w+)/i)
    if (columnPattern3) {
      column = columnPattern3[1]
    }
  }
  
  // 일반적인 컬럼명 패턴 (언더스코어 포함)
  if (!column) {
    const columnPattern4 = notes.match(/\b([a-z_]+_id|[a-z_]+_name|[a-z_]+_date|[a-z_]+_at)\b/i)
    if (columnPattern4) {
      column = columnPattern4[1]
    }
  }
  
  return { table, column }
}

const analyzeImpactNew = async () => {
  // 특이사항에서 테이블명과 컬럼명 추출 시도
  let tableName = impactTableName.value.trim()
  let columnName = impactColumnName.value.trim()
  
  if (impactSpecialNotes.value.trim()) {
    const extracted = extractTableAndColumnFromNotes(impactSpecialNotes.value)
    if (!tableName && extracted.table) {
      tableName = extracted.table
      impactTableName.value = extracted.table
    }
    if (!columnName && extracted.column) {
      columnName = extracted.column
      impactColumnName.value = extracted.column
    }
  }
  
  if (!tableName) {
    impactAnalysisErrorNew.value = '테이블명을 입력해주세요.'
    return
  }
  
  isAnalyzingImpactNew.value = true
  impactAnalysisErrorNew.value = ''
  impactAnalysisResultNew.value = null
  
  try {
    const requestBody = {
      table_name: tableName,
      column_name: columnName || null,
      special_notes: impactSpecialNotes.value.trim() || null
    }
    
    console.log('[프론트엔드] 영향도 분석 요청:', requestBody)
    
    const response = await fetch(getApiUrl('/api/impact/analyze'), {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody)
    })
    
    const data = await response.json()
    console.log('[프론트엔드] 영향도 분석 응답:', data)
    
    if (!response.ok || !data.success) {
      // 에러 응답 처리
      const errorMessage = data.error || data.details || `서버 오류 (${response.status} ${response.statusText})`
      console.error('[프론트엔드] 영향도 분석 오류:', errorMessage)
      
      // stdout/stderr 정보가 있으면 함께 표시
      let fullErrorMessage = errorMessage
      if (data.stdout && typeof data.stdout === 'string') {
        fullErrorMessage += `\n\n출력:\n${data.stdout.substring(0, 500)}`
      }
      if (data.stderr && typeof data.stderr === 'string') {
        fullErrorMessage += `\n\n에러:\n${data.stderr.substring(0, 500)}`
      }
      
      impactAnalysisErrorNew.value = fullErrorMessage
      impactAnalysisResultNew.value = null
      return
    }
    
    if (data.success && data.result) {
      impactAnalysisResultNew.value = data.result
      impactAnalysisErrorNew.value = ''
      // 첫 번째 섹션 자동 확장
      if (data.result.table_correlation) {
        expandedSections.value.table_correlation = true
      }
      console.log('[프론트엔드] 영향도 분석 성공:', data.result)
    } else {
      throw new Error(data.error || '영향도 분석 결과를 받을 수 없습니다.')
    }
  } catch (error) {
    console.error('[프론트엔드] 영향도 분석 오류:', error)
    impactAnalysisErrorNew.value = error.message || '영향도 분석 중 오류가 발생했습니다.'
    impactAnalysisResultNew.value = null
  } finally {
    isAnalyzingImpactNew.value = false
  }
}

const clearImpactAnalysisNew = () => {
  impactTableName.value = ''
  impactColumnName.value = ''
  impactSpecialNotes.value = ''
  impactAnalysisResultNew.value = null
  impactAnalysisErrorNew.value = ''
  // 섹션 접기 상태 초기화
  Object.keys(expandedSections.value).forEach(key => {
    expandedSections.value[key] = false
  })
}

const getImpactLevelClass = (level) => {
  const levelLower = level?.toLowerCase() || ''
  if (levelLower === 'critical') return 'impact-critical'
  if (levelLower === 'high') return 'impact-high'
  if (levelLower === 'medium') return 'impact-medium'
  if (levelLower === 'low') return 'impact-low'
  return ''
}
</script>

<style scoped>
.impact-analysis-container {
  margin-top: 1.5rem;
  padding: 2rem;
  background: white;
  color: #213547;
  border-radius: 16px;
  text-align: left;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  animation: slideDown 0.3s ease;
  width: 100%;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

.impact-analysis-notice {
  text-align: left;
  margin-bottom: 1.5rem;
}

.impact-analysis-notice p {
  text-align: left;
  margin: 0.5rem 0;
  color: #495057;
  font-size: 0.95rem;
  line-height: 1.6;
}

.impact-analysis-container .input-group {
  text-align: left;
  margin-bottom: 1rem;
}

.impact-analysis-container .input-group label {
  text-align: left;
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #213547;
}

.impact-analysis-container .input-field {
  width: 100%;
  text-align: left;
  padding: 0.75rem;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 0.95rem;
  color: #213547;
}

.impact-analysis-container .input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.impact-analysis-container h2 {
  text-align: left;
  margin-top: 0;
  margin-bottom: 1rem;
  color: #213547;
  font-size: 1.5rem;
  font-weight: 700;
}

.impact-analysis-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-start;
  margin-top: 1rem;
}

.btn-analyze-impact {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-analyze-impact:hover:not(:disabled) {
  background: linear-gradient(135deg, #5568d3 0%, #653a8f 100%);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
  transform: translateY(-2px);
}

.btn-analyze-impact:disabled {
  background: #95a5a6;
  cursor: not-allowed;
  box-shadow: none;
  transform: none;
}

.btn-clear-impact {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}

.btn-clear-impact:hover {
  background: linear-gradient(135deg, #c0392b 0%, #a93226 100%);
  box-shadow: 0 6px 16px rgba(231, 76, 60, 0.4);
  transform: translateY(-2px);
}

.impact-analysis-results {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
  text-align: left;
}

.impact-analysis-results h3 {
  text-align: left;
  margin-top: 0;
  margin-bottom: 1.5rem;
  color: #213547;
  font-size: 1.5rem;
  font-weight: 700;
}

.impact-summary-simple {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.summary-main {
  margin-bottom: 1.5rem;
}

.summary-target {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.1rem;
}

.target-label {
  font-weight: 600;
  opacity: 0.9;
}

.target-name {
  font-weight: 700;
  font-size: 1.2rem;
}

.target-column {
  font-weight: 600;
  opacity: 0.9;
}

.impact-overview {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.overview-item {
  text-align: center;
}

.overview-number {
  font-size: 2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.overview-label {
  font-size: 0.9rem;
  opacity: 0.9;
}

.impact-card-simple {
  background: white;
  border-radius: 10px;
  margin-bottom: 1rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  border: 1px solid #e9ecef;
  overflow: hidden;
}

.card-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  cursor: pointer;
  transition: background 0.2s;
}

.card-header-simple:hover {
  background: #f8f9fa;
}

.card-title-simple {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
}

.card-icon-simple {
  font-size: 1.5rem;
}

.card-title-main {
  font-weight: 600;
  font-size: 1rem;
  color: #333;
}

.card-title-sub {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}

.toggle-btn-simple {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  color: #666;
  padding: 0.25rem 0.5rem;
}

.card-content-simple {
  padding: 1rem 1.25rem;
  border-top: 1px solid #e9ecef;
}

.simple-section {
  margin-bottom: 1rem;
}

.simple-label {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.5rem;
  display: block;
  font-size: 0.9rem;
}

.simple-stat-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #667eea;
  color: white;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 0.25rem;
}

.simple-stat-badge-secondary {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  background: #e9ecef;
  color: #333;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  margin-top: 0.25rem;
  margin-left: 0.5rem;
}

.simple-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1rem;
}

.simple-stat {
  text-align: center;
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-number {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  color: #667eea;
}

.stat-label {
  display: block;
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.25rem;
}

.detail-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.detail-item-clean {
  padding: 0.75rem;
  background: #f8f9fa;
  border-radius: 6px;
  border-left: 3px solid #667eea;
}

.detail-item-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.detail-item-file {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #333;
  font-weight: 600;
}

.detail-item-line {
  font-size: 0.8rem;
  color: #666;
}

.detail-item-label {
  font-weight: 600;
  color: #333;
}

.detail-item-value {
  color: #667eea;
  font-weight: 600;
}

.detail-item-type {
  padding: 0.2rem 0.5rem;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 0.75rem;
  color: #666;
}

.detail-item-type-badge {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.detail-item-type-badge.type-table {
  background: #fff3cd;
  color: #856404;
}

.detail-item-type-badge.type-column {
  background: #d1ecf1;
  color: #0c5460;
}

.detail-item-info {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}

.detail-item-context {
  font-family: 'Courier New', monospace;
  font-size: 0.8rem;
  color: #666;
  margin-top: 0.5rem;
  padding: 0.5rem;
  background: white;
  border-radius: 4px;
}

.detail-item-nullable {
  padding: 0.2rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
}

.detail-item-nullable.nullable-yes {
  background: #d4edda;
  color: #155724;
}

.detail-item-nullable.nullable-no {
  background: #f8d7da;
  color: #721c24;
}

.procedure-name {
  font-weight: 700;
  font-size: 1rem;
}

.simple-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.simple-tag {
  padding: 0.25rem 0.75rem;
  background: #667eea;
  color: white;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
}

.simple-files {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.simple-file {
  font-family: 'Courier New', monospace;
  font-size: 0.85rem;
  color: #333;
  padding: 0.5rem;
  background: #f8f9fa;
  border-radius: 4px;
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

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.btn-icon {
  font-size: 18px;
}

.btn-text {
  font-size: 16px;
}
</style>


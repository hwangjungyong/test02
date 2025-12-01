<template>
  <div v-if="modelValue" class="sql-query-analysis-container">
    <h2>📊 AI 데이터 분석</h2>
    <div class="sql-analysis-notice">
      <p>ℹ️ PostgreSQL 쿼리를 분석하여 구조, 성능, 복잡도, 보안을 평가하고 최적화 제안을 제공합니다.</p>
    </div>
    
    <div class="input-group">
      <label for="sqlQueryFile">SQL 파일 경로 (선택사항):</label>
      <input
        id="sqlQueryFile"
        v-model="sqlQueryFile"
        type="text"
        placeholder="예: queries/complex_query.sql"
        class="input-field"
      />
    </div>
    
    <div class="input-group">
      <label for="sqlQueryText" style="font-size: 16px; font-weight: 600; margin-bottom: 0.75rem; display: block; color: #333;">
        SQL 쿼리 입력:
      </label>
      <textarea
        id="sqlQueryText"
        v-model="sqlQueryText"
        placeholder="SELECT * FROM users WHERE id = 1;&#10;&#10;또는 복잡한 쿼리를 붙여넣으세요..."
        class="sql-query-textarea"
        rows="25"
      ></textarea>
    </div>
    
    <div class="sql-analysis-actions">
      <button @click="analyzeSQLQuery" class="btn-analyze-sql" :disabled="isAnalyzingSQL">
        <span class="btn-icon" v-if="!isAnalyzingSQL">🔍</span>
        <span class="loading-spinner" v-if="isAnalyzingSQL"></span>
        <span class="btn-text">
          <span v-if="!isAnalyzingSQL">AI 쿼리 분석하기</span>
          <span v-else>분석 중...</span>
        </span>
      </button>
      <button @click="clearSQLAnalysis" class="btn-clear-sql">
        <span class="btn-icon">🗑️</span>
        <span class="btn-text">초기화</span>
      </button>
    </div>
    
    <div v-if="sqlAnalysisError" class="error">
      <p>{{ sqlAnalysisError }}</p>
    </div>
    
    <div v-if="sqlAnalysisResult" class="sql-analysis-results">
      <h3>분석 결과</h3>
      
      <!-- 리니지 정보 - 맨 위에 표시 -->
      <div v-if="sqlAnalysisResult && sqlAnalysisResult.lineage" class="analysis-section lineage-section-featured">
        <div class="lineage-header-with-action">
          <h4>🔗 데이터 리니지 정보</h4>
          <button 
            @click="scrollToLineageVisualization" 
            class="btn btn-lineage-quick-access"
            v-if="sqlAnalysisReport && sqlAnalysisReport.lineageHtmlPath"
          >
            📊 리니지 연관도 바로가기
          </button>
        </div>
        
        <!-- 리니지 연관도 요약 -->
        <div v-if="calculateLineageConnectivity()" class="lineage-connectivity-summary">
          <div class="connectivity-info">
            <span class="connectivity-label">리니지 연관도:</span>
            <span class="connectivity-value" :class="getConnectivityClass(calculateLineageConnectivity())">
              {{ calculateLineageConnectivity() }}%
            </span>
            <span class="connectivity-details">
              (테이블: {{ sqlAnalysisResult.lineage.tables?.length || 0 }}개, 
              JOIN: {{ sqlAnalysisResult.lineage.join_relationships?.length || 0 }}개,
              CTE: {{ sqlAnalysisResult.lineage.ctes?.length || 0 }}개)
            </span>
          </div>
          <div class="connectivity-bar">
            <div 
              class="connectivity-fill" 
              :style="{ width: calculateLineageConnectivity() + '%' }"
              :class="getConnectivityClass(calculateLineageConnectivity())"
            ></div>
          </div>
        </div>
        
        <!-- 테이블 목록 -->
        <div v-if="sqlAnalysisResult.lineage.tables && sqlAnalysisResult.lineage.tables.length > 0" class="lineage-info-block">
          <h5>📊 테이블 목록</h5>
          <div class="lineage-tags">
            <span v-for="(table, index) in sqlAnalysisResult.lineage.tables" :key="index" class="lineage-tag table-tag">
              {{ table }}
            </span>
          </div>
        </div>
        
        <!-- CTE 목록 -->
        <div v-if="sqlAnalysisResult.lineage.ctes && sqlAnalysisResult.lineage.ctes.length > 0" class="lineage-info-block">
          <h5>📝 CTE 목록</h5>
          <div class="lineage-tags">
            <span v-for="(cte, index) in sqlAnalysisResult.lineage.ctes" :key="index" class="lineage-tag cte-tag">
              {{ cte }}
            </span>
          </div>
        </div>
        
        <!-- JOIN 관계 -->
        <div v-if="sqlAnalysisResult.lineage.join_relationships && sqlAnalysisResult.lineage.join_relationships.length > 0" class="lineage-info-block">
          <h5>🔗 JOIN 관계 ({{ sqlAnalysisResult.lineage.join_relationships.length }}개)</h5>
          <div class="join-relationships-list">
            <div v-for="(join, index) in sqlAnalysisResult.lineage.join_relationships" :key="index" class="join-item">
              <div class="join-header">
                <span class="join-type" :class="getJoinTypeClass(join.join_type)">{{ join.join_type }}</span>
                <span class="join-tables">
                  <strong>{{ join.left_table || 'unknown' }}</strong> → <strong>{{ join.right_table || 'unknown' }}</strong>
                </span>
              </div>
              <div v-if="join.condition" class="join-condition">
                조건: <code>{{ join.condition }}</code>
              </div>
            </div>
          </div>
        </div>
        
        <!-- CTE 의존성 -->
        <div v-if="sqlAnalysisResult.lineage.cte_dependencies && sqlAnalysisResult.lineage.cte_dependencies.length > 0" class="lineage-info-block">
          <h5>📋 CTE 의존성</h5>
          <div class="join-relationships-list">
            <div v-for="(dep, index) in sqlAnalysisResult.lineage.cte_dependencies" :key="index" class="join-item">
              <span class="join-tables">
                <strong>{{ dep.cte_name }}</strong> ← {{ dep.referenced_cte || dep.referenced_table }}
              </span>
            </div>
          </div>
        </div>
        
        <!-- 서브쿼리 관계 -->
        <div v-if="sqlAnalysisResult.lineage.subquery_relationships && sqlAnalysisResult.lineage.subquery_relationships.length > 0" class="lineage-info-block">
          <h5>🔍 서브쿼리 관계</h5>
          <div class="join-relationships-list">
            <div v-for="(subq, index) in sqlAnalysisResult.lineage.subquery_relationships" :key="index" class="join-item">
              <span class="join-tables">
                위치: {{ subq.location }}, 깊이: {{ subq.depth }}, 참조 테이블: {{ subq.referenced_tables?.join(', ') || '없음' }}
              </span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 테이블 관계 그래프 - 선택적 표시 -->
      <div v-if="sqlAnalysisResult && sqlAnalysisResult.lineage && sqlAnalysisResult.lineage.join_relationships && sqlAnalysisResult.lineage.join_relationships.length > 0" class="analysis-section graph-section-featured">
        <div class="graph-header">
          <h4>📈 테이블 관계 그래프</h4>
          <p class="graph-subtitle">쿼리의 테이블 간 JOIN 관계를 시각화합니다</p>
        </div>
        <div class="table-relationship-graph-container featured-graph">
          <div ref="sqlTableGraphContainer" class="sql-table-graph featured"></div>
          <div class="graph-legend">
            <div class="legend-item">
              <span class="legend-color" style="background: #4a90e2;"></span>
              <span>테이블</span>
            </div>
            <div class="legend-item">
              <span class="legend-color" style="background: #f5576c;"></span>
              <span>CTE</span>
            </div>
            <div class="legend-item">
              <span class="legend-line" style="border-top: 2px solid #4a90e2;"></span>
              <span>LEFT JOIN</span>
            </div>
            <div class="legend-item">
              <span class="legend-line" style="border-top: 2px solid #f5576c;"></span>
              <span>INNER JOIN</span>
            </div>
            <div class="legend-item">
              <span class="legend-line" style="border-top: 2px dashed #4a90e2;"></span>
              <span>FULL OUTER JOIN</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 요약 정보 -->
      <div class="analysis-summary">
        <h4>📋 실행 요약</h4>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">성능 점수</span>
            <span class="summary-value" :class="getScoreClass(sqlAnalysisResult.performance?.score)">
              {{ sqlAnalysisResult.performance?.score || 0 }}/100
            </span>
            <span class="summary-level">{{ sqlAnalysisResult.performance?.level || 'N/A' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">복잡도 점수</span>
            <span class="summary-value" :class="getScoreClass(sqlAnalysisResult.complexity?.score, true)">
              {{ sqlAnalysisResult.complexity?.score || 0 }}/100
            </span>
            <span class="summary-level">{{ sqlAnalysisResult.complexity?.level || 'N/A' }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">보안 점수</span>
            <span class="summary-value" :class="getScoreClass(sqlAnalysisResult.security?.score)">
              {{ sqlAnalysisResult.security?.score || 0 }}/100
            </span>
            <span class="summary-level">{{ sqlAnalysisResult.security?.level || 'N/A' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 구조 분석 -->
      <div v-if="sqlAnalysisResult.structure" class="analysis-section">
        <h4>📐 쿼리 구조 분석</h4>
        <div class="structure-info">
          <p><strong>쿼리 타입:</strong> {{ sqlAnalysisResult.structure.query_type }}</p>
          <p><strong>테이블 수:</strong> {{ sqlAnalysisResult.structure.table_count }}개</p>
          <p><strong>컬럼 수:</strong> {{ sqlAnalysisResult.structure.column_count }}개</p>
          <p><strong>JOIN 수:</strong> {{ sqlAnalysisResult.structure.join_count }}개</p>
          <p><strong>서브쿼리 수:</strong> {{ sqlAnalysisResult.structure.subquery_count }}개</p>
          <p><strong>최대 서브쿼리 깊이:</strong> {{ sqlAnalysisResult.structure.max_subquery_depth }}</p>
          <p><strong>쿼리 길이:</strong> {{ sqlAnalysisResult.structure.query_length }} 문자, {{ sqlAnalysisResult.structure.query_lines }} 라인</p>
        </div>
      </div>
      
      <!-- 성능 분석 -->
      <div v-if="sqlAnalysisResult.performance" class="analysis-section">
        <h4>⚡ 성능 분석</h4>
        <div v-if="sqlAnalysisResult.performance.issues && sqlAnalysisResult.performance.issues.length > 0">
          <h5>성능 이슈:</h5>
          <ul>
            <li v-for="(issue, index) in sqlAnalysisResult.performance.issues" :key="index">
              <strong>[{{ issue.severity }}]</strong> {{ issue.type }}: {{ issue.message }}
              <br><small>영향: {{ issue.impact }}</small>
            </li>
          </ul>
        </div>
        <div v-else>
          <p>성능 이슈가 발견되지 않았습니다.</p>
        </div>
      </div>
      
      <!-- 보안 분석 -->
      <div v-if="sqlAnalysisResult.security" class="analysis-section">
        <h4>🔒 보안 분석</h4>
        <div v-if="sqlAnalysisResult.security.vulnerabilities && sqlAnalysisResult.security.vulnerabilities.length > 0">
          <h5>보안 취약점:</h5>
          <ul>
            <li v-for="(vuln, index) in sqlAnalysisResult.security.vulnerabilities" :key="index">
              <strong>[{{ vuln.severity }}]</strong> {{ vuln.type }}: {{ vuln.message }}
              <br><small>영향: {{ vuln.impact }}</small>
              <br><small>권장사항: {{ vuln.recommendation }}</small>
            </li>
          </ul>
        </div>
        <div v-else>
          <p>보안 취약점이 발견되지 않았습니다.</p>
        </div>
      </div>
      
      <!-- 최적화 제안 -->
      <div v-if="sqlAnalysisResult.optimization" class="analysis-section">
        <h4>💡 최적화 제안</h4>
        <div v-if="sqlAnalysisResult.optimization.suggestions && sqlAnalysisResult.optimization.suggestions.length > 0">
          <div v-for="(suggestion, index) in sqlAnalysisResult.optimization.suggestions" :key="index" class="suggestion-item">
            <strong>[{{ suggestion.priority }}]</strong> {{ suggestion.type }}: {{ suggestion.message }}
            <div v-if="suggestion.example" class="suggestion-example">
              <strong>예시:</strong> <code>{{ suggestion.example }}</code>
            </div>
            <div v-if="suggestion.expected_improvement" class="suggestion-improvement">
              <strong>예상 개선율:</strong> {{ suggestion.expected_improvement }}
            </div>
          </div>
        </div>
        <div v-else>
          <p>최적화 제안이 없습니다.</p>
        </div>
      </div>
      
      <!-- 리포트 다운로드 -->
      <div class="analysis-actions">
        <button @click="downloadSQLReport('json')" class="btn btn-download">
          📥 JSON 리포트 다운로드
        </button>
        <button @click="downloadSQLReport('markdown')" class="btn btn-download">
          📥 마크다운 리포트 다운로드
        </button>
        
        <!-- 리니지 생성 중 프로그레스 -->
        <div v-if="isGeneratingLineage" class="lineage-generation-progress">
          <div class="progress-label">리니지 시각화 생성 중...</div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" :style="{ width: lineageGenerationProgress + '%' }"></div>
          </div>
          <div class="progress-percentage">{{ Math.round(lineageGenerationProgress) }}%</div>
        </div>
        
        <button 
          v-if="sqlAnalysisReport && sqlAnalysisReport.lineageHtmlPath && !isGeneratingLineage" 
          @click="scrollToLineageVisualization" 
          class="btn btn-lineage-quick-access"
        >
          📊 리니지 연관도 바로가기
        </button>
        <button 
          v-if="sqlAnalysisReport && sqlAnalysisReport.lineageHtmlPath && !isGeneratingLineage" 
          @click="toggleLineageVisualization" 
          class="btn btn-open-lineage"
        >
          {{ showLineageVisualization ? '🔽 리니지 시각화 숨기기' : '🌐 리니지 시각화 보기' }}
        </button>
      </div>
      
      <!-- 리니지 시각화 영역 -->
      <div v-if="showLineageVisualization && sqlAnalysisReport && sqlAnalysisReport.lineageHtmlPath" class="lineage-visualization-container">
        <div class="lineage-visualization-header">
          <h4>📊 데이터 리니지 시각화</h4>
          <button @click="showLineageVisualization = false" class="btn-close-visualization">✕</button>
        </div>
        <div class="lineage-visualization-content">
          <div v-if="lineageHtmlContent" v-html="lineageHtmlContent" class="lineage-html-content"></div>
          <div v-else class="lineage-loading">
            <p>리니지 시각화를 불러오는 중...</p>
          </div>
        </div>
      </div>
      
      <!-- 영향도 분석 섹션 -->
      <div v-if="sqlAnalysisResult && sqlAnalysisResult.lineage" class="impact-analysis-section">
        <div class="impact-analysis-header">
          <h4>🔍 영향도 분석</h4>
          <p class="impact-analysis-description">
            특정 테이블 또는 컬럼에 이슈가 발생했을 때 영향받는 쿼리를 분석합니다.
          </p>
        </div>
        
        <div class="impact-analysis-inputs">
          <div class="input-group">
            <label for="impactTargetTable">분석 대상 테이블:</label>
            <select
              id="impactTargetTable"
              v-model="impactTargetTable"
              class="input-field"
            >
              <option value="">테이블 선택</option>
              <option v-for="table in sqlAnalysisResult.lineage.tables" :key="table" :value="table">
                {{ table }}
              </option>
            </select>
          </div>
          
          <div class="input-group">
            <label for="impactTargetColumn">분석 대상 컬럼 (선택사항):</label>
            <input
              id="impactTargetColumn"
              v-model="impactTargetColumn"
              type="text"
              placeholder="컬럼명 입력"
              class="input-field"
            />
          </div>
          
          <div class="impact-analysis-actions">
            <button 
              @click="analyzeImpact" 
              class="btn-analyze-impact" 
              :disabled="isAnalyzingImpact || !impactTargetTable"
            >
              <span class="btn-icon" v-if="!isAnalyzingImpact">🔍</span>
              <span class="loading-spinner" v-if="isAnalyzingImpact"></span>
              <span class="btn-text">
                <span v-if="!isAnalyzingImpact">영향도 분석하기</span>
                <span v-else>분석 중...</span>
              </span>
            </button>
            <button 
              @click="clearImpactAnalysis" 
              class="btn-clear-impact"
              v-if="impactAnalysisResult"
            >
              <span class="btn-icon">🗑️</span>
              <span class="btn-text">초기화</span>
            </button>
          </div>
        </div>
        
        <div v-if="impactAnalysisError" class="error">
          <p>{{ impactAnalysisError }}</p>
        </div>
        
        <div v-if="impactAnalysisResult" class="impact-analysis-results">
          <h5>영향도 분석 결과</h5>
          
          <div class="impact-summary">
            <div class="impact-summary-item">
              <span class="impact-summary-label">영향도 수준:</span>
              <span class="impact-summary-value" :class="getImpactLevelClass(impactAnalysisResult.impact_level)">
                {{ impactAnalysisResult.impact_level }}
              </span>
            </div>
            <div class="impact-summary-item">
              <span class="impact-summary-label">영향도 점수:</span>
              <span class="impact-summary-value">{{ impactAnalysisResult.impact_score }}/100</span>
            </div>
            <div class="impact-summary-item">
              <span class="impact-summary-label">직접 영향:</span>
              <span class="impact-summary-value">{{ impactAnalysisResult.statistics.total_direct_impacts }}개</span>
            </div>
            <div class="impact-summary-item">
              <span class="impact-summary-label">간접 영향:</span>
              <span class="impact-summary-value">{{ impactAnalysisResult.statistics.total_indirect_impacts }}개</span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResult.direct_impacts && impactAnalysisResult.direct_impacts.length > 0" class="impact-list">
            <h6>직접 영향</h6>
            <div class="impact-items">
              <div 
                v-for="(impact, index) in impactAnalysisResult.direct_impacts" 
                :key="index" 
                class="impact-item"
                :class="getImpactLevelClass(impact.impact_level)"
              >
                <div class="impact-item-header">
                  <span class="impact-type">{{ impact.type }}</span>
                  <span class="impact-level">{{ impact.impact_level }}</span>
                  <span class="impact-location">{{ impact.location }}</span>
                </div>
                <div class="impact-snippet">{{ impact.query_snippet }}</div>
              </div>
            </div>
          </div>
          
          <div v-if="impactAnalysisResult.indirect_impacts && impactAnalysisResult.indirect_impacts.length > 0" class="impact-list">
            <h6>간접 영향</h6>
            <div class="impact-items">
              <div 
                v-for="(impact, index) in impactAnalysisResult.indirect_impacts" 
                :key="index" 
                class="impact-item indirect"
              >
                <div class="impact-item-header">
                  <span class="impact-type">{{ impact.type }}</span>
                  <span class="impact-level">{{ impact.impact_level }}</span>
                </div>
                <div class="impact-path">{{ impact.path }}</div>
                <div v-if="impact.related_table" class="impact-related">
                  관련 테이블: {{ impact.related_table }}
                </div>
                <div v-if="impact.cte_name" class="impact-related">
                  관련 CTE: {{ impact.cte_name }}
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="impactAnalysisResult.affected_tables && impactAnalysisResult.affected_tables.length > 0" class="impact-affected">
            <h6>영향받는 테이블</h6>
            <div class="impact-tags">
              <span 
                v-for="(table, index) in impactAnalysisResult.affected_tables" 
                :key="index" 
                class="impact-tag"
              >
                {{ table }}
              </span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResult.affected_ctes && impactAnalysisResult.affected_ctes.length > 0" class="impact-affected">
            <h6>영향받는 CTE</h6>
            <div class="impact-tags">
              <span 
                v-for="(cte, index) in impactAnalysisResult.affected_ctes" 
                :key="index" 
                class="impact-tag cte-tag"
              >
                {{ cte }}
              </span>
            </div>
          </div>
          
          <div v-if="impactAnalysisResult.recommendations && impactAnalysisResult.recommendations.length > 0" class="impact-recommendations">
            <h6>권장사항</h6>
            <div class="recommendation-items">
              <div 
                v-for="(rec, index) in impactAnalysisResult.recommendations" 
                :key="index" 
                class="recommendation-item"
                :class="rec.priority.toLowerCase()"
              >
                <div class="recommendation-priority">{{ rec.priority }}</div>
                <div class="recommendation-message">{{ rec.message }}</div>
                <div class="recommendation-action">{{ rec.action }}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { Network } from 'vis-network'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const sqlQueryFile = ref('')
const sqlQueryText = ref('')
const isAnalyzingSQL = ref(false)
const sqlAnalysisError = ref('')
const sqlAnalysisResult = ref(null)
const sqlAnalysisReport = ref(null)
const impactAnalysisResult = ref(null)
const isAnalyzingImpact = ref(false)
const impactAnalysisError = ref('')
const impactTargetTable = ref('')
const impactTargetColumn = ref('')
const showLineageVisualization = ref(false)
const lineageHtmlContent = ref('')
const isGeneratingLineage = ref(false)
const lineageGenerationProgress = ref(0)
const sqlTableGraphContainer = ref(null)
let sqlTableGraphInstance = null

const analyzeSQLQuery = async () => {
  if (!sqlQueryText.value.trim() && !sqlQueryFile.value.trim()) {
    sqlAnalysisError.value = 'SQL 쿼리 또는 파일 경로를 입력해주세요.'
    return
  }
  
  isAnalyzingSQL.value = true
  sqlAnalysisError.value = ''
  sqlAnalysisResult.value = null
  
  try {
    const requestBody = {
      query_file: sqlQueryFile.value.trim() || null,
      query_text: sqlQueryText.value.trim() || null,
      output_format: 'both'
    }
    
    console.log('[프론트엔드] SQL 쿼리 분석 요청:', requestBody)
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 300000)
    
    const response = await fetch('/api/sql/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal
    }).finally(() => {
      clearTimeout(timeoutId)
    })
    
    if (!response.ok) {
      let errorData
      try {
        errorData = await response.json()
      } catch (e) {
        errorData = { error: `서버 오류 (${response.status} ${response.statusText})` }
      }
      throw new Error(errorData.error || `서버 오류 (${response.status})`)
    }
    
    const data = await response.json()
    
    if (data.success) {
      sqlAnalysisResult.value = data.result
      sqlAnalysisReport.value = data.report ? JSON.parse(JSON.stringify(data.report)) : null
      
      if (data.report && data.report.lineageHtmlPath) {
        isGeneratingLineage.value = false
        lineageGenerationProgress.value = 100
        await loadLineageVisualization(data.report.lineageHtmlPath)
      } else {
        isGeneratingLineage.value = true
        lineageGenerationProgress.value = 50
        await waitForLineageFile()
      }
      
      await nextTick()
      setTimeout(() => {
        if (data.result.lineage && data.result.lineage.join_relationships && data.result.lineage.join_relationships.length > 0) {
          renderSQLTableGraph(data.result.lineage)
        }
      }, 100)
    } else {
      sqlAnalysisError.value = data.error || '쿼리 분석에 실패했습니다.'
    }
  } catch (error) {
    console.error('SQL 쿼리 분석 오류:', error)
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      sqlAnalysisError.value = `API 서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인하세요. (포트 3001)\n\n오류: ${error.message}`
    } else {
      sqlAnalysisError.value = `쿼리 분석 중 오류가 발생했습니다: ${error.message}`
    }
  } finally {
    isAnalyzingSQL.value = false
  }
}

const clearSQLAnalysis = () => {
  sqlQueryFile.value = ''
  sqlQueryText.value = ''
  sqlAnalysisError.value = ''
  sqlAnalysisResult.value = null
  sqlAnalysisReport.value = null
  showLineageVisualization.value = false
  clearImpactAnalysis()
  
  if (sqlTableGraphInstance) {
    sqlTableGraphInstance.destroy()
    sqlTableGraphInstance = null
  }
}

const renderSQLTableGraph = (lineage) => {
  if (!sqlTableGraphContainer.value || !lineage) return
  
  if (sqlTableGraphInstance) {
    sqlTableGraphInstance.destroy()
    sqlTableGraphInstance = null
  }
  
  const nodes = []
  const edges = []
  const nodeMap = new Map()
  
  if (lineage.tables && lineage.tables.length > 0) {
    lineage.tables.forEach((table, index) => {
      const nodeId = `table_${index}`
      nodeMap.set(table, nodeId)
      nodes.push({
        id: nodeId,
        label: table,
        color: {
          background: '#4a90e2',
          border: '#357abd',
          highlight: {
            background: '#5ba3f5',
            border: '#4a90e2'
          }
        },
        font: { color: '#ffffff', size: 14, face: 'Arial' },
        shape: 'box',
        margin: 10
      })
    })
  }
  
  if (lineage.ctes && lineage.ctes.length > 0) {
    lineage.ctes.forEach((cte, index) => {
      const nodeId = `cte_${index}`
      nodeMap.set(cte, nodeId)
      nodes.push({
        id: nodeId,
        label: cte,
        color: {
          background: '#f5576c',
          border: '#d32f2f',
          highlight: {
            background: '#ff6b7a',
            border: '#f5576c'
          }
        },
        font: { color: '#ffffff', size: 14, face: 'Arial' },
        shape: 'ellipse',
        margin: 10
      })
    })
  }
  
  if (lineage.join_relationships && lineage.join_relationships.length > 0) {
    lineage.join_relationships.forEach((join, index) => {
      const leftTable = join.left_table || 'unknown'
      const rightTable = join.right_table || 'unknown'
      const joinType = join.join_type || 'JOIN'
      
      let edgeColor = '#4a90e2'
      let edgeStyle = 'solid'
      
      if (joinType.includes('LEFT')) {
        edgeColor = '#4a90e2'
      } else if (joinType.includes('INNER')) {
        edgeColor = '#f5576c'
      } else if (joinType.includes('FULL OUTER') || joinType.includes('OUTER')) {
        edgeColor = '#4a90e2'
        edgeStyle = 'dashed'
      } else if (joinType.includes('RIGHT')) {
        edgeColor = '#ff9800'
      }
      
      edges.push({
        from: nodeMap.get(leftTable) || `unknown_${index}_left`,
        to: nodeMap.get(rightTable) || `unknown_${index}_right`,
        label: joinType,
        color: { color: edgeColor, highlight: edgeColor, hover: edgeColor },
        dashes: edgeStyle === 'dashed',
        width: 2,
        arrows: { to: { enabled: true, scaleFactor: 0.8 } },
        font: { color: '#666', size: 10, align: 'middle' },
        smooth: { type: 'curvedCW', roundness: 0.2 }
      })
    })
  }
  
  const graphData = { nodes, edges }
  const options = {
    nodes: {
      borderWidth: 2,
      shadow: true,
      font: { size: 14, face: 'Arial' }
    },
    edges: {
      width: 2,
      shadow: true,
      smooth: { type: 'curvedCW', roundness: 0.2 },
      font: { size: 10, align: 'middle' }
    },
    physics: {
      enabled: true,
      stabilization: { enabled: true, iterations: 200 },
      barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.1,
        springLength: 200,
        springConstant: 0.04,
        damping: 0.09
      }
    },
    interaction: {
      hover: true,
      tooltipDelay: 100,
      zoomView: true,
      dragView: true
    }
  }
  
  try {
    sqlTableGraphInstance = new Network(sqlTableGraphContainer.value, graphData, options)
    sqlTableGraphInstance.on('click', (params) => {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0]
        const node = nodes.find(n => n.id === nodeId)
        if (node && node.label) {
          const tableName = node.label.replace(' (CTE)', '').trim()
          impactTargetTable.value = tableName
          impactTargetColumn.value = ''
          analyzeImpact()
        }
      }
    })
  } catch (error) {
    console.error('[그래프 렌더링] 오류:', error)
  }
}

watch(() => sqlAnalysisResult.value?.lineage, async (lineage) => {
  if (lineage) {
    await nextTick()
    setTimeout(() => {
      renderSQLTableGraph(lineage)
    }, 300)
  }
}, { deep: true, immediate: true })

const getJoinTypeClass = (joinType) => {
  if (!joinType) return ''
  const type = joinType.toUpperCase()
  if (type.includes('LEFT')) return 'join-type-left'
  if (type.includes('INNER')) return 'join-type-inner'
  if (type.includes('FULL OUTER') || type.includes('OUTER')) return 'join-type-outer'
  if (type.includes('RIGHT')) return 'join-type-right'
  return 'join-type-default'
}

const getScoreClass = (score, isComplexity = false) => {
  if (score === null || score === undefined) return ''
  if (isComplexity) {
    if (score >= 70) return 'score-very-high'
    if (score >= 50) return 'score-high'
    if (score >= 30) return 'score-medium'
    return 'score-low'
  } else {
    if (score >= 80) return 'score-excellent'
    if (score >= 60) return 'score-good'
    if (score >= 40) return 'score-medium'
    return 'score-low'
  }
}

const downloadSQLReport = (format) => {
  if (!sqlAnalysisReport.value) {
    alert('다운로드할 리포트가 없습니다.')
    return
  }
  
  const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5)
  const filename = `sql_analysis_${timestamp}.${format === 'json' ? 'json' : 'md'}`
  
  let content = ''
  let mimeType = ''
  
  if (format === 'json') {
    content = JSON.stringify(sqlAnalysisReport.value, null, 2)
    mimeType = 'application/json'
  } else {
    content = sqlAnalysisReport.value.markdown || ''
    mimeType = 'text/markdown'
  }
  
  const blob = new Blob([content], { type: mimeType })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
}

const waitForLineageFile = async () => {
  const maxWaitTime = 15000
  const checkInterval = 1000
  const startTime = Date.now()
  
  lineageGenerationProgress.value = 30
  
  while (Date.now() - startTime < maxWaitTime) {
    await new Promise(resolve => setTimeout(resolve, checkInterval))
    const elapsed = Date.now() - startTime
    const progress = Math.min(30 + (elapsed / maxWaitTime * 60), 90)
    lineageGenerationProgress.value = progress
    
    if (elapsed % 3000 < checkInterval) {
      try {
        const queryFile = sqlQueryFile.value || null
        const queryText = sqlQueryText.value || null
        
        if (queryFile || queryText) {
          const checkResponse = await fetch('/api/sql/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              query_file: queryFile,
              query_text: queryText,
              output_format: 'json'
            })
          })
          
          if (checkResponse.ok) {
            const checkData = await checkResponse.json()
            if (checkData.report && checkData.report.lineageHtmlPath) {
              isGeneratingLineage.value = false
              lineageGenerationProgress.value = 100
              if (!sqlAnalysisReport.value) {
                sqlAnalysisReport.value = {}
              }
              sqlAnalysisReport.value.lineageHtmlPath = checkData.report.lineageHtmlPath
              await loadLineageVisualization(checkData.report.lineageHtmlPath)
              return
            }
          }
        }
      } catch (error) {
        console.warn('[프론트엔드] 리니지 파일 확인 중 오류:', error)
      }
    }
  }
  
  if (sqlAnalysisReport.value && sqlAnalysisReport.value.lineageHtmlPath) {
    isGeneratingLineage.value = false
    lineageGenerationProgress.value = 100
    await loadLineageVisualization(sqlAnalysisReport.value.lineageHtmlPath)
    return
  }
  
  isGeneratingLineage.value = false
  lineageGenerationProgress.value = 100
}

const loadLineageVisualization = async (htmlPath) => {
  if (!htmlPath) return
  
  try {
    let fileUrl = htmlPath.replace(/\\/g, '/')
    
    if (fileUrl.startsWith('/api/lineage/')) {
      fileUrl = `${window.location.origin}${fileUrl}`
    } else if (!fileUrl.startsWith('http://') && !fileUrl.startsWith('https://')) {
      if (fileUrl.startsWith('/')) {
        fileUrl = `${window.location.origin}${fileUrl}`
      } else {
        fileUrl = `${window.location.origin}/api/lineage/${fileUrl}`
      }
    }
    
    const response = await fetch(fileUrl)
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const htmlContent = await response.text()
    if (!htmlContent || htmlContent.trim().length === 0) {
      throw new Error('HTML 내용이 비어있습니다.')
    }
    
    lineageHtmlContent.value = htmlContent
    showLineageVisualization.value = true
    
    setTimeout(() => {
      const container = document.querySelector('.lineage-visualization-container')
      if (container) {
        container.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }, 300)
  } catch (error) {
    console.error('[프론트엔드] 리니지 HTML 로드 실패:', error)
    showLineageVisualization.value = false
    isGeneratingLineage.value = false
  }
}

const calculateLineageConnectivity = () => {
  if (!sqlAnalysisResult.value || !sqlAnalysisResult.value.lineage) {
    return 0
  }
  
  const lineage = sqlAnalysisResult.value.lineage
  const tableCount = lineage.tables?.length || 0
  const cteCount = lineage.ctes?.length || 0
  const joinCount = lineage.join_relationships?.length || 0
  const totalNodes = tableCount + cteCount
  
  if (totalNodes === 0) {
    return 0
  }
  
  const maxPossibleJoins = totalNodes * (totalNodes - 1) / 2
  if (maxPossibleJoins === 0) {
    return 0
  }
  
  const connectivity = Math.round((joinCount / maxPossibleJoins) * 100)
  return Math.min(connectivity, 100)
}

const getConnectivityClass = (connectivity) => {
  if (connectivity >= 75) {
    return 'connectivity-high'
  } else if (connectivity >= 50) {
    return 'connectivity-medium'
  } else if (connectivity >= 30) {
    return 'connectivity-low-medium'
  } else {
    return 'connectivity-low'
  }
}

const scrollToLineageVisualization = async () => {
  if (!sqlAnalysisReport.value || !sqlAnalysisReport.value.lineageHtmlPath) {
    alert('리니지 리포트 파일을 찾을 수 없습니다.')
    return
  }
  
  if (!showLineageVisualization.value) {
    await loadLineageVisualization(sqlAnalysisReport.value.lineageHtmlPath)
  }
  
  setTimeout(() => {
    const container = document.querySelector('.lineage-visualization-container')
    if (container) {
      container.scrollIntoView({ behavior: 'smooth', block: 'start' })
    }
  }, 300)
}

const toggleLineageVisualization = async () => {
  if (!sqlAnalysisReport.value || !sqlAnalysisReport.value.lineageHtmlPath) {
    alert('리니지 리포트 파일을 찾을 수 없습니다.')
    return
  }
  
  if (showLineageVisualization.value) {
    showLineageVisualization.value = false
    lineageHtmlContent.value = ''
    return
  }
  
  await loadLineageVisualization(sqlAnalysisReport.value.lineageHtmlPath)
}

const analyzeImpact = async () => {
  if (!impactTargetTable.value.trim()) {
    impactAnalysisError.value = '분석 대상 테이블을 선택해주세요.'
    return
  }
  
  if (!sqlQueryFile.value.trim() && !sqlQueryText.value.trim()) {
    impactAnalysisError.value = 'SQL 쿼리 또는 파일 경로가 필요합니다.'
    return
  }
  
  isAnalyzingImpact.value = true
  impactAnalysisError.value = ''
  impactAnalysisResult.value = null
  
  try {
    const requestBody = {
      query_file: sqlQueryFile.value.trim() || null,
      query_text: sqlQueryText.value.trim() || null,
      target_table: impactTargetTable.value.trim(),
      target_column: impactTargetColumn.value.trim() || null
    }
    
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000)
    
    const response = await fetch('/api/sql/impact-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(requestBody),
      signal: controller.signal
    }).finally(() => {
      clearTimeout(timeoutId)
    })
    
    if (!response.ok) {
      let errorData
      try {
        const responseText = await response.text()
        try {
          errorData = JSON.parse(responseText)
        } catch (parseError) {
          errorData = { error: responseText || `서버 오류 (${response.status} ${response.statusText})` }
        }
      } catch (e) {
        errorData = { error: `서버 오류 (${response.status} ${response.statusText})` }
      }
      
      let errorMessage = errorData.error || `서버 오류 (${response.status})`
      if (errorData.stdout) {
        errorMessage += `\n\n출력:\n${errorData.stdout}`
      }
      if (errorData.stderr) {
        errorMessage += `\n\n에러:\n${errorData.stderr}`
      }
      
      throw new Error(errorMessage)
    }
    
    const data = await response.json()
    
    if (data.success) {
      if (!data.impact_analysis) {
        throw new Error('영향도 분석 결과가 없습니다.')
      }
      impactAnalysisResult.value = data.impact_analysis
    } else {
      throw new Error(data.error || '영향도 분석 실패')
    }
  } catch (error) {
    console.error('[프론트엔드] 영향도 분석 오류:', error)
    impactAnalysisError.value = `영향도 분석 중 오류가 발생했습니다: ${error.message}`
  } finally {
    isAnalyzingImpact.value = false
  }
}

const clearImpactAnalysis = () => {
  impactAnalysisResult.value = null
  impactAnalysisError.value = ''
  impactTargetTable.value = ''
  impactTargetColumn.value = ''
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
/* SQL 쿼리 분석 전용 스타일 */
.sql-query-analysis-container {
  padding: 2rem;
  background: linear-gradient(135deg, #fff8f0 0%, #ffffff 100%);
  color: #213547;
  border: 3px solid #ff8c42;
  border-radius: 20px;
  box-shadow: 
    0 8px 32px rgba(255, 140, 66, 0.25),
    0 0 0 1px rgba(255, 140, 66, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.8);
  margin-top: 2rem;
  position: relative;
  overflow: hidden;
}

.sql-query-analysis-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #ff6b35, #ff8c42, #ffa726, #ff8c42, #ff6b35);
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
}

.sql-analysis-notice {
  background: linear-gradient(135deg, #fff3e0 0%, #ffe0cc 100%);
  border-left: 5px solid #ff8c42;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 
    0 2px 8px rgba(255, 140, 66, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.6);
}

.sql-analysis-notice p {
  margin: 0;
  color: #e65100;
  font-size: 14px;
  line-height: 1.6;
  font-weight: 500;
}

.sql-query-textarea {
  width: 100%;
  min-height: 500px;
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
  box-shadow: 
    0 2px 8px rgba(255, 140, 66, 0.1),
    inset 0 1px 2px rgba(255, 140, 66, 0.05);
}

.sql-query-textarea:focus {
  outline: none;
  border-color: #ff8c42;
  box-shadow: 
    0 4px 20px rgba(255, 140, 66, 0.2),
    0 0 0 3px rgba(255, 140, 66, 0.15);
  background: #fffefb;
}

.sql-analysis-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}

.btn-analyze-sql {
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
  position: relative;
  overflow: visible;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
}

.btn-analyze-sql:hover:not(:disabled) {
  transform: translateY(-4px) scale(1.03);
  box-shadow: 
    0 12px 36px rgba(255, 107, 53, 0.6),
    0 4px 12px rgba(255, 140, 66, 0.4);
}

.btn-analyze-sql:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.btn-clear-sql {
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

.btn-clear-sql:hover {
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

.sql-analysis-results {
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

.lineage-section-featured {
  border: 3px solid #4a90e2 !important;
  background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%) !important;
}

.graph-section-featured {
  border: 3px solid #4a90e2 !important;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%) !important;
}

.lineage-info-block {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  border: 1px solid rgba(74, 144, 226, 0.2);
}

.lineage-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.lineage-tag {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  color: #ffffff;
}

.table-tag {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
}

.cte-tag {
  background: linear-gradient(135deg, #f5576c 0%, #d32f2f 100%);
}

.join-relationships-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.join-item {
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #4a90e2;
}

.join-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-wrap: wrap;
}

.join-type {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #ffffff;
  text-transform: uppercase;
}

.join-type-left {
  background: #4a90e2;
}

.join-type-inner {
  background: #f5576c;
}

.join-type-outer {
  background: #ff9800;
}

.join-type-right {
  background: #9c27b0;
}

.join-type-default {
  background: #757575;
}

.sql-table-graph {
  width: 100%;
  height: 650px;
  border: 3px solid rgba(74, 144, 226, 0.3);
  border-radius: 12px;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
}

.graph-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 13px;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 4px;
}

.legend-line {
  width: 30px;
  height: 0;
}

.analysis-summary {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  border-radius: 12px;
  border: 2px solid #e0e7ff;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1rem;
  background: #ffffff;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.summary-label {
  font-size: 14px;
  color: #666;
  font-weight: 600;
}

.summary-value {
  font-size: 32px;
  font-weight: 800;
  color: #333;
}

.summary-level {
  font-size: 12px;
  color: #999;
}

.score-excellent {
  color: #10b981;
}

.score-good {
  color: #3b82f6;
}

.score-medium {
  color: #f59e0b;
}

.score-low {
  color: #ef4444;
}

.structure-info p {
  margin: 0.5rem 0;
  color: #333;
}

.lineage-connectivity-summary {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f8f9ff 0%, #ffffff 100%);
  border-radius: 12px;
  border: 2px solid #e0e7ff;
}

.connectivity-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
  flex-wrap: wrap;
}

.connectivity-label {
  font-size: 16px;
  font-weight: 600;
  color: #333;
}

.connectivity-value {
  font-size: 28px;
  font-weight: 800;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: #f0f0f0;
  color: #333;
}

.connectivity-value.connectivity-high {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.connectivity-value.connectivity-medium {
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  color: white;
}

.connectivity-value.connectivity-low-medium {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.connectivity-value.connectivity-low {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.connectivity-bar {
  width: 100%;
  height: 12px;
  background: #e5e7eb;
  border-radius: 6px;
  overflow: hidden;
}

.connectivity-fill {
  height: 100%;
  transition: width 0.8s ease-out;
  border-radius: 6px;
}

.connectivity-fill.connectivity-high {
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
}

.connectivity-fill.connectivity-medium {
  background: linear-gradient(90deg, #3b82f6 0%, #2563eb 100%);
}

.connectivity-fill.connectivity-low-medium {
  background: linear-gradient(90deg, #f59e0b 0%, #d97706 100%);
}

.connectivity-fill.connectivity-low {
  background: linear-gradient(90deg, #ef4444 0%, #dc2626 100%);
}

.impact-analysis-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  border: 1px solid #e0e0e0;
}

.impact-analysis-inputs {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.impact-analysis-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
}

.btn-analyze-impact {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-analyze-impact:hover:not(:disabled) {
  transform: translateY(-2px);
}

.btn-analyze-impact:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-clear-impact {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 700;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.impact-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.impact-summary-value.impact-critical {
  color: #d32f2f;
}

.impact-summary-value.impact-high {
  color: #f57c00;
}

.impact-summary-value.impact-medium {
  color: #fbc02d;
}

.impact-summary-value.impact-low {
  color: #388e3c;
}

.impact-item {
  padding: 1rem;
  background: #ffffff;
  border-radius: 6px;
  border-left: 4px solid #ddd;
}

.impact-item.impact-critical {
  border-left-color: #d32f2f;
}

.impact-item.impact-high {
  border-left-color: #f57c00;
}

.impact-item.impact-medium {
  border-left-color: #fbc02d;
}

.impact-item.impact-low {
  border-left-color: #388e3c;
}

.lineage-visualization-container {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #ffffff;
  border-radius: 12px;
  border: 2px solid #e0e0e0;
}

.lineage-visualization-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.lineage-html-content {
  width: 100%;
  height: 800px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
}

.btn-lineage-quick-access {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  cursor: pointer;
}

.btn-open-lineage {
  background: linear-gradient(135deg, #4a90e2 0%, #357abd 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 0.6rem 1.2rem;
  font-weight: 600;
  cursor: pointer;
}

.analysis-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-top: 2rem;
}

.btn-download {
  padding: 0.75rem 1.5rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
}

.lineage-generation-progress {
  margin-top: 1rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.progress-bar-container {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-top: 0.5rem;
}

.progress-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
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
</style>


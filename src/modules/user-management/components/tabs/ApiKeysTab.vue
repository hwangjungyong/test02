<template>
  <div class="tab-content">
    <div v-if="loading" class="loading">
      <p>API 키 목록을 불러오는 중...</p>
    </div>
    <div v-else>
      <div class="api-keys-header">
        <h3>🔑 API 키 관리</h3>
        <button @click="openCreateModal" class="btn btn-primary">
          ➕ 새 API 키 생성
        </button>
      </div>

      <div v-if="apiKeys.length === 0" class="no-api-keys">
        <p>생성된 API 키가 없습니다.</p>
        <p>외부에서 API를 호출하려면 API 키가 필요합니다.</p>
      </div>

      <div v-else class="api-keys-list">
        <div v-for="key in apiKeys" :key="key.id" class="api-key-item">
          <div class="api-key-info">
            <div class="api-key-name">{{ key.name || '이름 없음' }}</div>
            <div class="api-key-value">{{ key.apiKey }}</div>
            <div v-if="key.description" class="api-key-description">{{ key.description }}</div>
            <div class="api-key-meta">
              <span>생성일: {{ formatDate(key.createdAt) }}</span>
              <span v-if="key.lastUsedAt">마지막 사용: {{ formatDate(key.lastUsedAt) }}</span>
              <span v-if="key.expiresAt">만료일: {{ formatDate(key.expiresAt) }}</span>
            </div>
          </div>
          <div class="api-key-actions">
            <button 
              @click="toggleKey(key.id, !key.isActive)" 
              class="btn btn-sm"
              :class="key.isActive ? 'btn-warning' : 'btn-success'"
            >
              {{ key.isActive ? '비활성화' : '활성화' }}
            </button>
            <button 
              @click="removeApiKey(key.id)" 
              class="btn btn-sm btn-danger"
            >
              삭제
            </button>
          </div>
        </div>
      </div>

      <div class="api-key-usage-info">
        <h4>📖 API 키 사용 방법</h4>
        <p class="usage-intro">
          아래 예제에서 <code>YOUR_API_KEY</code>를 실제 API 키로 교체하세요.
          <span v-if="activeApiKey" class="active-key-hint">
            현재 활성화된 키: <code>{{ activeApiKey.substring(0, 15) }}...</code>
          </span>
        </p>
        
        <div class="usage-examples">
          <div class="usage-example">
            <strong>방법 1: X-API-Key 헤더 (권장)</strong>
            <div class="code-block">
              <pre><code>curl -H "X-API-Key: YOUR_API_KEY" \
  "http://localhost:3001/api/news?q=AI"</code></pre>
              <button @click="copyCode('curl -H &quot;X-API-Key: YOUR_API_KEY&quot; &quot;http://localhost:3001/api/news?q=AI&quot;')" class="btn-copy-code">📋 복사</button>
            </div>
          </div>
          
          <div class="usage-example">
            <strong>방법 2: Authorization 헤더</strong>
            <div class="code-block">
              <pre><code>curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "http://localhost:3001/api/music/recommend?songTitle=Dynamite&artist=BTS"</code></pre>
              <button @click="copyCode('curl -H &quot;Authorization: ApiKey YOUR_API_KEY&quot; &quot;http://localhost:3001/api/music/recommend?songTitle=Dynamite&artist=BTS&quot;')" class="btn-copy-code">📋 복사</button>
            </div>
          </div>
          
          <div class="usage-example">
            <strong>방법 3: 쿼리 파라미터</strong>
            <div class="code-block">
              <pre><code>curl "http://localhost:3001/api/books/recommend?query=머신러닝&api_key=YOUR_API_KEY"</code></pre>
              <button @click="copyCode('curl &quot;http://localhost:3001/api/books/recommend?query=머신러닝&api_key=YOUR_API_KEY&quot;')" class="btn-copy-code">📋 복사</button>
            </div>
          </div>
        </div>

        <div class="api-endpoints-list">
          <h5>📚 사용 가능한 API 엔드포인트</h5>
          <div class="endpoints-grid">
            <div class="endpoint-item">
              <strong>뉴스 검색</strong>
              <code>GET /api/news?q=키워드</code>
              <code>GET /api/news/economy?q=키워드</code>
            </div>
            <div class="endpoint-item">
              <strong>음악 추천</strong>
              <code>GET /api/music/recommend?songTitle=제목&artist=아티스트</code>
              <code>GET /api/music/radio/current?station=kbs&limit=5</code>
              <code>GET /api/music/radio/recent?station=kbs&limit=10</code>
            </div>
            <div class="endpoint-item">
              <strong>도서 검색</strong>
              <code>GET /api/books/search?q=키워드&maxResults=10</code>
              <code>GET /api/books/recommend?query=키워드&category=computers</code>
            </div>
          </div>
        </div>

        <div class="usage-tips">
          <h5>💡 사용 팁</h5>
          <ul>
            <li>모든 API는 인증이 선택사항입니다 (인증 없이도 호출 가능)</li>
            <li>API 키를 사용하면 모든 호출이 자동으로 기록됩니다</li>
            <li>데이터 저장 API (<code>/api/user/*</code>)는 인증이 필수입니다</li>
            <li>Swagger UI에서 테스트: <a href="http://localhost:3001/api-docs" target="_blank">http://localhost:3001/api-docs</a></li>
          </ul>
        </div>
      </div>
    </div>

    <!-- API 키 생성 모달 -->
    <CreateApiKeyModal 
      v-model="showCreateModal"
      :error="error"
      :creating="creating"
      :created-api-key="createdApiKey"
      :form="newApiKeyForm"
      @create="createKey"
      @close="closeCreateModal"
      @copy="copyApiKey"
    />
  </div>
</template>

<script setup>
import { useApiKeys } from '../../composables/useApiKeys.js'
import { formatDate } from '../../../../utils/helpers.js'
import CreateApiKeyModal from '../CreateApiKeyModal.vue'

const {
  apiKeys,
  loading,
  error,
  creating,
  createdApiKey,
  showCreateModal,
  newApiKeyForm,
  activeApiKey,
  loadApiKeys,
  createKey,
  removeApiKey,
  toggleKey,
  openCreateModal,
  closeCreateModal,
  copyApiKey,
  copyCode
} = useApiKeys()

// 컴포넌트 마운트 시 API 키 목록 로드
import { onMounted } from 'vue'
onMounted(() => {
  loadApiKeys()
})
</script>


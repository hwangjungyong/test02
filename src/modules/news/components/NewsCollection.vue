<template>
  <div v-if="modelValue" class="news-collection-container">
    <h2>📰 수집된 뉴스 현황</h2>
    
    <!-- 통계 정보 -->
    <div class="stats-section">
      <div class="stat-item">
        <span class="stat-label">총 뉴스 수:</span>
        <span class="stat-value">{{ newsHistory.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">경제 뉴스:</span>
        <span class="stat-value">{{ economyNewsCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">AI 뉴스:</span>
        <span class="stat-value">{{ aiNewsCount }}</span>
      </div>
      <div class="stat-item">
        <button @click="loadNewsHistoryFromStorage" class="btn-refresh">
          🔄 데이터 새로고침
        </button>
      </div>
    </div>

    <!-- 검색 및 필터 -->
    <div class="search-filter-section">
      <div class="search-box">
        <input
          v-model="newsSearchQuery"
          type="text"
          placeholder="뉴스 제목 또는 출처 검색..."
          class="search-input"
          @input="applyNewsFilters"
        />
      </div>
      
      <div class="filter-box">
        <label>카테고리 필터:</label>
        <select v-model="selectedNewsCategory" @change="applyNewsFilters" class="filter-select">
          <option value="">전체</option>
          <option value="경제 뉴스">경제 뉴스</option>
          <option value="AI 뉴스">AI 뉴스</option>
        </select>
        
        <label>정렬:</label>
        <select v-model="newsSortBy" @change="applyNewsFilters" class="filter-select">
          <option value="date">날짜 순 (최신)</option>
          <option value="title">제목 순</option>
          <option value="source">출처 순</option>
        </select>
      </div>
    </div>

    <!-- 뉴스 목록 -->
    <div v-if="filteredNews.length > 0" class="news-list-container">
      <div class="news-list">
        <div v-for="(article, index) in paginatedNews" :key="article.id || index" class="news-item">
          <div class="news-header">
            <h3 class="news-title">
              <a :href="article.url" target="_blank" rel="noopener noreferrer" class="news-link">
                {{ article.title }}
              </a>
            </h3>
            <span class="news-category" :class="`category-${article.category === '경제 뉴스' ? 'economy' : 'ai'}`">
              {{ article.category }}
            </span>
          </div>
          <p class="news-summary">{{ article.summary }}</p>
          <div class="news-meta">
            <span class="news-date">📅 {{ article.date }}</span>
            <span class="news-source">📰 {{ article.source }}</span>
            <span v-if="article.keyword" class="news-keyword">🔍 {{ article.keyword }}</span>
            <span v-if="article.importanceStars" class="news-importance">{{ article.importanceStars }}</span>
          </div>
        </div>
      </div>

      <!-- 페이지네이션 -->
      <div class="pagination">
        <button 
          @click="currentNewsPage = Math.max(1, currentNewsPage - 1)" 
          :disabled="currentNewsPage === 1"
          class="page-btn"
        >
          이전
        </button>
        <span class="page-info">
          페이지 {{ currentNewsPage }} / {{ totalNewsPages }} (총 {{ filteredNews.length }}건)
        </span>
        <button 
          @click="currentNewsPage = Math.min(totalNewsPages, currentNewsPage + 1)" 
          :disabled="currentNewsPage === totalNewsPages"
          class="page-btn"
        >
          다음
        </button>
      </div>
    </div>
    <div v-else class="no-results">
      <p>수집된 뉴스가 없습니다. "한 달간 데이터 수집" 버튼을 클릭하여 뉴스를 수집해보세요.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  newsHistory: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue', 'refresh'])

const newsSearchQuery = ref('')
const selectedNewsCategory = ref('')
const newsSortBy = ref('date')
const filteredNews = ref([])
const paginatedNews = ref([])
const currentNewsPage = ref(1)
const newsPerPage = 10

const economyNewsCount = computed(() => {
  return props.newsHistory.filter(article => article.category === '경제 뉴스').length
})

const aiNewsCount = computed(() => {
  return props.newsHistory.filter(article => article.category === 'AI 뉴스').length
})

const totalNewsPages = computed(() => {
  return Math.ceil(filteredNews.value.length / newsPerPage)
})

const applyNewsFilters = () => {
  let filtered = [...props.newsHistory]
  
  if (newsSearchQuery.value) {
    const query = newsSearchQuery.value.toLowerCase()
    filtered = filtered.filter(article => 
      article.title?.toLowerCase().includes(query) ||
      article.source?.toLowerCase().includes(query)
    )
  }
  
  if (selectedNewsCategory.value) {
    filtered = filtered.filter(article => article.category === selectedNewsCategory.value)
  }
  
  if (newsSortBy.value === 'date') {
    filtered.sort((a, b) => {
      const dateA = new Date(a.date || a.collectedAt || 0)
      const dateB = new Date(b.date || b.collectedAt || 0)
      return dateB - dateA
    })
  } else if (newsSortBy.value === 'title') {
    filtered.sort((a, b) => (a.title || '').localeCompare(b.title || ''))
  } else if (newsSortBy.value === 'source') {
    filtered.sort((a, b) => (a.source || '').localeCompare(b.source || ''))
  }
  
  filteredNews.value = filtered
  updateNewsPagination()
}

const updateNewsPagination = () => {
  if (!filteredNews.value || filteredNews.value.length === 0) {
    paginatedNews.value = []
    return
  }
  
  const start = (currentNewsPage.value - 1) * newsPerPage
  const end = start + newsPerPage
  paginatedNews.value = filteredNews.value.slice(start, end)
}

const loadNewsHistoryFromStorage = () => {
  emit('refresh')
}

watch(() => props.newsHistory, () => {
  applyNewsFilters()
}, { deep: true })

watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    applyNewsFilters()
  }
})

onMounted(() => {
  if (props.modelValue) {
    applyNewsFilters()
  }
})
</script>

<style scoped>
.news-collection-container {
  margin-top: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  animation: slideDown 0.3s ease;
}

.news-collection-container h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  text-align: center;
}

.stats-section {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.stat-label {
  font-weight: 600;
  color: #666;
}

.stat-value {
  font-weight: 700;
  color: #667eea;
  font-size: 1.2rem;
}

.btn-refresh {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover {
  background: #5568d3;
}

.search-filter-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.search-box {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  box-sizing: border-box;
}

.filter-box {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-select {
  padding: 8px 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
}

.news-list-container {
  margin-top: 1.5rem;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.news-item {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: start;
  margin-bottom: 0.5rem;
}

.news-title {
  margin: 0;
  flex: 1;
}

.news-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  font-size: 1.1rem;
}

.news-link:hover {
  text-decoration: underline;
}

.news-category {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
}

.category-economy {
  background: #fff3e0;
  color: #e65100;
}

.category-ai {
  background: #e3f2fd;
  color: #1976d2;
}

.news-summary {
  color: #666;
  margin-bottom: 0.5rem;
  line-height: 1.6;
}

.news-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 14px;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 2rem;
}

.page-btn {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
}

.page-btn:hover:not(:disabled) {
  background: #5568d3;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  color: #666;
  font-size: 14px;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #666;
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
</style>


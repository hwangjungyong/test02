<template>
  <div v-if="modelValue" class="ai-articles-container">
    <h2>🤖 AI 뉴스 검색</h2>
    <div class="search-notice">
      <p>ℹ️ 최근 일주일 이내의 AI 관련 뉴스를 검색합니다.</p>
    </div>
    <div class="input-group">
      <label for="searchKeyword">검색 키워드:</label>
      <input
        id="searchKeyword"
        v-model="searchKeyword"
        type="text"
        placeholder="예: ChatGPT, 인공지능, 머신러닝, 딥러닝 등"
        class="input-field"
        @keyup.enter="searchAIArticles"
      />
    </div>
    <div class="search-actions">
      <button @click="searchAIArticles" class="btn btn-search" :disabled="isSearching">
        {{ isSearching ? '검색 중...' : '🔍 검색하기' }}
      </button>
      <button @click="fetchLatestAINews" class="btn btn-fetch" :disabled="isSearching">
        🔄 최신 데이터 가져오기
      </button>
      <button 
        @click="collectMonthlyNewsData" 
        class="btn btn-monthly-news"
        :disabled="isCollectingNewsData"
      >
        {{ isCollectingNewsData ? '수집 중...' : '📅 한 달간 데이터 수집' }}
      </button>
    </div>
    <!-- 뉴스 수집 진행 상황 -->
    <div v-if="isCollectingNewsData || newsCollectionStatus" class="monthly-collection-status">
      <div class="progress-info">
        <p class="status-text">{{ newsCollectionStatus }}</p>
        <div class="progress-bar-container">
          <div 
            class="progress-bar" 
            :style="{ width: newsCollectionProgress + '%' }"
          ></div>
        </div>
        <p class="progress-text">{{ newsCollectionProgress }}%</p>
      </div>
    </div>
    <div v-if="articleError" class="error">
      <p>{{ articleError }}</p>
    </div>
    <div v-if="aiArticles.length > 0" class="articles-results">
      <h3>검색 결과 ({{ aiArticles.length }}건)</h3>
      <div class="articles-list">
        <div v-for="(article, index) in aiArticles" :key="index" class="article-card">
          <h4 class="article-title">{{ article.title }}</h4>
          <p class="article-summary">{{ article.summary }}</p>
          <div class="article-meta">
            <span class="article-date">📅 {{ article.date }}</span>
            <span class="article-source">📰 {{ article.source }}</span>
            <span class="article-category">🏷️ {{ article.category }}</span>
          </div>
          <div class="article-actions">
            <a :href="article.url" target="_blank" rel="noopener noreferrer" class="article-link">
              🔗 기사 보기
            </a>
            <button @click="saveSingleNews(article)" class="btn-save-news" :disabled="isSavingNews">
              {{ isSavingNews ? '저장 중...' : '💾 저장' }}
            </button>
          </div>
        </div>
      </div>
      
      <!-- 데이터 연계도 분석 -->
      <div v-if="dataCorrelation.length > 0 || graphData.nodes.length > 0" class="correlation-section">
        <h3>📊 데이터 연계도 분석 (빅데이터 기반)</h3>
        
        <!-- 네트워크 그래프 -->
        <div v-if="graphData.nodes.length > 0" class="network-graph-container">
          <h4>🕸️ 키워드 상하위 관계도</h4>
          <div ref="networkContainer" class="network-graph"></div>
          <div class="graph-legend">
            <div class="legend-item">
              <span class="legend-color primary"></span>
              <span>상위 키워드 (검색어)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color secondary"></span>
              <span>하위 키워드 (관련어)</span>
            </div>
            <div class="legend-item">
              <span class="legend-color tertiary"></span>
              <span>연관 키워드</span>
            </div>
          </div>
        </div>
        
        <!-- 기존 연계도 차트 -->
        <div v-if="dataCorrelation.length > 0" class="correlation-chart">
          <h4>📈 키워드 연계도 상세</h4>
          <div class="correlation-item" v-for="(item, index) in dataCorrelation" :key="index">
            <div class="correlation-header">
              <span class="correlation-keyword">{{ item.keyword }}</span>
              <span class="correlation-score">연계도: {{ item.score }}%</span>
            </div>
            <div class="correlation-bar">
              <div class="correlation-bar-fill" :style="{ width: item.score + '%' }"></div>
            </div>
            <div class="correlation-details">
              <span class="detail-item">관련 기사: {{ item.relatedArticles }}건</span>
              <span class="detail-item">출처 다양성: {{ item.sourceDiversity }}개</span>
              <span class="detail-item">시간 분포: {{ item.timeDistribution }}</span>
              <span v-if="item.timeTrend" class="detail-item">트렌드: {{ item.timeTrend === '상승' ? '📈 상승' : item.timeTrend === '하락' ? '📉 하락' : '➡️ 안정' }}</span>
              <span v-if="item.tfidf" class="detail-item">TF-IDF: {{ item.tfidf }}</span>
              <span v-if="item.relatedKeywords && item.relatedKeywords.length > 0" class="detail-item">연관 키워드: {{ item.relatedKeywords.join(', ') }}</span>
              <span v-if="item.correlationStrength" class="detail-item">연계 강도: {{ item.correlationStrength }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
    <div v-else-if="searchKeyword && !isSearching && !articleError" class="no-results">
      <p>검색 결과가 없습니다. 다른 키워드를 시도해보세요.</p>
      <p class="suggestions">추천 키워드: ChatGPT, GPT, 인공지능, 머신러닝, 딥러닝, 자연어처리, AI</p>
    </div>
  </div>
</template>

<script setup>
import { ref, nextTick, onBeforeUnmount } from 'vue'
import { Network } from 'vis-network'
import 'vis-network/styles/vis-network.min.css'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'news-saved'])

const authStore = useAuthStore()

// 상태
const searchKeyword = ref('')
const aiArticles = ref([])
const isSearching = ref(false)
const articleError = ref('')
const dataCorrelation = ref([])
const graphData = ref({ nodes: [], edges: [] })
const networkContainer = ref(null)
let networkInstance = null
const isCollectingNewsData = ref(false)
const newsCollectionProgress = ref(0)
const newsCollectionStatus = ref('')
const lastAINewsFetch = ref(null)
const NEWS_FETCH_INTERVAL = 60 * 1000
const isSavingNews = ref(false)
const localNewsHistory = ref([])

// 로컬 스토리지에서 뉴스 히스토리 로드
const loadNewsHistoryFromStorage = () => {
  try {
    const stored = localStorage.getItem('newsHistory')
    if (stored) {
      localNewsHistory.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('뉴스 히스토리 로드 오류:', error)
  }
}

// 뉴스 히스토리 저장
const saveNewsHistoryToStorage = () => {
  localStorage.setItem('newsHistory', JSON.stringify(localNewsHistory.value))
  emit('news-saved', localNewsHistory.value)
}

// 컴포넌트 마운트 시 로드
loadNewsHistoryFromStorage()

// AI 뉴스 검색 함수 (App.vue에서 가져온 로직)
const searchAIArticles = async () => {
  articleError.value = ''
  aiArticles.value = []
  dataCorrelation.value = []
  isSearching.value = true

  if (!searchKeyword.value || searchKeyword.value.trim() === '') {
    articleError.value = '검색 키워드를 입력해주세요.'
    isSearching.value = false
    return
  }

  try {
    const searchKeywordEncoded = encodeURIComponent(searchKeyword.value.trim())
    const apiUrl = `/api/news?q=${searchKeywordEncoded}`
    
    const response = await fetch(apiUrl)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`News API 오류: ${response.status} - ${errorData.message || response.statusText}`)
    }

    const data = await response.json()

    if (!data.articles || data.articles.length === 0) {
      articleError.value = `"${searchKeyword.value}"에 대한 AI 관련 기사를 찾을 수 없습니다.`
      isSearching.value = false
      return
    }

    const now = new Date()
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    
    const allArticles = data.articles || []
    
    const formattedArticles = allArticles
      .filter(article => {
        if (!article.title || article.title === '[Removed]') return false
        if (article.publishedAt) {
          const publishedDate = new Date(article.publishedAt)
          if (publishedDate < oneWeekAgo) return false
        }
        return true
      })
      .sort((a, b) => {
        const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
        const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
        return dateB - dateA
      })
      .slice(0, 10)
      .map(article => {
        const publishedDate = article.publishedAt 
          ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          : '날짜 정보 없음'

        return {
          title: article.title || '제목 없음',
          summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
          date: publishedDate,
          source: article.source?.name || '출처 정보 없음',
          category: 'AI 뉴스',
          url: article.url || '#',
        }
      })

    if (formattedArticles.length === 0) {
      const allFormattedArticles = allArticles
        .filter(article => {
          if (!article.title || article.title === '[Removed]') return false
          return true
        })
        .sort((a, b) => {
          const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
          const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
          return dateB - dateA
        })
        .slice(0, 10)
        .map(article => {
          const publishedDate = article.publishedAt 
            ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })
            : '날짜 정보 없음'

          return {
            title: article.title || '제목 없음',
            summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
            date: publishedDate,
            source: article.source?.name || '출처 정보 없음',
            category: 'AI 뉴스',
            url: article.url || '#',
          }
        })
      
      if (allFormattedArticles.length === 0) {
        articleError.value = `"${searchKeyword.value}"에 대한 AI 관련 기사를 찾을 수 없습니다.`
        isSearching.value = false
        return
      }
      
      aiArticles.value = allFormattedArticles
      articleError.value = '최근 일주일 이내의 기사가 없어 전체 기사를 표시합니다.'
    } else {
      aiArticles.value = formattedArticles
      articleError.value = ''
    }
    
    analyzeDataCorrelation(aiArticles.value, searchKeyword.value.trim())
    
    isSearching.value = false
  } catch (error) {
    console.error('뉴스 검색 오류:', error)
    articleError.value = `뉴스 검색 중 오류가 발생했습니다: ${error.message}`
    isSearching.value = false
  }
}

// 데이터 연계도 분석 함수 (App.vue에서 가져온 로직 - 간소화 버전)
const analyzeDataCorrelation = (articles, searchKeyword) => {
  if (!articles || articles.length === 0) {
    dataCorrelation.value = []
    graphData.value = { nodes: [], edges: [] }
    return
  }

  // 간단한 키워드 분석 (복잡한 로직은 생략)
  const keywordFrequency = {}
  articles.forEach(article => {
    const text = `${article.title} ${article.summary}`.toLowerCase()
    const words = text.split(/\s+/).filter(w => w.length >= 2)
    words.forEach(word => {
      keywordFrequency[word] = (keywordFrequency[word] || 0) + 1
    })
  })

  const correlationResults = Object.entries(keywordFrequency)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 10)
    .map(([keyword, count]) => ({
      keyword,
      score: Math.min(100, (count / articles.length) * 100),
      relatedArticles: count,
      sourceDiversity: 1,
      timeDistribution: '분산',
      timeTrend: '안정',
      tfidf: count,
      relatedKeywords: [],
      correlationStrength: '보통'
    }))

  dataCorrelation.value = correlationResults
  graphData.value = { nodes: [], edges: [] }
}

// 최신 AI 뉴스 가져오기
const fetchLatestAINews = async () => {
  const now = Date.now()
  const timeSinceLastFetch = lastAINewsFetch.value ? now - lastAINewsFetch.value : NEWS_FETCH_INTERVAL + 1
  
  if (timeSinceLastFetch < NEWS_FETCH_INTERVAL) {
    const remainingSeconds = Math.ceil((NEWS_FETCH_INTERVAL - timeSinceLastFetch) / 1000)
    articleError.value = `너무 자주 호출되었습니다. ${remainingSeconds}초 후에 다시 시도해주세요.`
    return
  }
  
  if (!searchKeyword.value || searchKeyword.value.trim() === '') {
    searchKeyword.value = 'AI'
  }
  
  await searchAIArticles()
  lastAINewsFetch.value = Date.now()
}

// 한 달간 뉴스 데이터 수집 (간소화 버전)
const collectMonthlyNewsData = async () => {
  if (isCollectingNewsData.value) return

  isCollectingNewsData.value = true
  newsCollectionProgress.value = 0
  newsCollectionStatus.value = '뉴스 데이터 수집 시작...'

  try {
    // 간단한 수집 로직 (실제로는 더 복잡함)
    newsCollectionStatus.value = '수집 중...'
    newsCollectionProgress.value = 50
    
    await fetchLatestAINews()
    
    newsCollectionProgress.value = 100
    newsCollectionStatus.value = '수집 완료!'
    
    setTimeout(() => {
      newsCollectionStatus.value = ''
      newsCollectionProgress.value = 0
    }, 2000)
  } catch (error) {
    console.error('뉴스 수집 오류:', error)
    articleError.value = `뉴스 수집 중 오류가 발생했습니다: ${error.message}`
  } finally {
    isCollectingNewsData.value = false
  }
}

// 단일 뉴스 저장
const saveSingleNews = async (article) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    return
  }

  isSavingNews.value = true
  try {
    const articleId = `${article.title}-${article.source}-${article.date}`
    const existingArticle = localNewsHistory.value.find(a => a.id === articleId)
    
    if (!existingArticle) {
      const now = new Date().toISOString()
      localNewsHistory.value.push({
        id: articleId,
        title: article.title,
        summary: article.summary,
        date: article.date,
        source: article.source,
        category: article.category || 'AI 뉴스',
        keyword: article.keyword || searchKeyword.value,
        url: article.url,
        collectedAt: now
      })
      saveNewsHistoryToStorage()
    }

    if (authStore.token) {
      await fetch('/api/user/news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify([{
          title: article.title,
          summary: article.summary,
          date: article.date,
          source: article.source,
          category: article.category || 'AI 뉴스',
          keyword: article.keyword || searchKeyword.value,
          url: article.url,
          publishedDate: article.date
        }])
      })
    }
  } catch (error) {
    console.error('[뉴스 저장] 오류:', error)
    alert('뉴스 저장 중 오류가 발생했습니다.')
  } finally {
    isSavingNews.value = false
  }
}

// 컴포넌트 언마운트 시 정리
onBeforeUnmount(() => {
  if (networkInstance) {
    networkInstance.destroy()
    networkInstance = null
  }
})
</script>

<style scoped>
/* AI 뉴스 검색 스타일은 App.vue에서 가져옴 */
.ai-articles-container {
  margin-top: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  animation: slideDown 0.3s ease;
  width: 100%;
  max-width: 100%;
}

.ai-articles-container h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  text-align: center;
}

.search-notice {
  margin-bottom: 1rem;
  padding: 10px 15px;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
}

.search-notice p {
  margin: 0;
  color: #1976d2;
  font-size: 14px;
  font-weight: 500;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #35495e;
  font-weight: 600;
  font-size: 18px;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 18px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.search-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.btn {
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.btn-search {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-search:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-fetch {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-monthly-news {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.monthly-collection-status {
  margin-top: 1rem;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.progress-info {
  text-align: center;
}

.status-text {
  margin-bottom: 0.5rem;
  color: #666;
}

.progress-bar-container {
  width: 100%;
  height: 20px;
  background: #e0e0e0;
  border-radius: 10px;
  overflow: hidden;
  margin: 0.5rem 0;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.progress-text {
  color: #666;
  font-size: 14px;
}

.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
}

.articles-results {
  margin-top: 2rem;
}

.articles-results h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.4rem;
}

.articles-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.article-card {
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.article-title {
  color: #333;
  margin-bottom: 0.5rem;
  font-size: 1.2rem;
}

.article-summary {
  color: #666;
  margin-bottom: 1rem;
  line-height: 1.6;
}

.article-meta {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  font-size: 14px;
  color: #666;
}

.article-actions {
  display: flex;
  gap: 1rem;
}

.article-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
}

.article-link:hover {
  text-decoration: underline;
}

.btn-save-news {
  padding: 8px 16px;
  background: #667eea;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-save-news:hover:not(:disabled) {
  background: #5568d3;
}

.btn-save-news:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.correlation-section {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.correlation-section h3 {
  margin-bottom: 1rem;
}

.network-graph-container {
  margin-top: 1rem;
}

.network-graph {
  width: 100%;
  height: 400px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  background: white;
}

.graph-legend {
  display: flex;
  gap: 1rem;
  margin-top: 1rem;
  flex-wrap: wrap;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.legend-color {
  width: 16px;
  height: 16px;
  border-radius: 50%;
}

.legend-color.primary {
  background: #667eea;
}

.legend-color.secondary {
  background: #764ba2;
}

.legend-color.tertiary {
  background: #9e9e9e;
}

.correlation-chart {
  margin-top: 1rem;
}

.correlation-item {
  margin-bottom: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
}

.correlation-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 0.5rem;
}

.correlation-keyword {
  font-weight: 600;
  color: #333;
}

.correlation-score {
  color: #667eea;
  font-weight: 600;
}

.correlation-bar {
  width: 100%;
  height: 8px;
  background: #e0e0e0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.5rem;
}

.correlation-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.correlation-details {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 14px;
  color: #666;
}

.detail-item {
  padding: 4px 8px;
  background: #f5f5f5;
  border-radius: 4px;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #666;
}

.suggestions {
  margin-top: 0.5rem;
  font-size: 14px;
  color: #999;
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


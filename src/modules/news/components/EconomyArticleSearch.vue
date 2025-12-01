<template>
  <div v-if="modelValue" class="economy-articles-container">
    <h2>💰 경제 뉴스 검색</h2>
    <div class="search-notice">
      <p>ℹ️ 최근 2주 이내의 최신 경제 뉴스를 자동으로 불러옵니다.</p>
    </div>
    <div class="search-actions">
      <button 
        @click="fetchLatestEconomyNews" 
        class="btn btn-fetch"
        :disabled="isSearchingEconomy"
      >
        {{ isSearchingEconomy ? '불러오는 중...' : '🔄 최신 데이터 가져오기' }}
      </button>
      <button 
        @click="$emit('collect-monthly')" 
        class="btn btn-monthly-news"
        :disabled="isCollectingNewsData"
      >
        {{ isCollectingNewsData ? '수집 중...' : '📅 한 달간 데이터 수집' }}
      </button>
    </div>
    <div v-if="isCollectingNewsData || newsCollectionStatus" class="monthly-collection-status">
      <div class="progress-info">
        <p class="status-text">{{ newsCollectionStatus }}</p>
        <div class="progress-bar-container">
          <div class="progress-bar" :style="{ width: newsCollectionProgress + '%' }"></div>
        </div>
        <p class="progress-text">{{ newsCollectionProgress }}%</p>
      </div>
    </div>
    <div v-if="isSearchingEconomy" class="loading-state">
      <p>📰 최신 뉴스를 불러오는 중...</p>
    </div>
    <div v-if="economyArticleError" class="error">
      <p>{{ economyArticleError }}</p>
    </div>
    <div v-if="economyArticles.length > 0" class="articles-results">
      <div class="importance-legend">
        <h3>최신 뉴스 ({{ economyArticles.length }}건)</h3>
        <div class="legend">
          <span class="legend-item"><span class="stars">⭐⭐⭐</span> 매우중요</span>
          <span class="legend-item"><span class="stars">⭐⭐</span> 보통</span>
          <span class="legend-item"><span class="stars">⭐</span> 미흡</span>
        </div>
      </div>
      <div class="articles-table-container">
        <table class="articles-table">
          <thead>
            <tr>
              <th class="col-date">날짜</th>
              <th class="col-importance">중요도</th>
              <th class="col-title">뉴스기사</th>
              <th class="col-actions">저장</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(article, index) in economyArticles" :key="index" 
                :class="`importance-${article.importanceValue === 3 ? 'high' : article.importanceValue === 2 ? 'medium' : 'low'}`">
              <td class="col-date">{{ article.date }}</td>
              <td class="col-importance"><span class="stars">{{ article.importanceStars }}</span></td>
              <td class="col-title">
                <a :href="article.url" target="_blank" rel="noopener noreferrer" class="article-title-link">
                  {{ article.title }}
                </a>
              </td>
              <td class="col-actions">
                <button @click="$emit('save-news', article)" class="btn-save-news-small" :disabled="isSavingNews" title="저장">
                  {{ isSavingNews ? '...' : '💾' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else-if="!isSearchingEconomy && !economyArticleError" class="no-results">
      <p>뉴스를 불러오는 중입니다...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  isCollectingNewsData: { type: Boolean, default: false },
  newsCollectionStatus: { type: String, default: '' },
  newsCollectionProgress: { type: Number, default: 0 },
  isSavingNews: { type: Boolean, default: false }
})

const emit = defineEmits(['update:modelValue', 'collect-monthly', 'save-news'])

const authStore = useAuthStore()
const economyArticles = ref([])
const isSearchingEconomy = ref(false)
const economyArticleError = ref('')
const lastEconomyNewsFetch = ref(null)
const NEWS_FETCH_INTERVAL = 60 * 1000

const calculateEconomyImportance = (article) => {
  const title = (article.title || '').toLowerCase()
  const description = (article.description || '').toLowerCase()
  const content = (article.content || '').toLowerCase()
  const source = (article.source?.name || '').toLowerCase()
  const fullText = `${title} ${description} ${content}`
  let score = 0

  const veryImportantKeywords = [
    '금리', '기준금리', '금리인상', '금리인하', '금리정책',
    '환율', '원달러', '원화', '환율변동', '환율정책',
    'gdp', '국내총생산', '경제성장률',
    '인플레이션', '물가', '소비자물가', '생산자물가',
    '부동산가격', '아파트가격', '부동산정책', '주택가격',
    '코스피', '코스닥', '주가지수', '종합주가지수',
    '한국은행', '한은', '금융통화위원회', '금통위',
    '긴급', '속보', '특보', '발표', '결정', '발표'
  ]
  const normalKeywords = [
    '주식', '부동산', '금융', '증시', '경제', '경기',
    '기업', '기업실적', '수출', '수입', '무역',
    '고용', '실업률', '취업', '일자리'
  ]
  const majorSources = [
    '조선일보', '중앙일보', '매일경제', '한국경제', '이데일리',
    'chosun', 'joongang', 'mk', 'hankyung', 'edaily'
  ]

  veryImportantKeywords.forEach(keyword => {
    if (fullText.includes(keyword)) score += 3
  })
  majorSources.forEach(sourceName => {
    if (source.includes(sourceName)) score += 2
  })
  if (title.includes('긴급') || title.includes('속보') || title.includes('특보')) {
    score += 2
  }
  normalKeywords.forEach(keyword => {
    if (fullText.includes(keyword)) score += 1
  })

  if (score >= 5) {
    return { stars: '⭐⭐⭐', label: '매우중요', value: 3 }
  } else if (score >= 2) {
    return { stars: '⭐⭐', label: '보통', value: 2 }
  } else {
    return { stars: '⭐', label: '미흡', value: 1 }
  }
}

const fetchLatestEconomyNews = async () => {
  const now = Date.now()
  const timeSinceLastFetch = lastEconomyNewsFetch.value ? now - lastEconomyNewsFetch.value : NEWS_FETCH_INTERVAL + 1
  
  if (timeSinceLastFetch < NEWS_FETCH_INTERVAL) {
    const remainingSeconds = Math.ceil((NEWS_FETCH_INTERVAL - timeSinceLastFetch) / 1000)
    economyArticleError.value = `너무 자주 호출되었습니다. ${remainingSeconds}초 후에 다시 시도해주세요.`
    return
  }
  
  economyArticleError.value = ''
  economyArticles.value = []
  isSearchingEconomy.value = true

  try {
    const apiUrl = `/api/news/economy?q=경제`
    const response = await fetch(apiUrl)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`News API 오류: ${response.status} - ${errorData.message || response.statusText}`)
    }

    const data = await response.json()

    if (!data.articles || data.articles.length === 0) {
      economyArticleError.value = '최신 경제 뉴스를 찾을 수 없습니다.'
      isSearchingEconomy.value = false
      return
    }

    const nowDate = new Date()
    const twoWeeksAgo = new Date(nowDate.getTime() - 14 * 24 * 60 * 60 * 1000)
    const allArticles = data.articles || []
    
    let formattedArticles = allArticles
      .filter(article => {
        if (!article.title || article.title === '[Removed]') return false
        if (article.publishedAt) {
          const publishedDate = new Date(article.publishedAt)
          if (publishedDate < twoWeeksAgo) return false
        }
        return true
      })
      .sort((a, b) => {
        const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
        const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
        return dateB - dateA
      })
      .map(article => {
        const publishedDate = article.publishedAt 
          ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
              year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
            })
          : '날짜 정보 없음'
        const importance = calculateEconomyImportance(article)
        return {
          title: article.title || '제목 없음',
          summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
          date: publishedDate,
          source: article.source?.name || '출처 정보 없음',
          category: '경제 뉴스',
          url: article.url || '#',
          importanceStars: importance.stars,
          importanceLabel: importance.label,
          importanceValue: importance.value,
          publishedDate: article.publishedAt ? new Date(article.publishedAt).toISOString().split('T')[0] : ''
        }
      })
      .sort((a, b) => b.importanceValue - a.importanceValue)
    
    if (formattedArticles.length === 0 && allArticles.length > 0) {
      formattedArticles = allArticles
        .filter(article => {
          if (!article.title || article.title === '[Removed]') return false
          return true
        })
        .sort((a, b) => {
          const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
          const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
          return dateB - dateA
        })
        .slice(0, 50)
        .map(article => {
          const publishedDate = article.publishedAt 
            ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
                year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
              })
            : '날짜 정보 없음'
          const importance = calculateEconomyImportance(article)
          return {
            title: article.title || '제목 없음',
            summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
            date: publishedDate,
            source: article.source?.name || '출처 정보 없음',
            category: '경제 뉴스',
            url: article.url || '#',
            importanceStars: importance.stars,
            importanceLabel: importance.label,
            importanceValue: importance.value,
            publishedDate: article.publishedAt ? new Date(article.publishedAt).toISOString().split('T')[0] : ''
          }
        })
        .sort((a, b) => b.importanceValue - a.importanceValue)
      
      if (formattedArticles.length > 0) {
        economyArticleError.value = '최근 2주 이내의 기사가 없어 전체 기사를 표시합니다.'
      }
    }

    economyArticles.value = formattedArticles
    isSearchingEconomy.value = false
    lastEconomyNewsFetch.value = Date.now()
  } catch (error) {
    console.error('경제 뉴스 검색 오류:', error)
    economyArticleError.value = `뉴스 검색 중 오류가 발생했습니다: ${error.message}`
    isSearchingEconomy.value = false
  }
}

onMounted(() => {
  if (props.modelValue) {
    fetchLatestEconomyNews()
  }
})
</script>

<style scoped>
.economy-articles-container {
  margin-top: 1.5rem;
  padding: 3rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  animation: slideDown 0.3s ease;
  width: 100%;
  max-width: 100%;
}

.economy-articles-container h2 {
  color: #f5576c;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  text-align: center;
}

.search-notice {
  margin-bottom: 1rem;
  padding: 10px 15px;
  background: #fff3e0;
  border-left: 4px solid #f5576c;
  border-radius: 4px;
}

.search-notice p {
  margin: 0;
  color: #e65100;
  font-size: 14px;
  font-weight: 500;
}

.search-actions {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
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

.btn-fetch {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  color: white;
}

.btn-monthly-news {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
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
  background: linear-gradient(90deg, #f5576c 0%, #f093fb 100%);
  transition: width 0.3s ease;
}

.progress-text {
  color: #666;
  font-size: 14px;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 16px;
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

.importance-legend {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.importance-legend h3 {
  margin-bottom: 0.75rem;
}

.legend {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.articles-table-container {
  overflow-x: auto;
}

.articles-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
}

.articles-table thead {
  background: #f5f5f5;
}

.articles-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  color: #333;
  border-bottom: 2px solid #e0e0e0;
}

.articles-table td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
}

.articles-table tbody tr:hover {
  background: #f8f9fa;
}

.importance-high {
  background: #fff3e0;
}

.importance-medium {
  background: #fffde7;
}

.importance-low {
  background: #f5f5f5;
}

.col-date {
  width: 150px;
}

.col-importance {
  width: 100px;
}

.col-title {
  min-width: 300px;
}

.col-actions {
  width: 80px;
}

.article-title-link {
  color: #f5576c;
  text-decoration: none;
  font-weight: 500;
}

.article-title-link:hover {
  text-decoration: underline;
}

.btn-save-news-small {
  padding: 6px 12px;
  background: #f5576c;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
}

.btn-save-news-small:hover:not(:disabled) {
  background: #d32f2f;
}

.btn-save-news-small:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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


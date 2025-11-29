<template>
  <div v-if="modelValue" class="book-history-container">
    <h2>📚 실시간 도서 수집 현황</h2>
    
    <!-- 수집 버튼 -->
    <div class="collection-buttons">
      <button @click="collectMonthlyBookData" class="btn btn-collect" :disabled="isCollectingBookData">
        {{ isCollectingBookData ? '수집 중...' : '📅 한 달간 데이터 수집' }}
      </button>
      <button @click="fetchLatestBooks" class="btn btn-fetch">
        🔄 최신 데이터 가져오기
      </button>
    </div>

    <!-- 수집 진행 상황 -->
    <div v-if="isCollectingBookData" class="monthly-collection-status">
      <div class="progress-bar-container">
        <div class="progress-bar" :style="{ width: bookCollectionProgress + '%' }"></div>
      </div>
      <p class="status-text">{{ bookCollectionStatus }}</p>
    </div>

    <!-- 검색 및 필터 -->
    <div class="search-filter-section">
      <div class="search-box">
        <input
          v-model="bookSearchQuery"
          type="text"
          placeholder="도서 제목 또는 저자 검색..."
          class="search-input"
          @input="applyBookFilters"
        />
      </div>
      
      <div class="filter-box">
        <label>정렬:</label>
        <select v-model="bookSortBy" @change="applyBookFilters" class="filter-select">
          <option value="date">출판일 순</option>
          <option value="title">제목 순</option>
          <option value="author">저자 순</option>
          <option value="publisher">출판사 순</option>
        </select>
      </div>
    </div>

    <!-- 통계 -->
    <div v-if="booksHistory.length > 0" class="stats-section">
      <div class="stat-item">
        <span class="stat-label">총 도서 수:</span>
        <span class="stat-value">{{ booksHistory.length }}권</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">고유 저자:</span>
        <span class="stat-value">{{ uniqueBookAuthors.length }}명</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">고유 출판사:</span>
        <span class="stat-value">{{ uniqueBookPublishers.length }}개</span>
      </div>
    </div>

    <!-- 도서 목록 -->
    <div v-if="filteredBooks.length > 0" class="books-table-container">
      <table class="books-table">
        <thead>
          <tr>
            <th>순번</th>
            <th>제목</th>
            <th>저자</th>
            <th>출판사</th>
            <th>출판일</th>
            <th>카테고리</th>
            <th>링크</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(book, index) in paginatedBooks" :key="book.id || index">
            <td>{{ (currentBookPage - 1) * booksPerPage + index + 1 }}</td>
            <td class="book-title-cell">{{ book.title }}</td>
            <td>{{ book.authors.join(', ') }}</td>
            <td>{{ book.publisher }}</td>
            <td>{{ book.publishedDate }}</td>
            <td>{{ book.categories.join(', ') || '-' }}</td>
            <td>
              <a v-if="book.infoLink" :href="book.infoLink" target="_blank" class="book-link">상세</a>
            </td>
          </tr>
          <tr v-if="paginatedBooks.length === 0">
            <td colspan="7" class="no-data">검색 결과가 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 페이지네이션 -->
    <div v-if="filteredBooks.length > 0" class="pagination">
      <button
        @click="goToBookPage(currentBookPage - 1)"
        :disabled="currentBookPage === 1"
        class="page-btn"
      >
        이전
      </button>
      <span class="page-info">
        페이지 {{ currentBookPage }} / {{ totalBookPages }}
        (총 {{ filteredBooks.length }}권)
      </span>
      <button
        @click="goToBookPage(currentBookPage + 1)"
        :disabled="currentBookPage === totalBookPages"
        class="page-btn"
      >
        다음
      </button>
    </div>

    <div v-if="filteredBooks.length === 0 && booksHistory.length === 0" class="no-results">
      <p>수집된 도서가 없습니다. "한 달간 데이터 수집" 버튼을 클릭하여 도서를 수집해보세요.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()

// 상태
const booksHistory = ref([])
const bookSearchQuery = ref('')
const bookSortBy = ref('date')
const currentBookPage = ref(1)
const booksPerPage = ref(10)
const isCollectingBookData = ref(false)
const bookCollectionProgress = ref(0)
const bookCollectionStatus = ref('')
const filteredBooks = ref([])
const paginatedBooks = ref([])

// 계산된 속성
const totalBookPages = computed(() => {
  return Math.ceil(filteredBooks.value.length / booksPerPage.value)
})

const uniqueBookAuthors = computed(() => {
  const authors = new Set()
  booksHistory.value.forEach(book => {
    if (book.authors) book.authors.forEach(author => authors.add(author))
  })
  return Array.from(authors).sort()
})

const uniqueBookPublishers = computed(() => {
  const publishers = new Set()
  booksHistory.value.forEach(book => {
    if (book.publisher) publishers.add(book.publisher)
  })
  return Array.from(publishers).sort()
})

// 필터링 및 정렬 적용
const applyBookFilters = () => {
  let filtered = [...booksHistory.value]
  if (bookSearchQuery.value.trim()) {
    const query = bookSearchQuery.value.toLowerCase()
    filtered = filtered.filter(book => {
      const title = (book.title || '').toLowerCase()
      const authors = (book.authors || []).join(' ').toLowerCase()
      return title.includes(query) || authors.includes(query)
    })
  }
  filtered.sort((a, b) => {
    switch (bookSortBy.value) {
      case 'date': return (b.publishedDate || '').localeCompare(a.publishedDate || '')
      case 'title': return (a.title || '').localeCompare(b.title || '')
      case 'author': return (a.authors?.[0] || '').localeCompare(b.authors?.[0] || '')
      case 'publisher': return (a.publisher || '').localeCompare(b.publisher || '')
      default: return 0
    }
  })
  filteredBooks.value = filtered
  currentBookPage.value = 1
  updateBookPagination()
}

// 페이지네이션 업데이트
const updateBookPagination = () => {
  const start = (currentBookPage.value - 1) * booksPerPage.value
  const end = start + booksPerPage.value
  paginatedBooks.value = filteredBooks.value.slice(start, end)
}

// 페이지 이동
const goToBookPage = (page) => {
  if (page >= 1 && page <= totalBookPages.value) {
    currentBookPage.value = page
    updateBookPagination()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// localStorage에서 히스토리 불러오기
const loadBooksHistoryFromStorage = () => {
  const stored = localStorage.getItem('booksHistory')
  if (stored) {
    try {
      booksHistory.value = JSON.parse(stored)
      applyBookFilters()
    } catch (e) {
      console.error('도서 히스토리 로드 오류:', e)
      booksHistory.value = []
    }
  }
}

// localStorage에 히스토리 저장
const saveBooksHistoryToStorage = () => {
  localStorage.setItem('booksHistory', JSON.stringify(booksHistory.value))
  
  // 로그인한 경우 데이터베이스에도 저장
  if (authStore.isAuthenticated && authStore.token) {
    saveBooksToDatabase()
  }
}

// 도서를 데이터베이스에 저장
async function saveBooksToDatabase() {
  try {
    const recentBooks = booksHistory.value.slice(-50).map(book => ({
      title: book.title,
      authors: book.authors || [],
      publisher: book.publisher,
      description: book.description,
      thumbnail: book.thumbnail,
      imageUrl: book.thumbnail,
      previewLink: book.previewLink,
      publishedDate: book.publishedDate,
      categories: book.categories || [],
      isbn: book.id
    }))

    if (recentBooks.length > 0) {
      const response = await fetch('/api/user/books', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify(recentBooks)
      })

      if (response.ok) {
        const data = await response.json()
        console.log('[도서 저장] 데이터베이스에 저장 완료:', data.message)
      }
    }
  } catch (error) {
    console.error('[도서 저장] 데이터베이스 저장 오류:', error)
  }
}

// 최신 도서 가져오기
const fetchLatestBooks = async () => {
  try {
    const keywords = ['AI', '인공지능', '머신러닝', '딥러닝', '파이썬']
    const allBooks = []
    for (const keyword of keywords) {
      const response = await fetch(`/api/books/search?q=${encodeURIComponent(keyword)}&maxResults=10`)
      if (response.ok) {
        const data = await response.json()
        if (data.books) allBooks.push(...data.books)
      }
    }
    const uniqueBooks = []
    const seenIds = new Set()
    for (const book of allBooks) {
      if (book.id && !seenIds.has(book.id)) {
        seenIds.add(book.id)
        uniqueBooks.push(book)
      }
    }
    const existingIds = new Set(booksHistory.value.map(b => b.id))
    const newBooks = uniqueBooks.filter(b => b.id && !existingIds.has(b.id))
    booksHistory.value.push(...newBooks)
    saveBooksHistoryToStorage()
    applyBookFilters()
  } catch (error) {
    console.error('최신 도서 가져오기 오류:', error)
  }
}

// 한 달간 도서 데이터 수집
const collectMonthlyBookData = async () => {
  if (isCollectingBookData.value) return
  isCollectingBookData.value = true
  bookCollectionProgress.value = 0
  bookCollectionStatus.value = '도서 데이터 수집 시작...'
  try {
    const keywords = ['AI', '인공지능', '머신러닝', '딥러닝', '파이썬', '데이터사이언스']
    const allBooks = []
    for (let i = 0; i < keywords.length; i++) {
      const keyword = keywords[i]
      bookCollectionStatus.value = `${keyword} 검색 중... (${i + 1}/${keywords.length})`
      bookCollectionProgress.value = ((i + 1) / keywords.length) * 100
      const response = await fetch(`/api/books/search?q=${encodeURIComponent(keyword)}&maxResults=20`)
      if (response.ok) {
        const data = await response.json()
        if (data.books) allBooks.push(...data.books)
      }
      await new Promise(resolve => setTimeout(resolve, 500))
    }
    const uniqueBooks = []
    const seenIds = new Set()
    for (const book of allBooks) {
      if (book.id && !seenIds.has(book.id)) {
        seenIds.add(book.id)
        uniqueBooks.push(book)
      }
    }
    const existingIds = new Set(booksHistory.value.map(b => b.id))
    const newBooks = uniqueBooks.filter(b => b.id && !existingIds.has(b.id))
    booksHistory.value.push(...newBooks)
    saveBooksHistoryToStorage()
    applyBookFilters()
    bookCollectionStatus.value = `완료! 총 ${newBooks.length}권의 도서가 수집되었습니다.`
    bookCollectionProgress.value = 100
    setTimeout(() => {
      isCollectingBookData.value = false
      bookCollectionStatus.value = ''
      bookCollectionProgress.value = 0
    }, 3000)
  } catch (error) {
    console.error('한 달간 도서 수집 오류:', error)
    bookCollectionStatus.value = `오류 발생: ${error.message}`
    isCollectingBookData.value = false
  }
}

// 페이지 변경 감지
watch(currentBookPage, () => {
  updateBookPagination()
})

// 컴포넌트 마운트 시 로드
onMounted(() => {
  loadBooksHistoryFromStorage()
})
</script>

<style scoped>
.book-history-container {
  margin-top: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease;
}

.book-history-container h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.collection-buttons {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.btn {
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-collect {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-collect:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-collect:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-fetch {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
}

.btn-fetch:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.monthly-collection-status {
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.progress-bar-container {
  width: 100%;
  height: 24px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  transition: width 0.3s ease;
  border-radius: 12px;
}

.status-text {
  margin: 0;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
  color: white;
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
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.filter-box {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-box label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.filter-select {
  padding: 8px 12px;
  font-size: 14px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #667eea;
}

.stats-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #667eea;
}

.books-table-container {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.books-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.books-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.books-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
}

.books-table td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
}

.book-title-cell {
  font-weight: 600;
  color: #333;
}

.book-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 500;
}

.book-link:hover {
  text-decoration: underline;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.no-results {
  text-align: center;
  padding: 2rem;
  color: #666;
  background: #f8f9fa;
  border-radius: 8px;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.page-btn {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid #667eea;
  background: white;
  color: #667eea;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #667eea;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
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


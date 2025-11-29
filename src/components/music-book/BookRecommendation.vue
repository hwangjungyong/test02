<template>
  <div v-if="modelValue" class="book-container">
    <h2>📖 AI 도서 추천</h2>
    <div class="search-notice">
      <p>💡 원하는 도서에 대해 자유롭게 설명해주세요. AI가 당신의 요구사항을 분석하여 최적의 도서를 추천해드립니다.</p>
      <p>예시: "머신러닝을 처음 배우고 싶어요", "재미있는 소설을 읽고 싶어요", "경제에 대해 배우고 싶어요"</p>
    </div>
    <div class="input-group">
      <label for="bookKeyword">원하는 도서에 대해 설명해주세요:</label>
      <textarea
        id="bookKeyword"
        v-model="bookKeyword"
        type="text"
        placeholder="예: 머신러닝을 처음 배우고 싶어요. 파이썬 기초는 알고 있습니다."
        class="input-field"
        rows="3"
        style="resize: vertical; min-height: 80px;"
      ></textarea>
    </div>
    <div class="input-group">
      <label for="bookCategory">카테고리 (선택사항):</label>
      <select id="bookCategory" v-model="bookCategory" class="input-field">
        <option value="">전체</option>
        <option value="computers">컴퓨터/IT</option>
        <option value="science">과학</option>
        <option value="technology">기술</option>
        <option value="fiction">소설</option>
        <option value="business">경제/경영</option>
      </select>
    </div>
    <button @click="recommendBooks" class="btn btn-recommend" :disabled="isSearchingBooks">
      {{ isSearchingBooks ? 'AI 분석 중...' : '🤖 AI 도서 추천 받기' }}
    </button>
    <div v-if="recommendedBooks.length > 0" class="book-list">
      <h3 class="book-list-title">📚 추천 도서 목록 ({{ recommendedBooks.length }}건)</h3>
      <div class="books-grid">
        <div v-for="(book, index) in recommendedBooks" :key="book.id || index" class="book-card">
          <div class="book-card-header">
            <div class="book-thumbnail" v-if="book.thumbnail">
              <img :src="book.thumbnail" :alt="book.title" />
            </div>
            <div class="book-number-badge">{{ index + 1 }}</div>
          </div>
          <div class="book-card-body">
            <h4 class="book-title">{{ book.title }}</h4>
            <div class="book-meta">
              <div class="book-meta-item">
                <span class="book-meta-label">✍️ 저자</span>
                <span class="book-meta-value">{{ book.authors.join(', ') }}</span>
              </div>
              <div class="book-meta-item">
                <span class="book-meta-label">🏢 출판사</span>
                <span class="book-meta-value">{{ book.publisher }}</span>
              </div>
              <div class="book-meta-item">
                <span class="book-meta-label">📅 출판일</span>
                <span class="book-meta-value">{{ book.publishedDate }}</span>
              </div>
              <div v-if="book.averageRating > 0" class="book-meta-item">
                <span class="book-meta-label">⭐ 평점</span>
                <span class="book-meta-value">{{ book.averageRating }}/5.0 ({{ book.ratingsCount }}명)</span>
              </div>
            </div>
            <p v-if="book.description" class="book-description">
              {{ book.description.length > 200 ? book.description.substring(0, 200) + '...' : book.description }}
            </p>
            <div v-if="book.categories && book.categories.length > 0" class="book-categories">
              <span v-for="(cat, idx) in book.categories.slice(0, 3)" :key="idx" class="book-category-tag">
                {{ cat }}
              </span>
            </div>
          </div>
          <div class="book-card-footer">
            <button @click="saveSingleBook(book)" class="book-link-btn book-link-save" :disabled="isSavingBook">
              {{ isSavingBook ? '저장 중...' : '💾 저장' }}
            </button>
            <a v-if="book.infoLink" :href="book.infoLink" target="_blank" class="book-link-btn book-link-primary">
              📖 상세 정보
            </a>
            <a v-if="book.previewLink" :href="book.previewLink" target="_blank" class="book-link-btn book-link-secondary">
              👁️ 미리보기
            </a>
          </div>
        </div>
      </div>
    </div>
    <div v-if="bookError" class="error">
      <p>{{ bookError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue', 'book-saved'])

const authStore = useAuthStore()

// 상태
const bookKeyword = ref('')
const bookCategory = ref('')
const recommendedBooks = ref([])
const isSearchingBooks = ref(false)
const bookError = ref('')
const isSavingBook = ref(false)

// 도서 추천 함수
const recommendBooks = async () => {
  const trimmedKeyword = bookKeyword.value.trim()
  if (!trimmedKeyword) {
    bookError.value = '원하는 도서에 대해 설명을 입력해주세요.'
    return
  }
  isSearchingBooks.value = true
  bookError.value = ''
  recommendedBooks.value = []
  try {
    let url = `/api/books/recommend?query=${encodeURIComponent(trimmedKeyword)}`
    if (bookCategory.value) {
      url += `&category=${encodeURIComponent(bookCategory.value)}`
    }
    const response = await fetch(url)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status} 오류` }))
      throw new Error(errorData.error || `API 오류: ${response.status}`)
    }
    const data = await response.json()
    if (data.books && data.books.length > 0) {
      recommendedBooks.value = data.books
    } else {
      bookError.value = '추천 도서를 찾을 수 없습니다. 다른 설명으로 시도해보세요.'
    }
  } catch (error) {
    console.error('도서 추천 오류:', error)
    bookError.value = `도서 추천 중 오류가 발생했습니다: ${error.message}`
  } finally {
    isSearchingBooks.value = false
  }
}

// 단일 도서 저장 함수
const saveSingleBook = async (book) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    return
  }

  isSavingBook.value = true
  try {
    // 데이터베이스에 저장
    if (authStore.token) {
      const response = await fetch('/api/user/books', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify([{
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
        }])
      })

      if (response.ok) {
        const data = await response.json()
        alert(`도서가 저장되었습니다! (${data.saved}개 저장됨)`)
        emit('book-saved', book)
      } else {
        alert('도서 저장에 실패했습니다.')
      }
    }
  } catch (error) {
    console.error('[도서 저장] 오류:', error)
    alert('도서 저장 중 오류가 발생했습니다.')
  } finally {
    isSavingBook.value = false
  }
}
</script>

<style scoped>
.book-container {
  margin-top: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease;
}

.book-container h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.search-notice {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f0f4ff;
  border-left: 4px solid #667eea;
  border-radius: 8px;
}

.search-notice p {
  margin: 0.5rem 0;
  color: #555;
  font-size: 14px;
}

.input-group {
  margin-bottom: 1.5rem;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
  font-family: inherit;
}

.input-field:focus {
  outline: none;
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-recommend {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.btn-recommend:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 16px rgba(102, 126, 234, 0.4);
}

.btn-recommend:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.book-list {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  animation: slideDown 0.3s ease;
}

.book-list-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.book-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.book-card-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.book-thumbnail {
  width: 100%;
  max-width: 150px;
  height: auto;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.book-thumbnail img {
  width: 100%;
  height: auto;
  object-fit: cover;
  display: block;
}

.book-number-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.book-card-body {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 3em;
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.book-meta-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.book-meta-label {
  font-weight: 600;
  color: #666;
  min-width: 70px;
  flex-shrink: 0;
}

.book-meta-value {
  color: #333;
  flex: 1;
  word-break: break-word;
}

.book-description {
  font-size: 0.875rem;
  color: #555;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.book-category-tag {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(245, 87, 108, 0.2);
}

.book-card-footer {
  padding: 1rem 1.25rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.book-link-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  border: none;
  cursor: pointer;
}

.book-link-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.book-link-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.book-link-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.book-link-secondary:hover {
  background: #667eea;
  color: white;
}

.book-link-save {
  background: #4caf50;
  color: white;
  border: none;
}

.book-link-save:hover:not(:disabled) {
  background: #45a049;
}

.book-link-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #ffebee;
  border-left: 4px solid #f44336;
  border-radius: 8px;
  color: #c62828;
}

.error p {
  margin: 0;
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


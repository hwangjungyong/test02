<template>
  <div class="tab-content">
    <div v-if="loading" class="loading">
      <p>데이터를 불러오는 중...</p>
    </div>
    <div v-else>
      <div class="data-summary">
        <h3>📊 데이터 요약</h3>
        <div class="summary-cards">
          <div class="summary-card">
            <div class="summary-icon">📰</div>
            <div class="summary-info">
              <div class="summary-label">뉴스</div>
              <div class="summary-value">{{ userDataSummary.newsCount }}건</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">🎵</div>
            <div class="summary-info">
              <div class="summary-label">라디오 노래</div>
              <div class="summary-value">{{ userDataSummary.radioSongsCount }}건</div>
            </div>
          </div>
          <div class="summary-card">
            <div class="summary-icon">📚</div>
            <div class="summary-info">
              <div class="summary-label">도서</div>
              <div class="summary-value">{{ userDataSummary.booksCount }}건</div>
            </div>
          </div>
        </div>
      </div>

      <!-- 뉴스 데이터 -->
      <div v-if="userData.news && userData.news.length > 0" class="data-section">
        <h4>📰 뉴스 ({{ userData.news.length }}건)</h4>
        <div class="data-list">
          <div v-for="(item, index) in userData.news.slice(0, 10)" :key="index" class="data-item">
            <div class="data-item-title">{{ item.title }}</div>
            <div class="data-item-meta">
              <span>{{ item.source }}</span>
              <span>{{ formatDate(item.collectedAt) }}</span>
            </div>
          </div>
          <div v-if="userData.news.length > 10" class="data-more">
            외 {{ userData.news.length - 10 }}건 더...
          </div>
        </div>
      </div>

      <!-- 라디오 노래 데이터 -->
      <div v-if="userData.radioSongs && userData.radioSongs.length > 0" class="data-section">
        <h4>🎵 라디오 노래 ({{ userData.radioSongs.length }}건)</h4>
        <div class="data-list">
          <div v-for="(item, index) in userData.radioSongs.slice(0, 10)" :key="index" class="data-item">
            <div class="data-item-title">{{ item.title }} - {{ item.artist }}</div>
            <div class="data-item-meta">
              <span>{{ item.station }}</span>
              <span>{{ formatDate(item.playedAt || item.collectedAt) }}</span>
            </div>
          </div>
          <div v-if="userData.radioSongs.length > 10" class="data-more">
            외 {{ userData.radioSongs.length - 10 }}건 더...
          </div>
        </div>
      </div>

      <!-- 도서 데이터 -->
      <div v-if="userData.books && userData.books.length > 0" class="data-section">
        <h4>📚 도서 ({{ userData.books.length }}건)</h4>
        <div class="data-list">
          <div v-for="(item, index) in userData.books.slice(0, 10)" :key="index" class="data-item">
            <div class="data-item-title">{{ item.title }}</div>
            <div class="data-item-meta">
              <span>{{ item.authors }}</span>
              <span>{{ formatDate(item.collectedAt) }}</span>
            </div>
          </div>
          <div v-if="userData.books.length > 10" class="data-more">
            외 {{ userData.books.length - 10 }}건 더...
          </div>
        </div>
      </div>

      <div v-if="!userData.news?.length && !userData.radioSongs?.length && !userData.books?.length" class="no-data">
        <p>📭 저장된 데이터가 없습니다.</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import { useUserData } from '../../composables/useUserData.js'
import { formatDate } from '../../../../utils/helpers.js'

const {
  userData,
  userDataSummary,
  loading,
  loadDataSummary
} = useUserData()

onMounted(() => {
  loadDataSummary()
})
</script>


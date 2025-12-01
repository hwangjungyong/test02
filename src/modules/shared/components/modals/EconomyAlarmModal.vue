<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('close')">
    <div class="modal-content alarm-modal" @click.stop>
      <div class="modal-header">
        <h2>🔔 경제뉴스 알람</h2>
        <button @click="$emit('close')" class="btn-close">✕</button>
      </div>
      <div class="modal-body">
        <div v-if="alarmChecking" class="loading">
          <p>새로운 경제 뉴스를 확인하는 중...</p>
        </div>
        <div v-else-if="newEconomyNews.length > 0" class="alarm-results">
          <div class="alarm-summary">
            <h3>✨ 새로운 경제 뉴스 {{ newEconomyNews.length }}건 발견!</h3>
            <p class="alarm-time">확인 시간: {{ lastAlarmCheckTime }}</p>
          </div>
          <div class="alarm-news-list">
            <div v-for="(news, index) in newEconomyNews" :key="index" class="alarm-news-item">
              <div class="alarm-news-header">
                <span class="alarm-news-number">{{ index + 1 }}</span>
                <span class="alarm-news-importance">{{ news.importanceStars }}</span>
                <span class="alarm-news-date">{{ news.date }}</span>
              </div>
              <div class="alarm-news-title">
                <a :href="news.url" target="_blank" class="alarm-news-link">{{ news.title }}</a>
              </div>
              <div class="alarm-news-source">출처: {{ news.source }}</div>
              <div class="alarm-news-summary">{{ news.summary }}</div>
            </div>
          </div>
          <div class="alarm-actions">
            <button @click="$emit('save')" class="btn btn-save">💾 새 뉴스 저장하기</button>
            <button @click="$emit('close')" class="btn btn-close-alarm">닫기</button>
          </div>
        </div>
        <div v-else class="alarm-no-results">
          <p>📭 새로운 경제 뉴스가 없습니다.</p>
          <p class="alarm-time">확인 시간: {{ lastAlarmCheckTime }}</p>
          <button @click="$emit('close')" class="btn btn-close-alarm">닫기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  alarmChecking: {
    type: Boolean,
    default: false
  },
  newEconomyNews: {
    type: Array,
    default: () => []
  },
  lastAlarmCheckTime: {
    type: String,
    default: ''
  }
})

defineEmits(['close', 'save'])
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 90vw;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #eee;
}

.modal-header h2 {
  margin: 0;
  color: #333;
}

.btn-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-close:hover {
  color: #333;
}

.modal-body {
  padding: 20px;
  overflow-y: auto;
}

.loading {
  text-align: center;
  padding: 40px;
  color: #666;
}

.alarm-results {
  padding: 20px 0;
}

.alarm-summary {
  text-align: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 2px solid #e0e0e0;
}

.alarm-summary h3 {
  color: #667eea;
  font-size: 24px;
  margin-bottom: 8px;
}

.alarm-time {
  color: #999;
  font-size: 14px;
  margin: 0;
}

.alarm-news-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 24px;
  max-height: 400px;
  overflow-y: auto;
}

.alarm-news-item {
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.alarm-news-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.alarm-news-number {
  background: #667eea;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 12px;
}

.alarm-news-importance {
  font-size: 14px;
  font-weight: 600;
}

.alarm-news-date {
  margin-left: auto;
  color: #999;
  font-size: 12px;
}

.alarm-news-title {
  margin-bottom: 8px;
}

.alarm-news-link {
  color: #667eea;
  text-decoration: none;
  font-weight: 600;
  font-size: 16px;
}

.alarm-news-link:hover {
  text-decoration: underline;
}

.alarm-news-source {
  color: #666;
  font-size: 14px;
  margin-bottom: 8px;
}

.alarm-news-summary {
  color: #333;
  font-size: 14px;
  line-height: 1.6;
}

.alarm-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
  padding-top: 20px;
  border-top: 1px solid #e0e0e0;
}

.btn {
  padding: 12px 24px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.3s ease;
}

.btn-save {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-close-alarm {
  background: white;
  color: #667eea;
  padding: 12px 24px;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-close-alarm:hover {
  background: #667eea;
  color: white;
}

.alarm-no-results {
  padding: 40px 20px;
  text-align: center;
}

.alarm-no-results p {
  font-size: 18px;
  color: #666;
  margin-bottom: 12px;
}

.alarm-no-results .alarm-time {
  font-size: 14px;
  color: #999;
  margin-bottom: 24px;
}
</style>


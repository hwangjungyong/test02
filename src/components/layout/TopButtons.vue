<template>
  <div class="top-buttons">
    <!-- 인증 상태 표시 -->
    <div v-if="authStore.isAuthenticated" class="user-info">
      <span class="user-name">👤 {{ authStore.user?.name || authStore.user?.email }}</span>
      <button @click="$emit('openUserManagement')" class="btn btn-manage">사용자 관리하기</button>
      <button @click="$emit('logout')" class="btn btn-logout">로그아웃</button>
    </div>
    <div v-else class="auth-buttons">
      <button @click="$emit('showLogin')" class="btn btn-login">로그인</button>
      <button @click="$emit('showSignup')" class="btn btn-signup">회원가입</button>
    </div>
    
    <button @click="$emit('openDocsLibrary')" class="btn btn-docs-library">
      📚 가이드 문서
    </button>
    <button @click="$emit('openAPIDocs')" class="btn btn-api-docs">
      📚 API DOCS 보기
    </button>
    <button @click="$emit('toggleEconomyAlarm')" class="btn btn-alarm" :class="{ active: isEconomyAlarmEnabled }">
      🔔 {{ isEconomyAlarmEnabled ? '경제뉴스 알람 ON' : '경제뉴스 알람받기' }}
    </button>
    <button @click="$emit('showVoc')" class="btn btn-voc" style="background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%); color: white; border: none;">
      🌿 VOC 자동 대응
    </button>
  </div>
</template>

<script setup>
import { useAuthStore } from '../../stores/auth.js'

defineProps({
  isEconomyAlarmEnabled: {
    type: Boolean,
    default: false
  }
})

defineEmits(['openUserManagement', 'logout', 'showLogin', 'showSignup', 'openDocsLibrary', 'openAPIDocs', 'toggleEconomyAlarm', 'showVoc'])

const authStore = useAuthStore()
</script>

<style scoped>
.top-buttons {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
  z-index: 1000;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-name {
  font-weight: 600;
  color: #333;
}

.auth-buttons {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.2s;
}

.btn-login {
  background: #2196f3;
  color: white;
}

.btn-login:hover {
  background: #1976d2;
}

.btn-signup {
  background: #4caf50;
  color: white;
}

.btn-signup:hover {
  background: #388e3c;
}

.btn-manage {
  background: #667eea;
  color: white;
}

.btn-manage:hover {
  background: #5568d3;
}

.btn-logout {
  background: #f44336;
  color: white;
}

.btn-logout:hover {
  background: #d32f2f;
}

.btn-docs-library {
  background: #ff9800;
  color: white;
}

.btn-docs-library:hover {
  background: #f57c00;
}

.btn-api-docs {
  background: #9c27b0;
  color: white;
}

.btn-api-docs:hover {
  background: #7b1fa2;
}

.btn-alarm {
  background: #ff5722;
  color: white;
}

.btn-alarm:hover {
  background: #e64a19;
}

.btn-alarm.active {
  background: #4caf50;
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.7;
  }
}

.btn-voc:hover {
  opacity: 0.9;
  transform: translateY(-2px);
}
</style>


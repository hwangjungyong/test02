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
import { useAuthStore } from '../../../stores/auth.js'

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
  top: 15px;
  right: 15px;
  left: 15px;
  z-index: 1000;
  display: flex;
  flex-direction: row;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  padding: 10px;
  background: rgba(36, 36, 36, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 100%;
  box-sizing: border-box;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 0;
  flex-wrap: wrap;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}

.btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-login,
.btn-signup,
.btn-logout,
.btn-manage {
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-signup {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-signup:hover {
  background: #667eea;
  color: white;
}

.btn-logout {
  background: #f44336;
  color: white;
}

.btn-logout:hover {
  background: #d32f2f;
  transform: translateY(-2px);
}

.btn-manage {
  background: #2196f3;
  color: white;
}

.btn-manage:hover {
  background: #1976d2;
  transform: translateY(-2px);
}

.auth-buttons {
  display: flex;
  gap: 10px;
  margin-right: 0;
  flex-wrap: wrap;
}

.btn-docs-library {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
  box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
}

.btn-docs-library:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-api-docs {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.btn-api-docs:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(245, 87, 108, 0.4);
}

.btn-alarm {
  background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.btn-alarm:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(255, 152, 0, 0.4);
}

.btn-alarm.active {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
}

.btn-voc {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-voc:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(76, 175, 80, 0.4);
}
</style>


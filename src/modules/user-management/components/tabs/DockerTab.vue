<template>
  <div class="tab-content">
    <h3>🐳 Docker 컨테이너 상태</h3>
    <p style="margin-bottom: 20px; color: #666;">
      현재 실행 중인 Docker 컨테이너의 상태를 확인할 수 있습니다.
    </p>

    <div v-if="loading" class="loading">
      <p>Docker 상태를 불러오는 중...</p>
    </div>

    <div v-else-if="error" class="error-message" style="white-space: pre-line;">
      {{ error }}
    </div>

    <div v-else-if="dockerStatus">
      <!-- WSL 환경 안내 -->
      <div v-if="dockerStatus.docker?.useWSL" style="margin-bottom: 24px; padding: 16px; background: #e3f2fd; border-left: 4px solid #2196f3; border-radius: 4px;">
        <h4 style="margin-top: 0; color: #1976d2;">🐧 WSL 2 환경 감지됨</h4>
        <p style="margin: 8px 0; color: #424242;">
          {{ dockerStatus.docker?.wslMessage || 'WSL 2 환경에서 Docker Engine을 사용 중입니다. 모든 명령어는 WSL을 통해 실행됩니다.' }}
        </p>
        <div style="margin-top: 12px; padding: 12px; background: white; border-radius: 4px;">
          <strong style="color: #1976d2;">사용 방법:</strong>
          <ul style="margin: 8px 0; padding-left: 20px; color: #424242;">
            <li style="margin-bottom: 8px;">
              <strong>WSL 2 내에서 Docker Engine 설치 (아직 설치하지 않은 경우):</strong>
              <div style="margin-top: 4px; padding: 8px; background: #f5f5f5; border-radius: 4px; font-family: monospace; font-size: 12px;">
                wsl -d Ubuntu<br>
                curl -fsSL https://get.docker.com -o get-docker.sh<br>
                sudo sh get-docker.sh<br>
                sudo usermod -aG docker $USER
              </div>
            </li>
            <li style="margin-bottom: 8px;">
              <strong>Docker 서비스 시작:</strong>
              <div style="margin-top: 4px; padding: 8px; background: #f5f5f5; border-radius: 4px; font-family: monospace; font-size: 12px;">
                sudo service docker start
              </div>
            </li>
            <li>
              <strong>Windows에서 WSL의 Docker 사용:</strong>
              <div style="margin-top: 4px; padding: 8px; background: #f5f5f5; border-radius: 4px; font-family: monospace; font-size: 12px;">
                # WSL 접두사를 붙여서 실행<br>
                wsl docker ps<br>
                wsl docker-compose up -d
              </div>
            </li>
          </ul>
        </div>
        <p style="margin-top: 12px; font-size: 12px; color: #666;">
          💡 <strong>참고:</strong> WSL 2 환경에서는 모든 Docker 명령어에 <code>wsl</code> 접두사가 자동으로 추가됩니다.
        </p>
      </div>

      <!-- Docker 설치 상태 -->
      <div class="docker-info-section" style="margin-bottom: 24px; padding: 16px; background: #f5f5f5; border-radius: 8px;">
        <h4 style="margin-top: 0;">Docker 정보</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 12px;">
          <div>
            <strong>설치 여부:</strong>
            <span :style="{ color: dockerStatus.docker?.installed ? '#4caf50' : '#ff9800' }">
              {{ dockerStatus.docker?.installed ? '✅ 설치됨' : '⚠️ 미설치 (선택사항)' }}
            </span>
          </div>
          <div v-if="dockerStatus.docker?.installed">
            <strong>버전:</strong> {{ dockerStatus.docker?.version || 'N/A' }}
          </div>
          <div>
            <strong>실행 상태:</strong>
            <span :style="{ color: dockerStatus.docker?.running ? '#4caf50' : '#ff9800' }">
              {{ dockerStatus.docker?.running ? '✅ 실행 중' : '⏸️ 중지됨' }}
            </span>
          </div>
        </div>
        
        <!-- Docker 없이도 개발 가능 안내 -->
        <div v-if="!dockerStatus.docker?.installed" style="margin-top: 16px; padding: 12px; background: #e8f5e9; border-left: 4px solid #4caf50; border-radius: 4px;">
          <h5 style="margin: 0 0 8px 0; color: #2e7d32;">💡 Docker 없이도 개발 가능합니다!</h5>
          <p style="margin: 0 0 8px 0; color: #424242; font-size: 14px;">
            이 프로젝트는 Docker 없이도 개발할 수 있습니다. 다음 명령어로 실행하세요:
          </p>
          <div style="background: white; padding: 12px; border-radius: 4px; font-family: monospace; font-size: 12px; margin-top: 8px;">
            <div style="margin-bottom: 4px;"><strong>모든 서버 실행:</strong></div>
            <div style="color: #1976d2;">npm run start:all</div>
            <div style="margin-top: 8px; margin-bottom: 4px;"><strong>또는 개별 실행:</strong></div>
            <div style="color: #1976d2;">npm run api-server</div>
            <div style="color: #1976d2;">npm run dev</div>
          </div>
          <p style="margin: 8px 0 0 0; font-size: 12px; color: #666;">
            Docker는 배포나 프로덕션 환경에서만 필요합니다. 개발 중에는 선택사항입니다.
          </p>
        </div>
        
        <!-- 컨테이너 제어 버튼 -->
        <div v-if="dockerStatus.docker?.installed" style="margin-top: 16px; padding-top: 16px; border-top: 1px solid #ddd;">
          <h5 style="margin: 0 0 12px 0;">컨테이너 제어</h5>
          <div style="display: flex; gap: 8px; flex-wrap: wrap;">
            <button 
              @click="startContainers" 
              class="btn"
              :disabled="actionLoading"
              style="background: #4caf50; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;"
            >
              {{ actionLoading ? '실행 중...' : '▶️ 컨테이너 시작' }}
            </button>
            <button 
              @click="stopContainers" 
              class="btn"
              :disabled="actionLoading"
              style="background: #f44336; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;"
            >
              {{ actionLoading ? '중지 중...' : '⏹️ 컨테이너 중지' }}
            </button>
            <button 
              @click="restartContainers" 
              class="btn"
              :disabled="actionLoading"
              style="background: #ff9800; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;"
            >
              {{ actionLoading ? '재시작 중...' : '🔄 컨테이너 재시작' }}
            </button>
            <button 
              @click="loadStatus" 
              class="btn"
              :disabled="loading"
              style="background: #2196f3; color: white; border: none; padding: 8px 16px; border-radius: 4px; cursor: pointer; font-size: 14px;"
            >
              {{ loading ? '새로고침 중...' : '🔄 상태 새로고침' }}
            </button>
          </div>
          <div v-if="actionMessage" style="margin-top: 12px; padding: 8px; background: #e3f2fd; border-left: 3px solid #2196f3; border-radius: 4px; font-size: 12px;">
            {{ actionMessage }}
          </div>
        </div>
      </div>

      <!-- 컨테이너 목록 -->
      <div v-if="dockerStatus.docker?.containers && dockerStatus.docker.containers.length > 0">
        <h4>실행 중인 컨테이너 ({{ dockerStatus.docker.containers.length }}개)</h4>
        <div class="docker-containers-list" style="margin-top: 16px;">
          <div 
            v-for="container in dockerStatus.docker.containers" 
            :key="container.name"
            class="docker-container-card"
            style="padding: 16px; margin-bottom: 12px; border: 1px solid #ddd; border-radius: 8px; background: white;"
          >
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 12px;">
              <div>
                <h5 style="margin: 0 0 8px 0; color: #333;">
                  {{ container.name }}
                </h5>
                <div style="font-size: 12px; color: #666;">
                  <div><strong>이미지:</strong> {{ container.image }}</div>
                  <div style="margin-top: 4px;">
                    <strong>포트:</strong> {{ container.ports }}
                  </div>
                </div>
              </div>
              <div>
                <span 
                  :style="{ 
                    padding: '4px 12px', 
                    borderRadius: '12px', 
                    fontSize: '12px',
                    fontWeight: 'bold',
                    color: container.running ? '#4caf50' : '#f44336',
                    background: container.running ? '#e8f5e9' : '#ffebee'
                  }"
                >
                  {{ container.running ? '실행 중' : '중지됨' }}
                </span>
              </div>
            </div>
            <div style="font-size: 12px; color: #888;">
              {{ container.status }}
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="dockerStatus.docker?.installed" class="no-containers" style="padding: 24px; text-align: center; color: #666;">
        <p>실행 중인 컨테이너가 없습니다.</p>
        <p style="font-size: 12px; margin-top: 8px;">
          컨테이너를 시작하려면: <code>docker-compose up -d</code>
        </p>
      </div>

      <div v-if="dockerStatus.message" style="margin-top: 16px; padding: 12px; background: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
        <strong>알림:</strong> {{ dockerStatus.message }}
      </div>
    </div>

    <div style="margin-top: 24px; padding-top: 24px; border-top: 1px solid #ddd;">
      <h4>Docker 명령어 가이드</h4>
      <div style="background: #f5f5f5; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 12px;">
        <div v-if="dockerStatus?.docker?.useWSL" style="margin-bottom: 12px; padding: 8px; background: #e3f2fd; border-left: 3px solid #2196f3; border-radius: 4px;">
          <strong style="color: #1976d2;">🐧 WSL 환경:</strong> 다음 명령어는 WSL 2를 통해 실행됩니다.
        </div>
        <div style="margin-bottom: 8px;">
          <strong>컨테이너 시작:</strong> 
          <span v-if="dockerStatus?.docker?.useWSL">wsl docker-compose up -d</span>
          <span v-else>docker-compose up -d</span>
        </div>
        <div style="margin-bottom: 8px;">
          <strong>컨테이너 중지:</strong> 
          <span v-if="dockerStatus?.docker?.useWSL">wsl docker-compose down</span>
          <span v-else>docker-compose down</span>
        </div>
        <div style="margin-bottom: 8px;">
          <strong>컨테이너 재시작:</strong> 
          <span v-if="dockerStatus?.docker?.useWSL">wsl docker-compose restart</span>
          <span v-else>docker-compose restart</span>
        </div>
        <div style="margin-bottom: 8px;">
          <strong>로그 확인:</strong> 
          <span v-if="dockerStatus?.docker?.useWSL">wsl docker logs test02-frontend</span>
          <span v-else>docker logs test02-frontend</span>
        </div>
        <div>
          <strong>상태 확인:</strong> 
          <span v-if="dockerStatus?.docker?.useWSL">wsl docker ps</span>
          <span v-else>docker ps</span>
        </div>
        <div v-if="dockerStatus?.docker?.useWSL" style="margin-top: 12px; padding-top: 12px; border-top: 1px solid #ddd; font-size: 11px; color: #666;">
          💡 <strong>팁:</strong> WSL 2 내에서 직접 실행하려면 <code>wsl</code> 명령어로 진입한 후 명령어를 실행하세요.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useDocker } from '../../composables/useDocker.js'
import { onMounted } from 'vue'

const {
  dockerStatus,
  loading,
  error,
  actionLoading,
  actionMessage,
  loadStatus,
  startContainers,
  stopContainers,
  restartContainers
} = useDocker()

onMounted(() => {
  loadStatus()
})
</script>


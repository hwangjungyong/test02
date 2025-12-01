/**
 * Docker 관리 Composable
 */

import { ref } from 'vue'
import { getDockerStatus, startDockerContainers, stopDockerContainers, restartDockerContainers } from '../services/userService.js'

export function useDocker() {
  const dockerStatus = ref(null)
  const loading = ref(false)
  const error = ref('')
  const actionLoading = ref(false)
  const actionMessage = ref('')

  /**
   * Docker 상태 로드
   */
  async function loadStatus() {
    loading.value = true
    error.value = ''
    actionMessage.value = ''

    try {
      dockerStatus.value = await getDockerStatus()
    } catch (err) {
      console.error('[Docker 상태 로드] 상세 오류:', err)
      
      let errorMessage = 'Docker 상태를 불러오는 중 오류가 발생했습니다.'
      
      if (err.message) {
        errorMessage += `\n\n오류 내용: ${err.message}`
      }
      
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        errorMessage += '\n\n서버에 연결할 수 없습니다. API 서버가 실행 중인지 확인하세요.'
        errorMessage += '\n확인 방법: http://localhost:3001/api/docker/status'
      }
      
      error.value = errorMessage
    } finally {
      loading.value = false
    }
  }

  /**
   * Docker 컨테이너 시작
   */
  async function startContainers() {
    actionLoading.value = true
    actionMessage.value = ''

    try {
      const message = await startDockerContainers()
      actionMessage.value = message
      // 상태 새로고침
      setTimeout(() => {
        loadStatus()
      }, 2000)
    } catch (err) {
      console.error('[컨테이너 시작] 오류:', err)
      actionMessage.value = err.message || '컨테이너 시작 중 오류가 발생했습니다.'
    } finally {
      actionLoading.value = false
    }
  }

  /**
   * Docker 컨테이너 중지
   */
  async function stopContainers() {
    actionLoading.value = true
    actionMessage.value = ''

    try {
      const message = await stopDockerContainers()
      actionMessage.value = message
      // 상태 새로고침
      setTimeout(() => {
        loadStatus()
      }, 2000)
    } catch (err) {
      console.error('[컨테이너 중지] 오류:', err)
      actionMessage.value = err.message || '컨테이너 중지 중 오류가 발생했습니다.'
    } finally {
      actionLoading.value = false
    }
  }

  /**
   * Docker 컨테이너 재시작
   */
  async function restartContainers() {
    actionLoading.value = true
    actionMessage.value = ''

    try {
      const message = await restartDockerContainers()
      actionMessage.value = message
      // 상태 새로고침
      setTimeout(() => {
        loadStatus()
      }, 2000)
    } catch (err) {
      console.error('[컨테이너 재시작] 오류:', err)
      actionMessage.value = err.message || '컨테이너 재시작 중 오류가 발생했습니다.'
    } finally {
      actionLoading.value = false
    }
  }

  return {
    dockerStatus,
    loading,
    error,
    actionLoading,
    actionMessage,
    loadStatus,
    startContainers,
    stopContainers,
    restartContainers
  }
}


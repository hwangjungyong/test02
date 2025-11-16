import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  // 상태
  const user = ref(null)
  const token = ref(localStorage.getItem('token') || null)
  const isLoading = ref(false)

  // 계산된 속성
  const isAuthenticated = computed(() => !!token.value && !!user.value)

  // 액션
  async function login(email, password) {
    isLoading.value = true
    try {
      const response = await fetch('http://localhost:3001/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password })
      })

      const data = await response.json()

      if (data.success) {
        token.value = data.token
        user.value = data.user
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return { success: true, message: data.message }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('[로그인] 상세 오류:', error)
      
      // 연결 거부 오류인 경우 명확한 메시지 표시
      if (error.message && error.message.includes('Failed to fetch')) {
        return { 
          success: false, 
          error: '서버에 연결할 수 없습니다.\n\nAPI 서버가 실행 중인지 확인하세요.\n서버 시작: npm run api-server 또는 start-dev.bat' 
        }
      }
      
      return { 
        success: false, 
        error: `로그인 중 오류가 발생했습니다: ${error.message || '알 수 없는 오류'}` 
      }
    } finally {
      isLoading.value = false
    }
  }

  async function signup(email, password, name) {
    isLoading.value = true
    try {
      const response = await fetch('http://localhost:3001/api/auth/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ email, password, name })
      })

      const data = await response.json()

      if (data.success) {
        token.value = data.token
        user.value = data.user
        localStorage.setItem('token', data.token)
        localStorage.setItem('user', JSON.stringify(data.user))
        return { success: true, message: data.message }
      } else {
        return { success: false, error: data.error }
      }
    } catch (error) {
      console.error('[회원가입] 상세 오류:', error)
      
      // 연결 거부 오류인 경우 명확한 메시지 표시
      if (error.message && error.message.includes('Failed to fetch')) {
        return { 
          success: false, 
          error: '서버에 연결할 수 없습니다.\n\nAPI 서버가 실행 중인지 확인하세요.\n서버 시작: npm run api-server 또는 start-dev.bat' 
        }
      }
      
      return { 
        success: false, 
        error: `회원가입 중 오류가 발생했습니다: ${error.message || '알 수 없는 오류'}` 
      }
    } finally {
      isLoading.value = false
    }
  }

  async function fetchUser() {
    if (!token.value) return

    try {
      const response = await fetch('http://localhost:3001/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${token.value}`
        }
      })

      const data = await response.json()

      if (data.success) {
        user.value = data.user
        localStorage.setItem('user', JSON.stringify(data.user))
      } else {
        logout()
      }
    } catch (error) {
      console.error('사용자 정보 조회 오류:', error)
      logout()
    }
  }

  function logout() {
    user.value = null
    token.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
  }

  // 초기화: localStorage에서 사용자 정보 불러오기
  function init() {
    const storedToken = localStorage.getItem('token')
    const storedUser = localStorage.getItem('user')

    if (storedToken && storedUser) {
      token.value = storedToken
      try {
        user.value = JSON.parse(storedUser)
        // 토큰 유효성 확인
        fetchUser()
      } catch (error) {
        logout()
      }
    }
  }

  return {
    // 상태
    user,
    token,
    isLoading,
    // 계산된 속성
    isAuthenticated,
    // 액션
    login,
    signup,
    logout,
    fetchUser,
    init
  }
})


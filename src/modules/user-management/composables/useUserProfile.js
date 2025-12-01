/**
 * 사용자 프로필 관리 Composable
 */

import { ref } from 'vue'
import { getUserProfile, updateUserProfile } from '../services/userService.js'

export function useUserProfile() {
  const userProfile = ref(null)
  const profileForm = ref({
    email: '',
    name: ''
  })
  const loading = ref(false)
  const updating = ref(false)
  const error = ref('')
  const success = ref('')

  /**
   * 프로필 정보 로드
   */
  async function loadProfile() {
    loading.value = true
    error.value = ''

    try {
      const profile = await getUserProfile()
      userProfile.value = profile
      profileForm.value = {
        email: profile.email || '',
        name: profile.name || ''
      }
    } catch (err) {
      console.error('프로필 로드 오류:', err)
      error.value = err.message || '프로필 정보를 불러오는데 실패했습니다.'
    } finally {
      loading.value = false
    }
  }

  /**
   * 프로필 수정
   */
  async function updateProfile() {
    updating.value = true
    error.value = ''
    success.value = ''

    try {
      const updatedProfile = await updateUserProfile({
        email: profileForm.value.email,
        name: profileForm.value.name
      })

      userProfile.value = updatedProfile
      success.value = '프로필이 수정되었습니다.'

      // 2초 후 성공 메시지 제거
      setTimeout(() => {
        success.value = ''
      }, 2000)
    } catch (err) {
      console.error('프로필 수정 오류:', err)
      error.value = err.message || '프로필 수정에 실패했습니다.'
    } finally {
      updating.value = false
    }
  }

  /**
   * 에러 및 성공 메시지 초기화
   */
  function resetMessages() {
    error.value = ''
    success.value = ''
  }

  return {
    userProfile,
    profileForm,
    loading,
    updating,
    error,
    success,
    loadProfile,
    updateProfile,
    resetMessages
  }
}


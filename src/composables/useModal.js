/**
 * 모달 상태 관리를 위한 Composable
 * @returns {Object} 모달 관련 상태 및 메서드
 */
import { ref } from 'vue'

export function useModal(initialValue = false) {
  const isOpen = ref(initialValue)

  const open = () => {
    isOpen.value = true
  }

  const close = () => {
    isOpen.value = false
  }

  const toggle = () => {
    isOpen.value = !isOpen.value
  }

  return {
    isOpen,
    open,
    close,
    toggle
  }
}


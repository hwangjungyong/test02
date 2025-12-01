/**
 * 포맷팅 관련 유틸리티 Composable
 */
import { formatDate, formatDateTime } from '../utils/helpers.js'

export function useFormatting() {
  return {
    formatDate,
    formatDateTime
  }
}


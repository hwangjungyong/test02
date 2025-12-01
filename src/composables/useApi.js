/**
 * API 호출을 위한 Composable
 */
import { ref } from 'vue'
import { get, post, put, del } from '../services/baseService.js'
import { getErrorMessage } from '../utils/helpers.js'

export function useApi() {
  const loading = ref(false)
  const error = ref('')

  const executeRequest = async (requestFn, ...args) => {
    loading.value = true
    error.value = ''
    try {
      const result = await requestFn(...args)
      return result
    } catch (err) {
      error.value = getErrorMessage(err)
      throw err
    } finally {
      loading.value = false
    }
  }

  const apiGet = async (endpoint, params = {}) => {
    return executeRequest(get, endpoint, params)
  }

  const apiPost = async (endpoint, data = {}) => {
    return executeRequest(post, endpoint, data)
  }

  const apiPut = async (endpoint, data = {}) => {
    return executeRequest(put, endpoint, data)
  }

  const apiDelete = async (endpoint) => {
    return executeRequest(del, endpoint)
  }

  return {
    loading,
    error,
    apiGet,
    apiPost,
    apiPut,
    apiDelete
  }
}


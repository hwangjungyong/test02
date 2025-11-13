import { createApp } from 'vue'
import { createPinia } from 'pinia'
import './style.css'
import App from './App.vue'
import { useAuthStore } from './stores/auth.js'

const app = createApp(App)
const pinia = createPinia()

app.use(pinia)

// 인증 스토어 초기화
const authStore = useAuthStore()
authStore.init()

app.mount('#app')




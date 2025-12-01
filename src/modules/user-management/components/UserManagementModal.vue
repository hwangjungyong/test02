<template>
  <div v-if="modelValue" class="modal-overlay" @click="$emit('update:modelValue', false)">
    <div class="modal-content user-management-modal" @click.stop>
      <div class="modal-header">
        <h2>👤 사용자 관리</h2>
        <button @click="$emit('update:modelValue', false)" class="btn-close">✕</button>
      </div>
      <div class="modal-body">
        <!-- 탭 메뉴 -->
        <div class="user-tabs">
          <button 
            @click="currentTab = 'profile'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'profile' }"
          >
            프로필
          </button>
          <button 
            @click="currentTab = 'data'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'data' }"
          >
            내 데이터
          </button>
          <button 
            @click="currentTab = 'api-keys'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'api-keys' }"
          >
            API 키 관리
          </button>
          <button 
            @click="currentTab = 'db-schema'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'db-schema' }"
          >
            📊 DB 스키마
          </button>
          <button 
            @click="currentTab = 'docker'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'docker' }"
          >
            🐳 Docker 상태
          </button>
          <button 
            @click="currentTab = 'error-logs'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'error-logs' }"
          >
            🔍 AI에러로그현황
          </button>
          <button 
            @click="currentTab = 'delete'" 
            class="tab-btn" 
            :class="{ active: currentTab === 'delete' }"
          >
            계정 삭제
          </button>
        </div>

        <!-- 탭 컨텐츠 -->
        <ProfileTab v-if="currentTab === 'profile'" />
        <DataTab v-if="currentTab === 'data'" />
        <ApiKeysTab v-if="currentTab === 'api-keys'" />
        <DbSchemaTab v-if="currentTab === 'db-schema'" />
        <DockerTab v-if="currentTab === 'docker'" />
        <ErrorLogsTab 
          v-if="currentTab === 'error-logs'" 
          @show-detail="handleShowErrorLogDetail"
        />
        <DeleteAccountTab 
          v-if="currentTab === 'delete'" 
          @close="$emit('update:modelValue', false)"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import ProfileTab from './tabs/ProfileTab.vue'
import DataTab from './tabs/DataTab.vue'
import ApiKeysTab from './tabs/ApiKeysTab.vue'
import DbSchemaTab from './tabs/DbSchemaTab.vue'
import DockerTab from './tabs/DockerTab.vue'
import ErrorLogsTab from './tabs/ErrorLogsTab.vue'
import DeleteAccountTab from './tabs/DeleteAccountTab.vue'

const props = defineProps({
  modelValue: Boolean
})

const emit = defineEmits(['update:modelValue', 'show-error-log-detail'])

const currentTab = ref('profile')

// 모달이 열릴 때 프로필 탭으로 초기화
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    currentTab.value = 'profile'
  }
})

function handleShowErrorLogDetail(log) {
  emit('show-error-log-detail', log)
}
</script>


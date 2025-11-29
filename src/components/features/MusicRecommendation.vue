<template>
  <div v-if="modelValue" class="music-container">
    <h2>🎵 AI 노래 추천</h2>
    <div class="input-group">
      <label for="songTitle">좋아하는 노래 제목:</label>
      <input
        id="songTitle"
        v-model="songTitle"
        type="text"
        placeholder="예: Dynamite"
        class="input-field"
      />
    </div>
    <div class="input-group">
      <label for="artist">아티스트 (선택사항):</label>
      <input
        id="artist"
        v-model="artist"
        type="text"
        placeholder="예: BTS"
        class="input-field"
      />
    </div>
    <button @click="recommendSongs" class="btn btn-recommend">
      추천 받기
    </button>
    <div v-if="recommendations.length > 0" class="recommendations">
      <h3>추천 노래 목록</h3>
      <div class="song-list">
        <div v-for="(song, index) in recommendations" :key="index" class="song-item">
          <div class="song-number">{{ index + 1 }}</div>
          <div class="song-info">
            <div class="song-title">{{ song.title }}</div>
            <div class="song-artist">{{ song.artist }}</div>
            <div class="song-reason">💡 {{ song.reason }}</div>
          </div>
        </div>
      </div>
    </div>
    <div v-if="musicError" class="error">
      <p>{{ musicError }}</p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: { type: Boolean, default: false }
})

const songTitle = ref('')
const artist = ref('')
const recommendations = ref([])
const musicError = ref('')

const musicRecommendations = {
  'BTS': [
    { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
    { title: 'Spring Day', artist: 'BTS', reason: '인기 K-Pop 노래' },
    { title: 'Butter', artist: 'BTS', reason: '인기 K-Pop 노래' }
  ],
  'IU': [
    { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
    { title: 'Good Day', artist: 'IU', reason: '인기 K-Pop 노래' }
  ]
}

const recommendSongs = async () => {
  musicError.value = ''
  recommendations.value = []

  if (!songTitle.value || songTitle.value.trim() === '') {
    musicError.value = '노래 제목을 입력해주세요.'
    return
  }

  try {
    const params = new URLSearchParams({
      songTitle: songTitle.value.trim()
    })
    if (artist.value && artist.value.trim()) {
      params.append('artist', artist.value.trim())
    }
    
    const apiUrl = `/api/music/recommend?${params.toString()}`
    const response = await fetch(apiUrl)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`Last.fm API 오류: ${response.status} - ${errorData.error || response.statusText}`)
    }

    const data = await response.json()
    let foundRecommendations = []
    
    if (data.similartracks && data.similartracks.track && data.similartracks.track.length > 0) {
      foundRecommendations = data.similartracks.track.slice(0, 10).map(track => ({
        title: track.name || '제목 없음',
        artist: track.artist?.name || '아티스트 없음',
        reason: 'Last.fm 유사 트랙 추천'
      }))
    }

    if (foundRecommendations.length === 0) {
      if (artist.value && musicRecommendations[artist.value]) {
        foundRecommendations = musicRecommendations[artist.value]
      } else {
        foundRecommendations = [
          { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
          { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
          { title: 'How You Like That', artist: 'BLACKPINK', reason: '인기 K-Pop 노래' }
        ]
      }
    }

    recommendations.value = foundRecommendations
  } catch (error) {
    console.error('음악 추천 오류:', error)
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      musicError.value = 'API 서버 연결 실패: API 서버가 실행 중인지 확인하세요. (포트 3001)'
    } else {
      musicError.value = `음악 추천 중 오류가 발생했습니다: ${error.message}`
    }
    
    const fallbackRecommendations = [
      { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
      { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
      { title: 'How You Like That', artist: 'BLACKPINK', reason: '인기 K-Pop 노래' }
    ]
    recommendations.value = fallbackRecommendations
  }
}
</script>

<style scoped>
.music-container {
  margin-top: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  animation: slideDown 0.3s ease;
}

.music-container h2 {
  color: #a78bfa;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  text-align: center;
}

.input-group {
  margin-bottom: 1.5rem;
  text-align: left;
}

.input-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: #35495e;
  font-weight: 600;
  font-size: 18px;
}

.input-field {
  width: 100%;
  padding: 12px 16px;
  font-size: 18px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  transition: border-color 0.3s ease;
  box-sizing: border-box;
}

.input-field:focus {
  outline: none;
  border-color: #a78bfa;
  box-shadow: 0 0 0 3px rgba(167, 139, 250, 0.1);
}

.btn-recommend {
  width: 100%;
  padding: 14px;
  background: linear-gradient(135deg, #a78bfa 0%, #c084fc 100%);
  color: white;
  font-size: 20px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-recommend:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(167, 139, 250, 0.4);
}

.recommendations {
  margin-top: 2rem;
  padding: 1.5rem;
  background: rgba(167, 139, 250, 0.1);
  border-radius: 8px;
  border: 2px solid #a78bfa;
}

.recommendations h3 {
  color: #a78bfa;
  margin-bottom: 1rem;
}

.song-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.song-item {
  display: flex;
  gap: 1rem;
  padding: 1rem;
  background: white;
  border-radius: 8px;
  border: 1px solid #e0e0e0;
}

.song-number {
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #a78bfa;
  color: white;
  border-radius: 50%;
  font-weight: 600;
  flex-shrink: 0;
}

.song-info {
  flex: 1;
}

.song-title {
  font-weight: 600;
  font-size: 1.1rem;
  color: #333;
  margin-bottom: 0.25rem;
}

.song-artist {
  color: #666;
  margin-bottom: 0.5rem;
}

.song-reason {
  color: #a78bfa;
  font-size: 14px;
}

.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #ffebee;
  color: #c62828;
  border-radius: 8px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>


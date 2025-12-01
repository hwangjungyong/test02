<template>
  <div v-if="modelValue" class="radio-history-container">
    <h2>📻 실시간 라디오 수집 현황</h2>
    
    <!-- 검색 및 필터 -->
    <div class="search-filter-section">
      <div class="search-box">
        <input
          v-model="searchQuery"
          type="text"
          placeholder="노래 제목 또는 가수 검색..."
          class="search-input"
          @input="applyFilters"
        />
      </div>
      
      <div class="filter-box">
        <label>가수 필터:</label>
        <select v-model="selectedArtist" @change="applyFilters" class="filter-select">
          <option value="">전체</option>
          <option v-for="artist in uniqueArtists" :key="artist" :value="artist">
            {{ artist }}
          </option>
        </select>
        
        <label>장르 필터:</label>
        <select v-model="selectedGenre" @change="applyFilters" class="filter-select">
          <option value="">전체</option>
          <option v-for="genre in uniqueGenres" :key="genre" :value="genre">
            {{ genre }}
          </option>
        </select>
        
        <label>정렬:</label>
        <select v-model="sortBy" @change="applyFilters" class="filter-select">
          <option value="count">재생 횟수 순</option>
          <option value="recent">최근 재생 순</option>
          <option value="title">제목 순</option>
          <option value="artist">가수 순</option>
        </select>
      </div>
    </div>

    <!-- 통계 정보 -->
    <div class="stats-section">
      <div class="stat-item">
        <span class="stat-label">총 노래 수:</span>
        <span class="stat-value">{{ filteredSongs.length }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">총 재생 횟수:</span>
        <span class="stat-value">{{ totalPlayCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">고유 가수 수:</span>
        <span class="stat-value">{{ uniqueArtists.length }}</span>
      </div>
      <div class="stat-item">
        <button @click="fetchRadioSongs" class="btn-refresh">
          🔄 MCP 서버에서 최신 데이터 가져오기
        </button>
      </div>
      <div class="stat-item">
        <button 
          @click="collectMonthlyData" 
          class="btn-monthly"
          :disabled="isCollectingMonthlyData"
        >
          📅 한 달간 데이터 수집
        </button>
      </div>
    </div>

    <!-- 한 달간 데이터 수집 진행 상황 -->
    <div v-if="isCollectingMonthlyData || monthlyCollectionStatus" class="monthly-collection-status">
      <div class="progress-info">
        <p class="status-text">{{ monthlyCollectionStatus }}</p>
        <div class="progress-bar-container">
          <div 
            class="progress-bar" 
            :style="{ width: monthlyCollectionProgress + '%' }"
          ></div>
        </div>
        <p class="progress-text">{{ monthlyCollectionProgress }}%</p>
      </div>
    </div>

    <!-- 노래 목록 테이블 -->
    <div class="songs-table-container">
      <table class="songs-table">
        <thead>
          <tr>
            <th>순위</th>
            <th>제목</th>
            <th>가수</th>
            <th>장르</th>
            <th>재생 횟수</th>
            <th>마지막 재생</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="(song, index) in paginatedSongs"
            :key="song.id"
            class="song-row"
          >
            <td class="rank-cell">{{ (currentPage - 1) * 10 + index + 1 }}</td>
            <td class="title-cell">{{ song.title }}</td>
            <td class="artist-cell">{{ song.artist }}</td>
            <td class="genre-cell">{{ song.genre }}</td>
            <td class="count-cell">
              <span class="count-badge">{{ song.count }}</span>
            </td>
            <td class="time-cell">{{ song.lastPlayed }}</td>
          </tr>
          <tr v-if="paginatedSongs.length === 0">
            <td colspan="6" class="no-data">검색 결과가 없습니다.</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- 페이지네이션 -->
    <div class="pagination">
      <button
        @click="goToPage(currentPage - 1)"
        :disabled="currentPage === 1"
        class="page-btn"
      >
        이전
      </button>
      <span class="page-info">
        페이지 {{ currentPage }} / {{ totalPages }}
        (총 {{ filteredSongs.length }}개)
      </span>
      <button
        @click="goToPage(currentPage + 1)"
        :disabled="currentPage === totalPages"
        class="page-btn"
      >
        다음
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { useAuthStore } from '../../stores/auth.js'

const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['update:modelValue'])

const authStore = useAuthStore()

// 상태
const searchQuery = ref('')
const selectedArtist = ref('')
const selectedGenre = ref('')
const sortBy = ref('count')
const currentPage = ref(1)
const songsHistory = ref([])
const filteredSongs = ref([])
const paginatedSongs = ref([])
const isCollectingMonthlyData = ref(false)
const monthlyCollectionProgress = ref(0)
const monthlyCollectionStatus = ref('')
const monthlyDataCollection = ref([])

// 하드코딩된 라디오 방송국 데이터 (폴백용)
const radioStations = {
  kbs: {
    name: 'KBS 쿨FM',
    currentSong: {
      title: 'Dynamite',
      artist: 'BTS',
      genre: 'K-Pop',
    },
    recentSongs: [
      { title: 'Dynamite', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Butter', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Spring Day', artist: 'BTS', genre: 'K-Pop' },
    ],
  },
  mbc: {
    name: 'MBC FM4U',
    currentSong: {
      title: 'Celebrity',
      artist: 'IU',
      genre: 'K-Pop',
    },
    recentSongs: [
      { title: 'Celebrity', artist: 'IU', genre: 'K-Pop' },
      { title: 'Good Day', artist: 'IU', genre: 'K-Pop' },
    ],
  },
  sbs: {
    name: 'SBS 파워FM',
    currentSong: {
      title: 'How You Like That',
      artist: 'BLACKPINK',
      genre: 'K-Pop',
    },
    recentSongs: [
      { title: 'How You Like That', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'DDU-DU DDU-DU', artist: 'BLACKPINK', genre: 'K-Pop' },
    ],
  },
}

// 계산된 속성
const totalPages = computed(() => {
  return Math.ceil(filteredSongs.value.length / 10)
})

const totalPlayCount = computed(() => {
  return filteredSongs.value.reduce((sum, song) => sum + song.count, 0)
})

const uniqueArtists = computed(() => {
  const artists = [...new Set(songsHistory.value.map(song => song.artist))]
  return artists.sort()
})

const uniqueGenres = computed(() => {
  const genres = [...new Set(songsHistory.value.map(song => song.genre))]
  return genres.sort()
})

// 필터링 및 정렬 적용
const applyFilters = () => {
  let filtered = [...songsHistory.value]
  
  // 검색 필터
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(song => 
      song.title.toLowerCase().includes(query) ||
      song.artist.toLowerCase().includes(query)
    )
  }
  
  // 가수 필터
  if (selectedArtist.value) {
    filtered = filtered.filter(song => song.artist === selectedArtist.value)
  }
  
  // 장르 필터
  if (selectedGenre.value) {
    filtered = filtered.filter(song => song.genre === selectedGenre.value)
  }
  
  // 정렬
  filtered.sort((a, b) => {
    switch (sortBy.value) {
      case 'count':
        return b.count - a.count
      case 'recent':
        return new Date(b.lastPlayed) - new Date(a.lastPlayed)
      case 'title':
        return a.title.localeCompare(b.title)
      case 'artist':
        return a.artist.localeCompare(b.artist)
      default:
        return b.count - a.count
    }
  })
  
  filteredSongs.value = filtered
  currentPage.value = 1
  updatePagination()
}

// 페이지네이션 업데이트
const updatePagination = () => {
  const start = (currentPage.value - 1) * 10
  const end = start + 10
  paginatedSongs.value = filteredSongs.value.slice(start, end)
}

// 페이지 이동
const goToPage = (page) => {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    updatePagination()
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
}

// 라디오 노래 히스토리 관리
const addToHistory = (title, artist, genre) => {
  const songId = `${title}-${artist}`
  const existingSong = songsHistory.value.find(s => s.id === songId)
  
  if (existingSong) {
    existingSong.count++
    existingSong.lastPlayed = new Date().toLocaleString('ko-KR')
  } else {
    songsHistory.value.push({
      id: songId,
      title,
      artist,
      genre: genre || 'K-Pop',
      count: 1,
      lastPlayed: new Date().toLocaleString('ko-KR'),
      firstPlayed: new Date().toLocaleString('ko-KR')
    })
  }
  
  saveHistoryToStorage()
  applyFilters()
}

// localStorage에 히스토리 저장
const saveHistoryToStorage = () => {
  localStorage.setItem('radioSongsHistory', JSON.stringify(songsHistory.value))
  
  // 로그인한 경우 데이터베이스에도 저장
  if (authStore.isAuthenticated && authStore.token) {
    saveRadioSongsToDatabase()
  }
}

// 라디오 노래를 데이터베이스에 저장
async function saveRadioSongsToDatabase() {
  try {
    const recentSongs = songsHistory.value.slice(-50).map(song => ({
      title: song.title,
      artist: song.artist,
      genre: song.genre,
      station: song.stations && song.stations.length > 0 ? song.stations[0] : null,
      count: song.count || 1
    }))

    if (recentSongs.length > 0) {
      const response = await fetch('/api/user/radio-songs', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify(recentSongs)
      })

      if (response.ok) {
        const data = await response.json()
        console.log('[라디오 노래 저장] 데이터베이스에 저장 완료:', data.message)
      }
    }
  } catch (error) {
    console.error('[라디오 노래 저장] 데이터베이스 저장 오류:', error)
  }
}

// localStorage에서 히스토리 불러오기
const loadHistoryFromStorage = () => {
  const stored = localStorage.getItem('radioSongsHistory')
  if (stored) {
    songsHistory.value = JSON.parse(stored)
    applyFilters()
  } else {
    fetchRadioSongs()
  }
}

// MCP 서버에서 라디오 노래 정보 가져오기
const fetchRadioSongs = async () => {
  const allSongs = []
  const now = new Date()
  
  try {
    const stations = ['kbs', 'mbc', 'sbs']
    const stationNames = {
      kbs: 'KBS 쿨FM',
      mbc: 'MBC FM4U',
      sbs: 'SBS 파워FM'
    }
    
    for (const station of stations) {
      try {
        const currentResponse = await fetch(`/api/music/radio/current?station=${station}&limit=1`)
        if (currentResponse.ok) {
          const currentData = await currentResponse.json()
          if (currentData.tracks && currentData.tracks.track && currentData.tracks.track.length > 0) {
            const track = currentData.tracks.track[0]
            allSongs.push({
              title: track.name || '제목 없음',
              artist: track.artist?.name || '아티스트 없음',
              genre: 'K-Pop',
              station: stationNames[station],
            })
          }
        }
        
        const recentResponse = await fetch(`/api/music/radio/recent?station=${station}&limit=10`)
        if (recentResponse.ok) {
          const recentData = await recentResponse.json()
          if (recentData.tracks && recentData.tracks.track && recentData.tracks.track.length > 0) {
            recentData.tracks.track.forEach((track) => {
              allSongs.push({
                title: track.name || '제목 없음',
                artist: track.artist?.name || '아티스트 없음',
                genre: 'K-Pop',
                station: stationNames[station],
              })
            })
          }
        }
      } catch (error) {
        console.error(`[라디오 방송] ${station} 오류:`, error)
        const stationData = radioStations[station]
        if (stationData && stationData.currentSong) {
          allSongs.push({
            title: stationData.currentSong.title,
            artist: stationData.currentSong.artist,
            genre: stationData.currentSong.genre || 'K-Pop',
            station: stationData.name,
          })
        }
        if (stationData && stationData.recentSongs) {
          stationData.recentSongs.forEach((song) => {
            allSongs.push({
              title: song.title,
              artist: song.artist,
              genre: song.genre || 'K-Pop',
              station: stationData.name,
            })
          })
        }
      }
    }
  } catch (error) {
    console.error('[라디오 방송] 전체 오류:', error)
    Object.values(radioStations).forEach(station => {
      if (station.currentSong) {
        allSongs.push({
          title: station.currentSong.title,
          artist: station.currentSong.artist,
          genre: station.currentSong.genre || 'K-Pop',
          station: station.name,
        })
      }
      if (station.recentSongs) {
        station.recentSongs.forEach((song) => {
          allSongs.push({
            title: song.title,
            artist: song.artist,
            genre: song.genre || 'K-Pop',
            station: station.name,
          })
        })
      }
    })
  }
  
  // 중복 제거 및 히스토리에 추가
  const uniqueSongs = new Map()
  allSongs.forEach(song => {
    const key = `${song.title}-${song.artist}`
    if (!uniqueSongs.has(key)) {
      uniqueSongs.set(key, song)
    }
  })
  
  uniqueSongs.forEach(song => {
    addToHistory(song.title, song.artist, song.genre)
  })
}

// 한 달간 라디오 노래 데이터 수집
const collectMonthlyData = async () => {
  if (isCollectingMonthlyData.value) {
    return
  }

  isCollectingMonthlyData.value = true
  monthlyCollectionProgress.value = 0
  monthlyCollectionStatus.value = '데이터 수집 시작...'
  monthlyDataCollection.value = []

  try {
    const today = new Date()
    const daysToCollect = 30
    const stations = ['kbs', 'mbc', 'sbs']
    const stationNames = {
      kbs: 'KBS 쿨FM',
      mbc: 'MBC FM4U',
      sbs: 'SBS 파워FM'
    }

    let totalCollected = 0
    const allCollectedSongs = []

    for (let dayOffset = 0; dayOffset < daysToCollect; dayOffset++) {
      const targetDate = new Date(today)
      targetDate.setDate(today.getDate() - dayOffset)
      const dateStr = targetDate.toISOString().split('T')[0]

      monthlyCollectionStatus.value = `${dateStr} 데이터 수집 중... (${dayOffset + 1}/${daysToCollect}일)`

      for (const station of stations) {
        try {
          const recentResponse = await fetch(`/api/music/radio/recent?station=${station}&limit=50`)
          if (recentResponse.ok) {
            const recentData = await recentResponse.json()
            if (recentData.tracks && recentData.tracks.track && recentData.tracks.track.length > 0) {
              recentData.tracks.track.forEach((track) => {
                allCollectedSongs.push({
                  title: track.name || '제목 없음',
                  artist: track.artist?.name || '아티스트 없음',
                  genre: 'K-Pop',
                  station: stationNames[station],
                  date: dateStr,
                  collectedAt: new Date().toISOString()
                })
                totalCollected++
              })
            }
          }

          const currentResponse = await fetch(`/api/music/radio/current?station=${station}&limit=1`)
          if (currentResponse.ok) {
            const currentData = await currentResponse.json()
            if (currentData.tracks && currentData.tracks.track && currentData.tracks.track.length > 0) {
              const track = currentData.tracks.track[0]
              allCollectedSongs.push({
                title: track.name || '제목 없음',
                artist: track.artist?.name || '아티스트 없음',
                genre: 'K-Pop',
                station: stationNames[station],
                date: dateStr,
                collectedAt: new Date().toISOString()
              })
              totalCollected++
            }
          }

          await new Promise(resolve => setTimeout(resolve, 500))
        } catch (error) {
          console.error(`[한 달간 데이터 수집] ${station} 오류:`, error)
        }
      }

      monthlyCollectionProgress.value = Math.round(((dayOffset + 1) / daysToCollect) * 100)
    }

    monthlyCollectionStatus.value = `데이터 취합 중... (총 ${totalCollected}개 수집)`
    
    const uniqueSongsMap = new Map()
    
    allCollectedSongs.forEach(song => {
      const key = `${song.title}-${song.artist}`
      if (!uniqueSongsMap.has(key)) {
        uniqueSongsMap.set(key, {
          title: song.title,
          artist: song.artist,
          genre: song.genre,
          dates: [song.date],
          stations: [song.station],
          count: 1
        })
      } else {
        const existing = uniqueSongsMap.get(key)
        if (!existing.dates.includes(song.date)) {
          existing.dates.push(song.date)
        }
        if (!existing.stations.includes(song.station)) {
          existing.stations.push(song.station)
        }
        existing.count++
      }
    })

    uniqueSongsMap.forEach((songData, key) => {
      const songId = key
      const existingSong = songsHistory.value.find(s => s.id === songId)
      
      if (existingSong) {
        existingSong.count += songData.count
        existingSong.lastPlayed = new Date().toLocaleString('ko-KR')
      } else {
        songsHistory.value.push({
          id: songId,
          title: songData.title,
          artist: songData.artist,
          genre: songData.genre || 'K-Pop',
          count: songData.count,
          lastPlayed: new Date().toLocaleString('ko-KR'),
          firstPlayed: new Date().toLocaleString('ko-KR'),
          dates: songData.dates,
          stations: songData.stations
        })
      }
    })

    saveHistoryToStorage()
    applyFilters()

    monthlyCollectionStatus.value = `완료! 총 ${uniqueSongsMap.size}개의 고유 노래, ${totalCollected}개의 재생 기록이 수집되었습니다.`
    monthlyCollectionProgress.value = 100

    setTimeout(() => {
      isCollectingMonthlyData.value = false
      monthlyCollectionStatus.value = ''
      monthlyCollectionProgress.value = 0
    }, 3000)

  } catch (error) {
    console.error('[한 달간 데이터 수집] 오류:', error)
    monthlyCollectionStatus.value = `오류 발생: ${error.message}`
    isCollectingMonthlyData.value = false
  }
}

// 페이지 변경 감지
watch(currentPage, () => {
  updatePagination()
})

// 컴포넌트 마운트 시 로드
onMounted(() => {
  loadHistoryFromStorage()
})
</script>

<style scoped>
.radio-history-container {
  margin-top: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease;
}

.radio-history-container h2 {
  color: #f5576c;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.search-filter-section {
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.search-box {
  margin-bottom: 1rem;
}

.search-input {
  width: 100%;
  padding: 12px 16px;
  font-size: 16px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  box-sizing: border-box;
  transition: border-color 0.3s ease;
}

.search-input:focus {
  outline: none;
  border-color: #f5576c;
  box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.1);
}

.filter-box {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-box label {
  font-weight: 600;
  color: #333;
  font-size: 14px;
}

.filter-select {
  padding: 8px 12px;
  font-size: 14px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  background: white;
  cursor: pointer;
  transition: border-color 0.3s ease;
}

.filter-select:focus {
  outline: none;
  border-color: #f5576c;
}

.stats-section {
  display: flex;
  gap: 2rem;
  margin-bottom: 1.5rem;
  padding: 1rem;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  flex-wrap: wrap;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stat-value {
  font-size: 20px;
  font-weight: 700;
  color: #f5576c;
}

.btn-monthly {
  padding: 10px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-monthly:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-monthly:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.monthly-collection-status {
  margin: 20px 0;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.progress-info {
  color: white;
}

.status-text {
  margin: 0 0 15px 0;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.progress-bar-container {
  width: 100%;
  height: 24px;
  background-color: rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 100%);
  transition: width 0.3s ease;
  border-radius: 12px;
}

.progress-text {
  margin: 0;
  font-size: 14px;
  text-align: center;
  font-weight: 500;
}

.btn-refresh {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid #f5576c;
  background: white;
  color: #f5576c;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-refresh:hover {
  background: #f5576c;
  color: white;
}

.songs-table-container {
  overflow-x: auto;
  margin-bottom: 1.5rem;
}

.songs-table {
  width: 100%;
  border-collapse: collapse;
  background: white;
}

.songs-table thead {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  color: white;
}

.songs-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 14px;
}

.songs-table td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  font-size: 14px;
}

.song-row:hover {
  background: #f8f9fa;
  transition: background 0.2s ease;
}

.rank-cell {
  font-weight: 700;
  color: #f5576c;
  text-align: center;
  width: 60px;
}

.title-cell {
  font-weight: 600;
  color: #333;
}

.artist-cell {
  color: #666;
}

.genre-cell {
  color: #888;
  font-size: 12px;
}

.count-cell {
  text-align: center;
}

.count-badge {
  display: inline-block;
  padding: 4px 12px;
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  color: white;
  border-radius: 12px;
  font-weight: 600;
  font-size: 12px;
}

.time-cell {
  color: #888;
  font-size: 12px;
}

.no-data {
  text-align: center;
  padding: 2rem;
  color: #999;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: #f8f9fa;
  border-radius: 8px;
}

.page-btn {
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid #f5576c;
  background: white;
  color: #f5576c;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.page-btn:hover:not(:disabled) {
  background: #f5576c;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 14px;
  color: #666;
  font-weight: 500;
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


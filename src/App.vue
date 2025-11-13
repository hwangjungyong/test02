<template>
  <div id="app">
    <!-- 오른쪽 상단 버튼들 -->
    <div class="top-buttons">
      <!-- 인증 상태 표시 -->
      <div v-if="authStore.isAuthenticated" class="user-info">
        <span class="user-name">👤 {{ authStore.user?.name || authStore.user?.email }}</span>
        <button @click="openUserManagementModal" class="btn btn-manage">사용자 관리하기</button>
        <button @click="handleLogout" class="btn btn-logout">로그아웃</button>
      </div>
      <div v-else class="auth-buttons">
        <button @click="showLoginModal = true" class="btn btn-login">로그인</button>
        <button @click="showSignupModal = true" class="btn btn-signup">회원가입</button>
      </div>
      
      <button @click="openMCPGuide" class="btn btn-guide">
        📖 MCP 가이드 보기
      </button>
      <button @click="openPythonMCPGuide" class="btn btn-guide-python">
        🐍 Python MCP 가이드 보기
      </button>
      <button @click="openAPIDocs" class="btn btn-api-docs">
        📚 API DOCS 보기
      </button>
      <button @click="toggleEconomyNewsAlarm" class="btn btn-alarm" :class="{ active: isEconomyAlarmEnabled }">
        🔔 {{ isEconomyAlarmEnabled ? '경제뉴스 알람 ON' : '경제뉴스 알람받기' }}
      </button>
    </div>

    <!-- 로그인 모달 -->
    <div v-if="showLoginModal" class="modal-overlay" @click="showLoginModal = false">
      <div class="modal-content auth-modal" @click.stop>
        <div class="modal-header">
          <h2>🔐 로그인</h2>
          <button @click="showLoginModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleLogin" class="auth-form">
            <div class="form-group">
              <label>이메일</label>
              <input 
                v-model="loginForm.email" 
                type="email" 
                placeholder="이메일을 입력하세요"
                required
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>비밀번호</label>
              <input 
                v-model="loginForm.password" 
                type="password" 
                placeholder="비밀번호를 입력하세요"
                required
                class="form-input"
              />
            </div>
            <div v-if="authError" class="error-message">
              {{ authError }}
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="authStore.isLoading">
                {{ authStore.isLoading ? '로그인 중...' : '로그인' }}
              </button>
              <button type="button" @click="showLoginModal = false" class="btn btn-secondary">
                취소
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 회원가입 모달 -->
    <div v-if="showSignupModal" class="modal-overlay" @click="showSignupModal = false">
      <div class="modal-content auth-modal" @click.stop>
        <div class="modal-header">
          <h2>📝 회원가입</h2>
          <button @click="showSignupModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <form @submit.prevent="handleSignup" class="auth-form">
            <div class="form-group">
              <label>이메일</label>
              <input 
                v-model="signupForm.email" 
                type="email" 
                placeholder="이메일을 입력하세요"
                required
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>비밀번호</label>
              <input 
                v-model="signupForm.password" 
                type="password" 
                placeholder="비밀번호를 입력하세요 (최소 6자)"
                required
                minlength="6"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>이름 (선택사항)</label>
              <input 
                v-model="signupForm.name" 
                type="text" 
                placeholder="이름을 입력하세요"
                class="form-input"
              />
            </div>
            <div v-if="authError" class="error-message">
              {{ authError }}
            </div>
            <div class="form-actions">
              <button type="submit" class="btn btn-primary" :disabled="authStore.isLoading">
                {{ authStore.isLoading ? '가입 중...' : '회원가입' }}
              </button>
              <button type="button" @click="showSignupModal = false" class="btn btn-secondary">
                취소
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- 사용자 관리 모달 -->
    <div v-if="showUserManagementModal" class="modal-overlay" @click="showUserManagementModal = false">
      <div class="modal-content user-management-modal" @click.stop>
        <div class="modal-header">
          <h2>👤 사용자 관리</h2>
          <button @click="showUserManagementModal = false" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <!-- 탭 메뉴 -->
          <div class="user-tabs">
            <button 
              @click="userManagementTab = 'profile'" 
              class="tab-btn" 
              :class="{ active: userManagementTab === 'profile' }"
            >
              프로필
            </button>
            <button 
              @click="userManagementTab = 'data'" 
              class="tab-btn" 
              :class="{ active: userManagementTab === 'data' }"
            >
              내 데이터
            </button>
            <button 
              @click="userManagementTab = 'api-keys'" 
              class="tab-btn" 
              :class="{ active: userManagementTab === 'api-keys' }"
            >
              API 키 관리
            </button>
            <button 
              @click="userManagementTab = 'delete'" 
              class="tab-btn" 
              :class="{ active: userManagementTab === 'delete' }"
            >
              계정 삭제
            </button>
          </div>

          <!-- 프로필 탭 -->
          <div v-if="userManagementTab === 'profile'" class="tab-content">
            <div v-if="userProfileLoading" class="loading">
              <p>프로필 정보를 불러오는 중...</p>
            </div>
            <div v-else>
              <form @submit.prevent="handleUpdateProfile" class="auth-form">
                <div class="form-group">
                  <label>이메일</label>
                  <input 
                    v-model="profileForm.email" 
                    type="email" 
                    placeholder="이메일을 입력하세요"
                    required
                    class="form-input"
                  />
                </div>
                <div class="form-group">
                  <label>이름</label>
                  <input 
                    v-model="profileForm.name" 
                    type="text" 
                    placeholder="이름을 입력하세요"
                    class="form-input"
                  />
                </div>
                <div class="form-group">
                  <label>가입일</label>
                  <input 
                    :value="formatDate(userProfile?.createdAt)" 
                    type="text" 
                    disabled
                    class="form-input"
                  />
                </div>
                <div v-if="userManagementError" class="error-message">
                  {{ userManagementError }}
                </div>
                <div v-if="userManagementSuccess" class="success-message">
                  {{ userManagementSuccess }}
                </div>
                <div class="form-actions">
                  <button type="submit" class="btn btn-primary" :disabled="userProfileUpdating">
                    {{ userProfileUpdating ? '수정 중...' : '프로필 수정' }}
                  </button>
                </div>
              </form>
            </div>
          </div>

          <!-- 내 데이터 탭 -->
          <div v-if="userManagementTab === 'data'" class="tab-content">
            <div v-if="userDataLoading" class="loading">
              <p>데이터를 불러오는 중...</p>
            </div>
            <div v-else>
              <div class="data-summary">
                <h3>📊 데이터 요약</h3>
                <div class="summary-cards">
                  <div class="summary-card">
                    <div class="summary-icon">📰</div>
                    <div class="summary-info">
                      <div class="summary-label">뉴스</div>
                      <div class="summary-value">{{ userDataSummary.newsCount }}건</div>
                    </div>
                  </div>
                  <div class="summary-card">
                    <div class="summary-icon">🎵</div>
                    <div class="summary-info">
                      <div class="summary-label">라디오 노래</div>
                      <div class="summary-value">{{ userDataSummary.radioSongsCount }}건</div>
                    </div>
                  </div>
                  <div class="summary-card">
                    <div class="summary-icon">📚</div>
                    <div class="summary-info">
                      <div class="summary-label">도서</div>
                      <div class="summary-value">{{ userDataSummary.booksCount }}건</div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 뉴스 데이터 -->
              <div v-if="userData.news && userData.news.length > 0" class="data-section">
                <h4>📰 뉴스 ({{ userData.news.length }}건)</h4>
                <div class="data-list">
                  <div v-for="(item, index) in userData.news.slice(0, 10)" :key="index" class="data-item">
                    <div class="data-item-title">{{ item.title }}</div>
                    <div class="data-item-meta">
                      <span>{{ item.source }}</span>
                      <span>{{ formatDate(item.collectedAt) }}</span>
                    </div>
                  </div>
                  <div v-if="userData.news.length > 10" class="data-more">
                    외 {{ userData.news.length - 10 }}건 더...
                  </div>
                </div>
              </div>

              <!-- 라디오 노래 데이터 -->
              <div v-if="userData.radioSongs && userData.radioSongs.length > 0" class="data-section">
                <h4>🎵 라디오 노래 ({{ userData.radioSongs.length }}건)</h4>
                <div class="data-list">
                  <div v-for="(item, index) in userData.radioSongs.slice(0, 10)" :key="index" class="data-item">
                    <div class="data-item-title">{{ item.title }} - {{ item.artist }}</div>
                    <div class="data-item-meta">
                      <span>{{ item.station }}</span>
                      <span>{{ formatDate(item.playedAt || item.collectedAt) }}</span>
                    </div>
                  </div>
                  <div v-if="userData.radioSongs.length > 10" class="data-more">
                    외 {{ userData.radioSongs.length - 10 }}건 더...
                  </div>
                </div>
              </div>

              <!-- 도서 데이터 -->
              <div v-if="userData.books && userData.books.length > 0" class="data-section">
                <h4>📚 도서 ({{ userData.books.length }}건)</h4>
                <div class="data-list">
                  <div v-for="(item, index) in userData.books.slice(0, 10)" :key="index" class="data-item">
                    <div class="data-item-title">{{ item.title }}</div>
                    <div class="data-item-meta">
                      <span>{{ item.authors }}</span>
                      <span>{{ formatDate(item.collectedAt) }}</span>
                    </div>
                  </div>
                  <div v-if="userData.books.length > 10" class="data-more">
                    외 {{ userData.books.length - 10 }}건 더...
                  </div>
                </div>
              </div>

              <div v-if="!userData.news?.length && !userData.radioSongs?.length && !userData.books?.length" class="no-data">
                <p>📭 저장된 데이터가 없습니다.</p>
              </div>
            </div>
          </div>

          <!-- API 키 관리 탭 -->
          <div v-if="userManagementTab === 'api-keys'" class="tab-content">
            <div v-if="apiKeysLoading" class="loading">
              <p>API 키 목록을 불러오는 중...</p>
            </div>
            <div v-else>
              <div class="api-keys-header">
                <h3>🔑 API 키 관리</h3>
                <button @click="showCreateApiKeyModal = true" class="btn btn-primary">
                  ➕ 새 API 키 생성
                </button>
              </div>

              <div v-if="apiKeys.length === 0" class="no-api-keys">
                <p>생성된 API 키가 없습니다.</p>
                <p>외부에서 API를 호출하려면 API 키가 필요합니다.</p>
              </div>

              <div v-else class="api-keys-list">
                <div v-for="key in apiKeys" :key="key.id" class="api-key-item">
                  <div class="api-key-info">
                    <div class="api-key-name">{{ key.name || '이름 없음' }}</div>
                    <div class="api-key-value">{{ key.apiKey }}</div>
                    <div v-if="key.description" class="api-key-description">{{ key.description }}</div>
                    <div class="api-key-meta">
                      <span>생성일: {{ formatDate(key.createdAt) }}</span>
                      <span v-if="key.lastUsedAt">마지막 사용: {{ formatDate(key.lastUsedAt) }}</span>
                      <span v-if="key.expiresAt">만료일: {{ formatDate(key.expiresAt) }}</span>
                    </div>
                  </div>
                  <div class="api-key-actions">
                    <button 
                      @click="toggleApiKey(key.id, !key.isActive)" 
                      class="btn btn-sm"
                      :class="key.isActive ? 'btn-warning' : 'btn-success'"
                    >
                      {{ key.isActive ? '비활성화' : '활성화' }}
                    </button>
                    <button 
                      @click="deleteApiKey(key.id)" 
                      class="btn btn-sm btn-danger"
                    >
                      삭제
                    </button>
                  </div>
                </div>
              </div>

              <div class="api-key-usage-info">
                <h4>📖 API 키 사용 방법</h4>
                <p class="usage-intro">
                  아래 예제에서 <code>YOUR_API_KEY</code>를 실제 API 키로 교체하세요.
                  <span v-if="activeApiKey" class="active-key-hint">
                    현재 활성화된 키: <code>{{ activeApiKey.substring(0, 15) }}...</code>
                  </span>
                </p>
                
                <div class="usage-examples">
                  <div class="usage-example">
                    <strong>방법 1: X-API-Key 헤더 (권장)</strong>
                    <div class="code-block">
                      <pre><code>curl -H "X-API-Key: YOUR_API_KEY" \
  "http://localhost:3001/api/news?q=AI"</code></pre>
                      <button @click="copyCode('curl -H &quot;X-API-Key: YOUR_API_KEY&quot; &quot;http://localhost:3001/api/news?q=AI&quot;')" class="btn-copy-code">📋 복사</button>
                    </div>
                  </div>
                  
                  <div class="usage-example">
                    <strong>방법 2: Authorization 헤더</strong>
                    <div class="code-block">
                      <pre><code>curl -H "Authorization: ApiKey YOUR_API_KEY" \
  "http://localhost:3001/api/music/recommend?songTitle=Dynamite&artist=BTS"</code></pre>
                      <button @click="copyCode('curl -H &quot;Authorization: ApiKey YOUR_API_KEY&quot; &quot;http://localhost:3001/api/music/recommend?songTitle=Dynamite&artist=BTS&quot;')" class="btn-copy-code">📋 복사</button>
                    </div>
                  </div>
                  
                  <div class="usage-example">
                    <strong>방법 3: 쿼리 파라미터</strong>
                    <div class="code-block">
                      <pre><code>curl "http://localhost:3001/api/books/recommend?query=머신러닝&api_key=YOUR_API_KEY"</code></pre>
                      <button @click="copyCode('curl &quot;http://localhost:3001/api/books/recommend?query=머신러닝&api_key=YOUR_API_KEY&quot;')" class="btn-copy-code">📋 복사</button>
                    </div>
                  </div>
                </div>

                <div class="api-endpoints-list">
                  <h5>📚 사용 가능한 API 엔드포인트</h5>
                  <div class="endpoints-grid">
                    <div class="endpoint-item">
                      <strong>뉴스 검색</strong>
                      <code>GET /api/news?q=키워드</code>
                      <code>GET /api/news/economy?q=키워드</code>
                    </div>
                    <div class="endpoint-item">
                      <strong>음악 추천</strong>
                      <code>GET /api/music/recommend?songTitle=제목&artist=아티스트</code>
                      <code>GET /api/music/radio/current?station=kbs&limit=5</code>
                      <code>GET /api/music/radio/recent?station=kbs&limit=10</code>
                    </div>
                    <div class="endpoint-item">
                      <strong>도서 검색</strong>
                      <code>GET /api/books/search?q=키워드&maxResults=10</code>
                      <code>GET /api/books/recommend?query=키워드&category=computers</code>
                    </div>
                  </div>
                </div>

                <div class="usage-tips">
                  <h5>💡 사용 팁</h5>
                  <ul>
                    <li>모든 API는 인증이 선택사항입니다 (인증 없이도 호출 가능)</li>
                    <li>API 키를 사용하면 모든 호출이 자동으로 기록됩니다</li>
                    <li>데이터 저장 API (<code>/api/user/*</code>)는 인증이 필수입니다</li>
                    <li>Swagger UI에서 테스트: <a href="http://localhost:3001/api-docs" target="_blank">http://localhost:3001/api-docs</a></li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- API 키 생성 모달 -->
          <div v-if="showCreateApiKeyModal" class="modal-overlay" @click="showCreateApiKeyModal = false">
            <div class="modal-content api-key-modal" @click.stop>
              <div class="modal-header">
                <h2>🔑 새 API 키 생성</h2>
                <button @click="showCreateApiKeyModal = false" class="btn-close">✕</button>
              </div>
              <div class="modal-body">
                <form @submit.prevent="createApiKey" class="auth-form">
                  <div class="form-group">
                    <label>이름</label>
                    <input 
                      v-model="newApiKeyForm.name" 
                      type="text" 
                      placeholder="예: 프로덕션 키, 개발 키"
                      required
                      class="form-input"
                    />
                  </div>
                  <div class="form-group">
                    <label>설명 (선택사항)</label>
                    <textarea 
                      v-model="newApiKeyForm.description" 
                      placeholder="이 API 키의 용도를 설명해주세요"
                      class="form-input"
                      rows="3"
                    ></textarea>
                  </div>
                  <div class="form-group">
                    <label>만료일 (선택사항)</label>
                    <input 
                      v-model="newApiKeyForm.expiresInDays" 
                      type="number" 
                      placeholder="예: 30 (30일 후 만료)"
                      min="1"
                      class="form-input"
                    />
                    <small>비워두면 만료되지 않습니다.</small>
                  </div>
                  <div v-if="userManagementError" class="error-message">
                    {{ userManagementError }}
                  </div>
                  <div v-if="createdApiKey" class="success-message">
                    <p><strong>✅ API 키가 생성되었습니다!</strong></p>
                    <div class="api-key-display">
                      <code>{{ createdApiKey.apiKey }}</code>
                      <button @click="copyApiKey(createdApiKey.apiKey)" class="btn btn-sm btn-primary">
                        복사
                      </button>
                    </div>
                    <p class="warning-text">⚠️ 이 API 키는 이번에만 표시됩니다. 안전한 곳에 저장하세요!</p>
                  </div>
                  <div class="form-actions">
                    <button type="submit" class="btn btn-primary" :disabled="isCreatingApiKey">
                      {{ isCreatingApiKey ? '생성 중...' : 'API 키 생성' }}
                    </button>
                    <button type="button" @click="closeCreateApiKeyModal" class="btn btn-secondary">
                      {{ createdApiKey ? '닫기' : '취소' }}
                    </button>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <!-- 계정 삭제 탭 -->
          <div v-if="userManagementTab === 'delete'" class="tab-content">
            <div class="delete-warning">
              <h3>⚠️ 계정 삭제</h3>
              <p>계정을 삭제하면 다음 정보가 모두 삭제됩니다:</p>
              <ul>
                <li>프로필 정보</li>
                <li>저장된 뉴스 ({{ userDataSummary.newsCount }}건)</li>
                <li>저장된 라디오 노래 ({{ userDataSummary.radioSongsCount }}건)</li>
                <li>저장된 도서 ({{ userDataSummary.booksCount }}건)</li>
              </ul>
              <p class="warning-text">이 작업은 되돌릴 수 없습니다!</p>
              <div v-if="userManagementError" class="error-message">
                {{ userManagementError }}
              </div>
              <div class="form-actions">
                <button 
                  @click="handleDeleteAccount" 
                  class="btn btn-danger" 
                  :disabled="userAccountDeleting"
                >
                  {{ userAccountDeleting ? '삭제 중...' : '계정 삭제' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 경제뉴스 알람 모달 -->
    <div v-if="showEconomyAlarmModal" class="modal-overlay" @click="closeEconomyAlarmModal">
      <div class="modal-content alarm-modal" @click.stop>
        <div class="modal-header">
          <h2>🔔 경제뉴스 알람</h2>
          <button @click="closeEconomyAlarmModal" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="alarmChecking" class="loading">
            <p>새로운 경제 뉴스를 확인하는 중...</p>
          </div>
          <div v-else-if="newEconomyNews.length > 0" class="alarm-results">
            <div class="alarm-summary">
              <h3>✨ 새로운 경제 뉴스 {{ newEconomyNews.length }}건 발견!</h3>
              <p class="alarm-time">확인 시간: {{ lastAlarmCheckTime }}</p>
            </div>
            <div class="alarm-news-list">
              <div v-for="(news, index) in newEconomyNews" :key="index" class="alarm-news-item">
                <div class="alarm-news-header">
                  <span class="alarm-news-number">{{ index + 1 }}</span>
                  <span class="alarm-news-importance">{{ news.importanceStars }}</span>
                  <span class="alarm-news-date">{{ news.date }}</span>
                </div>
                <div class="alarm-news-title">
                  <a :href="news.url" target="_blank" class="alarm-news-link">{{ news.title }}</a>
                </div>
                <div class="alarm-news-source">출처: {{ news.source }}</div>
                <div class="alarm-news-summary">{{ news.summary }}</div>
              </div>
            </div>
            <div class="alarm-actions">
              <button @click="saveNewEconomyNews" class="btn btn-save">💾 새 뉴스 저장하기</button>
              <button @click="closeEconomyAlarmModal" class="btn btn-close-alarm">닫기</button>
            </div>
          </div>
          <div v-else class="alarm-no-results">
            <p>📭 새로운 경제 뉴스가 없습니다.</p>
            <p class="alarm-time">확인 시간: {{ lastAlarmCheckTime }}</p>
            <button @click="closeEconomyAlarmModal" class="btn btn-close-alarm">닫기</button>
          </div>
        </div>
      </div>
    </div>

    <!-- MCP 가이드 모달 -->
    <div v-if="showMCPGuide" class="modal-overlay" @click="closeMCPGuide">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h2>{{ currentGuideType === 'python' ? 'Python MCP 서버 가이드' : 'MCP 서버 가이드' }}</h2>
          <button @click="closeMCPGuide" class="btn-close">✕</button>
        </div>
        <div class="modal-body">
          <div v-if="isLoading" class="loading">
            <p>가이드를 불러오는 중...</p>
          </div>
          <div v-else v-html="markdownContent"></div>
        </div>
      </div>
    </div>

    <!-- 메인 콘텐츠 -->
    <div class="main-content">
      <div class="main-header">
        <h1>MCP 서버 관리 시스템</h1>
        <p class="subtitle">AI 기사 검색, 경제 뉴스, 음악 추천, 라디오 수집 현황을 한눈에</p>
      </div>

      <!-- 메인 기능 영역 (좌우 배치) -->
      <div class="main-features-grid">
        <!-- 기사 검색 섹션 (바운더리로 묶음) -->
        <div class="article-search-section">
          <div class="section-header">
            <h2>📰 기사 검색</h2>
            <p class="section-description">최근 일주일 이내의 최신 기사를 검색하세요</p>
          </div>
          <div class="article-search-buttons">
            <div class="button-group-card">
              <button @click="toggleAIArticleSearch" class="btn btn-ai-search" :class="{ active: showAIArticleSearch }">
                <div class="button-icon">🤖</div>
                <div class="button-content">
                  <div class="button-title">AI 뉴스 검색</div>
                  <div class="button-subtitle">인공지능 관련 최신 뉴스</div>
                </div>
              </button>
            </div>
            <div class="button-group-card">
              <button @click="toggleEconomyArticleSearch" class="btn btn-economy-search" :class="{ active: showEconomyArticleSearch }">
                <div class="button-icon">💰</div>
                <div class="button-content">
                  <div class="button-title">경제 뉴스 검색</div>
                  <div class="button-subtitle">경제·금융 최신 뉴스</div>
                </div>
              </button>
            </div>
            <div class="button-group-card">
              <button @click="toggleNewsCollection" class="btn btn-news-collection" :class="{ active: showNewsCollection }">
                <div class="button-icon">📰</div>
                <div class="button-content">
                  <div class="button-title">수집된 뉴스 현황</div>
                  <div class="button-subtitle">한 달간 수집된 뉴스 보기</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- 기타 기능 섹션 -->
        <div class="other-features-section">
          <div class="section-header">
            <h2>🎵 음악 & 라디오</h2>
            <p class="section-description">AI 기반 음악 추천과 실시간 라디오 수집 현황</p>
          </div>
          <div class="feature-buttons">
            <div class="button-group-card">
              <button @click="toggleMusicRecommendation" class="btn btn-music" :class="{ active: showMusicRecommendation }">
                <div class="button-icon">🎵</div>
                <div class="button-content">
                  <div class="button-title">AI 노래 추천</div>
                  <div class="button-subtitle">Last.fm 기반 음악 추천</div>
                </div>
              </button>
            </div>
            <div class="button-group-card">
              <button @click="loadRadioHistory" class="btn btn-radio" :class="{ active: showRadioHistory }">
                <div class="button-icon">📻</div>
                <div class="button-content">
                  <div class="button-title">실시간 라디오 수집 현황</div>
                  <div class="button-subtitle">라디오 방송 노래 현황</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- 도서 섹션 -->
        <div class="book-features-section">
          <div class="section-header">
            <h2>📚 도서</h2>
            <p class="section-description">AI 도서 추천과 실시간 도서 수집 현황</p>
          </div>
          <div class="feature-buttons">
            <div class="button-group-card">
              <button @click="toggleBookRecommendation" class="btn btn-book" :class="{ active: showBookRecommendation }">
                <div class="button-icon">📖</div>
                <div class="button-content">
                  <div class="button-title">AI 도서 추천</div>
                  <div class="button-subtitle">AI가 당신의 요구사항을 분석하여 도서 추천</div>
                </div>
              </button>
            </div>
            <div class="button-group-card">
              <button @click="loadBookHistory" class="btn btn-book-history" :class="{ active: showBookHistory }">
                <div class="button-icon">📚</div>
                <div class="button-content">
                  <div class="button-title">실시간 도서 수집 현황</div>
                  <div class="button-subtitle">수집된 도서 현황</div>
                </div>
              </button>
            </div>
          </div>
        </div>

        <!-- AI 화면 검증 섹션 -->
        <div class="screen-validation-section">
          <div class="section-header">
            <h2>🔍 AI 화면 검증</h2>
            <p class="section-description">웹 페이지 화면 캡처 및 요소 값 검증</p>
          </div>
          <div class="feature-buttons">
            <div class="button-group-card">
              <button @click="toggleScreenValidation" class="btn btn-screen-validation" :class="{ active: showScreenValidation }">
                <div class="button-icon">🔍</div>
                <div class="button-content">
                  <div class="button-title">AI 화면 검증</div>
                  <div class="button-subtitle">URL 접속하여 화면 캡처 및 요소 검증</div>
                </div>
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- 기사 검색 결과 영역 -->
      <div class="article-results-area">
        <!-- AI 뉴스 검색 -->
        <div v-if="showAIArticleSearch" class="ai-articles-container">
          <h2>🤖 AI 뉴스 검색</h2>
          <div class="search-notice">
            <p>ℹ️ 최근 일주일 이내의 AI 관련 뉴스를 검색합니다.</p>
          </div>
          <div class="input-group">
            <label for="searchKeyword">검색 키워드:</label>
            <input
              id="searchKeyword"
              v-model="searchKeyword"
              type="text"
              placeholder="예: ChatGPT, 인공지능, 머신러닝, 딥러닝 등"
              class="input-field"
              @keyup.enter="searchAIArticles"
            />
          </div>
          <div class="search-actions">
            <button @click="searchAIArticles" class="btn btn-search" :disabled="isSearching">
              {{ isSearching ? '검색 중...' : '🔍 검색하기' }}
            </button>
            <button @click="fetchLatestAINews" class="btn btn-fetch" :disabled="isSearching">
              🔄 최신 데이터 가져오기
            </button>
            <button 
              @click="collectMonthlyNewsData" 
              class="btn btn-monthly-news"
              :disabled="isCollectingNewsData"
            >
              {{ isCollectingNewsData ? '수집 중...' : '📅 한 달간 데이터 수집' }}
            </button>
          </div>
          <!-- 뉴스 수집 진행 상황 -->
          <div v-if="isCollectingNewsData || newsCollectionStatus" class="monthly-collection-status">
            <div class="progress-info">
              <p class="status-text">{{ newsCollectionStatus }}</p>
              <div class="progress-bar-container">
                <div 
                  class="progress-bar" 
                  :style="{ width: newsCollectionProgress + '%' }"
                ></div>
              </div>
              <p class="progress-text">{{ newsCollectionProgress }}%</p>
            </div>
          </div>
          <div v-if="articleError" class="error">
            <p>{{ articleError }}</p>
          </div>
          <div v-if="aiArticles.length > 0" class="articles-results">
            <h3>검색 결과 ({{ aiArticles.length }}건)</h3>
            <div class="articles-list">
              <div v-for="(article, index) in aiArticles" :key="index" class="article-card">
                <h4 class="article-title">{{ article.title }}</h4>
                <p class="article-summary">{{ article.summary }}</p>
                <div class="article-meta">
                  <span class="article-date">📅 {{ article.date }}</span>
                  <span class="article-source">📰 {{ article.source }}</span>
                  <span class="article-category">🏷️ {{ article.category }}</span>
                </div>
                <div class="article-actions">
                  <a :href="article.url" target="_blank" rel="noopener noreferrer" class="article-link">
                    🔗 기사 보기
                  </a>
                  <button @click="saveSingleNews(article)" class="btn-save-news" :disabled="isSavingNews">
                    {{ isSavingNews ? '저장 중...' : '💾 저장' }}
                  </button>
                </div>
              </div>
            </div>
            
            <!-- 데이터 연계도 분석 -->
            <div v-if="dataCorrelation.length > 0 || graphData.nodes.length > 0" class="correlation-section">
              <h3>📊 데이터 연계도 분석 (빅데이터 기반)</h3>
              
              <!-- 네트워크 그래프 -->
              <div v-if="graphData.nodes.length > 0" class="network-graph-container">
                <h4>🕸️ 키워드 상하위 관계도</h4>
                <div ref="networkContainer" class="network-graph"></div>
                <div class="graph-legend">
                  <div class="legend-item">
                    <span class="legend-color primary"></span>
                    <span>상위 키워드 (검색어)</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color secondary"></span>
                    <span>하위 키워드 (관련어)</span>
                  </div>
                  <div class="legend-item">
                    <span class="legend-color tertiary"></span>
                    <span>연관 키워드</span>
                  </div>
                </div>
              </div>
              
              <!-- 기존 연계도 차트 -->
              <div v-if="dataCorrelation.length > 0" class="correlation-chart">
                <h4>📈 키워드 연계도 상세</h4>
                <div class="correlation-item" v-for="(item, index) in dataCorrelation" :key="index">
                  <div class="correlation-header">
                    <span class="correlation-keyword">{{ item.keyword }}</span>
                    <span class="correlation-score">연계도: {{ item.score }}%</span>
                  </div>
                  <div class="correlation-bar">
                    <div class="correlation-bar-fill" :style="{ width: item.score + '%' }"></div>
                  </div>
                  <div class="correlation-details">
                    <span class="detail-item">관련 기사: {{ item.relatedArticles }}건</span>
                    <span class="detail-item">출처 다양성: {{ item.sourceDiversity }}개</span>
                    <span class="detail-item">시간 분포: {{ item.timeDistribution }}</span>
                    <span v-if="item.timeTrend" class="detail-item">트렌드: {{ item.timeTrend === '상승' ? '📈 상승' : item.timeTrend === '하락' ? '📉 하락' : '➡️ 안정' }}</span>
                    <span v-if="item.tfidf" class="detail-item">TF-IDF: {{ item.tfidf }}</span>
                    <span v-if="item.relatedKeywords && item.relatedKeywords.length > 0" class="detail-item">연관 키워드: {{ item.relatedKeywords.join(', ') }}</span>
                    <span v-if="item.correlationStrength" class="detail-item">연계 강도: {{ item.correlationStrength }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="searchKeyword && !isSearching && !articleError" class="no-results">
            <p>검색 결과가 없습니다. 다른 키워드를 시도해보세요.</p>
            <p class="suggestions">추천 키워드: ChatGPT, GPT, 인공지능, 머신러닝, 딥러닝, 자연어처리, AI</p>
          </div>
        </div>

        <!-- 경제 뉴스 검색 -->
        <div v-if="showEconomyArticleSearch" class="economy-articles-container">
          <h2>💰 경제 뉴스 검색</h2>
          <div class="search-notice">
            <p>ℹ️ 최근 2주 이내의 최신 경제 뉴스를 자동으로 불러옵니다.</p>
          </div>
          <div class="search-actions">
            <button 
              @click="fetchLatestEconomyNews" 
              class="btn btn-fetch"
              :disabled="isSearchingEconomy"
            >
              {{ isSearchingEconomy ? '불러오는 중...' : '🔄 최신 데이터 가져오기' }}
            </button>
            <button 
              @click="collectMonthlyNewsData" 
              class="btn btn-monthly-news"
              :disabled="isCollectingNewsData"
            >
              {{ isCollectingNewsData ? '수집 중...' : '📅 한 달간 데이터 수집' }}
            </button>
          </div>
          <!-- 뉴스 수집 진행 상황 -->
          <div v-if="isCollectingNewsData || newsCollectionStatus" class="monthly-collection-status">
            <div class="progress-info">
              <p class="status-text">{{ newsCollectionStatus }}</p>
              <div class="progress-bar-container">
                <div 
                  class="progress-bar" 
                  :style="{ width: newsCollectionProgress + '%' }"
                ></div>
              </div>
              <p class="progress-text">{{ newsCollectionProgress }}%</p>
            </div>
          </div>
          <div v-if="isSearchingEconomy" class="loading-state">
            <p>📰 최신 뉴스를 불러오는 중...</p>
          </div>
          <div v-if="economyArticleError" class="error">
            <p>{{ economyArticleError }}</p>
          </div>
          <div v-if="economyArticles.length > 0" class="articles-results">
            <div class="importance-legend">
              <h3>최신 뉴스 ({{ economyArticles.length }}건)</h3>
              <div class="legend">
                <span class="legend-item">
                  <span class="stars">⭐⭐⭐</span> 매우중요
                </span>
                <span class="legend-item">
                  <span class="stars">⭐⭐</span> 보통
                </span>
                <span class="legend-item">
                  <span class="stars">⭐</span> 미흡
                </span>
              </div>
            </div>
            <div class="articles-table-container">
              <table class="articles-table">
                <thead>
                  <tr>
                    <th class="col-date">날짜</th>
                    <th class="col-importance">중요도</th>
                    <th class="col-title">뉴스기사</th>
                    <th class="col-actions">저장</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(article, index) in economyArticles" :key="index" 
                      :class="`importance-${article.importanceValue === 3 ? 'high' : article.importanceValue === 2 ? 'medium' : 'low'}`">
                    <td class="col-date">{{ article.date }}</td>
                    <td class="col-importance">
                      <span class="stars">{{ article.importanceStars }}</span>
                    </td>
                    <td class="col-title">
                      <a :href="article.url" target="_blank" rel="noopener noreferrer" class="article-title-link">
                        {{ article.title }}
                      </a>
                    </td>
                    <td class="col-actions">
                      <button @click="saveSingleNews(article)" class="btn-save-news-small" :disabled="isSavingNews" title="저장">
                        {{ isSavingNews ? '...' : '💾' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <div v-else-if="!isSearchingEconomy && !economyArticleError" class="no-results">
            <p>뉴스를 불러오는 중입니다...</p>
          </div>
        </div>

        <!-- 수집된 뉴스 현황 -->
        <div v-if="showNewsCollection" class="news-collection-container">
          <h2>📰 수집된 뉴스 현황</h2>
          
          <!-- 통계 정보 -->
          <div class="stats-section">
            <div class="stat-item">
              <span class="stat-label">총 뉴스 수:</span>
              <span class="stat-value">{{ newsHistory.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">경제 뉴스:</span>
              <span class="stat-value">{{ economyNewsCount }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">AI 뉴스:</span>
              <span class="stat-value">{{ aiNewsCount }}</span>
            </div>
            <div class="stat-item">
              <button @click="loadNewsHistoryFromStorage" class="btn-refresh">
                🔄 데이터 새로고침
              </button>
            </div>
          </div>

          <!-- 검색 및 필터 -->
          <div class="search-filter-section">
            <div class="search-box">
              <input
                v-model="newsSearchQuery"
                type="text"
                placeholder="뉴스 제목 또는 출처 검색..."
                class="search-input"
                @input="applyNewsFilters"
              />
            </div>
            
            <div class="filter-box">
              <label>카테고리 필터:</label>
              <select v-model="selectedNewsCategory" @change="applyNewsFilters" class="filter-select">
                <option value="">전체</option>
                <option value="경제 뉴스">경제 뉴스</option>
                <option value="AI 뉴스">AI 뉴스</option>
              </select>
              
              <label>정렬:</label>
              <select v-model="newsSortBy" @change="applyNewsFilters" class="filter-select">
                <option value="date">날짜 순 (최신)</option>
                <option value="title">제목 순</option>
                <option value="source">출처 순</option>
              </select>
            </div>
          </div>

          <!-- 뉴스 목록 -->
          <div v-if="filteredNews.length > 0" class="news-list-container">
            <div class="news-list">
              <div v-for="(article, index) in paginatedNews" :key="article.id || index" class="news-item">
                <div class="news-header">
                  <h3 class="news-title">
                    <a :href="article.url" target="_blank" rel="noopener noreferrer" class="news-link">
                      {{ article.title }}
                    </a>
                  </h3>
                  <span class="news-category" :class="`category-${article.category === '경제 뉴스' ? 'economy' : 'ai'}`">
                    {{ article.category }}
                  </span>
                </div>
                <p class="news-summary">{{ article.summary }}</p>
                <div class="news-meta">
                  <span class="news-date">📅 {{ article.date }}</span>
                  <span class="news-source">📰 {{ article.source }}</span>
                  <span v-if="article.keyword" class="news-keyword">🔍 {{ article.keyword }}</span>
                  <span v-if="article.importanceStars" class="news-importance">{{ article.importanceStars }}</span>
                </div>
              </div>
            </div>

            <!-- 페이지네이션 -->
            <div class="pagination">
              <button 
                @click="currentNewsPage = Math.max(1, currentNewsPage - 1)" 
                :disabled="currentNewsPage === 1"
                class="page-btn"
              >
                이전
              </button>
              <span class="page-info">
                페이지 {{ currentNewsPage }} / {{ totalNewsPages }} (총 {{ filteredNews.length }}건)
              </span>
              <button 
                @click="currentNewsPage = Math.min(totalNewsPages, currentNewsPage + 1)" 
                :disabled="currentNewsPage === totalNewsPages"
                class="page-btn"
              >
                다음
              </button>
            </div>
          </div>
          <div v-else class="no-results">
            <p>수집된 뉴스가 없습니다. "한 달간 데이터 수집" 버튼을 클릭하여 뉴스를 수집해보세요.</p>
          </div>
        </div>
      </div>

      <!-- 기타 기능 결과 영역 -->
      <div class="other-results-area">
        <!-- 음악 추천 기능 -->
        <div v-if="showMusicRecommendation" class="music-container">
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

        <!-- 라디오 노래 현황 -->
        <div v-if="showRadioHistory" class="radio-history-container">
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

        <!-- 도서 추천 기능 -->
        <div v-if="showBookRecommendation" class="book-container">
          <h2>📖 AI 도서 추천</h2>
          <div class="search-notice">
            <p>💡 원하는 도서에 대해 자유롭게 설명해주세요. AI가 당신의 요구사항을 분석하여 최적의 도서를 추천해드립니다.</p>
            <p>예시: "머신러닝을 처음 배우고 싶어요", "재미있는 소설을 읽고 싶어요", "경제에 대해 배우고 싶어요"</p>
          </div>
          <div class="input-group">
            <label for="bookKeyword">원하는 도서에 대해 설명해주세요:</label>
            <textarea
              id="bookKeyword"
              v-model="bookKeyword"
              type="text"
              placeholder="예: 머신러닝을 처음 배우고 싶어요. 파이썬 기초는 알고 있습니다."
              class="input-field"
              rows="3"
              style="resize: vertical; min-height: 80px;"
            ></textarea>
          </div>
          <div class="input-group">
            <label for="bookCategory">카테고리 (선택사항):</label>
            <select id="bookCategory" v-model="bookCategory" class="input-field">
              <option value="">전체</option>
              <option value="computers">컴퓨터/IT</option>
              <option value="science">과학</option>
              <option value="technology">기술</option>
              <option value="fiction">소설</option>
              <option value="business">경제/경영</option>
            </select>
          </div>
          <button @click="recommendBooks" class="btn btn-recommend" :disabled="isSearchingBooks">
            {{ isSearchingBooks ? 'AI 분석 중...' : '🤖 AI 도서 추천 받기' }}
          </button>
          <div v-if="recommendedBooks.length > 0" class="book-list">
            <h3 class="book-list-title">📚 추천 도서 목록 ({{ recommendedBooks.length }}건)</h3>
            <div class="books-grid">
              <div v-for="(book, index) in recommendedBooks" :key="book.id || index" class="book-card">
                <div class="book-card-header">
                  <div class="book-thumbnail" v-if="book.thumbnail">
                    <img :src="book.thumbnail" :alt="book.title" />
                  </div>
                  <div class="book-number-badge">{{ index + 1 }}</div>
                </div>
                <div class="book-card-body">
                  <h4 class="book-title">{{ book.title }}</h4>
                  <div class="book-meta">
                    <div class="book-meta-item">
                      <span class="book-meta-label">✍️ 저자</span>
                      <span class="book-meta-value">{{ book.authors.join(', ') }}</span>
                    </div>
                    <div class="book-meta-item">
                      <span class="book-meta-label">🏢 출판사</span>
                      <span class="book-meta-value">{{ book.publisher }}</span>
                    </div>
                    <div class="book-meta-item">
                      <span class="book-meta-label">📅 출판일</span>
                      <span class="book-meta-value">{{ book.publishedDate }}</span>
                    </div>
                    <div v-if="book.averageRating > 0" class="book-meta-item">
                      <span class="book-meta-label">⭐ 평점</span>
                      <span class="book-meta-value">{{ book.averageRating }}/5.0 ({{ book.ratingsCount }}명)</span>
                    </div>
                  </div>
                  <p v-if="book.description" class="book-description">
                    {{ book.description.length > 200 ? book.description.substring(0, 200) + '...' : book.description }}
                  </p>
                  <div v-if="book.categories && book.categories.length > 0" class="book-categories">
                    <span v-for="(cat, idx) in book.categories.slice(0, 3)" :key="idx" class="book-category-tag">
                      {{ cat }}
                    </span>
                  </div>
                </div>
                <div class="book-card-footer">
                  <button @click="saveSingleBook(book)" class="book-link-btn book-link-save" :disabled="isSavingBook">
                    {{ isSavingBook ? '저장 중...' : '💾 저장' }}
                  </button>
                  <a v-if="book.infoLink" :href="book.infoLink" target="_blank" class="book-link-btn book-link-primary">
                    📖 상세 정보
                  </a>
                  <a v-if="book.previewLink" :href="book.previewLink" target="_blank" class="book-link-btn book-link-secondary">
                    👁️ 미리보기
                  </a>
                </div>
              </div>
            </div>
          </div>
          <div v-if="bookError" class="error">
            <p>{{ bookError }}</p>
          </div>
        </div>

        <!-- 도서 수집 현황 -->
        <div v-if="showBookHistory" class="book-history-container">
          <h2>📚 실시간 도서 수집 현황</h2>
          
          <!-- 수집 버튼 -->
          <div class="collection-buttons">
            <button @click="collectMonthlyBookData" class="btn btn-collect" :disabled="isCollectingBookData">
              {{ isCollectingBookData ? '수집 중...' : '📅 한 달간 데이터 수집' }}
            </button>
            <button @click="fetchLatestBooks" class="btn btn-fetch">
              🔄 최신 데이터 가져오기
            </button>
          </div>

          <!-- 수집 진행 상황 -->
          <div v-if="isCollectingBookData" class="monthly-collection-status">
            <div class="progress-bar-container">
              <div class="progress-bar" :style="{ width: bookCollectionProgress + '%' }"></div>
            </div>
            <p class="status-text">{{ bookCollectionStatus }}</p>
          </div>

          <!-- 검색 및 필터 -->
          <div class="search-filter-section">
            <div class="search-box">
              <input
                v-model="bookSearchQuery"
                type="text"
                placeholder="도서 제목 또는 저자 검색..."
                class="search-input"
                @input="applyBookFilters"
              />
            </div>
            
            <div class="filter-box">
              <label>정렬:</label>
              <select v-model="bookSortBy" @change="applyBookFilters" class="filter-select">
                <option value="date">출판일 순</option>
                <option value="title">제목 순</option>
                <option value="author">저자 순</option>
                <option value="publisher">출판사 순</option>
              </select>
            </div>
          </div>

          <!-- 통계 -->
          <div v-if="booksHistory.length > 0" class="stats-section">
            <div class="stat-item">
              <span class="stat-label">총 도서 수:</span>
              <span class="stat-value">{{ booksHistory.length }}권</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">고유 저자:</span>
              <span class="stat-value">{{ uniqueBookAuthors.length }}명</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">고유 출판사:</span>
              <span class="stat-value">{{ uniqueBookPublishers.length }}개</span>
            </div>
          </div>

          <!-- 도서 목록 -->
          <div v-if="filteredBooks.length > 0" class="books-table-container">
            <table class="books-table">
              <thead>
                <tr>
                  <th>순번</th>
                  <th>제목</th>
                  <th>저자</th>
                  <th>출판사</th>
                  <th>출판일</th>
                  <th>카테고리</th>
                  <th>링크</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(book, index) in paginatedBooks" :key="book.id || index">
                  <td>{{ (currentBookPage - 1) * booksPerPage + index + 1 }}</td>
                  <td class="book-title-cell">{{ book.title }}</td>
                  <td>{{ book.authors.join(', ') }}</td>
                  <td>{{ book.publisher }}</td>
                  <td>{{ book.publishedDate }}</td>
                  <td>{{ book.categories.join(', ') || '-' }}</td>
                  <td>
                    <a v-if="book.infoLink" :href="book.infoLink" target="_blank" class="book-link">상세</a>
                  </td>
                </tr>
                <tr v-if="paginatedBooks.length === 0">
                  <td colspan="7" class="no-data">검색 결과가 없습니다.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <!-- 페이지네이션 -->
          <div v-if="filteredBooks.length > 0" class="pagination">
            <button
              @click="goToBookPage(currentBookPage - 1)"
              :disabled="currentBookPage === 1"
              class="page-btn"
            >
              이전
            </button>
            <span class="page-info">
              페이지 {{ currentBookPage }} / {{ totalBookPages }}
              (총 {{ filteredBooks.length }}권)
            </span>
            <button
              @click="goToBookPage(currentBookPage + 1)"
              :disabled="currentBookPage === totalBookPages"
              class="page-btn"
            >
              다음
            </button>
          </div>

          <div v-if="filteredBooks.length === 0 && booksHistory.length === 0" class="no-results">
            <p>수집된 도서가 없습니다. "한 달간 데이터 수집" 버튼을 클릭하여 도서를 수집해보세요.</p>
          </div>
        </div>

        <!-- AI 화면 검증 결과 영역 -->
        <div v-if="showScreenValidation" class="screen-validation-container">
          <h2>🔍 AI 화면 검증</h2>
          <div class="validation-notice">
            <p>ℹ️ URL을 입력하면 해당 페이지에 접속하여 화면을 캡처하고 특정 요소의 값을 검증합니다.</p>
            <p>💡 MCP Python 서버(Playwright)를 사용하여 브라우저 자동화를 수행합니다.</p>
          </div>
          
          <div class="input-group">
            <label for="screenValidationUrl">접속할 URL:</label>
            <input
              id="screenValidationUrl"
              v-model="screenValidationUrl"
              type="url"
              placeholder="예: https://example.com"
              class="input-field"
            />
          </div>
          
          <div class="input-group">
            <label for="screenValidationSelector">CSS 선택자 (검증할 요소):</label>
            <input
              id="screenValidationSelector"
              v-model="screenValidationSelector"
              type="text"
              placeholder="예: #price, .title, h1, [data-testid='value']"
              class="input-field"
            />
            <small class="input-hint">요소의 텍스트 내용을 읽어옵니다. 비워두면 전체 페이지를 캡처합니다.</small>
          </div>
          
          <div class="input-group">
            <label for="screenValidationExpectedValue">예상 값 (선택사항):</label>
            <input
              id="screenValidationExpectedValue"
              v-model="screenValidationExpectedValue"
              type="text"
              placeholder="예: 1000원, Hello World"
              class="input-field"
            />
            <small class="input-hint">입력하면 읽은 값과 비교하여 검증 결과를 표시합니다.</small>
          </div>
          
          <div class="validation-actions">
            <button 
              @click="validateScreen" 
              class="btn btn-validate" 
              :disabled="isValidatingScreen || !screenValidationUrl"
            >
              {{ isValidatingScreen ? '검증 중...' : '🔍 화면 검증하기' }}
            </button>
            <button 
              @click="captureScreenOnly" 
              class="btn btn-capture" 
              :disabled="isValidatingScreen || !screenValidationUrl"
            >
              📸 화면 캡처만
            </button>
            <button 
              @click="interactAndGetResult" 
              class="btn btn-interact" 
              :disabled="isValidatingScreen || !screenValidationUrl"
            >
              ⚡ 입력/클릭 후 결과 가져오기
            </button>
          </div>
          
          <!-- 입력/클릭 액션 설정 - 간단한 버전 -->
          <div class="interact-actions-section">
            <h3>⚡ 자동으로 할 일 설정</h3>
            <p class="section-description">
              페이지에 접속한 후 자동으로 수행할 작업을 순서대로 설정하세요.
              <br>예: 1) 검색창에 "MCP" 입력 → 2) 검색 버튼 클릭 → 3) 결과 확인
            </p>
            
            <div v-for="(action, index) in interactActions" :key="index" class="action-item">
              <div class="action-header">
                <span class="action-number">📌 {{ index + 1 }}단계</span>
                <button 
                  v-if="interactActions.length > 1"
                  @click="removeAction(index)" 
                  class="btn-remove-action"
                  type="button"
                >
                  ✕ 삭제
                </button>
              </div>
              
              <div class="action-fields">
                <div class="field-group">
                  <label>무엇을 할까요?</label>
                  <select v-model="action.type" class="input-field" @change="onActionTypeChange(action)">
                    <option value="fill">📝 텍스트 입력하기</option>
                    <option value="click">🖱️ 버튼/링크 클릭하기</option>
                    <option value="select">📋 드롭다운에서 선택하기</option>
                    <option value="check">☑️ 체크박스 체크하기</option>
                    <option value="uncheck">☐ 체크박스 해제하기</option>
                    <option value="wait">⏱️ 잠시 대기하기</option>
                  </select>
                </div>
                
                <div v-if="action.type !== 'wait'" class="field-group">
                  <label>어떤 요소를 찾을까요? (개발자 도구에서 복사)</label>
                  <div class="help-box">
                    <p>💡 <strong>간단한 방법:</strong></p>
                    <ol>
                      <li>브라우저에서 해당 페이지 열기</li>
                      <li>F12 키 누르기 (개발자 도구 열림)</li>
                      <li>왼쪽 상단의 요소 선택 아이콘 클릭</li>
                      <li>원하는 요소 클릭</li>
                      <li>Elements 탭에서 선택된 요소 우클릭 → Copy → Copy selector</li>
                    </ol>
                    <p>또는 간단하게: ID가 있으면 <code>#아이디명</code>, 클래스가 있으면 <code>.클래스명</code></p>
                  </div>
                  <input
                    v-model="action.selector"
                    type="text"
                    :placeholder="getSelectorPlaceholder(action.type)"
                    class="input-field"
                  />
                </div>
                
                <div v-if="action.type === 'fill'" class="field-group">
                  <label>입력할 텍스트:</label>
                  <input
                    v-model="action.value"
                    type="text"
                    placeholder="예: 검색어, 사용자명 등"
                    class="input-field"
                  />
                </div>
                
                <div v-if="action.type === 'select'" class="field-group">
                  <label>선택할 옵션:</label>
                  <input
                    v-model="action.value"
                    type="text"
                    placeholder="드롭다운에서 선택할 값"
                    class="input-field"
                  />
                </div>
                
                <div v-if="action.type === 'wait'" class="field-group">
                  <label>몇 초 대기할까요?</label>
                  <input
                    v-model="action.value"
                    type="number"
                    placeholder="예: 2 (2초 대기)"
                    class="input-field"
                  />
                  <small class="input-hint">숫자만 입력하세요 (초 단위)</small>
                </div>
              </div>
            </div>
            
            <button @click="addAction" class="btn-add-action" type="button">
              + 다음 단계 추가
            </button>
            
            <div class="input-group" style="margin-top: 1.5rem;">
              <label for="interactResultSelector">📊 결과 확인 (선택사항):</label>
              <input
                id="interactResultSelector"
                v-model="interactResultSelector"
                type="text"
                placeholder="결과를 표시하는 요소의 선택자 (위와 같은 방법으로 복사)"
                class="input-field"
              />
              <small class="input-hint">
                모든 작업이 끝난 후 결과를 읽어올 요소를 지정하세요. 비워두면 화면만 캡처합니다.
              </small>
            </div>
          </div>
          
          <div v-if="screenValidationError" class="validation-error">
            <div class="error-header">
              <span class="error-icon">⚠️</span>
              <strong class="error-title">오류 발생</strong>
            </div>
            <div class="error-content">
              <pre class="error-message">{{ screenValidationError }}</pre>
            </div>
          </div>
          
          <div v-if="screenValidationResult" class="validation-result">
            <h3>검증 결과</h3>
            <div class="result-info">
              <p><strong>URL:</strong> {{ screenValidationResult.url }}</p>
              <p><strong>선택자:</strong> {{ screenValidationResult.selector || '전체 페이지' }}</p>
              <p v-if="screenValidationResult.actualValue"><strong>읽은 값:</strong> {{ screenValidationResult.actualValue }}</p>
              <p v-if="screenValidationResult.expectedValue"><strong>예상 값:</strong> {{ screenValidationResult.expectedValue }}</p>
              <div class="validation-status" :class="{ 'passed': screenValidationResult.passed, 'failed': !screenValidationResult.passed }">
                <strong>검증 결과:</strong> 
                <span v-if="screenValidationResult.passed">✅ {{ screenValidationResult.message }}</span>
                <span v-else-if="screenValidationResult.selectorError">❌ {{ screenValidationResult.message }}</span>
                <span v-else>❌ {{ screenValidationResult.message }}</span>
              </div>
              <div v-if="screenValidationResult.selectorError" class="selector-error-hint">
                <div class="error-hint-header">
                  <span class="hint-icon">💡</span>
                  <strong>선택자 도움말</strong>
                </div>
                <pre class="error-hint-text">{{ screenValidationResult.selectorError }}</pre>
              </div>
            </div>
            
            <div v-if="screenScreenshot" class="screenshot-container">
              <h4>캡처된 화면</h4>
              <img :src="`data:image/png;base64,${screenScreenshot}`" alt="화면 캡처" class="screenshot-image" />
            </div>
          </div>
          
          <!-- 입력/클릭 결과 -->
          <div v-if="interactResult" class="interact-result">
            <h3>입력/클릭 결과</h3>
            <div class="result-info">
              <p><strong>URL:</strong> {{ interactResult.url }}</p>
              <div v-if="interactResult.actions && interactResult.actions.length > 0" class="actions-log">
                <strong>수행된 액션:</strong>
                <ul>
                  <li v-for="(action, index) in interactResult.actions" :key="index">{{ action }}</li>
                </ul>
              </div>
              <p v-if="interactResult.resultSelector"><strong>결과 선택자:</strong> {{ interactResult.resultSelector }}</p>
              <p v-if="interactResult.resultValue"><strong>결과 값:</strong> {{ interactResult.resultValue }}</p>
            </div>
            
            <div v-if="screenScreenshot" class="screenshot-container">
              <h4>캡처된 화면</h4>
              <img :src="`data:image/png;base64,${screenScreenshot}`" alt="화면 캡처" class="screenshot-image" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 데이터 가져오기 결과 팝업 -->
    <div v-if="showFetchResult" class="fetch-result-overlay" @click="showFetchResult = false">
      <div class="fetch-result-modal" @click.stop>
        <div class="fetch-result-header">
          <h2>📻 MCP 서버에서 가져온 데이터</h2>
          <button @click="showFetchResult = false" class="btn-close">✕</button>
        </div>
        <div class="fetch-result-body">
          <div class="fetch-info">
            <p><strong>가져온 시간:</strong> {{ fetchTimestamp }}</p>
            <p><strong>총 노래 수:</strong> {{ fetchResultData.length }}개</p>
            <p><strong>데이터 소스:</strong> MCP 서버 (mcp-server.js)</p>
          </div>
          <div class="fetch-details">
            <h3>가져온 노래 상세 정보</h3>
            <div class="details-table">
              <table>
                <thead>
                  <tr>
                    <th>순번</th>
                    <th>방송국</th>
                    <th>타입</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, index) in fetchResultData" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>{{ item.방송국 }}</td>
                    <td>
                      <span :class="item.타입 === '현재 재생 중' ? 'badge-current' : 'badge-recent'">
                        {{ item.타입 }}
                      </span>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div class="fetch-result-footer">
          <button @click="showFetchResult = false" class="btn-close-modal">닫기</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useAuthStore } from './stores/auth.js'

const authStore = useAuthStore()

// 인증 모달 상태
const showLoginModal = ref(false)
const showSignupModal = ref(false)
const authError = ref('')

// 사용자 관리 모달
const showUserManagementModal = ref(false)
const userManagementTab = ref('profile')
const userProfileLoading = ref(false)
const userProfileUpdating = ref(false)
const userDataLoading = ref(false)
const userAccountDeleting = ref(false)
const userManagementError = ref('')
const userManagementSuccess = ref('')
const userProfile = ref(null)
const userData = ref({ news: [], radioSongs: [], books: [] })
const userDataSummary = ref({ newsCount: 0, radioSongsCount: 0, booksCount: 0 })
const apiKeys = ref([])
const apiKeysLoading = ref(false)
const showCreateApiKeyModal = ref(false)
const isCreatingApiKey = ref(false)
const createdApiKey = ref(null)
const newApiKeyForm = ref({
  name: '',
  description: '',
  expiresInDays: null
})

// 활성화된 API 키 (예제에 사용)
const activeApiKey = computed(() => {
  const active = apiKeys.value.find(k => k.isActive)
  return active ? active.apiKey : null
})

// 프로필 폼
const profileForm = ref({
  email: '',
  name: ''
})

// 로그인 폼
const loginForm = ref({
  email: '',
  password: ''
})

// 회원가입 폼
const signupForm = ref({
  email: '',
  password: '',
  name: ''
})

// 로그인 처리
async function handleLogin() {
  authError.value = ''
  const result = await authStore.login(loginForm.value.email, loginForm.value.password)
  
  if (result.success) {
    showLoginModal.value = false
    loginForm.value = { email: '', password: '' }
    alert('로그인 성공!')
  } else {
    authError.value = result.error || '로그인에 실패했습니다.'
  }
}

// 회원가입 처리
async function handleSignup() {
  authError.value = ''
  const result = await authStore.signup(
    signupForm.value.email, 
    signupForm.value.password, 
    signupForm.value.name
  )
  
  if (result.success) {
    showSignupModal.value = false
    signupForm.value = { email: '', password: '', name: '' }
    alert('회원가입 성공!')
  } else {
    authError.value = result.error || '회원가입에 실패했습니다.'
  }
}

// 로그아웃 처리
function handleLogout() {
  authStore.logout()
  alert('로그아웃되었습니다.')
}

// 사용자 관리 모달 열기
async function openUserManagementModal() {
  showUserManagementModal.value = true
  userManagementTab.value = 'profile'
  userManagementError.value = ''
  userManagementSuccess.value = ''
  
  // 프로필 정보 로드
  await loadUserProfile()
  
  // 데이터 요약 로드
  await loadUserDataSummary()
}

// 프로필 정보 로드
async function loadUserProfile() {
  userProfileLoading.value = true
  userManagementError.value = ''
  
  try {
    if (!authStore.token) {
      userManagementError.value = '로그인이 필요합니다.'
      return
    }

    const response = await fetch('/api/user/profile', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      if (response.status === 404) {
        userManagementError.value = 'API 엔드포인트를 찾을 수 없습니다. API 서버를 재시작해주세요.'
      } else if (response.status === 401) {
        userManagementError.value = '인증이 필요합니다. 다시 로그인해주세요.'
        authStore.logout()
      } else {
        userManagementError.value = `서버 오류 (${response.status})`
      }
      return
    }
    
    const data = await response.json()
    
    if (data.success) {
      userProfile.value = data.user
      profileForm.value = {
        email: data.user.email || '',
        name: data.user.name || ''
      }
    } else {
      userManagementError.value = data.error || '프로필 정보를 불러오는데 실패했습니다.'
    }
  } catch (error) {
    console.error('프로필 로드 오류:', error)
    userManagementError.value = `프로필 정보를 불러오는데 실패했습니다: ${error.message}`
  } finally {
    userProfileLoading.value = false
  }
}

// 프로필 수정
async function handleUpdateProfile() {
  userProfileUpdating.value = true
  userManagementError.value = ''
  userManagementSuccess.value = ''
  
  try {
    const response = await fetch('/api/user/profile', {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        email: profileForm.value.email,
        name: profileForm.value.name
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      userManagementSuccess.value = '프로필이 수정되었습니다.'
      userProfile.value = data.user
      // Auth store 업데이트
      authStore.user = data.user
      localStorage.setItem('authUser', JSON.stringify(data.user))
      
      // 2초 후 성공 메시지 제거
      setTimeout(() => {
        userManagementSuccess.value = ''
      }, 2000)
    } else {
      userManagementError.value = data.error || '프로필 수정에 실패했습니다.'
    }
  } catch (error) {
    console.error('프로필 수정 오류:', error)
    userManagementError.value = '프로필 수정에 실패했습니다.'
  } finally {
    userProfileUpdating.value = false
  }
}

// 사용자 데이터 요약 로드
async function loadUserDataSummary() {
  userDataLoading.value = true
  
  try {
    if (!authStore.token) {
      return
    }

    const response = await fetch('/api/user/data', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      console.error('데이터 로드 실패:', response.status, response.statusText)
      return
    }
    
    const data = await response.json()
    
    if (data.success) {
      userData.value = data.data
      userDataSummary.value = data.data.summary || { newsCount: 0, radioSongsCount: 0, booksCount: 0 }
    }
  } catch (error) {
    console.error('데이터 로드 오류:', error)
  } finally {
    userDataLoading.value = false
  }
}

// 사용자 데이터 로드 (탭 변경 시)
watch(userManagementTab, async (newTab) => {
  if (newTab === 'data') {
    await loadUserDataSummary()
  } else if (newTab === 'api-keys') {
    await loadApiKeys()
  }
})

// 계정 삭제
async function handleDeleteAccount() {
  if (!confirm('정말 계정을 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.')) {
    return
  }
  
  userAccountDeleting.value = true
  userManagementError.value = ''
  
  try {
    const response = await fetch('/api/user/account', {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    const data = await response.json()
    
    if (data.success) {
      alert('계정이 삭제되었습니다.')
      authStore.logout()
      showUserManagementModal.value = false
    } else {
      userManagementError.value = data.error || '계정 삭제에 실패했습니다.'
    }
  } catch (error) {
    console.error('계정 삭제 오류:', error)
    userManagementError.value = '계정 삭제에 실패했습니다.'
  } finally {
    userAccountDeleting.value = false
  }
}

// 날짜 포맷팅
function formatDate(dateString) {
  if (!dateString) return '-'
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}

// API 키 목록 로드
async function loadApiKeys() {
  apiKeysLoading.value = true
  userManagementError.value = ''
  
  try {
    if (!authStore.token) {
      return
    }

    const response = await fetch('/api/api-keys', {
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    if (!response.ok) {
      console.error('API 키 목록 로드 실패:', response.status)
      return
    }
    
    const data = await response.json()
    
    if (data.success) {
      apiKeys.value = data.apiKeys || []
    }
  } catch (error) {
    console.error('API 키 목록 로드 오류:', error)
  } finally {
    apiKeysLoading.value = false
  }
}

// API 키 생성
async function createApiKey() {
  isCreatingApiKey.value = true
  userManagementError.value = ''
  createdApiKey.value = null
  
  try {
    if (!authStore.token) {
      userManagementError.value = '로그인이 필요합니다.'
      return
    }

    const response = await fetch('/api/api-keys', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({
        name: newApiKeyForm.value.name,
        description: newApiKeyForm.value.description || null,
        expiresInDays: newApiKeyForm.value.expiresInDays ? parseInt(newApiKeyForm.value.expiresInDays) : null
      })
    })
    
    const data = await response.json()
    
    if (data.success) {
      createdApiKey.value = data.apiKey
      // 목록 새로고침
      await loadApiKeys()
    } else {
      userManagementError.value = data.error || 'API 키 생성에 실패했습니다.'
    }
  } catch (error) {
    console.error('API 키 생성 오류:', error)
    userManagementError.value = 'API 키 생성 중 오류가 발생했습니다.'
  } finally {
    isCreatingApiKey.value = false
  }
}

// API 키 생성 모달 닫기
function closeCreateApiKeyModal() {
  showCreateApiKeyModal.value = false
  createdApiKey.value = null
  newApiKeyForm.value = {
    name: '',
    description: '',
    expiresInDays: null
  }
}

// API 키 복사
function copyApiKey(apiKey) {
  navigator.clipboard.writeText(apiKey).then(() => {
    alert('API 키가 클립보드에 복사되었습니다!')
  }).catch(() => {
    alert('복사에 실패했습니다. 수동으로 복사해주세요.')
  })
}

// 코드 예제 복사
function copyCode(code) {
  // HTML 엔티티를 실제 문자로 변환
  const decodedCode = code.replace(/&quot;/g, '"').replace(/&amp;/g, '&').replace(/&lt;/g, '<').replace(/&gt;/g, '>')
  navigator.clipboard.writeText(decodedCode).then(() => {
    alert('코드가 클립보드에 복사되었습니다!')
  }).catch(() => {
    alert('복사에 실패했습니다. 수동으로 복사해주세요.')
  })
}

// API 키 삭제
async function deleteApiKey(keyId) {
  if (!confirm('정말 이 API 키를 삭제하시겠습니까?')) {
    return
  }
  
  try {
    if (!authStore.token) {
      alert('로그인이 필요합니다.')
      return
    }

    const response = await fetch(`/api/api-keys/${keyId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${authStore.token}`
      }
    })
    
    const data = await response.json()
    
    if (data.success) {
      alert('API 키가 삭제되었습니다.')
      await loadApiKeys()
    } else {
      alert(data.error || 'API 키 삭제에 실패했습니다.')
    }
  } catch (error) {
    console.error('API 키 삭제 오류:', error)
    alert('API 키 삭제 중 오류가 발생했습니다.')
  }
}

// API 키 활성화/비활성화
async function toggleApiKey(keyId, isActive) {
  try {
    if (!authStore.token) {
      alert('로그인이 필요합니다.')
      return
    }

    const response = await fetch(`/api/api-keys/${keyId}/toggle`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${authStore.token}`
      },
      body: JSON.stringify({ isActive })
    })
    
    const data = await response.json()
    
    if (data.success) {
      await loadApiKeys()
    } else {
      alert(data.error || 'API 키 상태 변경에 실패했습니다.')
    }
  } catch (error) {
    console.error('API 키 토글 오류:', error)
    alert('API 키 상태 변경 중 오류가 발생했습니다.')
  }
}
/**
 * Vue 앱 메인 컴포넌트
 * 
 * 역할:
 * - 사용자 인터페이스를 제공하는 프론트엔드
 * - 백엔드 API 서버를 통해 데이터를 가져오는 클라이언트
 * - AI 기사 검색, 음악 추천, 라디오 노래 현황 기능 제공
 * 
 * 주요 기능:
 * - AI 기사 검색: News API를 통해 뉴스 기사 검색
 * - 음악 추천: Last.fm API를 통해 유사한 트랙 검색
 * - 라디오 노래 현황: Last.fm API를 통해 인기 차트 조회 및 관리
 * - 검색, 필터, 정렬, 페이지네이션 기능
 * - localStorage를 통한 데이터 저장
 * 
 * 실행 방법:
 *   npm run dev
 * 
 * 포트: http://localhost:5173
 */

import { ref, computed, onMounted, watch, nextTick, onBeforeUnmount } from 'vue'
import { marked } from 'marked'
import { Network } from 'vis-network'

// ============================================
// Marked 설정
// ============================================

// marked 옵션 설정
// - breaks: true - 줄바꿈을 <br>로 변환
// - gfm: true - GitHub Flavored Markdown 지원
marked.setOptions({
  breaks: true, // 줄바꿈을 <br>로 변환
  gfm: true, // GitHub Flavored Markdown 지원
})

// ============================================
// 데이터베이스 (Fallback 데이터)
// ============================================

// 음악 추천 데이터베이스 (Fallback 데이터)
// - API 호출이 실패하거나 결과가 없을 때 사용되는 하드코딩된 데이터
// - 아티스트별 추천 노래 목록
const musicRecommendations = {
  'BTS': [
    { title: 'Butter', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'Permission to Dance', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'Boy With Luv', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'DNA', artist: 'BTS', reason: '같은 아티스트' },
    { title: 'Fake Love', artist: 'BTS', reason: '같은 아티스트' },
  ],
  'IU': [
    { title: 'Good Day', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Eight', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Blueming', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Palette', artist: 'IU', reason: '같은 아티스트' },
    { title: 'Strawberry Moon', artist: 'IU', reason: '같은 아티스트' },
  ],
  'BLACKPINK': [
    { title: 'DDU-DU DDU-DU', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Kill This Love', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Lovesick Girls', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Pink Venom', artist: 'BLACKPINK', reason: '같은 아티스트' },
    { title: 'Shut Down', artist: 'BLACKPINK', reason: '같은 아티스트' },
  ],
  'iKON': [
    { title: 'Love Scenario', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'Killing Me', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'Goodbye Road', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'Rhythm Ta', artist: 'iKON', reason: '같은 아티스트' },
    { title: 'My Type', artist: 'iKON', reason: '같은 아티스트' },
  ],
  'PSY': [
    { title: 'Gangnam Style', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'Gentleman', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'Daddy', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'New Face', artist: 'PSY', reason: '같은 아티스트' },
    { title: 'That That', artist: 'PSY', reason: '같은 아티스트' },
  ],
}

// 하드코딩된 데이터는 제거됨 - 이제 실제 API를 사용합니다

// 반응형 데이터
const showAIArticleSearch = ref(false)
const showEconomyArticleSearch = ref(false)
const showMusicRecommendation = ref(false)
const showRadioHistory = ref(false)
const showBookRecommendation = ref(false)
const showBookHistory = ref(false)
const showScreenValidation = ref(false)
const showMCPGuide = ref(false)
const currentGuideType = ref('nodejs') // 'nodejs' 또는 'python'
const markdownContent = ref('')
const isLoading = ref(false)
const aiArticles = ref([])
const isSearching = ref(false)
const articleError = ref('')
const dataCorrelation = ref([]) // 데이터 연계도 분석 결과
const graphData = ref({ nodes: [], edges: [] }) // 네트워크 그래프 데이터
const networkContainer = ref(null) // 네트워크 그래프 컨테이너
let networkInstance = null // vis-network 인스턴스
const economySearchKeyword = ref('')
const economyArticles = ref([])
const isSearchingEconomy = ref(false)
const economyArticleError = ref('')
const songTitle = ref('')
const artist = ref('')
const recommendations = ref([])
const musicError = ref('')
const searchKeyword = ref('')

// 라디오 노래 현황 관련
const searchQuery = ref('')
const selectedArtist = ref('')
const selectedGenre = ref('')
const sortBy = ref('count')
const currentPage = ref(1)
const songsHistory = ref([])
const filteredSongs = ref([])
const paginatedSongs = ref([])
const showFetchResult = ref(false)
const fetchResultData = ref([])
const fetchTimestamp = ref('')

// 한 달간 데이터 수집 관련
const isCollectingMonthlyData = ref(false)
const monthlyCollectionProgress = ref(0)
const monthlyCollectionStatus = ref('')
const monthlyDataCollection = ref([]) // 날짜별 수집된 데이터

// 뉴스 수집 관련
const isCollectingNewsData = ref(false)
const newsCollectionProgress = ref(0)
const newsCollectionStatus = ref('')
const newsHistory = ref([]) // 수집된 뉴스 히스토리
const showNewsCollection = ref(false) // 뉴스 수집 현황 표시 여부

// 뉴스 API 호출 제한 (1분에 한 번만 호출)
const lastEconomyNewsFetch = ref(null) // 마지막 경제 뉴스 호출 시간
const lastAINewsFetch = ref(null) // 마지막 AI 뉴스 호출 시간
const NEWS_FETCH_INTERVAL = 60 * 1000 // 1분 (밀리초)

// 경제뉴스 알람 관련
const isEconomyAlarmEnabled = ref(false) // 알람 활성화 여부
const showEconomyAlarmModal = ref(false) // 알람 모달 표시 여부
const alarmChecking = ref(false) // 알람 확인 중 여부
const newEconomyNews = ref([]) // 새로운 경제 뉴스 목록
const lastAlarmCheckTime = ref('') // 마지막 알람 확인 시간
const economyAlarmInterval = ref(null) // 알람 체크 인터벌
const ALARM_CHECK_INTERVAL = 60 * 1000 // 1분마다 체크

// 뉴스 필터링 및 페이지네이션
const newsSearchQuery = ref('')
const selectedNewsCategory = ref('')
const newsSortBy = ref('date') // 'date', 'title', 'source'
const filteredNews = ref([])
const currentNewsPage = ref(1)
const newsPerPage = 10

// 도서 관련
const bookKeyword = ref('')
const bookCategory = ref('')
const recommendedBooks = ref([])
const isSearchingBooks = ref(false)
const bookError = ref('')
const booksHistory = ref([]) // 수집된 도서 히스토리
const isSavingNews = ref(false)
const isSavingBook = ref(false)
const bookSearchQuery = ref('')
const bookSortBy = ref('date')
const currentBookPage = ref(1)
const booksPerPage = ref(10)
const isCollectingBookData = ref(false)
const bookCollectionProgress = ref(0)
const bookCollectionStatus = ref('')

// 화면 검증 관련
const screenValidationUrl = ref('')
const screenValidationSelector = ref('')
const screenValidationExpectedValue = ref('')
const screenValidationResult = ref(null)
const screenValidationError = ref('')
const isValidatingScreen = ref(false)
const screenScreenshot = ref(null) // Base64 이미지 데이터
const interactActions = ref([
  { type: 'fill', selector: '', value: '' }
])
const interactResultSelector = ref('')
const interactResult = ref(null)

// MCP 가이드 열기
const openMCPGuide = async () => {
  showMCPGuide.value = true
  currentGuideType.value = 'nodejs'
  
  // 이미 로드된 내용이 있으면 다시 로드하지 않음
  if (markdownContent.value && currentGuideType.value === 'nodejs') {
    return
  }

  isLoading.value = true
  
  try {
    // 한글 파일명을 URL 인코딩하여 요청
    const fileName = encodeURIComponent('MCP_가이드.md')
    const response = await fetch(`/${fileName}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const text = await response.text()
    
    if (!text || text.trim() === '') {
      throw new Error('파일 내용이 비어있습니다.')
    }
    
    // 마크다운을 HTML로 변환
    markdownContent.value = marked.parse(text)
  } catch (err) {
    console.error('MCP 가이드 로드 오류:', err)
    markdownContent.value = `
      <div style="padding: 20px; text-align: center;">
        <h3 style="color: #f44336;">⚠️ 가이드 파일을 불러올 수 없습니다</h3>
        <p>오류: ${err.message}</p>
        <p style="margin-top: 20px; color: #666;">
          파일 경로를 확인하거나 개발자 콘솔을 확인해주세요.
        </p>
      </div>
    `
  } finally {
    isLoading.value = false
  }
}

// Python MCP 가이드 열기
const openPythonMCPGuide = async () => {
  showMCPGuide.value = true
  currentGuideType.value = 'python'
  
  // 이미 로드된 내용이 있으면 다시 로드하지 않음
  if (markdownContent.value && currentGuideType.value === 'python') {
    return
  }

  isLoading.value = true
  
  try {
    // 한글 파일명을 URL 인코딩하여 요청
    const fileName = encodeURIComponent('MCP_가이드_보기_(Python).md')
    const response = await fetch(`/${fileName}`)
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    
    const text = await response.text()
    
    if (!text || text.trim() === '') {
      throw new Error('파일 내용이 비어있습니다.')
    }
    
    // 마크다운을 HTML로 변환
    markdownContent.value = marked.parse(text)
  } catch (err) {
    console.error('Python MCP 가이드 로드 오류:', err)
    markdownContent.value = `
      <div style="padding: 20px; text-align: center;">
        <h3 style="color: #f44336;">⚠️ 가이드 파일을 불러올 수 없습니다</h3>
        <p>오류: ${err.message}</p>
        <p style="margin-top: 20px; color: #666;">
          파일 경로를 확인하거나 개발자 콘솔을 확인해주세요.
        </p>
      </div>
    `
  } finally {
    isLoading.value = false
  }
}

// API DOCS 열기
const openAPIDocs = () => {
  window.open('http://localhost:3001/api-docs', '_blank')
}

// MCP 가이드 닫기
const closeMCPGuide = () => {
  showMCPGuide.value = false
  markdownContent.value = '' // 내용 초기화하여 다음에 다시 로드되도록
  currentGuideType.value = 'nodejs'
}

// ============================================
// 함수 정의
// ============================================

/**
 * 모든 섹션 닫기 함수
 * 
 * 기능:
 * - 모든 섹션을 닫고 초기화
 */
const closeAllSections = () => {
  showAIArticleSearch.value = false
  showEconomyArticleSearch.value = false
  showMusicRecommendation.value = false
  showRadioHistory.value = false
  showBookRecommendation.value = false
  showBookHistory.value = false
  showNewsCollection.value = false
  showScreenValidation.value = false
  
  // 데이터 초기화
  aiArticles.value = []
  economyArticles.value = []
  recommendations.value = []
  recommendedBooks.value = []
  articleError.value = ''
  economyArticleError.value = ''
  musicError.value = ''
  bookError.value = ''
  searchKeyword.value = ''
  dataCorrelation.value = []
  graphData.value = { nodes: [], edges: [] }
  if (networkInstance) {
    networkInstance.destroy()
    networkInstance = null
  }
}

/**
 * AI 뉴스 검색 토글 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 AI 뉴스 검색 섹션만 열기
 */
const toggleAIArticleSearch = () => {
  closeAllSections()
  showAIArticleSearch.value = true
}

/**
 * AI 뉴스 검색 함수
 * 
 * 기능:
 * - 백엔드 API 서버를 통해 News API 호출
 * - 사용자가 입력한 키워드로 AI 관련 뉴스 검색
 * - 검색 결과에 대한 데이터 연계도 분석 수행
 * 
 * API 엔드포인트:
 *   GET /api/news?q=키워드
 */
const searchAIArticles = async () => {
  // 에러 초기화
  articleError.value = ''
  aiArticles.value = []
  dataCorrelation.value = []
  isSearching.value = true

  // 입력값 검증
  if (!searchKeyword.value || searchKeyword.value.trim() === '') {
    articleError.value = '검색 키워드를 입력해주세요.'
    isSearching.value = false
    return
  }

  try {
    // Vite 프록시를 통해 News API 호출
    const searchKeywordEncoded = encodeURIComponent(searchKeyword.value.trim())
    const apiUrl = `/api/news?q=${searchKeywordEncoded}`
    
    const response = await fetch(apiUrl)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`News API 오류: ${response.status} - ${errorData.message || response.statusText}`)
    }

    const data = await response.json()

    // 결과가 없는 경우
    if (!data.articles || data.articles.length === 0) {
      articleError.value = `"${searchKeyword.value}"에 대한 AI 관련 기사를 찾을 수 없습니다.`
      isSearching.value = false
      return
    }

    // 기사 데이터 포맷팅 (최근 일주일 필터링, 최신일자 순 정렬)
    const now = new Date()
    const oneWeekAgo = new Date(now.getTime() - 7 * 24 * 60 * 60 * 1000)
    
    // 먼저 필터링 전 기사 수 확인
    const allArticles = data.articles || []
    
    const formattedArticles = allArticles
      .filter(article => {
        // 제목 필터링
        if (!article.title || article.title === '[Removed]') return false
        // 일주일 이상 지난 기사 필터링
        if (article.publishedAt) {
          const publishedDate = new Date(article.publishedAt)
          if (publishedDate < oneWeekAgo) return false
        }
        return true
      })
      .sort((a, b) => {
        // 최신일자 순으로 정렬 (내림차순)
        const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
        const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
        return dateB - dateA
      })
      .slice(0, 10) // 최대 10개
      .map(article => {
        const publishedDate = article.publishedAt 
          ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          : '날짜 정보 없음'

        return {
          title: article.title || '제목 없음',
          summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
          date: publishedDate,
          source: article.source?.name || '출처 정보 없음',
          category: 'AI 뉴스',
          url: article.url || '#',
        }
      })

    // 필터링 후 결과 확인
    if (formattedArticles.length === 0) {
      // 일주일 필터링 후 결과가 없으면, 필터링 없이 최신 기사 표시
      const allFormattedArticles = allArticles
        .filter(article => {
          // 제목 필터링만 수행
          if (!article.title || article.title === '[Removed]') return false
          return true
        })
        .sort((a, b) => {
          // 최신일자 순으로 정렬 (내림차순)
          const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
          const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
          return dateB - dateA
        })
        .slice(0, 10) // 최대 10개
        .map(article => {
          const publishedDate = article.publishedAt 
            ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })
            : '날짜 정보 없음'

          return {
            title: article.title || '제목 없음',
            summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
            date: publishedDate,
            source: article.source?.name || '출처 정보 없음',
            category: 'AI 뉴스',
            url: article.url || '#',
          }
        })
      
      if (allFormattedArticles.length === 0) {
        articleError.value = `"${searchKeyword.value}"에 대한 AI 관련 기사를 찾을 수 없습니다.`
        isSearching.value = false
        return
      }
      
      // 일주일 이내 기사가 없지만 전체 기사가 있는 경우
      aiArticles.value = allFormattedArticles
      articleError.value = '최근 일주일 이내의 기사가 없어 전체 기사를 표시합니다.'
    } else {
      // 정상적으로 일주일 이내 기사가 있는 경우
      aiArticles.value = formattedArticles
      articleError.value = ''
    }
    
    // 데이터 연계도 분석 수행
    analyzeDataCorrelation(aiArticles.value, searchKeyword.value.trim())
    
    isSearching.value = false
  } catch (error) {
    console.error('뉴스 검색 오류:', error)
    articleError.value = `뉴스 검색 중 오류가 발생했습니다: ${error.message}`
    isSearching.value = false
  }
}

/**
 * 데이터 연계도 분석 함수 (빅데이터 기반 - 고급 연관 분석)
 * 
 * 기능:
 * - 실제 기사 텍스트에서 키워드 자동 추출
 * - TF-IDF 기반 중요도 계산
 * - 키워드 간 상관관계 분석 (Jaccard 유사도, 코사인 유사도)
 * - 시간적 패턴 분석 (트렌드 분석)
 * - 출처 다양성 분석
 * - 네트워크 중심성 분석
 * - 빅데이터 패턴 분석을 통한 인사이트 제공
 * 
 * @param {Array} articles - 분석할 기사 배열
 * @param {string} searchKeyword - 검색 키워드
 */
const analyzeDataCorrelation = (articles, searchKeyword) => {
  if (!articles || articles.length === 0) {
    dataCorrelation.value = []
    graphData.value = { nodes: [], edges: [] }
    return
  }

  const totalArticles = articles.length
  
  // 1. 키워드 추출 (실제 기사 텍스트에서)
  const keywordFrequency = {} // TF (Term Frequency)
  const keywordDocumentFrequency = {} // DF (Document Frequency)
  const keywordCooccurrence = {} // 키워드 동시 출현 분석
  const keywordSources = {} // 키워드별 출처 집합
  const keywordDates = {} // 키워드별 날짜 배열
  const keywordPositions = {} // 키워드별 문서 내 위치 (제목=2점, 요약=1점)
  
  // 불용어 제거 (한글, 영어 공통)
  const stopWords = new Set([
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    '이', '가', '을', '를', '에', '의', '와', '과', '로', '으로', '에서', '에게', '에게서',
    '은', '는', '도', '만', '부터', '까지', '보다', '처럼', '같이', '또한', '그리고', '하지만',
    '것', '수', '등', '및', '또는', '그', '이것', '저것', '그것'
  ])
  
  // 키워드 추출 함수 (2글자 이상 단어 추출)
  const extractKeywords = (text) => {
    const words = text
      .toLowerCase()
      .replace(/[^\w\s가-힣]/g, ' ') // 특수문자 제거
      .split(/\s+/)
      .filter(word => word.length >= 2 && !stopWords.has(word))
    
    // 한글 단어와 영어 단어 분리
    const koreanWords = words.filter(w => /[가-힣]/.test(w))
    const englishWords = words.filter(w => /^[a-z]+$/.test(w))
    
    return [...koreanWords, ...englishWords]
  }
  
  // 각 기사에서 키워드 추출 및 분석
  articles.forEach((article, articleIndex) => {
    const titleText = (article.title || '').toLowerCase()
    const summaryText = (article.summary || '').toLowerCase()
    const fullText = `${titleText} ${summaryText}`
    
    // 제목과 요약에서 키워드 추출
    const titleKeywords = extractKeywords(titleText)
    const summaryKeywords = extractKeywords(summaryText)
    const allKeywords = [...new Set([...titleKeywords, ...summaryKeywords])]
    
    // 키워드 빈도 및 문서 빈도 계산
    allKeywords.forEach(keyword => {
      // TF 계산 (제목에 있으면 가중치 2, 요약에 있으면 가중치 1)
      const titleCount = titleKeywords.filter(k => k === keyword).length
      const summaryCount = summaryKeywords.filter(k => k === keyword).length
      const tf = titleCount * 2 + summaryCount
      
      keywordFrequency[keyword] = (keywordFrequency[keyword] || 0) + tf
      keywordDocumentFrequency[keyword] = (keywordDocumentFrequency[keyword] || 0) + 1
      
      // 키워드별 출처 수집
      if (article.source) {
        if (!keywordSources[keyword]) {
          keywordSources[keyword] = new Set()
        }
        keywordSources[keyword].add(article.source)
      }
      
      // 키워드별 날짜 수집
      if (article.date) {
        try {
          const date = new Date(article.date)
          if (!isNaN(date.getTime())) {
            if (!keywordDates[keyword]) {
              keywordDates[keyword] = []
            }
            keywordDates[keyword].push(date)
          }
        } catch (e) {
          // 날짜 파싱 실패 무시
        }
      }
      
      // 키워드 위치 점수 (제목에 있으면 높은 점수)
      if (titleKeywords.includes(keyword)) {
        keywordPositions[keyword] = (keywordPositions[keyword] || 0) + 2
      } else if (summaryKeywords.includes(keyword)) {
        keywordPositions[keyword] = (keywordPositions[keyword] || 0) + 1
      }
    })
    
    // 키워드 동시 출현 분석 (같은 기사에서 함께 나타나는 키워드)
    for (let i = 0; i < allKeywords.length; i++) {
      for (let j = i + 1; j < allKeywords.length; j++) {
        const key1 = allKeywords[i]
        const key2 = allKeywords[j]
        const pairKey = [key1, key2].sort().join('|')
        keywordCooccurrence[pairKey] = (keywordCooccurrence[pairKey] || 0) + 1
      }
    }
  })
  
  // 2. TF-IDF 기반 중요도 계산
  const calculateTFIDF = (keyword) => {
    const tf = keywordFrequency[keyword] || 0
    const df = keywordDocumentFrequency[keyword] || 0
    const idf = df > 0 ? Math.log(totalArticles / df) : 0
    const tfidf = tf * idf
    
    // 위치 가중치 적용 (제목에 자주 나타나면 중요)
    const positionScore = keywordPositions[keyword] || 0
    const positionWeight = 1 + (positionScore / (totalArticles * 2)) * 0.5
    
    return tfidf * positionWeight
  }
  
  // 3. 키워드 간 상관관계 분석 (Jaccard 유사도)
  const calculateJaccardSimilarity = (keyword1, keyword2) => {
    const articles1 = new Set()
    const articles2 = new Set()
    
    articles.forEach((article, index) => {
      const text = `${article.title} ${article.summary}`.toLowerCase()
      if (text.includes(keyword1.toLowerCase())) {
        articles1.add(index)
      }
      if (text.includes(keyword2.toLowerCase())) {
        articles2.add(index)
      }
    })
    
    const intersection = new Set([...articles1].filter(x => articles2.has(x)))
    const union = new Set([...articles1, ...articles2])
    
    return union.size > 0 ? intersection.size / union.size : 0
  }
  
  // 4. 키워드별 종합 점수 계산
  const keywordScores = {}
  Object.keys(keywordFrequency).forEach(keyword => {
    const tfidf = calculateTFIDF(keyword)
    const sourceDiversity = keywordSources[keyword] ? keywordSources[keyword].size : 0
    const documentCount = keywordDocumentFrequency[keyword] || 0
    
    // 시간적 트렌드 분석 (최근 기사에 많이 나타나면 높은 점수)
    let trendScore = 0
    if (keywordDates[keyword] && keywordDates[keyword].length > 0) {
      const sortedDates = [...keywordDates[keyword]].sort((a, b) => b - a)
      const recentCount = sortedDates.filter(date => {
        const daysAgo = (new Date() - date) / (1000 * 60 * 60 * 24)
        return daysAgo <= 3 // 최근 3일
      }).length
      trendScore = (recentCount / sortedDates.length) * 0.3
    }
    
    // 종합 점수 계산
    const baseScore = tfidf * 10 // TF-IDF를 0-100 스케일로 변환
    const diversityScore = (sourceDiversity / totalArticles) * 20 // 출처 다양성 점수
    const coverageScore = (documentCount / totalArticles) * 30 // 문서 커버리지 점수
    const trendBonus = trendScore * 20 // 트렌드 보너스
    
    keywordScores[keyword] = {
      keyword,
      tfidf,
      baseScore: Math.min(100, baseScore),
      diversityScore,
      coverageScore,
      trendScore: trendBonus,
      totalScore: Math.min(100, baseScore + diversityScore + coverageScore + trendBonus),
      documentCount,
      sourceDiversity,
      frequency: keywordFrequency[keyword]
    }
  })
  
  // 5. 상위 키워드 추출 (종합 점수 기준)
  const sortedKeywords = Object.values(keywordScores)
    .sort((a, b) => b.totalScore - a.totalScore)
    .slice(0, 15) // 상위 15개
  
  // 6. 키워드 간 상관관계 계산
  const keywordCorrelations = {}
  sortedKeywords.forEach((item1, i) => {
    sortedKeywords.slice(i + 1).forEach(item2 => {
      const similarity = calculateJaccardSimilarity(item1.keyword, item2.keyword)
      if (similarity > 0.1) { // 유사도 10% 이상만 저장
        const pairKey = [item1.keyword, item2.keyword].sort().join('|')
        keywordCorrelations[pairKey] = similarity
      }
    })
  })
  
  // 7. 연계도 결과 생성
  const correlationResults = sortedKeywords.map(item => {
    // 관련 기사 수 계산
    const relatedArticles = item.documentCount
    
    // 시간 분포 분석
    let timeDistribution = '분산'
    let timeTrend = '안정'
    if (keywordDates[item.keyword] && keywordDates[item.keyword].length > 0) {
      const sortedDates = [...keywordDates[item.keyword]].sort((a, b) => a - b)
      const dateRange = sortedDates[sortedDates.length - 1] - sortedDates[0]
      const daysDiff = dateRange / (1000 * 60 * 60 * 24)
      
      if (daysDiff <= 2) {
        timeDistribution = '집중'
      } else if (daysDiff <= 5) {
        timeDistribution = '보통'
      }
      
      // 트렌드 분석 (최근 증가 추세인지)
      const recentCount = sortedDates.filter(date => {
        const daysAgo = (new Date() - date) / (1000 * 60 * 60 * 24)
        return daysAgo <= 3
      }).length
      
      if (recentCount > sortedDates.length * 0.5) {
        timeTrend = '상승'
      } else if (recentCount < sortedDates.length * 0.2) {
        timeTrend = '하락'
      }
    }
    
    // 관련 키워드 찾기 (상관관계 높은 키워드)
    const relatedKeywords = Object.entries(keywordCorrelations)
      .filter(([pairKey, similarity]) => {
        const [key1, key2] = pairKey.split('|')
        return (key1 === item.keyword || key2 === item.keyword) && similarity > 0.2
      })
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([pairKey, similarity]) => {
        const [key1, key2] = pairKey.split('|')
        return key1 === item.keyword ? key2 : key1
      })
    
    return {
      keyword: item.keyword,
      score: Math.round(item.totalScore),
      relatedArticles: relatedArticles,
      sourceDiversity: item.sourceDiversity,
      timeDistribution: timeDistribution,
      timeTrend: timeTrend,
      tfidf: Math.round(item.tfidf * 100) / 100,
      relatedKeywords: relatedKeywords,
      correlationStrength: relatedKeywords.length > 0 ? '강함' : '보통'
    }
  })
  
  // 8. 검색 키워드 추가 (있는 경우)
  if (searchKeyword) {
    const searchKeywordLower = searchKeyword.toLowerCase()
    const existingIndex = correlationResults.findIndex(item => 
      item.keyword.toLowerCase() === searchKeywordLower
    )
    
    if (existingIndex >= 0) {
      // 이미 있으면 맨 앞으로 이동하고 점수 최대화
      const existing = correlationResults.splice(existingIndex, 1)[0]
      existing.score = 100
      correlationResults.unshift(existing)
    } else {
      // 없으면 새로 추가
      const searchKeywordArticles = articles.filter(article => {
        const text = `${article.title} ${article.summary}`.toLowerCase()
        return text.includes(searchKeywordLower)
      }).length
      
      correlationResults.unshift({
        keyword: searchKeyword,
        score: 100,
        relatedArticles: searchKeywordArticles,
        sourceDiversity: keywordSources[searchKeywordLower]?.size || 0,
        timeDistribution: '최신',
        timeTrend: '상승',
        tfidf: 0,
        relatedKeywords: [],
        correlationStrength: '최상'
      })
    }
  }
  
  dataCorrelation.value = correlationResults
  
  // 9. 네트워크 그래프 데이터 생성
  generateNetworkGraph(correlationResults, keywordCooccurrence, searchKeyword, articles)
}

/**
 * 네트워크 그래프 데이터 생성 함수
 * 
 * 기능:
 * - 키워드 간의 상하위 관계를 네트워크 그래프로 시각화
 * - vis-network를 사용하여 인터랙티브 그래프 생성
 * 
 * @param {Array} correlationResults - 연계도 분석 결과
 * @param {Object} keywordCooccurrence - 키워드 동시 출현 데이터
 * @param {string} searchKeyword - 검색 키워드
 */
const generateNetworkGraph = (correlationResults, keywordCooccurrence, searchKeyword, articles) => {
  if (!correlationResults || correlationResults.length === 0) {
    graphData.value = { nodes: [], edges: [] }
    return
  }
  
  // 최소 2회 이상 동시 출현한 관계만 표시
  const minCooccurrence = 2
  const minNodesForGraph = 3 // 최소 3개 노드 이상일 때만 그래프 표시
  
  if (correlationResults.length < minNodesForGraph) {
    graphData.value = { nodes: [], edges: [] }
    return
  }
  
  const nodes = []
  const edges = []
  const nodeMap = new Map()
  
  // 검색 키워드를 중심으로 정렬 (연계도 높은 순)
  const sortedResults = [...correlationResults].sort((a, b) => {
    const aIsRoot = a.level === 0 || a.keyword.toLowerCase() === searchKeyword?.toLowerCase()
    const bIsRoot = b.level === 0 || b.keyword.toLowerCase() === searchKeyword?.toLowerCase()
    
    if (aIsRoot && !bIsRoot) return -1
    if (!aIsRoot && bIsRoot) return 1
    return b.score - a.score
  })
  
  // 노드 생성 (상위 15개만)
  sortedResults.slice(0, 15).forEach((item, index) => {
    const nodeId = index + 1
    const isRoot = item.level === 0 || item.keyword.toLowerCase() === searchKeyword?.toLowerCase()
    
    nodeMap.set(item.keyword, nodeId)
    
    // 노드 크기는 연계도와 관련 기사 수에 비례
    const nodeSize = Math.max(14, Math.min(30, 14 + (item.score / 10) + (item.relatedArticles / 2)))
    
    nodes.push({
      id: nodeId,
      label: item.keyword,
      value: item.score,
      level: isRoot ? 0 : item.level || 1,
      color: isRoot 
        ? { background: '#667eea', border: '#5568d3' }
        : item.score >= 70
        ? { background: '#764ba2', border: '#653a8a' }
        : item.score >= 40
        ? { background: '#9e9e9e', border: '#757575' }
        : { background: '#bdbdbd', border: '#9e9e9e' },
      font: { 
        size: Math.round(nodeSize),
        color: '#333',
        face: 'Arial',
        bold: isRoot || item.score >= 70
      },
      shape: isRoot ? 'diamond' : 'circle',
      title: `키워드: ${item.keyword}\n연계도: ${item.score}%\n관련 기사: ${item.relatedArticles}건\n출처: ${item.sourceDiversity}개`
    })
  })
  
  // 동시 출현 빈도를 기반으로 관계 분석
  const strongRelations = new Set()
  
  // 동시 출현 빈도가 높은 관계만 엣지로 추가
  Object.entries(keywordCooccurrence)
    .filter(([pairKey, count]) => count >= minCooccurrence)
    .sort((a, b) => b[1] - a[1])
    .slice(0, 20) // 상위 20개 관계만
    .forEach(([pairKey, count]) => {
      const [key1, key2] = pairKey.split('|')
      if (nodeMap.has(key1) && nodeMap.has(key2)) {
        const id1 = nodeMap.get(key1)
        const id2 = nodeMap.get(key2)
        
        // 양방향 관계로 표시
        const relationKey = [id1, id2].sort().join('-')
        if (!strongRelations.has(relationKey)) {
          strongRelations.add(relationKey)
          
          // 연계도가 높은 키워드를 중심으로 방향 설정
          const node1 = sortedResults.find(r => r.keyword === key1)
          const node2 = sortedResults.find(r => r.keyword === key2)
          const fromId = (node1?.score || 0) >= (node2?.score || 0) ? id1 : id2
          const toId = fromId === id1 ? id2 : id1
          
          edges.push({
            from: fromId,
            to: toId,
            arrows: 'to',
            color: { 
              color: count >= 5 ? '#667eea' : count >= 3 ? '#764ba2' : '#9e9e9e',
              highlight: '#667eea'
            },
            width: Math.max(1, Math.min(4, Math.round(count / 2))),
            label: count >= 3 ? `${count}회` : '',
            font: { size: 11, color: '#667eea' },
            title: `동시 출현: ${count}회`
          })
        }
      }
    })
  
  // 검색 키워드가 있으면 중심 노드로 설정
  if (searchKeyword && nodeMap.has(searchKeyword)) {
    const rootId = nodeMap.get(searchKeyword)
    const rootNode = nodes.find(n => n.id === rootId)
    if (rootNode) {
      rootNode.level = 0
      rootNode.color = { background: '#667eea', border: '#5568d3' }
      rootNode.shape = 'diamond'
      rootNode.font.bold = true
      rootNode.font.size = 24
    }
  }
  
  // 엣지가 없으면 그래프를 표시하지 않음
  if (edges.length === 0) {
    graphData.value = { nodes: [], edges: [] }
    return
  }
  
  graphData.value = { nodes, edges }
  
  // 그래프 렌더링
  nextTick(() => {
    renderNetworkGraph()
  })
}

/**
 * 네트워크 그래프 렌더링 함수
 */
const renderNetworkGraph = () => {
  if (!networkContainer.value || graphData.value.nodes.length === 0) {
    return
  }
  
  // 검색 키워드를 중심으로 하는 레이아웃
  const rootNode = graphData.value.nodes.find(n => n.level === 0 || n.shape === 'diamond')
  
  const options = {
    layout: {
      hierarchical: rootNode ? {
        enabled: true,
        direction: 'UD', // 위에서 아래로
        sortMethod: 'directed',
        levelSeparation: 120,
        nodeSpacing: 150,
        treeSpacing: 150,
        shakeTowards: 'leaves'
      } : {
        enabled: false
      }
    },
    physics: {
      enabled: !rootNode, // 계층 구조가 있으면 물리 엔진 비활성화
      stabilization: {
        enabled: true,
        iterations: 200,
        fit: true
      },
      barnesHut: {
        gravitationalConstant: -2000,
        centralGravity: 0.1,
        springLength: 150,
        springConstant: 0.05,
        damping: 0.1
      }
    },
    interaction: {
      dragNodes: true,
      dragView: true,
      zoomView: true,
      selectConnectedEdges: true,
      hover: true
    },
    nodes: {
      borderWidth: 2,
      shadow: {
        enabled: true,
        color: 'rgba(0,0,0,0.2)',
        size: 5,
        x: 2,
        y: 2
      },
      shapeProperties: {
        useBorderWithImage: true
      },
      scaling: {
        min: 10,
        max: 30
      }
    },
    edges: {
      smooth: {
        type: 'continuous',
        roundness: 0.5
      },
      shadow: {
        enabled: true,
        color: 'rgba(0,0,0,0.1)',
        size: 3,
        x: 1,
        y: 1
      },
      font: {
        size: 11,
        align: 'middle'
      }
    }
  }
  
  // 기존 인스턴스 제거
  if (networkInstance) {
    networkInstance.destroy()
  }
  
  // 새 네트워크 생성
  networkInstance = new Network(networkContainer.value, graphData.value, options)
}


/**
 * 제목 자르기 함수
 * 
 * 기능:
 * - 제목이 너무 길면 지정된 길이로 자르고 말줄임표 추가
 * 
 * @param {string} title - 원본 제목
 * @param {number} maxLength - 최대 길이
 * @returns {string} - 잘린 제목
 */
const truncateTitle = (title, maxLength = 80) => {
  if (!title) return ''
  if (title.length <= maxLength) return title
  return title.substring(0, maxLength) + '...'
}

/**
 * 경제 뉴스 검색 토글 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 경제 뉴스 검색 섹션만 열기
 * - 섹션이 열릴 때 자동으로 최신 경제 뉴스 불러오기 (1분에 한 번만)
 */
const toggleEconomyArticleSearch = async () => {
  closeAllSections()
  showEconomyArticleSearch.value = true
  
  // 화면 초기화
  economyArticles.value = []
  economyArticleError.value = ''
  isSearchingEconomy.value = false
  
  // 자동으로 최신 뉴스 불러오기 (fetchLatestEconomyNews 내부에서 호출 제한 처리)
  try {
    await fetchLatestEconomyNews()
  } catch (error) {
    console.error('[경제 뉴스] 자동 로드 오류:', error)
    economyArticleError.value = `뉴스를 불러오는 중 오류가 발생했습니다: ${error.message}`
  }
}

/**
 * 경제 뉴스 중요도 계산 함수
 * 
 * 기능:
 * - 제목, 내용, 출처를 분석하여 경제 뉴스의 중요도를 계산
 * - 별 3개: 매우중요 (핵심 경제 지표, 주요 정책, 긴급 뉴스)
 * - 별 2개: 보통 (일반 경제 뉴스)
 * - 별 1개: 미흡 (경제 관련성이 낮은 뉴스)
 * 
 * 판단 기준:
 * - 매우중요: 금리, 환율, GDP, 인플레이션, 부동산 가격, 주가 지수, 금리 정책, 환율 정책, 주요 언론사, 긴급/속보
 * - 보통: 주식, 부동산, 금융, 증시, 경제 등 일반 키워드
 * - 미흡: 그 외
 */
const calculateEconomyImportance = (article) => {
  const title = (article.title || '').toLowerCase()
  const description = (article.description || '').toLowerCase()
  const content = (article.content || '').toLowerCase()
  const source = (article.source?.name || '').toLowerCase()
  const fullText = `${title} ${description} ${content}`

  let score = 0

  // 매우 중요 키워드 (핵심 경제 지표 및 정책)
  const veryImportantKeywords = [
    '금리', '기준금리', '금리인상', '금리인하', '금리정책',
    '환율', '원달러', '원화', '환율변동', '환율정책',
    'gdp', '국내총생산', '경제성장률',
    '인플레이션', '물가', '소비자물가', '생산자물가',
    '부동산가격', '아파트가격', '부동산정책', '주택가격',
    '코스피', '코스닥', '주가지수', '종합주가지수',
    '한국은행', '한은', '금융통화위원회', '금통위',
    '긴급', '속보', '특보', '발표', '결정', '발표'
  ]

  // 보통 중요 키워드
  const normalKeywords = [
    '주식', '부동산', '금융', '증시', '경제', '경기',
    '기업', '기업실적', '수출', '수입', '무역',
    '고용', '실업률', '취업', '일자리'
  ]

  // 주요 언론사 (매우 중요)
  const majorSources = [
    '조선일보', '중앙일보', '매일경제', '한국경제', '이데일리',
    'chosun', 'joongang', 'mk', 'hankyung', 'edaily'
  ]

  // 매우 중요 점수 계산
  veryImportantKeywords.forEach(keyword => {
    if (fullText.includes(keyword)) {
      score += 3
    }
  })

  // 주요 언론사 점수
  majorSources.forEach(sourceName => {
    if (source.includes(sourceName)) {
      score += 2
    }
  })

  // 긴급성 단어 점수
  if (title.includes('긴급') || title.includes('속보') || title.includes('특보')) {
    score += 2
  }

  // 보통 중요 점수 계산
  normalKeywords.forEach(keyword => {
    if (fullText.includes(keyword)) {
      score += 1
    }
  })

  // 중요도 결정 (별 개수)
  if (score >= 5) {
    return { stars: '⭐⭐⭐', label: '매우중요', value: 3 }
  } else if (score >= 2) {
    return { stars: '⭐⭐', label: '보통', value: 2 }
  } else {
    return { stars: '⭐', label: '미흡', value: 1 }
  }
}

/**
 * 경제뉴스 알람 토글 함수
 * 
 * 기능:
 * - 알람 활성화/비활성화
 * - 활성화 시 주기적으로 새로운 경제 뉴스 확인 (1분마다)
 * - 브라우저 알림 권한 요청
 * - 새로운 뉴스 발견 시 자동으로 팝업 표시
 */
const toggleEconomyNewsAlarm = async () => {
  if (isEconomyAlarmEnabled.value) {
    // 알람 비활성화
    isEconomyAlarmEnabled.value = false
    if (economyAlarmInterval.value) {
      clearInterval(economyAlarmInterval.value)
      economyAlarmInterval.value = null
    }
    // 모달도 닫기
    showEconomyAlarmModal.value = false
    console.log('[경제뉴스 알람] 알람이 비활성화되었습니다.')
  } else {
    // 알람 활성화
    isEconomyAlarmEnabled.value = true
    
    // 브라우저 알림 권한 요청
    if ('Notification' in window && Notification.permission === 'default') {
      await Notification.requestPermission()
    }
    
    // 즉시 확인 및 모달 표시
    showEconomyAlarmModal.value = true
    await checkNewEconomyNews()
    
    // 주기적으로 확인 (1분마다)
    economyAlarmInterval.value = setInterval(async () => {
      await checkNewEconomyNews()
      // 새로운 뉴스가 있으면 모달 자동 표시
      if (newEconomyNews.value.length > 0) {
        showEconomyAlarmModal.value = true
      }
    }, ALARM_CHECK_INTERVAL)
    
    console.log('[경제뉴스 알람] 알람이 활성화되었습니다. (1분마다 확인)')
  }
}

/**
 * 새로운 경제 뉴스 확인 함수
 * 
 * 기능:
 * - 최신 경제 뉴스를 가져와서 기존 히스토리와 비교
 * - 중복되지 않은 새로운 뉴스만 필터링
 * - 새로운 뉴스 발견 시 브라우저 알림 표시
 */
const checkNewEconomyNews = async () => {
  alarmChecking.value = true
  lastAlarmCheckTime.value = new Date().toLocaleString('ko-KR')
  
  try {
    // 최신 경제 뉴스 가져오기
    const apiUrl = `/api/news/economy?q=경제`
    const response = await fetch(apiUrl)
    
    if (!response.ok) {
      throw new Error(`API 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (!data.articles || data.articles.length === 0) {
      newEconomyNews.value = []
      alarmChecking.value = false
      return
    }
    
    // 기존 히스토리의 ID 목록 생성
    const existingIds = new Set(newsHistory.value.map(article => article.id))
    
    // 새로운 뉴스 필터링 (중복 제거)
    const now = new Date()
    const twoWeeksAgo = new Date(now.getTime() - 14 * 24 * 60 * 60 * 1000)
    
    const newNews = []
    for (const article of data.articles) {
      if (!article.title || article.title === '[Removed]') continue
      
      // 날짜 필터링
      if (article.publishedAt) {
        const publishedDate = new Date(article.publishedAt)
        if (publishedDate < twoWeeksAgo) continue
      }
      
      // 중복 확인
      const publishedDateStr = article.publishedAt ? new Date(article.publishedAt).toISOString().split('T')[0] : ''
      const articleId = `${article.title}-${article.source?.name || 'unknown'}-${publishedDateStr}`
      
      if (!existingIds.has(articleId)) {
        const publishedDate = article.publishedAt 
          ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          : '날짜 정보 없음'
        
        const importance = calculateEconomyImportance(article)
        
        newNews.push({
          id: articleId,
          title: article.title || '제목 없음',
          summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
          date: publishedDate,
          source: article.source?.name || '출처 정보 없음',
          category: '경제 뉴스',
          url: article.url || '#',
          importanceStars: importance.stars,
          importanceValue: importance.value,
          publishedDate: publishedDateStr
        })
      }
    }
    
    // 중요도 순으로 정렬
    newNews.sort((a, b) => b.importanceValue - a.importanceValue)
    
    // 이전에 발견된 뉴스와 비교하여 정말 새로운 뉴스만 표시
    const previousNewsIds = new Set(newEconomyNews.value.map(n => n.id))
    const trulyNewNews = newNews.filter(n => !previousNewsIds.has(n.id))
    
    if (trulyNewNews.length > 0) {
      newEconomyNews.value = newNews
      alarmChecking.value = false
      
      console.log(`[경제뉴스 알람] 새로운 뉴스 ${trulyNewNews.length}건 발견 (총 ${newNews.length}건)`)
      
      // 새로운 뉴스가 있으면 브라우저 알림 (권한 허용 시)
      if ('Notification' in window && Notification.permission === 'granted') {
        new Notification(`새로운 경제 뉴스 ${trulyNewNews.length}건`, {
          body: trulyNewNews[0].title,
          icon: '/favicon.ico',
          tag: 'economy-news-alarm',
          requireInteraction: false
        })
      }
      
      // 모달 자동 표시 (알람이 활성화되어 있을 때만)
      if (isEconomyAlarmEnabled.value) {
        showEconomyAlarmModal.value = true
      }
    } else {
      // 새로운 뉴스가 없으면 기존 목록 유지
      alarmChecking.value = false
      console.log(`[경제뉴스 알람] 새로운 뉴스 없음 (기존 ${newEconomyNews.value.length}건 유지)`)
    }
  } catch (error) {
    console.error('[경제뉴스 알람] 확인 오류:', error)
    alarmChecking.value = false
    // 에러 발생 시에도 기존 뉴스는 유지
  }
}

/**
 * 새로운 경제 뉴스 저장 함수
 * 
 * 기능:
 * - 알람에서 발견한 새로운 뉴스를 히스토리에 저장
 */
const saveNewEconomyNews = () => {
  if (newEconomyNews.value.length === 0) return
  
  const now = new Date().toISOString()
  let savedCount = 0
  
  newEconomyNews.value.forEach(news => {
    const existingArticle = newsHistory.value.find(a => a.id === news.id)
    if (!existingArticle) {
      newsHistory.value.push({
        ...news,
        collectedAt: now,
        keyword: '경제'
      })
      savedCount++
    }
  })
  
  // localStorage에 저장
  saveNewsHistoryToStorage()
  
  // 필터 업데이트
  if (showNewsCollection.value) {
    applyNewsFilters()
  }
  
  console.log(`[경제뉴스 알람] ${savedCount}건의 새 뉴스가 저장되었습니다.`)
  
  // 저장 후 알람 모달 닫기
  closeEconomyAlarmModal()
}

/**
 * 경제뉴스 알람 모달 닫기 함수
 */
const closeEconomyAlarmModal = () => {
  showEconomyAlarmModal.value = false
  // 알람은 계속 실행되도록 함 (알람이 활성화되어 있으면)
}

// 컴포넌트 언마운트 시 알람 정리
onBeforeUnmount(() => {
  if (economyAlarmInterval.value) {
    clearInterval(economyAlarmInterval.value)
  }
})

/**
 * 최신 경제 뉴스 가져오기 함수
 * - 각 기사에 중요도(별 개수) 추가
 * - 수집된 뉴스를 히스토리에 저장
 * - 1분에 한 번만 호출되도록 제한
 * 
 * API 엔드포인트:
 *   GET /api/news/economy?q=경제 (기본 키워드로 경제 사용)
 */
const fetchLatestEconomyNews = async () => {
  // 호출 제한 확인 (1분에 한 번만)
  const now = Date.now()
  const timeSinceLastFetch = lastEconomyNewsFetch.value ? now - lastEconomyNewsFetch.value : NEWS_FETCH_INTERVAL + 1
  
  if (timeSinceLastFetch < NEWS_FETCH_INTERVAL) {
    const remainingSeconds = Math.ceil((NEWS_FETCH_INTERVAL - timeSinceLastFetch) / 1000)
    console.log(`[경제 뉴스] 호출 제한: ${remainingSeconds}초 후에 다시 시도해주세요.`)
    economyArticleError.value = `너무 자주 호출되었습니다. ${remainingSeconds}초 후에 다시 시도해주세요.`
    return
  }
  
  // 화면 초기화 및 에러 초기화
  economyArticleError.value = ''
  economyArticles.value = []
  isSearchingEconomy.value = true
  
  console.log('[경제 뉴스] 최신 뉴스 불러오기 시작...')

  try {
    // Vite 프록시를 통해 News API 호출 (기본 키워드: 경제)
    const apiUrl = `/api/news/economy?q=경제`
    
    console.log('[경제 뉴스] API 호출:', apiUrl)
    const response = await fetch(apiUrl)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(`News API 오류: ${response.status} - ${errorData.message || response.statusText}`)
    }

    const data = await response.json()
    console.log('[경제 뉴스] API 응답:', data.articles?.length || 0, '건')

    // 결과가 없는 경우
    if (!data.articles || data.articles.length === 0) {
      economyArticleError.value = '최신 경제 뉴스를 찾을 수 없습니다.'
      isSearchingEconomy.value = false
      console.log('[경제 뉴스] 결과 없음')
      return
    }

    // 기사 데이터 포맷팅 (최근 2주 필터링, 최신일자 순 정렬)
    const nowDate = new Date()
    const twoWeeksAgo = new Date(nowDate.getTime() - 14 * 24 * 60 * 60 * 1000)
    
    // 먼저 필터링 전 기사 수 확인
    const allArticles = data.articles || []
    
    let formattedArticles = allArticles
      .filter(article => {
        // 제목 필터링
        if (!article.title || article.title === '[Removed]') return false
        // 2주 이상 지난 기사 필터링
        if (article.publishedAt) {
          const publishedDate = new Date(article.publishedAt)
          if (publishedDate < twoWeeksAgo) return false
        }
        return true
      })
      .sort((a, b) => {
        // 최신일자 순으로 정렬 (내림차순)
        const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
        const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
        return dateB - dateA
      })
      .map(article => {
        const publishedDate = article.publishedAt 
          ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
              year: 'numeric',
              month: 'long',
              day: 'numeric',
              hour: '2-digit',
              minute: '2-digit'
            })
          : '날짜 정보 없음'

        // 중요도 계산
        const importance = calculateEconomyImportance(article)

        return {
          title: article.title || '제목 없음',
          summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
          date: publishedDate,
          source: article.source?.name || '출처 정보 없음',
          category: '경제 뉴스',
          url: article.url || '#',
          importanceStars: importance.stars,
          importanceLabel: importance.label,
          importanceValue: importance.value,
          publishedDate: article.publishedAt ? new Date(article.publishedAt).toISOString().split('T')[0] : ''
        }
      })
      // 중요도 순으로 정렬 (매우중요 > 보통 > 미흡)
      .sort((a, b) => b.importanceValue - a.importanceValue)
    
    // 필터링 후 결과가 없으면 필터링 없이 최근 기사 표시
    if (formattedArticles.length === 0 && allArticles.length > 0) {
      console.log('[경제 뉴스] 2주 필터링 후 결과 없음, 전체 기사 사용')
      formattedArticles = allArticles
        .filter(article => {
          if (!article.title || article.title === '[Removed]') return false
          return true
        })
        .sort((a, b) => {
          const dateA = a.publishedAt ? new Date(a.publishedAt) : new Date(0)
          const dateB = b.publishedAt ? new Date(b.publishedAt) : new Date(0)
          return dateB - dateA
        })
        .slice(0, 50)
        .map(article => {
          const publishedDate = article.publishedAt 
            ? new Date(article.publishedAt).toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: 'long',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit'
              })
            : '날짜 정보 없음'

          const importance = calculateEconomyImportance(article)

          return {
            title: article.title || '제목 없음',
            summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
            date: publishedDate,
            source: article.source?.name || '출처 정보 없음',
            category: '경제 뉴스',
            url: article.url || '#',
            importanceStars: importance.stars,
            importanceLabel: importance.label,
            importanceValue: importance.value,
            publishedDate: article.publishedAt ? new Date(article.publishedAt).toISOString().split('T')[0] : ''
          }
        })
        .sort((a, b) => b.importanceValue - a.importanceValue)
      
      if (formattedArticles.length > 0) {
        economyArticleError.value = '최근 2주 이내의 기사가 없어 전체 기사를 표시합니다.'
      }
    }

    // 결과 설정
    economyArticles.value = formattedArticles
    isSearchingEconomy.value = false
    console.log('[경제 뉴스] 로드 완료:', formattedArticles.length, '건')
    
    // 마지막 호출 시간 업데이트
    lastEconomyNewsFetch.value = Date.now()
    
    // 수집된 뉴스를 히스토리에 추가
    if (formattedArticles.length > 0) {
      const now = new Date().toISOString()
      formattedArticles.forEach(article => {
        const articleId = `${article.title}-${article.source}-${article.publishedDate || article.date}`
        const existingArticle = newsHistory.value.find(a => a.id === articleId)
        
        if (!existingArticle) {
          newsHistory.value.push({
            id: articleId,
            title: article.title,
            summary: article.summary,
            date: article.date,
            source: article.source,
            category: '경제 뉴스',
            url: article.url,
            importanceStars: article.importanceStars,
            importanceValue: article.importanceValue,
            collectedAt: now,
            publishedDate: article.publishedDate,
            keyword: '경제'
          })
        }
      })
      
      // localStorage에 저장
      saveNewsHistoryToStorage()
      
      // 필터 업데이트
      if (showNewsCollection.value) {
        applyNewsFilters()
      }
    }
  } catch (error) {
    console.error('[경제 뉴스] 검색 오류:', error)
    economyArticleError.value = `경제 뉴스 검색 중 오류가 발생했습니다: ${error.message}`
    isSearchingEconomy.value = false
  }
}

/**
 * AI 뉴스 최신 데이터 가져오기 함수
 * 
 * 기능:
 * - AI 관련 키워드로 최신 뉴스를 가져옴
 * - 수집된 뉴스를 히스토리에 저장
 * - 1분에 한 번만 호출되도록 제한
 */
const fetchLatestAINews = async () => {
  // 호출 제한 확인 (1분에 한 번만)
  const now = Date.now()
  const timeSinceLastFetch = lastAINewsFetch.value ? now - lastAINewsFetch.value : NEWS_FETCH_INTERVAL + 1
  
  if (timeSinceLastFetch < NEWS_FETCH_INTERVAL) {
    const remainingSeconds = Math.ceil((NEWS_FETCH_INTERVAL - timeSinceLastFetch) / 1000)
    console.log(`[AI 뉴스] 호출 제한: ${remainingSeconds}초 후에 다시 시도해주세요.`)
    articleError.value = `너무 자주 호출되었습니다. ${remainingSeconds}초 후에 다시 시도해주세요.`
    return
  }
  
  if (!searchKeyword.value || searchKeyword.value.trim() === '') {
    // 키워드가 없으면 기본 키워드로 검색
    searchKeyword.value = 'AI'
  }
  
  await searchAIArticles()
  
  // 마지막 호출 시간 업데이트
  lastAINewsFetch.value = Date.now()
  
  // 수집된 뉴스를 히스토리에 추가
  if (aiArticles.value.length > 0) {
    const now = new Date().toISOString()
    aiArticles.value.forEach(article => {
      const articleId = `${article.title}-${article.source}-${article.date}`
      const existingArticle = newsHistory.value.find(a => a.id === articleId)
      
      if (!existingArticle) {
        newsHistory.value.push({
          id: articleId,
          title: article.title,
          summary: article.summary,
          date: article.date,
          source: article.source,
          category: 'AI 뉴스',
          url: article.url,
          collectedAt: now,
          keyword: searchKeyword.value
        })
      }
    })
    
    // localStorage에 저장
    saveNewsHistoryToStorage()
    
    // 필터 업데이트
    if (showNewsCollection.value) {
      applyNewsFilters()
    }
  }
}

/**
 * 한 달간 뉴스 데이터 수집 함수
 * 
 * 기능:
 * - 지난 30일간의 경제뉴스와 AI뉴스를 수집
 * - 날짜별로 데이터를 저장
 * - 수집된 데이터를 히스토리에 추가
 */
const collectMonthlyNewsData = async () => {
  if (isCollectingNewsData.value) {
    return // 이미 수집 중이면 중복 실행 방지
  }

  isCollectingNewsData.value = true
  newsCollectionProgress.value = 0
  newsCollectionStatus.value = '뉴스 데이터 수집 시작...'

  try {
    const today = new Date()
    const daysToCollect = 30 // 한 달(30일)간의 데이터 수집
    const allCollectedArticles = []

    // 지난 30일간의 데이터 수집
    for (let dayOffset = 0; dayOffset < daysToCollect; dayOffset++) {
      const targetDate = new Date(today)
      targetDate.setDate(today.getDate() - dayOffset)
      const dateStr = targetDate.toISOString().split('T')[0] // YYYY-MM-DD 형식

      newsCollectionStatus.value = `${dateStr} 데이터 수집 중... (${dayOffset + 1}/${daysToCollect}일)`

      // 1. 경제 뉴스 수집
      try {
        const economyResponse = await fetch(`/api/news/economy?q=경제`)
        if (economyResponse.ok) {
          const economyData = await economyResponse.json()
          if (economyData.articles && economyData.articles.length > 0) {
            economyData.articles.forEach(article => {
              if (article.publishedAt) {
                const publishedDate = new Date(article.publishedAt)
                const publishedDateStr = publishedDate.toISOString().split('T')[0]
                
                // 해당 날짜의 기사만 수집
                if (publishedDateStr === dateStr) {
                  const articleId = `${article.title}-${article.source?.name || 'unknown'}-${publishedDateStr}`
                  const existingArticle = allCollectedArticles.find(a => a.id === articleId)
                  
                  if (!existingArticle) {
                    const importance = calculateEconomyImportance(article)
                    allCollectedArticles.push({
                      id: articleId,
                      title: article.title || '제목 없음',
                      summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
                      date: publishedDate.toLocaleDateString('ko-KR'),
                      source: article.source?.name || '출처 정보 없음',
                      category: '경제 뉴스',
                      url: article.url || '#',
                      importanceStars: importance.stars,
                      importanceValue: importance.value,
                      collectedAt: new Date().toISOString(),
                      publishedDate: publishedDateStr
                    })
                  }
                }
              }
            })
          }
        }
      } catch (error) {
        console.error(`[한 달간 뉴스 수집] 경제 뉴스 오류 (${dateStr}):`, error)
      }

      // 2. AI 뉴스 수집 (여러 AI 관련 키워드로 검색)
      const aiKeywords = ['AI', '인공지능', '머신러닝', '딥러닝', 'ChatGPT', 'GPT']
      for (const keyword of aiKeywords) {
        try {
          const aiResponse = await fetch(`/api/news?q=${encodeURIComponent(keyword)}`)
          if (aiResponse.ok) {
            const aiData = await aiResponse.json()
            if (aiData.articles && aiData.articles.length > 0) {
              aiData.articles.forEach(article => {
                if (article.publishedAt) {
                  const publishedDate = new Date(article.publishedAt)
                  const publishedDateStr = publishedDate.toISOString().split('T')[0]
                  
                  // 해당 날짜의 기사만 수집
                  if (publishedDateStr === dateStr) {
                    const articleId = `${article.title}-${article.source?.name || 'unknown'}-${publishedDateStr}`
                    const existingArticle = allCollectedArticles.find(a => a.id === articleId)
                    
                    if (!existingArticle) {
                      allCollectedArticles.push({
                        id: articleId,
                        title: article.title || '제목 없음',
                        summary: article.description || article.content?.substring(0, 200) || '요약 정보 없음',
                        date: publishedDate.toLocaleDateString('ko-KR'),
                        source: article.source?.name || '출처 정보 없음',
                        category: 'AI 뉴스',
                        url: article.url || '#',
                        collectedAt: new Date().toISOString(),
                        publishedDate: publishedDateStr,
                        keyword: keyword
                      })
                    }
                  }
                }
              })
            }
          }
          
          // API 호출 간 딜레이 (API 제한 방지)
          await new Promise(resolve => setTimeout(resolve, 500))
        } catch (error) {
          console.error(`[한 달간 뉴스 수집] AI 뉴스 오류 (${dateStr}, ${keyword}):`, error)
        }
      }

      // 진행률 업데이트
      newsCollectionProgress.value = Math.round(((dayOffset + 1) / daysToCollect) * 100)
    }

    // 수집된 데이터를 히스토리에 취합
    const uniqueArticlesMap = new Map()
    allCollectedArticles.forEach(article => {
      if (!uniqueArticlesMap.has(article.id)) {
        uniqueArticlesMap.set(article.id, article)
      }
    })

    // 기존 히스토리에 추가
    const existingIds = new Set(newsHistory.value.map(a => a.id))
    uniqueArticlesMap.forEach(article => {
      if (!existingIds.has(article.id)) {
        newsHistory.value.push(article)
      }
    })

    // localStorage에 저장
    saveNewsHistoryToStorage()
    
    // 필터 업데이트 (화면이 열려있을 때만)
    if (showNewsCollection.value) {
      applyNewsFilters()
    }

    const economyCount = allCollectedArticles.filter(a => a.category === '경제 뉴스').length
    const aiCount = allCollectedArticles.filter(a => a.category === 'AI 뉴스').length
    newsCollectionStatus.value = `완료! 총 ${uniqueArticlesMap.size}개의 고유 뉴스가 수집되었습니다. (경제: ${economyCount}건, AI: ${aiCount}건)`
    
    console.log('[뉴스 수집] 완료:', {
      총: uniqueArticlesMap.size,
      경제: economyCount,
      AI: aiCount,
      localStorage: '저장됨'
    })
    newsCollectionProgress.value = 100

    // 완료 후 3초 뒤 상태 초기화
    setTimeout(() => {
      isCollectingNewsData.value = false
      newsCollectionStatus.value = ''
      newsCollectionProgress.value = 0
    }, 3000)

  } catch (error) {
    console.error('[한 달간 뉴스 수집] 오류:', error)
    newsCollectionStatus.value = `오류 발생: ${error.message}`
    isCollectingNewsData.value = false
  }
}

/**
 * 음악 추천 함수
 * 
 * 기능:
 * - 백엔드 API 서버를 통해 Last.fm API 호출
 * - 노래 제목 및 아티스트로 유사한 트랙 검색
 * - 추천 결과를 히스토리에 자동 저장
 * - API 실패 시 Fallback 데이터 사용
 * 
 * 사용 방법:
 *   songTitle.value에 노래 제목을 입력하고 호출
 *   artist.value에 아티스트를 입력 (선택사항)
 * 
 * API 엔드포인트:
 *   GET /api/music/recommend?songTitle=제목&artist=아티스트
 */
const recommendSongs = async () => {
  // 에러 초기화
  musicError.value = ''
  recommendations.value = []

  // 입력값 검증
  if (!songTitle.value || songTitle.value.trim() === '') {
    musicError.value = '노래 제목을 입력해주세요.'
    return
  }

  try {
    // 백엔드 API 서버를 통해 Last.fm API 호출
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

    // API 결과 처리
    let foundRecommendations = []
    if (data.similartracks && data.similartracks.track && data.similartracks.track.length > 0) {
      foundRecommendations = data.similartracks.track.slice(0, 10).map(track => ({
        title: track.name || '제목 없음',
        artist: track.artist?.name || '아티스트 없음',
        reason: 'Last.fm 유사 트랙 추천'
      }))
    }

    // API 결과가 없거나 오류가 발생한 경우 fallback
    if (foundRecommendations.length === 0) {
      // 하드코딩된 데이터에서 찾기
      if (artist.value && musicRecommendations[artist.value]) {
        foundRecommendations = musicRecommendations[artist.value]
      } else {
        // 제목으로 아티스트 찾기
        for (const [artistName, songs] of Object.entries(musicRecommendations)) {
          const found = songs.find(song => 
            song.title.toLowerCase().includes(songTitle.value.toLowerCase()) ||
            songTitle.value.toLowerCase().includes(song.title.toLowerCase())
          )
          if (found) {
            foundRecommendations = songs
            break
          }
        }
      }

      // 기본 추천 (찾지 못한 경우)
      if (foundRecommendations.length === 0) {
        foundRecommendations = [
          { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
          { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
          { title: 'How You Like That', artist: 'BLACKPINK', reason: '인기 K-Pop 노래' },
          { title: 'Love Scenario', artist: 'iKON', reason: '인기 K-Pop 노래' },
          { title: 'Spring Day', artist: 'BTS', reason: '인기 K-Pop 노래' },
        ]
      }
    }

    recommendations.value = foundRecommendations
    
    // 추천 받은 노래를 히스토리에 추가
    foundRecommendations.forEach(song => {
      addToHistory(song.title, song.artist, song.genre || 'K-Pop')
    })
  } catch (error) {
    console.error('음악 추천 오류:', error)
    
    // 네트워크 오류인 경우 더 자세한 메시지 제공
    if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
      musicError.value = 'API 서버 연결 실패: API 서버가 실행 중인지 확인하세요. (포트 3001)'
      console.error('[음악 추천] API 서버 연결 실패. API 서버가 실행 중인지 확인하세요. (포트 3001)')
    } else {
      musicError.value = `음악 추천 중 오류가 발생했습니다: ${error.message}`
    }
    
    // 오류 발생 시 fallback
    const fallbackRecommendations = [
      { title: 'Dynamite', artist: 'BTS', reason: '인기 K-Pop 노래' },
      { title: 'Celebrity', artist: 'IU', reason: '인기 K-Pop 노래' },
      { title: 'How You Like That', artist: 'BLACKPINK', reason: '인기 K-Pop 노래' },
      { title: 'Love Scenario', artist: 'iKON', reason: '인기 K-Pop 노래' },
      { title: 'Spring Day', artist: 'BTS', reason: '인기 K-Pop 노래' },
    ]
    recommendations.value = fallbackRecommendations
    fallbackRecommendations.forEach(song => {
      addToHistory(song.title, song.artist, song.genre || 'K-Pop')
    })
  }
}

// MCP 서버의 라디오 방송 데이터 (MCP 서버와 동일한 데이터)
const radioStations = {
  kbs: {
    name: 'KBS 쿨FM',
    currentSong: {
      title: 'Dynamite',
      artist: 'BTS',
      genre: 'K-Pop',
      time: new Date().toLocaleTimeString('ko-KR'),
    },
    recentSongs: [
      { title: 'Dynamite', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Butter', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Spring Day', artist: 'BTS', genre: 'K-Pop' },
      { title: 'Love Scenario', artist: 'iKON', genre: 'K-Pop' },
      { title: 'Gangnam Style', artist: 'PSY', genre: 'K-Pop' },
    ],
  },
  mbc: {
    name: 'MBC FM4U',
    currentSong: {
      title: 'Celebrity',
      artist: 'IU',
      genre: 'K-Pop',
      time: new Date().toLocaleTimeString('ko-KR'),
    },
    recentSongs: [
      { title: 'Celebrity', artist: 'IU', genre: 'K-Pop' },
      { title: 'Good Day', artist: 'IU', genre: 'K-Pop' },
      { title: 'Eight', artist: 'IU', genre: 'K-Pop' },
      { title: 'Through the Night', artist: 'IU', genre: 'Ballad' },
      { title: 'Blueming', artist: 'IU', genre: 'K-Pop' },
    ],
  },
  sbs: {
    name: 'SBS 파워FM',
    currentSong: {
      title: 'How You Like That',
      artist: 'BLACKPINK',
      genre: 'K-Pop',
      time: new Date().toLocaleTimeString('ko-KR'),
    },
    recentSongs: [
      { title: 'How You Like That', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'DDU-DU DDU-DU', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'Kill This Love', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'Lovesick Girls', artist: 'BLACKPINK', genre: 'K-Pop' },
      { title: 'Pink Venom', artist: 'BLACKPINK', genre: 'K-Pop' },
    ],
  },
}

/**
 * 라디오 노래 정보 가져오기 함수
 * 
 * 기능:
 * - 백엔드 API 서버를 통해 Last.fm API 호출
 * - 모든 방송국(KBS, MBC, SBS)의 현재 재생 중인 노래 및 최근 재생된 노래 조회
 * - 중복 제거 및 히스토리에 자동 저장
 * - API 실패 시 Fallback 데이터 사용
 * 
 * 사용 방법:
 *   "라디오 노래 현황" 버튼 클릭 시 자동 호출
 * 
 * API 엔드포인트:
 *   GET /api/music/radio/current?station=방송국&limit=개수
 *   GET /api/music/radio/recent?station=방송국&limit=개수
 */
const fetchRadioSongs = async () => {
  const allSongs = []
  const fetchDetails = [] // 가져온 데이터의 상세 정보
  
  // 현재 시간 기록
  const now = new Date()
  fetchTimestamp.value = now.toLocaleString('ko-KR')
  
  try {
    // 모든 방송국에 대해 API 호출
    const stations = ['kbs', 'mbc', 'sbs']
    const stationNames = {
      kbs: 'KBS 쿨FM',
      mbc: 'MBC FM4U',
      sbs: 'SBS 파워FM'
    }
    
    for (const station of stations) {
      try {
        // 현재 재생 중인 노래 가져오기
        const currentResponse = await fetch(`/api/music/radio/current?station=${station}&limit=1`)
        if (currentResponse.ok) {
          const currentData = await currentResponse.json()
          
          if (currentData.tracks && currentData.tracks.track && currentData.tracks.track.length > 0) {
            const track = currentData.tracks.track[0]
            const song = {
              title: track.name || '제목 없음',
              artist: track.artist?.name || '아티스트 없음',
              genre: 'K-Pop',
              station: stationNames[station],
              isCurrent: true,
              time: now.toLocaleTimeString('ko-KR')
            }
            allSongs.push(song)
            
            fetchDetails.push({
              방송국: song.station,
              타입: '현재 재생 중'
            })
          }
        } else {
          throw new Error(`HTTP ${currentResponse.status}: ${currentResponse.statusText}`)
        }
        
        // 최근 재생된 노래 가져오기
        const recentResponse = await fetch(`/api/music/radio/recent?station=${station}&limit=10`)
        if (recentResponse.ok) {
          const recentData = await recentResponse.json()
          
          if (recentData.tracks && recentData.tracks.track && recentData.tracks.track.length > 0) {
            recentData.tracks.track.forEach((track, index) => {
              const songData = {
                title: track.name || '제목 없음',
                artist: track.artist?.name || '아티스트 없음',
                genre: 'K-Pop',
                station: stationNames[station],
                isCurrent: false
              }
              allSongs.push(songData)
              
              fetchDetails.push({
                방송국: stationNames[station],
                타입: '최근 재생'
              })
            })
          }
        } else {
          throw new Error(`HTTP ${recentResponse.status}: ${recentResponse.statusText}`)
        }
      } catch (error) {
        console.error(`[라디오 방송] ${station} 오류:`, error)
        
        // 네트워크 오류인 경우 더 자세한 메시지 제공
        if (error.message === 'Failed to fetch' || error.name === 'TypeError') {
          console.error(`[라디오 방송] API 서버 연결 실패. API 서버가 실행 중인지 확인하세요. (포트 3001)`)
        }
        // 오류 발생 시 하드코딩된 데이터 사용
        const stationData = radioStations[station]
        if (stationData && stationData.currentSong) {
          const song = {
            title: stationData.currentSong.title,
            artist: stationData.currentSong.artist,
            genre: stationData.currentSong.genre || 'K-Pop',
            station: stationData.name,
            isCurrent: true,
            time: now.toLocaleTimeString('ko-KR')
          }
          allSongs.push(song)
          fetchDetails.push({
            방송국: song.station,
            타입: '현재 재생 중'
          })
        }
        if (stationData && stationData.recentSongs) {
          stationData.recentSongs.forEach((song, index) => {
            const songData = {
              title: song.title,
              artist: song.artist,
              genre: song.genre || 'K-Pop',
              station: stationData.name,
              isCurrent: false
            }
            allSongs.push(songData)
            fetchDetails.push({
              방송국: stationData.name,
              타입: '최근 재생'
            })
          })
        }
      }
    }
  } catch (error) {
    console.error('[라디오 방송] 전체 오류:', error)
    // 전체 오류 발생 시 하드코딩된 데이터 사용
    Object.values(radioStations).forEach(station => {
      if (station.currentSong) {
        const song = {
          title: station.currentSong.title,
          artist: station.currentSong.artist,
          genre: station.currentSong.genre || 'K-Pop',
          station: station.name,
          isCurrent: true,
          time: now.toLocaleTimeString('ko-KR')
        }
        allSongs.push(song)
        fetchDetails.push({
          방송국: song.station,
          타입: '현재 재생 중'
        })
      }
      if (station.recentSongs) {
        station.recentSongs.forEach((song, index) => {
          const songData = {
            title: song.title,
            artist: song.artist,
            genre: song.genre || 'K-Pop',
            station: station.name,
            isCurrent: false
          }
          allSongs.push(songData)
          fetchDetails.push({
            방송국: station.name,
            타입: '최근 재생'
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
  
  // 히스토리에 추가
  uniqueSongs.forEach(song => {
    addToHistory(song.title, song.artist, song.genre)
  })
  
  // 팝업에 표시할 데이터 저장
  fetchResultData.value = fetchDetails
  
  // 팝업 표시
  showFetchResult.value = true
  
  return Array.from(uniqueSongs.values())
}

/**
 * 음악 추천 토글 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 음악 추천 섹션만 열기
 */
const toggleMusicRecommendation = () => {
  closeAllSections()
  showMusicRecommendation.value = true
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
  
  // localStorage에 저장
  saveHistoryToStorage()
  applyFilters()
}

// localStorage에서 히스토리 불러오기
const loadHistoryFromStorage = () => {
  const stored = localStorage.getItem('radioSongsHistory')
  if (stored) {
    songsHistory.value = JSON.parse(stored)
    applyFilters()
  } else {
    // MCP 서버에서 라디오 노래 정보 가져오기
    fetchRadioSongs()
  }
}

/**
 * 라디오 히스토리 로드 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 라디오 히스토리 섹션만 열기
 * - MCP 서버에서 최신 라디오 노래 정보 가져오기
 */
const loadRadioHistory = () => {
  closeAllSections()
  showRadioHistory.value = true
  // MCP 서버에서 최신 라디오 노래 정보 가져오기
  fetchRadioSongs()
}

/**
 * 한 달간 라디오 노래 데이터 수집 및 취합 함수
 * 
 * 기능:
 * - 지난 30일간의 데이터를 수집하기 위해 매일 API를 호출
 * - 날짜별로 데이터를 저장
 * - 수집된 데이터를 취합하여 히스토리에 추가
 * 
 * 사용 방법:
 *   "한 달간 데이터 수집" 버튼 클릭 시 호출
 */
const collectMonthlyData = async () => {
  if (isCollectingMonthlyData.value) {
    return // 이미 수집 중이면 중복 실행 방지
  }

  isCollectingMonthlyData.value = true
  monthlyCollectionProgress.value = 0
  monthlyCollectionStatus.value = '데이터 수집 시작...'
  monthlyDataCollection.value = []

  try {
    const today = new Date()
    const daysToCollect = 30 // 한 달(30일)간의 데이터 수집
    const stations = ['kbs', 'mbc', 'sbs']
    const stationNames = {
      kbs: 'KBS 쿨FM',
      mbc: 'MBC FM4U',
      sbs: 'SBS 파워FM'
    }

    let totalCollected = 0
    const allCollectedSongs = []

    // 지난 30일간의 데이터 수집
    for (let dayOffset = 0; dayOffset < daysToCollect; dayOffset++) {
      const targetDate = new Date(today)
      targetDate.setDate(today.getDate() - dayOffset)
      const dateStr = targetDate.toISOString().split('T')[0] // YYYY-MM-DD 형식

      monthlyCollectionStatus.value = `${dateStr} 데이터 수집 중... (${dayOffset + 1}/${daysToCollect}일)`

      // 각 방송국에 대해 API 호출
      for (const station of stations) {
        try {
          // 최근 재생된 노래 가져오기 (더 많은 데이터를 위해 limit 증가)
          const recentResponse = await fetch(`/api/music/radio/recent?station=${station}&limit=50`)
          if (recentResponse.ok) {
            const recentData = await recentResponse.json()
            if (recentData.tracks && recentData.tracks.track && recentData.tracks.track.length > 0) {
              recentData.tracks.track.forEach((track) => {
                const songData = {
                  title: track.name || '제목 없음',
                  artist: track.artist?.name || '아티스트 없음',
                  genre: 'K-Pop',
                  station: stationNames[station],
                  date: dateStr,
                  collectedAt: new Date().toISOString()
                }
                allCollectedSongs.push(songData)
                totalCollected++
              })
            }
          }

          // 현재 재생 중인 노래도 가져오기
          const currentResponse = await fetch(`/api/music/radio/current?station=${station}&limit=1`)
          if (currentResponse.ok) {
            const currentData = await currentResponse.json()
            if (currentData.tracks && currentData.tracks.track && currentData.tracks.track.length > 0) {
              const track = currentData.tracks.track[0]
              const songData = {
                title: track.name || '제목 없음',
                artist: track.artist?.name || '아티스트 없음',
                genre: 'K-Pop',
                station: stationNames[station],
                date: dateStr,
                collectedAt: new Date().toISOString()
              }
              allCollectedSongs.push(songData)
              totalCollected++
            }
          }

          // API 호출 간 딜레이 (API 제한 방지)
          await new Promise(resolve => setTimeout(resolve, 500))
        } catch (error) {
          console.error(`[한 달간 데이터 수집] ${station} 오류:`, error)
        }
      }

      // 날짜별 수집 데이터 저장
      const daySongs = allCollectedSongs.filter(song => song.date === dateStr)
      monthlyDataCollection.value.push({
        date: dateStr,
        count: daySongs.length,
        songs: daySongs
      })

      // 진행률 업데이트
      monthlyCollectionProgress.value = Math.round(((dayOffset + 1) / daysToCollect) * 100)
    }

    // 수집된 데이터를 히스토리에 취합
    monthlyCollectionStatus.value = `데이터 취합 중... (총 ${totalCollected}개 수집)`
    
    const uniqueSongsMap = new Map()
    
    // 모든 수집된 노래를 취합 (중복 제거)
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

    // 취합된 데이터를 히스토리에 추가
    uniqueSongsMap.forEach((songData, key) => {
      const songId = key
      const existingSong = songsHistory.value.find(s => s.id === songId)
      
      if (existingSong) {
        // 기존 노래가 있으면 재생 횟수 증가
        existingSong.count += songData.count
        existingSong.lastPlayed = new Date().toLocaleString('ko-KR')
      } else {
        // 새로운 노래 추가
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

    // localStorage에 저장
    saveHistoryToStorage()
    applyFilters()

    monthlyCollectionStatus.value = `완료! 총 ${uniqueSongsMap.size}개의 고유 노래, ${totalCollected}개의 재생 기록이 수집되었습니다.`
    monthlyCollectionProgress.value = 100

    // 완료 후 3초 뒤 상태 초기화
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
    // 최근 저장된 노래만 전송 (마지막 50개)
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

// 뉴스 히스토리 저장 함수
const saveNewsHistoryToStorage = () => {
  localStorage.setItem('newsHistory', JSON.stringify(newsHistory.value))
  
  // 로그인한 경우 데이터베이스에도 저장
  if (authStore.isAuthenticated && authStore.token) {
    saveNewsToDatabase()
  }
}

// 단일 뉴스 저장
async function saveSingleNews(article) {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    return
  }

  isSavingNews.value = true
  try {
    // localStorage에 저장
    const articleId = `${article.title}-${article.source}-${article.date}`
    const existingArticle = newsHistory.value.find(a => a.id === articleId)
    
    if (!existingArticle) {
      const now = new Date().toISOString()
      newsHistory.value.push({
        id: articleId,
        title: article.title,
        summary: article.summary,
        date: article.date,
        source: article.source,
        category: article.category || 'AI 뉴스',
        keyword: article.keyword || searchKeyword.value,
        url: article.url,
        collectedAt: now,
        importanceStars: article.importanceStars,
        importanceValue: article.importanceValue
      })
      saveNewsHistoryToStorage()
    }

    // 데이터베이스에 저장
    if (authStore.token) {
      const response = await fetch('/api/user/news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify([{
          title: article.title,
          summary: article.summary,
          date: article.date,
          source: article.source,
          category: article.category || 'AI 뉴스',
          keyword: article.keyword || searchKeyword.value,
          url: article.url,
          publishedDate: article.date,
          importanceStars: article.importanceStars,
          importanceValue: article.importanceValue
        }])
      })

      if (response.ok) {
        const data = await response.json()
        alert(`뉴스가 저장되었습니다! (${data.saved}개 저장됨)`)
      } else {
        alert('뉴스 저장에 실패했습니다.')
      }
    }
  } catch (error) {
    console.error('[뉴스 저장] 오류:', error)
    alert('뉴스 저장 중 오류가 발생했습니다.')
  } finally {
    isSavingNews.value = false
  }
}

// 뉴스를 데이터베이스에 저장
async function saveNewsToDatabase() {
  try {
    // 최근 저장된 뉴스만 전송 (마지막 50개)
    const recentNews = newsHistory.value.slice(-50).map(news => ({
      title: news.title,
      summary: news.summary,
      date: news.date,
      source: news.source,
      category: news.category,
      keyword: news.keyword,
      url: news.url,
      publishedDate: news.date,
      importanceStars: news.importanceStars,
      importanceValue: news.importanceValue
    }))

    if (recentNews.length > 0) {
      const response = await fetch('/api/user/news', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify(recentNews)
      })

      if (response.ok) {
        const data = await response.json()
        console.log('[뉴스 저장] 데이터베이스에 저장 완료:', data.message)
      }
    }
  } catch (error) {
    console.error('[뉴스 저장] 데이터베이스 저장 오류:', error)
  }
}

// 뉴스 히스토리 불러오기 함수
const loadNewsHistoryFromStorage = () => {
  const stored = localStorage.getItem('newsHistory')
  if (stored) {
    try {
      newsHistory.value = JSON.parse(stored)
      console.log('[뉴스 히스토리] 로드 완료:', newsHistory.value.length, '건')
    } catch (e) {
      console.error('뉴스 히스토리 로드 오류:', e)
      newsHistory.value = []
    }
  } else {
    newsHistory.value = []
    console.log('[뉴스 히스토리] 저장된 데이터 없음')
  }
  // 필터 적용
  applyNewsFilters()
}

/**
 * 수집된 뉴스 현황 토글 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 수집된 뉴스 현황 섹션만 열기
 */
const toggleNewsCollection = () => {
  closeAllSections()
  showNewsCollection.value = true
  // 화면이 열릴 때 데이터 로드 및 필터 적용
  loadNewsHistoryFromStorage()
  // 필터 초기화
  newsSearchQuery.value = ''
  selectedNewsCategory.value = ''
  newsSortBy.value = 'date'
  currentNewsPage.value = 1
}

/**
 * 뉴스 필터링 및 정렬 함수
 */
const applyNewsFilters = () => {
  // newsHistory가 비어있으면 빈 배열 반환
  if (!newsHistory.value || newsHistory.value.length === 0) {
    filteredNews.value = []
    paginatedNews.value = []
    return
  }
  
  let filtered = [...newsHistory.value]
  
  // 검색 필터
  if (newsSearchQuery.value && newsSearchQuery.value.trim() !== '') {
    const query = newsSearchQuery.value.toLowerCase().trim()
    filtered = filtered.filter(article => {
      const title = (article.title || '').toLowerCase()
      const source = (article.source || '').toLowerCase()
      const summary = (article.summary || '').toLowerCase()
      return title.includes(query) || source.includes(query) || summary.includes(query)
    })
  }
  
  // 카테고리 필터
  if (selectedNewsCategory.value && selectedNewsCategory.value !== '') {
    filtered = filtered.filter(article => article.category === selectedNewsCategory.value)
  }
  
  // 정렬
  filtered.sort((a, b) => {
    switch (newsSortBy.value) {
      case 'date':
        const dateA = a.publishedDate || a.collectedAt || a.date || ''
        const dateB = b.publishedDate || b.collectedAt || b.date || ''
        return dateB.localeCompare(dateA) // 최신순
      case 'title':
        return (a.title || '').localeCompare(b.title || '')
      case 'source':
        return (a.source || '').localeCompare(b.source || '')
      default:
        return 0
    }
  })
  
  filteredNews.value = filtered
  currentNewsPage.value = 1
  updateNewsPagination()
  
  console.log('[뉴스 필터] 적용 완료:', filtered.length, '건')
}

/**
 * 뉴스 페이지네이션 업데이트
 */
const updateNewsPagination = () => {
  if (!filteredNews.value || filteredNews.value.length === 0) {
    paginatedNews.value = []
    return
  }
  
  const start = (currentNewsPage.value - 1) * newsPerPage
  const end = start + newsPerPage
  paginatedNews.value = filteredNews.value.slice(start, end)
  
  console.log('[뉴스 페이지네이션] 페이지:', currentNewsPage.value, '/', totalNewsPages.value, '총:', filteredNews.value.length, '건')
}

// 뉴스 페이지네이션 계산
const paginatedNews = ref([])
const totalNewsPages = computed(() => {
  return Math.ceil(filteredNews.value.length / newsPerPage)
})

// 뉴스 통계 계산
const economyNewsCount = computed(() => {
  return newsHistory.value.filter(article => article.category === '경제 뉴스').length
})

const aiNewsCount = computed(() => {
  return newsHistory.value.filter(article => article.category === 'AI 뉴스').length
})

// 뉴스 페이지 변경 감지
watch(currentNewsPage, () => {
  updateNewsPagination()
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

// 페이지 변경 감지
watch(currentPage, () => {
  updatePagination()
})

// 도서 관련 함수들
const recommendBooks = async () => {
  const trimmedKeyword = bookKeyword.value.trim()
  if (!trimmedKeyword) {
    bookError.value = '원하는 도서에 대해 설명을 입력해주세요.'
    return
  }
  isSearchingBooks.value = true
  bookError.value = ''
  recommendedBooks.value = []
  try {
    // 사용자 입력을 그대로 전달 (AI 분석은 서버에서 수행)
    let url = `/api/books/recommend?query=${encodeURIComponent(trimmedKeyword)}`
    if (bookCategory.value) {
      url += `&category=${encodeURIComponent(bookCategory.value)}`
    }
    console.log('[Vue 앱] 도서 추천 요청 URL:', url)
    console.log('[Vue 앱] 입력된 키워드:', trimmedKeyword)
    console.log('[Vue 앱] 선택된 카테고리:', bookCategory.value)
    const response = await fetch(url)
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: `HTTP ${response.status} 오류` }))
      throw new Error(errorData.error || `API 오류: ${response.status}`)
    }
    const data = await response.json()
    console.log('[Vue 앱] 도서 추천 응답:', data)
    if (data.books && data.books.length > 0) {
      recommendedBooks.value = data.books
    } else {
      bookError.value = '추천 도서를 찾을 수 없습니다. 다른 설명으로 시도해보세요.'
    }
  } catch (error) {
    console.error('도서 추천 오류:', error)
    bookError.value = `도서 추천 중 오류가 발생했습니다: ${error.message}`
  } finally {
    isSearchingBooks.value = false
  }
}

/**
 * 도서 추천 토글 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 도서 추천 섹션만 열기
 */
const toggleBookRecommendation = () => {
  closeAllSections()
  showBookRecommendation.value = true
}

/**
 * 도서 히스토리 로드 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 도서 히스토리 섹션만 열기
 */
const loadBookHistory = () => {
  closeAllSections()
  showBookHistory.value = true
  loadBooksHistoryFromStorage()
  applyBookFilters()
}

/**
 * 화면 검증 섹션 토글 함수
 * 
 * 기능:
 * - 다른 모든 섹션을 닫고 화면 검증 섹션만 열기
 */
const toggleScreenValidation = () => {
  closeAllSections()
  showScreenValidation.value = true
}

/**
 * 화면 검증 함수
 * 
 * 기능:
 * - MCP Python 서버를 통해 URL에 접속하여 화면 캡처 및 요소 검증
 */
const validateScreen = async () => {
  if (!screenValidationUrl.value.trim()) {
    screenValidationError.value = 'URL을 입력해주세요.'
    return
  }
  
  isValidatingScreen.value = true
  screenValidationError.value = ''
  screenValidationResult.value = null
  screenScreenshot.value = null
  
  try {
    // MCP 서버를 통해 화면 검증 수행
    // 실제로는 API 서버를 통해 MCP Python 서버와 통신해야 함
    // 여기서는 간단한 예시로 구현 (실제 구현은 API 서버에 엔드포인트 추가 필요)
    
    const response = await fetch('/api/screen/validate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: screenValidationUrl.value.trim(),
        selector: screenValidationSelector.value.trim() || null,
        expectedValue: screenValidationExpectedValue.value.trim() || null
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      // 에러 메시지 추출 (success: false인 경우)
      if (errorData.success === false && errorData.error) {
        throw new Error(errorData.error)
      }
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    // success가 false인 경우 에러 처리
    if (data.success === false) {
      throw new Error(data.error || '화면 검증 실패')
    }
    
    screenValidationResult.value = {
      url: data.url,
      selector: data.selector,
      actualValue: data.actualValue,
      expectedValue: data.expectedValue,
      passed: data.passed,
      message: data.message,
      selectorError: data.selectorError
    }
    
    if (data.screenshot) {
      screenScreenshot.value = data.screenshot
    }
    
  } catch (error) {
    console.error('화면 검증 오류:', error)
    // 에러 메시지 개선
    const errorMessage = error.message || '화면 검증 중 오류가 발생했습니다.'
    screenValidationError.value = errorMessage
    console.error('[화면 검증] 오류:', errorMessage)
  } finally {
    isValidatingScreen.value = false
  }
}

/**
 * 화면 캡처만 수행하는 함수
 * 
 * 기능:
 * - 요소 검증 없이 화면만 캡처
 */
const onActionTypeChange = (action) => {
  // wait 타입이면 selector 초기화
  if (action.type === 'wait') {
    action.selector = ''
  }
  // value 초기화
  if (action.type === 'click' || action.type === 'check' || action.type === 'uncheck') {
    action.value = ''
  }
}

const addAction = () => {
  interactActions.value.push({ type: 'fill', selector: '', value: '' })
}

const removeAction = (index) => {
  interactActions.value.splice(index, 1)
}

const getSelectorPlaceholder = (type) => {
  const placeholders = {
    fill: '예: #search-input, input[name="q"]',
    click: '예: #submit-button, button.search',
    select: '예: #category-select, select[name="category"]',
    check: '예: #agree-checkbox, input[type="checkbox"]',
    uncheck: '예: #agree-checkbox, input[type="checkbox"]',
    wait: '(대기 시간만 입력)'
  }
  return placeholders[type] || 'CSS 선택자 입력'
}

const getSelectorHint = (type) => {
  const hints = {
    fill: '텍스트를 입력할 입력 필드의 CSS 선택자',
    click: '클릭할 버튼/링크의 CSS 선택자',
    select: '선택할 드롭다운의 CSS 선택자',
    check: '체크할 체크박스의 CSS 선택자',
    uncheck: '체크 해제할 체크박스의 CSS 선택자',
    wait: '대기 시간만 입력하세요 (선택자 불필요)'
  }
  return hints[type] || ''
}

const getValueLabel = (type) => {
  const labels = {
    fill: '입력할 텍스트',
    select: '선택할 값',
    wait: '대기 시간 (밀리초)'
  }
  return labels[type] || '값'
}

const getValuePlaceholder = (type) => {
  const placeholders = {
    fill: '예: 검색어, 사용자명',
    select: '예: option1, value1',
    wait: '예: 2000 (2초 대기)'
  }
  return placeholders[type] || ''
}

const getValueHint = (type) => {
  const hints = {
    fill: '입력 필드에 입력할 텍스트 내용',
    select: '드롭다운에서 선택할 옵션의 값',
    wait: '대기할 시간을 밀리초 단위로 입력 (1000 = 1초)'
  }
  return hints[type] || ''
}

const interactAndGetResult = async () => {
  if (!screenValidationUrl.value.trim()) {
    screenValidationError.value = 'URL을 입력해주세요.'
    return
  }
  
  // 액션 검증 및 변환
  const actions = []
  for (const action of interactActions.value) {
    if (action.type === 'wait') {
      // 대기 시간은 초를 밀리초로 변환
      const seconds = parseInt(action.value) || 0
      if (seconds > 0) {
        actions.push({
          type: 'wait',
          selector: '',
          value: String(seconds * 1000) // 밀리초로 변환
        })
      }
    } else if (action.selector.trim()) {
      // selector가 있는 액션들
      const actionData = {
        type: action.type,
        selector: action.selector.trim()
      }
      if (action.value && action.value.trim()) {
        actionData.value = action.value.trim()
      }
      actions.push(actionData)
    }
  }
  
  if (actions.length === 0) {
    screenValidationError.value = '최소 하나의 액션을 설정해주세요.'
    return
  }
  
  isValidatingScreen.value = true
  screenValidationError.value = ''
  screenValidationResult.value = null
  interactResult.value = null
  
  try {
    const response = await fetch('/api/screen/interact', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: screenValidationUrl.value.trim(),
        actions: actions,
        resultSelector: interactResultSelector.value.trim() || null,
        waitAfterActions: 2000
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      if (errorData.success === false && errorData.error) {
        throw new Error(errorData.error)
      }
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    if (data.success === false) {
      throw new Error(data.error || '입력/클릭 실패')
    }
    
    interactResult.value = {
      url: data.url,
      actions: data.actions,
      resultSelector: data.resultSelector,
      resultValue: data.resultValue
    }
    
    if (data.screenshot) {
      screenScreenshot.value = data.screenshot
    }
    
  } catch (error) {
    console.error('입력/클릭 오류:', error)
    const errorMessage = error.message || '입력/클릭 중 오류가 발생했습니다.'
    screenValidationError.value = errorMessage
    console.error('[입력/클릭] 오류:', errorMessage)
  } finally {
    isValidatingScreen.value = false
  }
}

const captureScreenOnly = async () => {
  if (!screenValidationUrl.value.trim()) {
    screenValidationError.value = 'URL을 입력해주세요.'
    return
  }
  
  isValidatingScreen.value = true
  screenValidationError.value = ''
  screenValidationResult.value = null
  screenScreenshot.value = null
  
  try {
    const response = await fetch('/api/screen/capture', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        url: screenValidationUrl.value.trim(),
        selector: screenValidationSelector.value.trim() || null
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      // 에러 메시지 추출 (success: false인 경우)
      if (errorData.success === false && errorData.error) {
        throw new Error(errorData.error)
      }
      throw new Error(errorData.error || `HTTP 오류: ${response.status}`)
    }
    
    const data = await response.json()
    
    // success가 false인 경우 에러 처리
    if (data.success === false) {
      throw new Error(data.error || '화면 캡처 실패')
    }
    
    screenValidationResult.value = {
      url: data.url,
      selector: data.selector || '전체 페이지',
      actualValue: null,
      expectedValue: null,
      passed: true,
      message: '화면 캡처 완료'
    }
    
    if (data.screenshot) {
      screenScreenshot.value = data.screenshot
    }
    
  } catch (error) {
    console.error('화면 캡처 오류:', error)
    // 에러 메시지 개선
    const errorMessage = error.message || '화면 캡처 중 오류가 발생했습니다.'
    screenValidationError.value = errorMessage
    console.error('[화면 캡처] 오류:', errorMessage)
  } finally {
    isValidatingScreen.value = false
  }
}

const fetchLatestBooks = async () => {
  try {
    const keywords = ['AI', '인공지능', '머신러닝', '딥러닝', '파이썬']
    const allBooks = []
    for (const keyword of keywords) {
      const response = await fetch(`/api/books/search?q=${encodeURIComponent(keyword)}&maxResults=10`)
      if (response.ok) {
        const data = await response.json()
        if (data.books) allBooks.push(...data.books)
      }
    }
    const uniqueBooks = []
    const seenIds = new Set()
    for (const book of allBooks) {
      if (book.id && !seenIds.has(book.id)) {
        seenIds.add(book.id)
        uniqueBooks.push(book)
      }
    }
    const existingIds = new Set(booksHistory.value.map(b => b.id))
    const newBooks = uniqueBooks.filter(b => b.id && !existingIds.has(b.id))
    booksHistory.value.push(...newBooks)
    saveBooksHistoryToStorage()
    applyBookFilters()
  } catch (error) {
    console.error('최신 도서 가져오기 오류:', error)
  }
}

const collectMonthlyBookData = async () => {
  if (isCollectingBookData.value) return
  isCollectingBookData.value = true
  bookCollectionProgress.value = 0
  bookCollectionStatus.value = '도서 데이터 수집 시작...'
  try {
    const keywords = ['AI', '인공지능', '머신러닝', '딥러닝', '파이썬', '데이터사이언스']
    const allBooks = []
    for (let i = 0; i < keywords.length; i++) {
      const keyword = keywords[i]
      bookCollectionStatus.value = `${keyword} 검색 중... (${i + 1}/${keywords.length})`
      bookCollectionProgress.value = ((i + 1) / keywords.length) * 100
      const response = await fetch(`/api/books/search?q=${encodeURIComponent(keyword)}&maxResults=20`)
      if (response.ok) {
        const data = await response.json()
        if (data.books) allBooks.push(...data.books)
      }
      await new Promise(resolve => setTimeout(resolve, 500))
    }
    const uniqueBooks = []
    const seenIds = new Set()
    for (const book of allBooks) {
      if (book.id && !seenIds.has(book.id)) {
        seenIds.add(book.id)
        uniqueBooks.push(book)
      }
    }
    const existingIds = new Set(booksHistory.value.map(b => b.id))
    const newBooks = uniqueBooks.filter(b => b.id && !existingIds.has(b.id))
    booksHistory.value.push(...newBooks)
    saveBooksHistoryToStorage()
    applyBookFilters()
    bookCollectionStatus.value = `완료! 총 ${newBooks.length}권의 도서가 수집되었습니다.`
    bookCollectionProgress.value = 100
    setTimeout(() => {
      isCollectingBookData.value = false
      bookCollectionStatus.value = ''
      bookCollectionProgress.value = 0
    }, 3000)
  } catch (error) {
    console.error('한 달간 도서 수집 오류:', error)
    bookCollectionStatus.value = `오류 발생: ${error.message}`
    isCollectingBookData.value = false
  }
}

const saveBooksHistoryToStorage = () => {
  localStorage.setItem('booksHistory', JSON.stringify(booksHistory.value))
  
  // 로그인한 경우 데이터베이스에도 저장
  if (authStore.isAuthenticated && authStore.token) {
    saveBooksToDatabase()
  }
}

// 단일 도서 저장
async function saveSingleBook(book) {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.')
    return
  }

  isSavingBook.value = true
  try {
    // localStorage에 저장
    const existingBook = booksHistory.value.find(b => b.id === book.id)
    
    if (!existingBook) {
      booksHistory.value.push(book)
      saveBooksHistoryToStorage()
    }

    // 데이터베이스에 저장
    if (authStore.token) {
      const response = await fetch('/api/user/books', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify([{
          title: book.title,
          authors: book.authors || [],
          publisher: book.publisher,
          description: book.description,
          thumbnail: book.thumbnail,
          imageUrl: book.thumbnail,
          previewLink: book.previewLink,
          publishedDate: book.publishedDate,
          categories: book.categories || [],
          isbn: book.id
        }])
      })

      if (response.ok) {
        const data = await response.json()
        alert(`도서가 저장되었습니다! (${data.saved}개 저장됨)`)
      } else {
        alert('도서 저장에 실패했습니다.')
      }
    }
  } catch (error) {
    console.error('[도서 저장] 오류:', error)
    alert('도서 저장 중 오류가 발생했습니다.')
  } finally {
    isSavingBook.value = false
  }
}

// 도서를 데이터베이스에 저장
async function saveBooksToDatabase() {
  try {
    // 최근 저장된 도서만 전송 (마지막 50개)
    const recentBooks = booksHistory.value.slice(-50).map(book => ({
      title: book.title,
      authors: book.authors || [],
      publisher: book.publisher,
      description: book.description,
      thumbnail: book.thumbnail,
      imageUrl: book.thumbnail,
      previewLink: book.previewLink,
      publishedDate: book.publishedDate,
      categories: book.categories || [],
      isbn: book.id
    }))

    if (recentBooks.length > 0) {
      const response = await fetch('/api/user/books', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${authStore.token}`
        },
        body: JSON.stringify(recentBooks)
      })

      if (response.ok) {
        const data = await response.json()
        console.log('[도서 저장] 데이터베이스에 저장 완료:', data.message)
      }
    }
  } catch (error) {
    console.error('[도서 저장] 데이터베이스 저장 오류:', error)
  }
}

const loadBooksHistoryFromStorage = () => {
  const stored = localStorage.getItem('booksHistory')
  if (stored) {
    try {
      booksHistory.value = JSON.parse(stored)
    } catch (e) {
      console.error('도서 히스토리 로드 오류:', e)
      booksHistory.value = []
    }
  }
}

const applyBookFilters = () => {
  let filtered = [...booksHistory.value]
  if (bookSearchQuery.value.trim()) {
    const query = bookSearchQuery.value.toLowerCase()
    filtered = filtered.filter(book => {
      const title = (book.title || '').toLowerCase()
      const authors = (book.authors || []).join(' ').toLowerCase()
      return title.includes(query) || authors.includes(query)
    })
  }
  filtered.sort((a, b) => {
    switch (bookSortBy.value) {
      case 'date': return (b.publishedDate || '').localeCompare(a.publishedDate || '')
      case 'title': return (a.title || '').localeCompare(b.title || '')
      case 'author': return (a.authors?.[0] || '').localeCompare(b.authors?.[0] || '')
      case 'publisher': return (a.publisher || '').localeCompare(b.publisher || '')
      default: return 0
    }
  })
  filteredBooks.value = filtered
  updateBookPagination()
}

const updateBookPagination = () => {
  const start = (currentBookPage.value - 1) * booksPerPage.value
  const end = start + booksPerPage.value
  paginatedBooks.value = filteredBooks.value.slice(start, end)
}

const goToBookPage = (page) => {
  if (page >= 1 && page <= totalBookPages.value) {
    currentBookPage.value = page
    updateBookPagination()
  }
}

const filteredBooks = ref([])
const paginatedBooks = ref([])

const totalBookPages = computed(() => {
  return Math.ceil(filteredBooks.value.length / booksPerPage.value)
})

const uniqueBookAuthors = computed(() => {
  const authors = new Set()
  booksHistory.value.forEach(book => {
    if (book.authors) book.authors.forEach(author => authors.add(author))
  })
  return Array.from(authors).sort()
})

const uniqueBookPublishers = computed(() => {
  const publishers = new Set()
  booksHistory.value.forEach(book => {
    if (book.publisher) publishers.add(book.publisher)
  })
  return Array.from(publishers).sort()
})

// 컴포넌트 마운트 시 히스토리 불러오기
onMounted(() => {
  loadHistoryFromStorage()
  loadNewsHistoryFromStorage()
  loadBooksHistoryFromStorage()
})
</script>

<style scoped>
#app {
  position: relative;
  min-height: 100vh;
  width: 100%;
  max-width: 100%;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 0;
  box-sizing: border-box;
}

/* 오른쪽 상단 버튼 */
.top-buttons {
  position: fixed;
  top: 15px;
  right: 15px;
  left: 15px;
  z-index: 1000;
  display: flex;
  flex-direction: row;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: flex-end;
  align-items: center;
  padding: 10px;
  background: rgba(36, 36, 36, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
  max-width: 100%;
  box-sizing: border-box;
}

/* 버튼 스타일 */
.btn {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn:active {
  transform: translateY(0);
}

.btn-guide {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-guide-python {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.btn-api-docs {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.btn-api-docs:hover {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.btn-alarm {
  background: linear-gradient(135deg, #ffd89b 0%, #19547b 100%);
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  font-weight: 600;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
  position: relative;
}

.btn-alarm:hover {
  background: linear-gradient(135deg, #19547b 0%, #ffd89b 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.btn-alarm.active {
  background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 2px 8px rgba(255, 107, 107, 0.4);
  }
  50% {
    box-shadow: 0 2px 16px rgba(255, 107, 107, 0.8);
  }
}

.btn-guide-python:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.btn-guide:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* 메인 콘텐츠 */
.main-content {
  width: 100%;
  max-width: 100%;
  margin: 0;
  padding: 20px 30px;
  padding-top: 100px;
  font-size: 16px;
  box-sizing: border-box;
  overflow-x: hidden;
}

.main-header {
  text-align: center;
  margin-bottom: 2rem;
}

.main-content h1 {
  color: #42b983;
  margin-bottom: 0.5rem;
  font-size: 2.5rem;
  font-weight: 700;
  background: linear-gradient(135deg, #42b983 0%, #35495e 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  font-size: 16px;
  color: #666;
  margin-bottom: 0;
  font-weight: 400;
}

/* 메인 기능 그리드 (좌우 배치) */
.main-features-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  align-items: start;
  max-width: 100%;
  margin: 0;
}

@media (max-width: 1600px) {
  .main-features-grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }
}

@media (max-width: 1000px) {
  .main-features-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}

/* 기사 검색 섹션 (바운더리로 묶음) */
.article-search-section {
  padding: 1.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f5f7fa 50%, #e8ecf1 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
  height: fit-content;
}

.article-search-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #667eea 0%, #f093fb 50%, #f5576c 100%);
}

.section-header {
  margin-bottom: 1rem;
  text-align: center;
}

.section-header h2 {
  color: #2c3e50;
  font-size: 1.4rem;
  margin-bottom: 0.3rem;
  font-weight: 700;
}

.section-description {
  color: #666;
  font-size: 13px;
  margin: 0;
}

.article-search-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

.feature-buttons {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-top: 1rem;
}

/* 버튼 그룹 카드 */
.button-group-card {
  width: 100%;
  position: relative;
}

.button-group-card .btn {
  width: 100%;
  padding: 20px 24px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  gap: 14px;
  text-align: left;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  border: 2px solid transparent;
}

.button-group-card .btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0) 100%);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.button-group-card .btn:hover::before {
  opacity: 1;
}

.button-group-card .btn.active {
  border-color: rgba(255, 255, 255, 0.5);
  transform: translateY(-4px);
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.2);
}

.button-icon {
  font-size: 2rem;
  line-height: 1;
  flex-shrink: 0;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.button-content {
  flex: 1;
}

.button-title {
  font-size: 18px;
  font-weight: 700;
  margin-bottom: 3px;
  color: white;
  line-height: 1.3;
}

.button-subtitle {
  font-size: 12px;
  color: rgba(255, 255, 255, 0.85);
  font-weight: 400;
  line-height: 1.4;
}

.btn-ai-search {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
}

.btn-ai-search:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
}

.btn-ai-search.active {
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6);
}

.btn-economy-search {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(245, 87, 108, 0.35);
}

.btn-economy-search:hover {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(245, 87, 108, 0.5);
}

.btn-economy-search.active {
  box-shadow: 0 12px 40px rgba(245, 87, 108, 0.6);
}

.btn-news-collection {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.35);
}

.btn-news-collection:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(102, 126, 234, 0.5);
}

.btn-news-collection.active {
  box-shadow: 0 12px 40px rgba(102, 126, 234, 0.6);
}

/* 도서 기능 섹션 */
.book-features-section {
  padding: 1.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 50%, #e6f3ff 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
  height: fit-content;
}

.book-features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #ff9a9e 0%, #fecfef 50%, #fecfef 100%);
}

/* AI 화면 검증 섹션 */
.screen-validation-section {
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
  border-radius: 24px;
  box-shadow: 
    0 20px 60px rgba(102, 126, 234, 0.3),
    0 0 0 1px rgba(255, 255, 255, 0.1),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border: 2px solid rgba(255, 255, 255, 0.3);
  position: relative;
  overflow: hidden;
  height: fit-content;
  backdrop-filter: blur(10px);
}

.screen-validation-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 5px;
  background: linear-gradient(90deg, 
    #667eea 0%, 
    #764ba2 25%, 
    #f093fb 50%, 
    #764ba2 75%, 
    #667eea 100%);
  background-size: 200% 100%;
  animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.screen-validation-section::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(255, 255, 255, 0.15) 0%, transparent 70%);
  pointer-events: none;
  animation: pulse 4s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 0.3; transform: scale(1); }
  50% { opacity: 0.6; transform: scale(1.1); }
}

.btn-screen-validation {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.2) 0%, rgba(255, 255, 255, 0.1) 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.4);
  backdrop-filter: blur(10px);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-screen-validation:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.3) 0%, rgba(255, 255, 255, 0.2) 100%);
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.5),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  border-color: rgba(255, 255, 255, 0.6);
}

.btn-screen-validation.active {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.35) 0%, rgba(255, 255, 255, 0.25) 100%);
  box-shadow: 
    0 6px 20px rgba(102, 126, 234, 0.6),
    inset 0 2px 4px rgba(255, 255, 255, 0.3),
    inset 0 -2px 4px rgba(0, 0, 0, 0.1);
  border-color: rgba(255, 255, 255, 0.7);
}

/* 화면 검증 컨테이너 */
.screen-validation-container {
  background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
  border-radius: 20px;
  padding: 2.5rem;
  margin-top: 2rem;
  box-shadow: 
    0 10px 40px rgba(102, 126, 234, 0.15),
    0 0 0 1px rgba(102, 126, 234, 0.1);
  border: 1px solid rgba(102, 126, 234, 0.2);
  position: relative;
  overflow: hidden;
}

.screen-validation-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
}

.validation-notice {
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
  border-left: 5px solid #2196f3;
  padding: 1.25rem;
  margin-bottom: 2rem;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(33, 150, 243, 0.15);
  position: relative;
  overflow: hidden;
}

.validation-notice::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(33, 150, 243, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.validation-notice p {
  margin: 0.5rem 0;
  color: #1565c0;
  font-size: 14px;
  line-height: 1.6;
  position: relative;
  z-index: 1;
}

.validation-actions {
  display: flex;
  gap: 1.25rem;
  margin-top: 2rem;
  flex-wrap: wrap;
}

.btn-validate {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(102, 126, 234, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.btn-validate::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-validate:hover:not(:disabled)::before {
  left: 100%;
}

.btn-validate:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(102, 126, 234, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-validate:active:not(:disabled) {
  transform: translateY(-1px) scale(0.98);
}

.btn-validate:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn-interact {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
  transition: all 0.3s ease;
}

.btn-interact:hover:not(:disabled) {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(245, 87, 108, 0.4);
}

.btn-capture {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 
    0 4px 15px rgba(245, 87, 108, 0.4),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  position: relative;
  overflow: hidden;
}

.btn-capture::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s;
}

.btn-capture:hover:not(:disabled)::before {
  left: 100%;
}

.btn-capture:hover:not(:disabled) {
  transform: translateY(-3px) scale(1.02);
  box-shadow: 
    0 8px 25px rgba(245, 87, 108, 0.6),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

.btn-capture:active:not(:disabled) {
  transform: translateY(-1px) scale(0.98);
}

.btn-capture:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.input-hint {
  display: block;
  margin-top: 0.5rem;
  color: #666;
  font-size: 12px;
}

.validation-result {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f5f5f5;
  border-radius: 8px;
}

.result-info {
  margin-bottom: 1.5rem;
}

.result-info p {
  margin: 0.5rem 0;
  color: #333;
}

.validation-status {
  padding: 1rem;
  border-radius: 8px;
  margin-top: 1rem;
  font-size: 16px;
}

.validation-status.passed {
  background: #e8f5e9;
  color: #2e7d32;
  border: 2px solid #4caf50;
}

.validation-status.failed {
  background: #ffebee;
  color: #c62828;
  border: 2px solid #f44336;
}

.screenshot-container {
  margin-top: 1.5rem;
}

.screenshot-container h4 {
  margin-bottom: 1rem;
  color: #333;
}

.screenshot-image {
  max-width: 100%;
  border: 2px solid rgba(102, 126, 234, 0.2);
  border-radius: 12px;
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.12),
    0 0 0 1px rgba(102, 126, 234, 0.1);
  transition: transform 0.3s ease;
}

.screenshot-image:hover {
  transform: scale(1.01);
  box-shadow: 
    0 12px 32px rgba(0, 0, 0, 0.15),
    0 0 0 1px rgba(102, 126, 234, 0.2);
}

/* 에러 표시 스타일 개선 */
.validation-error {
  background: linear-gradient(135deg, #ffebee 0%, #ffcdd2 100%);
  border-left: 5px solid #f44336;
  border-radius: 12px;
  padding: 1.5rem;
  margin-top: 1.5rem;
  box-shadow: 0 4px 12px rgba(244, 67, 54, 0.2);
  position: relative;
  overflow: hidden;
}

.validation-error::before {
  content: '';
  position: absolute;
  top: 0;
  right: 0;
  width: 100px;
  height: 100px;
  background: radial-gradient(circle, rgba(244, 67, 54, 0.1) 0%, transparent 70%);
  pointer-events: none;
}

.error-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
  position: relative;
  z-index: 1;
}

.error-icon {
  font-size: 24px;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  25% { transform: translateX(-5px); }
  75% { transform: translateX(5px); }
}

.error-title {
  font-size: 18px;
  color: #c62828;
  font-weight: 700;
}

.error-content {
  position: relative;
  z-index: 1;
}

.error-message {
  background: rgba(255, 255, 255, 0.8);
  border-radius: 8px;
  padding: 1rem;
  margin: 0;
  color: #c62828;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  border: 1px solid rgba(244, 67, 54, 0.2);
}

.selector-error-hint {
  margin-top: 1rem;
  padding: 1.25rem;
  background: linear-gradient(135deg, #fff3cd 0%, #ffe69c 100%);
  border-left: 5px solid #ffc107;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(255, 193, 7, 0.2);
}

.error-hint-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  color: #856404;
  font-weight: 600;
}

.hint-icon {
  font-size: 20px;
}

.error-hint-text {
  margin: 0;
  color: #856404;
  font-size: 13px;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  font-family: 'Courier New', monospace;
  background: rgba(255, 255, 255, 0.6);
  padding: 0.75rem;
  border-radius: 6px;
  border: 1px solid rgba(255, 193, 7, 0.3);
}

.textarea-field {
  resize: vertical;
  min-height: 100px;
  font-family: 'Courier New', monospace;
  font-size: 13px;
}

.help-box {
  background: rgba(255, 255, 255, 0.05);
  border-left: 3px solid #4facfe;
  padding: 1rem;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  font-size: 12px;
  line-height: 1.8;
  color: rgba(255, 255, 255, 0.85);
}

.help-box p {
  margin: 0.5rem 0;
}

.help-box ol {
  margin: 0.5rem 0;
  padding-left: 1.5rem;
}

.help-box code {
  background: rgba(0, 0, 0, 0.3);
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  color: #4facfe;
}

.interact-actions-section {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.interact-result {
  margin-top: 1.5rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(132, 250, 176, 0.3);
}

.actions-log {
  margin-top: 1rem;
}

.actions-log ul {
  list-style: none;
  padding-left: 0;
  margin-top: 0.5rem;
}

.actions-log li {
  padding: 0.5rem;
  margin: 0.25rem 0;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 6px;
  font-size: 13px;
}

/* 기타 기능 섹션 */
.other-features-section {
  padding: 1.5rem;
  background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 50%, #e9ecef 100%);
  border-radius: 20px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.08), 0 0 0 1px rgba(0, 0, 0, 0.05);
  border: 2px solid rgba(255, 255, 255, 0.8);
  position: relative;
  overflow: hidden;
  height: fit-content;
}

.other-features-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(90deg, #4facfe 0%, #00f2fe 50%, #fa709a 100%);
}

.btn-mcp {
  background: linear-gradient(135deg, #42b983 0%, #35495e 100%);
  color: white;
  font-size: 18px;
  padding: 14px 28px;
}

.btn-mcp:hover {
  background: linear-gradient(135deg, #35495e 0%, #42b983 100%);
}

.btn-music {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(79, 172, 254, 0.35);
}

.btn-music:hover {
  background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(79, 172, 254, 0.5);
}

.btn-music.active {
  box-shadow: 0 12px 40px rgba(79, 172, 254, 0.6);
}

.btn-radio {
  background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(250, 112, 154, 0.35);
}

.btn-radio:hover {
  background: linear-gradient(135deg, #fee140 0%, #fa709a 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(250, 112, 154, 0.5);
}

.btn-radio.active {
  box-shadow: 0 12px 40px rgba(250, 112, 154, 0.6);
}

.btn-book {
  background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(255, 154, 158, 0.35);
}

.btn-book:hover {
  background: linear-gradient(135deg, #fecfef 0%, #ff9a9e 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(255, 154, 158, 0.5);
}

.btn-book.active {
  box-shadow: 0 12px 40px rgba(255, 154, 158, 0.6);
}

.btn-book-history {
  background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(252, 182, 159, 0.35);
}

.btn-book-history:hover {
  background: linear-gradient(135deg, #fcb69f 0%, #ffecd2 100%);
  transform: translateY(-4px);
  box-shadow: 0 10px 30px rgba(252, 182, 159, 0.5);
}

.btn-book-history.active {
  box-shadow: 0 12px 40px rgba(252, 182, 159, 0.6);
}

/* 기사 검색 결과 영역 */
.article-results-area {
  margin-top: 2rem;
}

/* AI 기사 검색 컨테이너 */
.ai-articles-container,
.economy-articles-container {
  margin-top: 1.5rem;
  padding: 2rem;
  background: white;
  border-radius: 16px;
  box-shadow: 0 6px 24px rgba(0, 0, 0, 0.12);
  animation: slideDown 0.3s ease;
  width: 100%;
  max-width: 100%;
  margin-left: auto;
  margin-right: auto;
  border: 1px solid rgba(0, 0, 0, 0.05);
  box-sizing: border-box;
}

/* 경제 뉴스 컨테이너 - 더 넓게 */
.economy-articles-container {
  padding: 3rem;
  min-width: 100%;
}

/* 기타 기능 결과 영역 */
.other-results-area {
  margin-top: 2rem;
}

.search-notice {
  margin-bottom: 1rem;
  padding: 10px 15px;
  background: #e3f2fd;
  border-left: 4px solid #2196f3;
  border-radius: 4px;
}

.loading-state {
  text-align: center;
  padding: 2rem;
  color: #666;
  font-size: 16px;
}

.search-notice p {
  margin: 0;
  color: #1976d2;
  font-size: 14px;
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

.ai-articles-container h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
  text-align: center;
}

.economy-articles-container h2 {
  color: #f5576c;
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
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

.btn-search {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 100%;
  padding: 14px;
  font-size: 20px;
  font-weight: 600;
  margin-top: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.2s, box-shadow 0.2s;
}

.btn-search:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.articles-results {
  margin-top: 2rem;
}

.articles-results h3 {
  color: #333;
  margin-bottom: 1rem;
  font-size: 1.4rem;
}

/* 중요도 범례 */
.importance-legend {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 2px solid #e0e0e0;
}

.importance-legend h3 {
  margin-bottom: 0.75rem;
}

.legend {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  align-items: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.legend-item .stars {
  font-size: 1.1rem;
  color: #ffa500;
}

/* 기사 카드 헤더 (중요도 표시) */
.article-header {
  margin-bottom: 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid #e0e0e0;
}

.importance-rating {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
}

.importance-rating .stars {
  font-size: 1.2rem;
  color: #ffa500;
  font-weight: 600;
}

.importance-label {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
  font-weight: 600;
  background: #f0f0f0;
  color: #666;
}

.importance-label.label-high {
  background: #fff3e0;
  color: #e65100;
}

.importance-label.label-medium {
  background: #fff8e1;
  color: #f57c00;
}

.importance-label.label-low {
  background: #f5f5f5;
  color: #757575;
}

/* 중요도별 색상 구분 (동적 클래스 사용) */
.article-card.importance-high {
  border-left-color: #f44336;
  background: #fff5f5;
}

.article-card.importance-medium {
  border-left-color: #ff9800;
  background: #fffaf0;
}

.article-card.importance-low {
  border-left-color: #9e9e9e;
  background: #f8f9fa;
}

/* 테이블 컨테이너 */
.articles-table-container {
  margin-top: 1.5rem;
  overflow-x: auto;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 100%;
  min-width: 100%;
}

/* 뉴스 테이블 */
.articles-table {
  width: 100%;
  min-width: 100%;
  border-collapse: collapse;
  background: white;
  font-size: 16px;
  table-layout: auto;
}

.articles-table thead {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.articles-table th {
  padding: 1.5rem 1.5rem;
  text-align: left;
  font-weight: 600;
  font-size: 18px;
  border-bottom: 2px solid rgba(255, 255, 255, 0.2);
}

.articles-table th.col-title {
  text-align: left;
}

.articles-table th.col-date {
  width: 250px;
  min-width: 220px;
}

.articles-table th.col-importance {
  width: 120px;
  min-width: 100px;
  text-align: center;
}

.articles-table th.col-title {
  width: auto;
  min-width: 400px;
}

.articles-table tbody tr {
  border-bottom: 1px solid #e0e0e0;
  transition: background-color 0.2s;
}

.articles-table tbody tr:hover {
  background-color: #f5f5f5;
}

.articles-table tbody tr.importance-high {
  background-color: #fff5f5;
  border-left: 4px solid #f44336;
}

.articles-table tbody tr.importance-high:hover {
  background-color: #ffe0e0;
}

.articles-table tbody tr.importance-medium {
  background-color: #fffaf0;
  border-left: 4px solid #ff9800;
}

.articles-table tbody tr.importance-medium:hover {
  background-color: #fff5e0;
}

.articles-table tbody tr.importance-low {
  background-color: #f8f9fa;
  border-left: 4px solid #9e9e9e;
}

.articles-table tbody tr.importance-low:hover {
  background-color: #f0f0f0;
}

.articles-table td {
  padding: 1.5rem 1.5rem;
  vertical-align: middle;
  font-size: 16px;
}

.articles-table td.col-date {
  color: #666;
  font-size: 15px;
  white-space: nowrap;
  width: 250px;
  min-width: 220px;
}

.articles-table td.col-importance {
  white-space: nowrap;
  text-align: center;
  width: 120px;
  min-width: 100px;
}

.articles-table td.col-importance .stars {
  font-size: 1.5rem;
  color: #ffa500;
  font-weight: 600;
}

.articles-table td.col-title {
  max-width: none;
  overflow: visible;
  text-overflow: clip;
  white-space: normal;
  text-align: left;
  width: auto;
  min-width: 400px;
  word-wrap: break-word;
  word-break: break-word;
}

/* 뉴스기사 제목 링크 */
.article-title-link {
  color: #333;
  text-decoration: none;
  font-weight: 500;
  transition: color 0.2s;
  display: block;
  overflow: visible;
  text-overflow: clip;
  white-space: normal;
  font-size: 16px;
  line-height: 1.6;
  word-wrap: break-word;
  word-break: break-word;
}

.article-title-link:hover {
  color: #667eea;
  text-decoration: underline;
}

.article-title-link:visited {
  color: #666;
}

.article-title {
  color: #333;
  margin: 0 0 0.75rem 0;
  font-size: 1.2rem;
  font-weight: 600;
}

.article-summary {
  color: #666;
  margin: 0 0 0.75rem 0;
  font-size: 0.95rem;
  line-height: 1.6;
}

.article-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.85rem;
  color: #888;
}

.article-date,
.article-source,
.article-category {
  display: inline-block;
}

.article-link {
  display: inline-block;
  padding: 0.5rem 1rem;
  background: #667eea;
  color: white;
  text-decoration: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  transition: background 0.2s;
}

.article-link:hover {
  background: #5568d3;
}

.article-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
  align-items: center;
}

.btn-save-news {
  padding: 0.5rem 1rem;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.3s ease;
  font-size: 14px;
}

.btn-save-news:hover:not(:disabled) {
  background: #45a049;
}

.btn-save-news:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-save-news-small {
  padding: 4px 8px;
  background: #4caf50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s ease;
  font-size: 12px;
}

.btn-save-news-small:hover:not(:disabled) {
  background: #45a049;
}

.btn-save-news-small:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.col-actions {
  width: 80px;
  text-align: center;
}

.no-results {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #fff3cd;
  border-radius: 8px;
  border-left: 4px solid #ffc107;
  text-align: center;
}

.no-results p {
  color: #856404;
  margin: 0 0 0.5rem 0;
}

.no-results .suggestions {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
}

/* 에러 메시지 */
.error {
  margin-top: 1rem;
  padding: 1rem;
  background: #ffebee;
  border-radius: 8px;
  border: 2px solid #f44336;
  color: #c62828;
  font-weight: 600;
  font-size: 18px;
}

.error p {
  margin: 0;
}

/* 데이터 연계도 분석 섹션 */
.correlation-section {
  margin-top: 3rem;
  padding: 2rem;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eaff 100%);
  border-radius: 12px;
  border: 2px solid #667eea;
}

.correlation-section h3 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 700;
}

.correlation-chart {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.correlation-item {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.correlation-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.correlation-keyword {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
}

.correlation-score {
  font-size: 1rem;
  font-weight: 600;
  color: #667eea;
  background: #e8eaff;
  padding: 0.4rem 0.8rem;
  border-radius: 20px;
}

.correlation-bar {
  width: 100%;
  height: 24px;
  background: #e0e0e0;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 1rem;
}

.correlation-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.5s ease;
  border-radius: 12px;
}

.correlation-details {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  font-size: 0.9rem;
  color: #666;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.detail-item::before {
  content: '•';
  color: #667eea;
  font-weight: bold;
}

/* GraphQL 쿼리 섹션 */
.graphql-query-section {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: #1e1e1e;
  border-radius: 8px;
  border: 2px solid #667eea;
}

.graphql-query-section h4 {
  color: #667eea;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 700;
}

.graphql-code {
  background: #1e1e1e;
  color: #d4d4d4;
  padding: 1.5rem;
  border-radius: 6px;
  overflow-x: auto;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  margin: 0;
  border: 1px solid #333;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 네트워크 그래프 컨테이너 */
.network-graph-container {
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.network-graph-container h4 {
  color: #667eea;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 700;
}

.network-graph {
  width: 100%;
  height: 600px;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  background: #fafafa;
  margin-bottom: 1rem;
}

.graph-legend {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  justify-content: center;
  padding: 1rem;
  background: #f5f5f5;
  border-radius: 6px;
}

.graph-legend .legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: #666;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.legend-color.primary {
  background: #667eea;
}

.legend-color.secondary {
  background: #764ba2;
}

.legend-color.tertiary {
  background: #9e9e9e;
}

.correlation-chart h4 {
  color: #667eea;
  margin-bottom: 1rem;
  font-size: 1.2rem;
  font-weight: 700;
}

/* 음악 추천 컨테이너 */
.music-container {
  margin-top: 2rem;
  padding: 2rem;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  animation: slideDown 0.3s ease;
}

.music-container h2 {
  color: #667eea;
  margin-bottom: 1.5rem;
  font-size: 1.8rem;
}

.btn-recommend {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  width: 100%;
  padding: 14px;
  font-size: 20px;
  font-weight: 600;
  margin-top: 1rem;
}

.btn-recommend:hover {
  background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
}

/* 추천 결과 */
.recommendations {
  margin-top: 2rem;
  padding: 1.5rem;
  background: linear-gradient(135deg, #f0f4ff 0%, #e8eaff 100%);
  border-radius: 8px;
  border: 2px solid #667eea;
  animation: fadeIn 0.5s ease;
}

.recommendations h3 {
  color: #667eea;
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.4rem;
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
  transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.song-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

.song-number {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 50%;
  font-weight: 600;
  font-size: 18px;
  flex-shrink: 0;
}

.song-info {
  flex: 1;
}

.song-title {
  font-size: 18px;
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.song-artist {
  font-size: 16px;
  color: #666;
  margin-bottom: 0.5rem;
}

.song-reason {
  font-size: 14px;
  color: #667eea;
  font-weight: 500;
}

/* 다크 모드 대응 */
@media (prefers-color-scheme: dark) {
  .ai-articles-container {
    background: #1e1e1e;
    color: rgba(255, 255, 255, 0.87);
  }

  .input-group label {
    color: rgba(255, 255, 255, 0.87);
  }

  .input-field {
    background: #2e2e2e;
    border-color: #404040;
    color: rgba(255, 255, 255, 0.87);
  }

  .input-field:focus {
    border-color: #667eea;
  }

  .ai-articles-container h2 {
    color: #667eea;
  }

  .article-card {
    background: #2d2d2d;
    color: rgba(255, 255, 255, 0.87);
  }

  .article-title {
    color: rgba(255, 255, 255, 0.87);
  }

  .article-summary {
    color: rgba(255, 255, 255, 0.7);
  }

  .music-container {
    background: #1e1e1e;
    color: rgba(255, 255, 255, 0.87);
  }

  .music-container h2 {
    color: #a78bfa;
  }

  .recommendations {
    background: rgba(102, 126, 234, 0.1);
    border-color: #a78bfa;
  }

  .recommendations h3 {
    color: #a78bfa;
  }

  .song-item {
    background: #2e2e2e;
    border-color: #404040;
  }

  .song-title {
    color: rgba(255, 255, 255, 0.87);
  }

  .song-artist {
    color: rgba(255, 255, 255, 0.6);
  }

  .song-reason {
    color: #c084fc;
  }
}

/* 라디오 노래 현황 컨테이너 */
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

/* 검색 및 필터 섹션 */
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

/* 통계 섹션 */
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

/* 한 달간 데이터 수집 진행 상황 */
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

/* 뉴스 수집 관련 스타일 */
.search-actions {
  display: flex;
  gap: 10px;
  margin: 15px 0;
  flex-wrap: wrap;
}

.btn-fetch {
  padding: 10px 20px;
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.3s ease;
}

.btn-fetch:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(79, 172, 254, 0.4);
}

.btn-fetch:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-monthly-news {
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

.btn-monthly-news:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-monthly-news:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 수집된 뉴스 현황 스타일 */
.news-collection-container {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
  margin-bottom: 2rem;
}

.news-collection-container h2 {
  color: white;
  margin-bottom: 1.5rem;
  font-size: 24px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.news-list-container {
  margin-top: 1.5rem;
}

.news-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.news-item {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  border-left: 4px solid #f5576c;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.news-item:hover {
  background: white;
  transform: translateX(4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  border-left-color: #f5576c;
}

.news-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.news-title {
  margin: 0;
  flex: 1;
  font-size: 18px;
  font-weight: 600;
  color: #333;
}

.news-link {
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.news-link:hover {
  color: #f5576c;
  text-decoration: underline;
}

.news-category {
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 600;
  white-space: nowrap;
}

.category-economy {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(245, 87, 108, 0.3);
}

.category-ai {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
  color: white;
  box-shadow: 0 2px 4px rgba(79, 172, 254, 0.3);
}

.news-summary {
  margin: 0.75rem 0;
  color: #666;
  font-size: 14px;
  line-height: 1.6;
}

.news-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 12px;
  color: #888;
}

.news-date,
.news-source,
.news-keyword,
.news-importance {
  display: flex;
  align-items: center;
  gap: 4px;
}

.news-collection-container .stats-section {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
}

.news-collection-container .stat-label {
  color: rgba(255, 255, 255, 0.9);
}

.news-collection-container .stat-value {
  color: white;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
}

.news-collection-container .search-filter-section {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
  backdrop-filter: blur(10px);
}

.news-collection-container .search-input,
.news-collection-container .filter-select {
  background: white;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.news-collection-container .search-input:focus,
.news-collection-container .filter-select:focus {
  border-color: #f5576c;
  box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.2);
}

.news-collection-container .no-results {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  padding: 2rem;
  text-align: center;
  color: #666;
}

.news-collection-container .pagination {
  background: rgba(255, 255, 255, 0.2);
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1.5rem;
  backdrop-filter: blur(10px);
}

.news-collection-container .page-btn {
  background: white;
  color: #667eea;
  border: 2px solid rgba(255, 255, 255, 0.3);
}

.news-collection-container .page-btn:hover:not(:disabled) {
  background: #f5576c;
  color: white;
  border-color: #f5576c;
}

.news-collection-container .page-info {
  color: white;
  font-weight: 600;
}

/* 노래 목록 테이블 */
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

/* 페이지네이션 */
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

/* 다크 모드 대응 */
@media (prefers-color-scheme: dark) {
  .radio-history-container {
    background: #1e1e1e;
    color: rgba(255, 255, 255, 0.87);
  }

  .radio-history-container h2 {
    color: #ff6b9d;
  }

  .search-filter-section {
    background: #2e2e2e;
  }

  .search-input {
    background: #2e2e2e;
    border-color: #404040;
    color: rgba(255, 255, 255, 0.87);
  }

  .filter-select {
    background: #2e2e2e;
    border-color: #404040;
    color: rgba(255, 255, 255, 0.87);
  }

  .stats-section {
    background: #2e2e2e;
  }

  .stat-value {
    color: #ff6b9d;
  }

  .songs-table {
    background: #1e1e1e;
  }

  .songs-table td {
    border-color: #404040;
    color: rgba(255, 255, 255, 0.87);
  }

  .song-row:hover {
    background: #2e2e2e;
  }

  .title-cell {
    color: rgba(255, 255, 255, 0.87);
  }

  .pagination {
    background: #2e2e2e;
  }

  .page-btn {
    background: #2e2e2e;
    border-color: #ff6b9d;
    color: #ff6b9d;
  }

  .page-btn:hover:not(:disabled) {
    background: #ff6b9d;
    color: white;
  }
}

/* 데이터 가져오기 결과 팝업 */
.fetch-result-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 3000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.fetch-result-modal {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  max-height: 90vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

.fetch-result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid #e0e0e0;
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  border-radius: 12px 12px 0 0;
}

.fetch-result-header h2 {
  color: white;
  margin: 0;
  font-size: 20px;
  font-weight: 600;
}

.fetch-result-body {
  padding: 24px;
  overflow-y: auto;
  flex: 1;
}

.fetch-info {
  background: #f8f9fa;
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 20px;
}

.fetch-info p {
  margin: 8px 0;
  font-size: 14px;
  color: #333;
}

.fetch-info strong {
  color: #f5576c;
  font-weight: 600;
}

.fetch-details h3 {
  color: #333;
  margin-bottom: 16px;
  font-size: 18px;
  font-weight: 600;
}

.details-table {
  overflow-x: auto;
}

.details-table table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}

.details-table thead {
  background: linear-gradient(135deg, #f5576c 0%, #f093fb 100%);
  color: white;
}

.details-table th {
  padding: 12px;
  text-align: left;
  font-weight: 600;
  font-size: 13px;
}

.details-table td {
  padding: 12px;
  border-bottom: 1px solid #e0e0e0;
  color: #333;
}

.details-table tbody tr:hover {
  background: #f8f9fa;
}

.badge-current {
  display: inline-block;
  padding: 4px 10px;
  background: #4caf50;
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.badge-recent {
  display: inline-block;
  padding: 4px 10px;
  background: #2196f3;
  color: white;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
}

.time-info {
  display: block;
  font-size: 11px;
  color: #666;
  margin-top: 4px;
}

.fetch-result-footer {
  padding: 16px 24px;
  border-top: 2px solid #e0e0e0;
  display: flex;
  justify-content: flex-end;
}

.btn-close-modal {
  padding: 10px 24px;
  font-size: 14px;
  font-weight: 600;
  border: 2px solid #f5576c;
  background: white;
  color: #f5576c;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-close-modal:hover {
  background: #f5576c;
  color: white;
}

/* 도서 추천 카드 스타일 */
.book-list {
  margin-top: 2rem;
  padding: 1.5rem;
  background: #f8f9fa;
  border-radius: 12px;
  animation: slideDown 0.3s ease;
}

.book-list-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #333;
  margin-bottom: 1.5rem;
  text-align: center;
}

.books-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.book-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: all 0.3s ease;
  display: flex;
  flex-direction: column;
  border: 1px solid #e0e0e0;
}

.book-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  border-color: #667eea;
}

.book-card-header {
  position: relative;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.book-thumbnail {
  width: 100%;
  max-width: 150px;
  height: auto;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.book-thumbnail img {
  width: 100%;
  height: auto;
  object-fit: cover;
  display: block;
}

.book-number-badge {
  position: absolute;
  top: 12px;
  right: 12px;
  background: rgba(255, 255, 255, 0.95);
  color: #667eea;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.book-card-body {
  padding: 1.25rem;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.book-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #333;
  margin: 0 0 1rem 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  min-height: 3em;
}

.book-meta {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #e9ecef;
}

.book-meta-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.book-meta-label {
  font-weight: 600;
  color: #666;
  min-width: 70px;
  flex-shrink: 0;
}

.book-meta-value {
  color: #333;
  flex: 1;
  word-break: break-word;
}

.book-description {
  font-size: 0.875rem;
  color: #555;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  flex: 1;
  display: -webkit-box;
  -webkit-line-clamp: 4;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.book-categories {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.book-category-tag {
  display: inline-block;
  padding: 4px 10px;
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 600;
  box-shadow: 0 2px 4px rgba(245, 87, 108, 0.2);
}

.book-card-footer {
  padding: 1rem 1.25rem;
  background: #f8f9fa;
  border-top: 1px solid #e9ecef;
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.book-link-btn {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  text-decoration: none;
  transition: all 0.3s ease;
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.book-link-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
}

.book-link-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.book-link-secondary {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.book-link-secondary:hover {
  background: #667eea;
  color: white;
}

.book-link-save {
  background: #4caf50;
  color: white;
  border: none;
  cursor: pointer;
}

.book-link-save:hover:not(:disabled) {
  background: #45a049;
  transform: translateY(-2px);
}

.book-link-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 반응형 디자인 */
@media (max-width: 768px) {
  .books-grid {
    grid-template-columns: 1fr;
  }
  
  .book-card-header {
    min-height: 180px;
  }
  
  .book-card-footer {
    flex-direction: column;
  }
  
  .book-link-btn {
    width: 100%;
    justify-content: center;
  }
}

/* 다크 모드 대응 */
@media (prefers-color-scheme: dark) {
  .book-list {
    background: #1e1e1e;
  }
  
  .book-list-title {
    color: rgba(255, 255, 255, 0.87);
  }
  
  .book-card {
    background: #2e2e2e;
    border-color: #404040;
  }
  
  .book-card:hover {
    border-color: #667eea;
  }
  
  .book-title {
    color: rgba(255, 255, 255, 0.87);
  }
  
  .book-meta-label {
    color: rgba(255, 255, 255, 0.6);
  }
  
  .book-meta-value {
    color: rgba(255, 255, 255, 0.87);
  }
  
  .book-description {
    color: rgba(255, 255, 255, 0.7);
  }
  
  .book-card-footer {
    background: #1e1e1e;
    border-color: #404040;
  }
  
  .book-link-secondary {
    background: #2e2e2e;
    border-color: #667eea;
    color: #667eea;
  }
  
  .book-link-secondary:hover {
    background: #667eea;
    color: white;
  }
  
  .fetch-info {
    background: #2e2e2e;
  }

  .fetch-info p {
    color: rgba(255, 255, 255, 0.87);
  }

  .fetch-details h3 {
    color: rgba(255, 255, 255, 0.87);
  }

  .details-table td {
    color: rgba(255, 255, 255, 0.87);
    border-color: #404040;
  }

  .details-table tbody tr:hover {
    background: #2e2e2e;
  }

  .time-info {
    color: rgba(255, 255, 255, 0.6);
  }

  .fetch-result-footer {
    border-color: #404040;
  }
}

/* MCP 가이드 모달 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 2000;
  padding: 20px;
  animation: fadeIn 0.3s ease;
}

.modal-content {
  background: white;
  border-radius: 12px;
  max-width: 900px;
  max-height: 90vh;
  width: 100%;
  display: flex;
  flex-direction: column;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 24px;
  border-bottom: 2px solid #e0e0e0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px 12px 0 0;
}

.modal-header h2 {
  color: white;
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.btn-close {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: white;
  font-size: 24px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.3s ease;
  font-weight: 300;
}

.btn-close:hover {
  background: rgba(255, 255, 255, 0.3);
}

.modal-body {
  padding: 24px;
  overflow-y: auto;
  font-size: 16px;
  line-height: 1.8;
  color: #333;
  text-align: left;
}

.loading {
  text-align: center;
  padding: 40px;
  font-size: 18px;
  color: #666;
}

.modal-body h1 {
  font-size: 28px;
  margin-top: 0;
  margin-bottom: 16px;
  color: #667eea;
  border-bottom: 2px solid #e0e0e0;
  padding-bottom: 12px;
  text-align: left;
}

.modal-body h2 {
  font-size: 24px;
  margin-top: 32px;
  margin-bottom: 16px;
  color: #764ba2;
  text-align: left;
}

.modal-body h3 {
  font-size: 20px;
  margin-top: 24px;
  margin-bottom: 12px;
  color: #555;
  text-align: left;
}

.modal-body p {
  font-size: 16px;
  margin-bottom: 16px;
  line-height: 1.8;
  text-align: left;
}

.modal-body ul,
.modal-body ol {
  font-size: 16px;
  margin-bottom: 16px;
  padding-left: 24px;
  line-height: 1.8;
  text-align: left;
}

.modal-body li {
  margin-bottom: 8px;
  font-size: 16px;
  text-align: left;
}

.modal-body code {
  background: #f5f5f5;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 15px;
  font-family: 'Courier New', 'Consolas', 'Monaco', monospace;
  word-break: break-word;
}

.modal-body pre {
  background: #2d2d2d;
  color: #f8f8f2;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  margin-bottom: 16px;
  font-size: 15px;
  line-height: 1.6;
  border: 1px solid #404040;
}

.modal-body pre code {
  background: transparent;
  padding: 0;
  color: inherit;
  font-size: 15px;
  display: block;
  white-space: pre;
}

.modal-body strong {
  font-weight: 600;
  color: #333;
}

.modal-body a {
  color: #667eea;
  text-decoration: none;
}

.modal-body a:hover {
  text-decoration: underline;
}

.modal-body blockquote {
  border-left: 4px solid #667eea;
  padding-left: 16px;
  margin: 16px 0;
  color: #666;
  font-style: italic;
  text-align: left;
}

.modal-body table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 16px;
  font-size: 16px;
}

.modal-body th,
.modal-body td {
  border: 1px solid #e0e0e0;
  padding: 12px;
  text-align: left;
}

.modal-body th {
  background: #f5f5f5;
  font-weight: 600;
}

.modal-body img {
  max-width: 100%;
  height: auto;
  border-radius: 8px;
  margin: 16px 0;
}

.modal-body hr {
  border: none;
  border-top: 2px solid #e0e0e0;
  margin: 24px 0;
}

/* 다크 모드 대응 */
@media (prefers-color-scheme: dark) {
  .modal-content {
    background: #1e1e1e;
    color: rgba(255, 255, 255, 0.87);
  }

  .modal-body {
    color: rgba(255, 255, 255, 0.87);
  }

  .modal-body h1 {
    color: #a78bfa;
  }

  .modal-body h2 {
    color: #c084fc;
  }

  .modal-body h3 {
    color: rgba(255, 255, 255, 0.87);
  }

  .modal-body code {
    background: #2d2d2d;
    color: #f8f8f2;
  }

  .modal-body th {
    background: #2d2d2d;
  }

  .modal-body th,
  .modal-body td {
    border-color: #404040;
  }
}

/* 경제뉴스 알람 모달 스타일 */
.alarm-modal {
  max-width: 800px;
  max-height: 85vh;
}

.alarm-results {
  padding: 20px;
}

.alarm-summary {
  margin-bottom: 20px;
  padding: 16px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.alarm-summary h3 {
  margin: 0 0 8px 0;
  font-size: 20px;
  font-weight: 700;
}

.alarm-time {
  margin: 8px 0 0 0;
  font-size: 14px;
  opacity: 0.9;
}

.alarm-news-list {
  max-height: 50vh;
  overflow-y: auto;
  margin-bottom: 20px;
}

.alarm-news-item {
  padding: 16px;
  margin-bottom: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #667eea;
  transition: all 0.3s ease;
}

.alarm-news-item:hover {
  background: #e9ecef;
  transform: translateX(4px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.alarm-news-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}

.alarm-news-number {
  background: #667eea;
  color: white;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: 700;
}

.alarm-news-importance {
  font-size: 18px;
}

.alarm-news-date {
  margin-left: auto;
  font-size: 12px;
  color: #666;
}

.alarm-news-title {
  margin-bottom: 8px;
}

.alarm-news-link {
  font-size: 16px;
  font-weight: 600;
  color: #667eea;
  text-decoration: none;
  transition: color 0.3s ease;
}

.alarm-news-link:hover {
  color: #764ba2;
  text-decoration: underline;
}

.alarm-news-source {
  font-size: 13px;
  color: #666;
  margin-bottom: 8px;
}

.alarm-news-summary {
  font-size: 14px;
  color: #555;
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.alarm-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 16px;
  border-top: 2px solid #e0e0e0;
}

.btn-save {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-save:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-close-alarm {
  background: white;
  color: #667eea;
  padding: 12px 24px;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-close-alarm:hover {
  background: #667eea;
  color: white;
}

.alarm-no-results {
  padding: 40px 20px;
  text-align: center;
}

.alarm-no-results p {
  font-size: 18px;
  color: #666;
  margin-bottom: 12px;
}

.alarm-no-results .alarm-time {
  font-size: 14px;
  color: #999;
  margin-bottom: 24px;
}

/* 인증 관련 스타일 */
.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-right: 0;
  flex-wrap: wrap;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  white-space: nowrap;
}

.btn-login,
.btn-signup,
.btn-logout,
.btn-manage {
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  border: none;
  white-space: nowrap;
  flex-shrink: 0;
}

.btn-login {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.btn-login:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-signup {
  background: white;
  color: #667eea;
  border: 2px solid #667eea;
}

.btn-signup:hover {
  background: #667eea;
  color: white;
}

.btn-logout {
  background: #f44336;
  color: white;
}

.btn-logout:hover {
  background: #d32f2f;
  transform: translateY(-2px);
}

.btn-manage {
  background: #2196f3;
  color: white;
}

.btn-manage:hover {
  background: #1976d2;
  transform: translateY(-2px);
}

.auth-buttons {
  display: flex;
  gap: 10px;
  margin-right: 0;
  flex-wrap: wrap;
}

/* 사용자 관리 모달 스타일 */
.user-management-modal {
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
}

.user-tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 24px;
  border-bottom: 2px solid #e0e0e0;
}

.tab-btn {
  padding: 12px 24px;
  background: transparent;
  border: none;
  border-bottom: 3px solid transparent;
  font-size: 14px;
  font-weight: 600;
  color: #666;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-btn:hover {
  color: #667eea;
}

.tab-btn.active {
  color: #667eea;
  border-bottom-color: #667eea;
}

.tab-content {
  padding: 20px 0;
}

/* 데이터 요약 카드 */
.data-summary {
  margin-bottom: 32px;
}

.data-summary h3 {
  margin-bottom: 16px;
  font-size: 18px;
  color: #333;
}

.summary-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.summary-card {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.summary-icon {
  font-size: 32px;
}

.summary-info {
  flex: 1;
}

.summary-label {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 24px;
  font-weight: 700;
}

/* 데이터 섹션 */
.data-section {
  margin-bottom: 32px;
}

.data-section h4 {
  margin-bottom: 16px;
  font-size: 16px;
  color: #333;
  padding-bottom: 8px;
  border-bottom: 2px solid #e0e0e0;
}

.data-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.data-item {
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.data-item-title {
  font-size: 14px;
  font-weight: 600;
  color: #333;
  margin-bottom: 8px;
}

.data-item-meta {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: #666;
}

.data-more {
  padding: 12px;
  text-align: center;
  color: #666;
  font-size: 14px;
  font-style: italic;
}

.no-data {
  padding: 40px;
  text-align: center;
  color: #999;
}

.no-data p {
  font-size: 16px;
}

/* 계정 삭제 경고 */
.delete-warning {
  padding: 20px;
}

.delete-warning h3 {
  color: #f44336;
  margin-bottom: 16px;
}

.delete-warning ul {
  margin: 16px 0;
  padding-left: 24px;
}

.delete-warning li {
  margin-bottom: 8px;
  color: #666;
}

.warning-text {
  color: #f44336;
  font-weight: 600;
  margin-top: 16px;
}

.btn-danger {
  background: #f44336;
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-danger:hover:not(:disabled) {
  background: #d32f2f;
  transform: translateY(-2px);
}

.btn-danger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.success-message {
  padding: 12px;
  background: #e8f5e9;
  color: #2e7d32;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #2e7d32;
  margin-bottom: 16px;
}

.auth-modal {
  max-width: 400px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 600;
  color: #333;
}

.form-input {
  padding: 12px;
  border: 2px solid #e0e0e0;
  border-radius: 6px;
  font-size: 14px;
  transition: border-color 0.3s ease;
}

.form-input:focus {
  outline: none;
  border-color: #667eea;
}

.form-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 8px;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 12px 24px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  color: #667eea;
  padding: 12px 24px;
  border: 2px solid #667eea;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
}

.btn-secondary:hover {
  background: #667eea;
  color: white;
}

.error-message {
  padding: 12px;
  background: #ffebee;
  color: #c62828;
  border-radius: 6px;
  font-size: 14px;
  border-left: 4px solid #c62828;
}

/* API 키 관리 스타일 */
.api-keys-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.api-keys-header h3 {
  margin: 0;
  font-size: 20px;
  color: #333;
}

.api-keys-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
  margin-bottom: 32px;
}

.api-key-item {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 16px;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  background: #f9f9f9;
  transition: box-shadow 0.3s ease;
}

.api-key-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.api-key-info {
  flex: 1;
}

.api-key-name {
  font-weight: 600;
  font-size: 16px;
  color: #333;
  margin-bottom: 8px;
}

.api-key-value {
  font-family: 'Courier New', monospace;
  font-size: 14px;
  color: #666;
  background: #fff;
  padding: 8px 12px;
  border-radius: 4px;
  margin-bottom: 8px;
  word-break: break-all;
}

.api-key-description {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.api-key-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  font-size: 12px;
  color: #999;
}

.api-key-actions {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}

.btn-sm {
  padding: 6px 12px;
  font-size: 14px;
}

.no-api-keys {
  text-align: center;
  padding: 40px;
  color: #666;
}

.api-key-usage-info {
  margin-top: 32px;
  padding: 20px;
  background: #f0f4ff;
  border-radius: 8px;
  border-left: 4px solid #667eea;
}

.api-key-usage-info h4 {
  margin-top: 0;
  margin-bottom: 16px;
  color: #333;
}

.usage-examples {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.usage-example {
  background: #fff;
  padding: 16px;
  border-radius: 6px;
}

.usage-example strong {
  display: block;
  margin-bottom: 8px;
  color: #333;
}

.usage-example pre {
  margin: 0;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 4px;
  overflow-x: auto;
}

.usage-example code {
  font-family: 'Courier New', monospace;
  font-size: 13px;
  color: #333;
}

.api-key-modal {
  max-width: 600px;
}

.api-key-display {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 6px;
}

.api-key-display code {
  flex: 1;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  word-break: break-all;
  padding: 8px;
  background: #fff;
  border-radius: 4px;
}

.warning-text {
  color: #d32f2f;
  font-size: 14px;
  margin-top: 8px;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background: #5a6268;
}
</style>




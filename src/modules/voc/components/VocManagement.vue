<template>
  <div v-if="showVocModal" class="voc-modal-overlay" @click="handleClose">
    <div class="voc-modal-container" @click.stop>
      <!-- 헤더 -->
      <div class="voc-modal-header">
        <div class="voc-header-content">
          <h1 class="voc-title">🌿 VOC 자동 대응 관리</h1>
          <p class="voc-subtitle">Service Request 관리 및 분석 시스템</p>
        </div>
        <button @click="handleClose" class="voc-close-btn" aria-label="닫기">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>
      </div>

      <!-- 탭 네비게이션 -->
      <div class="voc-tab-navigation">
        <button 
          @click="vocTab = 'sr-input'" 
          class="voc-tab-button" 
          :class="{ active: vocTab === 'sr-input' }"
        >
          <span class="tab-icon">📝</span>
          <span class="tab-label">SR 입력</span>
        </button>
        <button 
          @click="vocTab = 'sr-history'" 
          class="voc-tab-button" 
          :class="{ active: vocTab === 'sr-history' }"
        >
          <span class="tab-icon">📋</span>
          <span class="tab-label">SR 이력 조회</span>
        </button>
        <button 
          @click="vocTab = 'similar-sr'" 
          class="voc-tab-button" 
          :class="{ active: vocTab === 'similar-sr' }"
        >
          <span class="tab-icon">🔍</span>
          <span class="tab-label">유사 SR 검색</span>
        </button>
        <button 
          @click="vocTab = 'db-analysis'" 
          class="voc-tab-button" 
          :class="{ active: vocTab === 'db-analysis' }"
        >
          <span class="tab-icon">🗄️</span>
          <span class="tab-label">DB 변경 분석</span>
        </button>
      </div>

      <!-- 컨텐츠 영역 -->
      <div class="voc-modal-body">
        <!-- SR 입력 탭 -->
        <div v-if="vocTab === 'sr-input'" class="voc-tab-content">
          <div class="voc-section">
            <h2 class="section-title">새 SR 등록</h2>
            <p class="section-description">Confluence 페이지 또는 수동으로 SR을 등록합니다.</p>
            
            <form @submit.prevent="handleRegisterSr" class="voc-form">
              <div class="form-grid">
                <div class="form-group full-width">
                  <label class="form-label">
                    Confluence URL
                    <span class="label-optional">(선택사항)</span>
                  </label>
                  <input 
                    v-model="srForm.confluence_url" 
                    type="url" 
                    placeholder="https://confluence.example.com/pages/viewpage.action?pageId=123456"
                    class="form-input"
                  />
                  <p class="form-help">Confluence 페이지 URL을 입력하면 자동으로 페이지 정보를 가져옵니다.</p>
                </div>

                <div class="form-group full-width">
                  <label class="form-label">
                    SR 제목
                    <span class="label-required">*</span>
                  </label>
                  <input 
                    v-model="srForm.title" 
                    type="text" 
                    placeholder="SR 제목을 입력하세요"
                    required
                    class="form-input form-input-large"
                  />
                </div>

                <div class="form-group full-width">
                  <label class="form-label">요구사항 설명</label>
                  <textarea 
                    v-model="srForm.description" 
                    placeholder="요구사항을 상세히 입력하세요"
                    rows="6"
                    class="form-input form-textarea"
                  ></textarea>
                </div>

                <div class="form-group">
                  <label class="form-label">우선순위</label>
                  <select v-model="srForm.priority" class="form-input form-select">
                    <option value="low">낮음</option>
                    <option value="medium">보통</option>
                    <option value="high">높음</option>
                    <option value="critical">긴급</option>
                  </select>
                </div>

                <div class="form-group">
                  <label class="form-label">카테고리</label>
                  <input 
                    v-model="srForm.category" 
                    type="text" 
                    placeholder="예: 기능개선, 버그수정"
                    class="form-input"
                  />
                </div>

                <div class="form-group full-width">
                  <label class="form-label">태그</label>
                  <input 
                    v-model="srForm.tagsInput" 
                    type="text" 
                    placeholder="쉼표로 구분하여 입력 (예: 긴급, 고객요청, 기능개선)"
                    class="form-input"
                  />
                </div>
              </div>

              <div v-if="srFormError" class="alert alert-error">
                <span class="alert-icon">⚠️</span>
                <span>{{ srFormError }}</span>
              </div>

              <div v-if="srFormSuccess" class="alert alert-success">
                <span class="alert-icon">✓</span>
                <span>{{ srFormSuccess }}</span>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="srFormSubmitting">
                  <span v-if="srFormSubmitting">등록 중...</span>
                  <span v-else>SR 등록</span>
                </button>
                <button type="button" @click="resetSrForm" class="btn btn-secondary">
                  초기화
                </button>
              </div>
            </form>
          </div>
        </div>

        <!-- SR 이력 조회 탭 -->
        <div v-if="vocTab === 'sr-history'" class="voc-tab-content">
          <div class="voc-section">
            <h2 class="section-title">SR 이력 조회</h2>
            <p class="section-description">등록된 SR 목록을 조회하고 필터링할 수 있습니다.</p>
            
            <div class="filter-bar">
              <div class="filter-group">
                <label class="filter-label">상태</label>
                <select v-model="historyFilters.status" @change="loadSrHistory" class="filter-select">
                  <option value="">전체</option>
                  <option value="open">열림</option>
                  <option value="in_progress">진행중</option>
                  <option value="resolved">해결됨</option>
                  <option value="closed">닫힘</option>
                </select>
              </div>
              <div class="filter-group">
                <label class="filter-label">우선순위</label>
                <select v-model="historyFilters.priority" @change="loadSrHistory" class="filter-select">
                  <option value="">전체</option>
                  <option value="low">낮음</option>
                  <option value="medium">보통</option>
                  <option value="high">높음</option>
                  <option value="critical">긴급</option>
                </select>
              </div>
              <button @click="loadSrHistory" class="btn btn-filter">
                <span>🔍</span>
                <span>검색</span>
              </button>
            </div>

            <div v-if="srHistoryLoading" class="loading-state">
              <div class="spinner"></div>
              <p>SR 이력을 불러오는 중...</p>
            </div>

            <div v-else-if="srHistoryError" class="alert alert-error">
              <span class="alert-icon">⚠️</span>
              <span>{{ srHistoryError }}</span>
            </div>

            <div v-else-if="srHistoryList.length === 0" class="empty-state">
              <div class="empty-icon">📭</div>
              <p class="empty-message">등록된 SR이 없습니다.</p>
            </div>

            <div v-else class="sr-table-container">
              <div style="margin-bottom: 16px; display: flex; justify-content: space-between; align-items: center;">
                <h4 style="font-size: 16px; font-weight: 600; margin: 0; color: #212529; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;">
                  SR 목록 ({{ srHistoryList.length }}건) - 최신순
                </h4>
                <button @click="loadSrHistory" class="btn btn-refresh" style="padding: 8px 16px; background: #4caf50; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; display: flex; align-items: center; gap: 6px; transition: all 0.2s;">
                  <span>🔄</span>
                  <span>새로고침</span>
                </button>
              </div>

              <div style="overflow-x: auto;">
                <table style="width: 100%; border-collapse: collapse; background: white; border-radius: 8px; overflow: hidden; font-size: 13px; box-shadow: 0 1px 3px rgba(0,0,0,0.1);">
                  <thead>
                    <tr style="background: #f5f5f5;">
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">번호</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">SR 번호</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">제목</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">상태</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">우선순위</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">카테고리</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">생성일시</th>
                      <th style="padding: 12px; text-align: left; border-bottom: 2px solid #ddd; font-size: 13px; font-weight: 600; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">작업</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(sr, index) in srHistoryList" :key="sr.id" style="border-bottom: 1px solid #eee; transition: background-color 0.2s;" @mouseenter="$event.currentTarget.style.backgroundColor = '#f8f9fa'" @mouseleave="$event.currentTarget.style.backgroundColor = 'white'">
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #6c757d;">{{ index + 1 }}</td>
                      <td style="padding: 12px; font-size: 13px; font-family: 'Consolas', 'Monaco', 'Courier New', monospace; color: #495057; font-weight: 500;">{{ sr.sr_number }}</td>
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #212529; max-width: 400px;">
                        <div style="font-weight: 500; margin-bottom: 4px;">{{ sr.title }}</div>
                        <div v-if="sr.description" style="font-size: 12px; color: #6c757d; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; max-width: 400px;">
                          {{ sr.description.substring(0, 80) }}{{ sr.description.length > 80 ? '...' : '' }}
                        </div>
                      </td>
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;">
                        <span class="badge badge-status" :class="'status-' + sr.status" style="display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; white-space: nowrap;">
                          {{ getStatusLabel(sr.status) }}
                        </span>
                      </td>
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;">
                        <span class="badge badge-priority" :class="'priority-' + sr.priority" style="display: inline-block; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; white-space: nowrap;">
                          {{ getPriorityLabel(sr.priority) }}
                        </span>
                      </td>
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #495057;">
                        <span v-if="sr.category" style="padding: 4px 8px; border-radius: 4px; background: #e3f2fd; color: #1976d2; font-size: 12px; font-weight: 500;">
                          {{ sr.category }}
                        </span>
                        <span v-else style="color: #adb5bd;">-</span>
                      </td>
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif; color: #6c757d;">
                        {{ formatDate(sr.created_at) }}
                      </td>
                      <td style="padding: 12px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;">
                        <div style="display: flex; gap: 6px;">
                          <button @click="showSrDetail(sr)" class="btn-detail" style="padding: 6px 12px; background: #4caf50; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500; transition: all 0.2s;">
                            상세보기
                          </button>
                          <a v-if="sr.confluence_url" :href="sr.confluence_url" target="_blank" style="padding: 6px 12px; background: #2196f3; color: white; border: none; border-radius: 4px; cursor: pointer; font-size: 12px; font-weight: 500; text-decoration: none; display: inline-block; transition: all 0.2s;">
                            🔗
                          </a>
                        </div>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>

        <!-- 유사 SR 검색 탭 -->
        <div v-if="vocTab === 'similar-sr'" class="voc-tab-content">
          <div class="voc-section">
            <h2 class="section-title">Git 기반 유사 SR 검색</h2>
            <p class="section-description">Git 저장소에서 유사한 SR 처리 내역을 검색합니다.</p>
            
            <form @submit.prevent="handleSearchSimilarSr" class="voc-form">
              <div class="form-grid">
                <div class="form-group full-width">
                  <label class="form-label">
                    검색 키워드
                    <span class="label-required">*</span>
                  </label>
                  <input 
                    v-model="similarSrForm.keywords" 
                    type="text" 
                    placeholder="쉼표로 구분하여 입력 (예: 에러, 로그인, 데이터베이스)"
                    required
                    class="form-input form-input-large"
                  />
                  <p class="form-help">여러 키워드를 쉼표로 구분하여 입력하세요.</p>
                </div>

                <div class="form-group">
                  <label class="form-label">최대 결과 수</label>
                  <input 
                    v-model.number="similarSrForm.limit" 
                    type="number" 
                    min="1"
                    max="50"
                    class="form-input"
                  />
                </div>
              </div>

              <div v-if="similarSrError" class="alert alert-error">
                <span class="alert-icon">⚠️</span>
                <span>{{ similarSrError }}</span>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="similarSrSearching">
                  <span v-if="similarSrSearching">검색 중...</span>
                  <span v-else>
                    <span>🔍</span>
                    <span>검색</span>
                  </span>
                </button>
              </div>
            </form>

            <div v-if="similarSrResults.length > 0" class="results-section">
              <h3 class="results-title">검색 결과 ({{ similarSrResults.length }}건)</h3>
              <div class="commit-list">
                <div v-for="commit in similarSrResults" :key="commit.commit_hash" class="commit-card">
                  <div class="commit-header">
                    <div class="commit-author-info">
                      <strong class="commit-author">{{ commit.author }}</strong>
                      <span class="commit-date">{{ formatDate(commit.commit_date) }}</span>
                    </div>
                    <code class="commit-hash">{{ commit.commit_hash.substring(0, 7) }}</code>
                  </div>
                  <div class="commit-message">{{ commit.commit_message }}</div>
                  <div v-if="commit.files_changed && commit.files_changed.length > 0" class="commit-files">
                    <span class="files-count">변경된 파일: {{ commit.files_changed.length }}개</span>
                    <ul class="files-list">
                      <li v-for="file in commit.files_changed.slice(0, 5)" :key="file" class="file-item">{{ file }}</li>
                      <li v-if="commit.files_changed.length > 5" class="file-item-more">
                        ... 외 {{ commit.files_changed.length - 5 }}개
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- DB 변경 분석 탭 -->
        <div v-if="vocTab === 'db-analysis'" class="voc-tab-content">
          <div class="voc-section">
            <h2 class="section-title">DB 변경 분석</h2>
            <p class="section-description">SQL 쿼리를 분석하여 테이블 및 컬럼 변경 사항을 감지합니다.</p>
            
            <form @submit.prevent="handleAnalyzeDbChanges" class="voc-form">
              <div class="form-group full-width">
                <label class="form-label">
                  SQL 쿼리
                  <span class="label-required">*</span>
                </label>
                <textarea 
                  v-model="dbAnalysisForm.sql_query" 
                  placeholder="분석할 SQL 쿼리를 입력하세요&#10;&#10;예시:&#10;ALTER TABLE users ADD COLUMN phone TEXT;&#10;CREATE TABLE orders (id INTEGER PRIMARY KEY, user_id INTEGER);"
                  rows="10"
                  required
                  class="form-input form-textarea form-code"
                ></textarea>
                <p class="form-help">CREATE TABLE, ALTER TABLE, DROP TABLE 등의 쿼리를 분석할 수 있습니다.</p>
              </div>

              <div v-if="dbAnalysisError" class="alert alert-error">
                <span class="alert-icon">⚠️</span>
                <span>{{ dbAnalysisError }}</span>
              </div>

              <div class="form-actions">
                <button type="submit" class="btn btn-primary" :disabled="dbAnalysisAnalyzing">
                  <span v-if="dbAnalysisAnalyzing">분석 중...</span>
                  <span v-else>
                    <span>🔍</span>
                    <span>분석</span>
                  </span>
                </button>
              </div>
            </form>

            <div v-if="dbAnalysisResults" class="results-section">
              <h3 class="results-title">분석 결과</h3>
              <div class="analysis-summary">
                <div class="summary-item">
                  <span class="summary-label">변경 사항 수</span>
                  <span class="summary-value">{{ dbAnalysisResults.change_count }}건</span>
                </div>
              </div>
              <div v-if="dbAnalysisResults.changes && dbAnalysisResults.changes.length > 0" class="changes-list">
                <div v-for="(change, index) in dbAnalysisResults.changes" :key="index" class="change-card">
                  <div class="change-type-badge">
                    {{ getChangeTypeLabel(change.change_type) }}
                  </div>
                  <div class="change-details">
                    <div v-if="change.table_name" class="change-detail-item">
                      <span class="detail-label">테이블:</span>
                      <span class="detail-value">{{ change.table_name }}</span>
                    </div>
                    <div v-if="change.column_name" class="change-detail-item">
                      <span class="detail-label">컬럼:</span>
                      <span class="detail-value">{{ change.column_name }}</span>
                    </div>
                    <div v-if="change.description" class="change-description">
                      {{ change.description }}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- SR 상세보기 모달 -->
      <div v-if="showSrDetailModal" class="voc-modal-overlay" @click="closeSrDetail" style="z-index: 10001;">
        <div class="voc-modal-container sr-detail-modal" @click.stop style="max-width: 900px; max-height: 90vh; z-index: 10002;">
          <div class="voc-modal-header">
            <div class="voc-header-content">
              <h1 class="voc-title">📋 SR 상세 정보</h1>
            </div>
            <button @click="closeSrDetail" class="voc-close-btn" aria-label="닫기">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          <div class="voc-modal-body" v-if="selectedSr">
            <div class="sr-detail-section">
              <div class="detail-row">
                <span class="detail-label">SR 번호:</span>
                <span class="detail-value" style="font-family: 'Consolas', 'Monaco', 'Courier New', monospace;">{{ selectedSr.sr_number }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">제목:</span>
                <span class="detail-value" style="font-weight: 600;">{{ selectedSr.title }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">상태:</span>
                <span class="badge badge-status" :class="'status-' + selectedSr.status">
                  {{ getStatusLabel(selectedSr.status) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">우선순위:</span>
                <span class="badge badge-priority" :class="'priority-' + selectedSr.priority">
                  {{ getPriorityLabel(selectedSr.priority) }}
                </span>
              </div>
              <div class="detail-row" v-if="selectedSr.category">
                <span class="detail-label">카테고리:</span>
                <span class="detail-value">{{ selectedSr.category }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">생성일시:</span>
                <span class="detail-value">{{ formatDate(selectedSr.created_at) }}</span>
              </div>
              <div class="detail-row" v-if="selectedSr.updated_at">
                <span class="detail-label">수정일시:</span>
                <span class="detail-value">{{ formatDate(selectedSr.updated_at) }}</span>
              </div>
              <div class="detail-row" v-if="selectedSr.tags">
                <span class="detail-label">태그:</span>
                <div class="tags-container">
                  <span v-for="tag in (selectedSr.tags.split ? selectedSr.tags.split(',') : [])" :key="tag" class="tag-badge">
                    {{ tag.trim() }}
                  </span>
                </div>
              </div>
              <div class="detail-row full-width" v-if="selectedSr.description">
                <span class="detail-label">설명:</span>
                <div class="detail-description">{{ selectedSr.description }}</div>
              </div>
              <div class="detail-row full-width" v-if="selectedSr.confluence_url">
                <span class="detail-label">Confluence:</span>
                <a :href="selectedSr.confluence_url" target="_blank" class="confluence-link">
                  <span>🔗</span>
                  <span>{{ selectedSr.confluence_url }}</span>
                </a>
              </div>
              <div class="detail-row full-width" v-if="selectedSr.confluence_content">
                <span class="detail-label">Confluence 내용:</span>
                <div class="detail-description" style="background: #f8f9fa; padding: 12px; border-radius: 6px; font-size: 13px; line-height: 1.6;">
                  {{ selectedSr.confluence_content }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '../../../services/api.js';

export default {
  name: 'VocManagement',
  props: {
    showVocModal: {
      type: Boolean,
      default: false
    }
  },
  emits: ['close'],
  data() {
    return {
      vocTab: 'sr-input',
      srForm: {
        confluence_url: '',
        title: '',
        description: '',
        priority: 'medium',
        category: '',
        tagsInput: ''
      },
      srFormSubmitting: false,
      srFormError: null,
      srFormSuccess: null,
      srHistoryList: [],
      srHistoryLoading: false,
      srHistoryError: null,
      historyFilters: {
        status: '',
        priority: ''
      },
      similarSrForm: {
        keywords: '',
        limit: 10
      },
      similarSrSearching: false,
      similarSrError: null,
      similarSrResults: [],
      dbAnalysisForm: {
        sql_query: ''
      },
      dbAnalysisAnalyzing: false,
      dbAnalysisError: null,
      dbAnalysisResults: null,
      showSrDetailModal: false,
      selectedSr: null
    };
  },
  methods: {
    handleClose() {
      this.$emit('close');
    },
    
    showSrDetail(sr) {
      this.selectedSr = sr;
      this.showSrDetailModal = true;
    },
    
    closeSrDetail() {
      this.showSrDetailModal = false;
      this.selectedSr = null;
    },
    
    async handleRegisterSr() {
      this.srFormSubmitting = true;
      this.srFormError = null;
      this.srFormSuccess = null;
      
      try {
        const tags = this.srForm.tagsInput ? this.srForm.tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];
        
        const response = await apiRequest('/api/voc/sr', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            title: this.srForm.title,
            description: this.srForm.description,
            confluence_url: this.srForm.confluence_url || null,
            priority: this.srForm.priority,
            category: this.srForm.category || null,
            tags: tags
          })
        });
        
        if (response.success) {
          this.srFormSuccess = 'SR이 성공적으로 등록되었습니다.';
          this.resetSrForm();
          this.vocTab = 'sr-history';
          this.loadSrHistory();
        } else {
          this.srFormError = response.error || 'SR 등록에 실패했습니다.';
        }
      } catch (error) {
        this.srFormError = `SR 등록 중 오류가 발생했습니다: ${error.message}`;
      } finally {
        this.srFormSubmitting = false;
      }
    },
    
    resetSrForm() {
      this.srForm = {
        confluence_url: '',
        title: '',
        description: '',
        priority: 'medium',
        category: '',
        tagsInput: ''
      };
      this.srFormError = null;
      this.srFormSuccess = null;
    },
    
    async loadSrHistory() {
      this.srHistoryLoading = true;
      this.srHistoryError = null;
      
      try {
        const params = new URLSearchParams();
        if (this.historyFilters.status) params.append('status', this.historyFilters.status);
        if (this.historyFilters.priority) params.append('priority', this.historyFilters.priority);
        params.append('limit', '50');
        
        const response = await apiRequest(`/api/voc/sr?${params.toString()}`);
        
        if (response.success) {
          this.srHistoryList = response.sr_list || [];
        } else {
          this.srHistoryError = response.error || 'SR 이력을 불러오는데 실패했습니다.';
        }
      } catch (error) {
        this.srHistoryError = `SR 이력 조회 중 오류가 발생했습니다: ${error.message}`;
      } finally {
        this.srHistoryLoading = false;
      }
    },
    
    async handleSearchSimilarSr() {
      this.similarSrSearching = true;
      this.similarSrError = null;
      this.similarSrResults = [];
      
      try {
        const keywords = this.similarSrForm.keywords.split(',').map(k => k.trim()).filter(k => k);
        const params = new URLSearchParams();
        params.append('keywords', keywords.join(','));
        params.append('limit', this.similarSrForm.limit.toString());
        
        const response = await apiRequest(`/api/voc/git/search?${params.toString()}`);
        
        if (response.success) {
          this.similarSrResults = response.commits || [];
        } else {
          this.similarSrError = response.error || '유사 SR 검색에 실패했습니다.';
        }
      } catch (error) {
        this.similarSrError = `유사 SR 검색 중 오류가 발생했습니다: ${error.message}`;
      } finally {
        this.similarSrSearching = false;
      }
    },
    
    async handleAnalyzeDbChanges() {
      this.dbAnalysisAnalyzing = true;
      this.dbAnalysisError = null;
      this.dbAnalysisResults = null;
      
      try {
        const response = await apiRequest('/api/voc/db/analyze', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            sql_query: this.dbAnalysisForm.sql_query
          })
        });
        
        if (response.success) {
          this.dbAnalysisResults = response.analysis || { changes: [], change_count: 0 };
        } else {
          this.dbAnalysisError = response.error || 'DB 변경 분석에 실패했습니다.';
        }
      } catch (error) {
        this.dbAnalysisError = `DB 변경 분석 중 오류가 발생했습니다: ${error.message}`;
      } finally {
        this.dbAnalysisAnalyzing = false;
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleString('ko-KR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
      });
    },
    
    getStatusLabel(status) {
      const labels = {
        'open': '열림',
        'in_progress': '진행중',
        'resolved': '해결됨',
        'closed': '닫힘'
      };
      return labels[status] || status;
    },
    
    getPriorityLabel(priority) {
      const labels = {
        'low': '낮음',
        'medium': '보통',
        'high': '높음',
        'critical': '긴급'
      };
      return labels[priority] || priority;
    },
    
    getChangeTypeLabel(changeType) {
      const labels = {
        'table_create': '테이블 생성',
        'table_drop': '테이블 삭제',
        'column_add': '컬럼 추가',
        'column_drop': '컬럼 삭제',
        'column_modify': '컬럼 수정'
      };
      return labels[changeType] || changeType;
    }
  },
  watch: {
    vocTab(newTab) {
      if (newTab === 'sr-history') {
        this.loadSrHistory();
      }
    }
  }
};
</script>

<style scoped>
/* 모달 오버레이 */
.voc-modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10000;
  padding: 20px;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 모달 컨테이너 */
.voc-modal-container {
  width: 95%;
  max-width: 1600px;
  max-height: 95vh;
  background: #ffffff;
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from {
    transform: translateY(30px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 헤더 */
.voc-modal-header {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
  padding: 32px 40px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.voc-header-content {
  flex: 1;
}

.voc-title {
  font-size: 28px;
  font-weight: 700;
  margin: 0 0 8px 0;
  letter-spacing: -0.5px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.voc-subtitle {
  font-size: 15px;
  margin: 0;
  opacity: 0.9;
  font-weight: 400;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.voc-close-btn {
  background: rgba(255, 255, 255, 0.15);
  border: none;
  color: white;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  font-size: 20px;
}

.voc-close-btn:hover {
  background: rgba(255, 255, 255, 0.25);
  transform: scale(1.05);
}

/* 탭 네비게이션 */
.voc-tab-navigation {
  display: flex;
  gap: 4px;
  padding: 0 40px;
  background: #f8f9fa;
  border-bottom: 2px solid #e9ecef;
}

.voc-tab-button {
  background: transparent;
  border: none;
  padding: 16px 24px;
  font-size: 15px;
  font-weight: 500;
  color: #6c757d;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  border-bottom: 3px solid transparent;
  transition: all 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
  position: relative;
}

.voc-tab-button:hover {
  color: #4caf50;
  background: rgba(76, 175, 80, 0.05);
}

.voc-tab-button.active {
  color: #2e7d32;
  border-bottom-color: #4caf50;
  background: white;
  font-weight: 600;
}

.tab-icon {
  font-size: 18px;
}

.tab-label {
  font-size: 15px;
}

/* 본문 영역 */
.voc-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 40px;
  background: #ffffff;
}

.voc-tab-content {
  animation: fadeInContent 0.3s ease-out;
}

@keyframes fadeInContent {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.voc-section {
  max-width: 1200px;
  margin: 0 auto;
}

.section-title {
  font-size: 24px;
  font-weight: 700;
  color: #212529;
  margin: 0 0 8px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
  letter-spacing: -0.3px;
}

.section-description {
  font-size: 15px;
  color: #6c757d;
  margin: 0 0 32px 0;
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* 폼 스타일 */
.voc-form {
  margin-top: 24px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 32px;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.label-required {
  color: #dc3545;
  margin-left: 4px;
}

.label-optional {
  color: #6c757d;
  font-weight: 400;
  font-size: 12px;
  margin-left: 4px;
}

.form-input {
  padding: 12px 16px;
  font-size: 15px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  transition: all 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
  color: #212529;
  background: #ffffff;
}

.form-input:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.form-input-large {
  font-size: 16px;
  padding: 14px 18px;
}

.form-textarea {
  resize: vertical;
  min-height: 120px;
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.form-code {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
}

.form-select {
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg width='12' height='8' viewBox='0 0 12 8' fill='none' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M1 1L6 6L11 1' stroke='%23495057' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 16px center;
  padding-right: 40px;
}

.form-help {
  font-size: 13px;
  color: #6c757d;
  margin-top: 6px;
  line-height: 1.5;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* 알림 메시지 */
.alert {
  padding: 16px 20px;
  border-radius: 8px;
  margin-bottom: 24px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.alert-error {
  background: #fff5f5;
  color: #c92a2a;
  border: 1px solid #ffc9c9;
}

.alert-success {
  background: #f0fdf4;
  color: #2e7d32;
  border: 1px solid #bbf7d0;
}

.alert-icon {
  font-size: 18px;
}

/* 버튼 */
.form-actions {
  display: flex;
  gap: 12px;
  margin-top: 32px;
}

.btn {
  padding: 12px 24px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.4);
}

.btn-secondary {
  background: #f8f9fa;
  color: #495057;
  border: 2px solid #dee2e6;
}

.btn-secondary:hover:not(:disabled) {
  background: #e9ecef;
  border-color: #adb5bd;
}

/* 필터 바 */
.filter-bar {
  display: flex;
  gap: 16px;
  align-items: flex-end;
  margin-bottom: 32px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
}

.filter-group {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 180px;
}

.filter-label {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  margin-bottom: 6px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.filter-select {
  padding: 10px 14px;
  font-size: 14px;
  border: 2px solid #dee2e6;
  border-radius: 8px;
  background: white;
  cursor: pointer;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.filter-select:focus {
  outline: none;
  border-color: #4caf50;
  box-shadow: 0 0 0 3px rgba(76, 175, 80, 0.1);
}

.btn-filter {
  padding: 10px 20px;
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
  transition: all 0.2s;
}

.btn-filter:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
}

/* 로딩 상태 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: #6c757d;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #e9ecef;
  border-top-color: #4caf50;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  font-size: 15px;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* 빈 상태 */
.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: #6c757d;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-message {
  font-size: 16px;
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* SR 리스트 */
.sr-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.sr-card {
  background: #ffffff;
  border: 2px solid #e9ecef;
  border-left: 4px solid #4caf50;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s;
}

.sr-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.sr-card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  gap: 16px;
}

.sr-title-group {
  flex: 1;
}

.sr-title {
  font-size: 18px;
  font-weight: 700;
  color: #212529;
  margin: 0 0 8px 0;
  line-height: 1.4;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.sr-meta {
  display: flex;
  gap: 16px;
  font-size: 13px;
  color: #6c757d;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.sr-number {
  font-weight: 600;
  color: #495057;
}

.sr-badges {
  display: flex;
  gap: 8px;
  flex-shrink: 0;
}

.badge {
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 12px;
  font-weight: 600;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
  white-space: nowrap;
}

.badge-status.status-open {
  background: #fff3e0;
  color: #e65100;
}

.badge-status.status-in_progress {
  background: #e3f2fd;
  color: #1565c0;
}

.badge-status.status-resolved {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge-status.status-closed {
  background: #f3e5f5;
  color: #6a1b9a;
}

.badge-priority.priority-low {
  background: #e8f5e9;
  color: #2e7d32;
}

.badge-priority.priority-medium {
  background: #fff9c4;
  color: #f57f17;
}

.badge-priority.priority-high {
  background: #ffe0b2;
  color: #e65100;
}

.badge-priority.priority-critical {
  background: #ffcdd2;
  color: #c62828;
}

.sr-description {
  font-size: 15px;
  color: #495057;
  line-height: 1.7;
  margin-bottom: 16px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.sr-footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.sr-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #4caf50;
  text-decoration: none;
  font-size: 14px;
  font-weight: 600;
  transition: all 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.sr-link:hover {
  color: #2e7d32;
  text-decoration: underline;
}

/* 결과 섹션 */
.results-section {
  margin-top: 40px;
}

.results-title {
  font-size: 20px;
  font-weight: 700;
  color: #212529;
  margin: 0 0 24px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* 커밋 리스트 */
.commit-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.commit-card {
  background: #ffffff;
  border: 2px solid #e9ecef;
  border-left: 4px solid #4caf50;
  border-radius: 12px;
  padding: 24px;
  transition: all 0.2s;
}

.commit-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.commit-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.commit-author-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.commit-author {
  font-size: 15px;
  font-weight: 600;
  color: #212529;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.commit-date {
  font-size: 13px;
  color: #6c757d;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.commit-hash {
  background: #f8f9fa;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 12px;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  color: #495057;
}

.commit-message {
  font-size: 15px;
  color: #495057;
  line-height: 1.7;
  margin-bottom: 12px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.commit-files {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e9ecef;
}

.files-count {
  font-size: 13px;
  font-weight: 600;
  color: #495057;
  display: block;
  margin-bottom: 8px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.files-list {
  margin: 0;
  padding-left: 20px;
  list-style: none;
}

.file-item {
  font-size: 13px;
  color: #6c757d;
  padding: 4px 0;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.file-item::before {
  content: '📄 ';
  margin-right: 6px;
}

.file-item-more {
  font-size: 13px;
  color: #adb5bd;
  font-style: italic;
  padding: 4px 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* 분석 결과 */
.analysis-summary {
  background: #f8f9fa;
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 24px;
}

.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.summary-label {
  font-size: 15px;
  font-weight: 600;
  color: #495057;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.summary-value {
  font-size: 18px;
  font-weight: 700;
  color: #4caf50;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.changes-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.change-card {
  background: #ffffff;
  border: 2px solid #e9ecef;
  border-left: 4px solid #4caf50;
  border-radius: 12px;
  padding: 20px;
}

.change-type-badge {
  display: inline-block;
  background: linear-gradient(135deg, #4caf50 0%, #2e7d32 100%);
  color: white;
  padding: 6px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 12px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.change-details {
  margin-top: 12px;
}

.change-detail-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  font-size: 14px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.detail-label {
  font-weight: 600;
  color: #6c757d;
}

.detail-value {
  color: #212529;
  font-weight: 500;
}

.change-description {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e9ecef;
  font-size: 14px;
  color: #495057;
  line-height: 1.6;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

/* 스크롤바 스타일링 */
.voc-modal-body::-webkit-scrollbar {
  width: 10px;
}

.voc-modal-body::-webkit-scrollbar-track {
  background: #f1f1f1;
}

.voc-modal-body::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 5px;
}

.voc-modal-body::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* SR 테이블 컨테이너 */
.sr-table-container {
  margin-top: 24px;
}

.btn-refresh:hover {
  background: #2e7d32 !important;
  transform: translateY(-1px);
  box-shadow: 0 2px 8px rgba(76, 175, 80, 0.3);
}

.btn-detail:hover {
  background: #2e7d32 !important;
  transform: translateY(-1px);
}

/* SR 상세보기 모달 */
.sr-detail-modal {
  max-width: 900px !important;
}

.sr-detail-section {
  padding: 8px 0;
}

.detail-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 1px solid #e9ecef;
}

.detail-row.full-width {
  flex-direction: column;
  gap: 8px;
}

.detail-row:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.detail-label {
  font-size: 14px;
  font-weight: 600;
  color: #495057;
  min-width: 120px;
  flex-shrink: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.detail-value {
  font-size: 14px;
  color: #212529;
  flex: 1;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.detail-description {
  font-size: 14px;
  color: #495057;
  line-height: 1.7;
  white-space: pre-wrap;
  word-break: break-word;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.tag-badge {
  display: inline-block;
  padding: 4px 10px;
  background: #e3f2fd;
  color: #1976d2;
  border-radius: 12px;
  font-size: 12px;
  font-weight: 500;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
}

.confluence-link {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  color: #4caf50;
  text-decoration: none;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans KR', sans-serif;
  word-break: break-all;
}

.confluence-link:hover {
  color: #2e7d32;
  text-decoration: underline;
}

/* 반응형 디자인 */
@media (max-width: 1200px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-group {
    min-width: auto;
  }
}

@media (max-width: 768px) {
  .voc-modal-container {
    width: 100%;
    max-height: 100vh;
    border-radius: 0;
  }
  
  .voc-modal-header {
    padding: 24px 20px;
  }
  
  .voc-title {
    font-size: 22px;
  }
  
  .voc-modal-body {
    padding: 24px 20px;
  }
  
  .voc-tab-navigation {
    padding: 0 20px;
    overflow-x: auto;
  }
  
  .voc-tab-button {
    padding: 12px 16px;
    font-size: 14px;
  }
  
  .tab-icon {
    font-size: 16px;
  }
}
</style>

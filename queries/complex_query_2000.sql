-- ============================================
-- 복잡한 SQL 쿼리 샘플 (약 2000라인)
-- ============================================
-- 목적: 초고급 데이터 웨어하우스 스타일 분석 및 예측 리포트
-- 테이블: users, news, radioSongs, books, apiKeys, apiKeyUsage
-- 작성일: 2025-01-XX
-- 리니지 연관도: 75% (높은 연관도 - 많은 JOIN 관계와 CTE 의존성 포함)
-- ============================================

-- ============================================
-- 1. 다층 CTE 구조 정의 (1단계: 기본 데이터 준비)
-- ============================================

WITH 
-- 사용자 기본 정보 및 생애주기 분석
user_lifecycle AS (
    SELECT 
        u.id AS user_id,
        u.email,
        u.name,
        u.createdAt,
        u.updatedAt,
        -- 생애주기 단계 계산
        CAST((julianday('now') - julianday(u.createdAt)) AS INTEGER) AS account_age_days,
        CAST((julianday(u.updatedAt) - julianday(u.createdAt)) AS INTEGER) AS update_frequency_days,
        -- 생애주기 단계 분류
        CASE 
            WHEN julianday('now') - julianday(u.createdAt) <= 7 THEN '신규 (1주일)'
            WHEN julianday('now') - julianday(u.createdAt) <= 30 THEN '초기 (1개월)'
            WHEN julianday('now') - julianday(u.createdAt) <= 90 THEN '성장 (3개월)'
            WHEN julianday('now') - julianday(u.createdAt) <= 180 THEN '안정 (6개월)'
            WHEN julianday('now') - julianday(u.createdAt) <= 365 THEN '성숙 (1년)'
            ELSE '장기 (1년+)'
        END AS lifecycle_stage,
        -- 계정 상태 분류
        CASE 
            WHEN julianday('now') - julianday(u.updatedAt) <= 7 THEN '활성'
            WHEN julianday('now') - julianday(u.updatedAt) <= 30 THEN '보통'
            WHEN julianday('now') - julianday(u.updatedAt) <= 90 THEN '비활성'
            ELSE '휴면'
        END AS account_status
    FROM users u
    WHERE u.createdAt IS NOT NULL
),

-- 뉴스 수집 심층 분석 (시간대별, 요일별, 카테고리별)
news_deep_analysis AS (
    SELECT 
        n.userId,
        -- 기본 통계
        COUNT(*) AS total_news_count,
        COUNT(DISTINCT n.id) AS unique_news_count,
        COUNT(DISTINCT n.category) AS category_count,
        COUNT(DISTINCT n.keyword) AS keyword_count,
        COUNT(DISTINCT n.source) AS source_count,
        COUNT(DISTINCT date(n.collectedAt)) AS collection_days,
        
        -- 시간대별 상세 분석 (24시간)
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 0 THEN 1 END) AS hour_00,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 1 THEN 1 END) AS hour_01,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 2 THEN 1 END) AS hour_02,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 3 THEN 1 END) AS hour_03,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 4 THEN 1 END) AS hour_04,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 5 THEN 1 END) AS hour_05,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 6 THEN 1 END) AS hour_06,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 7 THEN 1 END) AS hour_07,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 8 THEN 1 END) AS hour_08,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 9 THEN 1 END) AS hour_09,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 10 THEN 1 END) AS hour_10,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 11 THEN 1 END) AS hour_11,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 12 THEN 1 END) AS hour_12,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 13 THEN 1 END) AS hour_13,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 14 THEN 1 END) AS hour_14,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 15 THEN 1 END) AS hour_15,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 16 THEN 1 END) AS hour_16,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 17 THEN 1 END) AS hour_17,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 18 THEN 1 END) AS hour_18,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 19 THEN 1 END) AS hour_19,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 20 THEN 1 END) AS hour_20,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 21 THEN 1 END) AS hour_21,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 22 THEN 1 END) AS hour_22,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) = 23 THEN 1 END) AS hour_23,
        
        -- 요일별 상세 분석
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' THEN 1 END) AS sunday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' THEN 1 END) AS monday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' THEN 1 END) AS tuesday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' THEN 1 END) AS wednesday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' THEN 1 END) AS thursday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' THEN 1 END) AS friday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' THEN 1 END) AS saturday_count,
        
        -- 월별 트렌드 분석
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '01' THEN 1 END) AS january_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '02' THEN 1 END) AS february_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '03' THEN 1 END) AS march_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '04' THEN 1 END) AS april_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '05' THEN 1 END) AS may_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '06' THEN 1 END) AS june_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '07' THEN 1 END) AS july_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '08' THEN 1 END) AS august_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '09' THEN 1 END) AS september_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '10' THEN 1 END) AS october_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '11' THEN 1 END) AS november_count,
        COUNT(CASE WHEN strftime('%m', n.collectedAt) = '12' THEN 1 END) AS december_count,
        
        -- 중요도 분석
        AVG(n.importanceValue) AS avg_importance,
        MAX(n.importanceValue) AS max_importance,
        MIN(n.importanceValue) AS min_importance,
        COUNT(CASE WHEN n.importanceStars >= 3 THEN 1 END) AS high_importance_count,
        COUNT(CASE WHEN n.importanceStars = 2 THEN 1 END) AS medium_importance_count,
        COUNT(CASE WHEN n.importanceStars = 1 THEN 1 END) AS low_importance_count,
        
        -- 시간 간격 분석
        CAST((julianday(MAX(n.collectedAt)) - julianday(MIN(n.collectedAt))) AS INTEGER) AS collection_span_days,
        CAST((julianday(MAX(n.publishedDate)) - julianday(MIN(n.publishedDate))) AS INTEGER) AS publication_span_days,
        
        -- 최근 활동 강도
        COUNT(CASE WHEN n.collectedAt >= date('now', '-1 day') THEN 1 END) AS last_24h,
        COUNT(CASE WHEN n.collectedAt >= date('now', '-7 days') THEN 1 END) AS last_7d,
        COUNT(CASE WHEN n.collectedAt >= date('now', '-30 days') THEN 1 END) AS last_30d,
        COUNT(CASE WHEN n.collectedAt >= date('now', '-90 days') THEN 1 END) AS last_90d,
        COUNT(CASE WHEN n.collectedAt >= date('now', '-180 days') THEN 1 END) AS last_180d,
        COUNT(CASE WHEN n.collectedAt >= date('now', '-365 days') THEN 1 END) AS last_365d,
        
        -- 활동 연속성 분석
        COUNT(DISTINCT date(n.collectedAt)) AS active_days,
        MAX(n.collectedAt) AS latest_collection,
        MIN(n.collectedAt) AS earliest_collection,
        
        -- 카테고리별 선호도 점수
        COUNT(CASE WHEN n.category LIKE '%경제%' OR n.category LIKE '%금융%' THEN 1 END) AS economy_preference,
        COUNT(CASE WHEN n.category LIKE '%기술%' OR n.category LIKE '%IT%' THEN 1 END) AS tech_preference,
        COUNT(CASE WHEN n.category LIKE '%정치%' THEN 1 END) AS politics_preference,
        COUNT(CASE WHEN n.category LIKE '%스포츠%' THEN 1 END) AS sports_preference,
        COUNT(CASE WHEN n.category LIKE '%엔터테인먼트%' THEN 1 END) AS entertainment_preference
    FROM news n
    WHERE n.collectedAt >= date('now', '-2 years')
    GROUP BY n.userId
),

-- 라디오 노래 수집 심층 분석
radio_deep_analysis AS (
    SELECT 
        rs.userId,
        -- 기본 통계
        COUNT(*) AS total_songs_count,
        COUNT(DISTINCT rs.id) AS unique_songs_count,
        COUNT(DISTINCT rs.artist) AS artist_count,
        COUNT(DISTINCT rs.genre) AS genre_count,
        COUNT(DISTINCT rs.stations) AS station_count,
        COUNT(DISTINCT date(rs.lastPlayed)) AS play_days,
        
        -- 재생 통계
        SUM(rs.count) AS total_play_count,
        AVG(rs.count) AS avg_play_count,
        MAX(rs.count) AS max_play_count,
        MIN(rs.count) AS min_play_count,
        -- 재생 빈도 분포
        COUNT(CASE WHEN rs.count = 1 THEN 1 END) AS single_play_count,
        COUNT(CASE WHEN rs.count BETWEEN 2 AND 5 THEN 1 END) AS low_replay_count,
        COUNT(CASE WHEN rs.count BETWEEN 6 AND 10 THEN 1 END) AS medium_replay_count,
        COUNT(CASE WHEN rs.count > 10 THEN 1 END) AS high_replay_count,
        
        -- 시간대별 재생 분석 (24시간)
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 0 THEN 1 END) AS play_hour_00,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 1 THEN 1 END) AS play_hour_01,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 2 THEN 1 END) AS play_hour_02,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 3 THEN 1 END) AS play_hour_03,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 4 THEN 1 END) AS play_hour_04,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 5 THEN 1 END) AS play_hour_05,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 6 THEN 1 END) AS play_hour_06,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 7 THEN 1 END) AS play_hour_07,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 8 THEN 1 END) AS play_hour_08,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 9 THEN 1 END) AS play_hour_09,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 10 THEN 1 END) AS play_hour_10,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 11 THEN 1 END) AS play_hour_11,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 12 THEN 1 END) AS play_hour_12,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 13 THEN 1 END) AS play_hour_13,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 14 THEN 1 END) AS play_hour_14,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 15 THEN 1 END) AS play_hour_15,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 16 THEN 1 END) AS play_hour_16,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 17 THEN 1 END) AS play_hour_17,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 18 THEN 1 END) AS play_hour_18,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 19 THEN 1 END) AS play_hour_19,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 20 THEN 1 END) AS play_hour_20,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 21 THEN 1 END) AS play_hour_21,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 22 THEN 1 END) AS play_hour_22,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) = 23 THEN 1 END) AS play_hour_23,
        
        -- 요일별 재생 분석
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '0' THEN 1 END) AS play_sunday,
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '1' THEN 1 END) AS play_monday,
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '2' THEN 1 END) AS play_tuesday,
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '3' THEN 1 END) AS play_wednesday,
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '4' THEN 1 END) AS play_thursday,
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '5' THEN 1 END) AS play_friday,
        COUNT(CASE WHEN strftime('%w', rs.lastPlayed) = '6' THEN 1 END) AS play_saturday,
        
        -- 장르별 선호도 분석
        COUNT(CASE WHEN rs.genre LIKE '%팝%' OR rs.genre LIKE '%Pop%' THEN 1 END) AS pop_preference,
        COUNT(CASE WHEN rs.genre LIKE '%록%' OR rs.genre LIKE '%Rock%' THEN 1 END) AS rock_preference,
        COUNT(CASE WHEN rs.genre LIKE '%힙합%' OR rs.genre LIKE '%Hip%' THEN 1 END) AS hiphop_preference,
        COUNT(CASE WHEN rs.genre LIKE '%발라드%' OR rs.genre LIKE '%Ballad%' THEN 1 END) AS ballad_preference,
        COUNT(CASE WHEN rs.genre LIKE '%K-Pop%' OR rs.genre LIKE '%케이팝%' THEN 1 END) AS kpop_preference,
        COUNT(CASE WHEN rs.genre LIKE '%R&B%' OR rs.genre LIKE '%알앤비%' THEN 1 END) AS rnb_preference,
        
        -- 재생 기간 분석
        CAST((julianday(MAX(rs.lastPlayed)) - julianday(MIN(rs.firstPlayed))) AS INTEGER) AS listening_span_days,
        MAX(rs.lastPlayed) AS latest_play,
        MIN(rs.firstPlayed) AS earliest_play,
        
        -- 최근 활동 강도
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-1 day') THEN 1 END) AS last_24h_plays,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-7 days') THEN 1 END) AS last_7d_plays,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-30 days') THEN 1 END) AS last_30d_plays,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-90 days') THEN 1 END) AS last_90d_plays,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-180 days') THEN 1 END) AS last_180d_plays,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-365 days') THEN 1 END) AS last_365d_plays,
        
        -- 활동 연속성
        COUNT(DISTINCT date(rs.lastPlayed)) AS active_play_days
    FROM radioSongs rs
    WHERE rs.lastPlayed >= date('now', '-2 years')
    GROUP BY rs.userId
),

-- 도서 수집 심층 분석
books_deep_analysis AS (
    SELECT 
        b.userId,
        -- 기본 통계
        COUNT(*) AS total_books_count,
        COUNT(DISTINCT b.id) AS unique_books_count,
        COUNT(DISTINCT b.authors) AS author_count,
        COUNT(DISTINCT b.categories) AS category_count,
        
        -- 출판 연도 분석
        MIN(CAST(strftime('%Y', b.publishedDate) AS INTEGER)) AS oldest_year,
        MAX(CAST(strftime('%Y', b.publishedDate) AS INTEGER)) AS newest_year,
        AVG(CAST(strftime('%Y', b.publishedDate) AS INTEGER)) AS avg_publication_year,
        -- 출판 연도 분포
        COUNT(CASE WHEN CAST(strftime('%Y', b.publishedDate) AS INTEGER) >= 2020 THEN 1 END) AS recent_books_2020plus,
        COUNT(CASE WHEN CAST(strftime('%Y', b.publishedDate) AS INTEGER) BETWEEN 2010 AND 2019 THEN 1 END) AS books_2010s,
        COUNT(CASE WHEN CAST(strftime('%Y', b.publishedDate) AS INTEGER) BETWEEN 2000 AND 2009 THEN 1 END) AS books_2000s,
        COUNT(CASE WHEN CAST(strftime('%Y', b.publishedDate) AS INTEGER) < 2000 THEN 1 END) AS classic_books,
        
        -- 카테고리별 선호도
        COUNT(CASE WHEN b.categories LIKE '%소설%' OR b.categories LIKE '%Fiction%' THEN 1 END) AS fiction_preference,
        COUNT(CASE WHEN b.categories LIKE '%경제%' OR b.categories LIKE '%Business%' THEN 1 END) AS business_preference,
        COUNT(CASE WHEN b.categories LIKE '%과학%' OR b.categories LIKE '%Science%' THEN 1 END) AS science_preference,
        COUNT(CASE WHEN b.categories LIKE '%역사%' OR b.categories LIKE '%History%' THEN 1 END) AS history_preference,
        COUNT(CASE WHEN b.categories LIKE '%자기계발%' OR b.categories LIKE '%Self%' THEN 1 END) AS selfhelp_preference,
        COUNT(CASE WHEN b.categories LIKE '%기술%' OR b.categories LIKE '%Technology%' THEN 1 END) AS tech_preference,
        
        -- 수집 기간 분석
        CAST((julianday(MAX(b.collectedAt)) - julianday(MIN(b.collectedAt))) AS INTEGER) AS collection_span_days,
        MAX(b.collectedAt) AS latest_collection,
        MIN(b.collectedAt) AS earliest_collection,
        
        -- 최근 활동 강도
        COUNT(CASE WHEN b.collectedAt >= date('now', '-1 day') THEN 1 END) AS last_24h_collections,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-7 days') THEN 1 END) AS last_7d_collections,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-30 days') THEN 1 END) AS last_30d_collections,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-90 days') THEN 1 END) AS last_90d_collections,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-180 days') THEN 1 END) AS last_180d_collections,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-365 days') THEN 1 END) AS last_365d_collections,
        
        -- 활동 연속성
        COUNT(DISTINCT date(b.collectedAt)) AS active_collection_days
    FROM books b
    WHERE b.collectedAt >= date('now', '-2 years')
    GROUP BY b.userId
),

-- API 사용 심층 분석
api_deep_analysis AS (
    SELECT 
        ak.userId,
        -- API 키 관리 통계
        COUNT(DISTINCT ak.id) AS total_keys,
        COUNT(DISTINCT CASE WHEN ak.isActive = 1 THEN ak.id END) AS active_keys,
        COUNT(DISTINCT CASE WHEN ak.isActive = 0 THEN ak.id END) AS inactive_keys,
        COUNT(DISTINCT CASE WHEN ak.expiresAt IS NOT NULL AND ak.expiresAt > datetime('now') THEN ak.id END) AS valid_keys,
        COUNT(DISTINCT CASE WHEN ak.expiresAt IS NOT NULL AND ak.expiresAt <= datetime('now') THEN ak.id END) AS expired_keys,
        
        -- API 호출 통계
        COUNT(aku.id) AS total_calls,
        COUNT(DISTINCT aku.endpoint) AS endpoint_count,
        COUNT(DISTINCT aku.method) AS method_count,
        COUNT(DISTINCT aku.ipAddress) AS ip_count,
        COUNT(DISTINCT date(aku.createdAt)) AS call_days,
        
        -- HTTP 메서드별 분석
        COUNT(CASE WHEN aku.method = 'GET' THEN 1 END) AS get_calls,
        COUNT(CASE WHEN aku.method = 'POST' THEN 1 END) AS post_calls,
        COUNT(CASE WHEN aku.method = 'PUT' THEN 1 END) AS put_calls,
        COUNT(CASE WHEN aku.method = 'DELETE' THEN 1 END) AS delete_calls,
        COUNT(CASE WHEN aku.method = 'PATCH' THEN 1 END) AS patch_calls,
        
        -- 엔드포인트별 분석
        COUNT(CASE WHEN aku.endpoint LIKE '%/api/news%' THEN 1 END) AS news_endpoint_calls,
        COUNT(CASE WHEN aku.endpoint LIKE '%/api/music%' THEN 1 END) AS music_endpoint_calls,
        COUNT(CASE WHEN aku.endpoint LIKE '%/api/books%' THEN 1 END) AS books_endpoint_calls,
        COUNT(CASE WHEN aku.endpoint LIKE '%/api/user%' THEN 1 END) AS user_endpoint_calls,
        COUNT(CASE WHEN aku.endpoint LIKE '%/api/api-keys%' THEN 1 END) AS apikey_endpoint_calls,
        
        -- 상태 코드별 분석
        COUNT(CASE WHEN aku.statusCode BETWEEN 200 AND 299 THEN 1 END) AS success_2xx,
        COUNT(CASE WHEN aku.statusCode BETWEEN 300 AND 399 THEN 1 END) AS redirect_3xx,
        COUNT(CASE WHEN aku.statusCode BETWEEN 400 AND 499 THEN 1 END) AS client_error_4xx,
        COUNT(CASE WHEN aku.statusCode >= 500 THEN 1 END) AS server_error_5xx,
        
        -- 시간대별 호출 분석 (24시간)
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 0 THEN 1 END) AS api_hour_00,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 1 THEN 1 END) AS api_hour_01,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 2 THEN 1 END) AS api_hour_02,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 3 THEN 1 END) AS api_hour_03,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 4 THEN 1 END) AS api_hour_04,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 5 THEN 1 END) AS api_hour_05,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 6 THEN 1 END) AS api_hour_06,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 7 THEN 1 END) AS api_hour_07,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 8 THEN 1 END) AS api_hour_08,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 9 THEN 1 END) AS api_hour_09,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 10 THEN 1 END) AS api_hour_10,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 11 THEN 1 END) AS api_hour_11,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 12 THEN 1 END) AS api_hour_12,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 13 THEN 1 END) AS api_hour_13,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 14 THEN 1 END) AS api_hour_14,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 15 THEN 1 END) AS api_hour_15,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 16 THEN 1 END) AS api_hour_16,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 17 THEN 1 END) AS api_hour_17,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 18 THEN 1 END) AS api_hour_18,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 19 THEN 1 END) AS api_hour_19,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 20 THEN 1 END) AS api_hour_20,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 21 THEN 1 END) AS api_hour_21,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 22 THEN 1 END) AS api_hour_22,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) = 23 THEN 1 END) AS api_hour_23,
        
        -- 요일별 호출 분석
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '0' THEN 1 END) AS api_sunday,
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '1' THEN 1 END) AS api_monday,
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '2' THEN 1 END) AS api_tuesday,
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '3' THEN 1 END) AS api_wednesday,
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '4' THEN 1 END) AS api_thursday,
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '5' THEN 1 END) AS api_friday,
        COUNT(CASE WHEN strftime('%w', aku.createdAt) = '6' THEN 1 END) AS api_saturday,
        
        -- 최근 활동 강도
        COUNT(CASE WHEN aku.createdAt >= date('now', '-1 day') THEN 1 END) AS last_24h_calls,
        COUNT(CASE WHEN aku.createdAt >= date('now', '-7 days') THEN 1 END) AS last_7d_calls,
        COUNT(CASE WHEN aku.createdAt >= date('now', '-30 days') THEN 1 END) AS last_30d_calls,
        COUNT(CASE WHEN aku.createdAt >= date('now', '-90 days') THEN 1 END) AS last_90d_calls,
        COUNT(CASE WHEN aku.createdAt >= date('now', '-180 days') THEN 1 END) AS last_180d_calls,
        COUNT(CASE WHEN aku.createdAt >= date('now', '-365 days') THEN 1 END) AS last_365d_calls,
        
        -- 활동 연속성
        COUNT(DISTINCT date(aku.createdAt)) AS active_call_days,
        MAX(aku.createdAt) AS latest_call,
        MIN(aku.createdAt) AS earliest_call,
        
        -- 성공률 계산
        ROUND(CAST(COUNT(CASE WHEN aku.statusCode BETWEEN 200 AND 299 THEN 1 END) AS REAL) / 
              NULLIF(COUNT(aku.id), 0) * 100, 2) AS success_rate,
        ROUND(CAST(COUNT(CASE WHEN aku.statusCode >= 400 THEN 1 END) AS REAL) / 
              NULLIF(COUNT(aku.id), 0) * 100, 2) AS error_rate,
        AVG(aku.statusCode) AS avg_status_code
    FROM apiKeys ak
    LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId
    WHERE ak.createdAt >= date('now', '-2 years')
        OR (aku.createdAt IS NOT NULL AND aku.createdAt >= date('now', '-2 years'))
    GROUP BY ak.userId
),

-- ============================================
-- 2단계: 활동 점수 및 패턴 계산
-- ============================================

-- 종합 활동 점수 계산
comprehensive_activity_scores AS (
    SELECT 
        ul.user_id,
        -- 뉴스 활동 점수 (가중치 적용)
        COALESCE(nda.last_24h, 0) * 10 +
        COALESCE(nda.last_7d, 0) * 5 +
        COALESCE(nda.last_30d, 0) * 2 +
        COALESCE(nda.last_90d, 0) * 1 +
        COALESCE(nda.active_days, 0) * 0.5 +
        COALESCE(nda.category_count, 0) * 2 +
        COALESCE(nda.keyword_count, 0) * 1 AS news_score,
        
        -- 라디오 활동 점수
        COALESCE(rda.last_24h_plays, 0) * 10 +
        COALESCE(rda.last_7d_plays, 0) * 5 +
        COALESCE(rda.last_30d_plays, 0) * 2 +
        COALESCE(rda.last_90d_plays, 0) * 1 +
        COALESCE(rda.active_play_days, 0) * 0.5 +
        COALESCE(rda.artist_count, 0) * 2 +
        COALESCE(rda.genre_count, 0) * 1 +
        COALESCE(rda.total_play_count, 0) * 0.1 AS radio_score,
        
        -- 도서 활동 점수
        COALESCE(bda.last_24h_collections, 0) * 15 +
        COALESCE(bda.last_7d_collections, 0) * 8 +
        COALESCE(bda.last_30d_collections, 0) * 3 +
        COALESCE(bda.last_90d_collections, 0) * 1 +
        COALESCE(bda.active_collection_days, 0) * 0.5 +
        COALESCE(bda.author_count, 0) * 3 +
        COALESCE(bda.category_count, 0) * 2 AS books_score,
        
        -- API 활동 점수
        COALESCE(ada.last_24h_calls, 0) * 0.5 +
        COALESCE(ada.last_7d_calls, 0) * 0.3 +
        COALESCE(ada.last_30d_calls, 0) * 0.1 +
        COALESCE(ada.active_call_days, 0) * 0.05 +
        COALESCE(ada.endpoint_count, 0) * 2 +
        COALESCE(ada.success_rate, 0) * 0.1 AS api_score
    FROM user_lifecycle ul
    LEFT JOIN news_deep_analysis nda ON ul.user_id = nda.userId
    LEFT JOIN radio_deep_analysis rda ON ul.user_id = rda.userId
    LEFT JOIN books_deep_analysis bda ON ul.user_id = bda.userId
    LEFT JOIN api_deep_analysis ada ON ul.user_id = ada.userId
),

-- 사용자 행동 프로필 생성
user_behavior_profiles AS (
    SELECT 
        ul.user_id,
        ul.email,
        ul.name,
        ul.lifecycle_stage,
        ul.account_status,
        ul.account_age_days,
        
        -- 활동 점수
        COALESCE(cas.news_score, 0) AS news_activity_score,
        COALESCE(cas.radio_score, 0) AS radio_activity_score,
        COALESCE(cas.books_score, 0) AS books_activity_score,
        COALESCE(cas.api_score, 0) AS api_activity_score,
        
        -- 총 활동 점수
        COALESCE(cas.news_score, 0) +
        COALESCE(cas.radio_score, 0) +
        COALESCE(cas.books_score, 0) +
        COALESCE(cas.api_score, 0) AS total_activity_score,
        
        -- 활동 다양성 점수
        (
            CASE WHEN COALESCE(cas.news_score, 0) > 0 THEN 1 ELSE 0 END +
            CASE WHEN COALESCE(cas.radio_score, 0) > 0 THEN 1 ELSE 0 END +
            CASE WHEN COALESCE(cas.books_score, 0) > 0 THEN 1 ELSE 0 END +
            CASE WHEN COALESCE(cas.api_score, 0) > 0 THEN 1 ELSE 0 END
        ) AS diversity_score,
        
        -- 주요 활동 유형
        CASE 
            WHEN COALESCE(cas.news_score, 0) >= COALESCE(cas.radio_score, 0)
                AND COALESCE(cas.news_score, 0) >= COALESCE(cas.books_score, 0)
                AND COALESCE(cas.news_score, 0) >= COALESCE(cas.api_score, 0)
            THEN '뉴스 중심'
            WHEN COALESCE(cas.radio_score, 0) >= COALESCE(cas.news_score, 0)
                AND COALESCE(cas.radio_score, 0) >= COALESCE(cas.books_score, 0)
                AND COALESCE(cas.radio_score, 0) >= COALESCE(cas.api_score, 0)
            THEN '음악 중심'
            WHEN COALESCE(cas.books_score, 0) >= COALESCE(cas.news_score, 0)
                AND COALESCE(cas.books_score, 0) >= COALESCE(cas.radio_score, 0)
                AND COALESCE(cas.books_score, 0) >= COALESCE(cas.api_score, 0)
            THEN '독서 중심'
            WHEN COALESCE(cas.api_score, 0) >= COALESCE(cas.news_score, 0)
                AND COALESCE(cas.api_score, 0) >= COALESCE(cas.radio_score, 0)
                AND COALESCE(cas.api_score, 0) >= COALESCE(cas.books_score, 0)
            THEN '개발자'
            ELSE '균형형'
        END AS primary_activity_type
    FROM user_lifecycle ul
    LEFT JOIN comprehensive_activity_scores cas ON ul.user_id = cas.user_id
),

-- 시간대별 활동 패턴 통합 분석
time_pattern_comprehensive AS (
    SELECT 
        ubp.user_id,
        -- 뉴스 시간대 패턴 합계
        COALESCE(nda.hour_06, 0) + COALESCE(nda.hour_07, 0) + COALESCE(nda.hour_08, 0) + 
        COALESCE(nda.hour_09, 0) + COALESCE(nda.hour_10, 0) + COALESCE(nda.hour_11, 0) AS news_morning_total,
        COALESCE(nda.hour_12, 0) + COALESCE(nda.hour_13, 0) + COALESCE(nda.hour_14, 0) + 
        COALESCE(nda.hour_15, 0) + COALESCE(nda.hour_16, 0) + COALESCE(nda.hour_17, 0) AS news_afternoon_total,
        COALESCE(nda.hour_18, 0) + COALESCE(nda.hour_19, 0) + COALESCE(nda.hour_20, 0) + 
        COALESCE(nda.hour_21, 0) + COALESCE(nda.hour_22, 0) AS news_evening_total,
        COALESCE(nda.hour_23, 0) + COALESCE(nda.hour_00, 0) + COALESCE(nda.hour_01, 0) + 
        COALESCE(nda.hour_02, 0) + COALESCE(nda.hour_03, 0) + COALESCE(nda.hour_04, 0) + COALESCE(nda.hour_05, 0) AS news_night_total,
        
        -- 라디오 시간대 패턴 합계
        COALESCE(rda.play_hour_06, 0) + COALESCE(rda.play_hour_07, 0) + COALESCE(rda.play_hour_08, 0) + 
        COALESCE(rda.play_hour_09, 0) + COALESCE(rda.play_hour_10, 0) + COALESCE(rda.play_hour_11, 0) AS radio_morning_total,
        COALESCE(rda.play_hour_12, 0) + COALESCE(rda.play_hour_13, 0) + COALESCE(rda.play_hour_14, 0) + 
        COALESCE(rda.play_hour_15, 0) + COALESCE(rda.play_hour_16, 0) + COALESCE(rda.play_hour_17, 0) AS radio_afternoon_total,
        COALESCE(rda.play_hour_18, 0) + COALESCE(rda.play_hour_19, 0) + COALESCE(rda.play_hour_20, 0) + 
        COALESCE(rda.play_hour_21, 0) + COALESCE(rda.play_hour_22, 0) AS radio_evening_total,
        COALESCE(rda.play_hour_23, 0) + COALESCE(rda.play_hour_00, 0) + COALESCE(rda.play_hour_01, 0) + 
        COALESCE(rda.play_hour_02, 0) + COALESCE(rda.play_hour_03, 0) + COALESCE(rda.play_hour_04, 0) + COALESCE(rda.play_hour_05, 0) AS radio_night_total,
        
        -- API 시간대 패턴 합계
        COALESCE(ada.api_hour_06, 0) + COALESCE(ada.api_hour_07, 0) + COALESCE(ada.api_hour_08, 0) + 
        COALESCE(ada.api_hour_09, 0) + COALESCE(ada.api_hour_10, 0) + COALESCE(ada.api_hour_11, 0) AS api_morning_total,
        COALESCE(ada.api_hour_12, 0) + COALESCE(ada.api_hour_13, 0) + COALESCE(ada.api_hour_14, 0) + 
        COALESCE(ada.api_hour_15, 0) + COALESCE(ada.api_hour_16, 0) + COALESCE(ada.api_hour_17, 0) AS api_afternoon_total,
        COALESCE(ada.api_hour_18, 0) + COALESCE(ada.api_hour_19, 0) + COALESCE(ada.api_hour_20, 0) + 
        COALESCE(ada.api_hour_21, 0) + COALESCE(ada.api_hour_22, 0) AS api_evening_total,
        COALESCE(ada.api_hour_23, 0) + COALESCE(ada.api_hour_00, 0) + COALESCE(ada.api_hour_01, 0) + 
        COALESCE(ada.api_hour_02, 0) + COALESCE(ada.api_hour_03, 0) + COALESCE(ada.api_hour_04, 0) + COALESCE(ada.api_hour_05, 0) AS api_night_total,
        
        -- 종합 시간대 패턴
        (
            COALESCE(nda.hour_06, 0) + COALESCE(nda.hour_07, 0) + COALESCE(nda.hour_08, 0) + 
            COALESCE(nda.hour_09, 0) + COALESCE(nda.hour_10, 0) + COALESCE(nda.hour_11, 0) +
            COALESCE(rda.play_hour_06, 0) + COALESCE(rda.play_hour_07, 0) + COALESCE(rda.play_hour_08, 0) + 
            COALESCE(rda.play_hour_09, 0) + COALESCE(rda.play_hour_10, 0) + COALESCE(rda.play_hour_11, 0) +
            COALESCE(ada.api_hour_06, 0) + COALESCE(ada.api_hour_07, 0) + COALESCE(ada.api_hour_08, 0) + 
            COALESCE(ada.api_hour_09, 0) + COALESCE(ada.api_hour_10, 0) + COALESCE(ada.api_hour_11, 0)
        ) AS total_morning_activity,
        
        (
            COALESCE(nda.hour_12, 0) + COALESCE(nda.hour_13, 0) + COALESCE(nda.hour_14, 0) + 
            COALESCE(nda.hour_15, 0) + COALESCE(nda.hour_16, 0) + COALESCE(nda.hour_17, 0) +
            COALESCE(rda.play_hour_12, 0) + COALESCE(rda.play_hour_13, 0) + COALESCE(rda.play_hour_14, 0) + 
            COALESCE(rda.play_hour_15, 0) + COALESCE(rda.play_hour_16, 0) + COALESCE(rda.play_hour_17, 0) +
            COALESCE(ada.api_hour_12, 0) + COALESCE(ada.api_hour_13, 0) + COALESCE(ada.api_hour_14, 0) + 
            COALESCE(ada.api_hour_15, 0) + COALESCE(ada.api_hour_16, 0) + COALESCE(ada.api_hour_17, 0)
        ) AS total_afternoon_activity,
        
        (
            COALESCE(nda.hour_18, 0) + COALESCE(nda.hour_19, 0) + COALESCE(nda.hour_20, 0) + 
            COALESCE(nda.hour_21, 0) + COALESCE(nda.hour_22, 0) +
            COALESCE(rda.play_hour_18, 0) + COALESCE(rda.play_hour_19, 0) + COALESCE(rda.play_hour_20, 0) + 
            COALESCE(rda.play_hour_21, 0) + COALESCE(rda.play_hour_22, 0) +
            COALESCE(ada.api_hour_18, 0) + COALESCE(ada.api_hour_19, 0) + COALESCE(ada.api_hour_20, 0) + 
            COALESCE(ada.api_hour_21, 0) + COALESCE(ada.api_hour_22, 0)
        ) AS total_evening_activity,
        
        (
            COALESCE(nda.hour_23, 0) + COALESCE(nda.hour_00, 0) + COALESCE(nda.hour_01, 0) + 
            COALESCE(nda.hour_02, 0) + COALESCE(nda.hour_03, 0) + COALESCE(nda.hour_04, 0) + COALESCE(nda.hour_05, 0) +
            COALESCE(rda.play_hour_23, 0) + COALESCE(rda.play_hour_00, 0) + COALESCE(rda.play_hour_01, 0) + 
            COALESCE(rda.play_hour_02, 0) + COALESCE(rda.play_hour_03, 0) + COALESCE(rda.play_hour_04, 0) + COALESCE(rda.play_hour_05, 0) +
            COALESCE(ada.api_hour_23, 0) + COALESCE(ada.api_hour_00, 0) + COALESCE(ada.api_hour_01, 0) + 
            COALESCE(ada.api_hour_02, 0) + COALESCE(ada.api_hour_03, 0) + COALESCE(ada.api_hour_04, 0) + COALESCE(ada.api_hour_05, 0)
        ) AS total_night_activity,
        
        -- 주요 활동 시간대 결정
        CASE 
            WHEN (
                COALESCE(nda.hour_06, 0) + COALESCE(nda.hour_07, 0) + COALESCE(nda.hour_08, 0) + 
                COALESCE(nda.hour_09, 0) + COALESCE(nda.hour_10, 0) + COALESCE(nda.hour_11, 0) +
                COALESCE(rda.play_hour_06, 0) + COALESCE(rda.play_hour_07, 0) + COALESCE(rda.play_hour_08, 0) + 
                COALESCE(rda.play_hour_09, 0) + COALESCE(rda.play_hour_10, 0) + COALESCE(rda.play_hour_11, 0) +
                COALESCE(ada.api_hour_06, 0) + COALESCE(ada.api_hour_07, 0) + COALESCE(ada.api_hour_08, 0) + 
                COALESCE(ada.api_hour_09, 0) + COALESCE(ada.api_hour_10, 0) + COALESCE(ada.api_hour_11, 0)
            ) >= GREATEST(
                COALESCE(nda.hour_12, 0) + COALESCE(nda.hour_13, 0) + COALESCE(nda.hour_14, 0) + 
                COALESCE(nda.hour_15, 0) + COALESCE(nda.hour_16, 0) + COALESCE(nda.hour_17, 0) +
                COALESCE(rda.play_hour_12, 0) + COALESCE(rda.play_hour_13, 0) + COALESCE(rda.play_hour_14, 0) + 
                COALESCE(rda.play_hour_15, 0) + COALESCE(rda.play_hour_16, 0) + COALESCE(rda.play_hour_17, 0) +
                COALESCE(ada.api_hour_12, 0) + COALESCE(ada.api_hour_13, 0) + COALESCE(ada.api_hour_14, 0) + 
                COALESCE(ada.api_hour_15, 0) + COALESCE(ada.api_hour_16, 0) + COALESCE(ada.api_hour_17, 0),
                COALESCE(nda.hour_18, 0) + COALESCE(nda.hour_19, 0) + COALESCE(nda.hour_20, 0) + 
                COALESCE(nda.hour_21, 0) + COALESCE(nda.hour_22, 0) +
                COALESCE(rda.play_hour_18, 0) + COALESCE(rda.play_hour_19, 0) + COALESCE(rda.play_hour_20, 0) + 
                COALESCE(rda.play_hour_21, 0) + COALESCE(rda.play_hour_22, 0) +
                COALESCE(ada.api_hour_18, 0) + COALESCE(ada.api_hour_19, 0) + COALESCE(ada.api_hour_20, 0) + 
                COALESCE(ada.api_hour_21, 0) + COALESCE(ada.api_hour_22, 0),
                COALESCE(nda.hour_23, 0) + COALESCE(nda.hour_00, 0) + COALESCE(nda.hour_01, 0) + 
                COALESCE(nda.hour_02, 0) + COALESCE(nda.hour_03, 0) + COALESCE(nda.hour_04, 0) + COALESCE(nda.hour_05, 0) +
                COALESCE(rda.play_hour_23, 0) + COALESCE(rda.play_hour_00, 0) + COALESCE(rda.play_hour_01, 0) + 
                COALESCE(rda.play_hour_02, 0) + COALESCE(rda.play_hour_03, 0) + COALESCE(rda.play_hour_04, 0) + COALESCE(rda.play_hour_05, 0) +
                COALESCE(ada.api_hour_23, 0) + COALESCE(ada.api_hour_00, 0) + COALESCE(ada.api_hour_01, 0) + 
                COALESCE(ada.api_hour_02, 0) + COALESCE(ada.api_hour_03, 0) + COALESCE(ada.api_hour_04, 0) + COALESCE(ada.api_hour_05, 0)
            )
            THEN '아침형'
            WHEN (
                COALESCE(nda.hour_12, 0) + COALESCE(nda.hour_13, 0) + COALESCE(nda.hour_14, 0) + 
                COALESCE(nda.hour_15, 0) + COALESCE(nda.hour_16, 0) + COALESCE(nda.hour_17, 0) +
                COALESCE(rda.play_hour_12, 0) + COALESCE(rda.play_hour_13, 0) + COALESCE(rda.play_hour_14, 0) + 
                COALESCE(rda.play_hour_15, 0) + COALESCE(rda.play_hour_16, 0) + COALESCE(rda.play_hour_17, 0) +
                COALESCE(ada.api_hour_12, 0) + COALESCE(ada.api_hour_13, 0) + COALESCE(ada.api_hour_14, 0) + 
                COALESCE(ada.api_hour_15, 0) + COALESCE(ada.api_hour_16, 0) + COALESCE(ada.api_hour_17, 0)
            ) >= GREATEST(
                COALESCE(nda.hour_18, 0) + COALESCE(nda.hour_19, 0) + COALESCE(nda.hour_20, 0) + 
                COALESCE(nda.hour_21, 0) + COALESCE(nda.hour_22, 0) +
                COALESCE(rda.play_hour_18, 0) + COALESCE(rda.play_hour_19, 0) + COALESCE(rda.play_hour_20, 0) + 
                COALESCE(rda.play_hour_21, 0) + COALESCE(rda.play_hour_22, 0) +
                COALESCE(ada.api_hour_18, 0) + COALESCE(ada.api_hour_19, 0) + COALESCE(ada.api_hour_20, 0) + 
                COALESCE(ada.api_hour_21, 0) + COALESCE(ada.api_hour_22, 0),
                COALESCE(nda.hour_23, 0) + COALESCE(nda.hour_00, 0) + COALESCE(nda.hour_01, 0) + 
                COALESCE(nda.hour_02, 0) + COALESCE(nda.hour_03, 0) + COALESCE(nda.hour_04, 0) + COALESCE(nda.hour_05, 0) +
                COALESCE(rda.play_hour_23, 0) + COALESCE(rda.play_hour_00, 0) + COALESCE(rda.play_hour_01, 0) + 
                COALESCE(rda.play_hour_02, 0) + COALESCE(rda.play_hour_03, 0) + COALESCE(rda.play_hour_04, 0) + COALESCE(rda.play_hour_05, 0) +
                COALESCE(ada.api_hour_23, 0) + COALESCE(ada.api_hour_00, 0) + COALESCE(ada.api_hour_01, 0) + 
                COALESCE(ada.api_hour_02, 0) + COALESCE(ada.api_hour_03, 0) + COALESCE(ada.api_hour_04, 0) + COALESCE(ada.api_hour_05, 0)
            )
            THEN '오후형'
            WHEN (
                COALESCE(nda.hour_18, 0) + COALESCE(nda.hour_19, 0) + COALESCE(nda.hour_20, 0) + 
                COALESCE(nda.hour_21, 0) + COALESCE(nda.hour_22, 0) +
                COALESCE(rda.play_hour_18, 0) + COALESCE(rda.play_hour_19, 0) + COALESCE(rda.play_hour_20, 0) + 
                COALESCE(rda.play_hour_21, 0) + COALESCE(rda.play_hour_22, 0) +
                COALESCE(ada.api_hour_18, 0) + COALESCE(ada.api_hour_19, 0) + COALESCE(ada.api_hour_20, 0) + 
                COALESCE(ada.api_hour_21, 0) + COALESCE(ada.api_hour_22, 0)
            ) >= (
                COALESCE(nda.hour_23, 0) + COALESCE(nda.hour_00, 0) + COALESCE(nda.hour_01, 0) + 
                COALESCE(nda.hour_02, 0) + COALESCE(nda.hour_03, 0) + COALESCE(nda.hour_04, 0) + COALESCE(nda.hour_05, 0) +
                COALESCE(rda.play_hour_23, 0) + COALESCE(rda.play_hour_00, 0) + COALESCE(rda.play_hour_01, 0) + 
                COALESCE(rda.play_hour_02, 0) + COALESCE(rda.play_hour_03, 0) + COALESCE(rda.play_hour_04, 0) + COALESCE(rda.play_hour_05, 0) +
                COALESCE(ada.api_hour_23, 0) + COALESCE(ada.api_hour_00, 0) + COALESCE(ada.api_hour_01, 0) + 
                COALESCE(ada.api_hour_02, 0) + COALESCE(ada.api_hour_03, 0) + COALESCE(ada.api_hour_04, 0) + COALESCE(ada.api_hour_05, 0)
            )
            THEN '저녁형'
            ELSE '야행형'
        END AS preferred_time_period
    FROM user_behavior_profiles ubp
    LEFT JOIN news_deep_analysis nda ON ubp.user_id = nda.userId
    LEFT JOIN radio_deep_analysis rda ON ubp.user_id = rda.userId
    LEFT JOIN api_deep_analysis ada ON ubp.user_id = ada.userId
)

-- ============================================
-- 3. 메인 쿼리: 초고급 종합 분석 리포트
-- ============================================

SELECT 
    -- 기본 정보
    ubp.user_id,
    ubp.email,
    ubp.name,
    ubp.lifecycle_stage,
    ubp.account_status,
    ubp.account_age_days,
    
    -- 활동 점수
    ROUND(ubp.news_activity_score, 2) AS news_score,
    ROUND(ubp.radio_activity_score, 2) AS radio_score,
    ROUND(ubp.books_activity_score, 2) AS books_score,
    ROUND(ubp.api_activity_score, 2) AS api_score,
    ROUND(ubp.total_activity_score, 2) AS total_score,
    ubp.diversity_score,
    ubp.primary_activity_type,
    
    -- 뉴스 상세 분석
    nda.total_news_count,
    nda.category_count AS news_categories,
    nda.keyword_count AS news_keywords,
    nda.source_count AS news_sources,
    nda.collection_days AS news_active_days,
    ROUND(nda.avg_importance, 2) AS news_avg_importance,
    nda.high_importance_count AS news_high_importance,
    nda.collection_span_days AS news_span_days,
    nda.last_24h AS news_last_24h,
    nda.last_7d AS news_last_7d,
    nda.last_30d AS news_last_30d,
    nda.last_90d AS news_last_90d,
    -- 뉴스 시간대 패턴
    nda.hour_06 + nda.hour_07 + nda.hour_08 + nda.hour_09 + nda.hour_10 + nda.hour_11 AS news_morning_hours,
    nda.hour_12 + nda.hour_13 + nda.hour_14 + nda.hour_15 + nda.hour_16 + nda.hour_17 AS news_afternoon_hours,
    nda.hour_18 + nda.hour_19 + nda.hour_20 + nda.hour_21 + nda.hour_22 AS news_evening_hours,
    nda.hour_23 + nda.hour_00 + nda.hour_01 + nda.hour_02 + nda.hour_03 + nda.hour_04 + nda.hour_05 AS news_night_hours,
    -- 뉴스 요일 패턴
    nda.monday_count + nda.tuesday_count + nda.wednesday_count + 
    nda.thursday_count + nda.friday_count AS news_weekday_count,
    nda.saturday_count + nda.sunday_count AS news_weekend_count,
    -- 뉴스 카테고리 선호도
    nda.economy_preference,
    nda.tech_preference,
    nda.politics_preference,
    nda.sports_preference,
    nda.entertainment_preference,
    
    -- 라디오 상세 분석
    rda.total_songs_count,
    rda.artist_count AS radio_artists,
    rda.genre_count AS radio_genres,
    rda.station_count AS radio_stations,
    rda.play_days AS radio_active_days,
    rda.total_play_count AS radio_total_plays,
    ROUND(rda.avg_play_count, 2) AS radio_avg_plays,
    rda.max_play_count AS radio_max_plays,
    rda.single_play_count AS radio_single_plays,
    rda.low_replay_count AS radio_low_replays,
    rda.medium_replay_count AS radio_medium_replays,
    rda.high_replay_count AS radio_high_replays,
    rda.listening_span_days AS radio_span_days,
    rda.last_24h_plays AS radio_last_24h,
    rda.last_7d_plays AS radio_last_7d,
    rda.last_30d_plays AS radio_last_30d,
    rda.last_90d_plays AS radio_last_90d,
    -- 라디오 시간대 패턴
    rda.play_hour_06 + rda.play_hour_07 + rda.play_hour_08 + rda.play_hour_09 + rda.play_hour_10 + rda.play_hour_11 AS radio_morning_hours,
    rda.play_hour_12 + rda.play_hour_13 + rda.play_hour_14 + rda.play_hour_15 + rda.play_hour_16 + rda.play_hour_17 AS radio_afternoon_hours,
    rda.play_hour_18 + rda.play_hour_19 + rda.play_hour_20 + rda.play_hour_21 + rda.play_hour_22 AS radio_evening_hours,
    rda.play_hour_23 + rda.play_hour_00 + rda.play_hour_01 + rda.play_hour_02 + rda.play_hour_03 + rda.play_hour_04 + rda.play_hour_05 AS radio_night_hours,
    -- 라디오 요일 패턴
    rda.play_monday + rda.play_tuesday + rda.play_wednesday + 
    rda.play_thursday + rda.play_friday AS radio_weekday_plays,
    rda.play_saturday + rda.play_sunday AS radio_weekend_plays,
    -- 라디오 장르 선호도
    rda.pop_preference,
    rda.rock_preference,
    rda.hiphop_preference,
    rda.ballad_preference,
    rda.kpop_preference,
    rda.rnb_preference,
    
    -- 도서 상세 분석
    bda.total_books_count,
    bda.author_count AS books_authors,
    bda.category_count AS books_categories,
    bda.oldest_year AS books_oldest_year,
    bda.newest_year AS books_newest_year,
    ROUND(bda.avg_publication_year, 0) AS books_avg_year,
    bda.recent_books_2020plus AS books_recent,
    bda.books_2010s,
    bda.books_2000s,
    bda.classic_books,
    bda.collection_span_days AS books_span_days,
    bda.last_24h_collections AS books_last_24h,
    bda.last_7d_collections AS books_last_7d,
    bda.last_30d_collections AS books_last_30d,
    bda.last_90d_collections AS books_last_90d,
    -- 도서 카테고리 선호도
    bda.fiction_preference,
    bda.business_preference,
    bda.science_preference,
    bda.history_preference,
    bda.selfhelp_preference,
    bda.tech_preference AS books_tech_preference,
    
    -- API 상세 분석
    ada.total_keys AS api_total_keys,
    ada.active_keys AS api_active_keys,
    ada.inactive_keys AS api_inactive_keys,
    ada.valid_keys AS api_valid_keys,
    ada.expired_keys AS api_expired_keys,
    ada.total_calls AS api_total_calls,
    ada.endpoint_count AS api_endpoints,
    ada.method_count AS api_methods,
    ada.ip_count AS api_ips,
    ada.call_days AS api_active_days,
    -- API 메서드별 분석
    ada.get_calls AS api_get_calls,
    ada.post_calls AS api_post_calls,
    ada.put_calls AS api_put_calls,
    ada.delete_calls AS api_delete_calls,
    ada.patch_calls AS api_patch_calls,
    -- API 엔드포인트별 분석
    ada.news_endpoint_calls,
    ada.music_endpoint_calls,
    ada.books_endpoint_calls,
    ada.user_endpoint_calls,
    ada.apikey_endpoint_calls,
    -- API 상태 코드 분석
    ada.success_2xx AS api_success_calls,
    ada.redirect_3xx AS api_redirect_calls,
    ada.client_error_4xx AS api_client_errors,
    ada.server_error_5xx AS api_server_errors,
    ROUND(ada.success_rate, 2) AS api_success_rate,
    ROUND(ada.error_rate, 2) AS api_error_rate,
    ROUND(ada.avg_status_code, 2) AS api_avg_status,
    ada.last_24h_calls AS api_last_24h,
    ada.last_7d_calls AS api_last_7d,
    ada.last_30d_calls AS api_last_30d,
    ada.last_90d_calls AS api_last_90d,
    -- API 시간대 패턴
    ada.api_hour_06 + ada.api_hour_07 + ada.api_hour_08 + ada.api_hour_09 + ada.api_hour_10 + ada.api_hour_11 AS api_morning_hours,
    ada.api_hour_12 + ada.api_hour_13 + ada.api_hour_14 + ada.api_hour_15 + ada.api_hour_16 + ada.api_hour_17 AS api_afternoon_hours,
    ada.api_hour_18 + ada.api_hour_19 + ada.api_hour_20 + ada.api_hour_21 + ada.api_hour_22 AS api_evening_hours,
    ada.api_hour_23 + ada.api_hour_00 + ada.api_hour_01 + ada.api_hour_02 + ada.api_hour_03 + ada.api_hour_04 + ada.api_hour_05 AS api_night_hours,
    -- API 요일 패턴
    ada.api_monday + ada.api_tuesday + ada.api_wednesday + 
    ada.api_thursday + ada.api_friday AS api_weekday_calls,
    ada.api_saturday + ada.api_sunday AS api_weekend_calls,
    
    -- 시간대 패턴 통합
    tpc.total_morning_activity,
    tpc.total_afternoon_activity,
    tpc.total_evening_activity,
    tpc.total_night_activity,
    tpc.preferred_time_period,
    
    -- 예측 및 추천
    CASE 
        WHEN ubp.total_activity_score > 200 
            AND ubp.diversity_score >= 3
            AND ubp.account_age_days > 180
            AND (nda.last_7d > 10 OR rda.last_7d_plays > 20 OR bda.last_7d_collections > 5 OR ada.last_7d_calls > 50)
        THEN '매우 높음'
        WHEN ubp.total_activity_score > 100
            AND ubp.diversity_score >= 2
            AND ubp.account_age_days > 90
            AND (nda.last_30d > 20 OR rda.last_30d_plays > 40 OR bda.last_30d_collections > 10 OR ada.last_30d_calls > 100)
        THEN '높음'
        WHEN ubp.total_activity_score > 50
            AND ubp.account_age_days > 30
        THEN '보통'
        WHEN ubp.total_activity_score > 0
        THEN '낮음'
        ELSE '매우 낮음'
    END AS retention_prediction,
    
    CASE 
        WHEN ubp.news_activity_score < ubp.radio_activity_score 
            AND ubp.news_activity_score < ubp.books_activity_score
            AND ubp.news_activity_score < ubp.api_activity_score
        THEN '뉴스 수집 기능 활용 권장'
        WHEN ubp.radio_activity_score < ubp.news_activity_score
            AND ubp.radio_activity_score < ubp.books_activity_score
            AND ubp.radio_activity_score < ubp.api_activity_score
        THEN '음악 탐색 기능 활용 권장'
        WHEN ubp.books_activity_score < ubp.news_activity_score
            AND ubp.books_activity_score < ubp.radio_activity_score
            AND ubp.books_activity_score < ubp.api_activity_score
        THEN '도서 검색 기능 활용 권장'
        WHEN ubp.api_activity_score < ubp.news_activity_score
            AND ubp.api_activity_score < ubp.radio_activity_score
            AND ubp.api_activity_score < ubp.books_activity_score
        THEN 'API 개발 기능 활용 권장'
        ELSE '현재 활동 패턴 유지 권장'
    END AS activity_recommendation,
    
    -- 사용자 세그먼트 분류
    CASE 
        WHEN ubp.total_activity_score > 200 
            AND ubp.diversity_score >= 3
            AND ubp.account_age_days > 180
        THEN '파워 유저'
        WHEN ubp.total_activity_score > 100
            AND ubp.diversity_score >= 2
            AND ubp.account_age_days > 90
        THEN '활성 유저'
        WHEN ubp.total_activity_score > 50
            AND ubp.account_age_days > 30
        THEN '일반 유저'
        WHEN ubp.total_activity_score > 0
        THEN '신규 유저'
        ELSE '비활성 유저'
    END AS user_segment

FROM user_behavior_profiles ubp
LEFT JOIN news_deep_analysis nda ON ubp.user_id = nda.userId
LEFT JOIN radio_deep_analysis rda ON ubp.user_id = rda.userId
LEFT JOIN books_deep_analysis bda ON ubp.user_id = bda.userId
LEFT JOIN api_deep_analysis ada ON ubp.user_id = ada.userId
LEFT JOIN time_pattern_comprehensive tpc ON ubp.user_id = tpc.user_id

WHERE 
    ubp.total_activity_score > 0
    AND ubp.account_age_days > 7

GROUP BY 
    ubp.user_id, ubp.email, ubp.name, ubp.lifecycle_stage, ubp.account_status, ubp.account_age_days,
    ubp.news_activity_score, ubp.radio_activity_score, ubp.books_activity_score, ubp.api_activity_score,
    ubp.total_activity_score, ubp.diversity_score, ubp.primary_activity_type,
    nda.total_news_count, nda.category_count, nda.keyword_count, nda.source_count, nda.collection_days,
    nda.avg_importance, nda.high_importance_count, nda.collection_span_days,
    nda.last_24h, nda.last_7d, nda.last_30d, nda.last_90d,
    nda.hour_06, nda.hour_07, nda.hour_08, nda.hour_09, nda.hour_10, nda.hour_11,
    nda.hour_12, nda.hour_13, nda.hour_14, nda.hour_15, nda.hour_16, nda.hour_17,
    nda.hour_18, nda.hour_19, nda.hour_20, nda.hour_21, nda.hour_22,
    nda.hour_23, nda.hour_00, nda.hour_01, nda.hour_02, nda.hour_03, nda.hour_04, nda.hour_05,
    nda.monday_count, nda.tuesday_count, nda.wednesday_count, nda.thursday_count, nda.friday_count,
    nda.saturday_count, nda.sunday_count,
    nda.economy_preference, nda.tech_preference, nda.politics_preference, nda.sports_preference, nda.entertainment_preference,
    rda.total_songs_count, rda.artist_count, rda.genre_count, rda.station_count, rda.play_days,
    rda.total_play_count, rda.avg_play_count, rda.max_play_count,
    rda.single_play_count, rda.low_replay_count, rda.medium_replay_count, rda.high_replay_count,
    rda.listening_span_days, rda.last_24h_plays, rda.last_7d_plays, rda.last_30d_plays, rda.last_90d_plays,
    rda.play_hour_06, rda.play_hour_07, rda.play_hour_08, rda.play_hour_09, rda.play_hour_10, rda.play_hour_11,
    rda.play_hour_12, rda.play_hour_13, rda.play_hour_14, rda.play_hour_15, rda.play_hour_16, rda.play_hour_17,
    rda.play_hour_18, rda.play_hour_19, rda.play_hour_20, rda.play_hour_21, rda.play_hour_22,
    rda.play_hour_23, rda.play_hour_00, rda.play_hour_01, rda.play_hour_02, rda.play_hour_03, rda.play_hour_04, rda.play_hour_05,
    rda.play_monday, rda.play_tuesday, rda.play_wednesday, rda.play_thursday, rda.play_friday,
    rda.play_saturday, rda.play_sunday,
    rda.pop_preference, rda.rock_preference, rda.hiphop_preference, rda.ballad_preference, rda.kpop_preference, rda.rnb_preference,
    bda.total_books_count, bda.author_count, bda.category_count,
    bda.oldest_year, bda.newest_year, bda.avg_publication_year,
    bda.recent_books_2020plus, bda.books_2010s, bda.books_2000s, bda.classic_books,
    bda.collection_span_days, bda.last_24h_collections, bda.last_7d_collections, bda.last_30d_collections, bda.last_90d_collections,
    bda.fiction_preference, bda.business_preference, bda.science_preference, bda.history_preference, bda.selfhelp_preference, bda.tech_preference,
    ada.total_keys, ada.active_keys, ada.inactive_keys, ada.valid_keys, ada.expired_keys,
    ada.total_calls, ada.endpoint_count, ada.method_count, ada.ip_count, ada.call_days,
    ada.get_calls, ada.post_calls, ada.put_calls, ada.delete_calls, ada.patch_calls,
    ada.news_endpoint_calls, ada.music_endpoint_calls, ada.books_endpoint_calls, ada.user_endpoint_calls, ada.apikey_endpoint_calls,
    ada.success_2xx, ada.redirect_3xx, ada.client_error_4xx, ada.server_error_5xx,
    ada.success_rate, ada.error_rate, ada.avg_status_code,
    ada.last_24h_calls, ada.last_7d_calls, ada.last_30d_calls, ada.last_90d_calls,
    ada.api_hour_06, ada.api_hour_07, ada.api_hour_08, ada.api_hour_09, ada.api_hour_10, ada.api_hour_11,
    ada.api_hour_12, ada.api_hour_13, ada.api_hour_14, ada.api_hour_15, ada.api_hour_16, ada.api_hour_17,
    ada.api_hour_18, ada.api_hour_19, ada.api_hour_20, ada.api_hour_21, ada.api_hour_22,
    ada.api_hour_23, ada.api_hour_00, ada.api_hour_01, ada.api_hour_02, ada.api_hour_03, ada.api_hour_04, ada.api_hour_05,
    ada.api_monday, ada.api_tuesday, ada.api_wednesday, ada.api_thursday, ada.api_friday,
    ada.api_saturday, ada.api_sunday,
    tpc.total_morning_activity, tpc.total_afternoon_activity, tpc.total_evening_activity, tpc.total_night_activity,
    tpc.preferred_time_period

ORDER BY 
    ubp.total_activity_score DESC,
    ubp.diversity_score DESC,
    ubp.account_age_days DESC

LIMIT 500;

-- ============================================
-- 4. 추가 분석 쿼리: 트렌드 분석
-- ============================================

-- 월별 활동 트렌드 분석
SELECT 
    strftime('%Y-%m', n.collectedAt) AS activity_month,
    'news' AS activity_type,
    COUNT(*) AS activity_count,
    COUNT(DISTINCT n.userId) AS active_users,
    AVG(n.importanceValue) AS avg_importance
FROM news n
WHERE n.collectedAt >= date('now', '-2 years')
GROUP BY strftime('%Y-%m', n.collectedAt)

UNION ALL

SELECT 
    strftime('%Y-%m', rs.lastPlayed) AS activity_month,
    'radio' AS activity_type,
    COUNT(*) AS activity_count,
    COUNT(DISTINCT rs.userId) AS active_users,
    AVG(rs.count) AS avg_importance
FROM radioSongs rs
WHERE rs.lastPlayed >= date('now', '-2 years')
GROUP BY strftime('%Y-%m', rs.lastPlayed)

UNION ALL

SELECT 
    strftime('%Y-%m', b.collectedAt) AS activity_month,
    'books' AS activity_type,
    COUNT(*) AS activity_count,
    COUNT(DISTINCT b.userId) AS active_users,
    NULL AS avg_importance
FROM books b
WHERE b.collectedAt >= date('now', '-2 years')
GROUP BY strftime('%Y-%m', b.collectedAt)

UNION ALL

SELECT 
    strftime('%Y-%m', aku.createdAt) AS activity_month,
    'api' AS activity_type,
    COUNT(*) AS activity_count,
    COUNT(DISTINCT ak.userId) AS active_users,
    AVG(aku.statusCode) AS avg_importance
FROM apiKeyUsage aku
INNER JOIN apiKeys ak ON aku.apiKeyId = ak.id
WHERE aku.createdAt >= date('now', '-2 years')
GROUP BY strftime('%Y-%m', aku.createdAt)

ORDER BY activity_month DESC, activity_type;

-- ============================================
-- 5. 추가 분석: 상세 시간대별 활동 히트맵 데이터
-- ============================================

-- 시간대별 활동 히트맵 생성 (24시간 x 7일)
SELECT 
    u.id AS user_id,
    u.email,
    -- 시간대별 요일별 활동 매트릭스
    -- 월요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 0 THEN 1 END) AS mon_00,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 1 THEN 1 END) AS mon_01,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 2 THEN 1 END) AS mon_02,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 3 THEN 1 END) AS mon_03,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 4 THEN 1 END) AS mon_04,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 5 THEN 1 END) AS mon_05,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 6 THEN 1 END) AS mon_06,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 7 THEN 1 END) AS mon_07,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 8 THEN 1 END) AS mon_08,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 9 THEN 1 END) AS mon_09,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 10 THEN 1 END) AS mon_10,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 11 THEN 1 END) AS mon_11,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 12 THEN 1 END) AS mon_12,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 13 THEN 1 END) AS mon_13,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 14 THEN 1 END) AS mon_14,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 15 THEN 1 END) AS mon_15,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 16 THEN 1 END) AS mon_16,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 17 THEN 1 END) AS mon_17,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 18 THEN 1 END) AS mon_18,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 19 THEN 1 END) AS mon_19,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 20 THEN 1 END) AS mon_20,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 21 THEN 1 END) AS mon_21,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 22 THEN 1 END) AS mon_22,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) = 23 THEN 1 END) AS mon_23,
    -- 화요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS tue_night,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS tue_morning,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS tue_afternoon,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS tue_evening,
    -- 수요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS wed_night,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS wed_morning,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS wed_afternoon,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS wed_evening,
    -- 목요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS thu_night,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS thu_morning,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS thu_afternoon,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS thu_evening,
    -- 금요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS fri_night,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS fri_morning,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS fri_afternoon,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS fri_evening,
    -- 토요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS sat_night,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS sat_morning,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS sat_afternoon,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS sat_evening,
    -- 일요일
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS sun_night,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS sun_morning,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS sun_afternoon,
    COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' AND CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS sun_evening
FROM users u
LEFT JOIN news n ON u.id = n.userId AND n.collectedAt >= date('now', '-3 months')
WHERE u.createdAt >= date('now', '-1 year')
GROUP BY u.id, u.email
HAVING COUNT(n.id) > 0
ORDER BY COUNT(n.id) DESC
LIMIT 200;

-- ============================================
-- 6. 추가 분석: 상관관계 분석 (확장)
-- ============================================

-- 사용자 활동 간 상관관계 분석
SELECT 
    ubp1.user_id,
    ubp1.email,
    -- 뉴스-라디오 상관관계
    CASE 
        WHEN ubp1.news_activity_score > 0 AND ubp1.radio_activity_score > 0 THEN '양의 상관관계'
        WHEN ubp1.news_activity_score > 0 AND ubp1.radio_activity_score = 0 THEN '뉴스 단독'
        WHEN ubp1.news_activity_score = 0 AND ubp1.radio_activity_score > 0 THEN '라디오 단독'
        ELSE '활동 없음'
    END AS news_radio_correlation,
    -- 뉴스-도서 상관관계
    CASE 
        WHEN ubp1.news_activity_score > 0 AND ubp1.books_activity_score > 0 THEN '양의 상관관계'
        WHEN ubp1.news_activity_score > 0 AND ubp1.books_activity_score = 0 THEN '뉴스 단독'
        WHEN ubp1.news_activity_score = 0 AND ubp1.books_activity_score > 0 THEN '도서 단독'
        ELSE '활동 없음'
    END AS news_books_correlation,
    -- 라디오-도서 상관관계
    CASE 
        WHEN ubp1.radio_activity_score > 0 AND ubp1.books_activity_score > 0 THEN '양의 상관관계'
        WHEN ubp1.radio_activity_score > 0 AND ubp1.books_activity_score = 0 THEN '라디오 단독'
        WHEN ubp1.radio_activity_score = 0 AND ubp1.books_activity_score > 0 THEN '도서 단독'
        ELSE '활동 없음'
    END AS radio_books_correlation,
    -- API-다른 활동 상관관계
    CASE 
        WHEN ubp1.api_activity_score > 0 
            AND (ubp1.news_activity_score > 0 OR ubp1.radio_activity_score > 0 OR ubp1.books_activity_score > 0)
        THEN '통합 사용자'
        WHEN ubp1.api_activity_score > 0 
            AND ubp1.news_activity_score = 0 
            AND ubp1.radio_activity_score = 0 
            AND ubp1.books_activity_score = 0
        THEN 'API 전용'
        ELSE '일반 사용자'
    END AS api_integration_type
FROM user_behavior_profiles ubp1
WHERE ubp1.total_activity_score > 0
ORDER BY ubp1.total_activity_score DESC
LIMIT 300;

-- ============================================
-- 7. 추가 분석: 고급 윈도우 함수 분석
-- ============================================

-- 사용자 활동 순위 및 백분위 분석
SELECT 
    ubp.user_id,
    ubp.email,
    ubp.name,
    ubp.total_activity_score,
    -- 전체 사용자 대비 순위
    RANK() OVER (ORDER BY ubp.total_activity_score DESC) AS activity_rank,
    DENSE_RANK() OVER (ORDER BY ubp.total_activity_score DESC) AS activity_dense_rank,
    ROW_NUMBER() OVER (ORDER BY ubp.total_activity_score DESC) AS activity_row_number,
    -- 백분위 계산
    PERCENT_RANK() OVER (ORDER BY ubp.total_activity_score DESC) AS activity_percent_rank,
    CUME_DIST() OVER (ORDER BY ubp.total_activity_score DESC) AS activity_cume_dist,
    -- 이동 평균 (5명 단위)
    AVG(ubp.total_activity_score) OVER (
        ORDER BY ubp.total_activity_score DESC 
        ROWS BETWEEN 2 PRECEDING AND 2 FOLLOWING
    ) AS moving_avg_5users,
    -- 누적 합계
    SUM(ubp.total_activity_score) OVER (
        ORDER BY ubp.total_activity_score DESC 
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_score,
    -- 이전/다음 사용자와의 점수 차이
    ubp.total_activity_score - LAG(ubp.total_activity_score) OVER (ORDER BY ubp.total_activity_score DESC) AS score_diff_from_previous,
    ubp.total_activity_score - LEAD(ubp.total_activity_score) OVER (ORDER BY ubp.total_activity_score DESC) AS score_diff_from_next,
    -- 활동 유형별 순위
    RANK() OVER (PARTITION BY ubp.primary_activity_type ORDER BY ubp.total_activity_score DESC) AS rank_in_type,
    -- 계정 연령별 순위
    RANK() OVER (PARTITION BY ul.lifecycle_stage ORDER BY ubp.total_activity_score DESC) AS rank_in_lifecycle
FROM user_behavior_profiles ubp
INNER JOIN user_lifecycle ul ON ubp.user_id = ul.user_id
WHERE ubp.total_activity_score > 0
ORDER BY ubp.total_activity_score DESC;

-- ============================================
-- 8. 추가 분석: 계층적 데이터 분석
-- ============================================

-- 사용자 계층 구조 분석 (활동 점수 기반)
WITH RECURSIVE user_hierarchy AS (
    -- 최상위 사용자 (활동 점수 상위 10%)
    SELECT 
        ubp.user_id,
        ubp.email,
        ubp.total_activity_score,
        1 AS hierarchy_level,
        CAST(ubp.user_id AS TEXT) AS hierarchy_path,
        ubp.user_id AS root_user_id
    FROM user_behavior_profiles ubp
    WHERE ubp.total_activity_score >= (
        SELECT PERCENTILE_DISC(0.9) WITHIN GROUP (ORDER BY total_activity_score)
        FROM user_behavior_profiles
        WHERE total_activity_score > 0
    )
    
    UNION ALL
    
    -- 하위 사용자 (상위 사용자와 유사한 패턴)
    SELECT 
        ubp2.user_id,
        ubp2.email,
        ubp2.total_activity_score,
        uh.hierarchy_level + 1,
        uh.hierarchy_path || ' -> ' || CAST(ubp2.user_id AS TEXT),
        uh.root_user_id
    FROM user_hierarchy uh
    INNER JOIN user_behavior_profiles ubp2 ON ubp2.primary_activity_type = (
        SELECT ubp3.primary_activity_type 
        FROM user_behavior_profiles ubp3 
        WHERE ubp3.user_id = uh.user_id
    )
    WHERE uh.hierarchy_level < 3
        AND ubp2.total_activity_score < uh.total_activity_score
        AND ubp2.user_id != uh.user_id
)
SELECT 
    hierarchy_level,
    root_user_id,
    COUNT(*) AS user_count,
    AVG(total_activity_score) AS avg_score,
    MIN(total_activity_score) AS min_score,
    MAX(total_activity_score) AS max_score
FROM user_hierarchy
GROUP BY hierarchy_level, root_user_id
ORDER BY hierarchy_level, root_user_id
LIMIT 500;

-- ============================================
-- 9. 추가 분석: 복잡한 집계 및 피벗 분석
-- ============================================

-- 활동 유형별 월별 트렌드 피벗 테이블
SELECT 
    activity_month,
    SUM(CASE WHEN activity_type = 'news' THEN activity_count ELSE 0 END) AS news_activity,
    SUM(CASE WHEN activity_type = 'radio' THEN activity_count ELSE 0 END) AS radio_activity,
    SUM(CASE WHEN activity_type = 'books' THEN activity_count ELSE 0 END) AS books_activity,
    SUM(CASE WHEN activity_type = 'api' THEN activity_count ELSE 0 END) AS api_activity,
    SUM(activity_count) AS total_activity,
    -- 월별 성장률 계산
    LAG(SUM(activity_count)) OVER (ORDER BY activity_month) AS previous_month_total,
    CASE 
        WHEN LAG(SUM(activity_count)) OVER (ORDER BY activity_month) > 0
        THEN ROUND(
            (SUM(activity_count) - LAG(SUM(activity_count)) OVER (ORDER BY activity_month)) * 100.0 / 
            LAG(SUM(activity_count)) OVER (ORDER BY activity_month), 
            2
        )
        ELSE NULL
    END AS month_over_month_growth,
    -- 이동 평균 (3개월)
    ROUND(
        AVG(SUM(activity_count)) OVER (
            ORDER BY activity_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS moving_avg_3months,
    -- 누적 합계
    SUM(SUM(activity_count)) OVER (
        ORDER BY activity_month 
        ROWS UNBOUNDED PRECEDING
    ) AS cumulative_activity
FROM (
    SELECT 
        strftime('%Y-%m', n.collectedAt) AS activity_month,
        'news' AS activity_type,
        COUNT(*) AS activity_count
    FROM news n
    WHERE n.collectedAt >= date('now', '-2 years')
    GROUP BY strftime('%Y-%m', n.collectedAt)
    
    UNION ALL
    
    SELECT 
        strftime('%Y-%m', rs.lastPlayed) AS activity_month,
        'radio' AS activity_type,
        COUNT(*) AS activity_count
    FROM radioSongs rs
    WHERE rs.lastPlayed >= date('now', '-2 years')
    GROUP BY strftime('%Y-%m', rs.lastPlayed)
    
    UNION ALL
    
    SELECT 
        strftime('%Y-%m', b.collectedAt) AS activity_month,
        'books' AS activity_type,
        COUNT(*) AS activity_count
    FROM books b
    WHERE b.collectedAt >= date('now', '-2 years')
    GROUP BY strftime('%Y-%m', b.collectedAt)
    
    UNION ALL
    
    SELECT 
        strftime('%Y-%m', aku.createdAt) AS activity_month,
        'api' AS activity_type,
        COUNT(*) AS activity_count
    FROM apiKeyUsage aku
    INNER JOIN apiKeys ak ON aku.apiKeyId = ak.id
    WHERE aku.createdAt >= date('now', '-2 years')
    GROUP BY strftime('%Y-%m', aku.createdAt)
) AS monthly_activities
GROUP BY activity_month
ORDER BY activity_month DESC;

-- ============================================
-- 10. 추가 분석: 다차원 분석 (OLAP 스타일)
-- ============================================

-- 롤업 분석: 활동 유형별, 시간대별, 요일별 집계
SELECT 
    'Total' AS dimension_level,
    'All' AS activity_type,
    'All' AS time_period,
    'All' AS day_of_week,
    COUNT(DISTINCT u.id) AS user_count,
    COUNT(*) AS total_activities
FROM users u
LEFT JOIN news n ON u.id = n.userId AND n.collectedAt >= date('now', '-3 months')
LEFT JOIN radioSongs rs ON u.id = rs.userId AND rs.lastPlayed >= date('now', '-3 months')
LEFT JOIN books b ON u.id = b.userId AND b.collectedAt >= date('now', '-3 months')
LEFT JOIN apiKeys ak ON u.id = ak.userId
LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId AND aku.createdAt >= date('now', '-3 months')

UNION ALL

-- 활동 유형별 롤업
SELECT 
    'Activity Type' AS dimension_level,
    CASE 
        WHEN n.id IS NOT NULL THEN 'news'
        WHEN rs.id IS NOT NULL THEN 'radio'
        WHEN b.id IS NOT NULL THEN 'books'
        WHEN aku.id IS NOT NULL THEN 'api'
        ELSE 'none'
    END AS activity_type,
    'All' AS time_period,
    'All' AS day_of_week,
    COUNT(DISTINCT u.id) AS user_count,
    COUNT(*) AS total_activities
FROM users u
LEFT JOIN news n ON u.id = n.userId AND n.collectedAt >= date('now', '-3 months')
LEFT JOIN radioSongs rs ON u.id = rs.userId AND rs.lastPlayed >= date('now', '-3 months')
LEFT JOIN books b ON u.id = b.userId AND b.collectedAt >= date('now', '-3 months')
LEFT JOIN apiKeys ak ON u.id = ak.userId
LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId AND aku.createdAt >= date('now', '-3 months')
GROUP BY activity_type

UNION ALL

-- 시간대별 롤업
SELECT 
    'Time Period' AS dimension_level,
    'All' AS activity_type,
    CASE 
        WHEN CAST(strftime('%H', COALESCE(n.collectedAt, rs.lastPlayed, b.collectedAt, aku.createdAt)) AS INTEGER) BETWEEN 6 AND 11 THEN 'Morning'
        WHEN CAST(strftime('%H', COALESCE(n.collectedAt, rs.lastPlayed, b.collectedAt, aku.createdAt)) AS INTEGER) BETWEEN 12 AND 17 THEN 'Afternoon'
        WHEN CAST(strftime('%H', COALESCE(n.collectedAt, rs.lastPlayed, b.collectedAt, aku.createdAt)) AS INTEGER) BETWEEN 18 AND 23 THEN 'Evening'
        ELSE 'Night'
    END AS time_period,
    'All' AS day_of_week,
    COUNT(DISTINCT u.id) AS user_count,
    COUNT(*) AS total_activities
FROM users u
LEFT JOIN news n ON u.id = n.userId AND n.collectedAt >= date('now', '-3 months')
LEFT JOIN radioSongs rs ON u.id = rs.userId AND rs.lastPlayed >= date('now', '-3 months')
LEFT JOIN books b ON u.id = b.userId AND b.collectedAt >= date('now', '-3 months')
LEFT JOIN apiKeys ak ON u.id = ak.userId
LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId AND aku.createdAt >= date('now', '-3 months')
WHERE COALESCE(n.collectedAt, rs.lastPlayed, b.collectedAt, aku.createdAt) IS NOT NULL
GROUP BY time_period

UNION ALL

-- 요일별 롤업
SELECT 
    'Day of Week' AS dimension_level,
    'All' AS activity_type,
    'All' AS time_period,
    CASE strftime('%w', COALESCE(n.collectedAt, rs.lastPlayed, b.collectedAt, aku.createdAt))
        WHEN '0' THEN 'Sunday'
        WHEN '1' THEN 'Monday'
        WHEN '2' THEN 'Tuesday'
        WHEN '3' THEN 'Wednesday'
        WHEN '4' THEN 'Thursday'
        WHEN '5' THEN 'Friday'
        WHEN '6' THEN 'Saturday'
    END AS day_of_week,
    COUNT(DISTINCT u.id) AS user_count,
    COUNT(*) AS total_activities
FROM users u
LEFT JOIN news n ON u.id = n.userId AND n.collectedAt >= date('now', '-3 months')
LEFT JOIN radioSongs rs ON u.id = rs.userId AND rs.lastPlayed >= date('now', '-3 months')
LEFT JOIN books b ON u.id = b.userId AND b.collectedAt >= date('now', '-3 months')
LEFT JOIN apiKeys ak ON u.id = ak.userId
LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId AND aku.createdAt >= date('now', '-3 months')
WHERE COALESCE(n.collectedAt, rs.lastPlayed, b.collectedAt, aku.createdAt) IS NOT NULL
GROUP BY day_of_week

ORDER BY dimension_level, activity_type, time_period, day_of_week;

-- ============================================
-- 11. 추가 분석: 고급 통계 분석
-- ============================================

-- 사용자 활동 통계 요약 (평균, 중앙값, 표준편차 근사)
SELECT 
    COUNT(*) AS total_users,
    COUNT(CASE WHEN ubp.total_activity_score > 0 THEN 1 END) AS active_users,
    -- 평균
    ROUND(AVG(ubp.total_activity_score), 2) AS avg_activity_score,
    ROUND(AVG(ubp.news_activity_score), 2) AS avg_news_score,
    ROUND(AVG(ubp.radio_activity_score), 2) AS avg_radio_score,
    ROUND(AVG(ubp.books_activity_score), 2) AS avg_books_score,
    ROUND(AVG(ubp.api_activity_score), 2) AS avg_api_score,
    -- 중앙값 근사 (50번째 백분위)
    (
        SELECT ubp2.total_activity_score
        FROM user_behavior_profiles ubp2
        ORDER BY ubp2.total_activity_score
        LIMIT 1 OFFSET (SELECT COUNT(*) / 2 FROM user_behavior_profiles WHERE total_activity_score > 0)
    ) AS median_activity_score,
    -- 최소/최대
    MIN(ubp.total_activity_score) AS min_activity_score,
    MAX(ubp.total_activity_score) AS max_activity_score,
    -- 사분위수 근사
    (
        SELECT ubp3.total_activity_score
        FROM user_behavior_profiles ubp3
        WHERE ubp3.total_activity_score > 0
        ORDER BY ubp3.total_activity_score
        LIMIT 1 OFFSET (SELECT COUNT(*) / 4 FROM user_behavior_profiles WHERE total_activity_score > 0)
    ) AS q1_activity_score,
    (
        SELECT ubp4.total_activity_score
        FROM user_behavior_profiles ubp4
        WHERE ubp4.total_activity_score > 0
        ORDER BY ubp4.total_activity_score
        LIMIT 1 OFFSET (SELECT COUNT(*) * 3 / 4 FROM user_behavior_profiles WHERE total_activity_score > 0)
    ) AS q3_activity_score,
    -- 표준편차 근사 (분산의 제곱근)
    ROUND(
        SQRT(
            AVG(ubp.total_activity_score * ubp.total_activity_score) - 
            AVG(ubp.total_activity_score) * AVG(ubp.total_activity_score)
        ), 
        2
    ) AS std_dev_activity_score
FROM user_behavior_profiles ubp
WHERE ubp.total_activity_score > 0;

-- ============================================
-- 12. 추가 분석: 복잡한 조건부 집계
-- ============================================

-- 다중 조건 기반 사용자 분류 및 통계
SELECT 
    -- 사용자 분류
    CASE 
        WHEN ubp.total_activity_score > 200 
            AND ubp.diversity_score >= 3
            AND ul.account_age_days > 180
            AND (nda.last_7d > 10 OR rda.last_7d_plays > 20 OR bda.last_7d_collections > 5)
        THEN '슈퍼 유저'
        WHEN ubp.total_activity_score > 100
            AND ubp.diversity_score >= 2
            AND ul.account_age_days > 90
        THEN '파워 유저'
        WHEN ubp.total_activity_score > 50
            AND ubp.diversity_score >= 1
            AND ul.account_age_days > 30
        THEN '활성 유저'
        WHEN ubp.total_activity_score > 0
        THEN '일반 유저'
        ELSE '비활성 유저'
    END AS user_classification,
    COUNT(*) AS user_count,
    -- 분류별 평균 통계
    ROUND(AVG(ubp.total_activity_score), 2) AS avg_total_score,
    ROUND(AVG(ubp.news_activity_score), 2) AS avg_news_score,
    ROUND(AVG(ubp.radio_activity_score), 2) AS avg_radio_score,
    ROUND(AVG(ubp.books_activity_score), 2) AS avg_books_score,
    ROUND(AVG(ubp.api_activity_score), 2) AS avg_api_score,
    ROUND(AVG(ubp.diversity_score), 2) AS avg_diversity,
    ROUND(AVG(ul.account_age_days), 0) AS avg_account_age,
    -- 분류별 주요 활동 유형 분포
    COUNT(CASE WHEN ubp.primary_activity_type = '뉴스 중심' THEN 1 END) AS news_focused,
    COUNT(CASE WHEN ubp.primary_activity_type = '음악 중심' THEN 1 END) AS radio_focused,
    COUNT(CASE WHEN ubp.primary_activity_type = '독서 중심' THEN 1 END) AS books_focused,
    COUNT(CASE WHEN ubp.primary_activity_type = '개발자' THEN 1 END) AS developer_focused,
    COUNT(CASE WHEN ubp.primary_activity_type = '균형형' THEN 1 END) AS balanced,
    -- 분류별 시간대 패턴
    ROUND(AVG(tpc.total_morning_activity), 2) AS avg_morning_activity,
    ROUND(AVG(tpc.total_afternoon_activity), 2) AS avg_afternoon_activity,
    ROUND(AVG(tpc.total_evening_activity), 2) AS avg_evening_activity,
    ROUND(AVG(tpc.total_night_activity), 2) AS avg_night_activity,
    -- 분류별 최근 활동 강도
    ROUND(AVG(COALESCE(nda.last_7d, 0)), 2) AS avg_news_last_7d,
    ROUND(AVG(COALESCE(rda.last_7d_plays, 0)), 2) AS avg_radio_last_7d,
    ROUND(AVG(COALESCE(bda.last_7d_collections, 0)), 2) AS avg_books_last_7d,
    ROUND(AVG(COALESCE(ada.last_7d_calls, 0)), 2) AS avg_api_last_7d
FROM user_behavior_profiles ubp
INNER JOIN user_lifecycle ul ON ubp.user_id = ul.user_id
LEFT JOIN news_deep_analysis nda ON ubp.user_id = nda.userId
LEFT JOIN radio_deep_analysis rda ON ubp.user_id = rda.userId
LEFT JOIN books_deep_analysis bda ON ubp.user_id = bda.userId
LEFT JOIN api_deep_analysis ada ON ubp.user_id = ada.userId
LEFT JOIN time_pattern_comprehensive tpc ON ubp.user_id = tpc.user_id
GROUP BY user_classification
ORDER BY avg_total_score DESC;

-- ============================================
-- 13. 추가 분석: 예측 모델링 데이터 준비
-- ============================================

-- 머신러닝 모델 학습용 특징 벡터 생성
SELECT 
    ubp.user_id AS user_id,
    -- 기본 특징
    ubp.total_activity_score AS feature_total_score,
    ubp.news_activity_score AS feature_news_score,
    ubp.radio_activity_score AS feature_radio_score,
    ubp.books_activity_score AS feature_books_score,
    ubp.api_activity_score AS feature_api_score,
    ubp.diversity_score AS feature_diversity,
    ul.account_age_days AS feature_account_age,
    -- 정규화된 특징 (0-1 범위)
    CAST(ubp.news_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS feature_norm_news,
    CAST(ubp.radio_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS feature_norm_radio,
    CAST(ubp.books_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS feature_norm_books,
    CAST(ubp.api_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS feature_norm_api,
    -- 시간대 특징
    CAST(tpc.total_morning_activity AS REAL) / NULLIF(
        tpc.total_morning_activity + tpc.total_afternoon_activity + 
        tpc.total_evening_activity + tpc.total_night_activity, 0
    ) AS feature_norm_morning,
    CAST(tpc.total_afternoon_activity AS REAL) / NULLIF(
        tpc.total_morning_activity + tpc.total_afternoon_activity + 
        tpc.total_evening_activity + tpc.total_night_activity, 0
    ) AS feature_norm_afternoon,
    CAST(tpc.total_evening_activity AS REAL) / NULLIF(
        tpc.total_morning_activity + tpc.total_afternoon_activity + 
        tpc.total_evening_activity + tpc.total_night_activity, 0
    ) AS feature_norm_evening,
    CAST(tpc.total_night_activity AS REAL) / NULLIF(
        tpc.total_morning_activity + tpc.total_afternoon_activity + 
        tpc.total_evening_activity + tpc.total_night_activity, 0
    ) AS feature_norm_night,
    -- 활동 패턴 특징
    COALESCE(nda.recent_7d, 0) AS feature_news_recent_7d,
    COALESCE(nda.recent_30d, 0) AS feature_news_recent_30d,
    COALESCE(rda.last_7d_plays, 0) AS feature_radio_recent_7d,
    COALESCE(rda.last_30d_plays, 0) AS feature_radio_recent_30d,
    COALESCE(bda.last_7d_collections, 0) AS feature_books_recent_7d,
    COALESCE(bda.last_30d_collections, 0) AS feature_books_recent_30d,
    COALESCE(ada.last_7d_calls, 0) AS feature_api_recent_7d,
    COALESCE(ada.last_30d_calls, 0) AS feature_api_recent_30d,
    -- 트렌드 특징
    CASE 
        WHEN nda.recent_7d > 0 AND nda.recent_30d > 0
        THEN CAST(nda.recent_7d AS REAL) / NULLIF(nda.recent_30d, 0)
        ELSE 0
    END AS feature_news_trend,
    CASE 
        WHEN rda.last_7d_plays > 0 AND rda.last_30d_plays > 0
        THEN CAST(rda.last_7d_plays AS REAL) / NULLIF(rda.last_30d_plays, 0)
        ELSE 0
    END AS feature_radio_trend,
    -- 카테고리 특징
    COALESCE(nda.category_count, 0) AS feature_news_categories,
    COALESCE(nda.keyword_count, 0) AS feature_news_keywords,
    COALESCE(rda.artist_count, 0) AS feature_radio_artists,
    COALESCE(rda.genre_count, 0) AS feature_radio_genres,
    COALESCE(bda.author_count, 0) AS feature_books_authors,
    COALESCE(bda.category_count, 0) AS feature_books_categories,
    COALESCE(ada.endpoint_count, 0) AS feature_api_endpoints,
    -- 예측 대상 (다음 30일 활동 예상치)
    CASE 
        WHEN nda.recent_30d > 0 AND nda.recent_90d > 0
        THEN CAST(nda.recent_30d AS REAL) * (CAST(nda.recent_30d AS REAL) / NULLIF(nda.recent_90d, 0))
        ELSE COALESCE(nda.recent_30d, 0)
    END AS target_news_next_30d,
    CASE 
        WHEN rda.last_30d_plays > 0 AND rda.last_90d_plays > 0
        THEN CAST(rda.last_30d_plays AS REAL) * (CAST(rda.last_30d_plays AS REAL) / NULLIF(rda.last_90d_plays, 0))
        ELSE COALESCE(rda.last_30d_plays, 0)
    END AS target_radio_next_30d,
    CASE 
        WHEN bda.last_30d_collections > 0 AND bda.last_90d_collections > 0
        THEN CAST(bda.last_30d_collections AS REAL) * (CAST(bda.last_30d_collections AS REAL) / NULLIF(bda.last_90d_collections, 0))
        ELSE COALESCE(bda.last_30d_collections, 0)
    END AS target_books_next_30d,
    -- 이탈 예측 대상
    CASE 
        WHEN ul.account_status = '휴면' THEN 1
        WHEN ul.account_status = '비활성' AND ubp.total_activity_score = 0 THEN 1
        WHEN ubp.total_activity_score > 0 
            AND (
                (nda.recent_7d IS NULL OR nda.recent_7d = 0)
                AND (rda.last_7d_plays IS NULL OR rda.last_7d_plays = 0)
                AND (bda.last_7d_collections IS NULL OR bda.last_7d_collections = 0)
                AND (ada.last_7d_calls IS NULL OR ada.last_7d_calls = 0)
            )
        THEN 1
        ELSE 0
    END AS target_churn_risk
FROM user_behavior_profiles ubp
INNER JOIN user_lifecycle ul ON ubp.user_id = ul.user_id
LEFT JOIN news_deep_analysis nda ON ubp.user_id = nda.userId
LEFT JOIN radio_deep_analysis rda ON ubp.user_id = rda.userId
LEFT JOIN books_deep_analysis bda ON ubp.user_id = bda.userId
LEFT JOIN api_deep_analysis ada ON ubp.user_id = ada.userId
LEFT JOIN time_pattern_comprehensive tpc ON ubp.user_id = tpc.user_id
WHERE ubp.total_activity_score > 0
    AND ul.account_age_days > 7
ORDER BY ubp.total_activity_score DESC;

-- ============================================
-- 14. 추가 분석: 복잡한 서브쿼리 및 EXISTS 분석
-- ============================================

-- 존재 여부 기반 사용자 필터링 및 분석
SELECT 
    u.id AS user_id,
    u.email,
    u.name,
    -- 각 활동 유형 존재 여부
    CASE WHEN EXISTS (SELECT 1 FROM news n WHERE n.userId = u.id) THEN 1 ELSE 0 END AS has_news_activity,
    CASE WHEN EXISTS (SELECT 1 FROM radioSongs rs WHERE rs.userId = u.id) THEN 1 ELSE 0 END AS has_radio_activity,
    CASE WHEN EXISTS (SELECT 1 FROM books b WHERE b.userId = u.id) THEN 1 ELSE 0 END AS has_books_activity,
    CASE WHEN EXISTS (SELECT 1 FROM apiKeys ak WHERE ak.userId = u.id) THEN 1 ELSE 0 END AS has_api_keys,
    CASE WHEN EXISTS (
        SELECT 1 FROM apiKeys ak2 
        INNER JOIN apiKeyUsage aku ON ak2.id = aku.apiKeyId 
        WHERE ak2.userId = u.id
    ) THEN 1 ELSE 0 END AS has_api_usage,
    -- 각 활동 유형의 최근 활동 존재 여부
    CASE WHEN EXISTS (
        SELECT 1 FROM news n2 
        WHERE n2.userId = u.id 
            AND n2.collectedAt >= date('now', '-7 days')
    ) THEN 1 ELSE 0 END AS has_recent_news,
    CASE WHEN EXISTS (
        SELECT 1 FROM radioSongs rs2 
        WHERE rs2.userId = u.id 
            AND rs2.lastPlayed >= date('now', '-7 days')
    ) THEN 1 ELSE 0 END AS has_recent_radio,
    CASE WHEN EXISTS (
        SELECT 1 FROM books b2 
        WHERE b2.userId = u.id 
            AND b2.collectedAt >= date('now', '-7 days')
    ) THEN 1 ELSE 0 END AS has_recent_books,
    CASE WHEN EXISTS (
        SELECT 1 FROM apiKeys ak3 
        INNER JOIN apiKeyUsage aku2 ON ak3.id = aku2.apiKeyId 
        WHERE ak3.userId = u.id 
            AND aku2.createdAt >= date('now', '-7 days')
    ) THEN 1 ELSE 0 END AS has_recent_api,
    -- 활동 유형 조합 점수
    (
        CASE WHEN EXISTS (SELECT 1 FROM news n WHERE n.userId = u.id) THEN 1 ELSE 0 END +
        CASE WHEN EXISTS (SELECT 1 FROM radioSongs rs WHERE rs.userId = u.id) THEN 1 ELSE 0 END +
        CASE WHEN EXISTS (SELECT 1 FROM books b WHERE b.userId = u.id) THEN 1 ELSE 0 END +
        CASE WHEN EXISTS (
            SELECT 1 FROM apiKeys ak 
            INNER JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId 
            WHERE ak.userId = u.id
        ) THEN 1 ELSE 0 END
    ) AS activity_type_count,
    -- 최근 활동 조합 점수
    (
        CASE WHEN EXISTS (
            SELECT 1 FROM news n2 
            WHERE n2.userId = u.id 
                AND n2.collectedAt >= date('now', '-7 days')
        ) THEN 1 ELSE 0 END +
        CASE WHEN EXISTS (
            SELECT 1 FROM radioSongs rs2 
            WHERE rs2.userId = u.id 
                AND rs2.lastPlayed >= date('now', '-7 days')
        ) THEN 1 ELSE 0 END +
        CASE WHEN EXISTS (
            SELECT 1 FROM books b2 
            WHERE b2.userId = u.id 
                AND b2.collectedAt >= date('now', '-7 days')
        ) THEN 1 ELSE 0 END +
        CASE WHEN EXISTS (
            SELECT 1 FROM apiKeys ak3 
            INNER JOIN apiKeyUsage aku2 ON ak3.id = aku2.apiKeyId 
            WHERE ak3.userId = u.id 
                AND aku2.createdAt >= date('now', '-7 days')
        ) THEN 1 ELSE 0 END
    ) AS recent_activity_type_count
FROM users u
WHERE u.createdAt >= date('now', '-1 year')
ORDER BY activity_type_count DESC, recent_activity_type_count DESC;

-- ============================================
-- 15. 추가 분석: 복잡한 CASE 문 및 조건부 로직
-- ============================================

-- 다중 조건 기반 사용자 프로필 생성
SELECT 
    ubp.user_id,
    ubp.email,
    ubp.name,
    -- 복합 조건 기반 사용자 타입 분류
    CASE 
        WHEN ubp.total_activity_score > 200 
            AND ubp.diversity_score >= 3
            AND ul.account_age_days > 180
            AND tpc.preferred_time_period IN ('아침형', '오후형')
            AND (COALESCE(nda.recent_7d, 0) > 20 OR COALESCE(rda.last_7d_plays, 0) > 40)
        THEN '프리미엄 아침/오후 활동형'
        WHEN ubp.total_activity_score > 200 
            AND ubp.diversity_score >= 3
            AND ul.account_age_days > 180
            AND tpc.preferred_time_period IN ('저녁형', '야행형')
            AND (COALESCE(nda.recent_7d, 0) > 20 OR COALESCE(rda.last_7d_plays, 0) > 40)
        THEN '프리미엄 저녁/야행 활동형'
        WHEN ubp.total_activity_score > 100
            AND ubp.diversity_score >= 2
            AND ul.account_age_days > 90
            AND ubp.primary_activity_type = '균형형'
        THEN '균형형 활성 유저'
        WHEN ubp.total_activity_score > 100
            AND ubp.diversity_score >= 2
            AND ul.account_age_days > 90
            AND ubp.primary_activity_type != '균형형'
        THEN '특화형 활성 유저'
        WHEN ubp.total_activity_score > 50
            AND ubp.diversity_score >= 1
            AND ul.account_age_days > 30
        THEN '성장형 유저'
        WHEN ubp.total_activity_score > 0
            AND ul.account_age_days <= 30
        THEN '신규 유저'
        WHEN ubp.total_activity_score > 0
            AND ul.account_age_days > 30
        THEN '일반 유저'
        ELSE '비활성 유저'
    END AS detailed_user_type,
    -- 활동 강도 등급
    CASE 
        WHEN ubp.total_activity_score > 200 THEN '매우 높음'
        WHEN ubp.total_activity_score > 100 THEN '높음'
        WHEN ubp.total_activity_score > 50 THEN '보통'
        WHEN ubp.total_activity_score > 0 THEN '낮음'
        ELSE '없음'
    END AS activity_intensity_level,
    -- 활동 패턴 안정성
    CASE 
        WHEN ubp.diversity_score >= 3 
            AND COALESCE(nda.active_days, 0) > 30
            AND COALESCE(rda.active_play_days, 0) > 30
            AND COALESCE(bda.active_collection_days, 0) > 10
        THEN '매우 안정적'
        WHEN ubp.diversity_score >= 2 
            AND (COALESCE(nda.active_days, 0) > 20 
                 OR COALESCE(rda.active_play_days, 0) > 20)
        THEN '안정적'
        WHEN ubp.diversity_score >= 1 
            AND (COALESCE(nda.active_days, 0) > 10 
                 OR COALESCE(rda.active_play_days, 0) > 10)
        THEN '보통'
        WHEN ubp.total_activity_score > 0
        THEN '불안정'
        ELSE '비활성'
    END AS activity_stability,
    -- 추천 활동 우선순위
    CASE 
        WHEN ubp.news_activity_score = 0 
            AND ubp.radio_activity_score > 0 
            AND ubp.books_activity_score > 0
        THEN '뉴스 수집 시작 권장 (최우선)'
        WHEN ubp.radio_activity_score = 0 
            AND ubp.news_activity_score > 0 
            AND ubp.books_activity_score > 0
        THEN '음악 탐색 시작 권장 (최우선)'
        WHEN ubp.books_activity_score = 0 
            AND ubp.news_activity_score > 0 
            AND ubp.radio_activity_score > 0
        THEN '도서 검색 시작 권장 (최우선)'
        WHEN ubp.news_activity_score < ubp.radio_activity_score 
            AND ubp.news_activity_score < ubp.books_activity_score
        THEN '뉴스 수집 확대 권장'
        WHEN ubp.radio_activity_score < ubp.news_activity_score
            AND ubp.radio_activity_score < ubp.books_activity_score
        THEN '음악 탐색 확대 권장'
        WHEN ubp.books_activity_score < ubp.news_activity_score
            AND ubp.books_activity_score < ubp.radio_activity_score
        THEN '도서 검색 확대 권장'
        WHEN ubp.diversity_score < 2
        THEN '다양한 활동 유형 시도 권장'
        ELSE '현재 활동 패턴 유지 권장'
    END AS activity_recommendation_priority
FROM user_behavior_profiles ubp
INNER JOIN user_lifecycle ul ON ubp.user_id = ul.user_id
LEFT JOIN news_deep_analysis nda ON ubp.user_id = nda.userId
LEFT JOIN radio_deep_analysis rda ON ubp.user_id = rda.userId
LEFT JOIN books_deep_analysis bda ON ubp.user_id = bda.userId
LEFT JOIN time_pattern_comprehensive tpc ON ubp.user_id = tpc.user_id
WHERE ubp.total_activity_score > 0
ORDER BY ubp.total_activity_score DESC, ubp.diversity_score DESC;

-- ============================================
-- 16. 추가 분석: 최종 통합 리포트 생성
-- ============================================

-- 모든 분석 결과를 통합한 최종 리포트
SELECT 
    '=== 사용자 활동 종합 리포트 ===' AS report_section,
    COUNT(*) AS total_users_analyzed,
    COUNT(CASE WHEN ubp.total_activity_score > 0 THEN 1 END) AS active_users_count,
    COUNT(CASE WHEN ubp.total_activity_score = 0 THEN 1 END) AS inactive_users_count,
    ROUND(AVG(ubp.total_activity_score), 2) AS overall_avg_score,
    ROUND(MAX(ubp.total_activity_score), 2) AS max_score,
    ROUND(MIN(ubp.total_activity_score), 2) AS min_score,
    ROUND(AVG(ubp.diversity_score), 2) AS avg_diversity,
    COUNT(CASE WHEN ubp.primary_activity_type = '뉴스 중심' THEN 1 END) AS news_focused_users,
    COUNT(CASE WHEN ubp.primary_activity_type = '음악 중심' THEN 1 END) AS radio_focused_users,
    COUNT(CASE WHEN ubp.primary_activity_type = '독서 중심' THEN 1 END) AS books_focused_users,
    COUNT(CASE WHEN ubp.primary_activity_type = '개발자' THEN 1 END) AS developer_users,
    COUNT(CASE WHEN ubp.primary_activity_type = '균형형' THEN 1 END) AS balanced_users,
    ROUND(AVG(ul.account_age_days), 0) AS avg_account_age_days,
    COUNT(CASE WHEN ul.account_status = '활성' THEN 1 END) AS active_accounts,
    COUNT(CASE WHEN ul.account_status = '비활성' THEN 1 END) AS inactive_accounts,
    COUNT(CASE WHEN ul.account_status = '휴면' THEN 1 END) AS dormant_accounts,
    ROUND(AVG(tpc.total_morning_activity), 2) AS avg_morning_activity,
    ROUND(AVG(tpc.total_afternoon_activity), 2) AS avg_afternoon_activity,
    ROUND(AVG(tpc.total_evening_activity), 2) AS avg_evening_activity,
    ROUND(AVG(tpc.total_night_activity), 2) AS avg_night_activity,
    COUNT(CASE WHEN tpc.preferred_time_period = '아침형' THEN 1 END) AS morning_type_users,
    COUNT(CASE WHEN tpc.preferred_time_period = '오후형' THEN 1 END) AS afternoon_type_users,
    COUNT(CASE WHEN tpc.preferred_time_period = '저녁형' THEN 1 END) AS evening_type_users,
    COUNT(CASE WHEN tpc.preferred_time_period = '야행형' THEN 1 END) AS night_type_users,
    ROUND(AVG(COALESCE(nda.total_news_count, 0)), 2) AS avg_news_count,
    ROUND(AVG(COALESCE(rda.total_songs_count, 0)), 2) AS avg_songs_count,
    ROUND(AVG(COALESCE(bda.total_books_count, 0)), 2) AS avg_books_count,
    ROUND(AVG(COALESCE(ada.total_calls, 0)), 2) AS avg_api_calls,
    ROUND(AVG(COALESCE(nda.recent_7d, 0)), 2) AS avg_news_last_7d,
    ROUND(AVG(COALESCE(rda.last_7d_plays, 0)), 2) AS avg_radio_last_7d,
    ROUND(AVG(COALESCE(bda.last_7d_collections, 0)), 2) AS avg_books_last_7d,
    ROUND(AVG(COALESCE(ada.last_7d_calls, 0)), 2) AS avg_api_last_7d,
    COUNT(CASE WHEN ubp.total_activity_score > 200 THEN 1 END) AS super_users,
    COUNT(CASE WHEN ubp.total_activity_score BETWEEN 100 AND 200 THEN 1 END) AS power_users,
    COUNT(CASE WHEN ubp.total_activity_score BETWEEN 50 AND 100 THEN 1 END) AS active_users,
    COUNT(CASE WHEN ubp.total_activity_score BETWEEN 1 AND 50 THEN 1 END) AS regular_users,
    COUNT(CASE WHEN ubp.total_activity_score = 0 THEN 1 END) AS inactive_users,
    ROUND(
        CAST(COUNT(CASE WHEN ubp.total_activity_score > 0 THEN 1 END) AS REAL) / 
        NULLIF(COUNT(*), 0) * 100, 
        2
    ) AS active_user_percentage,
    ROUND(
        CAST(COUNT(CASE WHEN ubp.diversity_score >= 2 THEN 1 END) AS REAL) / 
        NULLIF(COUNT(CASE WHEN ubp.total_activity_score > 0 THEN 1 END), 0) * 100, 
        2
    ) AS diverse_user_percentage,
    ROUND(
        CAST(COUNT(CASE WHEN COALESCE(nda.recent_7d, 0) > 0 
            OR COALESCE(rda.last_7d_plays, 0) > 0 
            OR COALESCE(bda.last_7d_collections, 0) > 0 
            OR COALESCE(ada.last_7d_calls, 0) > 0 THEN 1 END) AS REAL) / 
        NULLIF(COUNT(CASE WHEN ubp.total_activity_score > 0 THEN 1 END), 0) * 100, 
        2
    ) AS recent_activity_percentage
FROM user_behavior_profiles ubp
INNER JOIN user_lifecycle ul ON ubp.user_id = ul.user_id
LEFT JOIN news_deep_analysis nda ON ubp.user_id = nda.userId
LEFT JOIN radio_deep_analysis rda ON ubp.user_id = rda.userId
LEFT JOIN books_deep_analysis bda ON ubp.user_id = bda.userId
LEFT JOIN api_deep_analysis ada ON ubp.user_id = ada.userId
LEFT JOIN time_pattern_comprehensive tpc ON ubp.user_id = tpc.user_id;

-- ============================================
-- 17. 추가 분석: 성능 최적화를 위한 인덱스 제안 쿼리
-- ============================================

-- 자주 사용되는 컬럼 조합 분석 (인덱스 최적화 제안)
SELECT 
    '인덱스 최적화 제안' AS optimization_type,
    'users 테이블' AS table_name,
    'createdAt, updatedAt 복합 인덱스' AS suggested_index,
    COUNT(*) AS usage_frequency
FROM users u
WHERE u.createdAt >= date('now', '-1 year')
GROUP BY 'users 테이블'

UNION ALL

SELECT 
    '인덱스 최적화 제안' AS optimization_type,
    'news 테이블' AS table_name,
    'userId, collectedAt, publishedDate 복합 인덱스' AS suggested_index,
    COUNT(*) AS usage_frequency
FROM news n
WHERE n.userId IS NOT NULL 
    AND n.collectedAt >= date('now', '-1 year')
GROUP BY 'news 테이블'

UNION ALL

SELECT 
    '인덱스 최적화 제안' AS optimization_type,
    'radioSongs 테이블' AS table_name,
    'userId, lastPlayed, artist 복합 인덱스' AS suggested_index,
    COUNT(*) AS usage_frequency
FROM radioSongs rs
WHERE rs.userId IS NOT NULL 
    AND rs.lastPlayed >= date('now', '-1 year')
GROUP BY 'radioSongs 테이블'

UNION ALL

SELECT 
    '인덱스 최적화 제안' AS optimization_type,
    'books 테이블' AS table_name,
    'userId, collectedAt, publishedDate 복합 인덱스' AS suggested_index,
    COUNT(*) AS usage_frequency
FROM books b
WHERE b.userId IS NOT NULL 
    AND b.collectedAt >= date('now', '-1 year')
GROUP BY 'books 테이블'

UNION ALL

SELECT 
    '인덱스 최적화 제안' AS optimization_type,
    'apiKeys 테이블' AS table_name,
    'userId, isActive, createdAt 복합 인덱스' AS suggested_index,
    COUNT(*) AS usage_frequency
FROM apiKeys ak
WHERE ak.userId IS NOT NULL
GROUP BY 'apiKeys 테이블'

UNION ALL

SELECT 
    '인덱스 최적화 제안' AS optimization_type,
    'apiKeyUsage 테이블' AS table_name,
    'apiKeyId, createdAt, statusCode 복합 인덱스' AS suggested_index,
    COUNT(*) AS usage_frequency
FROM apiKeyUsage aku
WHERE aku.apiKeyId IS NOT NULL
    AND aku.createdAt >= date('now', '-1 year')
GROUP BY 'apiKeyUsage 테이블';

-- ============================================
-- 18. 추가 분석: 데이터 품질 검증 쿼리
-- ============================================

-- 데이터 무결성 및 품질 검증
SELECT 
    '데이터 품질 검증' AS validation_type,
    'users 테이블' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN email IS NULL OR email = '' THEN 1 END) AS missing_email,
    COUNT(CASE WHEN createdAt IS NULL THEN 1 END) AS missing_created_at,
    COUNT(CASE WHEN updatedAt IS NULL THEN 1 END) AS missing_updated_at,
    COUNT(CASE WHEN createdAt > updatedAt THEN 1 END) AS invalid_date_order,
    COUNT(CASE WHEN julianday('now') - julianday(createdAt) < 0 THEN 1 END) AS future_dates
FROM users

UNION ALL

SELECT 
    '데이터 품질 검증' AS validation_type,
    'news 테이블' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN title IS NULL OR title = '' THEN 1 END) AS missing_title,
    COUNT(CASE WHEN collectedAt IS NULL THEN 1 END) AS missing_collected_at,
    COUNT(CASE WHEN userId IS NOT NULL AND userId NOT IN (SELECT id FROM users) THEN 1 END) AS orphaned_records,
    COUNT(CASE WHEN publishedDate IS NOT NULL AND publishedDate > date('now') THEN 1 END) AS future_published_dates,
    COUNT(CASE WHEN importanceValue < 0 OR importanceValue > 100 THEN 1 END) AS invalid_importance_values
FROM news

UNION ALL

SELECT 
    '데이터 품질 검증' AS validation_type,
    'radioSongs 테이블' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN title IS NULL OR title = '' THEN 1 END) AS missing_title,
    COUNT(CASE WHEN lastPlayed IS NULL THEN 1 END) AS missing_last_played,
    COUNT(CASE WHEN userId IS NOT NULL AND userId NOT IN (SELECT id FROM users) THEN 1 END) AS orphaned_records,
    COUNT(CASE WHEN count < 0 THEN 1 END) AS negative_play_count,
    COUNT(CASE WHEN firstPlayed IS NOT NULL AND lastPlayed IS NOT NULL AND firstPlayed > lastPlayed THEN 1 END) AS invalid_date_order
FROM radioSongs

UNION ALL

SELECT 
    '데이터 품질 검증' AS validation_type,
    'books 테이블' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN title IS NULL OR title = '' THEN 1 END) AS missing_title,
    COUNT(CASE WHEN collectedAt IS NULL THEN 1 END) AS missing_collected_at,
    COUNT(CASE WHEN userId IS NOT NULL AND userId NOT IN (SELECT id FROM users) THEN 1 END) AS orphaned_records,
    COUNT(CASE WHEN publishedDate IS NOT NULL AND CAST(strftime('%Y', publishedDate) AS INTEGER) < 1900 THEN 1 END) AS invalid_publication_years,
    COUNT(CASE WHEN publishedDate IS NOT NULL AND publishedDate > date('now') THEN 1 END) AS future_publication_dates
FROM books

UNION ALL

SELECT 
    '데이터 품질 검증' AS validation_type,
    'apiKeys 테이블' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN apiKey IS NULL OR apiKey = '' THEN 1 END) AS missing_api_key,
    COUNT(CASE WHEN userId IS NULL THEN 1 END) AS missing_user_id,
    COUNT(CASE WHEN userId IS NOT NULL AND userId NOT IN (SELECT id FROM users) THEN 1 END) AS orphaned_records,
    COUNT(CASE WHEN createdAt IS NULL THEN 1 END) AS missing_created_at,
    COUNT(CASE WHEN expiresAt IS NOT NULL AND expiresAt < createdAt THEN 1 END) AS invalid_expiration_dates
FROM apiKeys

UNION ALL

SELECT 
    '데이터 품질 검증' AS validation_type,
    'apiKeyUsage 테이블' AS table_name,
    COUNT(*) AS total_records,
    COUNT(CASE WHEN apiKeyId IS NULL THEN 1 END) AS missing_api_key_id,
    COUNT(CASE WHEN apiKeyId IS NOT NULL AND apiKeyId NOT IN (SELECT id FROM apiKeys) THEN 1 END) AS orphaned_records,
    COUNT(CASE WHEN endpoint IS NULL OR endpoint = '' THEN 1 END) AS missing_endpoint,
    COUNT(CASE WHEN method IS NULL OR method = '' THEN 1 END) AS missing_method,
    COUNT(CASE WHEN createdAt IS NULL THEN 1 END) AS missing_created_at,
    COUNT(CASE WHEN statusCode < 100 OR statusCode >= 600 THEN 1 END) AS invalid_status_codes
FROM apiKeyUsage;

-- ============================================
-- 쿼리 종료
-- ============================================


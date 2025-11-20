-- ============================================
-- 복잡한 SQL 쿼리 샘플 (약 1000라인)
-- ============================================
-- 목적: 고급 사용자 행동 분석 및 예측 리포트
-- 테이블: users, news, radioSongs, books, apiKeys, apiKeyUsage
-- 작성일: 2025-01-XX
-- 리니지 연관도: 50% (중간 연관도 - 적절한 JOIN 관계 유지)
-- ============================================

-- ============================================
-- 1. 다중 레벨 CTE 정의
-- ============================================

WITH 
-- 사용자 기본 정보 및 가입 기간 계산
user_base_info AS (
    SELECT 
        u.id AS user_id,
        u.email,
        u.name,
        u.createdAt,
        u.updatedAt,
        -- 가입 기간 계산 (일 단위)
        CAST((julianday('now') - julianday(u.createdAt)) AS INTEGER) AS days_since_signup,
        -- 계정 업데이트 빈도
        CAST((julianday(u.updatedAt) - julianday(u.createdAt)) AS INTEGER) AS days_between_updates,
        -- 사용자 등급 분류
        CASE 
            WHEN julianday('now') - julianday(u.createdAt) > 365 THEN '장기 사용자'
            WHEN julianday('now') - julianday(u.createdAt) > 180 THEN '중기 사용자'
            WHEN julianday('now') - julianday(u.createdAt) > 90 THEN '단기 사용자'
            ELSE '신규 사용자'
        END AS user_tier
    FROM users u
    WHERE u.createdAt IS NOT NULL
),

-- 뉴스 수집 패턴 분석
news_collection_patterns AS (
    SELECT 
        n.userId,
        -- 시간대별 수집 패턴
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS morning_collections,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS afternoon_collections,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS evening_collections,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS night_collections,
        -- 요일별 수집 패턴
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' THEN 1 END) AS sunday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' THEN 1 END) AS monday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' THEN 1 END) AS tuesday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' THEN 1 END) AS wednesday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' THEN 1 END) AS thursday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' THEN 1 END) AS friday_count,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' THEN 1 END) AS saturday_count,
        -- 카테고리 선호도
        COUNT(DISTINCT n.category) AS preferred_categories_count,
        -- 키워드 다양성
        COUNT(DISTINCT n.keyword) AS keyword_diversity,
        -- 중요도 선호도
        AVG(n.importanceValue) AS avg_importance_preference,
        -- 출처 다양성
        COUNT(DISTINCT n.source) AS source_diversity,
        -- 최근 활동 강도
        COUNT(CASE WHEN n.collectedAt >= date('now', '-7 days') THEN 1 END) AS recent_week_activity,
        COUNT(CASE WHEN n.collectedAt >= date('now', '-30 days') THEN 1 END) AS recent_month_activity,
        -- 활동 연속성 (일별)
        COUNT(DISTINCT date(n.collectedAt)) AS active_days_count
    FROM news n
    WHERE n.collectedAt >= date('now', '-1 year')
    GROUP BY n.userId
),

-- 라디오 노래 수집 패턴 분석
radio_collection_patterns AS (
    SELECT 
        rs.userId,
        -- 아티스트 선호도 분석
        COUNT(DISTINCT rs.artist) AS artist_diversity,
        -- 장르 선호도 분석
        COUNT(DISTINCT rs.genre) AS genre_diversity,
        -- 재생 빈도 분석
        AVG(rs.count) AS avg_replay_count,
        MAX(rs.count) AS max_replay_count,
        MIN(rs.count) AS min_replay_count,
        -- 시간대별 재생 패턴
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS morning_plays,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS afternoon_plays,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS evening_plays,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS night_plays,
        -- 방송국 선호도
        COUNT(DISTINCT rs.stations) AS station_diversity,
        -- 최근 활동 강도
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-7 days') THEN 1 END) AS recent_week_activity,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-30 days') THEN 1 END) AS recent_month_activity,
        -- 활동 연속성
        COUNT(DISTINCT date(rs.lastPlayed)) AS active_days_count,
        -- 재생 기간 분석
        CAST((julianday(MAX(rs.lastPlayed)) - julianday(MIN(rs.firstPlayed))) AS INTEGER) AS listening_period_days
    FROM radioSongs rs
    WHERE rs.lastPlayed >= date('now', '-1 year')
    GROUP BY rs.userId
),

-- 도서 수집 패턴 분석
books_collection_patterns AS (
    SELECT 
        b.userId,
        -- 저자 선호도 분석
        COUNT(DISTINCT b.authors) AS author_diversity,
        -- 카테고리 선호도 분석
        COUNT(DISTINCT b.categories) AS category_diversity,
        -- 출판 연도 분석
        MIN(CAST(strftime('%Y', b.publishedDate) AS INTEGER)) AS oldest_book_year,
        MAX(CAST(strftime('%Y', b.publishedDate) AS INTEGER)) AS newest_book_year,
        -- 최근 활동 강도
        COUNT(CASE WHEN b.collectedAt >= date('now', '-7 days') THEN 1 END) AS recent_week_activity,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-30 days') THEN 1 END) AS recent_month_activity,
        COUNT(CASE WHEN b.collectedAt >= date('now', '-90 days') THEN 1 END) AS recent_quarter_activity,
        -- 활동 연속성
        COUNT(DISTINCT date(b.collectedAt)) AS active_days_count,
        -- 수집 기간 분석
        CAST((julianday(MAX(b.collectedAt)) - julianday(MIN(b.collectedAt))) AS INTEGER) AS collection_period_days
    FROM books b
    WHERE b.collectedAt >= date('now', '-1 year')
    GROUP BY b.userId
),

-- API 사용 패턴 분석
api_usage_patterns AS (
    SELECT 
        ak.userId,
        -- API 키 관리 패턴
        COUNT(DISTINCT ak.id) AS total_keys_created,
        COUNT(DISTINCT CASE WHEN ak.isActive = 1 THEN ak.id END) AS active_keys_count,
        COUNT(DISTINCT CASE WHEN ak.isActive = 0 THEN ak.id END) AS inactive_keys_count,
        -- API 호출 패턴
        COUNT(aku.id) AS total_api_calls,
        COUNT(DISTINCT aku.endpoint) AS endpoint_diversity,
        COUNT(DISTINCT aku.method) AS method_diversity,
        -- 시간대별 API 사용 패턴
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS morning_api_calls,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS afternoon_api_calls,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS evening_api_calls,
        COUNT(CASE WHEN CAST(strftime('%H', aku.createdAt) AS INTEGER) BETWEEN 0 AND 5 THEN 1 END) AS night_api_calls,
        -- 성공률 분석
        COUNT(CASE WHEN aku.statusCode BETWEEN 200 AND 299 THEN 1 END) AS success_calls,
        COUNT(CASE WHEN aku.statusCode >= 400 THEN 1 END) AS error_calls,
        -- 최근 활동 강도
        COUNT(CASE WHEN aku.createdAt >= date('now', '-7 days') THEN 1 END) AS recent_week_calls,
        COUNT(CASE WHEN aku.createdAt >= date('now', '-30 days') THEN 1 END) AS recent_month_calls,
        -- 활동 연속성
        COUNT(DISTINCT date(aku.createdAt)) AS active_days_count,
        -- 평균 응답 시간 (상태 코드 기반 추정)
        AVG(aku.statusCode) AS avg_status_code
    FROM apiKeys ak
    LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId
    WHERE ak.createdAt >= date('now', '-1 year')
        OR (aku.createdAt IS NOT NULL AND aku.createdAt >= date('now', '-1 year'))
    GROUP BY ak.userId
),

-- 사용자 활동 점수 계산
user_activity_scores AS (
    SELECT 
        ubi.user_id,
        -- 뉴스 활동 점수
        COALESCE(ncp.recent_week_activity, 0) * 2 +
        COALESCE(ncp.recent_month_activity, 0) * 1 +
        COALESCE(ncp.active_days_count, 0) * 0.5 AS news_activity_score,
        -- 라디오 활동 점수
        COALESCE(rcp.recent_week_activity, 0) * 2 +
        COALESCE(rcp.recent_month_activity, 0) * 1 +
        COALESCE(rcp.active_days_count, 0) * 0.5 AS radio_activity_score,
        -- 도서 활동 점수
        COALESCE(bcp.recent_week_activity, 0) * 3 +
        COALESCE(bcp.recent_month_activity, 0) * 2 +
        COALESCE(bcp.recent_quarter_activity, 0) * 1 +
        COALESCE(bcp.active_days_count, 0) * 0.5 AS books_activity_score,
        -- API 활동 점수
        COALESCE(aup.recent_week_calls, 0) * 0.1 +
        COALESCE(aup.recent_month_calls, 0) * 0.05 +
        COALESCE(aup.active_days_count, 0) * 0.01 AS api_activity_score
    FROM user_base_info ubi
    LEFT JOIN news_collection_patterns ncp ON ubi.user_id = ncp.userId
    LEFT JOIN radio_collection_patterns rcp ON ubi.user_id = rcp.userId
    LEFT JOIN books_collection_patterns bcp ON ubi.user_id = bcp.userId
    LEFT JOIN api_usage_patterns aup ON ubi.user_id = aup.userId
),

-- 사용자 행동 프로필 생성
user_behavior_profiles AS (
    SELECT 
        ubi.user_id,
        ubi.email,
        ubi.name,
        ubi.user_tier,
        ubi.days_since_signup,
        -- 활동 점수
        COALESCE(uas.news_activity_score, 0) AS news_score,
        COALESCE(uas.radio_activity_score, 0) AS radio_score,
        COALESCE(uas.books_activity_score, 0) AS books_score,
        COALESCE(uas.api_activity_score, 0) AS api_score,
        -- 총 활동 점수
        COALESCE(uas.news_activity_score, 0) +
        COALESCE(uas.radio_activity_score, 0) +
        COALESCE(uas.books_activity_score, 0) +
        COALESCE(uas.api_activity_score, 0) AS total_activity_score,
        -- 주요 활동 유형 결정
        CASE 
            WHEN COALESCE(uas.news_activity_score, 0) >= COALESCE(uas.radio_activity_score, 0)
                AND COALESCE(uas.news_activity_score, 0) >= COALESCE(uas.books_activity_score, 0)
                AND COALESCE(uas.news_activity_score, 0) >= COALESCE(uas.api_activity_score, 0)
            THEN '뉴스 중심'
            WHEN COALESCE(uas.radio_activity_score, 0) >= COALESCE(uas.news_activity_score, 0)
                AND COALESCE(uas.radio_activity_score, 0) >= COALESCE(uas.books_activity_score, 0)
                AND COALESCE(uas.radio_activity_score, 0) >= COALESCE(uas.api_activity_score, 0)
            THEN '음악 중심'
            WHEN COALESCE(uas.books_activity_score, 0) >= COALESCE(uas.news_activity_score, 0)
                AND COALESCE(uas.books_activity_score, 0) >= COALESCE(uas.radio_activity_score, 0)
                AND COALESCE(uas.books_activity_score, 0) >= COALESCE(uas.api_activity_score, 0)
            THEN '독서 중심'
            WHEN COALESCE(uas.api_activity_score, 0) >= COALESCE(uas.news_activity_score, 0)
                AND COALESCE(uas.api_activity_score, 0) >= COALESCE(uas.radio_activity_score, 0)
                AND COALESCE(uas.api_activity_score, 0) >= COALESCE(uas.books_activity_score, 0)
            THEN '개발자'
            ELSE '균형형'
        END AS primary_activity_type,
        -- 활동 다양성 점수
        (
            CASE WHEN COALESCE(uas.news_activity_score, 0) > 0 THEN 1 ELSE 0 END +
            CASE WHEN COALESCE(uas.radio_activity_score, 0) > 0 THEN 1 ELSE 0 END +
            CASE WHEN COALESCE(uas.books_activity_score, 0) > 0 THEN 1 ELSE 0 END +
            CASE WHEN COALESCE(uas.api_activity_score, 0) > 0 THEN 1 ELSE 0 END
        ) AS activity_diversity_score
    FROM user_base_info ubi
    LEFT JOIN user_activity_scores uas ON ubi.user_id = uas.user_id
),

-- 시간대별 활동 패턴 통합
time_pattern_analysis AS (
    SELECT 
        ubi.user_id,
        -- 뉴스 시간대 패턴
        COALESCE(ncp.morning_collections, 0) +
        COALESCE(rcp.morning_plays, 0) +
        COALESCE(aup.morning_api_calls, 0) AS total_morning_activity,
        COALESCE(ncp.afternoon_collections, 0) +
        COALESCE(rcp.afternoon_plays, 0) +
        COALESCE(aup.afternoon_api_calls, 0) AS total_afternoon_activity,
        COALESCE(ncp.evening_collections, 0) +
        COALESCE(rcp.evening_plays, 0) +
        COALESCE(aup.evening_api_calls, 0) AS total_evening_activity,
        COALESCE(ncp.night_collections, 0) +
        COALESCE(rcp.night_plays, 0) +
        COALESCE(aup.night_api_calls, 0) AS total_night_activity,
        -- 주요 활동 시간대 결정
        CASE 
            WHEN COALESCE(ncp.morning_collections, 0) + COALESCE(rcp.morning_plays, 0) + COALESCE(aup.morning_api_calls, 0) >=
                 GREATEST(
                     COALESCE(ncp.afternoon_collections, 0) + COALESCE(rcp.afternoon_plays, 0) + COALESCE(aup.afternoon_api_calls, 0),
                     COALESCE(ncp.evening_collections, 0) + COALESCE(rcp.evening_plays, 0) + COALESCE(aup.evening_api_calls, 0),
                     COALESCE(ncp.night_collections, 0) + COALESCE(rcp.night_plays, 0) + COALESCE(aup.night_api_calls, 0)
                 )
            THEN '아침형'
            WHEN COALESCE(ncp.afternoon_collections, 0) + COALESCE(rcp.afternoon_plays, 0) + COALESCE(aup.afternoon_api_calls, 0) >=
                 GREATEST(
                     COALESCE(ncp.evening_collections, 0) + COALESCE(rcp.evening_plays, 0) + COALESCE(aup.evening_api_calls, 0),
                     COALESCE(ncp.night_collections, 0) + COALESCE(rcp.night_plays, 0) + COALESCE(aup.night_api_calls, 0)
                 )
            THEN '오후형'
            WHEN COALESCE(ncp.evening_collections, 0) + COALESCE(rcp.evening_plays, 0) + COALESCE(aup.evening_api_calls, 0) >=
                 COALESCE(ncp.night_collections, 0) + COALESCE(rcp.night_plays, 0) + COALESCE(aup.night_api_calls, 0)
            THEN '저녁형'
            ELSE '야행형'
        END AS preferred_time_period
    FROM user_base_info ubi
    LEFT JOIN news_collection_patterns ncp ON ubi.user_id = ncp.userId
    LEFT JOIN radio_collection_patterns rcp ON ubi.user_id = rcp.userId
    LEFT JOIN api_usage_patterns aup ON ubi.user_id = aup.userId
),

-- 사용자 유사도 분석을 위한 벡터 생성
user_similarity_vectors AS (
    SELECT 
        ubp.user_id,
        ubp.news_score,
        ubp.radio_score,
        ubp.books_score,
        ubp.api_score,
        ubp.activity_diversity_score,
        -- 정규화된 점수 (0-1 범위)
        CAST(ubp.news_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_news_score,
        CAST(ubp.radio_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_radio_score,
        CAST(ubp.books_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_books_score,
        CAST(ubp.api_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_api_score
    FROM user_behavior_profiles ubp
    WHERE ubp.total_activity_score > 0
)

-- ============================================
-- 2. 메인 쿼리: 종합 사용자 행동 분석 리포트
-- ============================================

SELECT 
    -- 기본 정보
    ubp.user_id,
    ubp.email,
    ubp.name,
    ubp.user_tier,
    ubp.days_since_signup,
    
    -- 활동 점수
    ROUND(ubp.news_score, 2) AS news_activity_score,
    ROUND(ubp.radio_score, 2) AS radio_activity_score,
    ROUND(ubp.books_score, 2) AS books_activity_score,
    ROUND(ubp.api_score, 2) AS api_activity_score,
    ROUND(ubp.total_activity_score, 2) AS total_activity_score,
    ubp.activity_diversity_score,
    
    -- 행동 프로필
    ubp.primary_activity_type,
    tpa.preferred_time_period,
    
    -- 뉴스 패턴 상세
    ncp.morning_collections AS news_morning,
    ncp.afternoon_collections AS news_afternoon,
    ncp.evening_collections AS news_evening,
    ncp.night_collections AS news_night,
    ncp.preferred_categories_count AS news_categories,
    ncp.keyword_diversity AS news_keywords,
    ROUND(ncp.avg_importance_preference, 2) AS news_avg_importance,
    ncp.source_diversity AS news_sources,
    
    -- 라디오 패턴 상세
    rcp.artist_diversity AS radio_artists,
    rcp.genre_diversity AS radio_genres,
    ROUND(rcp.avg_replay_count, 2) AS radio_avg_replays,
    rcp.max_replay_count AS radio_max_replays,
    rcp.morning_plays AS radio_morning,
    rcp.afternoon_plays AS radio_afternoon,
    rcp.evening_plays AS radio_evening,
    rcp.night_plays AS radio_night,
    rcp.station_diversity AS radio_stations,
    rcp.listening_period_days AS radio_listening_days,
    
    -- 도서 패턴 상세
    bcp.author_diversity AS books_authors,
    bcp.category_diversity AS books_categories,
    bcp.oldest_book_year,
    bcp.newest_book_year,
    bcp.collection_period_days AS books_collection_days,
    
    -- API 패턴 상세
    aup.total_keys_created AS api_keys_total,
    aup.active_keys_count AS api_keys_active,
    aup.total_api_calls AS api_calls_total,
    aup.endpoint_diversity AS api_endpoints,
    aup.method_diversity AS api_methods,
    aup.morning_api_calls AS api_morning,
    aup.afternoon_api_calls AS api_afternoon,
    aup.evening_api_calls AS api_evening,
    aup.night_api_calls AS api_night,
    ROUND(CAST(aup.success_calls AS REAL) / NULLIF(aup.total_api_calls, 0) * 100, 2) AS api_success_rate,
    ROUND(CAST(aup.error_calls AS REAL) / NULLIF(aup.total_api_calls, 0) * 100, 2) AS api_error_rate,
    
    -- 시간대 패턴
    tpa.total_morning_activity,
    tpa.total_afternoon_activity,
    tpa.total_evening_activity,
    tpa.total_night_activity,
    
    -- 유사도 벡터
    ROUND(usv.normalized_news_score, 3) AS similarity_news,
    ROUND(usv.normalized_radio_score, 3) AS similarity_radio,
    ROUND(usv.normalized_books_score, 3) AS similarity_books,
    ROUND(usv.normalized_api_score, 3) AS similarity_api,
    
    -- 예측 점수 (활동 지속 가능성)
    CASE 
        WHEN ubp.total_activity_score > 100 
            AND ubp.activity_diversity_score >= 3
            AND ubp.days_since_signup > 90
        THEN '높음'
        WHEN ubp.total_activity_score > 50
            AND ubp.activity_diversity_score >= 2
            AND ubp.days_since_signup > 30
        THEN '보통'
        WHEN ubp.total_activity_score > 0
        THEN '낮음'
        ELSE '매우 낮음'
    END AS retention_prediction,
    
    -- 추천 활동 유형
    CASE 
        WHEN ubp.news_score < ubp.radio_score 
            AND ubp.news_score < ubp.books_score
        THEN '뉴스 수집 시작 권장'
        WHEN ubp.radio_score < ubp.news_score
            AND ubp.radio_score < ubp.books_score
        THEN '음악 탐색 시작 권장'
        WHEN ubp.books_score < ubp.news_score
            AND ubp.books_score < ubp.radio_score
        THEN '독서 시작 권장'
        ELSE '현재 활동 유지 권장'
    END AS activity_recommendation

FROM user_behavior_profiles ubp
LEFT JOIN news_collection_patterns ncp ON ubp.user_id = ncp.userId
LEFT JOIN radio_collection_patterns rcp ON ubp.user_id = rcp.userId
LEFT JOIN books_collection_patterns bcp ON ubp.user_id = bcp.userId
LEFT JOIN api_usage_patterns aup ON ubp.user_id = aup.userId
LEFT JOIN time_pattern_analysis tpa ON ubp.user_id = tpa.user_id
LEFT JOIN user_similarity_vectors usv ON ubp.user_id = usv.user_id

WHERE 
    ubp.total_activity_score > 0
    AND ubp.days_since_signup > 7  -- 최소 1주일 이상 활동한 사용자만

GROUP BY 
    ubp.user_id, ubp.email, ubp.name, ubp.user_tier, ubp.days_since_signup,
    ubp.news_score, ubp.radio_score, ubp.books_score, ubp.api_score,
    ubp.total_activity_score, ubp.activity_diversity_score,
    ubp.primary_activity_type,
    ncp.morning_collections, ncp.afternoon_collections, ncp.evening_collections, ncp.night_collections,
    ncp.preferred_categories_count, ncp.keyword_diversity, ncp.avg_importance_preference, ncp.source_diversity,
    rcp.artist_diversity, rcp.genre_diversity, rcp.avg_replay_count, rcp.max_replay_count,
    rcp.morning_plays, rcp.afternoon_plays, rcp.evening_plays, rcp.night_plays,
    rcp.station_diversity, rcp.listening_period_days,
    bcp.author_diversity, bcp.category_diversity, bcp.oldest_book_year, bcp.newest_book_year,
    bcp.collection_period_days,
    aup.total_keys_created, aup.active_keys_count, aup.total_api_calls,
    aup.endpoint_diversity, aup.method_diversity,
    aup.morning_api_calls, aup.afternoon_api_calls, aup.evening_api_calls, aup.night_api_calls,
    aup.success_calls, aup.error_calls,
    tpa.total_morning_activity, tpa.total_afternoon_activity,
    tpa.total_evening_activity, tpa.total_night_activity, tpa.preferred_time_period,
    usv.normalized_news_score, usv.normalized_radio_score,
    usv.normalized_books_score, usv.normalized_api_score

ORDER BY 
    ubp.total_activity_score DESC,
    ubp.activity_diversity_score DESC,
    ubp.days_since_signup DESC

LIMIT 200;

-- ============================================
-- 3. 서브쿼리: 유사 사용자 그룹 분석
-- ============================================

SELECT 
    ubp1.user_id AS user1_id,
    ubp1.email AS user1_email,
    ubp1.primary_activity_type AS user1_type,
    ubp2.user_id AS user2_id,
    ubp2.email AS user2_email,
    ubp2.primary_activity_type AS user2_type,
    -- 유사도 계산 (코사인 유사도 근사)
    ROUND(
        (
            (usv1.normalized_news_score * usv2.normalized_news_score) +
            (usv1.normalized_radio_score * usv2.normalized_radio_score) +
            (usv1.normalized_books_score * usv2.normalized_books_score) +
            (usv1.normalized_api_score * usv2.normalized_api_score)
        ) * 100, 2
    ) AS similarity_score
FROM user_behavior_profiles ubp1
INNER JOIN user_behavior_profiles ubp2 ON ubp1.user_id < ubp2.user_id
INNER JOIN user_similarity_vectors usv1 ON ubp1.user_id = usv1.user_id
INNER JOIN user_similarity_vectors usv2 ON ubp2.user_id = usv2.user_id
WHERE 
    ubp1.total_activity_score > 10
    AND ubp2.total_activity_score > 10
    AND ubp1.primary_activity_type = ubp2.primary_activity_type
ORDER BY similarity_score DESC
LIMIT 100;

-- ============================================
-- 4. 추가 분석: 사용자 세그먼트 분석
-- ============================================

-- 사용자 세그먼트별 통계
SELECT 
    CASE 
        WHEN ubp.total_activity_score > 200 THEN '파워 유저'
        WHEN ubp.total_activity_score > 100 THEN '활성 유저'
        WHEN ubp.total_activity_score > 50 THEN '일반 유저'
        WHEN ubp.total_activity_score > 0 THEN '신규 유저'
        ELSE '비활성 유저'
    END AS user_segment,
    COUNT(*) AS user_count,
    AVG(ubp.total_activity_score) AS avg_activity_score,
    AVG(ubp.diversity_score) AS avg_diversity_score,
    AVG(ubi.days_since_signup) AS avg_account_age_days,
    -- 세그먼트별 주요 활동 유형 분포
    COUNT(CASE WHEN ubp.primary_activity_type = '뉴스 중심' THEN 1 END) AS news_focused_count,
    COUNT(CASE WHEN ubp.primary_activity_type = '음악 중심' THEN 1 END) AS radio_focused_count,
    COUNT(CASE WHEN ubp.primary_activity_type = '독서 중심' THEN 1 END) AS books_focused_count,
    COUNT(CASE WHEN ubp.primary_activity_type = '개발자' THEN 1 END) AS developer_count,
    COUNT(CASE WHEN ubp.primary_activity_type = '균형형' THEN 1 END) AS balanced_count
FROM user_behavior_profiles ubp
INNER JOIN user_base_info ubi ON ubp.user_id = ubi.user_id
WHERE ubp.total_activity_score > 0
GROUP BY user_segment
ORDER BY avg_activity_score DESC;

-- ============================================
-- 5. 추가 분석: 활동 패턴 클러스터링 준비 데이터
-- ============================================

-- 사용자 활동 패턴 벡터 생성 (머신러닝 클러스터링용)
SELECT 
    ubp.user_id,
    ubp.email,
    -- 정규화된 활동 점수 (0-1 범위)
    CAST(ubp.news_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_news,
    CAST(ubp.radio_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_radio,
    CAST(ubp.books_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_books,
    CAST(ubp.api_activity_score AS REAL) / NULLIF(ubp.total_activity_score, 0) AS normalized_api,
    -- 시간대 패턴 벡터
    CAST(tpa.total_morning_activity AS REAL) / NULLIF(
        tpa.total_morning_activity + tpa.total_afternoon_activity + 
        tpa.total_evening_activity + tpa.total_night_activity, 0
    ) AS normalized_morning,
    CAST(tpa.total_afternoon_activity AS REAL) / NULLIF(
        tpa.total_morning_activity + tpa.total_afternoon_activity + 
        tpa.total_evening_activity + tpa.total_night_activity, 0
    ) AS normalized_afternoon,
    CAST(tpa.total_evening_activity AS REAL) / NULLIF(
        tpa.total_morning_activity + tpa.total_afternoon_activity + 
        tpa.total_evening_activity + tpa.total_night_activity, 0
    ) AS normalized_evening,
    CAST(tpa.total_night_activity AS REAL) / NULLIF(
        tpa.total_morning_activity + tpa.total_afternoon_activity + 
        tpa.total_evening_activity + tpa.total_night_activity, 0
    ) AS normalized_night,
    -- 다양성 점수
    ubp.diversity_score,
    -- 계정 연령
    ubi.days_since_signup
FROM user_behavior_profiles ubp
INNER JOIN user_base_info ubi ON ubp.user_id = ubi.user_id
LEFT JOIN time_pattern_analysis tpa ON ubp.user_id = tpa.user_id
WHERE ubp.total_activity_score > 10
ORDER BY ubp.total_activity_score DESC;

-- ============================================
-- 6. 추가 분석: 사용자 이탈 예측 지표
-- ============================================

-- 사용자 이탈 위험도 분석
SELECT 
    ubp.user_id,
    ubp.email,
    ubp.name,
    ubi.days_since_signup,
    ubi.account_status,
    ubp.total_activity_score,
    ubp.diversity_score,
    -- 최근 활동 감소율 계산
    CASE 
        WHEN ncp.recent_week_activity > 0 AND ncp.recent_month_activity > 0
        THEN ROUND(
            (CAST(ncp.recent_week_activity AS REAL) / NULLIF(ncp.recent_month_activity, 0) - 1) * 100, 
            2
        )
        ELSE NULL
    END AS news_activity_decline_rate,
    CASE 
        WHEN rcp.recent_week_activity > 0 AND rcp.recent_month_activity > 0
        THEN ROUND(
            (CAST(rcp.recent_week_activity AS REAL) / NULLIF(rcp.recent_month_activity, 0) - 1) * 100, 
            2
        )
        ELSE NULL
    END AS radio_activity_decline_rate,
    CASE 
        WHEN bcp.recent_week_activity > 0 AND bcp.recent_month_activity > 0
        THEN ROUND(
            (CAST(bcp.recent_week_activity AS REAL) / NULLIF(bcp.recent_month_activity, 0) - 1) * 100, 
            2
        )
        ELSE NULL
    END AS books_activity_decline_rate,
    -- 이탈 위험도 점수 계산
    CASE 
        WHEN ubi.account_status = '휴면' THEN 100
        WHEN ubi.account_status = '비활성' AND ubp.total_activity_score = 0 THEN 80
        WHEN ubp.total_activity_score > 0 
            AND (
                (ncp.recent_week_activity IS NULL OR ncp.recent_week_activity = 0)
                AND (rcp.recent_week_activity IS NULL OR rcp.recent_week_activity = 0)
                AND (bcp.recent_week_activity IS NULL OR bcp.recent_week_activity = 0)
                AND (aup.recent_week_calls IS NULL OR aup.recent_week_calls = 0)
            )
        THEN 60
        WHEN ubp.total_activity_score > 0 
            AND (
                (ncp.recent_week_activity IS NOT NULL AND ncp.recent_week_activity < ncp.recent_month_activity / 4)
                OR (rcp.recent_week_activity IS NOT NULL AND rcp.recent_week_activity < rcp.recent_month_activity / 4)
            )
        THEN 40
        ELSE 20
    END AS churn_risk_score,
    -- 이탈 예측 카테고리
    CASE 
        WHEN ubi.account_status = '휴면' THEN '즉시 이탈 위험'
        WHEN ubi.account_status = '비활성' AND ubp.total_activity_score = 0 THEN '높은 이탈 위험'
        WHEN ubp.total_activity_score > 0 
            AND (
                (ncp.recent_week_activity IS NULL OR ncp.recent_week_activity = 0)
                AND (rcp.recent_week_activity IS NULL OR rcp.recent_week_activity = 0)
                AND (bcp.recent_week_activity IS NULL OR bcp.recent_week_activity = 0)
            )
        THEN '중간 이탈 위험'
        WHEN ubp.total_activity_score > 0 
            AND (
                (ncp.recent_week_activity IS NOT NULL AND ncp.recent_week_activity < ncp.recent_month_activity / 4)
                OR (rcp.recent_week_activity IS NOT NULL AND rcp.recent_week_activity < rcp.recent_month_activity / 4)
            )
        THEN '낮은 이탈 위험'
        ELSE '정상 활동'
    END AS churn_risk_category
FROM user_behavior_profiles ubp
INNER JOIN user_base_info ubi ON ubp.user_id = ubi.user_id
LEFT JOIN news_collection_patterns ncp ON ubp.user_id = ncp.userId
LEFT JOIN radio_collection_patterns rcp ON ubp.user_id = rcp.userId
LEFT JOIN books_collection_patterns bcp ON ubp.user_id = bcp.userId
LEFT JOIN api_usage_patterns aup ON ubp.user_id = aup.userId
WHERE ubi.days_since_signup > 7
ORDER BY churn_risk_score DESC, ubp.total_activity_score DESC;

-- ============================================
-- 7. 추가 분석: 사용자 참여도 점수 계산
-- ============================================

-- 종합 참여도 점수 계산
SELECT 
    ubp.user_id,
    ubp.email,
    ubp.name,
    -- 기본 활동 점수 (0-100)
    LEAST(100, ubp.total_activity_score / 10) AS base_engagement_score,
    -- 다양성 보너스 (0-20)
    ubp.diversity_score * 5 AS diversity_bonus,
    -- 일관성 보너스 (활동 일수 기반, 0-20)
    LEAST(20, 
        (COALESCE(ncp.active_days_count, 0) + 
         COALESCE(rcp.active_days_count, 0) + 
         COALESCE(bcp.active_days_count, 0) + 
         COALESCE(aup.active_days_count, 0)) / 5
    ) AS consistency_bonus,
    -- 최근 활동 보너스 (0-20)
    CASE 
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 50 THEN 20
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 20 THEN 15
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 10 THEN 10
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 0 THEN 5
        ELSE 0
    END AS recent_activity_bonus,
    -- 계정 연령 보너스 (0-20)
    LEAST(20, ubi.days_since_signup / 18) AS account_age_bonus,
    -- 종합 참여도 점수 (0-200)
    LEAST(100, ubp.total_activity_score / 10) +
    (ubp.diversity_score * 5) +
    LEAST(20, 
        (COALESCE(ncp.active_days_count, 0) + 
         COALESCE(rcp.active_days_count, 0) + 
         COALESCE(bcp.active_days_count, 0) + 
         COALESCE(aup.active_days_count, 0)) / 5
    ) +
    CASE 
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 50 THEN 20
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 20 THEN 15
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 10 THEN 10
        WHEN (COALESCE(ncp.recent_week_activity, 0) + 
              COALESCE(rcp.recent_week_activity, 0) + 
              COALESCE(bcp.recent_week_activity, 0) + 
              COALESCE(aup.recent_week_calls, 0)) > 0 THEN 5
        ELSE 0
    END +
    LEAST(20, ubi.days_since_signup / 18) AS total_engagement_score,
    -- 참여도 등급
    CASE 
        WHEN (LEAST(100, ubp.total_activity_score / 10) +
              (ubp.diversity_score * 5) +
              LEAST(20, 
                  (COALESCE(ncp.active_days_count, 0) + 
                   COALESCE(rcp.active_days_count, 0) + 
                   COALESCE(bcp.active_days_count, 0) + 
                   COALESCE(aup.active_days_count, 0)) / 5
              ) +
              CASE 
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 50 THEN 20
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 20 THEN 15
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 10 THEN 10
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 0 THEN 5
                  ELSE 0
              END +
              LEAST(20, ubi.days_since_signup / 18)) >= 150 THEN '최고'
        WHEN (LEAST(100, ubp.total_activity_score / 10) +
              (ubp.diversity_score * 5) +
              LEAST(20, 
                  (COALESCE(ncp.active_days_count, 0) + 
                   COALESCE(rcp.active_days_count, 0) + 
                   COALESCE(bcp.active_days_count, 0) + 
                   COALESCE(aup.active_days_count, 0)) / 5
              ) +
              CASE 
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 50 THEN 20
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 20 THEN 15
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 10 THEN 10
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 0 THEN 5
                  ELSE 0
              END +
              LEAST(20, ubi.days_since_signup / 18)) >= 100 THEN '높음'
        WHEN (LEAST(100, ubp.total_activity_score / 10) +
              (ubp.diversity_score * 5) +
              LEAST(20, 
                  (COALESCE(ncp.active_days_count, 0) + 
                   COALESCE(rcp.active_days_count, 0) + 
                   COALESCE(bcp.active_days_count, 0) + 
                   COALESCE(aup.active_days_count, 0)) / 5
              ) +
              CASE 
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 50 THEN 20
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 20 THEN 15
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 10 THEN 10
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 0 THEN 5
                  ELSE 0
              END +
              LEAST(20, ubi.days_since_signup / 18)) >= 50 THEN '보통'
        WHEN (LEAST(100, ubp.total_activity_score / 10) +
              (ubp.diversity_score * 5) +
              LEAST(20, 
                  (COALESCE(ncp.active_days_count, 0) + 
                   COALESCE(rcp.active_days_count, 0) + 
                   COALESCE(bcp.active_days_count, 0) + 
                   COALESCE(aup.active_days_count, 0)) / 5
              ) +
              CASE 
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 50 THEN 20
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 20 THEN 15
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 10 THEN 10
                  WHEN (COALESCE(ncp.recent_week_activity, 0) + 
                        COALESCE(rcp.recent_week_activity, 0) + 
                        COALESCE(bcp.recent_week_activity, 0) + 
                        COALESCE(aup.recent_week_calls, 0)) > 0 THEN 5
                  ELSE 0
              END +
              LEAST(20, ubi.days_since_signup / 18)) > 0 THEN '낮음'
        ELSE '매우 낮음'
    END AS engagement_grade
FROM user_behavior_profiles ubp
INNER JOIN user_base_info ubi ON ubp.user_id = ubi.user_id
LEFT JOIN news_collection_patterns ncp ON ubp.user_id = ncp.userId
LEFT JOIN radio_collection_patterns rcp ON ubp.user_id = rcp.userId
LEFT JOIN books_collection_patterns bcp ON ubp.user_id = bcp.userId
LEFT JOIN api_usage_patterns aup ON ubp.user_id = aup.userId
WHERE ubp.total_activity_score > 0
ORDER BY total_engagement_score DESC;

-- ============================================
-- 8. 추가 분석: 활동 패턴 예측 모델 데이터
-- ============================================

-- 다음 활동 예측을 위한 특징 벡터 생성
SELECT 
    ubp.user_id,
    ubp.email,
    -- 과거 활동 패턴
    ncp.recent_30d AS news_30d_ago,
    ncp.recent_90d AS news_90d_ago,
    rcp.recent_30d_plays AS radio_30d_ago,
    rcp.recent_90d_plays AS radio_90d_ago,
    bcp.recent_30d_collections AS books_30d_ago,
    bcp.recent_90d_collections AS books_90d_ago,
    aup.recent_30d_calls AS api_30d_ago,
    aup.recent_90d_calls AS api_90d_ago,
    -- 활동 트렌드 (증가/감소)
    CASE 
        WHEN ncp.recent_30d > 0 AND ncp.recent_90d > 0
        THEN CAST(ncp.recent_30d AS REAL) / NULLIF(ncp.recent_90d, 0)
        ELSE NULL
    END AS news_trend_ratio,
    CASE 
        WHEN rcp.recent_30d_plays > 0 AND rcp.recent_90d_plays > 0
        THEN CAST(rcp.recent_30d_plays AS REAL) / NULLIF(rcp.recent_90d_plays, 0)
        ELSE NULL
    END AS radio_trend_ratio,
    CASE 
        WHEN bcp.recent_30d_collections > 0 AND bcp.recent_90d_collections > 0
        THEN CAST(bcp.recent_30d_collections AS REAL) / NULLIF(bcp.recent_90d_collections, 0)
        ELSE NULL
    END AS books_trend_ratio,
    -- 계정 연령
    ubi.days_since_signup,
    -- 활동 다양성
    ubp.diversity_score,
    -- 예측 대상: 다음 30일 활동 예상치
    CASE 
        WHEN ncp.recent_30d > 0 AND ncp.recent_90d > 0
        THEN CAST(ncp.recent_30d AS REAL) * (CAST(ncp.recent_30d AS REAL) / NULLIF(ncp.recent_90d, 0))
        ELSE COALESCE(ncp.recent_30d, 0)
    END AS predicted_news_next_30d,
    CASE 
        WHEN rcp.recent_30d_plays > 0 AND rcp.recent_90d_plays > 0
        THEN CAST(rcp.recent_30d_plays AS REAL) * (CAST(rcp.recent_30d_plays AS REAL) / NULLIF(rcp.recent_90d_plays, 0))
        ELSE COALESCE(rcp.recent_30d_plays, 0)
    END AS predicted_radio_next_30d,
    CASE 
        WHEN bcp.recent_30d_collections > 0 AND bcp.recent_90d_collections > 0
        THEN CAST(bcp.recent_30d_collections AS REAL) * (CAST(bcp.recent_30d_collections AS REAL) / NULLIF(bcp.recent_90d_collections, 0))
        ELSE COALESCE(bcp.recent_30d_collections, 0)
    END AS predicted_books_next_30d
FROM user_behavior_profiles ubp
INNER JOIN user_base_info ubi ON ubp.user_id = ubi.user_id
LEFT JOIN news_collection_patterns ncp ON ubp.user_id = ncp.userId
LEFT JOIN radio_collection_patterns rcp ON ubp.user_id = rcp.userId
LEFT JOIN books_collection_patterns bcp ON ubp.user_id = bcp.userId
LEFT JOIN api_usage_patterns aup ON ubp.user_id = aup.userId
WHERE ubp.total_activity_score > 0
    AND ubi.days_since_signup > 30
ORDER BY ubp.total_activity_score DESC;

-- ============================================
-- 쿼리 종료
-- ============================================


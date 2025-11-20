-- ============================================
-- 복잡한 SQL 쿼리 샘플 (약 750라인)
-- ============================================
-- 목적: 완전한 데이터 리니지 연결 구조를 보여주는 통합 분석 쿼리
-- 테이블: users, news, radioSongs, books, apiKeys, apiKeyUsage
-- 작성일: 2025-11-19
-- 특징: 모든 테이블 간 관계가 명확하게 연결되어 리니지 시각화에 완벽하게 표시됨
-- ============================================

-- ============================================
-- 1단계: 기본 사용자 및 활동 데이터 준비
-- ============================================

WITH 
-- 사용자 기본 정보 및 활동 요약
user_base_info AS (
    SELECT 
        u.id AS user_id,
        u.email,
        u.name,
        u.createdAt,
        u.updatedAt,
        CAST((julianday('now') - julianday(u.createdAt)) AS INTEGER) AS account_age_days
    FROM users u
    WHERE u.createdAt IS NOT NULL
),

-- 사용자별 뉴스 활동 통계
user_news_activity AS (
    SELECT 
        ubi.user_id,
        COUNT(DISTINCT n.id) AS total_news_count,
        COUNT(DISTINCT n.category) AS category_count,
        COUNT(DISTINCT n.keyword) AS keyword_count,
        MAX(n.publishedDate) AS latest_news_date,
        MIN(n.publishedDate) AS earliest_news_date,
        AVG(n.importanceValue) AS avg_importance,
        SUM(CASE WHEN n.importanceStars >= 3 THEN 1 ELSE 0 END) AS high_importance_count
    FROM user_base_info ubi
    LEFT JOIN news n ON ubi.user_id = n.userId
    WHERE n.collectedAt >= date('now', '-1 year')
    GROUP BY ubi.user_id
),

-- 사용자별 라디오 노래 활동 통계
user_radio_activity AS (
    SELECT 
        ubi.user_id,
        COUNT(DISTINCT rs.id) AS total_songs_count,
        COUNT(DISTINCT rs.artist) AS unique_artists_count,
        COUNT(DISTINCT rs.genre) AS unique_genres_count,
        SUM(rs.count) AS total_play_count,
        MAX(rs.lastPlayed) AS latest_play_date,
        MIN(rs.firstPlayed) AS earliest_play_date,
        AVG(rs.count) AS avg_play_count_per_song
    FROM user_base_info ubi
    LEFT JOIN radioSongs rs ON ubi.user_id = rs.userId
    WHERE rs.collectedAt >= date('now', '-1 year')
    GROUP BY ubi.user_id
),

-- 사용자별 도서 활동 통계
user_books_activity AS (
    SELECT 
        ubi.user_id,
        COUNT(DISTINCT b.id) AS total_books_count,
        COUNT(DISTINCT b.authors) AS unique_authors_count,
        COUNT(DISTINCT b.categories) AS unique_categories_count,
        MAX(b.publishedDate) AS latest_book_date,
        MIN(b.publishedDate) AS earliest_book_date
    FROM user_base_info ubi
    LEFT JOIN books b ON ubi.user_id = b.userId
    WHERE b.collectedAt >= date('now', '-1 year')
    GROUP BY ubi.user_id
),

-- 사용자별 API 사용 통계
user_api_activity AS (
    SELECT 
        ubi.user_id,
        COUNT(DISTINCT ak.id) AS total_api_keys_count,
        COUNT(DISTINCT CASE WHEN ak.isActive = 1 THEN ak.id END) AS active_api_keys_count,
        COUNT(aku.id) AS total_api_calls,
        COUNT(DISTINCT aku.endpoint) AS unique_endpoints_count,
        MAX(aku.createdAt) AS last_api_call_date,
        MIN(aku.createdAt) AS first_api_call_date,
        AVG(aku.statusCode) AS avg_status_code
    FROM user_base_info ubi
    LEFT JOIN apiKeys ak ON ubi.user_id = ak.userId
    LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId
    WHERE ubi.user_id IS NOT NULL
    GROUP BY ubi.user_id
),

-- ============================================
-- 2단계: 카테고리 및 장르별 집계 분석
-- ============================================

-- 카테고리별 뉴스 통계
category_news_summary AS (
    SELECT 
        n.category,
        COUNT(*) AS news_count,
        COUNT(DISTINCT n.userId) AS user_count,
        AVG(n.importanceValue) AS avg_importance,
        MAX(n.publishedDate) AS latest_news_date,
        MIN(n.publishedDate) AS earliest_news_date
    FROM news n
    WHERE n.category IS NOT NULL
        AND n.publishedDate >= date('now', '-3 months')
    GROUP BY n.category
    HAVING COUNT(*) >= 5
),

-- 아티스트별 라디오 통계
artist_radio_summary AS (
    SELECT 
        rs.artist,
        COUNT(DISTINCT rs.id) AS song_count,
        COUNT(DISTINCT rs.userId) AS user_count,
        SUM(rs.count) AS total_play_count,
        AVG(rs.count) AS avg_play_count,
        MAX(rs.lastPlayed) AS latest_play_date
    FROM radioSongs rs
    WHERE rs.artist IS NOT NULL
        AND rs.lastPlayed >= date('now', '-3 months')
    GROUP BY rs.artist
    HAVING COUNT(DISTINCT rs.id) >= 3
),

-- 저자별 도서 통계
author_books_summary AS (
    SELECT 
        b.authors,
        COUNT(DISTINCT b.id) AS book_count,
        COUNT(DISTINCT b.userId) AS user_count,
        MAX(b.publishedDate) AS latest_book_date
    FROM books b
    WHERE b.authors IS NOT NULL
        AND b.publishedDate >= date('now', '-1 year')
    GROUP BY b.authors
    HAVING COUNT(DISTINCT b.id) >= 2
),

-- ============================================
-- 3단계: 시간대별 활동 분석
-- ============================================

-- 월별 활동 통계 (뉴스, 라디오, 도서 통합)
monthly_activity_summary AS (
    SELECT 
        ubi.user_id,
        strftime('%Y-%m', n.collectedAt) AS activity_month,
        'news' AS activity_type,
        COUNT(*) AS activity_count
    FROM user_base_info ubi
    INNER JOIN news n ON ubi.user_id = n.userId
    WHERE n.collectedAt >= date('now', '-6 months')
    GROUP BY ubi.user_id, strftime('%Y-%m', n.collectedAt)
    
    UNION ALL
    
    SELECT 
        ubi.user_id,
        strftime('%Y-%m', rs.collectedAt) AS activity_month,
        'radio' AS activity_type,
        COUNT(*) AS activity_count
    FROM user_base_info ubi
    INNER JOIN radioSongs rs ON ubi.user_id = rs.userId
    WHERE rs.collectedAt >= date('now', '-6 months')
    GROUP BY ubi.user_id, strftime('%Y-%m', rs.collectedAt)
    
    UNION ALL
    
    SELECT 
        ubi.user_id,
        strftime('%Y-%m', b.collectedAt) AS activity_month,
        'books' AS activity_type,
        COUNT(*) AS activity_count
    FROM user_base_info ubi
    INNER JOIN books b ON ubi.user_id = b.userId
    WHERE b.collectedAt >= date('now', '-6 months')
    GROUP BY ubi.user_id, strftime('%Y-%m', b.collectedAt)
),

-- ============================================
-- 4단계: API 사용 패턴 분석
-- ============================================

-- API 엔드포인트별 사용 통계
api_endpoint_summary AS (
    SELECT 
        aku.endpoint,
        aku.method,
        COUNT(*) AS total_calls,
        COUNT(DISTINCT aku.apiKeyId) AS unique_api_keys,
        AVG(aku.statusCode) AS avg_status_code,
        COUNT(CASE WHEN aku.statusCode >= 200 AND aku.statusCode < 300 THEN 1 END) AS success_count,
        COUNT(CASE WHEN aku.statusCode >= 400 THEN 1 END) AS error_count,
        MAX(aku.createdAt) AS last_call_date
    FROM apiKeyUsage aku
    WHERE aku.createdAt >= date('now', '-3 months')
    GROUP BY aku.endpoint, aku.method
),

-- API 키별 사용 통계
api_key_summary AS (
    SELECT 
        ak.id AS api_key_id,
        ak.userId,
        ak.name AS api_key_name,
        ak.isActive,
        COUNT(aku.id) AS total_usage_count,
        COUNT(DISTINCT aku.endpoint) AS unique_endpoints,
        MAX(aku.createdAt) AS last_used_date,
        MIN(aku.createdAt) AS first_used_date
    FROM apiKeys ak
    LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId
    GROUP BY ak.id, ak.userId, ak.name, ak.isActive
),

-- ============================================
-- 5단계: 통합 사용자 활동 점수 계산
-- ============================================

-- 사용자 활동 종합 점수
user_activity_score AS (
    SELECT 
        ubi.user_id,
        ubi.email,
        ubi.name,
        ubi.account_age_days,
        COALESCE(una.total_news_count, 0) AS news_count,
        COALESCE(ura.total_songs_count, 0) AS radio_count,
        COALESCE(uba.total_books_count, 0) AS books_count,
        COALESCE(uaa.total_api_calls, 0) AS api_calls_count,
        -- 종합 활동 점수 계산
        (
            COALESCE(una.total_news_count, 0) * 1.0 +
            COALESCE(ura.total_songs_count, 0) * 2.0 +
            COALESCE(uba.total_books_count, 0) * 3.0 +
            COALESCE(uaa.total_api_calls, 0) * 0.1
        ) AS total_activity_score,
        -- 활동 유형 분류
        CASE 
            WHEN COALESCE(una.total_news_count, 0) > 50 THEN '뉴스 수집가'
            WHEN COALESCE(ura.total_songs_count, 0) > 100 THEN '음악 애호가'
            WHEN COALESCE(uba.total_books_count, 0) > 20 THEN '독서가'
            WHEN COALESCE(uaa.total_api_calls, 0) > 1000 THEN 'API 개발자'
            ELSE '일반 사용자'
        END AS user_type
    FROM user_base_info ubi
    LEFT JOIN user_news_activity una ON ubi.user_id = una.user_id
    LEFT JOIN user_radio_activity ura ON ubi.user_id = ura.user_id
    LEFT JOIN user_books_activity uba ON ubi.user_id = uba.user_id
    LEFT JOIN user_api_activity uaa ON ubi.user_id = uaa.user_id
),

-- ============================================
-- 6단계: 카테고리-사용자 매핑 분석
-- ============================================

-- 사용자별 선호 카테고리 분석
user_category_preference AS (
    SELECT 
        uas.user_id,
        uas.email,
        uas.name,
        cns.category,
        COUNT(*) AS category_news_count,
        AVG(n.importanceValue) AS avg_category_importance
    FROM user_activity_score uas
    INNER JOIN news n ON uas.user_id = n.userId
    INNER JOIN category_news_summary cns ON n.category = cns.category
    WHERE n.publishedDate >= date('now', '-3 months')
    GROUP BY uas.user_id, uas.email, uas.name, cns.category
    HAVING COUNT(*) >= 3
),

-- 사용자별 선호 아티스트 분석
user_artist_preference AS (
    SELECT 
        uas.user_id,
        uas.email,
        uas.name,
        ars.artist,
        COUNT(DISTINCT rs.id) AS artist_song_count,
        SUM(rs.count) AS total_play_count
    FROM user_activity_score uas
    INNER JOIN radioSongs rs ON uas.user_id = rs.userId
    INNER JOIN artist_radio_summary ars ON rs.artist = ars.artist
    WHERE rs.lastPlayed >= date('now', '-3 months')
    GROUP BY uas.user_id, uas.email, uas.name, ars.artist
    HAVING COUNT(DISTINCT rs.id) >= 2
),

-- 사용자별 선호 저자 분석
user_author_preference AS (
    SELECT 
        uas.user_id,
        uas.email,
        uas.name,
        abs.authors,
        COUNT(DISTINCT b.id) AS author_book_count
    FROM user_activity_score uas
    INNER JOIN books b ON uas.user_id = b.userId
    INNER JOIN author_books_summary abs ON b.authors = abs.authors
    WHERE b.publishedDate >= date('now', '-1 year')
    GROUP BY uas.user_id, uas.email, uas.name, abs.authors
    HAVING COUNT(DISTINCT b.id) >= 1
),

-- ============================================
-- 7단계: API 사용 패턴과 콘텐츠 활동 연관 분석
-- ============================================

-- API 사용과 콘텐츠 활동의 상관관계 분석
api_content_correlation AS (
    SELECT 
        uas.user_id,
        uas.email,
        uas.name,
        uas.total_activity_score,
        uaa.total_api_calls,
        uaa.unique_endpoints_count,
        una.total_news_count,
        ura.total_songs_count,
        uba.total_books_count,
        -- API 사용 강도 계산
        CASE 
            WHEN uaa.total_api_calls > 1000 THEN '높음'
            WHEN uaa.total_api_calls > 100 THEN '보통'
            WHEN uaa.total_api_calls > 0 THEN '낮음'
            ELSE '없음'
        END AS api_usage_level,
        -- 콘텐츠 활동 강도 계산
        CASE 
            WHEN (COALESCE(una.total_news_count, 0) + COALESCE(ura.total_songs_count, 0) + COALESCE(uba.total_books_count, 0)) > 200 THEN '높음'
            WHEN (COALESCE(una.total_news_count, 0) + COALESCE(ura.total_songs_count, 0) + COALESCE(uba.total_books_count, 0)) > 50 THEN '보통'
            WHEN (COALESCE(una.total_news_count, 0) + COALESCE(ura.total_songs_count, 0) + COALESCE(uba.total_books_count, 0)) > 0 THEN '낮음'
            ELSE '없음'
        END AS content_activity_level
    FROM user_activity_score uas
    LEFT JOIN user_api_activity uaa ON uas.user_id = uaa.user_id
    LEFT JOIN user_news_activity una ON uas.user_id = una.user_id
    LEFT JOIN user_radio_activity ura ON uas.user_id = ura.user_id
    LEFT JOIN user_books_activity uba ON uas.user_id = uba.user_id
),

-- ============================================
-- 메인 쿼리: 최종 통합 리포트
-- ============================================

SELECT 
    -- 사용자 기본 정보
    uas.user_id,
    uas.email,
    uas.name,
    uas.account_age_days,
    uas.user_type,
    uas.total_activity_score,
    
    -- 뉴스 활동 상세
    COALESCE(una.total_news_count, 0) AS news_total_count,
    COALESCE(una.category_count, 0) AS news_category_count,
    COALESCE(una.keyword_count, 0) AS news_keyword_count,
    una.latest_news_date,
    una.earliest_news_date,
    ROUND(COALESCE(una.avg_importance, 0), 2) AS news_avg_importance,
    COALESCE(una.high_importance_count, 0) AS news_high_importance_count,
    
    -- 라디오 활동 상세
    COALESCE(ura.total_songs_count, 0) AS radio_total_songs,
    COALESCE(ura.unique_artists_count, 0) AS radio_unique_artists,
    COALESCE(ura.unique_genres_count, 0) AS radio_unique_genres,
    COALESCE(ura.total_play_count, 0) AS radio_total_plays,
    ura.latest_play_date AS radio_latest_play,
    ura.earliest_play_date AS radio_earliest_play,
    ROUND(COALESCE(ura.avg_play_count_per_song, 0), 2) AS radio_avg_plays_per_song,
    
    -- 도서 활동 상세
    COALESCE(uba.total_books_count, 0) AS books_total_count,
    COALESCE(uba.unique_authors_count, 0) AS books_unique_authors,
    COALESCE(uba.unique_categories_count, 0) AS books_unique_categories,
    uba.latest_book_date AS books_latest_date,
    uba.earliest_book_date AS books_earliest_date,
    
    -- API 사용 상세
    COALESCE(uaa.total_api_keys_count, 0) AS api_total_keys,
    COALESCE(uaa.active_api_keys_count, 0) AS api_active_keys,
    COALESCE(uaa.total_api_calls, 0) AS api_total_calls,
    COALESCE(uaa.unique_endpoints_count, 0) AS api_unique_endpoints,
    uaa.last_api_call_date AS api_last_call,
    uaa.first_api_call_date AS api_first_call,
    ROUND(COALESCE(uaa.avg_status_code, 0), 2) AS api_avg_status_code,
    
    -- 상관관계 분석 결과
    acc.api_usage_level,
    acc.content_activity_level,
    
    -- 최근 활동 여부
    CASE 
        WHEN una.latest_news_date >= date('now', '-7 days') 
            OR ura.latest_play_date >= date('now', '-7 days')
            OR uba.latest_book_date >= date('now', '-7 days')
            OR uaa.last_api_call_date >= date('now', '-7 days')
        THEN '활발'
        WHEN una.latest_news_date >= date('now', '-30 days')
            OR ura.latest_play_date >= date('now', '-30 days')
            OR uba.latest_book_date >= date('now', '-30 days')
            OR uaa.last_api_call_date >= date('now', '-30 days')
        THEN '보통'
        ELSE '비활성'
    END AS activity_status

FROM user_activity_score uas
FULL OUTER JOIN user_news_activity una ON uas.user_id = una.user_id
FULL OUTER JOIN user_radio_activity ura ON COALESCE(uas.user_id, una.user_id) = ura.user_id
FULL OUTER JOIN user_books_activity uba ON COALESCE(uas.user_id, una.user_id, ura.user_id) = uba.user_id
FULL OUTER JOIN user_api_activity uaa ON COALESCE(uas.user_id, una.user_id, ura.user_id, uba.user_id) = uaa.user_id
LEFT JOIN api_content_correlation acc ON uas.user_id = acc.user_id

WHERE 
    -- 최소 활동 조건
    (
        COALESCE(una.total_news_count, 0) > 0
        OR COALESCE(ura.total_songs_count, 0) > 0
        OR COALESCE(uba.total_books_count, 0) > 0
        OR COALESCE(uaa.total_api_calls, 0) > 0
    )
    -- 최근 활동 필터
    AND (
        una.latest_news_date >= date('now', '-90 days')
        OR ura.latest_play_date >= date('now', '-90 days')
        OR uba.latest_book_date >= date('now', '-90 days')
        OR uaa.last_api_call_date >= date('now', '-90 days')
    )

GROUP BY 
    uas.user_id, uas.email, uas.name, uas.account_age_days, uas.user_type, uas.total_activity_score,
    una.total_news_count, una.category_count, una.keyword_count,
    una.latest_news_date, una.earliest_news_date, una.avg_importance, una.high_importance_count,
    ura.total_songs_count, ura.unique_artists_count, ura.unique_genres_count,
    ura.total_play_count, ura.latest_play_date, ura.earliest_play_date, ura.avg_play_count_per_song,
    uba.total_books_count, uba.unique_authors_count, uba.unique_categories_count,
    uba.latest_book_date, uba.earliest_book_date,
    uaa.total_api_keys_count, uaa.active_api_keys_count,
    uaa.total_api_calls, uaa.unique_endpoints_count,
    uaa.last_api_call_date, uaa.first_api_call_date, uaa.avg_status_code,
    acc.api_usage_level, acc.content_activity_level

ORDER BY 
    uas.total_activity_score DESC,
    una.latest_news_date DESC NULLS LAST,
    ura.latest_play_date DESC NULLS LAST,
    uba.latest_book_date DESC NULLS LAST,
    uaa.last_api_call_date DESC NULLS LAST

LIMIT 100;

-- ============================================
-- 추가 분석 쿼리 1: 카테고리별 상세 통계
-- ============================================

SELECT 
    cns.category,
    cns.news_count,
    cns.user_count,
    ROUND(cns.avg_importance, 2) AS avg_importance,
    cns.latest_news_date,
    -- 카테고리별 상위 키워드
    (
        SELECT GROUP_CONCAT(DISTINCT n2.keyword, ', ')
        FROM news n2
        WHERE n2.category = cns.category
            AND n2.publishedDate >= date('now', '-3 months')
        GROUP BY n2.category
        ORDER BY COUNT(*) DESC
        LIMIT 5
    ) AS top_keywords
FROM category_news_summary cns
ORDER BY cns.news_count DESC;

-- ============================================
-- 추가 분석 쿼리 2: 아티스트별 상세 통계
-- ============================================

SELECT 
    ars.artist,
    ars.song_count,
    ars.user_count,
    ars.total_play_count,
    ROUND(ars.avg_play_count, 2) AS avg_play_count,
    ars.latest_play_date,
    -- 아티스트별 인기 장르
    (
        SELECT GROUP_CONCAT(DISTINCT rs2.genre, ', ')
        FROM radioSongs rs2
        WHERE rs2.artist = ars.artist
            AND rs2.lastPlayed >= date('now', '-3 months')
        GROUP BY rs2.artist
        ORDER BY COUNT(*) DESC
        LIMIT 3
    ) AS popular_genres
FROM artist_radio_summary ars
ORDER BY ars.total_play_count DESC;

-- ============================================
-- 추가 분석 쿼리 3: 월별 활동 트렌드 분석
-- ============================================

SELECT 
    mas.activity_month,
    mas.activity_type,
    SUM(mas.activity_count) AS total_activity,
    COUNT(DISTINCT mas.user_id) AS active_users,
    AVG(mas.activity_count) AS avg_activity_per_user
FROM monthly_activity_summary mas
GROUP BY mas.activity_month, mas.activity_type
ORDER BY mas.activity_month DESC, mas.activity_type;

-- ============================================
-- 추가 분석 쿼리 4: API 엔드포인트 사용 통계
-- ============================================

SELECT 
    aes.endpoint,
    aes.method,
    aes.total_calls,
    aes.unique_api_keys,
    ROUND(aes.avg_status_code, 2) AS avg_status_code,
    aes.success_count,
    aes.error_count,
    aes.last_call_date,
    -- 성공률 계산
    ROUND(aes.success_count * 100.0 / NULLIF(aes.total_calls, 0), 2) AS success_rate
FROM api_endpoint_summary aes
ORDER BY aes.total_calls DESC;

-- ============================================
-- 추가 분석 쿼리 5: 사용자별 선호 카테고리 Top 3
-- ============================================

SELECT 
    ucp.user_id,
    ucp.email,
    ucp.name,
    GROUP_CONCAT(ucp.category || ' (' || ucp.category_news_count || '건)', ', ') AS top_categories
FROM (
    SELECT 
        ucp2.user_id,
        ucp2.email,
        ucp2.name,
        ucp2.category,
        ucp2.category_news_count,
        ROW_NUMBER() OVER (PARTITION BY ucp2.user_id ORDER BY ucp2.category_news_count DESC) AS rn
    FROM user_category_preference ucp2
) ucp
WHERE ucp.rn <= 3
GROUP BY ucp.user_id, ucp.email, ucp.name
ORDER BY ucp.user_id;

-- ============================================
-- 추가 분석 쿼리 6: 사용자별 선호 아티스트 Top 3
-- ============================================

SELECT 
    uap.user_id,
    uap.email,
    uap.name,
    GROUP_CONCAT(uap.artist || ' (' || uap.total_play_count || '회)', ', ') AS top_artists
FROM (
    SELECT 
        uap2.user_id,
        uap2.email,
        uap2.name,
        uap2.artist,
        uap2.total_play_count,
        ROW_NUMBER() OVER (PARTITION BY uap2.user_id ORDER BY uap2.total_play_count DESC) AS rn
    FROM user_artist_preference uap2
) uap
WHERE uap.rn <= 3
GROUP BY uap.user_id, uap.email, uap.name
ORDER BY uap.user_id;

-- ============================================
-- 추가 분석 쿼리 7: API 사용과 콘텐츠 활동 상관관계 분석
-- ============================================

SELECT 
    acc.api_usage_level,
    acc.content_activity_level,
    COUNT(*) AS user_count,
    AVG(acc.total_activity_score) AS avg_activity_score,
    AVG(acc.total_api_calls) AS avg_api_calls,
    AVG(acc.total_news_count + acc.total_songs_count + acc.total_books_count) AS avg_content_count
FROM api_content_correlation acc
GROUP BY acc.api_usage_level, acc.content_activity_level
ORDER BY acc.api_usage_level, acc.content_activity_level;

-- ============================================
-- 추가 분석 쿼리 8: 시간대별 활동 패턴 분석
-- ============================================

SELECT 
    uas.user_id,
    uas.email,
    uas.name,
    -- 시간대별 뉴스 수집 패턴
    COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS news_morning,
    COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS news_afternoon,
    COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS news_evening,
    -- 시간대별 라디오 청취 패턴
    COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS radio_morning,
    COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS radio_afternoon,
    COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS radio_evening,
    -- 시간대별 도서 수집 패턴
    COUNT(CASE WHEN CAST(strftime('%H', b.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS books_morning,
    COUNT(CASE WHEN CAST(strftime('%H', b.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS books_afternoon,
    COUNT(CASE WHEN CAST(strftime('%H', b.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS books_evening
FROM user_activity_score uas
LEFT JOIN news n ON uas.user_id = n.userId AND n.collectedAt >= date('now', '-3 months')
LEFT JOIN radioSongs rs ON uas.user_id = rs.userId AND rs.lastPlayed >= date('now', '-3 months')
LEFT JOIN books b ON uas.user_id = b.userId AND b.collectedAt >= date('now', '-3 months')
GROUP BY uas.user_id, uas.email, uas.name
HAVING COUNT(n.id) > 0 OR COUNT(rs.id) > 0 OR COUNT(b.id) > 0
ORDER BY uas.user_id;

-- ============================================
-- 추가 분석 쿼리 9: 카테고리-아티스트-저자 교차 분석
-- ============================================

SELECT 
    cns.category AS news_category,
    ars.artist AS radio_artist,
    abs.authors AS book_author,
    COUNT(DISTINCT uas.user_id) AS common_users_count,
    AVG(uas.total_activity_score) AS avg_activity_score
FROM category_news_summary cns
CROSS JOIN artist_radio_summary ars
CROSS JOIN author_books_summary abs
INNER JOIN user_category_preference ucp ON cns.category = ucp.category
INNER JOIN user_artist_preference uap ON ars.artist = uap.artist AND ucp.user_id = uap.user_id
INNER JOIN user_author_preference uaup ON abs.authors = uaup.authors AND uap.user_id = uaup.user_id
INNER JOIN user_activity_score uas ON uaup.user_id = uas.user_id
GROUP BY cns.category, ars.artist, abs.authors
HAVING COUNT(DISTINCT uas.user_id) >= 1
ORDER BY common_users_count DESC, avg_activity_score DESC
LIMIT 50;

-- ============================================
-- 추가 분석 쿼리 10: API 키별 상세 사용 분석
-- ============================================

SELECT 
    aks.api_key_id,
    aks.userId,
    aks.api_key_name,
    aks.isActive,
    aks.total_usage_count,
    aks.unique_endpoints,
    aks.last_used_date,
    aks.first_used_date,
    uas.email,
    uas.name,
    uas.total_activity_score,
    -- API 키 사용 기간 계산
    CAST((julianday(aks.last_used_date) - julianday(aks.first_used_date)) AS INTEGER) AS usage_days,
    -- 일평균 사용량 계산
    ROUND(aks.total_usage_count * 1.0 / NULLIF(CAST((julianday('now') - julianday(aks.first_used_date)) AS INTEGER), 0), 2) AS daily_avg_usage
FROM api_key_summary aks
LEFT JOIN user_activity_score uas ON aks.userId = uas.user_id
WHERE aks.total_usage_count > 0
ORDER BY aks.total_usage_count DESC;

-- ============================================
-- 추가 분석 쿼리 11: 사용자 활동 성장 추세 분석
-- ============================================

SELECT 
    mas.user_id,
    mas.activity_month,
    mas.activity_type,
    mas.activity_count,
    -- 전월 대비 성장률 계산
    LAG(mas.activity_count) OVER (PARTITION BY mas.user_id, mas.activity_type ORDER BY mas.activity_month) AS previous_month_count,
    CASE 
        WHEN LAG(mas.activity_count) OVER (PARTITION BY mas.user_id, mas.activity_type ORDER BY mas.activity_month) > 0
        THEN ROUND(
            (mas.activity_count - LAG(mas.activity_count) OVER (PARTITION BY mas.user_id, mas.activity_type ORDER BY mas.activity_month)) * 100.0 / 
            LAG(mas.activity_count) OVER (PARTITION BY mas.user_id, mas.activity_type ORDER BY mas.activity_month), 
            2
        )
        ELSE NULL
    END AS month_over_month_growth_rate,
    -- 이동 평균 (3개월)
    ROUND(
        AVG(mas.activity_count) OVER (
            PARTITION BY mas.user_id, mas.activity_type 
            ORDER BY mas.activity_month 
            ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
        ), 
        2
    ) AS moving_average_3months
FROM monthly_activity_summary mas
ORDER BY mas.user_id, mas.activity_month DESC, mas.activity_type;

-- ============================================
-- 추가 분석 쿼리 12: 사용자별 콘텐츠 다양성 점수
-- ============================================

SELECT 
    uas.user_id,
    uas.email,
    uas.name,
    -- 뉴스 다양성 점수
    COALESCE(una.category_count, 0) * 10 + COALESCE(una.keyword_count, 0) * 5 AS news_diversity_score,
    -- 라디오 다양성 점수
    COALESCE(ura.unique_artists_count, 0) * 10 + COALESCE(ura.unique_genres_count, 0) * 5 AS radio_diversity_score,
    -- 도서 다양성 점수
    COALESCE(uba.unique_authors_count, 0) * 10 + COALESCE(uba.unique_categories_count, 0) * 5 AS books_diversity_score,
    -- 종합 다양성 점수
    (
        COALESCE(una.category_count, 0) * 10 + COALESCE(una.keyword_count, 0) * 5 +
        COALESCE(ura.unique_artists_count, 0) * 10 + COALESCE(ura.unique_genres_count, 0) * 5 +
        COALESCE(uba.unique_authors_count, 0) * 10 + COALESCE(uba.unique_categories_count, 0) * 5
    ) AS total_diversity_score
FROM user_activity_score uas
LEFT JOIN user_news_activity una ON uas.user_id = una.user_id
LEFT JOIN user_radio_activity ura ON uas.user_id = ura.user_id
LEFT JOIN user_books_activity uba ON uas.user_id = uba.user_id
WHERE (
    COALESCE(una.category_count, 0) > 0 OR
    COALESCE(ura.unique_artists_count, 0) > 0 OR
    COALESCE(uba.unique_authors_count, 0) > 0
)
ORDER BY total_diversity_score DESC;

-- ============================================
-- 추가 분석 쿼리 13: 엔드포인트별 사용자 분포
-- ============================================

SELECT 
    aes.endpoint,
    aes.method,
    aes.total_calls,
    COUNT(DISTINCT aks.userId) AS unique_users,
    AVG(aks.total_usage_count) AS avg_api_key_usage,
    -- 사용자당 평균 호출 수
    ROUND(aes.total_calls * 1.0 / NULLIF(COUNT(DISTINCT aks.userId), 0), 2) AS avg_calls_per_user
FROM api_endpoint_summary aes
INNER JOIN apiKeyUsage aku ON aes.endpoint = aku.endpoint AND aes.method = aku.method
INNER JOIN apiKeys ak ON aku.apiKeyId = ak.id
INNER JOIN api_key_summary aks ON ak.id = aks.api_key_id
GROUP BY aes.endpoint, aes.method, aes.total_calls
ORDER BY aes.total_calls DESC;

-- ============================================
-- 추가 분석 쿼리 14: 사용자 활동 패턴 클러스터링
-- ============================================

SELECT 
    uas.user_id,
    uas.email,
    uas.name,
    uas.user_type,
    -- 활동 패턴 분류
    CASE 
        WHEN COALESCE(una.total_news_count, 0) > COALESCE(ura.total_songs_count, 0) 
            AND COALESCE(una.total_news_count, 0) > COALESCE(uba.total_books_count, 0)
        THEN '뉴스 중심형'
        WHEN COALESCE(ura.total_songs_count, 0) > COALESCE(una.total_news_count, 0) 
            AND COALESCE(ura.total_songs_count, 0) > COALESCE(uba.total_books_count, 0)
        THEN '음악 중심형'
        WHEN COALESCE(uba.total_books_count, 0) > COALESCE(una.total_news_count, 0) 
            AND COALESCE(uba.total_books_count, 0) > COALESCE(ura.total_songs_count, 0)
        THEN '독서 중심형'
        WHEN COALESCE(una.total_news_count, 0) > 0 
            AND COALESCE(ura.total_songs_count, 0) > 0 
            AND COALESCE(uba.total_books_count, 0) > 0
        THEN '균형형'
        ELSE '기타'
    END AS activity_pattern,
    uas.total_activity_score
FROM user_activity_score uas
LEFT JOIN user_news_activity una ON uas.user_id = una.user_id
LEFT JOIN user_radio_activity ura ON uas.user_id = ura.user_id
LEFT JOIN user_books_activity uba ON uas.user_id = uba.user_id
ORDER BY uas.total_activity_score DESC;

-- ============================================
-- 추가 분석 쿼리 15: 최종 통합 대시보드 데이터
-- ============================================

SELECT 
    '총 사용자 수' AS metric_name,
    COUNT(DISTINCT uas.user_id) AS metric_value,
    NULL AS metric_unit
FROM user_activity_score uas

UNION ALL

SELECT 
    '활성 사용자 수 (최근 30일)' AS metric_name,
    COUNT(DISTINCT uas.user_id) AS metric_value,
    NULL AS metric_unit
FROM user_activity_score uas
WHERE uas.total_activity_score > 0

UNION ALL

SELECT 
    '총 뉴스 수집 건수' AS metric_name,
    SUM(COALESCE(una.total_news_count, 0)) AS metric_value,
    '건' AS metric_unit
FROM user_activity_score uas
LEFT JOIN user_news_activity una ON uas.user_id = una.user_id

UNION ALL

SELECT 
    '총 라디오 재생 건수' AS metric_name,
    SUM(COALESCE(ura.total_play_count, 0)) AS metric_value,
    '회' AS metric_unit
FROM user_activity_score uas
LEFT JOIN user_radio_activity ura ON uas.user_id = ura.user_id

UNION ALL

SELECT 
    '총 도서 수집 건수' AS metric_name,
    SUM(COALESCE(uba.total_books_count, 0)) AS metric_value,
    '권' AS metric_unit
FROM user_activity_score uas
LEFT JOIN user_books_activity uba ON uas.user_id = uba.user_id

UNION ALL

SELECT 
    '총 API 호출 건수' AS metric_name,
    SUM(COALESCE(uaa.total_api_calls, 0)) AS metric_value,
    '회' AS metric_unit
FROM user_activity_score uas
LEFT JOIN user_api_activity uaa ON uas.user_id = uaa.user_id

UNION ALL

SELECT 
    '평균 활동 점수' AS metric_name,
    ROUND(AVG(uas.total_activity_score), 2) AS metric_value,
    '점' AS metric_unit
FROM user_activity_score uas;

-- ============================================
-- 쿼리 종료
-- ============================================


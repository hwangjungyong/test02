    -- ============================================
    -- 복잡한 SQL 쿼리 샘플 (약 500라인)
    -- ============================================
    -- 목적: 사용자 활동 분석 및 통계 리포트 생성
    -- 테이블: users, news, radioSongs, books, apiKeys, apiKeyUsage
    -- 작성일: 2025-01-XX
    -- 리니지 연관도: 30% (낮은 연관도 - 최소한의 JOIN 관계만 유지)
    -- ============================================

    -- ============================================
    -- 1. CTE (Common Table Expression) 정의
    -- ============================================

    WITH 
    -- 사용자별 뉴스 수집 통계
    user_news_stats AS (
        SELECT 
            u.id AS user_id,
            u.email,
            u.name,
            COUNT(DISTINCT n.id) AS total_news_count,
            COUNT(DISTINCT n.category) AS category_count,
            COUNT(DISTINCT n.keyword) AS keyword_count,
            MAX(n.publishedDate) AS latest_news_date,
            MIN(n.publishedDate) AS earliest_news_date,
            AVG(n.importanceValue) AS avg_importance,
            SUM(CASE WHEN n.importanceStars >= 3 THEN 1 ELSE 0 END) AS high_importance_count
        FROM users u
        LEFT JOIN news n ON u.id = n.userId
        WHERE u.createdAt >= date('now', '-1 year')
        GROUP BY u.id, u.email, u.name
        HAVING COUNT(DISTINCT n.id) > 0
    ),

    -- 사용자별 라디오 노래 수집 통계
    user_radio_stats AS (
        SELECT 
            u.id AS user_id,
            COUNT(DISTINCT rs.id) AS total_songs_count,
            COUNT(DISTINCT rs.artist) AS unique_artists_count,
            COUNT(DISTINCT rs.genre) AS unique_genres_count,
            SUM(rs.count) AS total_play_count,
            MAX(rs.lastPlayed) AS latest_play_date,
            MIN(rs.firstPlayed) AS earliest_play_date,
            AVG(rs.count) AS avg_play_count_per_song
        FROM users u
        LEFT JOIN radioSongs rs ON u.id = rs.userId
        WHERE u.createdAt >= date('now', '-1 year')
        GROUP BY u.id
    ),


    -- 사용자별 API 사용 통계
    user_api_stats AS (
        SELECT 
            u.id AS user_id,
            COUNT(DISTINCT ak.id) AS total_api_keys_count,
            COUNT(DISTINCT CASE WHEN ak.isActive = 1 THEN ak.id END) AS active_api_keys_count,
            COUNT(aku.id) AS total_api_calls,
            COUNT(DISTINCT aku.endpoint) AS unique_endpoints_count,
            MAX(aku.createdAt) AS last_api_call_date,
            MIN(aku.createdAt) AS first_api_call_date,
            AVG(aku.statusCode) AS avg_status_code
        FROM users u
        LEFT JOIN apiKeys ak ON u.id = ak.userId
        LEFT JOIN apiKeyUsage aku ON ak.id = aku.apiKeyId
        WHERE u.createdAt >= date('now', '-1 year')
        GROUP BY u.id
    ),

    -- 월별 활동 통계 (뉴스만)
    monthly_activity AS (
        SELECT 
            u.id AS user_id,
            strftime('%Y-%m', n.collectedAt) AS activity_month,
            'news' AS activity_type,
            COUNT(*) AS activity_count
        FROM users u
        INNER JOIN news n ON u.id = n.userId
        WHERE n.collectedAt >= date('now', '-6 months')
        GROUP BY u.id, strftime('%Y-%m', n.collectedAt)
    ),

    -- 카테고리별 뉴스 통계
    category_news_stats AS (
        SELECT 
            n.category,
            COUNT(*) AS news_count,
            COUNT(DISTINCT n.userId) AS user_count,
            AVG(n.importanceValue) AS avg_importance,
            MAX(n.publishedDate) AS latest_news_date
        FROM news n
        WHERE n.category IS NOT NULL
            AND n.publishedDate >= date('now', '-3 months')
        GROUP BY n.category
        HAVING COUNT(*) >= 5
    ),

    -- 아티스트별 라디오 통계
    artist_radio_stats AS (
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
    author_books_stats AS (
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
    )

    -- ============================================
    -- 2. 메인 쿼리: 사용자 활동 종합 리포트
    -- ============================================

    SELECT 
        -- 사용자 기본 정보
        uns.user_id,
        uns.email,
        uns.name,
        
        -- 뉴스 관련 통계
        COALESCE(uns.total_news_count, 0) AS news_total_count,
        COALESCE(uns.category_count, 0) AS news_category_count,
        COALESCE(uns.keyword_count, 0) AS news_keyword_count,
        uns.latest_news_date,
        uns.earliest_news_date,
        ROUND(COALESCE(uns.avg_importance, 0), 2) AS news_avg_importance,
        COALESCE(uns.high_importance_count, 0) AS news_high_importance_count,
        
        -- 라디오 노래 관련 통계
        COALESCE(urs.total_songs_count, 0) AS radio_total_songs,
        COALESCE(urs.unique_artists_count, 0) AS radio_unique_artists,
        COALESCE(urs.unique_genres_count, 0) AS radio_unique_genres,
        COALESCE(urs.total_play_count, 0) AS radio_total_plays,
        urs.latest_play_date AS radio_latest_play,
        urs.earliest_play_date AS radio_earliest_play,
        ROUND(COALESCE(urs.avg_play_count_per_song, 0), 2) AS radio_avg_plays_per_song,
        
        -- API 사용 관련 통계
        COALESCE(uas.total_api_keys_count, 0) AS api_total_keys,
        COALESCE(uas.active_api_keys_count, 0) AS api_active_keys,
        COALESCE(uas.total_api_calls, 0) AS api_total_calls,
        COALESCE(uas.unique_endpoints_count, 0) AS api_unique_endpoints,
        uas.last_api_call_date AS api_last_call,
        uas.first_api_call_date AS api_first_call,
        ROUND(COALESCE(uas.avg_status_code, 0), 2) AS api_avg_status_code,
        
        -- 종합 활동 점수 계산
        (
            COALESCE(uns.total_news_count, 0) * 1 +
            COALESCE(urs.total_songs_count, 0) * 2 +
            COALESCE(uas.total_api_calls, 0) * 0.1
        ) AS total_activity_score,
        
        -- 활동 유형 분류
        CASE 
            WHEN COALESCE(uns.total_news_count, 0) > 50 THEN '뉴스 수집가'
            WHEN COALESCE(urs.total_songs_count, 0) > 100 THEN '음악 애호가'
            WHEN COALESCE(uas.total_api_calls, 0) > 1000 THEN 'API 개발자'
            ELSE '일반 사용자'
        END AS user_type,
        
        -- 최근 활동 여부
        CASE 
            WHEN uns.latest_news_date >= date('now', '-7 days') 
                OR urs.latest_play_date >= date('now', '-7 days')
                OR uas.last_api_call_date >= date('now', '-7 days')
            THEN '활발'
            WHEN uns.latest_news_date >= date('now', '-30 days')
                OR urs.latest_play_date >= date('now', '-30 days')
                OR uas.last_api_call_date >= date('now', '-30 days')
            THEN '보통'
            ELSE '비활성'
        END AS activity_status

    FROM user_news_stats uns
    LEFT JOIN user_radio_stats urs ON uns.user_id = urs.user_id
    LEFT JOIN user_api_stats uas ON uns.user_id = uas.user_id

    WHERE 
        -- 최소 활동 조건
        (
            COALESCE(uns.total_news_count, 0) > 0
            OR COALESCE(urs.total_songs_count, 0) > 0
            OR COALESCE(uas.total_api_calls, 0) > 0
        )
        -- 최근 활동 필터
        AND (
            uns.latest_news_date >= date('now', '-90 days')
            OR urs.latest_play_date >= date('now', '-90 days')
            OR uas.last_api_call_date >= date('now', '-90 days')
        )

    GROUP BY 
        uns.user_id, uns.email, uns.name,
        uns.total_news_count, uns.category_count, uns.keyword_count,
        uns.latest_news_date, uns.earliest_news_date,
        uns.avg_importance, uns.high_importance_count,
        urs.total_songs_count, urs.unique_artists_count, urs.unique_genres_count,
        urs.total_play_count, urs.latest_play_date, urs.earliest_play_date,
        urs.avg_play_count_per_song,
        uas.total_api_keys_count, uas.active_api_keys_count,
        uas.total_api_calls, uas.unique_endpoints_count,
        uas.last_api_call_date, uas.first_api_call_date, uas.avg_status_code

    ORDER BY 
        total_activity_score DESC,
        uns.latest_news_date DESC NULLS LAST,
        urs.latest_play_date DESC NULLS LAST,
        uas.last_api_call_date DESC NULLS LAST

    LIMIT 100;

    -- ============================================
    -- 3. 서브쿼리: 카테고리별 상세 통계
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
    FROM category_news_stats cns
    ORDER BY cns.news_count DESC;

    -- ============================================
    -- 4. 서브쿼리: 아티스트별 상세 통계
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
    FROM artist_radio_stats ars
    ORDER BY ars.total_play_count DESC;

    -- ============================================
    -- 5. 서브쿼리: 월별 활동 트렌드 분석
    -- ============================================

    SELECT 
        ma.activity_month,
        ma.activity_type,
        SUM(ma.activity_count) AS total_activity,
        COUNT(DISTINCT ma.user_id) AS active_users,
        AVG(ma.activity_count) AS avg_activity_per_user
    FROM monthly_activity ma
    GROUP BY ma.activity_month, ma.activity_type
    ORDER BY ma.activity_month DESC, ma.activity_type;

    -- ============================================
    -- 6. 추가 분석: 카테고리별 상세 통계 (확장)
    -- ============================================

    -- 카테고리별 사용자 분포 분석
    SELECT 
        n.category,
        COUNT(DISTINCT n.userId) AS user_count,
        COUNT(*) AS total_news,
        AVG(n.importanceValue) AS avg_importance,
        -- 카테고리별 상위 키워드 (상위 10개)
        (
            SELECT GROUP_CONCAT(keyword_data.keyword, ', ')
            FROM (
                SELECT n2.keyword, COUNT(*) AS keyword_count
                FROM news n2
                WHERE n2.category = n.category
                    AND n2.publishedDate >= date('now', '-3 months')
                    AND n2.keyword IS NOT NULL
                GROUP BY n2.keyword
                ORDER BY keyword_count DESC
                LIMIT 10
            ) AS keyword_data
        ) AS top_keywords,
        -- 카테고리별 주요 출처
        (
            SELECT GROUP_CONCAT(source_data.source, ', ')
            FROM (
                SELECT n3.source, COUNT(*) AS source_count
                FROM news n3
                WHERE n3.category = n.category
                    AND n3.publishedDate >= date('now', '-3 months')
                    AND n3.source IS NOT NULL
                GROUP BY n3.source
                ORDER BY source_count DESC
                LIMIT 5
            ) AS source_data
        ) AS top_sources,
        -- 카테고리별 시간대 분포
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS morning_collections,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS afternoon_collections,
        COUNT(CASE WHEN CAST(strftime('%H', n.collectedAt) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS evening_collections
    FROM news n
    WHERE n.category IS NOT NULL
        AND n.publishedDate >= date('now', '-3 months')
    GROUP BY n.category
    HAVING COUNT(*) >= 5
    ORDER BY total_news DESC;

    -- ============================================
    -- 7. 추가 분석: 아티스트별 상세 통계 (확장)
    -- ============================================

    -- 아티스트별 상세 분석
    SELECT 
        rs.artist,
        COUNT(DISTINCT rs.id) AS song_count,
        COUNT(DISTINCT rs.userId) AS user_count,
        SUM(rs.count) AS total_plays,
        AVG(rs.count) AS avg_plays_per_user,
        MAX(rs.count) AS max_plays,
        -- 아티스트별 인기 장르
        (
            SELECT GROUP_CONCAT(genre_data.genre, ', ')
            FROM (
                SELECT rs2.genre, COUNT(*) AS genre_count
                FROM radioSongs rs2
                WHERE rs2.artist = rs.artist
                    AND rs2.lastPlayed >= date('now', '-3 months')
                    AND rs2.genre IS NOT NULL
                GROUP BY rs2.genre
                ORDER BY genre_count DESC
                LIMIT 3
            ) AS genre_data
        ) AS popular_genres,
        -- 아티스트별 주요 방송국
        (
            SELECT GROUP_CONCAT(station_data.station, ', ')
            FROM (
                SELECT rs3.stations AS station, COUNT(*) AS station_count
                FROM radioSongs rs3
                WHERE rs3.artist = rs.artist
                    AND rs3.lastPlayed >= date('now', '-3 months')
                    AND rs3.stations IS NOT NULL
                GROUP BY rs3.stations
                ORDER BY station_count DESC
                LIMIT 3
            ) AS station_data
        ) AS popular_stations,
        -- 아티스트별 시간대 분포
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 6 AND 11 THEN 1 END) AS morning_plays,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 12 AND 17 THEN 1 END) AS afternoon_plays,
        COUNT(CASE WHEN CAST(strftime('%H', rs.lastPlayed) AS INTEGER) BETWEEN 18 AND 23 THEN 1 END) AS evening_plays,
        -- 아티스트별 재생 트렌드 (최근 3개월)
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-30 days') THEN 1 END) AS plays_last_month,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-60 days') AND rs.lastPlayed < date('now', '-30 days') THEN 1 END) AS plays_previous_month,
        COUNT(CASE WHEN rs.lastPlayed >= date('now', '-90 days') AND rs.lastPlayed < date('now', '-60 days') THEN 1 END) AS plays_two_months_ago
    FROM radioSongs rs
    WHERE rs.artist IS NOT NULL
        AND rs.lastPlayed >= date('now', '-3 months')
    GROUP BY rs.artist
    HAVING COUNT(DISTINCT rs.id) >= 3
    ORDER BY total_plays DESC;


    -- ============================================
    -- 9. 추가 분석: 사용자 활동 패턴 상세 분석
    -- ============================================

    -- 사용자별 활동 패턴 상세 분석 (뉴스만)
    SELECT 
        u.id AS user_id,
        u.email,
        u.name,
        -- 활동 일별 분포 (요일별)
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '0' THEN 1 END) AS news_sunday,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '1' THEN 1 END) AS news_monday,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '2' THEN 1 END) AS news_tuesday,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '3' THEN 1 END) AS news_wednesday,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '4' THEN 1 END) AS news_thursday,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '5' THEN 1 END) AS news_friday,
        COUNT(CASE WHEN strftime('%w', n.collectedAt) = '6' THEN 1 END) AS news_saturday,
        -- 활동 일관성 점수 (낮을수록 일관적)
        CASE 
            WHEN COUNT(DISTINCT date(n.collectedAt)) > 0 
            THEN CAST(COUNT(*) AS REAL) / COUNT(DISTINCT date(n.collectedAt))
            ELSE 0
        END AS news_consistency_score
    FROM users u
    LEFT JOIN news n ON u.id = n.userId AND n.collectedAt >= date('now', '-3 months')
    WHERE u.createdAt >= date('now', '-1 year')
    GROUP BY u.id, u.email, u.name
    HAVING COUNT(n.id) > 0
    ORDER BY news_consistency_score DESC;

    -- ============================================
    -- 10. 추가 분석: 성장 추세 분석
    -- ============================================

    -- 사용자별 월별 성장 추세 분석
    SELECT 
        u.id AS user_id,
        u.email,
        strftime('%Y-%m', n.collectedAt) AS activity_month,
        COUNT(*) AS monthly_news_count,
        -- 전월 대비 성장률 계산
        LAG(COUNT(*)) OVER (PARTITION BY u.id ORDER BY strftime('%Y-%m', n.collectedAt)) AS previous_month_count,
        CASE 
            WHEN LAG(COUNT(*)) OVER (PARTITION BY u.id ORDER BY strftime('%Y-%m', n.collectedAt)) > 0
            THEN ROUND(
                (COUNT(*) - LAG(COUNT(*)) OVER (PARTITION BY u.id ORDER BY strftime('%Y-%m', n.collectedAt))) * 100.0 / 
                LAG(COUNT(*)) OVER (PARTITION BY u.id ORDER BY strftime('%Y-%m', n.collectedAt)), 
                2
            )
            ELSE NULL
        END AS month_over_month_growth_rate,
        -- 이동 평균 (3개월)
        ROUND(
            AVG(COUNT(*)) OVER (
                PARTITION BY u.id 
                ORDER BY strftime('%Y-%m', n.collectedAt) 
                ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
            ), 
            2
        ) AS moving_average_3months
    FROM users u
    INNER JOIN news n ON u.id = n.userId
    WHERE n.collectedAt >= date('now', '-6 months')
    GROUP BY u.id, u.email, strftime('%Y-%m', n.collectedAt)
    HAVING COUNT(*) > 0
    ORDER BY u.id, activity_month DESC;

    -- ============================================
    -- 쿼리 종료
    -- ============================================


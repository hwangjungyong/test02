-- 테스트용 SQL 쿼리
-- 간단한 SELECT 쿼리 예시

SELECT 
    u.id,
    u.name,
    u.email,
    o.total,
    o.created_at
FROM users u
INNER JOIN orders o ON u.id = o.user_id
WHERE u.status = 'active'
    AND o.total > 1000
GROUP BY u.id, u.name, u.email, o.total, o.created_at
HAVING COUNT(o.id) > 5
ORDER BY o.total DESC
LIMIT 10;


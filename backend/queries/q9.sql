-- QUERY 9: Churn Analysis - Customers with No Purchase in 60 Days
-- Business question: Which customers are going silent and need re-engagement?
-- SQL concepts: DATEDIFF(), HAVING clause filter, @as_of reference date.
-- FIX (v2): Cancelled orders excluded from purchase count; @as_of replaces CURDATE().
SELECT u.user_id, u.username, u.email, u.city, u.region, u.user_type,
       MAX(o.order_date)                        AS last_purchase_date,
       DATEDIFF(@as_of, MAX(o.order_date))      AS days_since_last_purchase,
       COUNT(o.order_id)                        AS lifetime_orders,
       ROUND(SUM(o.total_amount),2)             AS lifetime_value,
       CASE WHEN DATEDIFF(@as_of, MAX(o.order_date)) BETWEEN 60 AND 90   THEN 'Early Churn Risk'
            WHEN DATEDIFF(@as_of, MAX(o.order_date)) BETWEEN 91 AND 180  THEN 'Churning'
            ELSE 'Churned' END AS churn_status
FROM users u JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status <> 'Cancelled'
GROUP BY u.user_id, u.username, u.email, u.city, u.region, u.user_type
HAVING days_since_last_purchase >= 60
ORDER BY days_since_last_purchase DESC;

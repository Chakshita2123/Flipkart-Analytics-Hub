-- QUERY 1: Top 10 Customers by Total Spending
-- Business question: Who are our highest-value customers by delivered spend?
-- SQL concepts: GROUP BY, ORDER BY, aggregate functions.
SELECT
    u.user_id, u.username, u.city, u.region, u.user_type,
    COUNT(o.order_id)            AS total_orders,
    ROUND(SUM(o.total_amount),2) AS total_spending,
    ROUND(AVG(o.total_amount),2) AS avg_order_value,
    MAX(o.order_date)            AS last_order_date
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.user_id, u.username, u.city, u.region, u.user_type
ORDER BY total_spending DESC LIMIT 10;

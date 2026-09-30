-- QUERY 4: Regional Sales Performance
-- Business question: Which regions generate the most revenue from active orders?
-- SQL concepts: DISTINCT counting, window SUM OVER() for share percentage.
SELECT
    o.region,
    COUNT(DISTINCT o.order_id)                                               AS total_orders,
    COUNT(DISTINCT o.user_id)                                                AS unique_customers,
    ROUND(SUM(o.total_amount),2)                                             AS total_revenue,
    ROUND(AVG(o.total_amount),2)                                             AS avg_order_value,
    ROUND(SUM(o.total_amount)*100.0/SUM(SUM(o.total_amount)) OVER (),2)     AS revenue_share_pct
FROM orders o
WHERE o.order_status NOT IN ('Cancelled','Returned')
GROUP BY o.region ORDER BY total_revenue DESC;

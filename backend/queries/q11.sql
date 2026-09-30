-- QUERY 11: Festival Season Sales Patterns
-- Business question: Which months show festival-driven volume and revenue spikes?
-- SQL concepts: DATE_FORMAT(), CASE WHEN for festival tagging by exact YYYY-MM.
-- Data covers Oct 2025 - Sep 2026 with actual volume spikes in festival months.
WITH monthly_sales AS (
    SELECT DATE_FORMAT(o.order_date,'%Y-%m') AS sale_month,
           MONTHNAME(o.order_date)           AS month_name,
           COUNT(o.order_id)                 AS total_orders,
           ROUND(SUM(o.total_amount),2)      AS total_revenue,
           COUNT(DISTINCT o.user_id)         AS active_customers,
           ROUND(AVG(o.total_amount),2)      AS avg_order_value
    FROM orders o
    WHERE o.order_status NOT IN ('Cancelled','Returned')
    GROUP BY DATE_FORMAT(o.order_date,'%Y-%m'), MONTHNAME(o.order_date)
)
SELECT sale_month, month_name, total_orders, total_revenue, active_customers, avg_order_value,
       CASE sale_month
           WHEN '2025-10' THEN 'Navratri / Big Billion Days'
           WHEN '2025-11' THEN 'Diwali / Dhanteras'
           WHEN '2025-12' THEN 'End of Season Sale'
           WHEN '2026-01' THEN 'Republic Day Sale'
           WHEN '2026-02' THEN 'Valentine Sale'
           WHEN '2026-03' THEN 'Holi Sale'
           WHEN '2026-08' THEN 'Independence Day Sale'
           WHEN '2026-09' THEN 'Pre-Festive Season'
           ELSE 'Regular Month'
       END AS festival_tag
FROM monthly_sales
ORDER BY sale_month;

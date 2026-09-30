-- QUERY 14: Time-to-First-Purchase and Customer Value Analysis
-- Business question: How quickly do users convert after sign-up? What is their CLV?
-- SQL concepts: Chained CTEs, clean MIN() aggregation (one row per user, no fan-out).
-- FIX (v2): Renamed from "Customer Acquisition Cost Analysis" (no cost data in schema).
--           Rewrote first_orders CTE using simple MIN() per user_id to eliminate
--           the GROUP BY order_date/total_amount fan-out that double-counted CLV.
WITH first_orders_clean AS (
    -- Exactly one row per user: earliest delivered order date and its value.
    SELECT user_id,
           MIN(order_date)   AS first_order_date,
           MIN(total_amount) AS first_order_value
    FROM orders
    WHERE order_status = 'Delivered'
    GROUP BY user_id
),
customer_summary AS (
    SELECT u.user_id, u.username, u.user_type, u.signup_date,
           f.first_order_date, f.first_order_value,
           DATEDIFF(f.first_order_date, u.signup_date) AS days_to_first_purchase,
           COUNT(o.order_id)            AS total_orders,
           ROUND(SUM(o.total_amount),2) AS total_clv
    FROM users u
    JOIN first_orders_clean f ON u.user_id = f.user_id
    JOIN orders o             ON u.user_id = o.user_id
    WHERE o.order_status = 'Delivered'
    GROUP BY u.user_id, u.username, u.user_type, u.signup_date,
             f.first_order_date, f.first_order_value
)
SELECT user_id, username, user_type, signup_date, first_order_date,
       days_to_first_purchase, first_order_value, total_orders, total_clv,
       ROUND(total_clv/NULLIF(total_orders,0),2) AS avg_order_value,
       CASE WHEN days_to_first_purchase <= 7  THEN 'Instant Converter'
            WHEN days_to_first_purchase <= 30 THEN 'Quick Converter'
            WHEN days_to_first_purchase <= 90 THEN 'Slow Converter'
            ELSE 'Long-term Nurture' END AS acquisition_type
FROM customer_summary ORDER BY total_clv DESC;

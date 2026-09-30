-- QUERY 8: Monthly Revenue Trends
-- Business question: How does revenue grow month-on-month?
-- SQL concepts: LAG() for MoM growth; cumulative SUM OVER UNBOUNDED PRECEDING.
WITH monthly AS (
    SELECT DATE_FORMAT(order_date,'%Y-%m') AS order_month,
           COUNT(order_id)                 AS orders_placed,
           ROUND(SUM(total_amount),2)      AS monthly_revenue,
           COUNT(DISTINCT user_id)         AS unique_customers
    FROM orders WHERE order_status NOT IN ('Cancelled','Returned')
    GROUP BY DATE_FORMAT(order_date,'%Y-%m')
)
SELECT order_month, orders_placed, monthly_revenue, unique_customers,
       LAG(monthly_revenue) OVER (ORDER BY order_month) AS prev_month_revenue,
       ROUND((monthly_revenue - LAG(monthly_revenue) OVER (ORDER BY order_month))*100.0
             /NULLIF(LAG(monthly_revenue) OVER (ORDER BY order_month),0),2) AS mom_growth_pct,
       ROUND(SUM(monthly_revenue) OVER (ORDER BY order_month ROWS UNBOUNDED PRECEDING),2) AS cumulative_revenue
FROM monthly ORDER BY order_month;

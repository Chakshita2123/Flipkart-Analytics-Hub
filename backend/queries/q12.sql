-- QUERY 12: Payment Method Distribution by Region
-- Business question: Does payment preference differ across North/South/East/West?
-- SQL concepts: PARTITION BY region for within-group percentage.
SELECT region, payment_method, COUNT(*) AS order_count,
       ROUND(SUM(total_amount),2) AS revenue,
       ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (PARTITION BY region),2) AS pct_within_region
FROM orders GROUP BY region, payment_method ORDER BY region, order_count DESC;

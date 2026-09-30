-- QUERY 3: Payment Method Preferences (with Percentages)
-- Business question: How is revenue distributed across payment methods?
-- SQL concepts: SUM() OVER() for window-level percentage calculation.
-- NOTE: Actual COD share in this dataset is ~60%; see output for exact figures.
SELECT
    payment_method,
    COUNT(*)                                                              AS order_count,
    ROUND(SUM(total_amount),2)                                            AS total_revenue,
    ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (),2)                         AS order_pct,
    ROUND(SUM(total_amount)*100.0/SUM(SUM(total_amount)) OVER (),2)       AS revenue_pct,
    ROUND(AVG(total_amount),2)                                            AS avg_order_value
FROM orders GROUP BY payment_method ORDER BY order_count DESC;

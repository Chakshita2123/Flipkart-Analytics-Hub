-- QUERY 10: Category Performance Metrics
-- Business question: How do categories compare on revenue, volume, and returns?
-- SQL concepts: CTE pre-aggregation to prevent returns fan-out, multi-table JOINs.
-- FIX (v2): returns pre-aggregated in CTE.
WITH cat_returns AS (
    SELECT oi.order_id, oi.product_id, COUNT(*) AS ret_count
    FROM returns r
    JOIN order_items oi ON r.order_id = oi.order_id AND r.product_id = oi.product_id
    GROUP BY oi.order_id, oi.product_id
)
SELECT c.category_name, c.subcategory,
       COUNT(DISTINCT p.product_id)               AS product_count,
       SUM(oi.quantity)                           AS units_sold,
       ROUND(SUM(oi.quantity*oi.unit_price),2)    AS gross_revenue,
       ROUND(AVG(p.price),2)                      AS avg_product_price,
       ROUND(AVG(p.rating),2)                     AS avg_product_rating,
       COALESCE(SUM(cr.ret_count),0)              AS total_returns,
       ROUND(COALESCE(SUM(cr.ret_count),0)*100.0
             /NULLIF(SUM(oi.quantity),0),2)        AS return_rate_pct
FROM categories c
JOIN products p     ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders o       ON oi.order_id   = o.order_id
LEFT JOIN cat_returns cr ON oi.order_id = cr.order_id AND oi.product_id = cr.product_id
WHERE o.order_status NOT IN ('Cancelled')
GROUP BY c.category_name, c.subcategory ORDER BY gross_revenue DESC;

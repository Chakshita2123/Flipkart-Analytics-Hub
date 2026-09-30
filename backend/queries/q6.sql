-- QUERY 6: Product Return Analysis and Return Rates
-- Business question: Which products have the highest return rates (>15% = HIGH RISK)?
-- SQL concepts: CTE pre-aggregation prevents returns join fan-out; LEFT JOIN, NULLIF,
--               GROUP_CONCAT.
-- FIX (v2): returns pre-aggregated in CTE to prevent SUM(quantity) fan-out inflation.
WITH returns_agg AS (
    SELECT order_id, product_id,
           COUNT(*)                                       AS return_count,
           GROUP_CONCAT(reason ORDER BY return_id SEPARATOR ' | ') AS return_reasons
    FROM returns
    GROUP BY order_id, product_id
)
SELECT
    p.product_id, p.product_name, c.category_name,
    COUNT(DISTINCT oi.order_id)       AS total_orders,
    COALESCE(SUM(ra.return_count),0)  AS total_returns,
    ROUND(COALESCE(SUM(ra.return_count),0)*100.0
          /NULLIF(COUNT(DISTINCT oi.order_id),0),2)           AS return_rate_pct,
    GROUP_CONCAT(DISTINCT ra.return_reasons SEPARATOR ' | ')  AS return_reasons,
    CASE
        WHEN COALESCE(SUM(ra.return_count),0)*100.0
             /NULLIF(COUNT(DISTINCT oi.order_id),0) > 15
             THEN 'HIGH RISK - Review Needed'
        WHEN COALESCE(SUM(ra.return_count),0)*100.0
             /NULLIF(COUNT(DISTINCT oi.order_id),0) > 5
             THEN 'MODERATE - Monitor'
        ELSE 'HEALTHY'
    END AS return_health_flag
FROM products p
JOIN categories  c   ON p.category_id = c.category_id
JOIN order_items oi  ON p.product_id  = oi.product_id
LEFT JOIN returns_agg ra ON oi.order_id = ra.order_id AND oi.product_id = ra.product_id
GROUP BY p.product_id, p.product_name, c.category_name
HAVING total_orders > 0 ORDER BY return_rate_pct DESC;

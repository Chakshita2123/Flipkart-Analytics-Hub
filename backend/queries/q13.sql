-- QUERY 13: Seller Reliability Score (Weighted 0-100)
-- Business question: Which sellers are most reliable based on cancellations, returns, reviews?
-- SQL concepts: CTE, weighted scoring formula, COALESCE.
-- FIX (v2): NULLIF(total_orders,1) -> NULLIF(total_orders,0) so single-order sellers
--           are not incorrectly penalised with NULL reliability score.
WITH seller_stats AS (
    SELECT s.seller_id, s.seller_name, s.rating AS platform_rating,
           COUNT(DISTINCT o.order_id) AS total_orders,
           COUNT(DISTINCT CASE WHEN o.order_status='Cancelled' THEN o.order_id END) AS cancelled_orders,
           COUNT(DISTINCT CASE WHEN o.order_status='Returned'  THEN o.order_id END) AS returned_orders,
           COUNT(DISTINCT rv.review_id) AS review_count,
           ROUND(AVG(rv.rating),2) AS avg_review_rating
    FROM sellers s
    JOIN products p      ON s.seller_id  = p.seller_id
    JOIN order_items oi  ON p.product_id = oi.product_id
    JOIN orders o        ON oi.order_id  = o.order_id
    LEFT JOIN reviews rv ON p.product_id = rv.product_id
    GROUP BY s.seller_id, s.seller_name, s.rating
)
SELECT seller_id, seller_name, platform_rating, total_orders,
       cancelled_orders, returned_orders, review_count,
       COALESCE(avg_review_rating,0) AS avg_review_rating,
       ROUND(cancelled_orders*100.0/NULLIF(total_orders,0),2) AS cancel_rate_pct,
       ROUND(returned_orders *100.0/NULLIF(total_orders,0),2) AS return_rate_pct,
       ROUND((COALESCE(avg_review_rating,3)/5.0*40) +
             ((1-cancelled_orders/NULLIF(total_orders,0))*30) +
             ((1-returned_orders /NULLIF(total_orders,0))*20) +
             (platform_rating/5.0*10), 2) AS reliability_score
FROM seller_stats ORDER BY reliability_score DESC;

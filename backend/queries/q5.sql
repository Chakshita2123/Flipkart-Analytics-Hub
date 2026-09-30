-- QUERY 5: Top Sellers by Rating and Revenue (Composite Score)
-- Business question: Which sellers perform best combining rating and revenue?
-- SQL concepts: Composite scoring with MAX() OVER() for normalisation.
SELECT
    s.seller_id, s.seller_name, s.rating AS seller_rating, s.total_products,
    COUNT(DISTINCT oi.order_id)                  AS total_orders_fulfilled,
    ROUND(SUM(oi.quantity*oi.unit_price),2)       AS gross_revenue,
    ROUND(AVG(oi.unit_price),2)                   AS avg_selling_price,
    ROUND((s.rating/5.0)*0.4 +
          (SUM(oi.quantity*oi.unit_price)/MAX(SUM(oi.quantity*oi.unit_price)) OVER ())*0.6,4)
                                                  AS composite_score
FROM sellers s
JOIN products p     ON s.seller_id  = p.seller_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o       ON oi.order_id  = o.order_id
WHERE o.order_status IN ('Delivered','Shipped')
GROUP BY s.seller_id, s.seller_name, s.rating, s.total_products
ORDER BY composite_score DESC;

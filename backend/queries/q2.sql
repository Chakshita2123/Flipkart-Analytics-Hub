-- QUERY 2: Best-Selling Products by Category
-- Business question: Which products lead within each category by units sold?
-- SQL concepts: RANK() window function with PARTITION BY.
SELECT
    c.category_name, c.subcategory, p.product_name,
    SUM(oi.quantity)                           AS units_sold,
    ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
    RANK() OVER (PARTITION BY c.category_name ORDER BY SUM(oi.quantity) DESC) AS category_rank
FROM products p
JOIN categories  c  ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders      o  ON oi.order_id   = o.order_id
WHERE o.order_status IN ('Delivered','Shipped')
GROUP BY c.category_name, c.subcategory, p.product_id, p.product_name
ORDER BY c.category_name, category_rank;

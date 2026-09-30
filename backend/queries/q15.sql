-- QUERY 15: Inventory Health Check
-- Business question: Which products need restocking? Which are overstocked?
-- SQL concepts: FIELD() for priority-based custom sort; stock velocity = units/24 weeks.
-- FIX (v2): order_status filter applied INSIDE the subquery so that non-delivered/shipped
--           order items are excluded from total_units_sold. Previously the filter was in
--           LEFT JOIN...ON which had no effect on unmatched rows.
WITH product_sales AS (
    SELECT p.product_id, p.product_name, p.price, p.stock AS current_stock, p.rating,
           c.category_name, s.seller_name,
           COALESCE(ds.total_units_sold,0) AS total_units_sold,
           COALESCE(ds.total_orders,0)     AS total_orders
    FROM products p
    JOIN categories c ON p.category_id = c.category_id
    JOIN sellers s    ON p.seller_id   = s.seller_id
    LEFT JOIN (
        SELECT oi.product_id,
               SUM(oi.quantity)              AS total_units_sold,
               COUNT(DISTINCT oi.order_id)   AS total_orders
        FROM order_items oi
        JOIN orders o ON oi.order_id = o.order_id
        WHERE o.order_status IN ('Delivered','Shipped')
        GROUP BY oi.product_id
    ) ds ON p.product_id = ds.product_id
)
SELECT product_id, product_name, category_name, seller_name, price,
       current_stock, total_units_sold, total_orders, rating,
       ROUND(current_stock/NULLIF(total_units_sold/24.0,0),1) AS estimated_weeks_of_stock,
       CASE WHEN current_stock=0                             THEN 'OUT OF STOCK'
            WHEN current_stock<=10 AND total_units_sold>5   THEN 'CRITICAL - Reorder Now'
            WHEN current_stock<=30 AND total_units_sold>10  THEN 'LOW STOCK - Monitor'
            WHEN current_stock>100 AND total_units_sold<2   THEN 'OVERSTOCKED - Review'
            ELSE 'HEALTHY' END AS stock_health,
       ROUND(current_stock*price,2) AS inventory_value_inr
FROM product_sales
ORDER BY FIELD(stock_health,'OUT OF STOCK','CRITICAL - Reorder Now','LOW STOCK - Monitor','OVERSTOCKED - Review','HEALTHY'),
         total_units_sold DESC;

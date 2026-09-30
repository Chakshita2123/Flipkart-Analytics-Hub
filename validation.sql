-- =============================================================================
-- Flipkart Analytics Hub - Data Integrity Validation (v2)
-- =============================================================================
-- Run this file AFTER loading schema.sql and sample_data.sql.
-- EVERY check must return bad_rows = 0.
-- If any check returns > 0, there is a data integrity problem.
-- =============================================================================
USE flipkart_analytics;

-- CHECK 1: FK orphans - orders referencing non-existent users
SELECT 'CHECK 1 - orphan orders.user_id' AS check_name,
       COUNT(*) AS bad_rows
FROM orders o LEFT JOIN users u ON o.user_id = u.user_id
WHERE u.user_id IS NULL;

-- CHECK 2: FK orphans - order_items referencing non-existent orders
SELECT 'CHECK 2 - orphan order_items.order_id' AS check_name,
       COUNT(*) AS bad_rows
FROM order_items oi LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_id IS NULL;

-- CHECK 3: FK orphans - order_items referencing non-existent products
SELECT 'CHECK 3 - orphan order_items.product_id' AS check_name,
       COUNT(*) AS bad_rows
FROM order_items oi LEFT JOIN products p ON oi.product_id = p.product_id
WHERE p.product_id IS NULL;

-- CHECK 4: Order total must equal SUM(quantity * unit_price) for every order
SELECT 'CHECK 4 - order total vs items sum' AS check_name,
       COUNT(*) AS bad_rows
FROM orders o
JOIN (
    SELECT order_id, ROUND(SUM(quantity * unit_price),2) AS items_total
    FROM order_items GROUP BY order_id
) s ON o.order_id = s.order_id
WHERE ROUND(o.total_amount,2) <> s.items_total;

-- CHECK 5: Every order must have at least one order_item
SELECT 'CHECK 5 - orders with no items' AS check_name,
       COUNT(*) AS bad_rows
FROM orders o LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE oi.order_item_id IS NULL;

-- CHECK 6: Returns must match an existing order_items row (order_id + product_id combo)
SELECT 'CHECK 6 - returns with no matching order_item' AS check_name,
       COUNT(*) AS bad_rows
FROM returns r
LEFT JOIN order_items oi ON r.order_id = oi.order_id AND r.product_id = oi.product_id
WHERE oi.order_item_id IS NULL;

-- CHECK 7: Returns only allowed on Delivered or Returned orders
SELECT 'CHECK 7 - returns on invalid order status' AS check_name,
       COUNT(*) AS bad_rows
FROM returns r JOIN orders o ON r.order_id = o.order_id
WHERE o.order_status NOT IN ('Delivered','Returned');

-- CHECK 8: Every order with status = 'Returned' must have at least one return row
SELECT 'CHECK 8 - Returned orders missing return row' AS check_name,
       COUNT(*) AS bad_rows
FROM orders o LEFT JOIN returns r ON o.order_id = r.order_id
WHERE o.order_status = 'Returned' AND r.return_id IS NULL;

-- CHECK 9: orders.region must match users.region
SELECT 'CHECK 9 - region mismatch orders vs users' AS check_name,
       COUNT(*) AS bad_rows
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.region <> u.region;

-- CHECK 10: Reviews only by users who have a Delivered order for that product
SELECT 'CHECK 10 - reviews not by verified Delivered buyers' AS check_name,
       COUNT(*) AS bad_rows
FROM reviews rv
WHERE NOT EXISTS (
    SELECT 1
    FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
    WHERE o.user_id = rv.user_id
      AND oi.product_id = rv.product_id
      AND o.order_status = 'Delivered'
);

-- CHECK 11: sellers.total_products must equal actual count of products for that seller
SELECT 'CHECK 11 - sellers.total_products mismatch' AS check_name,
       COUNT(*) AS bad_rows
FROM sellers s
LEFT JOIN (SELECT seller_id, COUNT(*) AS c FROM products GROUP BY seller_id) p
       ON s.seller_id = p.seller_id
WHERE s.total_products <> COALESCE(p.c, 0);

-- CHECK 12: All orders must be placed strictly AFTER the user's signup_date
SELECT 'CHECK 12 - orders on or before user signup_date' AS check_name,
       COUNT(*) AS bad_rows
FROM orders o JOIN users u ON o.user_id = u.user_id
WHERE o.order_date <= u.signup_date;

-- CHECK 13: unit_price in order_items must exactly match the product price
SELECT 'CHECK 13 - unit_price != product.price' AS check_name,
       COUNT(*) AS bad_rows
FROM order_items oi JOIN products p ON oi.product_id = p.product_id
WHERE ROUND(oi.unit_price,2) <> ROUND(p.price,2);

-- =============================================================================
-- SUMMARY: All 13 checks in one result set
-- Every chk value must have bad_rows = 0.
-- =============================================================================
SELECT '=== SUMMARY (all bad_rows should be 0) ===' AS section;
SELECT 'CHECK 1  orphan orders.user_id'                  AS chk, (SELECT COUNT(*) FROM orders o LEFT JOIN users u ON o.user_id=u.user_id WHERE u.user_id IS NULL) AS bad_rows
UNION ALL
SELECT 'CHECK 2  orphan order_items.order_id',                (SELECT COUNT(*) FROM order_items oi LEFT JOIN orders o ON oi.order_id=o.order_id WHERE o.order_id IS NULL)
UNION ALL
SELECT 'CHECK 3  orphan order_items.product_id',              (SELECT COUNT(*) FROM order_items oi LEFT JOIN products p ON oi.product_id=p.product_id WHERE p.product_id IS NULL)
UNION ALL
SELECT 'CHECK 4  order total vs items sum',                   (SELECT COUNT(*) FROM orders o JOIN (SELECT order_id,ROUND(SUM(quantity*unit_price),2) AS s FROM order_items GROUP BY order_id) x ON o.order_id=x.order_id WHERE ROUND(o.total_amount,2)<>x.s)
UNION ALL
SELECT 'CHECK 5  orders with no items',                       (SELECT COUNT(*) FROM orders o LEFT JOIN order_items oi ON o.order_id=oi.order_id WHERE oi.order_item_id IS NULL)
UNION ALL
SELECT 'CHECK 6  returns with no matching order_item',        (SELECT COUNT(*) FROM returns r LEFT JOIN order_items oi ON r.order_id=oi.order_id AND r.product_id=oi.product_id WHERE oi.order_item_id IS NULL)
UNION ALL
SELECT 'CHECK 7  returns on invalid order status',            (SELECT COUNT(*) FROM returns r JOIN orders o ON r.order_id=o.order_id WHERE o.order_status NOT IN ('Delivered','Returned'))
UNION ALL
SELECT 'CHECK 8  Returned orders missing return row',         (SELECT COUNT(*) FROM orders o LEFT JOIN returns r ON o.order_id=r.order_id WHERE o.order_status='Returned' AND r.return_id IS NULL)
UNION ALL
SELECT 'CHECK 9  region mismatch orders vs users',            (SELECT COUNT(*) FROM orders o JOIN users u ON o.user_id=u.user_id WHERE o.region<>u.region)
UNION ALL
SELECT 'CHECK 10 reviews not by verified buyers',             (SELECT COUNT(*) FROM reviews rv WHERE NOT EXISTS (SELECT 1 FROM orders o JOIN order_items oi ON o.order_id=oi.order_id WHERE o.user_id=rv.user_id AND oi.product_id=rv.product_id AND o.order_status='Delivered'))
UNION ALL
SELECT 'CHECK 11 sellers.total_products mismatch',            (SELECT COUNT(*) FROM sellers s LEFT JOIN (SELECT seller_id,COUNT(*) AS c FROM products GROUP BY seller_id) p ON s.seller_id=p.seller_id WHERE s.total_products<>COALESCE(p.c,0))
UNION ALL
SELECT 'CHECK 12 orders on or before signup_date',            (SELECT COUNT(*) FROM orders o JOIN users u ON o.user_id=u.user_id WHERE o.order_date<=u.signup_date)
UNION ALL
SELECT 'CHECK 13 unit_price != product.price',                (SELECT COUNT(*) FROM order_items oi JOIN products p ON oi.product_id=p.product_id WHERE ROUND(oi.unit_price,2)<>ROUND(p.price,2));

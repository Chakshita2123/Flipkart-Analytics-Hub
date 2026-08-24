-- =============================================================================
-- Flipkart Analytics Hub - 15 Advanced Analytical SQL Queries
-- =============================================================================
USE flipkart_analytics;

-- QUERY 1: Top 10 Customers by Total Spending
-- Identifies highest-value customers by summing all delivered orders.
SELECT
    u.user_id, u.username, u.city, u.region, u.user_type,
    COUNT(o.order_id)            AS total_orders,
    ROUND(SUM(o.total_amount),2) AS total_spending,
    ROUND(AVG(o.total_amount),2) AS avg_order_value,
    MAX(o.order_date)            AS last_order_date
FROM users u
JOIN orders o ON u.user_id = o.user_id
WHERE o.order_status = 'Delivered'
GROUP BY u.user_id, u.username, u.city, u.region, u.user_type
ORDER BY total_spending DESC LIMIT 10;

-- QUERY 2: Best-Selling Products by Category
-- Uses RANK() window function with PARTITION BY for in-category ranking.
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

-- QUERY 3: Payment Method Preferences (with Percentages)
-- COD dominance (~60%) typical in Indian e-commerce.
SELECT
    payment_method,
    COUNT(*)                                                              AS order_count,
    ROUND(SUM(total_amount),2)                                            AS total_revenue,
    ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (),2)                         AS order_pct,
    ROUND(SUM(total_amount)*100.0/SUM(SUM(total_amount)) OVER (),2)       AS revenue_pct,
    ROUND(AVG(total_amount),2)                                            AS avg_order_value
FROM orders GROUP BY payment_method ORDER BY order_count DESC;

-- QUERY 4: Regional Sales Performance
SELECT
    o.region,
    COUNT(DISTINCT o.order_id)                                               AS total_orders,
    COUNT(DISTINCT o.user_id)                                                AS unique_customers,
    ROUND(SUM(o.total_amount),2)                                             AS total_revenue,
    ROUND(AVG(o.total_amount),2)                                             AS avg_order_value,
    ROUND(SUM(o.total_amount)*100.0/SUM(SUM(o.total_amount)) OVER (),2)     AS revenue_share_pct
FROM orders o
WHERE o.order_status NOT IN ('Cancelled','Returned')
GROUP BY o.region ORDER BY total_revenue DESC;

-- QUERY 5: Top Sellers by Rating and Revenue (Composite Score)
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

-- QUERY 6: Product Return Analysis and Return Rates
-- Flags products with >15% return rate as HIGH RISK.
SELECT
    p.product_id, p.product_name, c.category_name,
    COUNT(DISTINCT oi.order_id)  AS total_orders,
    COUNT(DISTINCT r.return_id)  AS total_returns,
    ROUND(COUNT(DISTINCT r.return_id)*100.0/NULLIF(COUNT(DISTINCT oi.order_id),0),2) AS return_rate_pct,
    GROUP_CONCAT(DISTINCT r.reason ORDER BY r.return_id SEPARATOR ' | ') AS return_reasons,
    CASE
        WHEN COUNT(DISTINCT r.return_id)*100.0/NULLIF(COUNT(DISTINCT oi.order_id),0) > 15
             THEN 'HIGH RISK - Review Needed'
        WHEN COUNT(DISTINCT r.return_id)*100.0/NULLIF(COUNT(DISTINCT oi.order_id),0) > 5
             THEN 'MODERATE - Monitor'
        ELSE 'HEALTHY'
    END AS return_health_flag
FROM products p
JOIN categories  c   ON p.category_id = c.category_id
JOIN order_items oi  ON p.product_id  = oi.product_id
LEFT JOIN returns r  ON oi.order_id   = r.order_id AND oi.product_id = r.product_id
GROUP BY p.product_id, p.product_name, c.category_name
HAVING total_orders > 0 ORDER BY return_rate_pct DESC;

-- QUERY 7: Customer Lifetime Value - RFM Analysis
-- NTILE(5) segments customers into Champion, Loyal, Potential, At Risk, Lost.
WITH rfm_raw AS (
    SELECT u.user_id, u.username, u.city, u.user_type,
           DATEDIFF(CURDATE(), MAX(o.order_date)) AS recency_days,
           COUNT(o.order_id)                       AS frequency,
           ROUND(SUM(o.total_amount),2)            AS monetary
    FROM users u JOIN orders o ON u.user_id = o.user_id
    WHERE o.order_status = 'Delivered'
    GROUP BY u.user_id, u.username, u.city, u.user_type
),
rfm_scores AS (
    SELECT *, NTILE(5) OVER (ORDER BY recency_days ASC)  AS r_score,
              NTILE(5) OVER (ORDER BY frequency DESC)     AS f_score,
              NTILE(5) OVER (ORDER BY monetary DESC)      AS m_score
    FROM rfm_raw
)
SELECT user_id, username, city, user_type, recency_days, frequency, monetary,
       r_score, f_score, m_score,
       ROUND((r_score+f_score+m_score)/3.0,2) AS rfm_avg_score,
       CASE WHEN (r_score+f_score+m_score) >= 13 THEN 'Champion'
            WHEN (r_score+f_score+m_score) >= 10 THEN 'Loyal Customer'
            WHEN (r_score+f_score+m_score) >= 7  THEN 'Potential Loyalist'
            WHEN r_score <= 2                     THEN 'At Risk'
            ELSE 'Lost Customer' END AS customer_segment
FROM rfm_scores ORDER BY rfm_avg_score DESC;

-- QUERY 8: Monthly Revenue Trends
-- LAG() for MoM growth; cumulative SUM OVER UNBOUNDED PRECEDING.
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

-- QUERY 9: Churn Analysis - Customers with No Purchase in 60 Days
SELECT u.user_id, u.username, u.email, u.city, u.region, u.user_type,
       MAX(o.order_date)                      AS last_purchase_date,
       DATEDIFF(CURDATE(),MAX(o.order_date))  AS days_since_last_purchase,
       COUNT(o.order_id)                      AS lifetime_orders,
       ROUND(SUM(o.total_amount),2)           AS lifetime_value,
       CASE WHEN DATEDIFF(CURDATE(),MAX(o.order_date)) BETWEEN 60 AND 90   THEN 'Early Churn Risk'
            WHEN DATEDIFF(CURDATE(),MAX(o.order_date)) BETWEEN 91 AND 180  THEN 'Churning'
            ELSE 'Churned' END AS churn_status
FROM users u JOIN orders o ON u.user_id = o.user_id
GROUP BY u.user_id, u.username, u.email, u.city, u.region, u.user_type
HAVING days_since_last_purchase >= 60
ORDER BY days_since_last_purchase DESC;

-- QUERY 10: Category Performance Metrics
SELECT c.category_name, c.subcategory,
       COUNT(DISTINCT p.product_id)               AS product_count,
       SUM(oi.quantity)                           AS units_sold,
       ROUND(SUM(oi.quantity*oi.unit_price),2)    AS gross_revenue,
       ROUND(AVG(p.price),2)                      AS avg_product_price,
       ROUND(AVG(p.rating),2)                     AS avg_product_rating,
       COUNT(DISTINCT r.return_id)                AS total_returns,
       ROUND(COUNT(DISTINCT r.return_id)*100.0/NULLIF(SUM(oi.quantity),0),2) AS return_rate_pct
FROM categories c
JOIN products p     ON c.category_id = p.category_id
JOIN order_items oi ON p.product_id  = oi.product_id
JOIN orders o       ON oi.order_id   = o.order_id
LEFT JOIN returns r ON o.order_id    = r.order_id AND p.product_id = r.product_id
WHERE o.order_status NOT IN ('Cancelled')
GROUP BY c.category_name, c.subcategory ORDER BY gross_revenue DESC;

-- QUERY 11: Festival Season Sales Patterns
-- Tags months: Diwali, Big Billion Days, Republic Day Sale, Holi, etc.
SELECT DATE_FORMAT(o.order_date,'%Y-%m') AS sale_month,
       MONTHNAME(o.order_date) AS month_name,
       COUNT(o.order_id) AS total_orders, ROUND(SUM(o.total_amount),2) AS total_revenue,
       COUNT(DISTINCT o.user_id) AS active_customers, ROUND(AVG(o.total_amount),2) AS avg_order_value,
       CASE MONTH(o.order_date)
           WHEN 1  THEN 'Republic Day Sale'
           WHEN 2  THEN 'Valentine Sale'
           WHEN 3  THEN 'Holi Sale'
           WHEN 8  THEN 'Independence Day Sale'
           WHEN 10 THEN 'Navratri / Big Billion Days'
           WHEN 11 THEN 'Diwali / Dhanteras'
           WHEN 12 THEN 'End of Season Sale'
           ELSE         'Regular Month'
       END AS festival_tag
FROM orders o WHERE o.order_status NOT IN ('Cancelled','Returned')
GROUP BY sale_month, month_name, MONTH(o.order_date) ORDER BY sale_month;

-- QUERY 12: Payment Method Distribution by Region
-- PARTITION BY region gives within-group percentage.
SELECT region, payment_method, COUNT(*) AS order_count,
       ROUND(SUM(total_amount),2) AS revenue,
       ROUND(COUNT(*)*100.0/SUM(COUNT(*)) OVER (PARTITION BY region),2) AS pct_within_region
FROM orders GROUP BY region, payment_method ORDER BY region, order_count DESC;

-- QUERY 13: Seller Reliability Score (Weighted 0-100)
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
             ((1-cancelled_orders/NULLIF(total_orders,1))*30) +
             ((1-returned_orders /NULLIF(total_orders,1))*20) +
             (platform_rating/5.0*10), 2) AS reliability_score
FROM seller_stats ORDER BY reliability_score DESC;

-- QUERY 14: Customer Acquisition Cost Analysis
-- FIRST_VALUE() + chained CTEs to classify conversion speed.
WITH first_orders AS (
    SELECT user_id, MIN(order_date) AS first_order_date,
           FIRST_VALUE(total_amount) OVER (PARTITION BY user_id ORDER BY order_date) AS first_order_value
    FROM orders WHERE order_status='Delivered' GROUP BY user_id, order_date, total_amount
),
customer_summary AS (
    SELECT u.user_id, u.username, u.user_type, u.signup_date,
           f.first_order_date, f.first_order_value,
           DATEDIFF(f.first_order_date, u.signup_date) AS days_to_first_purchase,
           COUNT(o.order_id) AS total_orders, ROUND(SUM(o.total_amount),2) AS total_clv
    FROM users u JOIN first_orders f ON u.user_id=f.user_id
    JOIN orders o ON u.user_id=o.user_id WHERE o.order_status='Delivered'
    GROUP BY u.user_id, u.username, u.user_type, u.signup_date, f.first_order_date, f.first_order_value
)
SELECT user_id, username, user_type, signup_date, first_order_date,
       days_to_first_purchase, first_order_value, total_orders, total_clv,
       ROUND(total_clv/NULLIF(total_orders,0),2) AS avg_order_value,
       CASE WHEN days_to_first_purchase <= 7  THEN 'Instant Converter'
            WHEN days_to_first_purchase <= 30 THEN 'Quick Converter'
            WHEN days_to_first_purchase <= 90 THEN 'Slow Converter'
            ELSE 'Long-term Nurture' END AS acquisition_type
FROM customer_summary ORDER BY total_clv DESC;

-- QUERY 15: Inventory Health Check
-- FIELD() for priority-based sort; stock velocity = units sold / 24 weeks.
WITH product_sales AS (
    SELECT p.product_id, p.product_name, p.price, p.stock AS current_stock, p.rating,
           c.category_name, s.seller_name,
           COALESCE(SUM(oi.quantity),0)   AS total_units_sold,
           COUNT(DISTINCT oi.order_id)    AS total_orders
    FROM products p
    JOIN categories c    ON p.category_id = c.category_id
    JOIN sellers s       ON p.seller_id   = s.seller_id
    LEFT JOIN order_items oi ON p.product_id = oi.product_id
    LEFT JOIN orders o   ON oi.order_id=o.order_id AND o.order_status IN ('Delivered','Shipped')
    GROUP BY p.product_id,p.product_name,p.price,p.stock,p.rating,c.category_name,s.seller_name
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

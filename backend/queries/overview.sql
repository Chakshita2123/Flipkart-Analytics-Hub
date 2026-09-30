-- OVERVIEW KPIS QUERY
-- Business question: What are the high-level business performance totals?
-- KPI Definitions:
--   total_revenue: Sum of order totals for active orders (excluding Cancelled & Returned).
--                  Reconciles exactly with Query 8 monthly sum and Query 4 regional sum.
--   active_orders: Count of orders with status NOT IN ('Cancelled', 'Returned') [286 orders].
--   total_orders_placed: Total count of all orders placed in system [334 orders].
--   active_customers: Count of distinct users with at least one active order.
--   avg_order_value: Active revenue divided by active orders.
--   delivered_orders: Count of successfully delivered orders [256 orders].
--   returned_orders: Count of orders marked Returned [19 orders].
--   cancelled_orders: Count of orders marked Cancelled [29 orders].
--   total_return_items: Count of individual items logged in returns table [34 items].
--   order_return_rate_pct: Percentage of placed orders that were returned (~5.7%).

SELECT
    ROUND(SUM(CASE WHEN o.order_status NOT IN ('Cancelled','Returned') THEN o.total_amount ELSE 0 END), 2) AS total_revenue,
    COUNT(DISTINCT CASE WHEN o.order_status NOT IN ('Cancelled','Returned') THEN o.order_id END)           AS active_orders,
    COUNT(DISTINCT o.order_id)                                                                              AS total_orders_placed,
    COUNT(DISTINCT CASE WHEN o.order_status NOT IN ('Cancelled','Returned') THEN o.user_id END)            AS active_customers,
    ROUND(SUM(CASE WHEN o.order_status NOT IN ('Cancelled','Returned') THEN o.total_amount ELSE 0 END)
          / NULLIF(COUNT(DISTINCT CASE WHEN o.order_status NOT IN ('Cancelled','Returned') THEN o.order_id END), 0), 2) AS avg_order_value,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Delivered' THEN o.order_id END)                             AS delivered_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Returned'  THEN o.order_id END)                             AS returned_orders,
    COUNT(DISTINCT CASE WHEN o.order_status = 'Cancelled' THEN o.order_id END)                             AS cancelled_orders,
    (SELECT COUNT(*) FROM returns)                                                                          AS total_return_items,
    ROUND(COUNT(DISTINCT CASE WHEN o.order_status = 'Returned' THEN o.order_id END) * 100.0
          / NULLIF(COUNT(DISTINCT o.order_id), 0), 2)                                                      AS order_return_rate_pct
FROM orders o;

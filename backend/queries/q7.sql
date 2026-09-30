-- QUERY 7: Customer Lifetime Value - RFM Analysis
-- Business question: Segment customers: Champion, Loyal, Potential, At-Risk, Lost.
-- SQL concepts: CTE + NTILE(5) window function.
-- FIX (v2): NTILE direction corrected so score 5 = best on all axes.
--           Champion = most recent + frequent + highest spend.
--           @as_of replaces CURDATE() for reproducibility.
WITH rfm_raw AS (
    SELECT u.user_id, u.username, u.city, u.user_type,
           DATEDIFF(@as_of, MAX(o.order_date))  AS recency_days,
           COUNT(o.order_id)                    AS frequency,
           ROUND(SUM(o.total_amount),2)         AS monetary
    FROM users u JOIN orders o ON u.user_id = o.user_id
    WHERE o.order_status = 'Delivered'
    GROUP BY u.user_id, u.username, u.city, u.user_type
),
rfm_scores AS (
    -- r_score 5 = most recent (smallest recency_days), ORDER BY DESC -> tile 1 = worst
    -- f_score 5 = most frequent, ORDER BY ASC -> tile 5 = highest
    -- m_score 5 = highest spend, ORDER BY ASC -> tile 5 = highest
    SELECT *, NTILE(5) OVER (ORDER BY recency_days DESC) AS r_score,
              NTILE(5) OVER (ORDER BY frequency ASC)     AS f_score,
              NTILE(5) OVER (ORDER BY monetary ASC)      AS m_score
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

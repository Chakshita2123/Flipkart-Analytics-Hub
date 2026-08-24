# Flipkart Analytics Hub - SQL Portfolio Project

[![SQL](https://img.shields.io/badge/SQL-MySQL%208.0-blue?style=flat-square&logo=mysql)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-brightgreen?style=flat-square)]()
[![Queries](https://img.shields.io/badge/Analytical%20Queries-15-orange?style=flat-square)]()

> A complete, production-ready SQL analytics project modelled on an Indian e-commerce marketplace.  
> 8-table schema · 155+ realistic orders · 15 advanced analytical queries

---

## Project Overview

| Metric | Value |
|--------|-------|
| Users | 100 across Delhi, Mumbai, Bangalore, Kolkata, Chennai, Hyderabad |
| Sellers | 20 rated 4.0–4.9 |
| Products | 50 across Electronics, Fashion, Home, Books |
| Orders | 155+ (March–August 2026) |
| Payment Pattern | ~60% COD · ~20% UPI · ~20% Cards/Wallet |
| Regions | North · South · East · West |
| Price Range | Rs 199 – Rs 1,49,990 |

---

## Database Schema (8 Tables)

| Table | PK | Key Foreign Keys | Notable Columns |
|-------|----|-----------------|-----------------|
| users | user_id | — | region ENUM, user_type ENUM |
| sellers | seller_id | user_id → users | rating DECIMAL |
| categories | category_id | — | category_name, subcategory |
| products | product_id | category_id, seller_id | price, stock, rating |
| orders | order_id | user_id | payment_method ENUM, order_status ENUM |
| order_items | order_item_id | order_id, product_id | quantity, unit_price |
| reviews | review_id | product_id, user_id | rating CHECK(1-5) |
| returns | return_id | order_id, product_id | reason, status ENUM |

---

## Setup Instructions

```bash
# Import in order:
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql

# Run queries one by one:
mysql -u root -p flipkart_analytics < queries.sql
```

---

## 15 Analytical Queries

| # | Query | Key Concept |
|---|-------|-------------|
| 1 | Top 10 Customers by Spending | GROUP BY, ORDER BY |
| 2 | Best-Selling Products by Category | RANK() OVER PARTITION BY |
| 3 | Payment Method Preferences | SUM() OVER(), % calculation |
| 4 | Regional Sales Performance | Window SUM OVER() |
| 5 | Top Sellers by Rating + Revenue | Composite scoring |
| 6 | Product Return Analysis | LEFT JOIN, NULLIF, GROUP_CONCAT |
| 7 | Customer Lifetime Value (RFM) | CTE + NTILE(5) |
| 8 | Monthly Revenue Trends | LAG(), cumulative SUM OVER() |
| 9 | Churn Analysis (60-day) | DATEDIFF(), HAVING |
| 10 | Category Performance Metrics | Multi-table JOINs |
| 11 | Festival Season Patterns | DATE_FORMAT(), CASE WHEN |
| 12 | Payment Method by Region | PARTITION BY region |
| 13 | Seller Reliability Score | CTE + weighted formula |
| 14 | Customer Acquisition Analysis | FIRST_VALUE(), chained CTEs |
| 15 | Inventory Health Check | FIELD() custom sort |

---

## SQL Concepts Demonstrated

```
DDL           CREATE TABLE with ENUM, CHECK, FK constraints
DML           Bulk INSERT with realistic Indian e-commerce data
Window Funcs  RANK, NTILE, LAG, FIRST_VALUE, SUM OVER, PARTITION BY
CTEs          WITH clauses for multi-step analytical logic
Joins         INNER JOIN, LEFT JOIN up to 5 tables
Aggregation   SUM, COUNT, AVG, MAX, MIN with GROUP BY / HAVING
Conditional   CASE WHEN, COALESCE, NULLIF, FIELD
Date Funcs    DATE_FORMAT, DATEDIFF, MONTHNAME, CURDATE
String Funcs  GROUP_CONCAT with ORDER BY and SEPARATOR
Business KPIs RFM scoring, CLV, churn rate, reliability score, inventory velocity
```

---

## Portfolio Tips

**Resume line:**
> "Designed and analysed an 8-table MySQL database with 15 BI queries for an Indian e-commerce platform, implementing RFM segmentation, churn detection, inventory health scoring, and regional revenue analytics using window functions and CTEs."

**Extend this project:**
- Connect to Power BI / Tableau for a live dashboard
- Use Python + matplotlib to visualise query results
- Add stored procedures to automate monthly RFM refresh
- Demonstrate EXPLAIN ANALYZE for query optimisation

---

## Project Structure

```
flipkart-analytics-hub/
├── schema.sql           # 8-table schema with all constraints
├── sample_data.sql      # Realistic Indian e-commerce data
├── queries.sql          # 15 advanced analytical queries
├── README.md            # This file
└── generate_project.py  # Python script that created these files
```

---

MIT License -- use freely for your portfolio. Star the repo if it helped!

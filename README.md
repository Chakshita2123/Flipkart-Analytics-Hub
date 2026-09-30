# Flipkart Analytics Hub - SQL Portfolio Project

[![SQL](https://img.shields.io/badge/SQL-MySQL%208.0-blue?style=flat-square&logo=mysql)](https://www.mysql.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green?style=flat-square)](LICENSE)
[![Queries](https://img.shields.io/badge/Analytical%20Queries-15-orange?style=flat-square)](queries.sql)

> **Synthetic / Sample Data** - All users, sellers, products, orders, and transactions are
> artificially generated (Python, random seed 42) for portfolio purposes only.
> 8-table schema | 334 orders | 15 advanced analytical queries | Oct 2025 - Sep 2026

---

## Project Overview

| Metric | Value |
|--------|-------|
| Users | 97 (North / South / East / West across 20+ cities) |
| Sellers | 20 (rated 4.3 - 4.9) |
| Products | 50 (Electronics, Fashion, Home, Books) |
| Orders | 334 (Oct 2025 - Sep 2026) |
| Order Items | 864 line-items (1-4 per order) |
| Payment | 56.3% COD | 21.3% UPI | 22.5% Cards+Wallet (measured) |
| Price Range | Rs 199 - Rs 149,990 |
| Returned Orders | 19 (~5.7% of all orders) |
| Return Rows | 34 |
| Reviews | 70 (verified Delivered buyers only) |

---

## Setup

### Bash / Linux / macOS
```bash
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql
mysql -u root -p flipkart_analytics < validation.sql
mysql -u root -p flipkart_analytics < queries.sql
```

### Windows PowerShell
```powershell
Get-Content schema.sql | & "mysql" -u root -p
Get-Content sample_data.sql | & "mysql" -u root -p
Get-Content validation.sql | & "mysql" -u root -p
Get-Content queries.sql | & "mysql" -u root -p
```

---

## Database Schema (8 Tables)

| Table | Key Foreign Keys | Notable Columns |
|-------|-----------------|-----------------|
| users | - | region ENUM, user_type ENUM |
| sellers | user_id -> users | rating DECIMAL, total_products INT |
| categories | - | category_name, subcategory |
| products | category_id, seller_id | price, stock, rating |
| orders | user_id | payment_method ENUM, order_status ENUM |
| order_items | order_id, product_id | quantity, unit_price |
| reviews | product_id, user_id | rating CHECK(1-5) |
| returns | order_id, product_id | reason, status ENUM |

---

## 15 Analytical Queries

| # | Query | SQL Concepts |
|---|-------|-------------|
| 1 | Top 10 Customers by Spending | GROUP BY, ORDER BY, aggregate functions |
| 2 | Best-Selling Products by Category | RANK() OVER PARTITION BY |
| 3 | Payment Method Preferences | SUM() OVER(), percentage |
| 4 | Regional Sales Performance | Window SUM OVER() |
| 5 | Top Sellers - Rating + Revenue | Composite normalised scoring |
| 6 | Product Return Analysis | CTE pre-aggregation, LEFT JOIN, NULLIF, GROUP_CONCAT |
| 7 | RFM Customer Segmentation | CTE + NTILE(5), fixed @as_of |
| 8 | Monthly Revenue Trends | LAG(), cumulative SUM OVER() |
| 9 | Churn Analysis (60-day) | DATEDIFF(), HAVING, @as_of |
| 10 | Category Performance | CTE pre-aggregation, multi-table JOINs |
| 11 | Festival Season Patterns | DATE_FORMAT(), CASE WHEN |
| 12 | Payment by Region | PARTITION BY region |
| 13 | Seller Reliability Score | CTE + weighted formula, NULLIF fix |
| 14 | Time-to-First-Purchase & CLV | Chained CTEs, one clean row per user |
| 15 | Inventory Health Check | FIELD() custom sort, subquery status filter |

---

## SQL Concepts Demonstrated

```
DDL             CREATE TABLE with ENUM, CHECK, FK constraints
DML             Bulk INSERT with realistic Indian e-commerce data
Window Funcs    RANK, NTILE, LAG, SUM OVER, PARTITION BY, ROWS UNBOUNDED PRECEDING
CTEs            WITH clauses for multi-step analytical logic
Joins           INNER JOIN, LEFT JOIN up to 5 tables
Aggregation     SUM, COUNT, AVG, MAX, MIN with GROUP BY / HAVING
Conditional     CASE WHEN, COALESCE, NULLIF, FIELD
Date Funcs      DATE_FORMAT, DATEDIFF, MONTHNAME, @as_of session variable
String Funcs    GROUP_CONCAT with ORDER BY and SEPARATOR
Business KPIs   RFM scoring, CLV, churn rate, reliability score, inventory velocity
Integrity       validation.sql: 13 automated data-quality checks
```

---

## Resume Line

> "Designed and queried an 8-table MySQL 8 database (334 synthetic orders, Oct 2025-Sep 2026)
> for an Indian e-commerce platform. Implemented 15 BI queries covering RFM customer
> segmentation, churn detection, festival-season trend analysis, inventory health scoring,
> and regional revenue analytics using window functions, CTEs, and automated integrity
> validation (13 checks, all pass)."

---

## Project Structure

```
flipkart-analytics-hub/
|-- schema.sql          # 8-table schema (FK, ENUM, CHECK constraints)
|-- sample_data.sql     # Synthetic data (seed=42, Oct 2025-Sep 2026, 334 orders)
|-- queries.sql         # 15 analytical queries (v2 - all bugs fixed)
|-- validation.sql      # 13 integrity checks (all must return bad_rows = 0)
|-- README.md           # This file (stats computed from actual loaded data)
`-- generate_project.py # Python generator (run to regenerate all files)
```

MIT License - use freely for your portfolio.

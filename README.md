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

## Architecture

```
[ MySQL 8.0 Database ] (8 tables, synthetic e-commerce data)
         │
         ▼  (mysql2 pool + prepared session @as_of)
[ Node.js / Express API ] (/backend)
         │
         ├── REST Endpoints: GET /api/overview, /api/revenue/monthly, etc.
         └── npm run export-snapshot ─────────► [ Static Snapshot JSONs ]
                                                              │
                                                              ▼
[ React + Vite + Recharts Dashboard ] (/frontend) ◄───────────┘
  • Live Mode: Queries Express API & MySQL in real time
  • Snapshot Mode: Loads static JSON snapshots with zero backend needed
```

---

## Setup & Running

### 1. Database Setup

#### Bash / Linux / macOS
```bash
mysql -u root -p < schema.sql
mysql -u root -p < sample_data.sql
mysql -u root -p flipkart_analytics < validation.sql
mysql -u root -p flipkart_analytics < queries.sql
```

#### Windows PowerShell
```powershell
Get-Content schema.sql | & "mysql" -u root -p
Get-Content sample_data.sql | & "mysql" -u root -p
Get-Content validation.sql | & "mysql" -u root -p
Get-Content queries.sql | & "mysql" -u root -p
```

---

### 2. Backend API Setup (`/backend`)

The backend connects to MySQL using a connection pool and provides read-only endpoints.

```bash
cd backend
npm install
cp .env.example .env
```
*(In PowerShell: `Copy-Item .env.example .env`)*

Configure your `.env`:
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=flipkart_analytics
PORT=5000
FRONTEND_URL=http://localhost:5173
```

Start the API server:
```bash
npm start
# Server runs on http://localhost:5000
# Test health: curl http://localhost:5000/api/health
```

To export static snapshot files from the database:
```bash
npm run export-snapshot
# Writes JSON files to frontend/public/snapshot/*.json
```

---

### 3. Frontend Dashboard Setup (`/frontend`)

```bash
cd frontend
npm install
cp .env.example .env
```
*(In PowerShell: `Copy-Item .env.example .env`)*

#### Data Mode Switch
In `frontend/.env`:
- `VITE_DATA_MODE=live` : Connects to the Express backend (`http://localhost:5000/api`).
- `VITE_DATA_MODE=snapshot` : Runs entirely in the browser using static snapshots (`/snapshot/*.json`), requiring no backend or database server.

Start the frontend development server:
```bash
npm run dev
# Dashboard opens on http://localhost:5173
```

---

### 4. Static Deployment (Vercel / Netlify / GitHub Pages)

In snapshot mode, the frontend can be deployed as a static site without needing a Node or MySQL server:

1. Generate the latest snapshot: `cd backend && npm run export-snapshot`
2. Set `VITE_DATA_MODE=snapshot` in `frontend/.env` (or in deployment environment variables)
3. Build the production static bundle:
   ```bash
   cd frontend
   npm run build
   ```
4. Deploy the generated `frontend/dist` directory:
   - **Vercel**: Set Root Directory to `frontend`, Build Command `npm run build`, Output Directory `dist`
   - **Netlify**: Set Base directory to `frontend`, Build command `npm run build`, Publish directory `dist`

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
| 11 | Festival Season Patterns | CTE monthly aggregation, CASE WHEN |
| 12 | Payment by Region | PARTITION BY region |
| 13 | Seller Reliability Score | CTE + weighted formula, NULLIF fix |
| 14 | Time-to-First-Purchase & CLV | Chained CTEs, one clean row per user |
| 15 | Inventory Health Check | FIELD() custom sort, subquery status filter |

---

## Deploying on Render (Free & Fast)

### Option 1: Frontend Static Site (Recommended - 100% Free)
Because the dashboard includes full static snapshots of all 15 SQL query results (`/frontend/public/snapshot/`), you can host the entire dashboard, charts, tables, and **View SQL** panels on Render's Free Static Site tier without spinning up a database.

1. Sign up/log in at [render.com](https://render.com).
2. Click **New +** > **Static Site**.
3. Connect your GitHub repository: `Flipkart-Analytics-Hub`.
4. Configure the settings:
   - **Name**: `flipkart-analytics-dashboard`
   - **Root Directory**: `frontend`
   - **Build Command**: `npm install && npm run build`
   - **Publish Directory**: `dist`
5. Under **Environment Variables**, add:
   - `VITE_DATA_MODE` = `snapshot`
   - `NEXT_PUBLIC_DATA_MODE` = `snapshot`
6. Under **Redirects/Rewrites**, add:
   - **Type**: `Rewrite`
   - **Source**: `/*`
   - **Destination**: `/index.html`
7. Click **Create Static Site**. Your dashboard will be live in 1-2 minutes!

---

### Option 2: 1-Click Blueprint (using `render.yaml`)
1. Go to Render Dashboard > **Blueprints**.
2. Click **New Blueprint Instance**.
3. Select your repository. Render will automatically read `render.yaml` and configure the static site.
4. Click **Apply**.

---

### Option 3: Full-Stack (Live Node API + External MySQL)
Render does not natively host MySQL databases (only PostgreSQL). To run live SQL queries on Render:
1. Spin up a free MySQL 8 database on [Aiven](https://aiven.io), [TiDB Serverless](https://tidbcloud.com), or [Railway](https://railway.app).
2. Import `schema.sql` and `sample_data.sql` into that database.
3. In Render, create a **Web Service** for `backend`:
   - **Root Directory**: `backend`
   - **Build Command**: `npm install`
   - **Start Command**: `node server.js`
   - **Environment Variables**: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, `FRONTEND_URL`.
4. Create the **Static Site** for `frontend` with `VITE_DATA_MODE=live` and `VITE_API_BASE_URL=https://<your-backend>.onrender.com/api`.

---

## Project Structure

```
flipkart-analytics-hub/
|-- schema.sql              # 8-table schema (FK, ENUM, CHECK constraints)
|-- sample_data.sql         # Synthetic data (seed=42, Oct 2025-Sep 2026, 334 orders)
|-- queries.sql             # 15 analytical queries (v2 - all bugs fixed)
|-- validation.sql          # 13 integrity checks (all must return bad_rows = 0)
|-- README.md               # Documentation & setup instructions
|-- generate_project.py     # Python data generator (seed=42)
|-- backend/                # Node.js + Express API server
|   |-- server.js           # Express app, CORS, rate-limiting
|   |-- db.js               # mysql2 connection pool + @as_of session handler
|   |-- create_readonly_user.sql # Read-only MySQL credentials script
|   |-- queries/            # 1 SQL file per query (q1.sql ... q15.sql, overview.sql)
|   |-- routes/api.js       # Fixed GET endpoints + /api/sql/:id allowlist
|   `-- scripts/exportSnapshot.js # npm run export-snapshot script
`-- frontend/               # React + Vite + Tailwind + Recharts dashboard
    |-- src/                # UI pages, components, and data service
    |   |-- pages/          # 9 analytical pages (Overview, Revenue, Customers...)
    |   |-- components/     # DataTable, SqlViewerModal, MetricCard, Navbar, Sidebar
    |   `-- api.js          # Unified live vs snapshot data layer
    `-- public/snapshot/    # 16 pre-exported static JSON datasets
```

MIT License - use freely for your portfolio.


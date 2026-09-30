/**
 * exportSnapshot.js
 * Runs every query directly against the MySQL database and exports
 * static JSON snapshots into /frontend/public/snapshot/*.json
 * 
 * Usage: npm run export-snapshot (from backend/ directory)
 */

const fs = require('fs');
const path = require('path');
const { runQueryFile, getQuerySql, pool } = require('../db');

const snapshotDir = path.join(__dirname, '..', '..', 'frontend', 'public', 'snapshot');

const QUERY_TITLES = {
  overview: 'KPI Totals & High-Level Business Metrics',
  q1: 'Query 1: Top 10 Customers by Total Spending',
  q2: 'Query 2: Best-Selling Products by Category (Window RANK)',
  q3: 'Query 3: Payment Method Preferences & Revenue Share',
  q4: 'Query 4: Regional Sales Performance & Market Share',
  q5: 'Query 5: Top Sellers by Rating and Revenue (Composite Score)',
  q6: 'Query 6: Product Return Analysis & Risk Categorisation',
  q7: 'Query 7: Customer Lifetime Value - RFM Segmentation (NTILE)',
  q8: 'Query 8: Monthly Revenue Trends & MoM Growth (LAG)',
  q9: 'Query 9: Customer Churn Analysis (60-Day Inactive Cohorts)',
  q10: 'Query 10: Category Performance Metrics & Return Rates',
  q11: 'Query 11: Festival Season Sales Patterns & Volume Spikes',
  q12: 'Query 12: Payment Method Distribution by Geographic Region',
  q13: 'Query 13: Seller Reliability Score (Weighted Multi-Factor 0-100)',
  q14: 'Query 14: Time-to-First-Purchase & Customer Lifetime Value',
  q15: 'Query 15: Inventory Health Check & Restocking Priority'
};

async function exportAll() {
  console.log('--- Starting Snapshot Export ---');
  console.log(`Target directory: ${snapshotDir}`);

  if (!fs.existsSync(snapshotDir)) {
    fs.mkdirSync(snapshotDir, { recursive: true });
  }

  const generatedAt = new Date().toISOString();

  async function exportQuery(fileName, queryFile, transform = (data) => data) {
    try {
      const rows = await runQueryFile(queryFile);
      const data = transform(rows);
      const payload = {
        generated_at: generatedAt,
        query: queryFile.replace('.sql', ''),
        count: Array.isArray(data) ? data.length : 1,
        data
      };
      const filePath = path.join(snapshotDir, `${fileName}.json`);
      fs.writeFileSync(filePath, JSON.stringify(payload, null, 2), 'utf8');
      console.log(`  [OK] Exported ${fileName}.json (${Array.isArray(data) ? data.length : 1} records)`);
      return data;
    } catch (err) {
      console.error(`  [ERROR] Exporting ${fileName}:`, err.message);
      throw err;
    }
  }

  try {
    // 1. Overview KPIs
    await exportQuery('overview', 'overview.sql', (rows) => rows[0] || {});

    // 2. Query 8: Monthly revenue
    await exportQuery('revenue_monthly', 'q8.sql');

    // 3. Query 11: Festival sales
    await exportQuery('festival', 'q11.sql');

    // 4. Query 7: RFM Customer segmentation
    await exportQuery('customers_rfm', 'q7.sql');

    // 5. Query 9: Churn analysis
    await exportQuery('customers_churn', 'q9.sql');

    // 6. Query 13: Seller reliability
    await exportQuery('sellers_reliability', 'q13.sql');

    // 7. Query 15: Inventory health
    await exportQuery('inventory', 'q15.sql');

    // 8. Query 6: Returns
    await exportQuery('returns', 'q6.sql');

    // 9. Query 10: Category metrics
    await exportQuery('categories', 'q10.sql');

    // 10. Regions (Q4 + Q12)
    const [sales, paymentsByRegion] = await Promise.all([
      runQueryFile('q4.sql'),
      runQueryFile('q12.sql')
    ]);
    fs.writeFileSync(
      path.join(snapshotDir, 'regions.json'),
      JSON.stringify({
        generated_at: generatedAt,
        query: 'q4_q12',
        data: {
          regional_sales: sales,
          payments_by_region: paymentsByRegion
        }
      }, null, 2),
      'utf8'
    );
    console.log('  [OK] Exported regions.json (q4 + q12)');

    // 11. Payments (Q3)
    await exportQuery('payments', 'q3.sql');

    // 12. Top Customers (Q1)
    await exportQuery('top_customers', 'q1.sql');

    // 13. Top Products (Q2)
    await exportQuery('top_products', 'q2.sql');

    // 14. Acquisition & CLV (Q14)
    await exportQuery('acquisition', 'q14.sql');

    // 15. Top Sellers (Q5)
    await exportQuery('top_sellers', 'q5.sql');

    // 16. Export all SQL query definitions for offline "View SQL"
    const sqlMap = {};
    for (const [key, title] of Object.entries(QUERY_TITLES)) {
      sqlMap[key] = {
        id: key,
        title,
        sql: getQuerySql(`${key}.sql`)
      };
    }
    fs.writeFileSync(
      path.join(snapshotDir, 'sql_queries.json'),
      JSON.stringify({
        generated_at: generatedAt,
        queries: sqlMap
      }, null, 2),
      'utf8'
    );
    console.log('  [OK] Exported sql_queries.json (16 query texts)');

    console.log('\nSnapshot export completed successfully!');
  } finally {
    await pool.end();
  }
}

exportAll().catch((err) => {
  console.error('Snapshot export failed:', err);
  process.exit(1);
});

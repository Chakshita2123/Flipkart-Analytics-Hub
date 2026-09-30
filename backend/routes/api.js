const express = require('express');
const router = express.Router();
const { runQueryFile, getQuerySql } = require('../db');

// Metadata mapping for allowlisted queries
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

// Standard wrapper for endpoint execution
function handleQuery(queryFile, dataTransform = (data) => data) {
  return async (req, res) => {
    try {
      const rows = await runQueryFile(queryFile);
      res.json({
        success: true,
        query: queryFile.replace('.sql', ''),
        count: Array.isArray(rows) ? rows.length : 1,
        data: dataTransform(rows)
      });
    } catch (err) {
      console.error(`Error running ${queryFile}:`, err.message);
      // Never leak SQL structure or stack trace to client
      res.status(500).json({
        success: false,
        error: 'Failed to retrieve data from analytics database'
      });
    }
  };
}

// 1. Health check
router.get('/health', (req, res) => {
  res.json({ status: 'ok', timestamp: new Date().toISOString() });
});

// 2. Overview KPIs
router.get('/overview', handleQuery('overview.sql', (rows) => rows[0] || {}));

// 3. Revenue & Monthly Trends (Q8)
router.get('/revenue/monthly', handleQuery('q8.sql'));

// 4. Festival Season Analysis (Q11)
router.get('/festival', handleQuery('q11.sql'));

// 5. RFM Customer Segmentation (Q7)
router.get('/customers/rfm', handleQuery('q7.sql'));

// 6. Churn Analysis (Q9)
router.get('/customers/churn', handleQuery('q9.sql'));

// 7. Seller Reliability (Q13)
router.get('/sellers/reliability', handleQuery('q13.sql'));

// 8. Inventory Health (Q15)
router.get('/inventory', handleQuery('q15.sql'));

// 9. Product Returns (Q6)
router.get('/returns', handleQuery('q6.sql'));

// 10. Category Performance (Q10)
router.get('/categories', handleQuery('q10.sql'));

// 11. Regions (Q4 and Q12)
router.get('/regions', async (req, res) => {
  try {
    const [sales, paymentsByRegion] = await Promise.all([
      runQueryFile('q4.sql'),
      runQueryFile('q12.sql')
    ]);
    res.json({
      success: true,
      query: 'q4_q12',
      data: {
        regional_sales: sales,
        payments_by_region: paymentsByRegion
      }
    });
  } catch (err) {
    console.error('Error running /regions:', err.message);
    res.status(500).json({ success: false, error: 'Failed to retrieve regional data' });
  }
});

// 12. Payment Methods (Q3)
router.get('/payments', handleQuery('q3.sql'));

// 13. Top Customers (Q1)
router.get('/top-customers', handleQuery('q1.sql'));

// 14. Top Products (Q2)
router.get('/top-products', handleQuery('q2.sql'));

// 15. Customer Acquisition & CLV (Q14)
router.get('/acquisition', handleQuery('q14.sql'));

// 16. Top Sellers (Q5)
router.get('/top-sellers', handleQuery('q5.sql'));

// 17. Expose SQL text for UI "View SQL" panels (Fixed allowlist only)
router.get('/sql/:id', (req, res) => {
  let key = String(req.params.id).toLowerCase();
  if (/^\d+$/.test(key)) {
    key = `q${key}`;
  }
  
  if (!QUERY_TITLES[key]) {
    return res.status(404).json({ success: false, error: 'Query not found in allowlist' });
  }

  try {
    const filename = `${key}.sql`;
    const sqlText = getQuerySql(filename);
    res.json({
      success: true,
      id: key,
      title: QUERY_TITLES[key],
      sql: sqlText
    });
  } catch (err) {
    console.error(`Error reading SQL file for ${key}:`, err.message);
    res.status(500).json({ success: false, error: 'Failed to read query definition' });
  }
});

module.exports = router;

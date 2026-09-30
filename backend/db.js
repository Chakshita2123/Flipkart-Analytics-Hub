const mysql = require('mysql2/promise');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const pool = mysql.createPool({
  host: process.env.DB_HOST || 'localhost',
  port: parseInt(process.env.DB_PORT || '3306', 10),
  user: process.env.DB_USER || 'root',
  password: process.env.DB_PASSWORD || '',
  database: process.env.DB_NAME || 'flipkart_analytics',
  waitForConnections: true,
  connectionLimit: 10,
  queueLimit: 0,
  multipleStatements: true,
  decimalNumbers: true
});

// Cache query SQL files from backend/queries/
const queriesDir = path.join(__dirname, 'queries');
const queryCache = {};

function getQuerySql(filename) {
  if (!queryCache[filename]) {
    const filePath = path.join(queriesDir, filename);
    queryCache[filename] = fs.readFileSync(filePath, 'utf8');
  }
  return queryCache[filename];
}

/**
 * Execute a query on a dedicated pooled connection,
 * ensuring @as_of session variable is set on the exact same session.
 */
async function executeQuery(sql, params = []) {
  const conn = await pool.getConnection();
  try {
    // Set @as_of on this specific connection session
    await conn.query('SET @as_of = (SELECT MAX(order_date) FROM orders);');
    const [rows] = await conn.query(sql, params);
    return rows;
  } finally {
    conn.release();
  }
}

/**
 * Execute one of the standard query files by filename (e.g., 'q1.sql')
 */
async function runQueryFile(filename, params = []) {
  const sql = getQuerySql(filename);
  return executeQuery(sql, params);
}

module.exports = {
  pool,
  executeQuery,
  runQueryFile,
  getQuerySql
};

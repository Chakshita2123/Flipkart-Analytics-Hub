/**
 * Flipkart Analytics Hub - API & Data Service
 * 
 * In 'live' mode: Fetches from Node Express API connected to live MySQL.
 * In 'snapshot' mode: Fetches from static JSON files in /snapshot/*.json.
 * If 'live' fails (e.g. backend stopped), automatically falls back to snapshot.
 */

// Check both NEXT_PUBLIC_DATA_MODE and VITE_DATA_MODE
const PREFERRED_MODE = (
  import.meta.env.NEXT_PUBLIC_DATA_MODE ||
  import.meta.env.VITE_DATA_MODE ||
  'live'
).toLowerCase();

const API_BASE = import.meta.env.VITE_API_BASE_URL || import.meta.env.VITE_API_URL || 'http://localhost:5000/api';

let activeMode = PREFERRED_MODE;
let snapshotTimestamp = null;
let cachedSqlMap = null;

export function getDataMode() {
  return activeMode;
}

export function getSnapshotTimestamp() {
  return snapshotTimestamp;
}

// Indian Rupee formatting (e.g. ₹15,81,745.00)
export function formatINR(val, includeDecimals = true) {
  if (val === null || val === undefined || isNaN(val)) return '₹0.00';
  const num = Number(val);
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    maximumFractionDigits: includeDecimals ? 2 : 0,
    minimumFractionDigits: includeDecimals ? 2 : 0
  }).format(num);
}

// Compact Indian format (e.g. ₹1.58 Cr or ₹34.5 L)
export function formatINRCompact(val) {
  if (val === null || val === undefined || isNaN(val)) return '₹0';
  const num = Number(val);
  if (num >= 10000000) {
    return `₹${(num / 10000000).toFixed(2)} Cr`;
  }
  if (num >= 100000) {
    return `₹${(num / 100000).toFixed(2)} L`;
  }
  if (num >= 1000) {
    return `₹${(num / 1000).toFixed(1)} K`;
  }
  return `₹${num.toFixed(0)}`;
}

export function formatNumber(val) {
  if (val === null || val === undefined || isNaN(val)) return '0';
  return new Intl.NumberFormat('en-IN').format(Number(val));
}

export function formatPct(val) {
  if (val === null || val === undefined || isNaN(val)) return '0.0%';
  return `${Number(val).toFixed(2)}%`;
}

// Universal fetcher with snapshot fallback
async function requestData(endpoint, snapshotFile) {
  // If explicitly in snapshot mode, read snapshot JSON directly
  if (PREFERRED_MODE === 'snapshot') {
    return fetchSnapshot(snapshotFile);
  }

  // Live mode: try live API first
  try {
    const res = await fetch(`${API_BASE}${endpoint}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();
    if (!json.success) throw new Error(json.error || 'Request failed');
    activeMode = 'live';
    return json.data;
  } catch (err) {
    console.warn(`Live API error for ${endpoint}, falling back to snapshot:`, err.message);
    activeMode = 'snapshot';
    return fetchSnapshot(snapshotFile);
  }
}

async function fetchSnapshot(filename) {
  const res = await fetch(`/snapshot/${filename}.json`);
  if (!res.ok) throw new Error(`Failed to load snapshot ${filename}.json`);
  const json = await res.json();
  if (json.generated_at) {
    snapshotTimestamp = json.generated_at;
  }
  return json.data;
}

// API methods
export const api = {
  getOverview: () => requestData('/overview', 'overview'),
  getMonthlyRevenue: () => requestData('/revenue/monthly', 'revenue_monthly'),
  getFestival: () => requestData('/festival', 'festival'),
  getCustomersRFM: () => requestData('/customers/rfm', 'customers_rfm'),
  getCustomersChurn: () => requestData('/customers/churn', 'customers_churn'),
  getSellersReliability: () => requestData('/sellers/reliability', 'sellers_reliability'),
  getInventory: () => requestData('/inventory', 'inventory'),
  getReturns: () => requestData('/returns', 'returns'),
  getCategories: () => requestData('/categories', 'categories'),
  getRegions: () => requestData('/regions', 'regions'),
  getPayments: () => requestData('/payments', 'payments'),
  getTopCustomers: () => requestData('/top-customers', 'top_customers'),
  getTopProducts: () => requestData('/top-products', 'top_products'),
  getAcquisition: () => requestData('/acquisition', 'acquisition'),
  getTopSellers: () => requestData('/top-sellers', 'top_sellers'),

  // Get raw SQL definition for "View SQL" modal
  getQuerySql: async (queryId) => {
    let key = String(queryId).toLowerCase();
    if (/^\d+$/.test(key)) key = `q${key}`;

    const loadFromSnapshot = async () => {
      if (cachedSqlMap && (cachedSqlMap[key] || cachedSqlMap.queries?.[key])) {
        return cachedSqlMap.queries?.[key] || cachedSqlMap[key];
      }
      try {
        let res = await fetch('/snapshot/sql.json');
        if (!res.ok) res = await fetch('/snapshot/sql_queries.json');
        if (!res.ok) throw new Error('Snapshot SQL not available');
        const json = await res.json();
        cachedSqlMap = json;
        return json.queries?.[key] || json[key] || { id: key, title: `Query ${key}`, sql: '-- SQL query not found' };
      } catch (e) {
        return { id: key, title: `Query ${key}`, sql: '-- Snapshot SQL unavailable' };
      }
    };

    if (PREFERRED_MODE === 'snapshot') {
      return loadFromSnapshot();
    }

    try {
      const res = await fetch(`${API_BASE}/sql/${key}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const json = await res.json();
      return json;
    } catch (e) {
      // Fallback to snapshot sql file
      return loadFromSnapshot();
    }
  }
};

import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid
} from 'recharts';
import { api, formatINR, formatINRCompact, formatNumber, formatPct } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const PAYMENT_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#8b5cf6', '#ec4899'];

export default function RegionsPaymentsPage() {
  const [payments, setPayments] = useState([]);
  const [regionsData, setRegionsData] = useState({ regional_sales: [], payments_by_region: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getPayments(), api.getRegions()])
      .then(([payData, regData]) => {
        setPayments(payData);
        setRegionsData(regData || { regional_sales: [], payments_by_region: [] });
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Regional Sales & Payment Distribution..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  const regionalSales = regionsData.regional_sales || [];
  const paymentsByRegion = regionsData.payments_by_region || [];

  const paymentColumns = [
    { key: 'payment_method', label: 'Payment Method', sortable: true },
    { key: 'order_count', label: 'Order Volume', align: 'right', sortable: true },
    {
      key: 'total_revenue',
      label: 'Gross Revenue',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'order_pct',
      label: 'Order Volume %',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-semibold text-slate-300">{formatPct(v)}</span>
    },
    {
      key: 'revenue_pct',
      label: 'Revenue Share %',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-bold text-brand-400">{formatPct(v)}</span>
    },
    {
      key: 'avg_order_value',
      label: 'Avg Order Value',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    }
  ];

  const regionalColumns = [
    { key: 'region', label: 'Geographic Region', sortable: true },
    { key: 'total_orders', label: 'Active Orders', align: 'right', sortable: true },
    { key: 'unique_customers', label: 'Unique Buyers', align: 'right', sortable: true },
    {
      key: 'total_revenue',
      label: 'Active Revenue',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-bold text-emerald-400">{formatINR(v)}</span>
    },
    {
      key: 'avg_order_value',
      label: 'Avg Order Value',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'revenue_share_pct',
      label: 'National Revenue %',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-bold text-brand-400">{formatPct(v)}</span>
    }
  ];

  const regionalPaymentColumns = [
    { key: 'region', label: 'Region', sortable: true },
    { key: 'payment_method', label: 'Payment Method', sortable: true },
    { key: 'order_count', label: 'Orders', align: 'right', sortable: true },
    {
      key: 'revenue',
      label: 'Revenue',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'pct_within_region',
      label: 'Within-Region Share %',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-semibold text-brand-300">{formatPct(v)}</span>
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Regional Markets & Payment Preferences</h2>
          <p className="text-xs text-slate-400">
            National payment method distribution (Query 3), regional revenue performance (Query 4), and within-region payment partitions (Query 12)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="q3" title="Query 3: Payment Method Preferences" />
          <SqlViewerModal queryId="q4" title="Query 4: Regional Sales Performance" />
          <SqlViewerModal queryId="q12" title="Query 12: Payment Method by Region (PARTITION BY)" />
        </div>
      </div>

      {/* Regional Performance Cards (Query 4) */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        {regionalSales.map((r) => (
          <div key={r.region} className="p-4 rounded-xl bg-slate-850 border border-slate-800 shadow-sm">
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
              {r.region} India
            </span>
            <div className="text-xl font-bold font-mono text-emerald-400 mt-1">
              {formatINR(r.total_revenue, false)}
            </div>
            <div className="mt-2 text-xs text-slate-400 flex items-center justify-between">
              <span>{r.total_orders} active orders</span>
              <span className="font-mono text-brand-400 font-semibold">{r.revenue_share_pct}% share</span>
            </div>
          </div>
        ))}
      </div>

      {/* Query 3 National Payments Table & Pie */}
      <div className="p-5 rounded-xl bg-slate-850 border border-slate-800 shadow-sm">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 gap-2">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              National Payment Method Distribution (Query 3)
            </h3>
            <p className="text-xs text-slate-400">Window SUM() OVER() share calculation across all 334 orders</p>
          </div>
          <SqlViewerModal queryId="q3" title="Query 3: Payment Method Preferences" />
        </div>
        <div className="mt-4">
          <DataTable columns={paymentColumns} data={payments} searchable={false} pageSize={5} />
        </div>
      </div>

      {/* Query 4 Regional Sales Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Regional Sales Performance (Query 4)
            </h3>
            <p className="text-xs text-slate-400">
              Filtered on active orders NOT IN ('Cancelled','Returned') reconciling with net revenue
            </p>
          </div>
          <SqlViewerModal queryId="q4" title="Query 4: Regional Sales Performance" />
        </div>
        <DataTable
          columns={regionalColumns}
          data={regionalSales}
          searchable={false}
          pageSize={4}
        />
      </div>

      {/* Query 12 Regional Payment Partition Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Payment Preferences by Geographic Region (Query 12)
            </h3>
            <p className="text-xs text-slate-400">
              Within-region share calculated via window SUM(COUNT(*)) OVER (PARTITION BY region)
            </p>
          </div>
          <SqlViewerModal queryId="q12" title="Query 12: Regional Payment Preferences" />
        </div>
        <DataTable
          columns={regionalPaymentColumns}
          data={paymentsByRegion}
          defaultSortKey="region"
          pageSize={10}
        />
      </div>
    </div>
  );
}

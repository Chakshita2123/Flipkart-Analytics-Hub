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
import { api, formatINR, formatINRCompact, formatNumber } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

const SEGMENT_COLORS = {
  Champion: '#10b981', // emerald
  'Loyal Customer': '#3b82f6', // blue
  'Potential Loyalist': '#6366f1', // indigo
  'At Risk': '#f59e0b', // amber
  'Lost Customer': '#ef4444' // rose
};

export default function CustomersPage() {
  const [rfm, setRfm] = useState([]);
  const [topCustomers, setTopCustomers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getCustomersRFM(), api.getTopCustomers()])
      .then(([rfmData, topData]) => {
        setRfm(rfmData);
        setTopCustomers(topData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Customer RFM Segments & Top Customers..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  // Aggregate segment counts from RFM query results
  const segmentStats = {};
  rfm.forEach((row) => {
    const seg = row.customer_segment || 'Other';
    if (!segmentStats[seg]) {
      segmentStats[seg] = { name: seg, count: 0, totalSpend: 0 };
    }
    segmentStats[seg].count += 1;
    segmentStats[seg].totalSpend += Number(row.monetary || 0);
  });
  const segmentChartData = Object.values(segmentStats);

  const rfmColumns = [
    { key: 'user_id', label: 'ID', sortable: true },
    { key: 'username', label: 'Customer', sortable: true },
    { key: 'city', label: 'City', sortable: true },
    {
      key: 'user_type',
      label: 'Membership',
      sortable: true,
      render: (type) => (
        <span
          className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
            type === 'VIP'
              ? 'bg-purple-500/10 text-purple-400 border border-purple-500/20'
              : type === 'Premium'
              ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
              : 'bg-slate-800 text-slate-400'
          }`}
        >
          {type}
        </span>
      )
    },
    { key: 'recency_days', label: 'Recency (Days)', align: 'right', sortable: true },
    { key: 'frequency', label: 'Orders (F)', align: 'right', sortable: true },
    {
      key: 'monetary',
      label: 'Delivered Spend (M)',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'r_score',
      label: 'R-Tile',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono text-slate-400">{v}/5</span>
    },
    {
      key: 'f_score',
      label: 'F-Tile',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono text-slate-400">{v}/5</span>
    },
    {
      key: 'm_score',
      label: 'M-Tile',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono text-slate-400">{v}/5</span>
    },
    {
      key: 'rfm_avg_score',
      label: 'RFM Score',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-bold text-white">{v}</span>
    },
    {
      key: 'customer_segment',
      label: 'Segment',
      sortable: true,
      render: (seg) => {
        const color = SEGMENT_COLORS[seg] || '#94a3b8';
        return (
          <span
            className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[11px] font-medium"
            style={{ backgroundColor: `${color}15`, color, border: `1px solid ${color}30` }}
          >
            <span className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: color }} />
            {seg}
          </span>
        );
      }
    }
  ];

  const topCustomerColumns = [
    { key: 'user_id', label: 'User ID', sortable: true },
    { key: 'username', label: 'Customer Name', sortable: true },
    { key: 'city', label: 'City', sortable: true },
    { key: 'region', label: 'Region', sortable: true },
    { key: 'total_orders', label: 'Delivered Orders', align: 'right', sortable: true },
    {
      key: 'total_spending',
      label: 'Total Delivered Spend',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-bold text-emerald-400 font-mono">{formatINR(v)}</span>
    },
    {
      key: 'avg_order_value',
      label: 'Avg Order Value',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    { key: 'last_order_date', label: 'Last Order Date', align: 'right', sortable: true }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Customer Analytics & RFM Segmentation</h2>
          <p className="text-xs text-slate-400">
            Window NTILE(5) customer segmentation and top spender rankings powered by Query 7 and Query 1
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="q1" title="Query 1: Top 10 Customers by Total Spending" />
          <SqlViewerModal queryId="q7" title="Query 7: Customer Lifetime Value - RFM Analysis (NTILE 5)" />
        </div>
      </div>

      {/* Segment Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-5 gap-3">
        {segmentChartData.map((seg) => {
          const color = SEGMENT_COLORS[seg.name] || '#94a3b8';
          const avgSpend = seg.count > 0 ? seg.totalSpend / seg.count : 0;
          return (
            <div
              key={seg.name}
              className="p-3.5 rounded-xl bg-slate-850 border border-slate-800 shadow-sm"
              style={{ borderTop: `3px solid ${color}` }}
            >
              <span className="text-[11px] font-semibold text-slate-300 block">{seg.name}</span>
              <div className="text-xl font-bold font-mono text-white mt-1">{seg.count} buyers</div>
              <div className="text-[11px] text-slate-400 mt-1">Avg: {formatINRCompact(avgSpend)}</div>
            </div>
          );
        })}
      </div>

      {/* Top 10 Customers (Query 1) */}
      <div className="p-5 rounded-xl bg-slate-850 border border-slate-800 shadow-sm">
        <div className="flex items-center justify-between pb-3 border-b border-slate-800 gap-2">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">Top 10 High-Value Customers (Query 1)</h3>
            <p className="text-xs text-slate-400">Ranked by total delivered revenue</p>
          </div>
          <SqlViewerModal queryId="q1" title="Query 1: Top 10 Customers by Total Spending" />
        </div>
        <div className="mt-4">
          <DataTable columns={topCustomerColumns} data={topCustomers} searchable={false} pageSize={10} />
        </div>
      </div>

      {/* Full RFM Table (Query 7) */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              RFM Segmentation Matrix (Query 7)
            </h3>
            <p className="text-xs text-slate-400">
              All 90 delivered customers classified into NTILE(5) tiles for Recency, Frequency, and Monetary
            </p>
          </div>
          <SqlViewerModal queryId="q7" title="Query 7: Customer Lifetime Value - RFM Analysis (NTILE 5)" />
        </div>
        <DataTable
          columns={rfmColumns}
          data={rfm}
          defaultSortKey="rfm_avg_score"
          defaultSortDir="desc"
          pageSize={10}
        />
      </div>
    </div>
  );
}

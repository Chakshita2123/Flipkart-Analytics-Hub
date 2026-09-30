import React, { useEffect, useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';
import { api, formatINR, formatINRCompact, formatNumber, formatPct } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function RevenuePage() {
  const [monthly, setMonthly] = useState([]);
  const [festival, setFestival] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getMonthlyRevenue(), api.getFestival()])
      .then(([moData, festData]) => {
        setMonthly(moData);
        setFestival(festData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Revenue & Festival Trends..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  const monthlyColumns = [
    { key: 'order_month', label: 'Month', sortable: true },
    { key: 'orders_placed', label: 'Orders Placed', align: 'right', sortable: true },
    {
      key: 'monthly_revenue',
      label: 'Monthly Revenue',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    { key: 'unique_customers', label: 'Unique Buyers', align: 'right', sortable: true },
    {
      key: 'prev_month_revenue',
      label: 'Prior Month',
      align: 'right',
      render: (v) => (v ? formatINR(v) : '-')
    },
    {
      key: 'mom_growth_pct',
      label: 'MoM Growth',
      align: 'right',
      sortable: true,
      render: (v) => {
        if (v === null || v === undefined) return <span className="text-slate-500">Base</span>;
        const num = Number(v);
        return (
          <span className={`font-semibold ${num >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            {num >= 0 ? '+' : ''}{num}%
          </span>
        );
      }
    },
    {
      key: 'cumulative_revenue',
      label: 'Cumulative Revenue',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    }
  ];

  const festivalColumns = [
    { key: 'sale_month', label: 'Month', sortable: true },
    {
      key: 'festival_tag',
      label: 'Festival / Campaign',
      sortable: true,
      render: (tag) => {
        const isFestive = tag !== 'Regular Month';
        return (
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium ${
              isFestive
                ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                : 'bg-slate-800 text-slate-400'
            }`}
          >
            {tag}
          </span>
        );
      }
    },
    { key: 'total_orders', label: 'Orders', align: 'right', sortable: true },
    {
      key: 'total_revenue',
      label: 'Revenue',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    { key: 'active_customers', label: 'Active Users', align: 'right', sortable: true },
    {
      key: 'avg_order_value',
      label: 'Avg Order Value',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Revenue & Festival Dynamics</h2>
          <p className="text-xs text-slate-400">
            Window LAG() growth tracking and festival campaign volume spikes (Big Billion Days, Diwali, Republic Day)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="q8" title="Query 8: Monthly Revenue Trends (LAG & Cumulative)" />
          <SqlViewerModal queryId="q11" title="Query 11: Festival Season Sales Patterns" />
        </div>
      </div>

      {/* Festival Sales Comparison Chart */}
      <div className="p-5 rounded-xl bg-slate-850 border border-slate-800 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-2">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-slate-200">Festival vs Regular Monthly Revenue</h3>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-amber-500/10 text-amber-400">
                Campaign Impact
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Highlighting major Indian festive spikes: Oct (Navratri/BBD ₹5.01M), Nov (Diwali ₹4.85M), Jan (Republic Day ₹4.12M), Aug (Independence Day ₹2.62M)
            </p>
          </div>
          <SqlViewerModal queryId="q11" title="Query 11: Festival Season Sales Patterns" />
        </div>

        <div className="h-72 mt-4 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={festival} margin={{ top: 10, right: 10, left: 15, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis
                dataKey="sale_month"
                stroke="#64748b"
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                tickLine={false}
              />
              <YAxis
                stroke="#64748b"
                tick={{ fill: '#94a3b8', fontSize: 11 }}
                tickFormatter={(val) => formatINRCompact(val)}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip
                content={({ active, payload }) => {
                  if (active && payload && payload.length) {
                    const row = payload[0].payload;
                    return (
                      <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 shadow-xl text-xs space-y-1">
                        <div className="font-semibold text-slate-200">
                          {row.month_name} ({row.sale_month})
                        </div>
                        <div className="text-amber-400 font-medium">{row.festival_tag}</div>
                        <div className="text-brand-400 font-mono">
                          Revenue: {formatINR(row.total_revenue)}
                        </div>
                        <div className="text-slate-400">
                          Orders: <span className="font-mono text-slate-200">{row.total_orders}</span>
                        </div>
                        <div className="text-slate-400">
                          Avg Order Value: <span className="font-mono text-slate-200">{formatINR(row.avg_order_value)}</span>
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Bar dataKey="total_revenue" fill="#3b82f6" radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Query 11 Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-200">Festival Campaign Breakdown (Query 11)</h3>
          <SqlViewerModal queryId="q11" title="Query 11: Festival Season Sales Patterns" />
        </div>
        <DataTable columns={festivalColumns} data={festival} defaultSortKey="sale_month" pageSize={12} />
      </div>

      {/* Query 8 Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-sm font-semibold text-slate-200">
            Month-over-Month Revenue & LAG() Window Analysis (Query 8)
          </h3>
          <SqlViewerModal queryId="q8" title="Query 8: Monthly Revenue Trends (LAG & Cumulative)" />
        </div>
        <DataTable columns={monthlyColumns} data={monthly} defaultSortKey="order_month" pageSize={12} />
      </div>
    </div>
  );
}

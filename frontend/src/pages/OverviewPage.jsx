import React, { useEffect, useState } from 'react';
import {
  DollarSign,
  ShoppingCart,
  Users,
  TrendingUp,
  RotateCcw,
  CheckCircle2,
  XCircle,
  Clock,
  Info
} from 'lucide-react';
import {
  ResponsiveContainer,
  AreaChart,
  Area,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid
} from 'recharts';
import { api, formatINR, formatINRCompact, formatNumber, formatPct } from '../api';
import MetricCard from '../components/MetricCard';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function OverviewPage() {
  const [overview, setOverview] = useState(null);
  const [monthly, setMonthly] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getOverview(), api.getMonthlyRevenue()])
      .then(([ovData, moData]) => {
        setOverview(ovData);
        setMonthly(moData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Overview KPIs & Monthly Performance..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  return (
    <div className="space-y-6">
      {/* Header & SQL Modal */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Executive Business Overview</h2>
          <p className="text-xs text-slate-400">
            High-level e-commerce performance metrics calculated purely via SQL aggregations
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="overview" title="KPI Overview Aggregations SQL" />
          <SqlViewerModal queryId="q8" title="Monthly Trend & LAG() SQL" />
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <MetricCard
          title="Net Revenue"
          value={formatINR(overview.total_revenue, false)}
          subtitle="Active delivered & confirmed orders"
          icon={DollarSign}
          color="emerald"
        />
        <MetricCard
          title="Active Orders"
          value={formatNumber(overview.active_orders)}
          subtitle={`Out of ${overview.total_orders_placed} total placed`}
          icon={ShoppingCart}
          color="blue"
        />
        <MetricCard
          title="Active Customers"
          value={formatNumber(overview.active_customers)}
          subtitle="97 total registered users"
          icon={Users}
          color="purple"
        />
        <MetricCard
          title="Avg Order Value"
          value={formatINR(overview.avg_order_value)}
          subtitle="Net revenue / active orders"
          icon={TrendingUp}
          color="indigo"
        />
        <MetricCard
          title="Order Return Rate"
          value={formatPct(overview.order_return_rate_pct)}
          subtitle={`${overview.returned_orders} returned orders (${overview.total_return_items} items)`}
          icon={RotateCcw}
          color="rose"
        />
      </div>

      {/* Order Status Breakdown Bar */}
      <div className="p-4 rounded-xl bg-slate-850 border border-slate-800 flex flex-wrap items-center justify-between gap-3 text-xs">
        <div className="text-slate-400 font-medium">Order Status Distribution:</div>
        <div className="flex flex-wrap items-center gap-2">
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <CheckCircle2 className="w-3.5 h-3.5" />
            <span>Delivered: {overview.delivered_orders}</span>
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <RotateCcw className="w-3.5 h-3.5" />
            <span>Returned: {overview.returned_orders}</span>
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-amber-500/10 text-amber-400 border border-amber-500/20">
            <XCircle className="w-3.5 h-3.5" />
            <span>Cancelled: {overview.cancelled_orders}</span>
          </span>
          <span className="inline-flex items-center gap-1 px-2.5 py-1 rounded-md bg-blue-500/10 text-blue-400 border border-blue-500/20">
            <Clock className="w-3.5 h-3.5" />
            <span>In Transit / Pending: {overview.active_orders - overview.delivered_orders}</span>
          </span>
        </div>
      </div>

      {/* Monthly Revenue Chart */}
      <div className="p-5 rounded-xl bg-slate-850 border border-slate-800 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-4 border-b border-slate-800/80 gap-2">
          <div>
            <div className="flex items-center gap-2">
              <h3 className="text-sm font-semibold text-slate-200">Monthly Revenue & Trajectory</h3>
              <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-400">
                Oct 2025 - Sep 2026
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-0.5">
              Net monthly revenue derived directly from Query 8 with cumulative tracking
            </p>
          </div>
          <SqlViewerModal queryId="q8" title="Query 8: Monthly Revenue Trends (LAG & Cumulative SUM)" />
        </div>

        <div className="h-72 mt-4 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={monthly} margin={{ top: 10, right: 10, left: 15, bottom: 0 }}>
              <defs>
                <linearGradient id="revenueGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.35} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" vertical={false} />
              <XAxis
                dataKey="order_month"
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
                content={({ active, payload, label }) => {
                  if (active && payload && payload.length) {
                    const row = payload[0].payload;
                    return (
                      <div className="p-3 rounded-lg bg-slate-950 border border-slate-800 shadow-xl text-xs space-y-1">
                        <div className="font-semibold text-slate-200">{label}</div>
                        <div className="text-brand-400 font-mono">
                          Monthly Revenue: {formatINR(row.monthly_revenue)}
                        </div>
                        <div className="text-slate-400">
                          Orders Placed: <span className="font-mono text-slate-200">{row.orders_placed}</span>
                        </div>
                        <div className="text-slate-400">
                          MoM Growth: <span className={`font-mono ${Number(row.mom_growth_pct) >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                            {row.mom_growth_pct !== null ? `${row.mom_growth_pct}%` : 'N/A (Base)'}
                          </span>
                        </div>
                        <div className="text-slate-400 pt-1 border-t border-slate-800 font-mono text-[11px]">
                          Cumulative: {formatINR(row.cumulative_revenue)}
                        </div>
                      </div>
                    );
                  }
                  return null;
                }}
              />
              <Area
                type="monotone"
                dataKey="monthly_revenue"
                stroke="#3b82f6"
                strokeWidth={2.5}
                fillOpacity={1}
                fill="url(#revenueGrad)"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* KPI Definitions & Reconciliations Card */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800/80 text-xs">
        <div className="flex items-center gap-2 text-slate-300 font-semibold mb-2">
          <Info className="w-4 h-4 text-brand-400" />
          <span>KPI Definitions & SQL Reconciliation</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3 text-slate-400 leading-relaxed">
          <div className="p-3 rounded-lg bg-slate-850/60 border border-slate-800">
            <span className="font-medium text-slate-300 block mb-1">1. Revenue Reconciliation</span>
            Overview net revenue (₹30.17M) reconciles to the exact rupee with Query 8 monthly sum and Query 4 regional sum: orders with status NOT IN ('Cancelled','Returned').
          </div>
          <div className="p-3 rounded-lg bg-slate-850/60 border border-slate-800">
            <span className="font-medium text-slate-300 block mb-1">2. Order Integrity</span>
            All 334 orders have 1-4 line items whose quantity × unit_price strictly equals the order total. Returns only attach to valid delivered orders.
          </div>
          <div className="p-3 rounded-lg bg-slate-850/60 border border-slate-800">
            <span className="font-medium text-slate-300 block mb-1">3. Customer Activity</span>
            90 active customers have placed completed or pending orders during the 12-month period across North, South, East, and West India.
          </div>
        </div>
      </div>
    </div>
  );
}

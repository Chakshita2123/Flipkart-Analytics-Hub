import React, { useEffect, useState } from 'react';
import { api, formatINR, formatNumber } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function ChurnAcquisitionPage() {
  const [churn, setChurn] = useState([]);
  const [acquisition, setAcquisition] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getCustomersChurn(), api.getAcquisition()])
      .then(([churnData, acqData]) => {
        setChurn(churnData);
        setAcquisition(acqData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Churn Cohorts & Acquisition Analysis..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  // Churn cohorts counts
  const churnSummary = {
    'Early Churn Risk': churn.filter((c) => c.churn_status === 'Early Churn Risk').length,
    Churning: churn.filter((c) => c.churn_status === 'Churning').length,
    Churned: churn.filter((c) => c.churn_status === 'Churned').length
  };

  const churnColumns = [
    { key: 'user_id', label: 'ID', sortable: true },
    { key: 'username', label: 'Customer', sortable: true },
    { key: 'email', label: 'Email', sortable: true },
    { key: 'city', label: 'City', sortable: true },
    { key: 'region', label: 'Region', sortable: true },
    {
      key: 'user_type',
      label: 'Tier',
      sortable: true,
      render: (t) => (
        <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-800 text-slate-300">
          {t}
        </span>
      )
    },
    { key: 'last_purchase_date', label: 'Last Purchase Date', sortable: true },
    {
      key: 'days_since_last_purchase',
      label: 'Days Inactive',
      align: 'right',
      sortable: true,
      render: (days) => <span className="font-mono font-bold text-slate-200">{days}d</span>
    },
    { key: 'lifetime_orders', label: 'Orders', align: 'right', sortable: true },
    {
      key: 'lifetime_value',
      label: 'Lifetime Value',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'churn_status',
      label: 'Cohort',
      sortable: true,
      render: (status) => {
        const isCritical = status === 'Churned';
        const isMedium = status === 'Churning';
        return (
          <span
            className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] font-medium ${
              isCritical
                ? 'bg-rose-500/10 text-rose-400 border border-rose-500/20'
                : isMedium
                ? 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                : 'bg-yellow-500/10 text-yellow-300 border border-yellow-500/20'
            }`}
          >
            {status}
          </span>
        );
      }
    }
  ];

  const acqColumns = [
    { key: 'user_id', label: 'ID', sortable: true },
    { key: 'username', label: 'Customer', sortable: true },
    { key: 'signup_date', label: 'Sign-up Date', sortable: true },
    { key: 'first_order_date', label: 'First Order', sortable: true },
    {
      key: 'days_to_first_purchase',
      label: 'Days to Convert',
      align: 'right',
      sortable: true,
      render: (d) => <span className="font-mono text-brand-400 font-semibold">{d}d</span>
    },
    {
      key: 'first_order_value',
      label: '1st Order Spend',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    { key: 'total_orders', label: 'Orders', align: 'right', sortable: true },
    {
      key: 'total_clv',
      label: 'Total CLV',
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
    {
      key: 'acquisition_type',
      label: 'Conversion Speed',
      sortable: true,
      render: (type) => (
        <span className="text-[11px] px-2 py-0.5 rounded bg-slate-800 text-slate-300 font-medium">
          {type}
        </span>
      )
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Customer Retention & Conversion Lifecycle</h2>
          <p className="text-xs text-slate-400">
            60-day silence churn cohorts (Query 9) and time-to-first-purchase customer lifetime value (Query 14)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="q9" title="Query 9: Churn Analysis (60+ Days Inactive)" />
          <SqlViewerModal queryId="q14" title="Query 14: Time-to-First-Purchase & Customer Lifetime Value" />
        </div>
      </div>

      {/* Churn Cohort Summary Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-850 border border-yellow-500/20 shadow-sm">
          <span className="text-xs uppercase font-medium tracking-wider text-yellow-400">
            Early Churn Risk (60-90 Days)
          </span>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            {churnSummary['Early Churn Risk']} customers
          </div>
          <p className="text-xs text-slate-400 mt-1">Prime re-engagement window before habit breaks</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-amber-500/20 shadow-sm">
          <span className="text-xs uppercase font-medium tracking-wider text-amber-400">
            Churning (91-180 Days)
          </span>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            {churnSummary['Churning']} customers
          </div>
          <p className="text-xs text-slate-400 mt-1">Dormant segment requiring targeted incentives</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-rose-500/20 shadow-sm">
          <span className="text-xs uppercase font-medium tracking-wider text-rose-400">
            Churned (&gt; 180 Days)
          </span>
          <div className="text-2xl font-bold font-mono text-white mt-1">
            {churnSummary['Churned']} customers
          </div>
          <p className="text-xs text-slate-400 mt-1">Inactive for over half a year</p>
        </div>
      </div>

      {/* Query 9 Churn Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Customers Inactive for 60+ Days (Query 9)
            </h3>
            <p className="text-xs text-slate-400">
              Calculated using DATEDIFF(@as_of, MAX(order_date)) excluding cancelled orders
            </p>
          </div>
          <SqlViewerModal queryId="q9" title="Query 9: Churn Analysis (DATEDIFF & HAVING)" />
        </div>
        <DataTable
          columns={churnColumns}
          data={churn}
          defaultSortKey="days_since_last_purchase"
          defaultSortDir="desc"
          pageSize={10}
        />
      </div>

      {/* Query 14 Acquisition Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Time-to-First-Purchase & Customer Lifetime Value (Query 14)
            </h3>
            <p className="text-xs text-slate-400">
              Chained CTEs with MIN() earliest order aggregation ensuring zero fan-out
            </p>
          </div>
          <SqlViewerModal queryId="q14" title="Query 14: Time-to-First-Purchase & CLV (Chained CTEs)" />
        </div>
        <DataTable
          columns={acqColumns}
          data={acquisition}
          defaultSortKey="total_clv"
          defaultSortDir="desc"
          pageSize={10}
        />
      </div>
    </div>
  );
}

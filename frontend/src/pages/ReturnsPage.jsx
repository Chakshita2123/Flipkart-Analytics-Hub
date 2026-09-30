import React, { useEffect, useState } from 'react';
import { AlertOctagon, CheckCircle2, ShieldAlert } from 'lucide-react';
import { api, formatPct } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function ReturnsPage() {
  const [returnsData, setReturnsData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    api.getReturns()
      .then((data) => setReturnsData(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Aggregating Return Reasons & Risk Flags..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  const highRiskCount = returnsData.filter((r) => r.return_health_flag.includes('HIGH RISK')).length;
  const moderateCount = returnsData.filter((r) => r.return_health_flag.includes('MODERATE')).length;
  const healthyCount = returnsData.filter((r) => r.return_health_flag === 'HEALTHY').length;

  const returnsColumns = [
    { key: 'product_id', label: 'ID', sortable: true },
    { key: 'product_name', label: 'Product Name', sortable: true },
    { key: 'category_name', label: 'Category', sortable: true },
    { key: 'total_orders', label: 'Orders Placed', align: 'right', sortable: true },
    { key: 'total_returns', label: 'Returns Logged', align: 'right', sortable: true },
    {
      key: 'return_rate_pct',
      label: 'Return Rate (%)',
      align: 'right',
      sortable: true,
      render: (v) => {
        const num = Number(v);
        return (
          <span
            className={`font-mono font-bold text-xs ${
              num > 15 ? 'text-rose-400' : num > 5 ? 'text-amber-400' : 'text-emerald-400'
            }`}
          >
            {formatPct(v)}
          </span>
        );
      }
    },
    {
      key: 'return_health_flag',
      label: 'Health Classification',
      sortable: true,
      render: (flag) => {
        let style = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
        if (flag.includes('HIGH RISK')) style = 'bg-rose-500/10 text-rose-400 border-rose-500/30 font-bold';
        else if (flag.includes('MODERATE')) style = 'bg-amber-500/10 text-amber-400 border-amber-500/30';

        return (
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] border font-medium ${style}`}>
            {flag}
          </span>
        );
      }
    },
    {
      key: 'return_reasons',
      label: 'Customer Return Reasons (GROUP_CONCAT)',
      sortable: false,
      render: (reasons) => (
        <span className="text-[11px] text-slate-400 font-mono truncate block max-w-xs" title={reasons}>
          {reasons || 'None'}
        </span>
      )
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Product Return Rates & Root-Cause Analysis</h2>
          <p className="text-xs text-slate-400">
            CTE pre-aggregation preventing join fan-out with string GROUP_CONCAT reason aggregation (Query 6)
          </p>
        </div>
        <SqlViewerModal queryId="q6" title="Query 6: Product Return Analysis & Return Rates" />
      </div>

      {/* Summary KPI Badges */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-slate-850 border border-rose-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-rose-400">High Risk (&gt; 15% Returns)</span>
            <ShieldAlert className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{highRiskCount} products</div>
          <p className="text-[11px] text-slate-400 mt-1">Requires immediate supplier or packaging review</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-amber-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-amber-400">Moderate Risk (5-15%)</span>
            <AlertOctagon className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{moderateCount} products</div>
          <p className="text-[11px] text-slate-400 mt-1">Monitor for customer feedback trends</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-emerald-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-emerald-400">Healthy (&le; 5%)</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{healthyCount} products</div>
          <p className="text-[11px] text-slate-400 mt-1">Low return incidence</p>
        </div>
      </div>

      {/* Query 6 Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Product Return Health Matrix (Query 6)
            </h3>
            <p className="text-xs text-slate-400">
              Pre-aggregated in CTE returns_agg to prevent multiplication of order items
            </p>
          </div>
          <SqlViewerModal queryId="q6" title="Query 6: Product Return Analysis" />
        </div>
        <DataTable
          columns={returnsColumns}
          data={returnsData}
          defaultSortKey="return_rate_pct"
          defaultSortDir="desc"
          pageSize={10}
        />
      </div>
    </div>
  );
}

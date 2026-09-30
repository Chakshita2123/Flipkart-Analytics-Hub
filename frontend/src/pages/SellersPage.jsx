import React, { useEffect, useState } from 'react';
import { api, formatINR, formatPct } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function SellersPage() {
  const [topSellers, setTopSellers] = useState([]);
  const [reliability, setReliability] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getTopSellers(), api.getSellersReliability()])
      .then(([sellersData, relData]) => {
        setTopSellers(sellersData);
        setReliability(relData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Seller Ratings & Reliability Metrics..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  const topSellersColumns = [
    { key: 'seller_id', label: 'ID', sortable: true },
    { key: 'seller_name', label: 'Seller Name', sortable: true },
    {
      key: 'seller_rating',
      label: 'Rating',
      align: 'right',
      sortable: true,
      render: (r) => <span className="font-mono text-amber-400 font-bold">★ {Number(r).toFixed(2)}</span>
    },
    { key: 'total_products', label: 'Catalog Size', align: 'right', sortable: true },
    { key: 'total_orders_fulfilled', label: 'Orders Fulfilled', align: 'right', sortable: true },
    {
      key: 'gross_revenue',
      label: 'Gross Revenue',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono text-emerald-400 font-bold">{formatINR(v)}</span>
    },
    {
      key: 'avg_selling_price',
      label: 'Avg Price',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'composite_score',
      label: 'Composite Score (0-1)',
      align: 'right',
      sortable: true,
      render: (s) => (
        <span className="font-mono font-bold text-brand-400 bg-brand-500/10 px-2 py-0.5 rounded border border-brand-500/20">
          {Number(s).toFixed(4)}
        </span>
      )
    }
  ];

  const reliabilityColumns = [
    { key: 'seller_id', label: 'ID', sortable: true },
    { key: 'seller_name', label: 'Seller Name', sortable: true },
    {
      key: 'platform_rating',
      label: 'Base Rating',
      align: 'right',
      sortable: true,
      render: (r) => <span className="font-mono text-amber-400">★ {r}</span>
    },
    { key: 'total_orders', label: 'Total Orders', align: 'right', sortable: true },
    { key: 'cancelled_orders', label: 'Cancelled', align: 'right', sortable: true },
    {
      key: 'cancel_rate_pct',
      label: 'Cancel %',
      align: 'right',
      sortable: true,
      render: (v) => {
        const num = Number(v);
        return (
          <span className={`font-mono ${num > 10 ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>
            {formatPct(v)}
          </span>
        );
      }
    },
    { key: 'returned_orders', label: 'Returned', align: 'right', sortable: true },
    {
      key: 'return_rate_pct',
      label: 'Return %',
      align: 'right',
      sortable: true,
      render: (v) => {
        const num = Number(v);
        return (
          <span className={`font-mono ${num > 10 ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>
            {formatPct(v)}
          </span>
        );
      }
    },
    { key: 'review_count', label: 'Reviews', align: 'right', sortable: true },
    {
      key: 'avg_review_rating',
      label: 'Customer Review',
      align: 'right',
      sortable: true,
      render: (v) => (v > 0 ? `★ ${v}` : 'No reviews')
    },
    {
      key: 'reliability_score',
      label: 'Reliability Score (0-100)',
      align: 'right',
      sortable: true,
      render: (score) => {
        const num = Number(score);
        return (
          <span
            className={`font-mono font-bold px-2 py-0.5 rounded text-xs ${
              num >= 90
                ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20'
                : num >= 80
                ? 'bg-blue-500/10 text-blue-400 border border-blue-500/20'
                : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
            }`}
          >
            {num.toFixed(2)}
          </span>
        );
      }
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Seller Performance & Quality Benchmarks</h2>
          <p className="text-xs text-slate-400">
            Multi-factor composite scoring (Query 5) and weighted reliability indices (Query 13)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="q5" title="Query 5: Top Sellers Composite Score" />
          <SqlViewerModal queryId="q13" title="Query 13: Seller Reliability Score (Weighted 0-100)" />
        </div>
      </div>

      {/* Query 13 Reliability Scoring Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Seller Reliability Matrix (Query 13)
            </h3>
            <p className="text-xs text-slate-400">
              Weighted formula: Reviews (40%) + Low Cancellations (30%) + Low Returns (20%) + Platform Rating (10%)
            </p>
          </div>
          <SqlViewerModal queryId="q13" title="Query 13: Seller Reliability Score (Weighted 0-100)" />
        </div>
        <DataTable
          columns={reliabilityColumns}
          data={reliability}
          defaultSortKey="reliability_score"
          defaultSortDir="desc"
          pageSize={10}
        />
      </div>

      {/* Query 5 Top Sellers Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Seller Revenue & Composite Rating (Query 5)
            </h3>
            <p className="text-xs text-slate-400">
              Normalised rating (40%) and revenue vs top seller (60%) via MAX() OVER()
            </p>
          </div>
          <SqlViewerModal queryId="q5" title="Query 5: Top Sellers by Rating & Revenue" />
        </div>
        <DataTable
          columns={topSellersColumns}
          data={topSellers}
          defaultSortKey="composite_score"
          defaultSortDir="desc"
          pageSize={10}
        />
      </div>
    </div>
  );
}

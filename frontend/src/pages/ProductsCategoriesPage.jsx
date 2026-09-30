import React, { useEffect, useState } from 'react';
import { api, formatINR, formatPct } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function ProductsCategoriesPage() {
  const [topProducts, setTopProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    Promise.all([api.getTopProducts(), api.getCategories()])
      .then(([prodData, catData]) => {
        setTopProducts(prodData);
        setCategories(catData);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Loading Products & Category Performance..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  const categoryColumns = [
    { key: 'category_name', label: 'Category', sortable: true },
    { key: 'subcategory', label: 'Subcategory', sortable: true },
    { key: 'product_count', label: 'Products', align: 'right', sortable: true },
    { key: 'units_sold', label: 'Units Sold', align: 'right', sortable: true },
    {
      key: 'gross_revenue',
      label: 'Gross Revenue',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono text-emerald-400 font-bold">{formatINR(v)}</span>
    },
    {
      key: 'avg_product_price',
      label: 'Avg Price',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'avg_product_rating',
      label: 'Avg Rating',
      align: 'right',
      sortable: true,
      render: (r) => <span className="font-mono text-amber-400">★ {r}</span>
    },
    { key: 'total_returns', label: 'Returned Items', align: 'right', sortable: true },
    {
      key: 'return_rate_pct',
      label: 'Return Rate',
      align: 'right',
      sortable: true,
      render: (v) => {
        const num = Number(v);
        return (
          <span className={`font-mono ${num > 3.5 ? 'text-rose-400 font-bold' : 'text-slate-300'}`}>
            {formatPct(v)}
          </span>
        );
      }
    }
  ];

  const productColumns = [
    {
      key: 'category_rank',
      label: 'Rank',
      align: 'right',
      sortable: true,
      render: (r) => (
        <span
          className={`font-mono font-bold text-xs px-2 py-0.5 rounded ${
            r === 1 ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' : 'text-slate-400'
          }`}
        >
          #{r}
        </span>
      )
    },
    { key: 'category_name', label: 'Category', sortable: true },
    { key: 'subcategory', label: 'Subcategory', sortable: true },
    { key: 'product_name', label: 'Product Name', sortable: true },
    { key: 'units_sold', label: 'Units Sold', align: 'right', sortable: true },
    {
      key: 'total_revenue',
      label: 'Delivered Revenue',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono font-semibold text-slate-200">{formatINR(v)}</span>
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Products & Category Analytics</h2>
          <p className="text-xs text-slate-400">
            Window RANK() partition by category (Query 2) and aggregated category performance with return rate (Query 10)
          </p>
        </div>
        <div className="flex items-center gap-2">
          <SqlViewerModal queryId="q2" title="Query 2: Best-Selling Products by Category (Window RANK)" />
          <SqlViewerModal queryId="q10" title="Query 10: Category Performance Metrics (CTE Pre-aggregation)" />
        </div>
      </div>

      {/* Query 10 Category Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Category & Subcategory Breakdown (Query 10)
            </h3>
            <p className="text-xs text-slate-400">
              CTE pre-aggregation eliminates return fan-out duplication across categories
            </p>
          </div>
          <SqlViewerModal queryId="q10" title="Query 10: Category Performance Metrics" />
        </div>
        <DataTable
          columns={categoryColumns}
          data={categories}
          defaultSortKey="gross_revenue"
          defaultSortDir="desc"
          pageSize={12}
        />
      </div>

      {/* Query 2 Best Sellers Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Category Best Sellers (Query 2)
            </h3>
            <p className="text-xs text-slate-400">
              Ranked within each category using RANK() OVER (PARTITION BY category_name ORDER BY SUM(quantity) DESC)
            </p>
          </div>
          <SqlViewerModal queryId="q2" title="Query 2: Best-Selling Products (RANK OVER PARTITION)" />
        </div>
        <DataTable
          columns={productColumns}
          data={topProducts}
          defaultSortKey="category_rank"
          defaultSortDir="asc"
          pageSize={10}
        />
      </div>
    </div>
  );
}

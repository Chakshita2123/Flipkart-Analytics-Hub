import React, { useEffect, useState } from 'react';
import { AlertTriangle, AlertCircle, CheckCircle, PackageOpen } from 'lucide-react';
import { api, formatINR, formatNumber } from '../api';
import DataTable from '../components/DataTable';
import SqlViewerModal from '../components/SqlViewerModal';
import LoadingState from '../components/LoadingState';
import ErrorState from '../components/ErrorState';

export default function InventoryPage() {
  const [inventory, setInventory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const loadData = () => {
    setLoading(true);
    setError(null);
    api.getInventory()
      .then((data) => setInventory(data))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => {
    loadData();
  }, []);

  if (loading) return <LoadingState message="Calculating Stock Velocity & Reorder Priorities..." />;
  if (error) return <ErrorState error={error} onRetry={loadData} />;

  // Health categories summary
  const summary = {
    critical: inventory.filter((i) => i.stock_health.includes('CRITICAL')).length,
    low: inventory.filter((i) => i.stock_health.includes('LOW STOCK')).length,
    healthy: inventory.filter((i) => i.stock_health === 'HEALTHY').length,
    overstocked: inventory.filter((i) => i.stock_health.includes('OVERSTOCKED')).length,
    totalValue: inventory.reduce((sum, i) => sum + Number(i.inventory_value_inr || 0), 0)
  };

  const inventoryColumns = [
    { key: 'product_id', label: 'ID', sortable: true },
    { key: 'product_name', label: 'Product Name', sortable: true },
    { key: 'category_name', label: 'Category', sortable: true },
    { key: 'seller_name', label: 'Seller', sortable: true },
    {
      key: 'price',
      label: 'Price',
      align: 'right',
      sortable: true,
      render: (v) => formatINR(v)
    },
    {
      key: 'current_stock',
      label: 'Current Stock',
      align: 'right',
      sortable: true,
      render: (s) => <span className="font-mono font-bold text-white">{s} units</span>
    },
    { key: 'total_units_sold', label: 'Units Sold (24w)', align: 'right', sortable: true },
    {
      key: 'estimated_weeks_of_stock',
      label: 'Runway (Weeks)',
      align: 'right',
      sortable: true,
      render: (w) => (w !== null ? <span className="font-mono">{w}w</span> : 'N/A')
    },
    {
      key: 'stock_health',
      label: 'Health Flag',
      sortable: true,
      render: (status) => {
        let style = 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20';
        if (status.includes('CRITICAL')) style = 'bg-rose-500/10 text-rose-400 border-rose-500/30 font-bold';
        else if (status.includes('LOW STOCK')) style = 'bg-amber-500/10 text-amber-400 border-amber-500/30';
        else if (status.includes('OVERSTOCKED')) style = 'bg-purple-500/10 text-purple-400 border-purple-500/30';

        return (
          <span className={`inline-flex items-center px-2 py-0.5 rounded text-[11px] border font-medium ${style}`}>
            {status}
          </span>
        );
      }
    },
    {
      key: 'inventory_value_inr',
      label: 'Holding Value',
      align: 'right',
      sortable: true,
      render: (v) => <span className="font-mono text-slate-300 font-semibold">{formatINR(v)}</span>
    }
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-2 border-b border-slate-800">
        <div>
          <h2 className="text-lg font-bold text-white tracking-tight">Inventory Health & Stock Velocity</h2>
          <p className="text-xs text-slate-400">
            Automated stock velocity and replenishment priority sorting via SQL FIELD() (Query 15)
          </p>
        </div>
        <SqlViewerModal queryId="q15" title="Query 15: Inventory Health Check & Restocking Priority" />
      </div>

      {/* Summary KPI Badges */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-850 border border-rose-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-rose-400">Critical Reorder</span>
            <AlertCircle className="w-4 h-4 text-rose-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{summary.critical}</div>
          <p className="text-[11px] text-slate-400 mt-1">Stock &le; 10 units &amp; high velocity</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-amber-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-amber-400">Low Stock</span>
            <AlertTriangle className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{summary.low}</div>
          <p className="text-[11px] text-slate-400 mt-1">Stock &le; 30 units &amp; moderate velocity</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-emerald-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-emerald-400">Healthy Stock</span>
            <CheckCircle className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-2xl font-bold font-mono text-white mt-1">{summary.healthy}</div>
          <p className="text-[11px] text-slate-400 mt-1">Well balanced inventory ratio</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-850 border border-purple-500/20 shadow-sm">
          <div className="flex items-center justify-between">
            <span className="text-xs uppercase font-medium text-purple-400">Total Holding Value</span>
            <PackageOpen className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-xl font-bold font-mono text-white mt-1">
            {formatINR(summary.totalValue, false)}
          </div>
          <p className="text-[11px] text-slate-400 mt-1">Aggregate warehouse stock value</p>
        </div>
      </div>

      {/* Query 15 Inventory Table */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h3 className="text-sm font-semibold text-slate-200">
              Product Inventory & Restock Status (Query 15)
            </h3>
            <p className="text-xs text-slate-400">
              Filtered inside subquery on ('Delivered','Shipped') ensuring accurate units sold
            </p>
          </div>
          <SqlViewerModal queryId="q15" title="Query 15: Inventory Health Check" />
        </div>
        <DataTable
          columns={inventoryColumns}
          data={inventory}
          defaultSortKey="estimated_weeks_of_stock"
          defaultSortDir="asc"
          pageSize={10}
        />
      </div>
    </div>
  );
}

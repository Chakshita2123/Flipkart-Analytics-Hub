import React, { useState } from 'react';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import OverviewPage from './pages/OverviewPage';
import RevenuePage from './pages/RevenuePage';
import CustomersPage from './pages/CustomersPage';
import ChurnAcquisitionPage from './pages/ChurnAcquisitionPage';
import SellersPage from './pages/SellersPage';
import ProductsCategoriesPage from './pages/ProductsCategoriesPage';
import InventoryPage from './pages/InventoryPage';
import ReturnsPage from './pages/ReturnsPage';
import RegionsPaymentsPage from './pages/RegionsPaymentsPage';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [refreshKey, setRefreshKey] = useState(0);

  const handleRefresh = () => {
    setRefreshKey((k) => k + 1);
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'overview':
        return <OverviewPage key={refreshKey} />;
      case 'revenue':
        return <RevenuePage key={refreshKey} />;
      case 'customers':
        return <CustomersPage key={refreshKey} />;
      case 'churn':
        return <ChurnAcquisitionPage key={refreshKey} />;
      case 'sellers':
        return <SellersPage key={refreshKey} />;
      case 'products':
        return <ProductsCategoriesPage key={refreshKey} />;
      case 'inventory':
        return <InventoryPage key={refreshKey} />;
      case 'returns':
        return <ReturnsPage key={refreshKey} />;
      case 'regions':
        return <RegionsPaymentsPage key={refreshKey} />;
      default:
        return <OverviewPage key={refreshKey} />;
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col font-sans">
      <Navbar onRefresh={handleRefresh} />

      <div className="flex-1 flex overflow-hidden">
        <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

        <main className="flex-1 overflow-y-auto p-6 lg:p-8">
          <div className="max-w-7xl mx-auto space-y-8">
            {renderActivePage()}
          </div>
        </main>
      </div>

      {/* Prominent Footer */}
      <footer className="border-t border-slate-800 bg-slate-950 px-6 py-4 text-center text-xs text-slate-400">
        <div className="flex flex-col sm:flex-row items-center justify-between gap-2 max-w-7xl mx-auto">
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 rounded-full bg-amber-400"></span>
            <span className="font-semibold text-slate-300">Synthetic sample data</span>
            <span className="text-slate-500">—</span>
            <span>All users, sellers, products, orders, and returns are generated for portfolio demonstration.</span>
          </div>

          <div className="text-slate-500 font-mono text-[11px]">
            MySQL 8.0 &bull; Node.js Express &bull; React &bull; 15 Analytical Queries
          </div>
        </div>
      </footer>
    </div>
  );
}

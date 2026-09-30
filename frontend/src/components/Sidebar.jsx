import React from 'react';
import {
  LayoutDashboard,
  TrendingUp,
  Users,
  UserX,
  Store,
  Package,
  Boxes,
  RotateCcw,
  Globe2,
  FileCode2
} from 'lucide-react';

const NAV_ITEMS = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard, badge: 'KPIs + Q8' },
  { id: 'revenue', label: 'Revenue & Festivals', icon: TrendingUp, badge: 'Q8, Q11' },
  { id: 'customers', label: 'Customers & RFM', icon: Users, badge: 'Q1, Q7' },
  { id: 'churn', label: 'Churn & Acquisition', icon: UserX, badge: 'Q9, Q14' },
  { id: 'sellers', label: 'Sellers & Reliability', icon: Store, badge: 'Q5, Q13' },
  { id: 'products', label: 'Products & Categories', icon: Package, badge: 'Q2, Q10' },
  { id: 'inventory', label: 'Inventory Health', icon: Boxes, badge: 'Q15' },
  { id: 'returns', label: 'Product Returns', icon: RotateCcw, badge: 'Q6' },
  { id: 'regions', label: 'Regions & Payments', icon: Globe2, badge: 'Q3, Q4, Q12' },
];

export default function Sidebar({ activeTab, setActiveTab }) {
  return (
    <aside className="w-64 border-r border-slate-800 bg-slate-900/60 flex flex-col shrink-0">
      <div className="p-4 border-b border-slate-800/80">
        <div className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">
          Analytics Navigation
        </div>
      </div>

      <nav className="flex-1 p-3 space-y-1 overflow-y-auto">
        {NAV_ITEMS.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                isActive
                  ? 'bg-brand-500/15 text-brand-400 border border-brand-500/30 font-semibold shadow-sm'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-2.5">
                <Icon className={`w-4 h-4 ${isActive ? 'text-brand-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              <span
                className={`text-[10px] font-mono px-1.5 py-0.5 rounded ${
                  isActive ? 'bg-brand-500/20 text-brand-300' : 'bg-slate-800 text-slate-500'
                }`}
              >
                {item.badge}
              </span>
            </button>
          );
        })}
      </nav>

      {/* SQL Hero Callout in Sidebar */}
      <div className="p-3 m-3 rounded-lg bg-slate-950 border border-slate-800/80 text-xs">
        <div className="flex items-center gap-1.5 text-brand-400 font-semibold mb-1">
          <FileCode2 className="w-3.5 h-3.5" />
          <span>SQL is the Hero</span>
        </div>
        <p className="text-[11px] text-slate-400 leading-relaxed">
          Zero client-side metrics calculation. Every chart & table directly reflects pure MySQL 8.0 query results.
        </p>
      </div>
    </aside>
  );
}

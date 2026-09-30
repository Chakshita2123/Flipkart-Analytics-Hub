import React from 'react';

export default function MetricCard({ title, value, subtitle, icon: Icon, trend, trendLabel, color = 'blue' }) {
  const colorMap = {
    blue: 'border-blue-500/20 bg-blue-500/5 text-blue-400',
    emerald: 'border-emerald-500/20 bg-emerald-500/5 text-emerald-400',
    amber: 'border-amber-500/20 bg-amber-500/5 text-amber-400',
    rose: 'border-rose-500/20 bg-rose-500/5 text-rose-400',
    purple: 'border-purple-500/20 bg-purple-500/5 text-purple-400',
    indigo: 'border-indigo-500/20 bg-indigo-500/5 text-indigo-400'
  };

  const badgeColor = colorMap[color] || colorMap.blue;

  return (
    <div className="p-5 rounded-xl bg-slate-850 border border-slate-800 hover:border-slate-700/80 transition-all shadow-sm">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium uppercase tracking-wider text-slate-400">{title}</span>
        {Icon && (
          <div className={`p-2 rounded-lg border ${badgeColor}`}>
            <Icon className="w-4 h-4" />
          </div>
        )}
      </div>

      <div className="mt-3">
        <div className="text-2xl font-bold text-slate-100 font-mono tracking-tight">{value}</div>
        {subtitle && <p className="mt-1 text-xs text-slate-400 leading-normal">{subtitle}</p>}
      </div>

      {(trend !== undefined || trendLabel) && (
        <div className="mt-3 pt-3 border-t border-slate-800/60 flex items-center gap-1.5 text-xs">
          {trend !== undefined && (
            <span className={`font-medium ${trend >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
              {trend >= 0 ? '+' : ''}{trend}%
            </span>
          )}
          {trendLabel && <span className="text-slate-500">{trendLabel}</span>}
        </div>
      )}
    </div>
  );
}

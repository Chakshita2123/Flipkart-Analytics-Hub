import React from 'react';
import { Database, Archive, Github, RefreshCw } from 'lucide-react';
import { getDataMode, getSnapshotTimestamp } from '../api';

export default function Navbar({ onRefresh }) {
  const mode = getDataMode();
  const timestamp = getSnapshotTimestamp();

  return (
    <header className="h-16 px-6 border-b border-slate-800 bg-slate-900/90 backdrop-blur sticky top-0 z-30 flex items-center justify-between">
      <div className="flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-brand-600 to-indigo-500 flex items-center justify-center font-bold text-white shadow-md shadow-brand-500/20">
          ⚡
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-white flex items-center gap-2">
            Flipkart Analytics Hub
            <span className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-brand-500/10 text-brand-400 border border-brand-500/20">
              MySQL 8.0 BI
            </span>
          </h1>
          <p className="text-[11px] text-slate-400">15 Analytical Queries Visualised</p>
        </div>
      </div>

      <div className="flex items-center gap-3">
        {/* Mode Badge */}
        <div className="flex items-center gap-2 px-3 py-1 rounded-full text-xs border border-slate-800 bg-slate-850">
          {mode === 'live' ? (
            <>
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              <span className="text-slate-300 font-medium">Live MySQL Mode</span>
            </>
          ) : (
            <>
              <Archive className="w-3.5 h-3.5 text-amber-400" />
              <span className="text-slate-300 font-medium">
                Snapshot Mode {timestamp ? `(${new Date(timestamp).toLocaleDateString()})` : ''}
              </span>
            </>
          )}
        </div>

        {onRefresh && (
          <button
            onClick={onRefresh}
            className="p-1.5 rounded-lg border border-slate-800 bg-slate-850 hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw className="w-4 h-4" />
          </button>
        )}

        <a
          href="https://github.com/Chakshita2123/Flipkart-Analytics-Hub"
          target="_blank"
          rel="noreferrer"
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border border-slate-800 bg-slate-850 hover:bg-slate-800 text-xs text-slate-300 hover:text-white transition-colors"
        >
          <Github className="w-4 h-4" />
          <span className="hidden sm:inline">GitHub</span>
        </a>
      </div>
    </header>
  );
}

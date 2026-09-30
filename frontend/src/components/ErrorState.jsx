import React from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';

export default function ErrorState({ error, onRetry }) {
  return (
    <div className="py-16 p-6 rounded-xl bg-slate-850 border border-rose-500/20 text-center max-w-md mx-auto my-12">
      <div className="w-12 h-12 rounded-full bg-rose-500/10 text-rose-400 flex items-center justify-center mx-auto mb-3">
        <AlertCircle className="w-6 h-6" />
      </div>
      <h3 className="text-sm font-semibold text-slate-200">Failed to Retrieve Query Data</h3>
      <p className="mt-1 text-xs text-slate-400 leading-relaxed">
        {error || 'Unable to connect to the analytics database or load the snapshot.'}
      </p>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-xs font-medium text-slate-200 transition-colors"
        >
          <RefreshCw className="w-3.5 h-3.5" />
          <span>Retry Query</span>
        </button>
      )}
    </div>
  );
}

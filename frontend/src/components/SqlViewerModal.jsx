import React, { useState, useEffect } from 'react';
import { Code2, Copy, Check, ChevronDown, ChevronUp, ExternalLink } from 'lucide-react';
import { api } from '../api';

export default function SqlViewerModal({ queryId, title }) {
  const [isOpen, setIsOpen] = useState(false);
  const [copied, setCopied] = useState(false);
  const [queryData, setQueryData] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen && !queryData) {
      setLoading(true);
      api.getQuerySql(queryId)
        .then((data) => setQueryData(data))
        .catch(() => setQueryData({ sql: '-- Unable to load query text' }))
        .finally(() => setLoading(false));
    }
  }, [isOpen, queryId, queryData]);

  const handleCopy = () => {
    if (queryData?.sql) {
      navigator.clipboard.writeText(queryData.sql);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    }
  };

  const displayId = String(queryId).toUpperCase();

  return (
    <div className="inline-block">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="inline-flex items-center gap-1.5 px-2.5 py-1 text-xs font-medium rounded-md bg-brand-500/10 text-brand-400 border border-brand-500/20 hover:bg-brand-500/20 hover:border-brand-500/40 transition-colors"
        title="View the raw SQL query powering this visualization"
      >
        <Code2 className="w-3.5 h-3.5" />
        <span>Powered by {displayId}</span>
        {isOpen ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
      </button>

      {isOpen && (
        <div className="mt-3 p-4 rounded-lg bg-slate-950 border border-slate-800 text-left shadow-2xl animate-fadeIn">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/80">
            <div className="flex items-center gap-2">
              <span className="text-xs font-semibold uppercase tracking-wider text-brand-400">
                {queryData?.title || title || `SQL Definition (${displayId})`}
              </span>
              <span className="text-[10px] px-1.5 py-0.5 rounded bg-slate-800 text-slate-400">
                MySQL 8.0
              </span>
            </div>
            <button
              onClick={handleCopy}
              className="inline-flex items-center gap-1 px-2 py-1 text-xs rounded bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
            >
              {copied ? (
                <>
                  <Check className="w-3 h-3 text-emerald-400" />
                  <span className="text-emerald-400 font-medium">Copied!</span>
                </>
              ) : (
                <>
                  <Copy className="w-3 h-3" />
                  <span>Copy SQL</span>
                </>
              )}
            </button>
          </div>

          <div className="mt-3 overflow-x-auto max-h-96">
            {loading ? (
              <div className="py-6 text-center text-xs text-slate-500">Loading SQL text...</div>
            ) : (
              <pre className="text-xs text-slate-300 font-mono leading-relaxed selection:bg-brand-500/30">
                <code>{queryData?.sql || '-- No SQL available'}</code>
              </pre>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

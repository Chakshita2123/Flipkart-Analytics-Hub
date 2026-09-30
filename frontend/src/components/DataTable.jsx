import React, { useState, useMemo } from 'react';
import { ChevronUp, ChevronDown, ChevronsUpDown, Search, ArrowLeft, ArrowRight } from 'lucide-react';

export default function DataTable({
  columns,
  data = [],
  searchable = true,
  searchPlaceholder = 'Search records...',
  defaultSortKey = null,
  defaultSortDir = 'asc',
  pageSize = 10,
  rowKey = (row, i) => i
}) {
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState(defaultSortKey);
  const [sortDir, setSortDir] = useState(defaultSortDir);
  const [currentPage, setCurrentPage] = useState(1);
  const [rowsPerPage, setRowsPerPage] = useState(pageSize);

  // 1. Filtering
  const filteredData = useMemo(() => {
    if (!search.trim()) return data;
    const term = search.toLowerCase();
    return data.filter((row) =>
      columns.some((col) => {
        const val = row[col.key];
        return val !== null && val !== undefined && String(val).toLowerCase().includes(term);
      })
    );
  }, [data, search, columns]);

  // 2. Sorting
  const sortedData = useMemo(() => {
    if (!sortKey) return filteredData;
    return [...filteredData].sort((a, b) => {
      const valA = a[sortKey];
      const valB = b[sortKey];

      if (valA === valB) return 0;
      if (valA === null || valA === undefined) return 1;
      if (valB === null || valB === undefined) return -1;

      const numA = Number(valA);
      const numB = Number(valB);
      const isNum = !isNaN(numA) && !isNaN(numB);

      let comparison = 0;
      if (isNum) {
        comparison = numA - numB;
      } else {
        comparison = String(valA).localeCompare(String(valB));
      }
      return sortDir === 'asc' ? comparison : -comparison;
    });
  }, [filteredData, sortKey, sortDir]);

  // 3. Pagination
  const totalPages = Math.ceil(sortedData.length / rowsPerPage) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * rowsPerPage;
    return sortedData.slice(start, start + rowsPerPage);
  }, [sortedData, currentPage, rowsPerPage]);

  const handleSort = (key) => {
    if (sortKey === key) {
      if (sortDir === 'asc') setSortDir('desc');
      else {
        setSortKey(null);
        setSortDir('asc');
      }
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  return (
    <div className="rounded-xl bg-slate-850 border border-slate-800 overflow-hidden shadow-sm">
      {/* Search and control header */}
      {searchable && (
        <div className="p-4 border-b border-slate-800 flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="relative flex-1 max-w-sm">
            <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
            <input
              type="text"
              value={search}
              onChange={(e) => {
                setSearch(e.target.value);
                setCurrentPage(1);
              }}
              placeholder={searchPlaceholder}
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg bg-slate-900 border border-slate-700/80 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500 transition-colors"
            />
          </div>

          <div className="flex items-center gap-3 text-xs text-slate-400">
            <span>Showing {sortedData.length} records</span>
            <select
              value={rowsPerPage}
              onChange={(e) => {
                setRowsPerPage(Number(e.target.value));
                setCurrentPage(1);
              }}
              className="px-2 py-1 rounded bg-slate-900 border border-slate-700 text-slate-300 text-xs focus:outline-none"
            >
              <option value={10}>10 / page</option>
              <option value={25}>25 / page</option>
              <option value={50}>50 / page</option>
              <option value={100}>100 / page</option>
            </select>
          </div>
        </div>
      )}

      {/* Table Content */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-300">
          <thead className="bg-slate-900/80 text-[11px] uppercase tracking-wider text-slate-400 font-semibold border-b border-slate-800">
            <tr>
              {columns.map((col) => {
                const isSorted = sortKey === col.key;
                return (
                  <th
                    key={col.key}
                    onClick={() => col.sortable !== false && handleSort(col.key)}
                    className={`py-3 px-4 ${col.sortable !== false ? 'cursor-pointer select-none hover:text-slate-200' : ''} ${col.align === 'right' ? 'text-right' : ''}`}
                  >
                    <div className={`inline-flex items-center gap-1.5 ${col.align === 'right' ? 'justify-end w-full' : ''}`}>
                      <span>{col.label}</span>
                      {col.sortable !== false && (
                        <span>
                          {isSorted ? (
                            sortDir === 'asc' ? <ChevronUp className="w-3.5 h-3.5 text-brand-400" /> : <ChevronDown className="w-3.5 h-3.5 text-brand-400" />
                          ) : (
                            <ChevronsUpDown className="w-3 h-3 text-slate-600" />
                          )}
                        </span>
                      )}
                    </div>
                  </th>
                );
              })}
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-normal">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-8 text-center text-slate-500">
                  No records match your query
                </td>
              </tr>
            ) : (
              paginatedData.map((row, idx) => (
                <tr key={rowKey(row, idx)} className="hover:bg-slate-800/40 transition-colors">
                  {columns.map((col) => {
                    const value = row[col.key];
                    const rendered = col.render ? col.render(value, row) : value;
                    return (
                      <td
                        key={col.key}
                        className={`py-3 px-4 whitespace-nowrap ${col.align === 'right' ? 'text-right font-mono' : ''}`}
                      >
                        {rendered !== null && rendered !== undefined ? rendered : '-'}
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="p-3 border-t border-slate-800 bg-slate-900/40 flex items-center justify-between text-xs text-slate-400">
          <div>
            Page {currentPage} of {totalPages}
          </div>
          <div className="flex items-center gap-1.5">
            <button
              onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
            >
              <ArrowLeft className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded bg-slate-800 hover:bg-slate-700 disabled:opacity-40 disabled:cursor-not-allowed text-slate-300"
            >
              <ArrowRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

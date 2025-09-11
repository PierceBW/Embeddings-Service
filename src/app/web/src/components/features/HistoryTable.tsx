import React, { useMemo, useState } from 'react';
import { usePredictions } from '../../hooks/usePredictions';
import { usePredictionStore } from '../../store/predictionStore';
import { RiskBadge, Input, Skeleton } from '../../components/ui';
import clsx from 'clsx';
import { ArrowUpIcon, ArrowDownIcon, PlusIcon, ClipboardIcon } from '@heroicons/react/24/outline';

interface Props {
  onNew: () => void;
}

export default function HistoryTable({ onNew }: Props) {
  const { data, isLoading, isFetching, error } = usePredictions({ page: 1, pageSize: 200 });
  const { selectedId, setSelectedId, setPanelMode } = usePredictionStore();
  const [search, setSearch] = useState('');
  const [sortKey, setSortKey] = useState<'timestamp' | 'risk_score'>('timestamp');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');

  const filtered = useMemo(() => {
    if (!data) return [];
    let rows = data;
    if (search) rows = rows.filter((r) => r.id.toLowerCase().includes(search.toLowerCase()));
    rows = [...rows].sort((a, b) => {
      const dir = sortDir === 'asc' ? 1 : -1;
      if (sortKey === 'timestamp') return (new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()) * dir;
      return (a.risk_score - b.risk_score) * dir;
    });
    return rows;
  }, [data, search, sortKey, sortDir]);

  const toggleSort = (key: typeof sortKey) => {
    if (sortKey === key) setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'));
    else {
      setSortKey(key);
      setSortDir('desc');
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <Input
          placeholder="Search by ID…"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-40 text-sm"
        />
        <button
          onClick={onNew}
          className="inline-flex items-center gap-1 text-sm text-indigo-600 hover:underline"
        >
          <PlusIcon className="w-4 h-4" /> New Prediction
        </button>
      </div>

      {isLoading ? (
        <div className="space-y-3 p-2">
          {Array.from({ length: 8 }).map((_, i) => (
            <Skeleton key={i} className="h-8 w-full" />
          ))}
        </div>
      ) : error ? (
        <p className="text-red-500">Failed to load predictions.</p>
      ) : (
        <div className="overflow-y-auto max-h-[80vh] border border-slate-200 rounded-md p-1 pt-0">
          <table className="w-full text-sm border-separate border-spacing-y-1">
            <thead className="bg-slate-50 sticky top-0 z-10">
              <tr>
                <th className="px-3 py-2 text-left">ID</th>
                <th
                  className="px-3 py-2 text-left cursor-pointer"
                  onClick={() => toggleSort('timestamp')}
                >
                  Timestamp{' '}
                  {sortKey === 'timestamp' && (
                    sortDir === 'asc' ? <ArrowUpIcon className="inline w-4 h-4" /> : <ArrowDownIcon className="inline w-4 h-4" />
                  )}
                </th>
                <th className="px-3 py-2 text-left">Risk</th>
                <th
                  className="px-3 py-2 text-left cursor-pointer"
                  onClick={() => toggleSort('risk_score')}
                >
                  Score{' '}
                  {sortKey === 'risk_score' && (
                    sortDir === 'asc' ? <ArrowUpIcon className="inline w-4 h-4" /> : <ArrowDownIcon className="inline w-4 h-4" />
                  )}
                </th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((row) => (
                <tr
                  key={row.id}
                  onClick={() => {
                    setSelectedId(row.id);
                    setPanelMode('history');
                  }}
                  className={clsx(
                    'hover:bg-slate-100 cursor-pointer',
                    selectedId === row.id &&
                      'ring-2 ring-indigo-500 ring-offset-0 ring-offset-white bg-indigo-50 rounded-sm'
                  )}
                >
                  <td className="px-3 py-2 font-mono flex items-center gap-1">
                    <span>Pred-{row.id.slice(0, 8)}</span>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        navigator.clipboard.writeText(row.id);
                      }}
                      className="text-slate-400 hover:text-slate-600"
                      title="Copy full ID"
                    >
                      <ClipboardIcon className="w-4 h-4" />
                    </button>
                  </td>
                  <td className="px-3 py-2">{new Date(row.timestamp).toLocaleString()}</td>
                  <td className="px-3 py-2">
                    <RiskBadge level={row.risk_level} />
                  </td>
                  <td className="px-3 py-2">
                    <div className="h-2 bg-slate-200 rounded">
                      <div
                        className={clsx(
                          'h-2 rounded',
                          row.risk_level === 0
                            ? 'bg-green-500'
                            : row.risk_level === 1
                            ? 'bg-yellow-500'
                            : 'bg-red-500'
                        )}
                        style={{ width: `${row.risk_score * 100}%` }}
                      />
                    </div>
                  </td>
                </tr>
              ))}
              {isFetching && (
                <tr>
                  <td colSpan={4} className="p-2 text-center text-xs text-slate-500">
                    Refreshing…
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
} 
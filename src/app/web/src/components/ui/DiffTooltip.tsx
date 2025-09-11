import React from 'react';
import { diffFeatures } from '../../utils/diffFeatures';

interface Props {
  anchor: Record<string, unknown>;
  neighbour: Record<string, unknown>;
  pos: { x: number; y: number };
  meta?: { id: string; risk_score: number; dist: number } | null;
}

export default function DiffTooltip({ anchor, neighbour, pos, meta }: Props) {
  const changes = diffFeatures(anchor, neighbour).slice(0, 10); // cap at 10 rows
  if (!changes.length) return null;
  return (
    <div
      style={{ top: pos.y + 12, left: pos.x + 12 }}
      className="fixed z-50 bg-white border border-slate-300 rounded shadow-lg p-3 text-xs max-w-sm"
    >
      {meta && (
        <div className="text-xs text-slate-700 mb-1 font-medium">
          {meta.id.slice(0, 6)} – {(meta.risk_score * 100).toFixed(1)}% / {meta.dist.toFixed(3)}
        </div>
      )}
      <h4 className="font-semibold mb-2">Feature Differences</h4>
      <ul className="space-y-1 max-h-64 overflow-y-auto">
        {changes.map((c) => {
          let color = 'text-slate-800';
          if (c.pctDiff !== undefined) {
            if (c.pctDiff < 0.05) color = 'text-yellow-600';
            else if (c.pctDiff >= 0.05) color = 'text-red-600';
          } else if (String(c.from) !== String(c.to)) {
            color = 'text-red-600';
          }

          const same = String(c.from) === String(c.to);
          return (
            <li key={c.key} className="flex justify-between gap-2">
              <span className="text-slate-600 truncate max-w-[120px]">{c.key}</span>
              <span className={same ? 'text-green-600' : color}>{String(c.to)}</span>
            </li>
          );
        })}
      </ul>
      {changes.length === 10 && (
        <p className="text-[10px] text-slate-400 mt-1">Showing first 10 diffs…</p>
      )}
    </div>
  );
}

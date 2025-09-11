import React from 'react';
import { useNearestNeighbors } from '../../hooks/useNearestNeighbors';
import { usePredictionStore } from '../../store/predictionStore';
// removed unused metadata/riskLabel imports
import clsx from 'clsx';
import DiffTooltip from '../../components/ui/DiffTooltip';
import { useNeighbourDetail } from '../../hooks/useNeighbourDetail';
import { usePredictionDetail } from '../../hooks/usePredictionDetail';

interface Props {
  id: string;
  riskScore: number;
  riskLevel: number;
}

export default function NearestNeighborsPanel({ id, riskScore, riskLevel }: Props) {
  const { nnMetric, setNNMetric, setSelectedId, setPanelMode, setHoverNeighbor, hoverNeighborId, hoverPos } = usePredictionStore();
  const { data: anchorDetail } = usePredictionDetail(id);
  const { data: neighborDetail } = useNeighbourDetail(hoverNeighborId);
  const { data, isLoading } = useNearestNeighbors(id);
  const hovered = data?.find((n) => n.id === hoverNeighborId) ?? null;

  if (isLoading || !data) return <p className="text-sm text-slate-500">Loading neighbors…</p>;

  // Dynamic Y domain: zoom to [min-0.1, max+0.1] with clamping
  const rawMin = Math.min(...data.map((n) => n.dist_metric));
  const rawMax = Math.max(...data.map((n) => n.dist_metric));
  const padDomain = 0.1;
  let domainMin = rawMin - padDomain;
  let domainMax = rawMax + padDomain;
  if (domainMin < 0) domainMin = 0;
  if (domainMax <= domainMin) domainMax = domainMin + 1; // ensure non-zero span

  const colorMap = {
    0: '#16a34a', // green
    1: '#eab308', // amber
    2: '#dc2626', // red
  } as const;

  // chart dimensions & scales
  const width = 560;
  const height = 320;
  const pad = 30; // extra space for axis labels

  // X: linear 0–1
  const x = (score: number) => pad + score * (width - pad * 2);
  // Y: dynamic linear scale in [domainMin, domainMax]
  const y = (d: number) => {
    const t = (d - domainMin) / (domainMax - domainMin);
    const clamped = Math.max(0, Math.min(1, t));
    return pad + (height - pad * 2) * (1 - clamped);
  };

  return (
    <div className="space-y-4">
      <svg width={width} height={height} className="border border-slate-200 rounded w-full">
        {/* axes */}
        <line x1={pad} y1={pad} x2={pad} y2={height - pad} stroke="#cbd5e1" />
        <line x1={pad} y1={height - pad} x2={width - pad} y2={height - pad} stroke="#cbd5e1" />
        {/* axis labels */}
        {/* metric toggle */}
        {/* <foreignObject x={width - 160} y={pad - 20} width="150" height="28">
          <div className="flex gap-2 text-xs">
            {(['euclidean', 'cosine'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setNNMetric(m)}
                className={`px-2 py-1 rounded ${nnMetric===m ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-800'}`}
              >
                {m === 'euclidean' ? 'Euclidean' : 'Cosine'}
              </button>
            ))}
          </div>
        </foreignObject> */}

        <text x={width / 2} y={height - 12} textAnchor="middle" className="text-xs fill-slate-500">Risk Score</text>
        <text x={25} y={height - 12} textAnchor="left" className="text-xs fill-slate-500">Low</text>
        <text x={width - 50} y={height - 12} textAnchor="right" className="text-xs fill-slate-500">High</text>
        <text x={-height / 2} y={20} transform="rotate(-90)" textAnchor="middle" className="text-xs fill-slate-500">{nnMetric==='cosine' ? 'Cosine Dist' : 'Euclid Dist'}</text>
        {/* points */}
        {data.map((n) => {
          const t = (n.dist_metric - domainMin) / (domainMax - domainMin);
          const nt = Math.max(0, Math.min(1, t));
          const opacity = 1 - 0.7 * nt; 
          return (
          <circle
            key={n.id}
            cx={x(n.risk_score)}
            cy={y(n.dist_metric)}
            r={hoverNeighborId === n.id ? 6 : 4}
            fill={colorMap[n.risk_level as 0 | 1 | 2] ?? '#94a3b8'}
            fillOpacity={opacity}
            className="cursor-pointer"
            onMouseEnter={(e) => setHoverNeighbor(n.id, { x: e.clientX, y: e.clientY })}
            onMouseLeave={() => setHoverNeighbor(null)}
            onClick={() => { setSelectedId(n.id); setPanelMode('history'); }}
          >
          </circle>
        );})}
        {/* focus point (star) anchored below x-axis */}
        {(() => {
          const xStar = x(riskScore);
          const yStar = height - pad; // exactly on the x-axis (y = 0)
          const pts = [
            `${xStar},${yStar - 10}`,
            `${xStar + 3},${yStar - 3}`,
            `${xStar + 10},${yStar - 3}`,
            `${xStar + 4},${yStar + 2}`,
            `${xStar + 6},${yStar + 10}`,
            `${xStar},${yStar + 5}`,
            `${xStar - 6},${yStar + 10}`,
            `${xStar - 4},${yStar + 2}`,
            `${xStar - 10},${yStar - 3}`,
            `${xStar - 3},${yStar - 3}`,
          ].join(' ');
          return (
            <polygon points={pts} fill={colorMap[riskLevel as 0 | 1 | 2]} stroke="white" strokeWidth={0.5} />
          );
        })()}

      </svg>

      {hoverNeighborId && hovered && anchorDetail && neighborDetail && (
        <DiffTooltip
          anchor={anchorDetail.features_json}
          neighbour={neighborDetail.features_json}
          pos={hoverPos ?? { x: width - pad + 20, y: pad }}
          meta={{ id: hovered.id, risk_score: hovered.risk_score, dist: hovered.dist_metric }}
        />
      )}

      <table className="w-full text-sm border border-slate-200 rounded">
        <thead className="bg-slate-50">
          <tr>
            <th className="px-3 py-2 text-left">ID</th>
            <th className="px-3 py-2 text-left">Risk %</th>
            <th className="px-3 py-2 text-left">Score</th>
            <th className="px-3 py-2 text-left">Distance</th>
          </tr>
        </thead>
        <tbody>
          {data.map((n) => (
            <tr
              key={n.id}
              className={clsx('cursor-pointer hover:bg-slate-100', hoverNeighborId === n.id && 'bg-slate-100')}
              onClick={() => { setSelectedId(n.id); setPanelMode('history'); }}
              onMouseEnter={(e) => setHoverNeighbor(n.id, { x: e.clientX, y: e.clientY })}
              onMouseLeave={() => setHoverNeighbor(null)}
            >
              <td className="px-3 py-2 font-mono">Pred-{n.id.slice(0, 8)}</td>
              <td className="px-3 py-2 font-semibold" style={{ color: colorMap[n.risk_level as 0 | 1 | 2] }}>{(n.risk_score * 100).toFixed(1)}%</td>
              <td className="px-3 py-2">
                <div className="h-2 bg-slate-200 rounded">
                  <div className={clsx('h-2 rounded', n.risk_level === 0 ? 'bg-green-500' : n.risk_level === 1 ? 'bg-yellow-500' : 'bg-red-500')} style={{ width: `${n.risk_score * 100}%` }} />
                </div>
              </td>
              <td className="px-3 py-2">{n.dist_metric.toFixed(3)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 
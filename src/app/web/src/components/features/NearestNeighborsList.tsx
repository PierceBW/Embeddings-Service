import React from 'react';
import { usePredictionStore } from '../../store/predictionStore';
import { useNearestNeighbors } from '../../hooks/useNearestNeighbors';
import { riskLabel } from '../../utils/riskLabel';
import { useMetadata } from '../../hooks/useMetadata';
import clsx from 'clsx';
import { Skeleton } from '../../components/ui';

export default function NearestNeighborsList() {
  const { selectedId } = usePredictionStore();
  const { nnMetric, setNNMetric, setSelectedId, setPanelMode, setHoverNeighbor, hoverNeighborId } = usePredictionStore();
  const { data: meta } = useMetadata();
  const { data, isLoading, error } = useNearestNeighbors(selectedId);

  if (isLoading) return (
    <div className="space-y-3 p-2">
      {Array.from({ length: 5 }).map((_, i) => (
        <Skeleton className="h-10 w-full" key={i} />
      ))}
    </div>
  );
  if (error) return <p className="text-red-500">Failed to fetch neighbors.</p>;
  if (!data?.length) return <p className="text-gray-500">No neighbors found.</p>;

  return (
    <ul className="space-y-2 overflow-y-auto max-h-[80vh] p4">
      {data.map((n) => (
        <li
          key={n.id}
          onClick={() => { setSelectedId(n.id); setPanelMode('history'); }}
          onMouseEnter={() => setHoverNeighbor(n.id)}
          onMouseLeave={() => setHoverNeighbor(null)}
          className={clsx(
            'bg-white rounded p-3 cursor-pointer transition-all shadow-md hover:shadow-lg hover:bg-slate-100 transform hover:scale-[1.03]',
            (selectedId === n.id || hoverNeighborId===n.id) && 'ring-2 ring-indigo-500 ring-offset-2 ring-offset-white bg-indigo-50'
          )}
        >
          <p className="font-semibold text-gray-800">
            {riskLabel(n.risk_level, meta)} — {(n.risk_score * 100).toFixed(1)}%
          </p>
          <p className="text-xs text-gray-500 mt-1">
            {nnMetric==='cosine' ? 'Cosine: ' : 'Dist: '}{n.dist_metric.toFixed(3)}
          </p>
        </li>
      ))}
    </ul>
  );
} 
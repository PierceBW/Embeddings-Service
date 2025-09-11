import React, { useState } from 'react';
import HistoryTable from './HistoryTable';
import NewPredictionModal from './NewPredictionModal';
import NearestNeighborsList from './NearestNeighborsList';
import { PanelMode, usePredictionStore } from '../../store/predictionStore';

export default function SidePanel() {
  const { panelMode, setPanelMode } = usePredictionStore();
  const [open, setOpen] = useState(false);

  const headingMap: Record<PanelMode, string> = {
    history: 'Recent Predictions',
    nearest: 'Nearest Predictions',
  };

  return (
    <div className="p-4 border-t md:border-t-0 md:border-l h-full overflow-y-auto">
      <div className="bg-white shadow rounded p-6 mt-6">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold">{headingMap[panelMode]}</h3>
          {panelMode === 'nearest' && (
            <button
              className="text-sm text-blue-600 hover:underline"
              onClick={() => setPanelMode('history')}
            >
              ← Back to History
            </button>
          )}
        </div>
        {panelMode === 'history' ? (
          <HistoryTable onNew={() => setOpen(true)} />
        ) : (
          <NearestNeighborsList />
        )}

        <NewPredictionModal isOpen={open} onClose={() => setOpen(false)} />
      </div>
    </div>
  );
} 
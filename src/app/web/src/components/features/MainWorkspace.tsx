import PredictForm from '../../features/PredictForm/PredictForm';
import CSVUpload from '../../features/CSVUpload/CSVUpload';
import ResultCard from './ResultCard';
import NearestNeighborsList from './NearestNeighborsList';
import { usePredictionStore } from '../../store/predictionStore';
import React from 'react';
import { usePredictions } from '../../hooks/usePredictions';
import { Tab } from '@headlessui/react';
import clsx from 'clsx';
import PredictionHeader from './PredictionHeader';
import NearestNeighborsPanel from './NearestNeighborsPanel';
import { usePredictionDetail } from '../../hooks/usePredictionDetail';

export default function MainWorkspace() {
  const { selectedId, setSelectedId } = usePredictionStore();
  const { data: predictions } = usePredictions({ page: 1, pageSize: 50 });
  const { data: detail } = usePredictionDetail(selectedId);

  React.useEffect(() => {
    if (!selectedId && predictions && predictions.length > 0) {
      setSelectedId(predictions[0].id);
    }
  }, [selectedId, predictions, setSelectedId]);

  if (!selectedId) {
    return (
      <div className="p-6 bg-white shadow rounded mt-6 max-w-3xl mx-auto">
        <h2 className="text-xl font-semibold">Welcome to the Risk Prediction Dashboard</h2>
        <p className="text-slate-600 mt-2">Select a prediction on the left or create a new one to get started.</p>
      </div>
    );
  }

  return (
    <div className="p-4">
      <div className="mx-auto">
        <div className="bg-white shadow rounded p-6 mt-6">
          <Tab.Group>
            <div className="flex items-center justify-between mb-4">
              <PredictionHeader id={selectedId} timestamp={predictions?.find(p=>p.id===selectedId)?.timestamp ?? ''} />
              <Tab.List className="flex gap-2">
                {['Summary', 'Nearest Neighbors'].map((label) => (
                  <Tab
                    key={label}
                    className={({ selected }: { selected: boolean }) =>
                      clsx('px-4 py-2 rounded-md text-sm',
                        selected ? 'bg-indigo-600 text-white' : 'bg-slate-200 text-slate-800')}
                  >
                    {label}
                  </Tab>
                ))}
              </Tab.List>
            </div>

            <Tab.Panels>
              <Tab.Panel>
                <ResultCard id={selectedId} />
              </Tab.Panel>
              <Tab.Panel>
                <NearestNeighborsPanel
                  id={selectedId}
                  riskScore={detail?.risk_score ?? 0}
                  riskLevel={detail?.risk_level ?? 0}
                />
              </Tab.Panel>
            </Tab.Panels>
          </Tab.Group>
        </div>
      </div>
    </div>
  );
} 
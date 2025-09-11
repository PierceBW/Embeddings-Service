import React from 'react';
import { usePredictionDetail } from '../../hooks/usePredictionDetail';
import { useExplain } from '../../hooks/useExplain';
import { useMetadata } from '../../hooks/useMetadata';
import { riskLabel } from '../../utils/riskLabel';
import { RiskBadge, Button, Gauge } from '../../components/ui';
import { usePredictionStore } from '../../store/predictionStore';
import { MODEL_FIELD_MAPPINGS } from '../../constants/modelFieldMappings';
import FeatureSummary from './FeatureSummary/FeatureSummary';

interface Props {
  id: string;
}

export default function ResultCard({ id }: Props) {
  const { data: meta } = useMetadata();
  const { data, isLoading, error } = usePredictionDetail(id);
  const explainMutation = useExplain(id);
  const { setSelectedId, setPanelMode } = usePredictionStore();

  if (isLoading) return <p>Loading prediction…</p>;
  if (error || !data) return <p className="text-red-500">Failed to load prediction.</p>;

  const eligibleForExplain = data.risk_level >= 1; // medium or high
  const showExplain = eligibleForExplain && !data.explanation_json;
  const explanation = data.explanation_json;

  return (
    <div className="max-w-3xl mx-auto bg-white shadow p-6 rounded mt-6">
      <div className="flex items-center gap-6 mb-11">
        <Gauge
          value={data.risk_score}
          color={data.risk_level === 0 ? '#16a34a' : data.risk_level === 1 ? '#eab308' : '#dc2626'}
        />
        <RiskBadge level={data.risk_level} />
      </div>

      <div className="mb-6">
        {/* <h3 className="text-lg font-semibold mb-2">Input Features</h3> */}
        <FeatureSummary features={data.features_json} />
      </div>
      <div className="flex gap-2 mb-4">
        {showExplain && (
          <Button onClick={() => explainMutation.mutate()} disabled={explainMutation.isPending}>
            {explainMutation.isPending ? 'Explaining…' : 'Explain'}
          </Button>
        )}
      </div>

      {explanation && (
        <div className="mt-4">
          <h3 className="font-semibold mb-2">Risk Drivers</h3>
          {explanation.risk_drivers.length > 0 ? (
            <ul className="list-disc pl-5 text-gray-700 space-y-1">
              {explanation.risk_drivers.map((d) => {
                const friendly = MODEL_FIELD_MAPPINGS[meta?.active_model ?? '']?.[d]?.label ?? d;
                return <li key={d}>{friendly}</li>;
              })}
            </ul>
          ) : (
            <p className="text-sm text-slate-600">
              Complex Risk Profile: The risk is driven by a combination of factors rather than a single driver.
            </p>
          )}
        </div>
      )}

      {data.risk_level === 2 && !showExplain && !explanation && (
        <p className="text-red-600 mt-4 text-sm font-medium">
          Multiple factors contributed to this high risk score.
        </p>
      )}
    </div>
  );
} 
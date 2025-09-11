import React, { useState, FormEvent } from 'react';
import { useMetadata } from '../../hooks/useMetadata';
import { usePredict } from '../../hooks/usePredict';
import { MODEL_FIELD_MAPPINGS } from '../../constants/modelFieldMappings';
import { riskLabel } from '../../utils/riskLabel';
import { Input, Button } from '../../components/ui';
import { ArrowPathIcon, MagnifyingGlassIcon } from '@heroicons/react/24/solid';

interface PFProps { onSuccess?: () => void }

export default function PredictForm({ onSuccess }: PFProps) {
  const { data: metadata, isLoading, error } = useMetadata();
  const predictMutation = usePredict();

  const [formState, setFormState] = useState<Record<string, string>>({});

  // Initialize form state once metadata arrives
  React.useEffect(() => {
    if (metadata?.feature_order?.length && Object.keys(formState).length === 0) {
      const initial: Record<string, string> = {};
      metadata.feature_order.forEach((f) => (initial[f] = ''));
      setFormState(initial);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [metadata]);

  if (isLoading) return <p>Loading metadata…</p>;
  if (error) return <p className="text-red-500">Failed to load metadata</p>;
  if (!metadata) return null;

  const handleChange = (feature: string, value: string) => {
    setFormState((prev) => ({ ...prev, [feature]: value }));
  };

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    predictMutation.mutate(formState, {
      onSuccess: () => {
        onSuccess?.();
      },
    });
  };

  const fieldMapping = MODEL_FIELD_MAPPINGS[metadata.active_model] ?? {};

  return (
    <div className="max-w-3xl mx-auto bg-white shadow p-6 rounded mt-6">


      <form onSubmit={handleSubmit} className="space-y-4">
        {metadata.feature_order.map((feature) => {
          const cfg = fieldMapping[feature];
          const label = cfg?.label ?? feature.replace(/_/g, ' ');
          const inputType = cfg?.type ?? 'text';
          return (
            <div key={feature} className="flex flex-col">
              <label className="font-medium mb-1 capitalize" htmlFor={feature}>
                {label}
              </label>
              <Input
                id={feature}
                type={inputType}
                value={formState[feature] ?? ''}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => handleChange(feature, e.target.value)}
                className="border rounded p-2 focus:outline-none focus:ring focus:border-blue-300"
                required
              />
            </div>
          );
        })}

        <Button
          leftIcon={<MagnifyingGlassIcon className="w-4 h-4" />}
          type="submit"
          disabled={predictMutation.isPending}
          className=""
        >
          {predictMutation.isPending ? 'Predicting…' : 'Predict'}
        </Button>
      </form>

      {predictMutation.isError && (
        <p className="text-red-500 mt-4">Something went wrong. Try again.</p>
      )}

      {predictMutation.data && (
        <div className="mt-6 bg-gray-50 p-4 rounded border">
          <h3 className="font-semibold mb-2">Prediction Result</h3>
          <p>
            Risk Level: <strong>{riskLabel(predictMutation.data.risk_level, metadata)}</strong>
          </p>
          <p>
            Risk Score: <strong>{predictMutation.data.risk_score.toFixed(3)}</strong>
          </p>
        </div>
      )}
    </div>
  );
} 
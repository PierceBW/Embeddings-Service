import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

export interface FeaturePayload {
  [key: string]: string | number | boolean;
}

export interface PredictResult {
  record_id: string;
  risk_level: number;
  risk_score: number;
  mdl_used: string;
  version: string;
}

/**
 * Hook wrapping POST /predict endpoint.
 * Returns a tanstack mutation object.
 */
export const usePredict = () => {
  const qc = useQueryClient();
  return useMutation<PredictResult, unknown, FeaturePayload>({
    mutationFn: async (features) => {
      const { data } = await axios.post<PredictResult>('/predict', {
        features,
      });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['predictions'] });
    },
  });
}; 
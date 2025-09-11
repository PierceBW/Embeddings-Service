import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { PredictResult } from './usePredict';

export interface BatchPredictResponse extends PredictResult {}

export const useBatchPredict = () => {
  const qc = useQueryClient();
  return useMutation<BatchPredictResponse[], unknown, Record<string, string | number | boolean>[]>({
    mutationFn: async (items) => {
      const { data } = await axios.post<BatchPredictResponse[]>('/predict/batch', {
        items: items.map((features) => ({ features })),
      });
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['predictions'] });
    },
  });
}; 
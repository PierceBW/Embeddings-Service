import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { PredictionItem } from './usePredictions';

export interface PredictionDetail extends PredictionItem {
  features_json: Record<string, unknown>;
  explanation_json: { explanation_type: string; risk_drivers: string[]; notes: string } | null;
}

export const usePredictionDetail = (id: string | null) => {
  return useQuery<PredictionDetail | null>({
    queryKey: ['prediction', id],
    enabled: Boolean(id),
    queryFn: async () => {
      if (!id) return null;
      const { data } = await axios.get<PredictionDetail>(`/predictions/${id}`);
      return data;
    },
  });
}; 
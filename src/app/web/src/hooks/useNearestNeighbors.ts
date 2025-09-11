import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { usePredictionStore } from '../store/predictionStore';

export interface NeighborItem {
  id: string;
  risk_level: number;
  risk_score: number;
  dist_metric: number;
}

export const useNearestNeighbors = (id: string | null, k = 12) => {
  const metric = usePredictionStore((s) => s.nnMetric);
  return useQuery<NeighborItem[]>({
    queryKey: ['nearest', id, metric, k],
    enabled: Boolean(id),
    queryFn: async () => {
      if (!id) return [];
      const { data } = await axios.get<{ euclidean: NeighborItem[]; cosine: NeighborItem[] }>(
        `/predictions/${id}/nearest`,
        { params: { k } },
      );
      return metric === 'cosine' ? data.cosine : data.euclidean;
    },
    staleTime: 60_000,
  });
}; 
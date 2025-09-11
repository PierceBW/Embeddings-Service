// web/src/hooks/useNeighbourDetail.ts
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { PredictionDetail } from './usePredictionDetail';

export const useNeighbourDetail = (id: string | null) => {
  return useQuery<PredictionDetail | null>({
    queryKey: ['neighbor-detail', id],
    enabled: Boolean(id),
    queryFn: async () => {
      if (!id) return null;
      const { data } = await axios.get<PredictionDetail>(`/predictions/${id}`);
      return data;
    },
    staleTime: 60_000,
  });
};

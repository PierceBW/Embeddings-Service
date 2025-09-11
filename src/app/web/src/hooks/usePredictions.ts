import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { RiskCategory } from './useMetadata';

export interface PredictionItem {
  id: string;
  risk_level: number;
  risk_score: number;
  timestamp: string;
  model_id: string;
}

export interface UsePredictionsOptions {
  page?: number;
  pageSize?: number;
  mdl_id?: string;
  risk_level?: number;
  score_min?: number;
  score_max?: number;
}

export const usePredictions = (opts: UsePredictionsOptions = {}) => {
  const {
    page = 1,
    pageSize = 25,
    mdl_id,
    risk_level,
    score_min,
    score_max,
  } = opts;

  return useQuery<PredictionItem[]>({
    queryKey: ['predictions', page, pageSize, mdl_id, risk_level, score_min, score_max],
    queryFn: async () => {
      const { data } = await axios.get<PredictionItem[]>('/predictions', {
        params: {
          page,
          page_size: pageSize,
          mdl_id,
          risk_level,
          score_min,
          score_max,
        },
      });
      return data;
    },
    staleTime: 1000 * 60, // 1 min
  });
}; 
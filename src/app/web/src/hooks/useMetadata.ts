import { useQuery } from '@tanstack/react-query';
import axios from 'axios';

export interface RiskCategory {
  code: number;
  default_name: string;
  upper_bound: number;
}

export interface MetadataResponse {
  status: string;
  feature_order: string[];
  risk_categories: RiskCategory[];
  active_model: string;
  model_id: string;
  version: string;
}

/**
 * Fetch global service metadata – feature ordering & risk category labels.
 * Components can import this hook to gain access to the information.
 */
export const useMetadata = () => {
  return useQuery<MetadataResponse>({
    queryKey: ['metadata'],
    queryFn: async () => {
      const { data } = await axios.get<MetadataResponse>('/metadata');
      return data;
    },
    staleTime: 1000 * 60 * 5, // cache for 5 min
  });
}; 
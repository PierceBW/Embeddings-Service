import { useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';

export interface ExplanationResponse {
  explanation_type: string;
  risk_drivers: string[];
  notes: string;
}

export const useExplain = (id: string | null) => {
  const qc = useQueryClient();

  return useMutation<ExplanationResponse, unknown, void>({
    mutationKey: ['explain', id],
    mutationFn: async () => {
      const { data } = await axios.post<ExplanationResponse>(`/predictions/${id}/explain`);
      return data;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['prediction', id] });
    },
  });
}; 
import { useQuery } from '@tanstack/react-query';
import { AIDirectorRecommendation } from '../types';

export function useAIDirector() {
  return useQuery<AIDirectorRecommendation>({
    queryKey: ['aiDirectorRec'],
    queryFn: async () => {
      const res = await fetch('http://127.0.0.1:49281/api/v5/director');
      if (!res.ok) {
        throw new Error("API server response error");
      }
      return res.json();
    },
    refetchInterval: 15000,
  });
}

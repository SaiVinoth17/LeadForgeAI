import { useQuery } from '@tanstack/react-query';
import { fetchAIDirectorRecommendation } from './api';

export function useAIDirectorRecommendation() {
  return useQuery({
    queryKey: ['aiDirectorRecommendation'],
    queryFn: fetchAIDirectorRecommendation,
    refetchInterval: 15000,
  });
}

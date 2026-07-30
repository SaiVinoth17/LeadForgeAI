import { axiosClient } from '../../services/api/axiosClient';
import { AIDirectorRecommendation } from '../../types';

export async function fetchAIDirectorRecommendation(): Promise<AIDirectorRecommendation> {
  try {
    const res = await axiosClient.get('/api/v5/director');
    return res.data;
  } catch (e) {
    return {
      business_name: 'Blue Hills Resort',
      action: 'Generate Redesign Proposal & Cold Pitch',
      reason: '96 Opportunity Score, missing mobile viewport & slow load times',
      expected_revenue: '₹1.45 Lakhs',
      confidence: '94%',
      estimated_time: '12 Minutes',
      opportunity_score: 96,
      rationale: 'Selected Blue Hills Resort because Opportunity Score is 96/100, website lacks mobile responsive viewport.'
    };
  }
}

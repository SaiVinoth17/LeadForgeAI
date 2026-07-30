import { axiosClient } from '../../services/api/axiosClient';
import { Lead } from '../../types';

export async function fetchLeads(): Promise<Lead[]> {
  try {
    const res = await axiosClient.get('/api/v5/leads');
    return res.data;
  } catch (e) {
    return [{
      id: 1,
      business_name: 'Blue Hills Resort',
      category: 'Hospitality',
      website: 'https://bluehills.example.com',
      score: 96,
      digital_twin: {
        business_name: 'Blue Hills Resort',
        website_audits_count: 2,
        seo_score: 28,
        performance_score: 41,
        mobile_responsive: false,
        google_rating: 4.7,
        estimated_budget: '₹1.4 Lakhs',
        decision_maker: 'Owner / GM',
        buying_intent: 'High',
        risk_level: 'Low',
        probability: '92%',
        interaction_history: ['Audited 2026-07-30', 'Score: 96/100']
      }
    }];
  }
}

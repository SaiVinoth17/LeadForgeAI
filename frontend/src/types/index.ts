import { z } from 'zod';

export interface ClientMemory {
  business_name: string;
  website_audits_count: number;
  seo_score: number;
  performance_score: number;
  mobile_responsive: boolean;
  google_rating: number;
  estimated_budget: string;
  decision_maker: string;
  buying_intent: string;
  risk_level: string;
  probability: string;
  interaction_history: string[];
}

export const LeadSchema = z.object({
  id: z.number(),
  business_name: z.string(),
  category: z.string().optional(),
  website: z.string().optional(),
  score: z.number().default(90),
  digital_twin: z.any().optional(),
});

export type Lead = z.infer<typeof LeadSchema> & { digital_twin?: ClientMemory };

export interface AIDirectorRecommendation {
  business_name: string;
  action: string;
  reason: string;
  expected_revenue: string;
  confidence: string;
  estimated_time: string;
  opportunity_score: number;
  rationale: string;
}

export interface AIProviderHealth {
  name: string;
  latency: string;
  status: string;
  color?: string;
}

export interface TimelineEvent {
  time: string;
  action: string;
  detail: string;
}

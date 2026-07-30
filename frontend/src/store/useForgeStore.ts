import { create } from 'zustand';
import { TimelineEvent, AIProviderHealth } from '../types';

interface ForgeState {
  isBooted: boolean;
  aiCoreState: 'Idle' | 'Thinking' | 'Analyzing' | 'Generating' | 'Waiting' | 'Error';
  commandPaletteOpen: boolean;
  timelineEvents: TimelineEvent[];
  providerHealth: AIProviderHealth[];
  
  // Actions
  setBooted: (booted: boolean) => void;
  setAICoreState: (state: 'Idle' | 'Thinking' | 'Analyzing' | 'Generating' | 'Waiting' | 'Error') => void;
  setCommandPaletteOpen: (open: boolean) => void;
  addTimelineEvent: (event: TimelineEvent) => void;
  setProviderHealth: (health: AIProviderHealth[]) => void;
}

export const useForgeStore = create<ForgeState>((set) => ({
  isBooted: false,
  aiCoreState: 'Idle',
  commandPaletteOpen: false,
  timelineEvents: [
    { time: '09:31', action: '🔍 Website Audited', detail: 'Blue Hills Resort (Score: 94/100)' },
    { time: '09:32', action: '📄 Proposal Generated', detail: 'Enterprise Next.js Redesign (₹1.45L)' },
    { time: '09:33', action: '✉️ Cold Email Written', detail: 'Personalized performance pitch draft' },
    { time: '09:34', action: '💵 Invoice Created', detail: '50% Upfront Retainer INV-0105' },
    { time: '09:35', action: '📊 CRM Synced', detail: 'Opportunity moved to Qualified' },
  ],
  providerHealth: [
    { name: 'Gemini 1.5 Flash', latency: '12 ms', status: 'Online' },
    { name: 'Groq LPU Engine', latency: '45 ms', status: 'Online' },
    { name: 'Ollama (Local GPU)', latency: 'Offline', status: 'Standby' },
    { name: 'OpenRouter Proxy', latency: '180 ms', status: 'Online' },
  ],

  setBooted: (isBooted) => set({ isBooted }),
  setAICoreState: (aiCoreState) => set({ aiCoreState }),
  setCommandPaletteOpen: (commandPaletteOpen) => set({ commandPaletteOpen }),
  addTimelineEvent: (event) => set((state) => ({ timelineEvents: [event, ...state.timelineEvents] })),
  setProviderHealth: (providerHealth) => set({ providerHealth }),
}));

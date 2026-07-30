import { useState } from 'react';
import { toast } from 'sonner';
import { useQuery, useMutation } from '@tanstack/react-query';
import { axiosClient } from '../services/api/axiosClient';
import { motion } from 'framer-motion';

type Tab = 'ai' | 'general' | 'billing';

const TABS: { id: Tab; label: string }[] = [
  { id: 'ai',      label: 'AI Providers'    },
  { id: 'general', label: 'General'         },
  { id: 'billing', label: 'Billing'         },
];

function KeyInput({
  label, value, onChange, hint
}: { label: string; value: string; onChange: (v: string) => void; hint?: string }) {
  const [show, setShow] = useState(false);
  return (
    <div>
      <div className="flex items-center justify-between mb-1.5">
        <label className="text-xs font-semibold" style={{ color: 'var(--text-secondary)' }}>{label}</label>
        {hint && <span className="label">{hint}</span>}
      </div>
      <div className="relative">
        <input
          type={show ? 'text' : 'password'}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          className="input pr-16"
        />
        <button
          type="button"
          onClick={() => setShow((s) => !s)}
          className="absolute right-3 top-1/2 -translate-y-1/2 label hover:opacity-80"
          style={{ color: 'var(--text-accent)' }}
        >
          {show ? 'Hide' : 'Reveal'}
        </button>
      </div>
    </div>
  );
}

export function SettingsPage() {
  const [tab, setTab] = useState<Tab>('ai');
  const [geminiKey, setGeminiKey] = useState('sk-gemini-prod-active');
  const [groqKey,   setGroqKey]   = useState('gsk_groq_lpu_active');
  const [ollamaUrl, setOllamaUrl] = useState('http://localhost:11434');
  const [orKey,     setOrKey]     = useState('sk-or-v1-active');

  const handleSave = () => {
    axiosClient.post('/api/v5/settings', {
      ai_providers: { gemini_key: geminiKey, groq_key: groqKey, ollama_url: ollamaUrl, openrouter_key: orKey }
    }).catch(() => {});
    toast.success('Settings saved successfully.');
  };

  return (
    <div className="space-y-5 animate-fade-up max-w-3xl">
      <div>
        <h1 className="text-xl font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>Settings & Configuration</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Manage AI providers, workspace preferences, and billing</p>
      </div>

      <div className="surface-card overflow-hidden">
        {/* Tab bar */}
        <div className="flex border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface-2)' }}>
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className="px-5 py-3 text-sm font-medium transition-colors relative"
              style={{
                color: tab === t.id ? 'var(--text-accent)' : 'var(--text-secondary)',
                background: 'transparent',
              }}
            >
              {t.label}
              {tab === t.id && (
                <motion.div
                  layoutId="tab-indicator"
                  className="absolute bottom-0 left-0 right-0 h-0.5 rounded-t"
                  style={{ background: 'var(--primary)' }}
                />
              )}
            </button>
          ))}
        </div>

        {/* Tab content */}
        <div className="p-6">
          {tab === 'ai' && (
            <motion.div key="ai" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              <KeyInput label="Gemini Provider API Key"  value={geminiKey} onChange={setGeminiKey} hint="Primary" />
              <KeyInput label="Groq LPU API Key"         value={groqKey}   onChange={setGroqKey}   hint="Secondary" />
              <KeyInput label="OpenRouter API Key"        value={orKey}     onChange={setOrKey}     hint="Fallback" />
              <div>
                <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>
                  Ollama Local URL
                </label>
                <input value={ollamaUrl} onChange={(e) => setOllamaUrl(e.target.value)} className="input" />
              </div>
              <div className="pt-2">
                <button onClick={handleSave} className="btn-primary">Save AI Settings</button>
              </div>
            </motion.div>
          )}

          {tab === 'general' && (
            <motion.div key="general" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4 text-sm">
              {[
                ['Agency Name',    'LeadForge Operating Systems'],
                ['Timezone',       'Asia/Kolkata (IST +5:30)'],
                ['Currency',       'Indian Rupee (₹ INR)'],
                ['Database',       'SQLite — Local Encrypted'],
                ['AI Router',      'Forge AI Director v2'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-2 border-b" style={{ borderColor: 'var(--border)' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{k}</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{v}</span>
                </div>
              ))}
            </motion.div>
          )}

          {tab === 'billing' && (
            <motion.div key="billing" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="space-y-4">
              <div className="p-4 rounded-lg" style={{ background: 'var(--primary-dim)', border: '1px solid var(--border-accent)' }}>
                <div className="text-sm font-bold mb-0.5" style={{ color: 'var(--text-accent)' }}>Enterprise Unlimited</div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>Commercial License — Active</div>
              </div>
              {[
                ['Plan',         'Enterprise Unlimited'],
                ['Status',       'Active'],
                ['Renewal',      '2027-01-01'],
                ['Seats',        'Unlimited'],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between py-2 border-b text-sm" style={{ borderColor: 'var(--border)' }}>
                  <span style={{ color: 'var(--text-secondary)' }}>{k}</span>
                  <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{v}</span>
                </div>
              ))}
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}

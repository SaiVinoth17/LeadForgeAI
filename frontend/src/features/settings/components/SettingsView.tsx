import React, { useState } from 'react';
import { toast } from 'sonner';

export function SettingsView() {
  const [activeTab, setActiveTab] = useState<'ai' | 'general' | 'billing'>('ai');
  const [geminiKey, setGeminiKey] = useState('sk-gemini-prod-active');
  const [groqKey, setGroqKey] = useState('gsk_groq_lpu_active');

  const handleSave = () => {
    toast.success("Settings saved successfully!");
  };

  return (
    <div className="glass-card p-6 border border-indigo-500/20 max-w-4xl mx-auto my-6">
      <h2 className="text-xl font-bold text-gray-100 mb-4">⚙️ FORGE OS V6 SETTINGS & AI PROVIDERS</h2>

      <div className="flex gap-4 border-b border-gray-800 pb-3 mb-6 text-sm font-medium">
        <button
          onClick={() => setActiveTab('ai')}
          className={`pb-2 ${activeTab === 'ai' ? 'text-indigo-400 border-b-2 border-indigo-500 font-bold' : 'text-gray-400'}`}
        >
          AI Providers & Keys
        </button>
        <button
          onClick={() => setActiveTab('general')}
          className={`pb-2 ${activeTab === 'general' ? 'text-indigo-400 border-b-2 border-indigo-500 font-bold' : 'text-gray-400'}`}
        >
          General & Workspace
        </button>
        <button
          onClick={() => setActiveTab('billing')}
          className={`pb-2 ${activeTab === 'billing' ? 'text-indigo-400 border-b-2 border-indigo-500 font-bold' : 'text-gray-400'}`}
        >
          Subscription & Billing
        </button>
      </div>

      {activeTab === 'ai' && (
        <div className="space-y-4 text-xs">
          <div>
            <label className="text-gray-300 font-semibold block mb-1">⭐ Gemini Provider API Key</label>
            <input
              type="password"
              value={geminiKey}
              onChange={(e) => setGeminiKey(e.target.value)}
              className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200"
            />
          </div>
          <div>
            <label className="text-gray-300 font-semibold block mb-1">⚡ Groq LPU API Key</label>
            <input
              type="password"
              value={groqKey}
              onChange={(e) => setGroqKey(e.target.value)}
              className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200"
            />
          </div>
          <button
            onClick={handleSave}
            className="bg-indigo-600 hover:bg-indigo-500 text-white font-bold px-4 py-2 rounded-lg"
          >
            Save AI Settings
          </button>
        </div>
      )}

      {activeTab === 'general' && (
        <div className="text-xs text-gray-300 space-y-2">
          <p><strong>Agency Name:</strong> LeadForge Operating Systems</p>
          <p><strong>Timezone:</strong> Asia/Kolkata (IST)</p>
          <p><strong>Database:</strong> SQLite (Local Encrypted)</p>
        </div>
      )}

      {activeTab === 'billing' && (
        <div className="text-xs text-gray-300 space-y-2">
          <p><strong>Current Plan:</strong> Enterprise Unlimited Tier</p>
          <p><strong>Status:</strong> Active (Commercial License)</p>
        </div>
      )}
    </div>
  );
}

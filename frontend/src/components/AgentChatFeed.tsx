import { motion, AnimatePresence } from 'framer-motion';

const AGENT_COLORS: Record<string, string> = {
  'Research': 'var(--primary)',
  'SEO':      'var(--warning)',
  'Proposal': 'var(--success)',
  'CRM':      'var(--accent)',
};

const FEED = [
  { agent: 'Research Agent', text: 'Indexed 46 local businesses. 8 high-opportunity targets flagged in QuadTree.' },
  { agent: 'SEO Agent',      text: 'Blue Hills Resort: Mobile score 41/100. Maps ranking: Page 3. Action required.' },
  { agent: 'Proposal Agent', text: 'Pre-generated Enterprise SEO & Local Maps Boost proposal — est. ₹1.45L.' },
  { agent: 'CRM Agent',      text: 'Blue Hills Resort moved to Qualified stage. Recommended contact: Owner/GM.' },
];

function agentColor(name: string) {
  for (const [k, v] of Object.entries(AGENT_COLORS)) {
    if (name.includes(k)) return v;
  }
  return 'var(--text-accent)';
}

function agentInitial(name: string) {
  return name[0];
}

export function AgentChatFeed() {
  return (
    <div className="surface-card p-5">
      <div className="flex items-center justify-between mb-4">
        <span className="label-accent">Agent Activity</span>
        <span className="badge" style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border)', color: 'var(--text-tertiary)' }}>
          {FEED.length} events
        </span>
      </div>

      <div className="space-y-3 max-h-[220px] overflow-y-auto pr-1">
        {FEED.map((item, i) => {
          const color = agentColor(item.agent);
          return (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -8 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              className="flex gap-3"
            >
              {/* Avatar */}
              <div
                className="w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
                style={{ background: `${color}20`, color, border: `1px solid ${color}40` }}
              >
                {agentInitial(item.agent)}
              </div>
              {/* Content */}
              <div className="flex-1 min-w-0">
                <div className="text-xs font-semibold mb-0.5" style={{ color }}>{item.agent}</div>
                <div className="text-xs leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{item.text}</div>
              </div>
            </motion.div>
          );
        })}

        {/* Typing indicator */}
        <div className="flex gap-3 opacity-60">
          <div className="w-6 h-6 rounded-md flex items-center justify-center text-xs font-bold shrink-0 mt-0.5"
            style={{ background: 'var(--primary-dim)', color: 'var(--text-accent)', border: '1px solid var(--border-accent)' }}>
            A
          </div>
          <div className="flex items-center gap-1 pt-1">
            {[0, 1, 2].map((j) => (
              <span key={j} className="w-1.5 h-1.5 rounded-full animate-blink"
                style={{ background: 'var(--text-tertiary)', animationDelay: `${j * 0.2}s` }} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

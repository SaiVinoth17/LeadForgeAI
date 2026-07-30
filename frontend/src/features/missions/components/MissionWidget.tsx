import { motion } from 'framer-motion';

const MILESTONES = [
  { label: 'Research',  done: true  },
  { label: 'Audit',     done: true  },
  { label: 'Proposal',  done: true  },
  { label: 'Outreach',  done: false },
  { label: 'Contract',  done: false },
];

export function MissionWidget() {
  const progress = 6;
  const total = 10;
  const pct = (progress / total) * 100;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.2, duration: 0.35 }}
      className="surface-card p-5"
    >
      <div className="flex items-center justify-between mb-1">
        <span className="label-accent">Active Mission</span>
        <span className="badge badge-primary">{progress}/{total}</span>
      </div>

      <h4 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary)' }}>
        Acquire 10 Local Hotel Clients
      </h4>

      {/* Progress bar */}
      <div className="w-full h-1.5 rounded-full overflow-hidden mb-3" style={{ background: 'var(--bg-surface-3)' }}>
        <motion.div
          className="h-full rounded-full"
          style={{ background: 'var(--accent)' }}
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: 'easeOut', delay: 0.3 }}
        />
      </div>

      {/* Milestones */}
      <div className="flex gap-1 mb-4">
        {MILESTONES.map((m) => (
          <div key={m.label} className="flex-1 text-center">
            <div
              className="h-1 rounded-full mb-1"
              style={{ background: m.done ? 'var(--accent)' : 'var(--bg-surface-3)' }}
            />
            <span style={{ fontSize: 9, color: m.done ? 'var(--text-secondary)' : 'var(--text-tertiary)' }}>
              {m.label}
            </span>
          </div>
        ))}
      </div>

      <div className="flex justify-between items-center">
        <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>
          {progress} of {total} clients acquired
        </span>
        <span className="text-xs font-semibold" style={{ color: 'var(--success)' }}>₹12.0 Lakhs</span>
      </div>
    </motion.div>
  );
}

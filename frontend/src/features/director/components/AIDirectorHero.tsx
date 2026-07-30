import { motion } from 'framer-motion';
import { useAIDirectorRecommendation } from '../hooks';

export function AIDirectorHero() {
  const { data: rec, isLoading } = useAIDirectorRecommendation();

  if (isLoading || !rec) {
    return (
      <div className="surface-card p-6 animate-pulse">
        <div className="h-3 rounded w-32 mb-3" style={{ background: 'var(--bg-surface-2)' }} />
        <div className="h-6 rounded w-64 mb-2" style={{ background: 'var(--bg-surface-2)' }} />
        <div className="h-3 rounded w-full" style={{ background: 'var(--bg-surface-2)' }} />
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: 'easeOut' }}
      className="surface-card p-6"
      style={{ border: '1px solid var(--border-accent)', boxShadow: '0 0 0 1px var(--border-accent), 0 8px 32px rgba(99,102,241,0.12)' }}
    >
      {/* Header row */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <span className="label-accent">AI Director</span>
          <span className="badge badge-primary">Next Action</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="badge badge-success">
            <span className="w-1.5 h-1.5 rounded-full animate-blink" style={{ background: 'var(--success)' }} />
            {rec.confidence} confidence
          </span>
          <span className="badge" style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border)', color: 'var(--text-secondary)' }}>
            {rec.estimated_time}
          </span>
        </div>
      </div>

      {/* Main action */}
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1">
          <h2 className="text-lg font-bold mb-1.5" style={{ color: 'var(--text-primary)' }}>
            Contact{' '}
            <span style={{ color: 'var(--text-accent)' }}>{rec.business_name}</span>
            {' '}—{' '}
            <span style={{ color: 'var(--success)' }}>{rec.expected_revenue}</span>
          </h2>
          <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
            {rec.reason}
          </p>
        </div>

        <motion.button
          whileHover={{ scale: 1.02, boxShadow: '0 6px 24px var(--primary-glow)' }}
          whileTap={{ scale: 0.97 }}
          className="btn-primary shrink-0"
        >
          Approve & Dispatch
        </motion.button>
      </div>

      {/* Rationale */}
      <div className="mt-4 pt-4" style={{ borderTop: '1px solid var(--border)' }}>
        <span className="label mr-2">Reasoning</span>
        <span className="text-xs" style={{ color: 'var(--text-tertiary)' }}>{rec.rationale}</span>
      </div>
    </motion.div>
  );
}

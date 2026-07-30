import { motion } from 'framer-motion';

const OPPORTUNITIES = [
  { name: 'Blue Hills Resort',   score: 96, tier: 'Easy Win',  revenue: '₹1.45L',  color: 'var(--success)' },
  { name: 'Apex Dental',         score: 94, tier: 'Easy Win',  revenue: '₹85K',    color: 'var(--success)' },
  { name: 'Grand Horizon Hotel', score: 88, tier: 'High Value', revenue: '₹2.1L',  color: 'var(--primary)' },
  { name: 'Metro Health Clinic', score: 82, tier: 'High Value', revenue: '₹1.2L',  color: 'var(--primary)' },
];

export function OpportunityMatrix() {
  return (
    <div className="surface-card p-5">
      <div className="flex items-center justify-between mb-4">
        <span className="label-accent">Opportunity Matrix</span>
        <span className="badge badge-primary">{OPPORTUNITIES.length} targets</span>
      </div>

      <div className="space-y-2">
        {OPPORTUNITIES.map((op, i) => (
          <motion.div
            key={i}
            initial={{ opacity: 0, x: -6 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: i * 0.07 }}
            className="flex items-center gap-3 p-2.5 rounded-lg cursor-pointer transition-colors"
            style={{ background: 'var(--bg-base)', border: '1px solid var(--border)' }}
            whileHover={{ borderColor: op.color + '60', background: `${op.color}08` }}
          >
            {/* Score */}
            <div
              className="w-9 h-9 rounded-md flex items-center justify-center shrink-0 mono text-xs font-bold"
              style={{ background: `${op.color}15`, color: op.color }}
            >
              {op.score}
            </div>
            {/* Info */}
            <div className="flex-1 min-w-0">
              <div className="text-xs font-semibold truncate" style={{ color: 'var(--text-primary)' }}>{op.name}</div>
              <div className="label">{op.tier}</div>
            </div>
            {/* Revenue */}
            <span className="text-xs font-bold" style={{ color: op.color }}>{op.revenue}</span>
          </motion.div>
        ))}
      </div>
    </div>
  );
}

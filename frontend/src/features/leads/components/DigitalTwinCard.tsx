import { motion } from 'framer-motion';
import { useLeads } from '../hooks';

function ScoreRing({ value }: { value: number }) {
  const r = 22;
  const circ = 2 * Math.PI * r;
  const dash = (value / 100) * circ;
  const color = value >= 80 ? 'var(--success)' : value >= 60 ? 'var(--warning)' : 'var(--danger)';

  return (
    <div className="relative w-14 h-14 shrink-0">
      <svg viewBox="0 0 52 52" className="w-full h-full -rotate-90">
        <circle cx="26" cy="26" r={r} fill="none" stroke="var(--bg-surface-3)" strokeWidth="4" />
        <circle
          cx="26" cy="26" r={r} fill="none"
          stroke={color} strokeWidth="4"
          strokeDasharray={`${dash} ${circ}`}
          strokeLinecap="round"
          style={{ transition: 'stroke-dasharray 0.6s ease' }}
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="mono font-bold text-xs" style={{ color }}>{value}</span>
      </div>
    </div>
  );
}

function MetricTile({ label, value, color }: { label: string; value: string; color?: string }) {
  return (
    <div className="metric-tile">
      <div className="label mb-1">{label}</div>
      <div className="text-sm font-bold" style={{ color: color ?? 'var(--text-primary)' }}>{value}</div>
    </div>
  );
}

export function DigitalTwinCard() {
  const { data: leads, isLoading } = useLeads();
  const lead = leads?.[0];
  const dt = lead?.digital_twin;

  if (isLoading) {
    return (
      <div className="surface-card p-5">
        <div className="label-accent mb-4">Digital Twin</div>
        <div className="animate-pulse space-y-2">
          {[...Array(4)].map((_, i) => (
            <div key={i} className="h-10 rounded-lg" style={{ background: 'var(--bg-surface-2)' }} />
          ))}
        </div>
      </div>
    );
  }

  if (!lead || !dt) return null;

  const intentColor =
    dt.buying_intent === 'High' ? 'var(--success)' :
    dt.buying_intent === 'Medium' ? 'var(--warning)' :
    'var(--text-tertiary)';

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.1, duration: 0.35 }}
      className="surface-card p-5"
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <span className="label-accent">Digital Twin</span>
        <span className="badge badge-success">
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--success)' }} />
          Synced
        </span>
      </div>

      {/* Business + score */}
      <div className="flex items-center gap-3 mb-4">
        <ScoreRing value={lead.score} />
        <div>
          <div className="font-semibold text-sm mb-0.5" style={{ color: 'var(--text-primary)' }}>{lead.business_name}</div>
          <div className="label">{lead.category}</div>
          {lead.website && (
            <a href={lead.website} target="_blank" rel="noreferrer"
              className="text-xs hover:underline" style={{ color: 'var(--text-accent)' }}>
              {lead.website.replace(/^https?:\/\//, '')}
            </a>
          )}
        </div>
      </div>

      {/* Metrics grid */}
      <div className="grid grid-cols-2 gap-2">
        <MetricTile label="SEO Score"     value={`${dt.seo_score}%`}     color="var(--warning)" />
        <MetricTile label="Performance"   value={`${dt.performance_score}%`} color="var(--warning)" />
        <MetricTile label="Buying Intent" value={dt.buying_intent}       color={intentColor} />
        <MetricTile label="Win Probability" value={dt.probability}       color="var(--success)" />
        <MetricTile label="Budget"        value={dt.estimated_budget} />
        <MetricTile label="Decision Maker" value={dt.decision_maker} />
      </div>
    </motion.div>
  );
}

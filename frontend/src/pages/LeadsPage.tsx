import { motion } from 'framer-motion';
import { useLeads } from '../features/leads/hooks';
import { DigitalTwinCard } from '../features/leads/components/DigitalTwinCard';

function ScoreBadge({ score }: { score: number }) {
  const color = score >= 85 ? 'var(--success)' : score >= 65 ? 'var(--warning)' : 'var(--danger)';
  return (
    <span className="mono text-xs font-bold px-2 py-0.5 rounded"
      style={{ background: `${color}18`, color, border: `1px solid ${color}35` }}>
      {score}
    </span>
  );
}

export function LeadsPage() {
  const { data: leads, isLoading } = useLeads();

  return (
    <div className="space-y-5 animate-fade-up">
      <div>
        <h1 className="text-xl font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>Leads & Digital Twins</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Live client intelligence profiles with AI-scored opportunity rankings
        </p>
      </div>

      <div className="grid grid-cols-12 gap-5">
        {/* Lead table */}
        <div className="col-span-12 lg:col-span-8">
          <div className="surface-card overflow-hidden">
            <div className="flex items-center justify-between p-4 border-b" style={{ borderColor: 'var(--border)' }}>
              <span className="label-accent">All Leads</span>
              <span className="badge badge-primary">{leads?.length ?? 0} records</span>
            </div>

            {isLoading ? (
              <div className="p-6 space-y-3">
                {[...Array(4)].map((_, i) => (
                  <div key={i} className="h-12 rounded-lg animate-pulse" style={{ background: 'var(--bg-surface-2)' }} />
                ))}
              </div>
            ) : (
              <table className="w-full text-sm">
                <thead>
                  <tr style={{ borderBottom: '1px solid var(--border)' }}>
                    {['Business', 'Category', 'Website', 'Score', 'Intent'].map((h) => (
                      <th key={h} className="text-left p-3 label" style={{ color: 'var(--text-tertiary)' }}>{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {(leads ?? []).map((lead, i) => (
                    <motion.tr
                      key={lead.id}
                      initial={{ opacity: 0, y: 4 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.04 }}
                      className="border-b transition-colors cursor-pointer"
                      style={{ borderColor: 'var(--border)' }}
                      whileHover={{ background: 'var(--bg-surface-2)' } as any}
                    >
                      <td className="p-3 font-medium" style={{ color: 'var(--text-primary)' }}>{lead.business_name}</td>
                      <td className="p-3" style={{ color: 'var(--text-secondary)' }}>{lead.category ?? '—'}</td>
                      <td className="p-3">
                        {lead.website
                          ? <a href={lead.website} target="_blank" rel="noreferrer"
                              className="hover:underline text-xs" style={{ color: 'var(--text-accent)' }}>
                              {lead.website.replace(/^https?:\/\//, '')}
                            </a>
                          : <span style={{ color: 'var(--text-tertiary)' }}>—</span>}
                      </td>
                      <td className="p-3"><ScoreBadge score={lead.score} /></td>
                      <td className="p-3">
                        <span className="text-xs" style={{ color: lead.digital_twin?.buying_intent === 'High' ? 'var(--success)' : 'var(--text-secondary)' }}>
                          {lead.digital_twin?.buying_intent ?? '—'}
                        </span>
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </div>

        {/* Twin sidebar */}
        <div className="col-span-12 lg:col-span-4">
          <DigitalTwinCard />
        </div>
      </div>
    </div>
  );
}

import { motion } from 'framer-motion';
import { useQuery } from '@tanstack/react-query';
import { axiosClient } from '../services/api/axiosClient';

interface WorkflowStage {
  stage: string;
  status: 'Completed' | 'Running' | 'Waiting';
}

interface WorkflowStatus {
  current_stage: string;
  progress: number;
  pipeline: WorkflowStage[];
}

async function fetchWorkflow(): Promise<WorkflowStatus> {
  try {
    const res = await axiosClient.get('/api/v5/workflow/status');
    return res.data;
  } catch {
    return {
      current_stage: 'Stage 4: Cold Email Generation',
      progress: 0.65,
      pipeline: [
        { stage: 'Website Audit',  status: 'Completed' },
        { stage: 'SEO Analysis',   status: 'Completed' },
        { stage: 'Proposal',       status: 'Completed' },
        { stage: 'Cold Email',     status: 'Running'   },
        { stage: 'Contract',       status: 'Waiting'   },
      ],
    };
  }
}

const STATUS_STYLE: Record<string, { color: string; label: string }> = {
  Completed: { color: 'var(--success)', label: 'Done'    },
  Running:   { color: 'var(--primary)', label: 'Running' },
  Waiting:   { color: 'var(--text-tertiary)', label: 'Waiting' },
};

export function MissionsPage() {
  const { data: wf } = useQuery({ queryKey: ['workflow'], queryFn: fetchWorkflow, refetchInterval: 5000 });

  return (
    <div className="space-y-5 animate-fade-up">
      <div>
        <h1 className="text-xl font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>Active Missions</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Autonomous workflow pipeline and mission progress tracking
        </p>
      </div>

      {/* Active mission overview */}
      <div className="grid grid-cols-12 gap-5">
        <div className="col-span-12 lg:col-span-8 space-y-4">

          {/* Mission card */}
          <div className="surface-card p-6">
            <div className="flex items-center justify-between mb-1">
              <span className="label-accent">Current Mission</span>
              <span className="badge badge-primary">In Progress</span>
            </div>
            <h2 className="text-lg font-bold mb-4" style={{ color: 'var(--text-primary)' }}>
              Acquire 10 Local Hotel Clients — Phase 2
            </h2>

            {/* Mission progress */}
            <div className="mb-4">
              <div className="flex justify-between mb-2">
                <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>Overall Mission Progress</span>
                <span className="mono text-xs" style={{ color: 'var(--text-primary)' }}>60%</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ background: 'var(--bg-surface-3)' }}>
                <motion.div
                  className="h-full rounded-full"
                  style={{ background: 'linear-gradient(90deg, var(--primary), var(--accent))' }}
                  initial={{ width: 0 }}
                  animate={{ width: '60%' }}
                  transition={{ duration: 1, ease: 'easeOut', delay: 0.3 }}
                />
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3">
              {[
                { label: 'Clients Acquired', value: '6 / 10' },
                { label: 'Est. Revenue',     value: '₹12.0L' },
                { label: 'Days Remaining',   value: '14'      },
              ].map((m) => (
                <div key={m.label} className="metric-tile text-center">
                  <div className="text-lg font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>{m.value}</div>
                  <div className="label">{m.label}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Workflow pipeline */}
          {wf && (
            <div className="surface-card p-6">
              <div className="flex items-center justify-between mb-4">
                <span className="label-accent">Workflow Pipeline</span>
                <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{wf.current_stage}</span>
              </div>

              <div className="space-y-2">
                {wf.pipeline.map((stage, i) => {
                  const s = STATUS_STYLE[stage.status];
                  return (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.06 }}
                      className="flex items-center gap-3 p-3 rounded-lg"
                      style={{ background: stage.status === 'Running' ? 'var(--primary-dim)' : 'var(--bg-base)', border: '1px solid var(--border)' }}
                    >
                      <div className="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0"
                        style={{ borderColor: s.color }}>
                        {stage.status === 'Completed' && (
                          <div className="w-2.5 h-2.5 rounded-full" style={{ background: s.color }} />
                        )}
                        {stage.status === 'Running' && (
                          <div className="w-2.5 h-2.5 rounded-full animate-blink" style={{ background: s.color }} />
                        )}
                      </div>
                      <span className="text-sm font-medium flex-1" style={{ color: 'var(--text-primary)' }}>{stage.stage}</span>
                      <span className="badge" style={{ background: `${s.color}15`, color: s.color, border: `1px solid ${s.color}30` }}>
                        {s.label}
                      </span>
                    </motion.div>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Right: stats */}
        <div className="col-span-12 lg:col-span-4">
          <div className="surface-card p-5">
            <span className="label-accent block mb-4">Mission Stats</span>
            <div className="space-y-3">
              {[
                { label: 'Websites Audited',    value: '46', color: 'var(--primary)' },
                { label: 'Proposals Sent',       value: '12', color: 'var(--success)' },
                { label: 'Emails Dispatched',    value: '28', color: 'var(--warning)' },
                { label: 'Deals Closed',         value: '6',  color: 'var(--success)' },
                { label: 'Pipeline Value',       value: '₹24L', color: 'var(--accent)' },
              ].map((s) => (
                <div key={s.label} className="flex items-center justify-between metric-tile">
                  <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{s.label}</span>
                  <span className="mono font-bold text-sm" style={{ color: s.color }}>{s.value}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

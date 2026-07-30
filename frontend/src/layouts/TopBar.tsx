import { useLocation } from 'react-router-dom';
import { useForgeStore } from '../store/useForgeStore';

const ROUTE_LABELS: Record<string, string> = {
  '/':         'Mission Control',
  '/leads':    'Leads & Digital Twins',
  '/missions': 'Active Missions',
  '/health':   'AI Provider Health',
  '/settings': 'Settings & Configuration',
  '/profile':  'User Profile',
};

const AI_STATE_COLORS: Record<string, string> = {
  Idle:       'var(--text-tertiary)',
  Thinking:   'var(--primary)',
  Analyzing:  'var(--warning)',
  Generating: 'var(--success)',
  Waiting:    'var(--text-tertiary)',
  Error:      'var(--danger)',
};

export function TopBar() {
  const location = useLocation();
  const aiState = useForgeStore((s) => s.aiCoreState);
  const label = ROUTE_LABELS[location.pathname] ?? 'Forge OS';
  const color = AI_STATE_COLORS[aiState] ?? 'var(--text-tertiary)';

  return (
    <header
      className="fixed right-0 z-20 flex items-center justify-between px-5"
      style={{
        left: 'var(--sidebar-width)',
        height: 'var(--topbar-height)',
        top: 0,
        background: 'rgba(8,10,15,0.85)',
        backdropFilter: 'blur(12px)',
        borderBottom: '1px solid var(--border)',
      }}
    >
      {/* Breadcrumb */}
      <div className="flex items-center gap-2">
        <span className="label" style={{ color: 'var(--text-tertiary)' }}>Forge OS</span>
        <span style={{ color: 'var(--border-strong)' }}>/</span>
        <span className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>{label}</span>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">
        {/* AI Status */}
        <div className="flex items-center gap-1.5 badge" style={{ background: 'var(--bg-surface-2)', border: '1px solid var(--border)' }}>
          <span className="w-1.5 h-1.5 rounded-full animate-blink" style={{ background: color }} />
          <span className="mono text-xs" style={{ color }}>{aiState}</span>
        </div>

        {/* System status */}
        <div className="badge badge-success">
          <span className="w-1.5 h-1.5 rounded-full" style={{ background: 'var(--success)' }} />
          <span>System Online</span>
        </div>
      </div>
    </header>
  );
}

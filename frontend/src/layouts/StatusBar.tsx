import { useForgeStore } from '../store/useForgeStore';

export function StatusBar() {
  const events = useForgeStore((s) => s.timelineEvents);

  const items = [...events, ...events]; // duplicate for seamless loop

  return (
    <footer
      className="fixed bottom-0 right-0 z-20 overflow-hidden flex items-center"
      style={{
        left: 'var(--sidebar-width)',
        height: 'var(--statusbar-height)',
        background: 'var(--bg-surface)',
        borderTop: '1px solid var(--border)',
      }}
    >
      {/* Live indicator */}
      <div className="shrink-0 flex items-center gap-1.5 px-3 border-r" style={{ borderColor: 'var(--border)', height: '100%' }}>
        <span className="w-1.5 h-1.5 rounded-full animate-blink" style={{ background: 'var(--success)' }} />
        <span className="label" style={{ color: 'var(--success)' }}>LIVE</span>
      </div>

      {/* Scrolling ticker */}
      <div className="flex-1 overflow-hidden">
        <div className="flex animate-ticker whitespace-nowrap" style={{ gap: '48px' }}>
          {items.map((ev, i) => (
            <span key={i} className="flex items-center gap-2 text-xs shrink-0">
              <span className="mono" style={{ color: 'var(--text-tertiary)', fontSize: 10 }}>{ev.time}</span>
              <span style={{ color: 'var(--text-primary)', fontWeight: 500 }}>{ev.action}</span>
              <span style={{ color: 'var(--text-secondary)' }}>{ev.detail}</span>
              <span style={{ color: 'var(--border-strong)', marginLeft: 8 }}>·</span>
            </span>
          ))}
        </div>
      </div>
    </footer>
  );
}

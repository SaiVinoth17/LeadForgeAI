import { NavLink, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuthStore } from '../features/auth/useAuthStore';

const NAV = [
  { to: '/',         icon: '⚡', label: 'Mission Control' },
  { to: '/leads',    icon: '🎯', label: 'Leads & Twins'   },
  { to: '/missions', icon: '🚀', label: 'Missions'         },
  { to: '/health',   icon: '💚', label: 'AI Health'        },
  { to: '/settings', icon: '⚙️', label: 'Settings'         },
];

export function Sidebar() {
  const user = useAuthStore((s) => s.user);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    toast.success('Signed out');
    navigate('/login', { replace: true });
  };

  return (
    <aside
      style={{
        width: 'var(--sidebar-width)',
        background: 'var(--bg-surface)',
        borderRight: '1px solid var(--border)',
        position: 'fixed',
        left: 0,
        top: 0,
        bottom: 0,
        zIndex: 30,
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      {/* Logo */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 10,
          padding: '0 16px',
          height: 'var(--topbar-height)',
          borderBottom: '1px solid var(--border)',
        }}
      >
        <div
          style={{
            width: 28,
            height: 28,
            borderRadius: 8,
            background: 'var(--primary)',
            color: 'white',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: 14,
            fontWeight: 900,
            boxShadow: '0 0 16px var(--primary-glow)',
            flexShrink: 0,
          }}
        >
          F
        </div>
        <div>
          <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.15 }}>Forge OS</div>
          <div className="label" style={{ color: 'var(--text-tertiary)' }}>V6</div>
        </div>
      </div>

      {/* Navigation */}
      <nav style={{ flex: 1, overflowY: 'auto', padding: 12 }}>
        <div className="label" style={{ color: 'var(--text-tertiary)', padding: '4px 8px 8px' }}>Workspace</div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.to === '/'}
              className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
            >
              <span style={{ fontSize: 15, width: 18, textAlign: 'center', flexShrink: 0 }}>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </div>
      </nav>

      {/* User footer */}
      <div style={{ padding: 12, borderTop: '1px solid var(--border)' }}>
        {/* Profile button */}
        <NavLink
          to="/profile"
          className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
          style={{ marginBottom: 4 }}
        >
          <div
            style={{
              width: 22,
              height: 22,
              borderRadius: '50%',
              background: 'var(--primary-dim)',
              color: 'var(--text-accent)',
              border: '1px solid var(--border-accent)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontSize: 11,
              fontWeight: 700,
              flexShrink: 0,
            }}
          >
            {user?.name?.[0]?.toUpperCase() ?? 'A'}
          </div>
          <div style={{ overflow: 'hidden', flex: 1 }}>
            <div style={{ fontSize: 12, fontWeight: 600, color: 'var(--text-primary)', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
              {user?.name ?? 'Admin'}
            </div>
            <div className="label" style={{ color: 'var(--text-tertiary)' }}>{user?.role ?? 'Owner'}</div>
          </div>
        </NavLink>

        {/* Logout button */}
        <button
          onClick={handleLogout}
          className="nav-item"
          style={{ width: '100%', textAlign: 'left', cursor: 'pointer', color: 'var(--danger)', opacity: 0.8 }}
          title="Sign out"
        >
          <span style={{ fontSize: 14, width: 18, textAlign: 'center', flexShrink: 0 }}>↩</span>
          <span style={{ fontSize: 12 }}>Sign Out</span>
        </button>
      </div>
    </aside>
  );
}

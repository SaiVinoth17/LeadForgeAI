import { Sidebar } from './Sidebar';
import { TopBar } from './TopBar';
import { StatusBar } from './StatusBar';

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <div className="min-h-screen" style={{ background: 'var(--bg-base)' }}>
      <Sidebar />
      <TopBar />

      {/* Main content */}
      <main
        style={{
          marginLeft: 'var(--sidebar-width)',
          paddingTop: 'var(--topbar-height)',
          paddingBottom: 'var(--statusbar-height)',
          minHeight: '100vh',
        }}
      >
        <div className="p-6 max-w-[1440px] mx-auto">
          {children}
        </div>
      </main>

      <StatusBar />
    </div>
  );
}

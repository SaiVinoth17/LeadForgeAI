import { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { AppProviders } from './app/providers';
import { AppShell } from './layouts/AppShell';
import { BootScreen } from './components/BootScreen';
import { ProtectedRoute } from './features/auth/components/ProtectedRoute';
import { LoginView } from './features/auth/components/LoginView';
import { RegisterView } from './features/auth/components/RegisterView';
import { ForgotPasswordView } from './features/auth/components/ForgotPasswordView';
import { useForgeStore } from './store/useForgeStore';
import { useAuthStore } from './features/auth/useAuthStore';
import { MissionControlPage } from './pages/Dashboard/MissionControlPage';
import { LeadsPage } from './pages/LeadsPage';
import { MissionsPage } from './pages/MissionsPage';
import { HealthPage } from './pages/HealthPage';
import { SettingsPage } from './pages/SettingsPage';
import { ProfilePage } from './pages/ProfilePage';

export default function App() {
  const isBooted = useForgeStore((state) => state.isBooted);
  const initialize = useAuthStore((state) => state.initialize);

  // Hydrate auth session once on app mount
  useEffect(() => {
    initialize();
  }, [initialize]);

  if (!isBooted) {
    return <BootScreen />;
  }

  return (
    <AppProviders>
      <BrowserRouter>
        <Routes>
          {/* ── Public auth routes (no sidebar/topbar) ── */}
          <Route path="/login" element={<LoginView />} />
          <Route path="/register" element={<RegisterView />} />
          <Route path="/forgot-password" element={<ForgotPasswordView />} />

          {/* ── Protected app routes (inside AppShell) ── */}
          <Route
            path="/*"
            element={
              <ProtectedRoute>
                <AppShell>
                  <Routes>
                    <Route path="/"         element={<MissionControlPage />} />
                    <Route path="/leads"    element={<LeadsPage />} />
                    <Route path="/missions" element={<MissionsPage />} />
                    <Route path="/health"   element={<HealthPage />} />
                    <Route path="/settings" element={<SettingsPage />} />
                    <Route path="/profile"  element={<ProfilePage />} />
                    <Route path="*"         element={<Navigate to="/" replace />} />
                  </Routes>
                </AppShell>
              </ProtectedRoute>
            }
          />
        </Routes>
      </BrowserRouter>
    </AppProviders>
  );
}

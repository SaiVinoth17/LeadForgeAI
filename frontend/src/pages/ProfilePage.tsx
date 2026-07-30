import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { toast } from 'sonner';
import { useAuthStore } from '../features/auth/useAuthStore';

export function ProfilePage() {
  const user = useAuthStore((s) => s.user);
  const updateProfile = useAuthStore((s) => s.updateProfile);
  const changePassword = useAuthStore((s) => s.changePassword);
  const logout = useAuthStore((s) => s.logout);
  const navigate = useNavigate();

  // Profile edit state
  const [name, setName] = useState(user?.name ?? '');
  const [company, setCompany] = useState(user?.company ?? '');
  const [profileLoading, setProfileLoading] = useState(false);

  // Password change state
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [passwordLoading, setPasswordLoading] = useState(false);

  // Logout confirmation
  const [showLogoutConfirm, setShowLogoutConfirm] = useState(false);

  const handleProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfileLoading(true);
    try {
      await updateProfile({ name, company });
      toast.success('Profile updated successfully!');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Failed to update profile');
    } finally {
      setProfileLoading(false);
    }
  };

  const handlePasswordChange = async (e: React.FormEvent) => {
    e.preventDefault();
    if (newPassword !== confirmPassword) {
      toast.error('New passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      toast.error('Password must be at least 8 characters');
      return;
    }
    setPasswordLoading(true);
    try {
      await changePassword(currentPassword, newPassword);
      toast.success('Password changed successfully!');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      toast.error(err?.response?.data?.error || 'Failed to change password');
    } finally {
      setPasswordLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    toast.success('Signed out successfully');
    navigate('/login', { replace: true });
  };

  return (
    <div className="space-y-5 animate-fade-up max-w-3xl">
      <div>
        <h1 className="text-xl font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>
          User Profile
        </h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          Manage your account details, password, and session
        </p>
      </div>

      {/* Account Info Card */}
      <div className="surface-card overflow-hidden">
        <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface-2)' }}>
          <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Account Information</div>
        </div>
        <div className="p-6 space-y-2">
          {[
            ['Email', user?.email ?? '—'],
            ['Role', user?.role ?? '—'],
            ['Subscription', user?.subscription ?? '—'],
            ['Linked Providers', (user?.linked_providers ?? []).join(', ') || '—'],
          ].map(([k, v]) => (
            <div key={k} className="flex justify-between py-2 border-b text-sm" style={{ borderColor: 'var(--border)' }}>
              <span style={{ color: 'var(--text-secondary)' }}>{k}</span>
              <span className="font-medium" style={{ color: 'var(--text-primary)' }}>{v}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Edit Profile Card */}
      <div className="surface-card overflow-hidden">
        <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface-2)' }}>
          <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Edit Profile</div>
        </div>
        <form onSubmit={handleProfileSave} className="p-6 space-y-4">
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Full Name
            </label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="input"
              placeholder="Your Name"
              disabled={profileLoading}
            />
          </div>
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Agency / Company
            </label>
            <input
              value={company}
              onChange={(e) => setCompany(e.target.value)}
              className="input"
              placeholder="My Agency"
              disabled={profileLoading}
            />
          </div>
          <button
            type="submit"
            disabled={profileLoading}
            className="btn-primary"
          >
            {profileLoading ? 'Saving...' : 'Save Profile'}
          </button>
        </form>
      </div>

      {/* Change Password Card */}
      <div className="surface-card overflow-hidden">
        <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface-2)' }}>
          <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Change Password</div>
        </div>
        <form onSubmit={handlePasswordChange} className="p-6 space-y-4">
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Current Password
            </label>
            <input
              type="password"
              value={currentPassword}
              onChange={(e) => setCurrentPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
              required
              disabled={passwordLoading}
            />
          </div>
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              New Password <span style={{ color: 'var(--text-tertiary)' }}>(min. 8 chars)</span>
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
              required
              disabled={passwordLoading}
            />
          </div>
          <div>
            <label className="text-xs font-semibold block mb-1.5" style={{ color: 'var(--text-secondary)' }}>
              Confirm New Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="input"
              placeholder="••••••••"
              required
              disabled={passwordLoading}
            />
          </div>
          <button
            type="submit"
            disabled={passwordLoading}
            className="btn-primary"
          >
            {passwordLoading ? 'Changing...' : 'Change Password'}
          </button>
        </form>
      </div>

      {/* Logout Card */}
      <div className="surface-card overflow-hidden">
        <div className="px-6 py-4 border-b" style={{ borderColor: 'var(--border)', background: 'var(--bg-surface-2)' }}>
          <div className="text-sm font-semibold" style={{ color: 'var(--text-primary)' }}>Session</div>
        </div>
        <div className="p-6">
          {!showLogoutConfirm ? (
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-medium" style={{ color: 'var(--text-primary)' }}>Sign out of Forge OS</div>
                <div className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  This will clear your session and redirect to the login page.
                </div>
              </div>
              <button
                onClick={() => setShowLogoutConfirm(true)}
                className="px-4 py-2 text-xs font-semibold rounded-lg border transition-colors"
                style={{
                  color: 'var(--danger)',
                  borderColor: 'var(--danger)',
                  background: 'transparent',
                }}
              >
                Sign Out
              </button>
            </div>
          ) : (
            <motion.div
              initial={{ opacity: 0, y: 4 }}
              animate={{ opacity: 1, y: 0 }}
              className="flex items-center gap-3"
            >
              <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Confirm sign out?</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-xs font-semibold rounded-lg text-white transition-colors"
                style={{ background: 'var(--danger)' }}
              >
                Yes, Sign Out
              </button>
              <button
                onClick={() => setShowLogoutConfirm(false)}
                className="px-4 py-2 text-xs font-semibold rounded-lg border transition-colors"
                style={{ color: 'var(--text-secondary)', borderColor: 'var(--border)' }}
              >
                Cancel
              </button>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuthStore } from '../useAuthStore';

type Step = 'request' | 'reset' | 'done';

export function ForgotPasswordView() {
  const [step, setStep] = useState<Step>('request');
  const [email, setEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [copiedToken, setCopiedToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const forgotPassword = useAuthStore((s) => s.forgotPassword);
  const resetPassword = useAuthStore((s) => s.resetPassword);
  const navigate = useNavigate();

  const handleRequestToken = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      const result = await forgotPassword(email);
      if (result.reset_token) {
        setCopiedToken(result.reset_token);
        toast.success('Reset token generated!');
        setStep('reset');
      } else {
        // Email not found — we still show the reset step to prevent enumeration
        toast.info('If that email exists, a reset token was generated.');
        setStep('reset');
      }
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Failed to request reset token';
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    if (newPassword.length < 8) {
      setError('Password must be at least 8 characters');
      return;
    }
    setIsLoading(true);
    try {
      await resetPassword(resetToken, newPassword);
      toast.success('Password reset successfully!');
      setStep('done');
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Failed to reset password. Check your token.';
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const copyToken = () => {
    navigator.clipboard.writeText(copiedToken).then(() => toast.success('Token copied!'));
  };

  return (
    <div className="min-h-screen bg-[#0A0C10] flex items-center justify-center p-6 text-gray-100">
      <div className="glass-card p-8 border border-indigo-500/30 rounded-2xl max-w-md w-full glow-primary">
        <h1 className="text-2xl font-extrabold text-indigo-400 mb-1 text-center">⚡ FORGE OS V6</h1>
        <p className="text-xs uppercase tracking-widest text-gray-400 text-center mb-6">PASSWORD RECOVERY</p>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
            {error}
          </div>
        )}

        {/* Step 1: Request reset token */}
        {step === 'request' && (
          <form onSubmit={handleRequestToken} className="space-y-3 text-xs">
            <p className="text-gray-400 text-xs mb-4">
              Enter your email address and we'll generate a password reset token.
            </p>
            <div>
              <label className="text-gray-400 block mb-1">Email Address</label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="admin@leadforge.ai"
                className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
                required
                disabled={isLoading}
              />
            </div>
            <button
              type="submit"
              disabled={isLoading}
              className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-2.5 rounded-lg text-xs transition-colors"
            >
              {isLoading ? 'Generating token...' : 'Generate Reset Token'}
            </button>
          </form>
        )}

        {/* Step 2: Enter token + new password */}
        {step === 'reset' && (
          <div className="space-y-4 text-xs">
            {copiedToken && (
              <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/30">
                <p className="text-emerald-400 font-semibold mb-2">Your reset token (copy this!):</p>
                <div className="flex items-center gap-2">
                  <code className="flex-1 bg-[#0A0C10] p-2 rounded text-emerald-300 text-[10px] break-all font-mono">
                    {copiedToken}
                  </code>
                  <button
                    onClick={copyToken}
                    className="flex-shrink-0 bg-emerald-600 hover:bg-emerald-500 text-white px-2 py-1 rounded text-[10px] font-semibold"
                  >
                    Copy
                  </button>
                </div>
                <p className="text-gray-500 text-[10px] mt-2">Expires in 30 minutes</p>
              </div>
            )}

            <form onSubmit={handleResetPassword} className="space-y-3">
              <div>
                <label className="text-gray-400 block mb-1">Reset Token</label>
                <input
                  type="text"
                  value={resetToken}
                  onChange={(e) => setResetToken(e.target.value)}
                  placeholder="Paste your reset token here"
                  className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200 font-mono text-[10px] focus:outline-none focus:border-indigo-500"
                  required
                  disabled={isLoading}
                />
              </div>
              <div>
                <label className="text-gray-400 block mb-1">New Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
                  required
                  disabled={isLoading}
                />
              </div>
              <div>
                <label className="text-gray-400 block mb-1">Confirm New Password</label>
                <input
                  type="password"
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
                  required
                  disabled={isLoading}
                />
              </div>
              <button
                type="submit"
                disabled={isLoading}
                className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-bold py-2.5 rounded-lg text-xs transition-colors"
              >
                {isLoading ? 'Resetting password...' : 'Reset Password'}
              </button>
            </form>
          </div>
        )}

        {/* Step 3: Done */}
        {step === 'done' && (
          <div className="text-center space-y-4">
            <div className="text-4xl">✅</div>
            <p className="text-emerald-400 font-semibold">Password reset successfully!</p>
            <p className="text-gray-400 text-xs">You can now sign in with your new password.</p>
            <button
              onClick={() => navigate('/login', { replace: true })}
              className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2.5 rounded-lg text-xs transition-colors"
            >
              Go to Sign In
            </button>
          </div>
        )}

        <div className="mt-5 text-center text-[11px] text-gray-500">
          <Link to="/login" className="text-indigo-400 hover:text-indigo-300">
            ← Back to Sign In
          </Link>
        </div>
      </div>
    </div>
  );
}

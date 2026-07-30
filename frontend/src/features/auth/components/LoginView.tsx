import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { useAuthStore } from '../useAuthStore';

export function LoginView() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const login = useAuthStore((state) => state.login);
  const navigate = useNavigate();

  const handleEmailLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);
    try {
      await login(email, password);
      toast.success('Signed in successfully!');
      navigate('/', { replace: true });
    } catch (err: any) {
      const msg = err?.response?.data?.error || 'Invalid email or password';
      setError(msg);
      toast.error(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleOAuth = (provider: string) => {
    toast.info(`OAuth (${provider}) requires external provider setup. Use email/password for local auth.`);
  };

  return (
    <div className="min-h-screen bg-[#0A0C10] flex items-center justify-center p-6 text-gray-100">
      <div className="glass-card p-8 border border-indigo-500/30 rounded-2xl max-w-md w-full glow-primary">
        <h1 className="text-2xl font-extrabold text-indigo-400 mb-1 text-center">⚡ FORGE OS V6</h1>
        <p className="text-xs uppercase tracking-widest text-gray-400 text-center mb-6">SIGN IN TO YOUR AGENCY WORKSPACE</p>

        {/* OAuth Buttons */}
        <div className="space-y-2 mb-6">
          <button
            onClick={() => handleOAuth('Google')}
            className="w-full bg-[#161B22] hover:bg-[#1C2128] border border-gray-800 rounded-lg py-2 text-xs font-semibold flex items-center justify-center gap-2"
          >
            🔴 Continue with Google
          </button>
          <button
            onClick={() => handleOAuth('GitHub')}
            className="w-full bg-[#161B22] hover:bg-[#1C2128] border border-gray-800 rounded-lg py-2 text-xs font-semibold flex items-center justify-center gap-2"
          >
            🐙 Continue with GitHub
          </button>
          <button
            onClick={() => handleOAuth('Microsoft')}
            className="w-full bg-[#161B22] hover:bg-[#1C2128] border border-gray-800 rounded-lg py-2 text-xs font-semibold flex items-center justify-center gap-2"
          >
            🪟 Continue with Microsoft
          </button>
          <button
            onClick={() => handleOAuth('Apple')}
            className="w-full bg-[#161B22] hover:bg-[#1C2128] border border-gray-800 rounded-lg py-2 text-xs font-semibold flex items-center justify-center gap-2"
          >
            🍏 Continue with Apple
          </button>
        </div>

        <div className="flex items-center gap-3 my-4">
          <div className="flex-1 h-[1px] bg-gray-800" />
          <span className="text-[10px] text-gray-500 uppercase">OR EMAIL</span>
          <div className="flex-1 h-[1px] bg-gray-800" />
        </div>

        {error && (
          <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/30 text-red-400 text-xs">
            {error}
          </div>
        )}

        <form onSubmit={handleEmailLogin} className="space-y-3 text-xs">
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
          <div>
            <div className="flex items-center justify-between mb-1">
              <label className="text-gray-400">Password</label>
              <Link to="/forgot-password" className="text-indigo-400 hover:text-indigo-300 text-[10px]">
                Forgot password?
              </Link>
            </div>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="••••••••"
              className="w-full bg-[#0A0C10] border border-gray-800 rounded-lg p-2.5 text-gray-200 focus:outline-none focus:border-indigo-500"
              required
              disabled={isLoading}
            />
          </div>
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold py-2.5 rounded-lg text-xs transition-colors"
          >
            {isLoading ? 'Signing in...' : 'Sign In with Email'}
          </button>
        </form>

        <div className="mt-5 text-center text-[11px] text-gray-500">
          Don't have an account?{' '}
          <Link to="/register" className="text-indigo-400 hover:text-indigo-300 font-semibold">
            Create one
          </Link>
        </div>

        <div className="mt-3 pt-3 border-t border-gray-800 text-center">
          <p className="text-[10px] text-gray-600">Default: admin@leadforge.ai / Admin123!</p>
        </div>
      </div>
    </div>
  );
}

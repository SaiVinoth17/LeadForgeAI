import { create } from 'zustand';
import { axiosClient } from '../../services/api/axiosClient';

export interface UserProfile {
  id: number;
  name: string;
  email: string;
  role: string;
  company: string;
  subscription: string;
  linked_providers: string[];
}

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  user: UserProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;

  // Actions
  initialize: () => Promise<void>;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string, company?: string) => Promise<void>;
  logout: () => Promise<void>;
  forgotPassword: (email: string) => Promise<{ reset_token: string | null; message: string }>;
  resetPassword: (token: string, newPassword: string) => Promise<void>;
  updateProfile: (data: { name?: string; company?: string }) => Promise<void>;
  changePassword: (currentPassword: string, newPassword: string) => Promise<void>;
  setTokens: (accessToken: string, refreshToken: string, user: UserProfile) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: localStorage.getItem('forge_access_token'),
  refreshToken: localStorage.getItem('forge_refresh_token'),
  user: null,
  isAuthenticated: false,
  isLoading: true,

  // Called once on app mount to hydrate session from localStorage token
  initialize: async () => {
    const token = localStorage.getItem('forge_access_token');
    if (!token) {
      set({ isLoading: false, isAuthenticated: false });
      return;
    }
    try {
      const user = await axiosClient.get<UserProfile>('/api/v5/auth/me').then(r => r.data);
      set({ user, isAuthenticated: true, isLoading: false });
    } catch {
      // Token is invalid or expired — try to refresh
      const refreshToken = localStorage.getItem('forge_refresh_token');
      if (refreshToken) {
        try {
          const res = await axiosClient.post<{ access_token: string; user: UserProfile }>('/api/v5/auth/refresh', { refresh_token: refreshToken });
          const { access_token, user } = res.data;
          localStorage.setItem('forge_access_token', access_token);
          set({ accessToken: access_token, user, isAuthenticated: true, isLoading: false });
        } catch {
          // Refresh also failed — clear everything
          get().clearAuth();
          set({ isLoading: false });
        }
      } else {
        get().clearAuth();
        set({ isLoading: false });
      }
    }
  },

  login: async (email, password) => {
    const res = await axiosClient.post<{ access_token: string; refresh_token: string; user: UserProfile }>(
      '/api/v5/auth/login',
      { email, password }
    );
    const { access_token, refresh_token, user } = res.data;
    get().setTokens(access_token, refresh_token, user);
  },

  register: async (name, email, password, company) => {
    const res = await axiosClient.post<{ access_token: string; refresh_token: string; user: UserProfile }>(
      '/api/v5/auth/register',
      { name, email, password, company: company || 'My Agency' }
    );
    const { access_token, refresh_token, user } = res.data;
    get().setTokens(access_token, refresh_token, user);
  },

  logout: async () => {
    const refreshToken = get().refreshToken;
    try {
      await axiosClient.post('/api/v5/auth/logout', { refresh_token: refreshToken });
    } catch {
      // Ignore errors on logout
    }
    get().clearAuth();
  },

  forgotPassword: async (email) => {
    const res = await axiosClient.post<{ message: string; reset_token: string | null }>(
      '/api/v5/auth/forgot-password',
      { email }
    );
    return res.data;
  },

  resetPassword: async (token, newPassword) => {
    await axiosClient.post('/api/v5/auth/reset-password', {
      token,
      new_password: newPassword,
    });
  },

  updateProfile: async (data) => {
    const res = await axiosClient.put<UserProfile>('/api/v5/auth/profile', data);
    set({ user: res.data });
  },

  changePassword: async (currentPassword, newPassword) => {
    await axiosClient.put('/api/v5/auth/password', {
      current_password: currentPassword,
      new_password: newPassword,
    });
  },

  setTokens: (accessToken, refreshToken, user) => {
    localStorage.setItem('forge_access_token', accessToken);
    localStorage.setItem('forge_refresh_token', refreshToken);
    set({ accessToken, refreshToken, user, isAuthenticated: true });
  },

  clearAuth: () => {
    localStorage.removeItem('forge_access_token');
    localStorage.removeItem('forge_refresh_token');
    set({ accessToken: null, refreshToken: null, user: null, isAuthenticated: false });
  },
}));

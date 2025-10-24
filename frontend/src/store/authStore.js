import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { authAPI } from '../api';
import { toast } from 'react-toastify';

export const useAuthStore = create(
  persist(
    (set, get) => ({
      // State
      user: null,
      token: null,
      refreshToken: null,
      isAuthenticated: false,
      isLoading: false,

      // Actions
      login: async (credentials) => {
        set({ isLoading: true });
        try {
          const data = await authAPI.login(credentials);
          if (!data.access_token) {
            throw new Error('Invalid response from server');
          }
          
          set({
            user: data.user,
            token: data.access_token,
            refreshToken: data.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
          toast.success('Login successful!');
          return { success: true };
        } catch (error) {
          set({ isLoading: false });
          const message = error.message || 'Login failed';
          toast.error(message);
          return { success: false, error: message };
        }
      },

      register: async (userData) => {
        set({ isLoading: true });
        try {
          const data = await authAPI.register(userData);
          set({
            user: data.user,
            token: data.access_token,
            refreshToken: data.refresh_token,
            isAuthenticated: true,
            isLoading: false,
          });
          toast.success('Registration successful!');
          return { success: true };
        } catch (error) {
          set({ isLoading: false });
          const message = error.response?.data?.error || 'Registration failed';
          toast.error(message);
          return { success: false, error: message };
        }
      },

      logout: async () => {
        try {
          await authAPI.logout();
        } catch (error) {
          // Continue with logout even if API call fails
          console.error('Logout API error:', error);
        }
        
        set({
          user: null,
          token: null,
          refreshToken: null,
          isAuthenticated: false,
          isLoading: false,
        });
        
        toast.success('Logged out successfully');
      },

      refreshAccessToken: async () => {
        try {
          const data = await authAPI.refresh();
          set({ token: data.access_token });
          return true;
        } catch (error) {
          // Refresh failed, logout user
          get().logout();
          return false;
        }
      },

      checkAuth: async () => {
        const { token } = get();
        if (!token) return false;

        try {
          const data = await authAPI.me();
          set({ user: data.user, isAuthenticated: true });
          return true;
        } catch (error) {
          get().logout();
          return false;
        }
      },

      isAdmin: () => {
        const { user } = get();
        return user?.role === 'admin';
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        refreshToken: state.refreshToken,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
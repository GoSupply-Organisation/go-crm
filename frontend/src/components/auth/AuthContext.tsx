'use client';

import React, { createContext, useContext, useState, useEffect } from 'react';
import { authApi } from '@/lib/api/auth';
import { apiClient } from '@/lib/api/client';
import { User } from '@/lib/types/auth';

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password1: string, password2: string) => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (data: Partial<User>) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      await authApi.getCsrfToken();
      const userData = await authApi.getUser();
      setUser(userData);
    } catch (error) {
      console.error('Auth check failed:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const response = await authApi.login({ email, password });
    if (response.success) {
      await authApi.getCsrfToken();
      const userData = await authApi.getUser();
      setUser(userData);
    } else {
      throw new Error(response.message || 'Login failed');
    }
  };

  const signup = async (email: string, password1: string, password2: string) => {
    const response = await authApi.signup({ email, password1, password2 });
    if ('error' in response) {
      throw new Error(response.error);
    }
    // After signup, login to get user data
    await login(email, password1);
  };

  const logout = async () => {
    try {
      await authApi.logout();
    } catch (error) {
      console.error('Logout failed:', error);
    } finally {
      setUser(null);
    }
  };

  const updateUser = async (data: Partial<User>) => {
    const updatedUser = await authApi.updateUser(data);
    setUser(updatedUser);
  };

  const refreshUser = async () => {
    try {
      const userData = await authApi.getUser();
      setUser(userData);
    } catch (error) {
      console.error('User refresh failed:', error);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    signup,
    logout,
    updateUser,
    refreshUser,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
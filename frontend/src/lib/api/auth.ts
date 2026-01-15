import { apiClient } from './client';
import {
  LoginCredentials,
  SignupData,
  AuthResponse,
  User,
} from '../types/auth';

export const authApi = {
  // Get CSRF token
  getCsrfToken: async (): Promise<{ csrftoken: string }> => {
    const response = await apiClient.get<{ csrftoken: string }>('/api/auth/set-csrf-token');
    apiClient.setCsrfToken(response.csrftoken);
    return response;
  },

  // Login
  login: async (credentials: LoginCredentials): Promise<{ success: boolean; message?: string }> => {
    return apiClient.post<{ success: boolean; message?: string }>('/api/auth/login', credentials);
  },

  // Signup
  signup: async (data: SignupData): Promise<{ success: string } | { error: string }> => {
    return apiClient.post<{ success: string } | { error: string }>('/api/auth/register', data);
  },

  // Logout
  logout: async (): Promise<{ message: string }> => {
    return apiClient.post<{ message: string }>('/api/auth/logout');
  },

  // Get user details
  getUser: async (): Promise<User> => {
    return apiClient.get<User>('/api/auth/user');
  },

  // Update user details
  updateUser: async (data: Partial<User>): Promise<User> => {
    return apiClient.patch<User>('/api/auth/user', data);
  },
};
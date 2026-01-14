import { apiClient } from './client';
import {
  LoginCredentials,
  SignupData,
  AuthResponse,
  User,
  PasswordResetData,
  PasswordResetConfirmData,
  PasswordChangeData,
  AuthTokens,
} from '../types/auth';

export const authApi = {
  // Login
  login: async (credentials: LoginCredentials): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/rest-auth/login/', credentials);
  },

  // Signup
  signup: async (data: SignupData): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/rest-auth/registration/', data);
  },

  // Logout
  logout: async (): Promise<{ detail: string }> => {
    return apiClient.post<{ detail: string }>('/rest-auth/logout/');
  },

  // Get user details
  getUser: async (): Promise<User> => {
    return apiClient.get<User>('/rest-auth/user/');
  },

  // Update user details
  updateUser: async (data: Partial<User>): Promise<User> => {
    return apiClient.patch<User>('/rest-auth/user/', data);
  },

  // Password reset
  passwordReset: async (data: PasswordResetData): Promise<{ detail: string }> => {
    return apiClient.post<{ detail: string }>('/rest-auth/password/reset/', data);
  },

  // Password reset confirm
  passwordResetConfirm: async (data: PasswordResetConfirmData): Promise<{ detail: string }> => {
    return apiClient.post<{ detail: string }>('/rest-auth/password/reset/confirm/', data);
  },

  // Password change
  passwordChange: async (data: PasswordChangeData): Promise<{ detail: string }> => {
    return apiClient.post<{ detail: string }>('/rest-auth/password/change/', data);
  },

  // Verify token
  verifyToken: async (token: string): Promise<User> => {
    return apiClient.post<User>('/rest-auth/token/verify/', { token });
  },
};
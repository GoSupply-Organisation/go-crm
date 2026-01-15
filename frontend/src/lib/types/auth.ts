export interface LoginCredentials {
  username?: string;
  email: string;
  password: string;
}

export interface SignupData {
  username?: string;
  email: string;
  password1: string;
  password2: string;
}

export interface AuthResponse {
  key: string;
  user: User;
}

export interface User {
  username: string;
  email: string;
}

export interface PasswordResetData {
  email: string;
}

export interface PasswordResetConfirmData {
  uid: string;
  token: string;
  new_password1: string;
  new_password2: string;
}

export interface PasswordChangeData {
  new_password1: string;
  new_password2: string;
  old_password: string;
}

export interface AuthTokens {
  key: string;
}
// 'use client'; // <--- THIS LINE IS REQUIRED to fix the error

// import { useState, useEffect, createContext, useContext, ReactNode, useCallback, useMemo } from 'react';
// import { apiClient } from '../api/client';

// interface User {
//   id: number;
//   username: string;
//   email: string;
// }

// interface AuthContextType {
//   user: User | null;
//   loading: boolean;
//   login: (username: string, password: string) => Promise<void>;
//   logout: () => void;
//   isAuthenticated: boolean;
// }

// const AuthContext = createContext<AuthContextType | undefined>(undefined);

// export function AuthProvider({ children }: { children: ReactNode }) {
//   const [user, setUser] = useState<User | null>(null);
//   const [loading, setLoading] = useState(true);

//   const fetchUserInfo = async () => {
//     try {
//       // TODO: Replace with actual API call to get current user
//       // const response = await apiClient.get('/auth/user/');
//       // setUser(response.data);
      
//       // Mock user for persistence
//       setUser({ id: 1, username: 'persisted_user', email: 'test@example.com' });
//       setLoading(false);
//     } catch (error) {
//       console.error('Session invalid', error);
//       localStorage.removeItem('auth_token');
//       apiClient.clearToken();
//       setUser(null);
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     const token = localStorage.getItem('auth_token');
//     if (token) {
//       fetchUserInfo();
//     } else {
//       setLoading(false);
//     }
//   }, []);

//   const login = useCallback(async (username: string, password: string) => {
//     setLoading(true);
//     try {
//       // TODO: Replace with actual API call
//       // const response = await apiClient.post('/auth/login/', { username, password });
//       // const { access_token, user } = response.data;

//       // Mock login logic
//       const mockToken = 'mock_jwt_token';
//       const mockUser = { id: 1, username, email: `${username}@example.com` };

//       localStorage.setItem('auth_token', mockToken);
//       apiClient.setToken(mockToken);
//       setUser(mockUser);
//     } catch (error) {
//       console.error(error);
//       throw new Error('Login failed');
//     } finally {
//       setLoading(false);
//     }
//   }, []);

//   const logout = useCallback(() => {
//     localStorage.removeItem('auth_token');
//     apiClient.clearToken();
//     setUser(null);
//   }, []);

//   const value = useMemo(
//     () => ({
//       user,
//       loading,
//       login,
//       logout,
//       isAuthenticated: !!user,
//     }),
//     [user, loading, login, logout]
//   );

//   return (
//     <AuthContext.Provider value={value}>
//       {children}
//     </AuthContext.Provider>
//   );
// }

// export function useAuth() {
//   const context = useContext(AuthContext);
//   if (context === undefined) {
//     throw new Error('useAuth must be used within an AuthProvider');
//   }
//   return context;
// }
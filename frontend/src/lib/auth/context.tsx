'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { User, auth } from '@/lib/api/client';

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    try {
      const savedToken = localStorage.getItem('cip_token');
      const savedUser = localStorage.getItem('cip_user');
      if (savedToken && savedUser) {
        setToken(savedToken);
        setUser(JSON.parse(savedUser));
      }
    } catch {
      localStorage.removeItem('cip_token');
      localStorage.removeItem('cip_user');
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    const response = await auth.login(email, password);
    setToken(response.access_token);
    setUser(response.user);
    localStorage.setItem('cip_token', response.access_token);
    localStorage.setItem('cip_user', JSON.stringify(response.user));
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    localStorage.removeItem('cip_token');
    localStorage.removeItem('cip_user');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

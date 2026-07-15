'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/lib/auth/context';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login, user } = useAuth();
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      await login(email, password);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  // Redirect after login based on role
  useEffect(() => {
    if (user) {
      const roleRoutes: Record<string, string> = {
        citizen: '/citizen',
        mp: '/mp',
        officer: '/officer',
        admin: '/admin',
      };
      router.push(roleRoutes[user.role] || '/citizen');
    }
  }, [user, router]);

  return (
    <div style={{ minHeight: '100vh', display: 'flex' }}>
      {/* Left - Form */}
      <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem' }}>
        <div style={{ width: '100%', maxWidth: '400px' }}>
          <div style={{ marginBottom: '2rem' }}>
            <Link href="/" style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--action-primary)', textDecoration: 'none' }}>
              CIP
            </Link>
          </div>
          
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Welcome back</h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>Sign in to your account</p>

          {error && (
            <div style={{ 
              background: '#fee2e2', 
              color: '#991b1b', 
              padding: '0.75rem 1rem', 
              borderRadius: 'var(--radius-md)', 
              marginBottom: '1.5rem',
              fontSize: '0.875rem'
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '1rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>
                Email
              </label>
              <input
                type="email"
                className="input-field"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
                required
              />
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>
                Password
              </label>
              <input
                type="password"
                className="input-field"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter your password"
                required
              />
            </div>

            <button 
              type="submit" 
              className="btn-primary" 
              style={{ width: '100%', padding: '0.75rem' }}
              disabled={loading}
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p style={{ marginTop: '1.5rem', textAlign: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Don&apos;t have an account? <Link href="/register" style={{ color: 'var(--action-primary)', fontWeight: 500 }}>Sign up</Link>
          </p>
        </div>
      </div>

      {/* Right - Visual */}
      <div style={{ 
        flex: 1, 
        background: 'var(--action-primary)', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        padding: '3rem'
      }}>
        <div style={{ color: 'white', maxWidth: '400px' }}>
          <h2 style={{ fontSize: '2rem', fontWeight: 700, marginBottom: '1rem', lineHeight: 1.2 }}>
            Empowering communities through data
          </h2>
          <p style={{ fontSize: '1rem', opacity: 0.8, lineHeight: 1.6 }}>
            CIP connects citizen voices with actionable intelligence, helping representatives make informed decisions for sustainable development.
          </p>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useAuth } from '@/lib/auth/context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

export default function CitizenLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !user) router.push('/login');
  }, [user, isLoading, router]);

  if (isLoading || !user) return null;

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ 
        padding: '0.75rem 2rem', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '1px solid var(--border)',
        background: 'var(--surface)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '2rem' }}>
          <Link href="/citizen" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--action-primary)', textDecoration: 'none' }}>
            CIP
          </Link>
          <nav style={{ display: 'flex', gap: '1.5rem' }}>
            <Link href="/citizen" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>Dashboard</Link>
            <Link href="/citizen/submit" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>Submit Issue</Link>
            <Link href="/citizen/chat" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>AI Assistant</Link>
            <Link href="/citizen/my-issues" style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', textDecoration: 'none' }}>My Issues</Link>
          </nav>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{user.full_name}</span>
          <button onClick={logout} className="btn-secondary" style={{ padding: '0.5rem 1rem', fontSize: '0.8125rem' }}>Sign Out</button>
        </div>
      </header>
      <main style={{ flex: 1, padding: '2rem', maxWidth: 'var(--content-max-width)', margin: '0 auto', width: '100%' }}>
        {children}
      </main>
    </div>
  );
}

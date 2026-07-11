'use client';

import { useAuth } from '@/lib/auth/context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';
import Link from 'next/link';

export default function MpLayout({ children }: { children: React.ReactNode }) {
  const { user, isLoading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && (!user || (user.role !== 'mp' && user.role !== 'admin'))) {
      router.push('/login');
    }
  }, [user, isLoading, router]);

  if (isLoading || !user) return null;

  const navItems = [
    { href: '/mp', label: 'Dashboard' },
    { href: '/mp/issues', label: 'Issues' },
    { href: '/mp/priorities', label: 'Priorities' },
    { href: '/mp/hotspots', label: 'Hotspots' },
    { href: '/mp/copilot', label: 'Copilot' },
  ];

  return (
    <div style={{ minHeight: '100vh', display: 'flex' }}>
      {/* Sidebar */}
      <aside style={{
        width: '240px',
        background: 'var(--action-primary)',
        color: 'white',
        display: 'flex',
        flexDirection: 'column',
        flexShrink: 0,
      }}>
        <div style={{ padding: '1.5rem', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
          <Link href="/mp" style={{ fontSize: '1.25rem', fontWeight: 700, color: 'white', textDecoration: 'none' }}>
            CIP
          </Link>
          <div style={{ fontSize: '0.75rem', opacity: 0.6, marginTop: '0.25rem' }}>MP Dashboard</div>
        </div>

        <nav style={{ flex: 1, padding: '1rem 0' }}>
          {navItems.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              style={{
                display: 'block',
                padding: '0.625rem 1.5rem',
                color: 'rgba(255,255,255,0.7)',
                textDecoration: 'none',
                fontSize: '0.875rem',
                transition: 'all 0.15s',
              }}
            >
              {item.label}
            </Link>
          ))}
        </nav>

        <div style={{ padding: '1rem 1.5rem', borderTop: '1px solid rgba(255,255,255,0.1)' }}>
          <div style={{ fontSize: '0.8125rem', opacity: 0.8, marginBottom: '0.5rem' }}>{user.full_name}</div>
          <div style={{ fontSize: '0.75rem', opacity: 0.5, marginBottom: '0.75rem' }}>{user.constituency || 'Constituency'}</div>
          <button onClick={logout} style={{
            background: 'rgba(255,255,255,0.1)',
            color: 'white',
            border: 'none',
            padding: '0.5rem 1rem',
            borderRadius: 'var(--radius-md)',
            cursor: 'pointer',
            fontSize: '0.8125rem',
            width: '100%',
          }}>
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main content */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <header style={{
          padding: '0.75rem 2rem',
          borderBottom: '1px solid var(--border)',
          background: 'var(--surface)',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
        }}>
          <div style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>
            Constituency Intelligence
          </div>
          <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {user.constituency || 'All Constituencies'}
          </div>
        </header>
        <main style={{ flex: 1, padding: '2rem', background: 'var(--background)' }}>
          {children}
        </main>
      </div>
    </div>
  );
}

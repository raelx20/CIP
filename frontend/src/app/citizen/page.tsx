'use client';

import { useAuth } from '@/lib/auth/context';
import Link from 'next/link';

export default function CitizenDashboard() {
  const { user } = useAuth();

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>
        Welcome, {user?.full_name}
      </h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Track your submissions and get updates on development requests.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '1.5rem' }}>
        <Link href="/citizen/submit" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ cursor: 'pointer', transition: 'box-shadow 0.15s' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>Submit New Issue</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Report a development need or community issue in your area.
            </p>
          </div>
        </Link>

        <Link href="/citizen/chat" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ cursor: 'pointer', transition: 'box-shadow 0.15s' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>AI Assistant</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              Chat with our AI to describe your issue and get guidance.
            </p>
          </div>
        </Link>

        <Link href="/citizen/my-issues" style={{ textDecoration: 'none' }}>
          <div className="card" style={{ cursor: 'pointer', transition: 'box-shadow 0.15s' }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '0.5rem' }}>My Issues</h2>
            <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
              View consolidated issues you contributed to.
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
}

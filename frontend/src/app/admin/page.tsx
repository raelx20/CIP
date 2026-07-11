'use client';

import { useAuth } from '@/lib/auth/context';
import { admin, Dashboard } from '@/lib/api/client';
import { useEffect, useState } from 'react';

export default function AdminDashboardPage() {
  const { token } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    admin.getDashboard(token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading admin dashboard...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--critical)' }}>Failed to load dashboard: {error}</p>
      </div>
    );
  }

  const stats = [
    { label: 'Total Submissions', value: data?.total_submissions ?? 0, color: 'var(--information)' },
    { label: 'Pending Review', value: data?.pending_review ?? 0, color: 'var(--warning)' },
    { label: 'Active Issues', value: data?.active_clusters ?? 0, color: 'var(--accent)' },
    { label: 'High Priority', value: data?.high_priority ?? 0, color: 'var(--critical)' },
  ];

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Admin Dashboard</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        System overview and management.
      </p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="card">
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '0.5rem', display: 'block' }}>
              {stat.label}
            </span>
            <span style={{ fontSize: '2rem', fontWeight: 700, color: stat.color }}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>

      {(!data?.issues_by_category || data.issues_by_category.length === 0) && data?.total_submissions === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)' }}>No data yet. System will populate as citizens submit issues.</p>
        </div>
      )}
    </div>
  );
}

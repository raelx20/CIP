'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, Dashboard } from '@/lib/api/client';
import { useEffect, useState } from 'react';

export default function MpDashboardPage() {
  const { token } = useAuth();
  const [data, setData] = useState<Dashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    mp.getDashboard(token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading dashboard...</p>
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
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem', color: 'var(--text-primary)' }}>
        Dashboard
      </h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Overview of constituency intelligence and citizen engagement.
      </p>

      {/* Stats Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        {stats.map((stat) => (
          <div key={stat.label} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
            <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
              {stat.label}
            </span>
            <span style={{ fontSize: '2rem', fontWeight: 700, color: stat.color }}>
              {stat.value}
            </span>
          </div>
        ))}
      </div>

      {/* Category Distribution */}
      {data?.issues_by_category && data.issues_by_category.length > 0 && (
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Issues by Category</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
            {data.issues_by_category.map((cat) => (
              <div key={cat.category} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{cat.category}</span>
                <span style={{ fontSize: '0.875rem', fontWeight: 600 }}>{cat.count}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Empty state when no data */}
      {(!data?.issues_by_category || data.issues_by_category.length === 0) && data?.total_submissions === 0 && (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)', fontSize: '1rem' }}>No data yet. Submissions will appear here once citizens start reporting issues.</p>
        </div>
      )}
    </div>
  );
}

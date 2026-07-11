'use client';

import { useAuth } from '@/lib/auth/context';
import { admin, PriorityResponse } from '@/lib/api/client';
import { useEffect, useState } from 'react';

export default function AdminPrioritiesPage() {
  const { token } = useAuth();
  const [data, setData] = useState<PriorityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    admin.getPriorities('', token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading priorities...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--critical)' }}>Failed to load priorities: {error}</p>
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Priority Rankings</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem', fontSize: '0.875rem' }}>
        System-wide ranked priorities.
      </p>

      {!data?.rankings.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)' }}>No priority rankings available.</p>
        </div>
      ) : (
        <div className="card">
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Rank</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Score</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase' }}>Level</th>
              </tr>
            </thead>
            <tbody>
              {data.rankings.map((r) => (
                <tr key={r.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>{r.rank || '-'}</td>
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700 }}>{r.final_score.toFixed(2)}</td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span className={`badge ${
                      r.priority_level === 'critical' ? 'badge-critical' :
                      r.priority_level === 'high' ? 'badge-warning' : 'badge-neutral'
                    }`}>
                      {r.priority_level}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

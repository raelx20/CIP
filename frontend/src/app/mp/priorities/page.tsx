'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, PriorityRanking, PriorityResponse } from '@/lib/api/client';
import { useEffect, useState } from 'react';

export default function MpPrioritiesPage() {
  const { token } = useAuth();
  const [data, setData] = useState<PriorityResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    mp.getPriorities('', token)
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
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Priority Rankings</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          Ranked development priorities based on demand, severity, and urgency.
          {data?.scoring_version && <span style={{ marginLeft: '0.5rem', opacity: 0.6 }}>Scoring v{data.scoring_version}</span>}
        </p>
      </div>

      {!data?.rankings.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)' }}>No priority rankings available yet. Rankings are generated as issues are assessed.</p>
        </div>
      ) : (
        <div className="card" style={{ overflow: 'hidden' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr style={{ borderBottom: '2px solid var(--border)' }}>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Rank</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Score</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Level</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Calculated</th>
                <th style={{ textAlign: 'left', padding: '0.75rem 1rem', fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>Reasoning</th>
              </tr>
            </thead>
            <tbody>
              {data.rankings.map((r: PriorityRanking) => (
                <tr key={r.id} style={{ borderBottom: '1px solid var(--border)' }}>
                  <td style={{ padding: '0.75rem 1rem', fontWeight: 700, fontSize: '1rem' }}>
                    {r.rank || '-'}
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span style={{
                      fontSize: '1.125rem',
                      fontWeight: 700,
                      color: r.priority_level === 'critical' ? 'var(--critical)' :
                             r.priority_level === 'high' ? 'var(--warning)' :
                             r.priority_level === 'medium' ? 'var(--information)' : 'var(--text-secondary)',
                    }}>
                      {r.final_score.toFixed(2)}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem' }}>
                    <span className={`badge ${
                      r.priority_level === 'critical' ? 'badge-critical' :
                      r.priority_level === 'high' ? 'badge-warning' :
                      r.priority_level === 'medium' ? 'badge-info' : 'badge-neutral'
                    }`}>
                      {r.priority_level}
                    </span>
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                    {new Date(r.calculation_timestamp).toLocaleDateString()}
                  </td>
                  <td style={{ padding: '0.75rem 1rem', fontSize: '0.8125rem', color: 'var(--text-secondary)', maxWidth: '300px' }}>
                    {r.reasoning || 'N/A'}
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

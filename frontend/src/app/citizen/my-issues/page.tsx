'use client';

import { useAuth } from '@/lib/auth/context';
import { citizen, IssueCluster } from '@/lib/api/client';
import { useEffect, useState } from 'react';

export default function CitizenMyIssuesPage() {
  const { token } = useAuth();
  const [issues, setIssues] = useState<IssueCluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [message, setMessage] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    citizen.getMyIssues(token)
      .then((data) => {
        setIssues(data.issues || []);
        setMessage(data.message || '');
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading your issues...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--critical)' }}>Failed to load issues: {error}</p>
      </div>
    );
  }

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>My Issues</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Consolidated issues you contributed to. Multiple reports of the same problem are combined.
      </p>

      {message && (
        <div style={{
          background: 'var(--surface-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '0.75rem 1rem',
          marginBottom: '1.5rem',
          fontSize: '0.875rem',
          color: 'var(--text-secondary)',
        }}>
          {message}
        </div>
      )}

      {!issues.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1rem' }}>No issues yet. Submit your first development request to get started.</p>
          <a href="/citizen/submit" className="btn-primary" style={{ textDecoration: 'none', display: 'inline-block' }}>
            Submit a Request
          </a>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {issues.map((issue) => (
            <div key={issue.id} className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                <div>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.25rem' }}>{issue.title}</h3>
                  {issue.summary && (
                    <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                      {issue.summary}
                    </p>
                  )}
                  <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                    <span>{issue.category.replace(/_/g, ' ')}</span>
                    <span>{issue.raw_submission_count} people reported this</span>
                  </div>
                  {issue.formatted_address && (
                    <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                      {issue.formatted_address}
                    </p>
                  )}
                </div>
                <span className={`badge ${
                  issue.lifecycle_state === 'active' ? 'badge-success' :
                  issue.lifecycle_state === 'completed' ? 'badge-info' : 'badge-neutral'
                }`}>
                  {issue.lifecycle_state}
                </span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

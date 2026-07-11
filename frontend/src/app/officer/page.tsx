'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, IssueCluster, IssueListResponse } from '@/lib/api/client';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function OfficerDashboardPage() {
  const { token } = useAuth();
  const [data, setData] = useState<IssueListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    mp.getIssues('limit=20', token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading review queue...</p>
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

  const needsReview = data?.issues.filter(
    (i) => i.lifecycle_state === 'needs_review' || i.lifecycle_state === 'ready_for_review'
  ) || [];

  const recentIssues = data?.issues.slice(0, 5) || [];

  return (
    <div>
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Officer Review Queue</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Review flagged submissions and manage issue assessments.
      </p>

      {/* Stats */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', marginBottom: '2rem' }}>
        <div className="card">
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Pending Review</span>
          <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--warning)' }}>{needsReview.length}</div>
        </div>
        <div className="card">
          <span style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)' }}>Total Issues</span>
          <div style={{ fontSize: '2rem', fontWeight: 700 }}>{data?.total ?? 0}</div>
        </div>
      </div>

      {/* Needs review */}
      {needsReview.length > 0 && (
        <div style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Needs Review</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {needsReview.map((issue: IssueCluster) => (
              <Link key={issue.id} href={`/officer/issues/${issue.id}`} style={{ textDecoration: 'none' }}>
                <div className="card" style={{ cursor: 'pointer', transition: 'box-shadow 0.15s' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.25rem' }}>{issue.title}</h3>
                      <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                        {issue.raw_submission_count} submissions | {issue.category.replace(/_/g, ' ')}
                      </p>
                    </div>
                    <span className="badge badge-warning">{issue.lifecycle_state}</span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* Recent issues */}
      <div>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Recent Issues</h2>
        {!recentIssues.length ? (
          <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
            <p style={{ color: 'var(--text-muted)' }}>No issues available.</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {recentIssues.map((issue: IssueCluster) => (
              <Link key={issue.id} href={`/officer/issues/${issue.id}`} style={{ textDecoration: 'none' }}>
                <div className="card" style={{ cursor: 'pointer' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <h3 style={{ fontSize: '0.9375rem', fontWeight: 600 }}>{issue.title}</h3>
                      <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                        {issue.category.replace(/_/g, ' ')} | Confidence: {(issue.confidence * 100).toFixed(0)}%
                      </p>
                    </div>
                    <span className={`badge ${
                      issue.lifecycle_state === 'active' ? 'badge-success' : 'badge-neutral'
                    }`}>
                      {issue.lifecycle_state}
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

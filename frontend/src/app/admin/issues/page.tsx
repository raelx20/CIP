'use client';

import { useAuth } from '@/lib/auth/context';
import { admin, IssueCluster, IssueListResponse } from '@/lib/api/client';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function AdminIssuesPage() {
  const { token } = useAuth();
  const [data, setData] = useState<IssueListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    admin.getIssues('limit=50', token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading issues...</p>
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
      <div style={{ marginBottom: '1.5rem' }}>
        <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Issues</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          {data?.total ?? 0} issues in system
        </p>
      </div>

      {!data?.issues.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)' }}>No issues found.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {data.issues.map((issue: IssueCluster) => (
            <Link key={issue.id} href={`/admin/issues/${issue.id}`} style={{ textDecoration: 'none' }}>
              <div className="card" style={{ cursor: 'pointer' }}>
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
                      <span>{issue.raw_submission_count} submissions</span>
                      <span>Confidence: {(issue.confidence * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                  <span className={`badge ${
                    issue.lifecycle_state === 'active' ? 'badge-success' :
                    issue.lifecycle_state === 'needs_review' ? 'badge-warning' : 'badge-neutral'
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
  );
}

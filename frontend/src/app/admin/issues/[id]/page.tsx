'use client';

import { useAuth } from '@/lib/auth/context';
import { admin, IssueDetail } from '@/lib/api/client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

export default function AdminIssueDetailPage() {
  const { token } = useAuth();
  const params = useParams();
  const issueId = params.id as string;
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token || !issueId) return;
    setLoading(true);
    admin.getIssueDetail(issueId, token)
      .then(setIssue)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token, issueId]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading issue...</p>
      </div>
    );
  }

  if (error || !issue) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--critical)' }}>{error || 'Issue not found'}</p>
        <Link href="/admin/issues" style={{ color: 'var(--action-primary)', marginTop: '1rem', display: 'inline-block' }}>
          Back to Issues
        </Link>
      </div>
    );
  }

  return (
    <div>
      <Link href="/admin/issues" style={{ fontSize: '0.875rem', color: 'var(--action-primary)', textDecoration: 'none', display: 'inline-block', marginBottom: '1rem' }}>
        &larr; Back to Issues
      </Link>

      <div className="card" style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.375rem', fontWeight: 700, marginBottom: '0.5rem' }}>{issue.title}</h1>
        {issue.summary && <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{issue.summary}</p>}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem' }}>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Category</div>
          <div style={{ fontSize: '1rem', fontWeight: 600 }}>{issue.category.replace(/_/g, ' ')}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Submissions</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{issue.raw_submission_count}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Trusted Demand</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--success)' }}>{issue.trusted_demand}</div>
        </div>
        <div className="card">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Confidence</div>
          <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{(issue.confidence * 100).toFixed(0)}%</div>
        </div>
        {issue.severity && (
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Severity</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{issue.severity}/10</div>
          </div>
        )}
        {issue.urgency && (
          <div className="card">
            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Urgency</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{issue.urgency}/10</div>
          </div>
        )}
      </div>

      {issue.formatted_address && (
        <div className="card" style={{ marginTop: '1rem' }}>
          <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Location</h2>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{issue.formatted_address}</p>
        </div>
      )}
    </div>
  );
}

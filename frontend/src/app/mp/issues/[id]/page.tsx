'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, IssueDetail } from '@/lib/api/client';
import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import Link from 'next/link';

export default function MpIssueDetailPage() {
  const { token } = useAuth();
  const params = useParams();
  const issueId = params.id as string;
  const [issue, setIssue] = useState<IssueDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!token || !issueId) return;
    setLoading(true);
    mp.getIssueDetail(issueId, token)
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
        <Link href="/mp/issues" style={{ color: 'var(--action-primary)', marginTop: '1rem', display: 'inline-block' }}>
          Back to Issues
        </Link>
      </div>
    );
  }

  const formatCategory = (cat: string) => cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

  return (
    <div>
      <Link href="/mp/issues" style={{ fontSize: '0.875rem', color: 'var(--action-primary)', textDecoration: 'none', display: 'inline-block', marginBottom: '1rem' }}>
        &larr; Back to Issues
      </Link>

      <div style={{ display: 'flex', gap: '1.5rem', flexWrap: 'wrap' }}>
        {/* Main content */}
        <div style={{ flex: '1 1 600px' }}>
          <div className="card" style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.75rem' }}>
              <h1 style={{ fontSize: '1.375rem', fontWeight: 700 }}>{issue.title}</h1>
              <span className="badge badge-neutral">{formatCategory(issue.category)}</span>
              <span className={`badge ${
                issue.lifecycle_state === 'active' ? 'badge-success' :
                issue.lifecycle_state === 'needs_review' ? 'badge-warning' : 'badge-neutral'
              }`}>
                {issue.lifecycle_state}
              </span>
            </div>
            {issue.summary && (
              <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>{issue.summary}</p>
            )}
          </div>

          {/* Stats */}
          <div className="card" style={{ marginBottom: '1rem' }}>
            <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Demand Metrics</h2>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(140px, 1fr))', gap: '1rem' }}>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Submissions</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{issue.raw_submission_count}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Trusted Demand</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--success)' }}>{issue.trusted_demand}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Suspicious Demand</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--warning)' }}>{issue.suspicious_demand}</div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Confidence</div>
                <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{(issue.confidence * 100).toFixed(0)}%</div>
              </div>
              {issue.affected_population && (
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Affected Pop.</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>~{issue.affected_population}</div>
                </div>
              )}
              {issue.demand_velocity !== undefined && issue.demand_velocity !== null && (
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Demand Velocity</div>
                  <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{issue.demand_velocity.toFixed(2)}</div>
                </div>
              )}
            </div>
          </div>

          {/* Location */}
          {issue.formatted_address && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem' }}>Location</h2>
              <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>{issue.formatted_address}</p>
              {issue.latitude && issue.longitude && (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  {issue.latitude.toFixed(4)}, {issue.longitude.toFixed(4)}
                </p>
              )}
              {issue.administrative_areas && issue.administrative_areas.length > 0 && (
                <p style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                  Areas: {issue.administrative_areas.join(', ')}
                </p>
              )}
            </div>
          )}

          {/* Evidence */}
          {issue.supporting_evidence && issue.supporting_evidence.length > 0 && (
            <div className="card" style={{ marginBottom: '1rem' }}>
              <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.75rem' }}>Supporting Evidence</h2>
              {issue.supporting_evidence.map((ev, i) => (
                <div key={i} style={{ padding: '0.75rem', background: 'var(--surface-subtle)', borderRadius: 'var(--radius-md)', marginBottom: '0.5rem' }}>
                  <pre style={{ fontSize: '0.8125rem', color: 'var(--text-secondary)', whiteSpace: 'pre-wrap' }}>
                    {JSON.stringify(ev, null, 2)}
                  </pre>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div style={{ width: '280px', flexShrink: 0 }}>
          <div className="card">
            <h2 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem' }}>Details</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {issue.severity && (
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Severity</div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{issue.severity}/10</div>
                </div>
              )}
              {issue.urgency && (
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Urgency</div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{issue.urgency}/10</div>
                </div>
              )}
              {issue.persistence && (
                <div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Persistence</div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{issue.persistence}</div>
                </div>
              )}
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>First Reported</div>
                <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                  {new Date(issue.first_reported).toLocaleDateString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Latest Report</div>
                <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>
                  {new Date(issue.latest_report).toLocaleDateString()}
                </div>
              </div>
              <div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Subcategory</div>
                <div style={{ fontSize: '0.875rem', fontWeight: 500 }}>{issue.subcategory || 'N/A'}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

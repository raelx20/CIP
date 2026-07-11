'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, IssueCluster, IssueListResponse } from '@/lib/api/client';
import { useEffect, useState } from 'react';
import Link from 'next/link';

export default function MpIssuesPage() {
  const { token } = useAuth();
  const [data, setData] = useState<IssueListResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [category, setCategory] = useState('');
  const [skip, setSkip] = useState(0);
  const limit = 20;

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    const params = new URLSearchParams();
    if (category) params.set('category', category);
    params.set('skip', String(skip));
    params.set('limit', String(limit));
    mp.getIssues(params.toString(), token)
      .then(setData)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token, category, skip]);

  const formatCategory = (cat: string) => cat.replace(/_/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase());

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
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
        <div>
          <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.25rem' }}>Issues</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
            {data?.total ?? 0} consolidated issues
          </p>
        </div>
        <div style={{ display: 'flex', gap: '0.75rem' }}>
          <select
            className="input-field"
            value={category}
            onChange={(e) => { setCategory(e.target.value); setSkip(0); }}
            style={{ width: 'auto', minWidth: '160px' }}
          >
            <option value="">All Categories</option>
            <option value="water_supply">Water Supply</option>
            <option value="road_infrastructure">Road Infrastructure</option>
            <option value="electricity">Electricity</option>
            <option value="sanitation">Sanitation</option>
            <option value="healthcare">Healthcare</option>
            <option value="education">Education</option>
          </select>
        </div>
      </div>

      {!data?.issues.length ? (
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <p style={{ color: 'var(--text-muted)' }}>No issues found.</p>
        </div>
      ) : (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {data.issues.map((issue: IssueCluster) => (
            <Link
              key={issue.id}
              href={`/mp/issues/${issue.id}`}
              style={{ textDecoration: 'none' }}
            >
              <div className="card" style={{ cursor: 'pointer', transition: 'box-shadow 0.15s' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                      <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)' }}>{issue.title}</h3>
                      <span className="badge badge-neutral">{formatCategory(issue.category)}</span>
                      <span className={`badge ${
                        issue.lifecycle_state === 'active' ? 'badge-success' :
                        issue.lifecycle_state === 'needs_review' ? 'badge-warning' : 'badge-neutral'
                      }`}>
                        {issue.lifecycle_state}
                      </span>
                    </div>
                    {issue.summary && (
                      <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>
                        {issue.summary}
                      </p>
                    )}
                    <div style={{ display: 'flex', gap: '1.5rem', fontSize: '0.8125rem', color: 'var(--text-muted)' }}>
                      <span>{issue.raw_submission_count} submissions</span>
                      <span>Trusted demand: {issue.trusted_demand}</span>
                      <span>Confidence: {(issue.confidence * 100).toFixed(0)}%</span>
                      {issue.affected_population && <span>Affected: ~{issue.affected_population}</span>}
                    </div>
                  </div>
                  <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: '1rem' }}>
                    {issue.severity && (
                      <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>
                        Severity
                      </div>
                    )}
                    {issue.severity && (
                      <span className={`badge ${issue.severity >= 7 ? 'badge-critical' : issue.severity >= 4 ? 'badge-warning' : 'badge-success'}`}>
                        {issue.severity}/10
                      </span>
                    )}
                  </div>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination */}
      {data && data.total > limit && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: '1rem', marginTop: '1.5rem' }}>
          <button
            className="btn-secondary"
            disabled={skip === 0}
            onClick={() => setSkip(Math.max(0, skip - limit))}
          >
            Previous
          </button>
          <span style={{ display: 'flex', alignItems: 'center', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            {skip + 1}-{Math.min(skip + limit, data.total)} of {data.total}
          </span>
          <button
            className="btn-secondary"
            disabled={skip + limit >= data.total}
            onClick={() => setSkip(skip + limit)}
          >
            Next
          </button>
        </div>
      )}
    </div>
  );
}

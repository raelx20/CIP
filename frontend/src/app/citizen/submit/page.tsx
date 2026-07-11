'use client';

import { useAuth } from '@/lib/auth/context';
import { citizen, Submission } from '@/lib/api/client';
import { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function CitizenSubmitPage() {
  const { token, user } = useAuth();
  const router = useRouter();
  const [content, setContent] = useState('');
  const [language, setLanguage] = useState('en');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState<Submission | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token || !user) return;
    setError('');
    setLoading(true);

    try {
      const result = await citizen.submit(
        {
          citizen_id: user.id,
          content,
          source_modality: 'text',
          source_channel: 'web',
          language,
        },
        token
      );
      setSuccess(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Submission failed');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{ maxWidth: '600px', margin: '0 auto' }}>
        <div className="card" style={{ textAlign: 'center', padding: '3rem' }}>
          <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>&#10003;</div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '0.5rem' }}>Submission Received</h1>
          <p style={{ color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
            Your development request has been submitted and is being processed.
          </p>
          <div style={{ background: 'var(--surface-subtle)', borderRadius: 'var(--radius-md)', padding: '1rem', marginBottom: '1.5rem', textAlign: 'left' }}>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Submission ID</div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 600, fontFamily: 'monospace' }}>{success.id}</div>
            <div style={{ fontSize: '0.8125rem', color: 'var(--text-muted)', marginTop: '0.75rem', marginBottom: '0.25rem' }}>Status</div>
            <div style={{ fontSize: '0.9375rem', fontWeight: 500 }}>{success.status}</div>
          </div>
          <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'center' }}>
            <button onClick={() => router.push('/citizen')} className="btn-primary">
              Back to Dashboard
            </button>
            <button onClick={() => { setSuccess(null); setContent(''); }} className="btn-secondary">
              Submit Another
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: '600px', margin: '0 auto' }}>
      <h1 style={{ fontSize: '1.75rem', fontWeight: 700, marginBottom: '0.5rem' }}>Submit a Development Request</h1>
      <p style={{ color: 'var(--text-secondary)', marginBottom: '2rem' }}>
        Describe the issue or development need in your community. Be as specific as possible.
      </p>

      {error && (
        <div style={{
          background: '#fee2e2',
          color: '#991b1b',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-md)',
          marginBottom: '1.5rem',
          fontSize: '0.875rem',
        }}>
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit}>
        <div style={{ marginBottom: '1rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>
            Language
          </label>
          <select
            className="input-field"
            value={language}
            onChange={(e) => setLanguage(e.target.value)}
          >
            <option value="en">English</option>
            <option value="hi">Hindi</option>
            <option value="or">Odia</option>
          </select>
        </div>

        <div style={{ marginBottom: '1.5rem' }}>
          <label style={{ display: 'block', fontSize: '0.875rem', fontWeight: 500, marginBottom: '0.5rem' }}>
            Describe Your Issue
          </label>
          <textarea
            className="input-field"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Please describe the development need or issue in detail. Include the location, what is affected, and how many people are impacted..."
            rows={6}
            required
            style={{ resize: 'vertical' }}
          />
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.375rem' }}>
            {content.length}/10000 characters
          </p>
        </div>

        <button
          type="submit"
          className="btn-primary"
          style={{ width: '100%', padding: '0.875rem' }}
          disabled={loading || !content.trim()}
        >
          {loading ? 'Submitting...' : 'Submit Request'}
        </button>
      </form>
    </div>
  );
}

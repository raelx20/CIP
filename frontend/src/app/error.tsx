'use client';

export default function GlobalError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, -apple-system, sans-serif',
    }}>
      <div style={{ textAlign: 'center', padding: '2rem', maxWidth: '400px' }}>
        <h1 style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          Something went wrong
        </h1>
        <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          An unexpected error occurred. Please try again.
        </p>
        <button
          onClick={reset}
          className="btn-primary"
          style={{ padding: '0.75rem 1.5rem' }}
        >
          Try Again
        </button>
      </div>
    </div>
  );
}

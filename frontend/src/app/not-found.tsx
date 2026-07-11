'use client';

export default function NotFound() {
  return (
    <div style={{
      minHeight: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontFamily: 'system-ui, -apple-system, sans-serif',
    }}>
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        <h1 style={{ fontSize: '4rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.5rem' }}>
          404
        </h1>
        <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', marginBottom: '1.5rem' }}>
          Page not found
        </p>
        <a
          href="/"
          className="btn-primary"
          style={{ padding: '0.75rem 1.5rem', textDecoration: 'none' }}
        >
          Go Home
        </a>
      </div>
    </div>
  );
}

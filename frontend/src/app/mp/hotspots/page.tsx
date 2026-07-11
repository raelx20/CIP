'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, Hotspot } from '@/lib/api/client';
import { useEffect, useState } from 'react';

export default function MpHotspotsPage() {
  const { token } = useAuth();
  const [hotspots, setHotspots] = useState<Hotspot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selected, setSelected] = useState<Hotspot | null>(null);

  useEffect(() => {
    if (!token) return;
    setLoading(true);
    mp.getHotspots('', token)
      .then((data) => setHotspots(data.hotspots || []))
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [token]);

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading hotspots...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ padding: '2rem', textAlign: 'center' }}>
        <p style={{ color: 'var(--critical)' }}>Failed to load hotspots: {error}</p>
      </div>
    );
  }

  return (
    <div style={{ display: 'flex', gap: '1.5rem', height: 'calc(100vh - 120px)' }}>
      {/* Map placeholder */}
      <div style={{
        flex: 1,
        background: 'var(--surface)',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
          <p style={{ fontSize: '1.125rem', marginBottom: '0.5rem' }}>Geospatial Intelligence Map</p>
          <p style={{ fontSize: '0.875rem' }}>Map integration with MapLibre GL JS</p>
          {hotspots.length > 0 && (
            <p style={{ fontSize: '0.8125rem', marginTop: '0.5rem' }}>{hotspots.length} hotspot locations</p>
          )}
        </div>
      </div>

      {/* Hotspot list panel */}
      <div style={{ width: '320px', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
        <div style={{ marginBottom: '1rem' }}>
          <h1 style={{ fontSize: '1.375rem', fontWeight: 700, marginBottom: '0.25rem' }}>Hotspots</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.8125rem' }}>
            {hotspots.length} geographic clusters
          </p>
        </div>

        <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
          {!hotspots.length ? (
            <div className="card" style={{ textAlign: 'center', padding: '2rem' }}>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>No hotspots found.</p>
            </div>
          ) : (
            hotspots.map((h) => (
              <div
                key={h.cluster_id}
                className="card"
                style={{
                  cursor: 'pointer',
                  transition: 'all 0.15s',
                  border: selected?.cluster_id === h.cluster_id ? '2px solid var(--action-primary)' : undefined,
                }}
                onClick={() => setSelected(h)}
              >
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.25rem' }}>{h.title}</h3>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{h.category.replace(/_/g, ' ')}</p>
                  </div>
                  <span className="badge badge-neutral" style={{ fontSize: '0.6875rem' }}>
                    {h.submission_count} reports
                  </span>
                </div>
                <div style={{ display: 'flex', gap: '0.75rem', marginTop: '0.5rem', fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                  {h.severity && <span>Severity: {h.severity}/10</span>}
                  {h.urgency && <span>Urgency: {h.urgency}/10</span>}
                </div>
                {h.latitude && h.longitude && (
                  <div style={{ fontSize: '0.6875rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>
                    {h.latitude.toFixed(4)}, {h.longitude.toFixed(4)}
                  </div>
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

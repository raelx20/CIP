'use client';

import { useAuth } from '@/lib/auth/context';
import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function Home() {
  const { user, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && user) {
      if (user.role === 'citizen') router.push('/citizen');
      else if (user.role === 'mp') router.push('/mp');
      else if (user.role === 'admin') router.push('/admin');
      else if (user.role === 'officer') router.push('/officer');
    }
  }, [user, isLoading, router]);

  if (isLoading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <p style={{ color: 'var(--text-muted)' }}>Loading...</p>
      </div>
    );
  }

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      <header style={{ 
        padding: '1rem 2rem', 
        display: 'flex', 
        justifyContent: 'space-between', 
        alignItems: 'center',
        borderBottom: '1px solid var(--border)'
      }}>
        <div style={{ fontSize: '1.25rem', fontWeight: 600, color: 'var(--action-primary)' }}>
          CIP
        </div>
        <div style={{ display: 'flex', gap: '1rem' }}>
          <a href="/login" className="btn-secondary" style={{ textDecoration: 'none' }}>Sign In</a>
          <a href="/register" className="btn-primary" style={{ textDecoration: 'none' }}>Get Started</a>
        </div>
      </header>

      <main style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '4rem 2rem' }}>
        <div style={{ maxWidth: '640px', textAlign: 'center' }}>
          <h1 style={{ fontSize: '3rem', fontWeight: 700, lineHeight: 1.1, marginBottom: '1.5rem', color: 'var(--text-primary)' }}>
            Your Voice, Your Development
          </h1>
          <p style={{ fontSize: '1.125rem', color: 'var(--text-secondary)', marginBottom: '2rem', lineHeight: 1.6 }}>
            Report local issues, track development needs, and help your representatives make data-driven decisions for your community.
          </p>
          
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', marginBottom: '3rem' }}>
            <a href="/citizen/submit" className="btn-primary" style={{ textDecoration: 'none', padding: '0.875rem 2rem', fontSize: '1rem' }}>
              Submit a Request
            </a>
            <a href="/citizen/track" className="btn-secondary" style={{ textDecoration: 'none', padding: '0.875rem 2rem', fontSize: '1rem' }}>
              Track Request
            </a>
          </div>

          <div style={{ 
            background: 'var(--surface)', 
            border: '1px solid var(--border)', 
            borderRadius: 'var(--radius-lg)', 
            padding: '2rem',
            textAlign: 'left'
          }}>
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>How CIP Works</h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <span style={{ 
                  background: 'var(--action-primary)', 
                  color: 'white', 
                  width: '28px', 
                  height: '28px', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  flexShrink: 0
                }}>1</span>
                <div>
                  <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.25rem' }}>Submit Your Issue</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Describe your development need in your language - text, voice, or photo.</p>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <span style={{ 
                  background: 'var(--action-primary)', 
                  color: 'white', 
                  width: '28px', 
                  height: '28px', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  flexShrink: 0
                }}>2</span>
                <div>
                  <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.25rem' }}>AI Processes & Verifies</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Our AI understands your issue, verifies location, and consolidates similar reports.</p>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start' }}>
                <span style={{ 
                  background: 'var(--action-primary)', 
                  color: 'white', 
                  width: '28px', 
                  height: '28px', 
                  borderRadius: '50%', 
                  display: 'flex', 
                  alignItems: 'center', 
                  justifyContent: 'center',
                  fontSize: '0.875rem',
                  fontWeight: 600,
                  flexShrink: 0
                }}>3</span>
                <div>
                  <h3 style={{ fontSize: '0.9375rem', fontWeight: 600, marginBottom: '0.25rem' }}>Prioritized for Action</h3>
                  <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Issues are ranked by urgency, impact, and evidence for MP decision-making.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </main>

      <footer style={{ 
        padding: '1.5rem 2rem', 
        borderTop: '1px solid var(--border)', 
        textAlign: 'center',
        fontSize: '0.875rem',
        color: 'var(--text-muted)'
      }}>
        Constituency Intelligence Platform - Empowering Data-Driven Governance
      </footer>
    </div>
  );
}

'use client';

import { useAuth } from '@/lib/auth/context';
import { admin, CopilotCitation } from '@/lib/api/client';
import { useState, useRef, useEffect } from 'react';

interface CopilotMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: CopilotCitation[];
  uncertainty?: string;
}

export default function AdminCopilotPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    const q = input.trim();
    if (!q || !token) return;

    setMessages((prev) => [...prev, { role: 'user', content: q }]);
    setInput('');
    setLoading(true);

    try {
      const response = await admin.copilot({ query: q }, token);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: response.answer,
          citations: response.citations,
          uncertainty: response.uncertainty,
        },
      ]);
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: 'Sorry, I encountered an error. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      <h1 style={{ fontSize: '1.375rem', fontWeight: 700, marginBottom: '1rem' }}>Admin Copilot</h1>

      <div style={{
        flex: 1,
        overflowY: 'auto',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '1rem',
        background: 'var(--surface)',
        marginBottom: '1rem',
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            Ask questions about the system data.
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '1rem' }}>
            <div style={{ display: 'flex', justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start' }}>
              <div style={{
                maxWidth: '75%',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-lg)',
                background: msg.role === 'user' ? 'var(--action-primary)' : 'var(--surface-subtle)',
                color: msg.role === 'user' ? 'white' : 'var(--text-primary)',
              }}>
                {msg.content}
              </div>
            </div>
            {msg.role === 'assistant' && msg.citations && msg.citations.length > 0 && (
              <div style={{ marginTop: '0.5rem', paddingLeft: '1rem' }}>
                {msg.citations.map((c, ci) => (
                  <span key={ci} className="badge badge-neutral" style={{ marginRight: '0.5rem', fontSize: '0.6875rem' }}>
                    {c.source_name}
                  </span>
                ))}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-lg)', background: 'var(--surface-subtle)' }}>
              <span style={{ color: 'var(--text-muted)' }}>Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          className="input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Ask about system data..."
          disabled={loading}
        />
        <button onClick={sendMessage} className="btn-primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </div>
    </div>
  );
}

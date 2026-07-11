'use client';

import { useAuth } from '@/lib/auth/context';
import { mp, CopilotCitation } from '@/lib/api/client';
import { useState, useRef, useEffect } from 'react';

interface CopilotMessage {
  role: 'user' | 'assistant';
  content: string;
  citations?: CopilotCitation[];
  uncertainty?: string;
}

const SUGGESTIONS = [
  'What are the highest-priority development works this month?',
  'Which areas have recurring drinking-water problems?',
  'Which high-priority issues lack officer verification?',
  'What are the most common categories of complaints?',
];

export default function MpCopilotPage() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<CopilotMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async (query?: string) => {
    const q = query || input.trim();
    if (!q || !token) return;

    const userMsg: CopilotMessage = { role: 'user', content: q };
    setMessages((prev) => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const response = await mp.copilot({ query: q }, token);
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
        { role: 'assistant', content: 'Sorry, I encountered an error processing your query. Please try again.' },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 120px)' }}>
      <div style={{ marginBottom: '1rem' }}>
        <h1 style={{ fontSize: '1.375rem', fontWeight: 700, marginBottom: '0.25rem' }}>MP Copilot</h1>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>
          Ask questions about your constituency data and get evidence-grounded answers.
        </p>
      </div>

      {/* Chat area */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        border: '1px solid var(--border)',
        borderRadius: 'var(--radius-lg)',
        padding: '1rem',
        background: 'var(--surface)',
        marginBottom: '1rem',
      }}>
        {messages.length === 0 && !loading && (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '1rem', color: 'var(--text-primary)' }}>
              How can I help you today?
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', maxWidth: '480px', margin: '0 auto' }}>
              {SUGGESTIONS.map((s) => (
                <button
                  key={s}
                  onClick={() => sendMessage(s)}
                  style={{
                    padding: '0.75rem 1rem',
                    border: '1px solid var(--border)',
                    borderRadius: 'var(--radius-md)',
                    background: 'var(--surface)',
                    cursor: 'pointer',
                    textAlign: 'left',
                    fontSize: '0.875rem',
                    color: 'var(--text-secondary)',
                    transition: 'all 0.15s',
                  }}
                >
                  {s}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div key={i} style={{ marginBottom: '1rem' }}>
            <div style={{
              display: 'flex',
              justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
            }}>
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
                <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>Sources:</p>
                {msg.citations.map((c, ci) => (
                  <span key={ci} className="badge badge-neutral" style={{ marginRight: '0.5rem', marginBottom: '0.25rem', fontSize: '0.6875rem' }}>
                    {c.source_name}: {(c.confidence * 100).toFixed(0)}%
                  </span>
                ))}
              </div>
            )}
            {msg.role === 'assistant' && msg.uncertainty && (
              <div style={{ marginTop: '0.5rem', paddingLeft: '1rem' }}>
                <span style={{ fontSize: '0.75rem', color: 'var(--warning)' }}>
                  Uncertainty: {msg.uncertainty}
                </span>
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ display: 'flex', justifyContent: 'flex-start', marginBottom: '1rem' }}>
            <div style={{ padding: '0.75rem 1rem', borderRadius: 'var(--radius-lg)', background: 'var(--surface-subtle)' }}>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Thinking...</span>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={{ display: 'flex', gap: '0.75rem' }}>
        <input
          type="text"
          className="input-field"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && !loading && sendMessage()}
          placeholder="Ask about constituency issues, priorities, trends..."
          disabled={loading}
        />
        <button
          onClick={() => sendMessage()}
          className="btn-primary"
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}

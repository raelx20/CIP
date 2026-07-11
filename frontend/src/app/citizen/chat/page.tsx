'use client';

import { useState, useRef, useEffect } from 'react';
import { useAuth } from '@/lib/auth/context';
import { citizen, ChatMessage } from '@/lib/api/client';

export default function CitizenChat() {
  const { token } = useAuth();
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || !token) return;

    const userMessage: ChatMessage = { role: 'citizen', content: input };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      const response = await citizen.chat(
        { role: 'citizen', content: input, detected_language: 'en' },
        token
      );
      setMessages((prev) => [...prev, response.message]);
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
      <h1 style={{ fontSize: '1.5rem', fontWeight: 700, marginBottom: '1rem' }}>AI Assistant</h1>
      
      <div style={{ 
        flex: 1, 
        overflowY: 'auto', 
        border: '1px solid var(--border)', 
        borderRadius: 'var(--radius-lg)', 
        padding: '1rem',
        background: 'var(--surface)',
        marginBottom: '1rem'
      }}>
        {messages.length === 0 && (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-muted)' }}>
            <p style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Hello! I&apos;m here to help you report local issues.</p>
            <p style={{ fontSize: '0.875rem' }}>Describe the problem you&apos;re facing, and I&apos;ll guide you through the process.</p>
          </div>
        )}
        
        {messages.map((msg, i) => (
          <div
            key={i}
            style={{
              display: 'flex',
              justifyContent: msg.role === 'citizen' ? 'flex-end' : 'flex-start',
              marginBottom: '1rem',
            }}
          >
            <div
              style={{
                maxWidth: '70%',
                padding: '0.75rem 1rem',
                borderRadius: 'var(--radius-lg)',
                background: msg.role === 'citizen' ? 'var(--action-primary)' : 'var(--surface-subtle)',
                color: msg.role === 'citizen' ? 'white' : 'var(--text-primary)',
              }}
            >
              {msg.content}
            </div>
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
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Describe your issue..."
          disabled={loading}
        />
        <button 
          onClick={sendMessage} 
          className="btn-primary"
          disabled={loading || !input.trim()}
        >
          Send
        </button>
      </div>
    </div>
  );
}

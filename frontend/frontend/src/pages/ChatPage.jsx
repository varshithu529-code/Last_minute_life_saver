import { useState } from 'react';
import { api } from '../services/api';

export default function ChatPage() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Hi! I\'m your productivity companion. Ask about conflicts, deadlines, or meeting prep.',
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);

  const send = async (e) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    const userMsg = input.trim();
    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.chat(userMsg);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: res.reply,
          confidence: res.confidence,
        },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Error: ${err.message}`, error: true },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-page">
      <header className="page-header">
        <h1>Chat</h1>
        <p>Powered by Azure OpenAI GPT-4o with confidence guardrails</p>
      </header>

      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={`bubble ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.confidence != null && (
              <span className="confidence">Confidence: {(msg.confidence * 100).toFixed(0)}%</span>
            )}
          </div>
        ))}
        {loading && <div className="bubble assistant"><p>Thinking…</p></div>}
      </div>

      <form onSubmit={send} className="chat-input">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your schedule or tasks…"
          disabled={loading}
        />
        <button type="submit" className="primary" disabled={loading}>
          Send
        </button>
      </form>

      <p className="voice-note">
        Voice interface: integrate Azure Speech SDK via <code>microsoft-cognitiveservices-speech-sdk</code>
      </p>

      <style>{`
        .page-header { margin-bottom: 1.5rem; }
        .page-header h1 { font-size: 1.75rem; }
        .page-header p { color: var(--text-muted); margin-top: 0.25rem; }
        .chat-window {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem;
          min-height: 400px;
          max-height: 60vh;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin-bottom: 1rem;
        }
        .bubble {
          max-width: 85%;
          padding: 0.75rem 1rem;
          border-radius: 12px;
          font-size: 0.9rem;
        }
        .bubble.user {
          align-self: flex-end;
          background: var(--accent);
          color: white;
        }
        .bubble.assistant {
          align-self: flex-start;
          background: var(--bg);
          border: 1px solid var(--border);
        }
        .confidence { display: block; font-size: 0.7rem; color: var(--text-muted); margin-top: 0.5rem; }
        .chat-input { display: flex; gap: 0.5rem; }
        .chat-input input { flex: 1; }
        .voice-note {
          margin-top: 1rem;
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .voice-note code {
          background: var(--surface);
          padding: 0.125rem 0.375rem;
          border-radius: 4px;
        }
      `}</style>
    </div>
  );
}

import { useCallback, useEffect, useState } from 'react';
import { api } from '../services/api';
import ImpactMetrics from '../components/ImpactMetrics';
import ChatEntry from '../components/ChatEntry';
import ActionCardsPanel from '../components/ActionCardsPanel';

const WELCOME = {
  role: 'assistant',
  content:
    'Hi! I\'m Last Minute Life Saver. Try "Rescue my deadline", "Prep me for meeting", or "Resolve conflict" — I\'ll act, not just remind.',
};

export default function Dashboard() {
  const [metrics, setMetrics] = useState(null);
  const [messages, setMessages] = useState([WELCOME]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [actionCards, setActionCards] = useState([]);
  const [liveSummary, setLiveSummary] = useState(null);
  const [toast, setToast] = useState(null);
  const [error, setError] = useState(null);

  const refreshMetrics = useCallback(() => {
    api.getMetrics().then(setMetrics).catch(console.error);
  }, []);

  useEffect(() => {
    refreshMetrics();
  }, [refreshMetrics]);

  const showToast = (msg) => {
    setToast(msg);
    setTimeout(() => setToast(null), 3000);
  };

  const sendMessage = async (text) => {
    const userMsg = (text || input).trim();
    if (!userMsg || loading) return;

    setInput('');
    setMessages((prev) => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);
    setError(null);

    try {
      const res = await api.chat(userMsg);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: res.reply, confidence: res.confidence },
      ]);
      if (res.action_cards?.length) {
        setActionCards(res.action_cards);
      }
      if (res.summary) {
        setLiveSummary(res.summary);
      }
      refreshMetrics();
    } catch (e) {
      setError(e.message);
      setMessages((prev) => [
        ...prev,
        { role: 'assistant', content: `Something went wrong: ${e.message}` },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="wireframe-dashboard">
      <header className="page-header">
        <h1>Last Minute Life Saver</h1>
        <p>This bot doesn&apos;t just remind you — it saves you.</p>
      </header>

      <ImpactMetrics metrics={metrics} liveSummary={liveSummary} />

      <ChatEntry
        messages={messages}
        loading={loading}
        input={input}
        onInputChange={setInput}
        onSend={() => sendMessage()}
        onQuickPrompt={sendMessage}
      />

      {error && <div className="error">{error}</div>}
      {toast && <div className="toast">{toast}</div>}

      <ActionCardsPanel cards={actionCards} onToast={showToast} />

      <style>{`
        .page-header { margin-bottom: 1.5rem; }
        .page-header h1 { font-size: 1.75rem; font-weight: 700; }
        .page-header p { color: var(--text-muted); margin-top: 0.25rem; }
        .error {
          background: rgba(239, 68, 68, 0.15);
          border: 1px solid var(--danger);
          padding: 0.75rem 1rem;
          border-radius: 8px;
          margin-bottom: 1rem;
        }
        .toast {
          position: fixed;
          bottom: 1.5rem;
          right: 1.5rem;
          background: var(--success);
          color: #000;
          padding: 0.75rem 1.25rem;
          border-radius: 8px;
          font-size: 0.875rem;
          font-weight: 600;
          z-index: 100;
          animation: slideIn 0.2s ease;
        }
        @keyframes slideIn {
          from { transform: translateY(12px); opacity: 0; }
          to { transform: translateY(0); opacity: 1; }
        }
      `}</style>
    </div>
  );
}

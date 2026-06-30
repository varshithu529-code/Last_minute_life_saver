const QUICK_PROMPTS = [
  'Rescue my deadline',
  'Prep me for meeting',
  'Resolve conflict',
  'Save my day',
];

export default function ChatEntry({ messages, loading, input, onInputChange, onSend, onQuickPrompt }) {
  return (
    <section className="chat-entry">
      <h2>Ask your companion</h2>
      <p className="hint">Natural language entry point — the bot responds with proactive actions.</p>

      <div className="quick-prompts">
        {QUICK_PROMPTS.map((prompt) => (
          <button
            key={prompt}
            type="button"
            className="chip"
            onClick={() => onQuickPrompt(prompt)}
            disabled={loading}
          >
            {prompt}
          </button>
        ))}
      </div>

      <div className="chat-window">
        {messages.map((msg, i) => (
          <div key={i} className={`bubble ${msg.role}`}>
            <p>{msg.content}</p>
            {msg.confidence != null && (
              <span className="confidence">Confidence: {(msg.confidence * 100).toFixed(0)}%</span>
            )}
          </div>
        ))}
        {loading && (
          <div className="bubble assistant">
            <p>Working on it…</p>
          </div>
        )}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          onSend();
        }}
        className="chat-input"
      >
        <input
          value={input}
          onChange={(e) => onInputChange(e.target.value)}
          placeholder='Try "Rescue my deadline" or "Prep me for meeting"'
          disabled={loading}
        />
        <button type="submit" className="primary" disabled={loading || !input.trim()}>
          Send
        </button>
      </form>

      <style>{`
        .chat-entry {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1.25rem 1.5rem;
          margin-bottom: 1.5rem;
        }
        .chat-entry h2 { font-size: 1rem; margin-bottom: 0.25rem; }
        .hint { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 1rem; }
        .quick-prompts {
          display: flex;
          flex-wrap: wrap;
          gap: 0.5rem;
          margin-bottom: 1rem;
        }
        .chip {
          background: var(--bg);
          border: 1px solid var(--border);
          color: var(--text);
          padding: 0.375rem 0.75rem;
          font-size: 0.8rem;
          border-radius: 999px;
        }
        .chip:hover:not(:disabled) {
          border-color: var(--accent);
          color: var(--accent);
        }
        .chat-window {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 1rem;
          min-height: 160px;
          max-height: 280px;
          overflow-y: auto;
          display: flex;
          flex-direction: column;
          gap: 0.75rem;
          margin-bottom: 0.75rem;
        }
        .bubble {
          max-width: 90%;
          padding: 0.75rem 1rem;
          border-radius: 12px;
          font-size: 0.875rem;
          line-height: 1.45;
        }
        .bubble.user {
          align-self: flex-end;
          background: var(--accent);
          color: white;
        }
        .bubble.assistant {
          align-self: flex-start;
          background: var(--surface);
          border: 1px solid var(--border);
        }
        .confidence {
          display: block;
          font-size: 0.7rem;
          color: var(--text-muted);
          margin-top: 0.5rem;
        }
        .chat-input { display: flex; gap: 0.5rem; }
        .chat-input input { flex: 1; }
      `}</style>
    </section>
  );
}

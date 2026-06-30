import { useState } from 'react';

export default function DeadlineCard({ card, onPreview, onSend }) {
  const [showPreview, setShowPreview] = useState(false);

  return (
    <article className="action-card deadline">
      <div className="card-icon">✉️</div>
      <div className="card-body">
        <h3>{card.title}</h3>
        <p className="subtitle">{card.subtitle} · {card.action}</p>
        {showPreview && (
          <div className="preview">
            <pre>{card.draft_email}</pre>
          </div>
        )}
        <div className="card-actions">
          <button
            type="button"
            className="secondary"
            onClick={() => {
              setShowPreview(!showPreview);
              onPreview?.();
            }}
          >
            {showPreview ? 'Hide Email' : 'Preview Email'}
          </button>
          <button type="button" className="primary" onClick={onSend}>Send</button>
        </div>
      </div>
      <style>{`
        .action-card {
          display: flex;
          gap: 1rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-left: 3px solid var(--danger);
          border-radius: var(--radius);
          padding: 1rem 1.25rem;
        }
        .card-icon { font-size: 1.5rem; }
        .card-body { flex: 1; }
        .card-body h3 { font-size: 0.95rem; margin-bottom: 0.25rem; }
        .subtitle { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
        .preview {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 0.75rem;
          margin-bottom: 0.75rem;
          max-height: 120px;
          overflow-y: auto;
        }
        .preview pre {
          font-family: inherit;
          font-size: 0.8rem;
          white-space: pre-wrap;
          color: var(--text-muted);
          margin: 0;
        }
        .card-actions { display: flex; gap: 0.5rem; }
      `}</style>
    </article>
  );
}

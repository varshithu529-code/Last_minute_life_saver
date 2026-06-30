import { useState } from 'react';

export default function PrepCard({ card, onOpenNotes }) {
  const [open, setOpen] = useState(false);

  return (
    <article className="action-card prep">
      <div className="card-icon">📋</div>
      <div className="card-body">
        <h3>{card.title}</h3>
        <p className="subtitle">{card.subtitle}</p>
        <p className="action-text">{card.action}</p>
        {open && (
          <div className="notes-panel">
            {card.previous_notes && (
              <div className="notes-block">
                <strong>Last notes</strong>
                <p>{card.previous_notes}</p>
              </div>
            )}
            <div className="notes-block">
              <strong>Prep checklist</strong>
              <p>{card.prep_checklist}</p>
            </div>
          </div>
        )}
        <div className="card-actions">
          <button
            type="button"
            className="primary"
            onClick={() => {
              setOpen(true);
              onOpenNotes?.();
            }}
          >
            Open Notes
          </button>
        </div>
      </div>
      <style>{`
        .action-card {
          display: flex;
          gap: 1rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-left: 3px solid var(--accent);
          border-radius: var(--radius);
          padding: 1rem 1.25rem;
        }
        .card-icon { font-size: 1.5rem; }
        .card-body { flex: 1; }
        .card-body h3 { font-size: 0.95rem; margin-bottom: 0.25rem; }
        .subtitle { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
        .action-text { font-size: 0.875rem; margin-bottom: 0.75rem; }
        .notes-panel {
          background: var(--bg);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 0.75rem;
          margin-bottom: 0.75rem;
          max-height: 180px;
          overflow-y: auto;
        }
        .notes-block { margin-bottom: 0.75rem; }
        .notes-block strong {
          display: block;
          font-size: 0.7rem;
          text-transform: uppercase;
          color: var(--accent);
          margin-bottom: 0.25rem;
        }
        .notes-block p { font-size: 0.8rem; color: var(--text-muted); white-space: pre-wrap; }
        .card-actions { display: flex; gap: 0.5rem; }
      `}</style>
    </article>
  );
}

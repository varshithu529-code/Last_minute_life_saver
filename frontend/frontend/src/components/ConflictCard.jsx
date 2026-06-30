export default function ConflictCard({ card, onUndo, onConfirm }) {
  return (
    <article className="action-card conflict">
      <div className="card-icon">📅</div>
      <div className="card-body">
        <h3>{card.title}</h3>
        <p className="subtitle">{card.subtitle}</p>
        <p className="action-text">{card.action}</p>
        <div className="card-actions">
          <button type="button" className="secondary" onClick={onUndo}>Undo</button>
          <button type="button" className="primary" onClick={onConfirm}>Confirm</button>
        </div>
      </div>
      <style>{`
        .action-card {
          display: flex;
          gap: 1rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-left: 3px solid var(--warning);
          border-radius: var(--radius);
          padding: 1rem 1.25rem;
        }
        .card-icon { font-size: 1.5rem; }
        .card-body { flex: 1; }
        .card-body h3 { font-size: 0.95rem; margin-bottom: 0.25rem; }
        .subtitle { font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem; }
        .action-text { font-size: 0.875rem; margin-bottom: 0.75rem; }
        .card-actions { display: flex; gap: 0.5rem; }
      `}</style>
    </article>
  );
}

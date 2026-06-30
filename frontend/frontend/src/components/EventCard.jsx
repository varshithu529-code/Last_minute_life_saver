export default function EventCard({ event }) {
  const start = new Date(event.start_time);
  const end = new Date(event.end_time);

  return (
    <article className={`event-card ${event.has_conflict ? 'conflict' : ''}`}>
      <div className="time">
        <span>{start.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
        <span className="dash">–</span>
        <span>{end.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
      </div>
      <div className="details">
        <h3>{event.title}</h3>
        <p>{start.toLocaleDateString()} {event.location && `· ${event.location}`}</p>
        {event.has_conflict && <span className="badge badge-conflict">Conflict</span>}
      </div>
      <style>{`
        .event-card {
          display: flex;
          gap: 1rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem 1.25rem;
        }
        .event-card.conflict { border-color: var(--warning); }
        .time {
          display: flex;
          flex-direction: column;
          align-items: center;
          font-size: 0.85rem;
          font-weight: 600;
          min-width: 4rem;
          color: var(--accent);
        }
        .dash { color: var(--text-muted); font-weight: 400; }
        .details h3 { font-size: 0.95rem; margin-bottom: 0.25rem; }
        .details p { font-size: 0.8rem; color: var(--text-muted); }
      `}</style>
    </article>
  );
}

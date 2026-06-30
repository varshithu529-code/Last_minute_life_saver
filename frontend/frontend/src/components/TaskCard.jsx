const PRIORITY_LABELS = {
  urgent_important: 'Do First',
  not_urgent_important: 'Schedule',
  urgent_not_important: 'Delegate',
  not_urgent_not_important: 'Eliminate',
};

export default function TaskCard({ task }) {
  const priorityClass = task.priority?.includes('urgent') ? 'badge-urgent' : 'badge-important';

  return (
    <article className="task-card">
      <header>
        <h3>{task.title}</h3>
        {task.priority && (
          <span className={`badge ${priorityClass}`}>
            {PRIORITY_LABELS[task.priority] || task.priority}
          </span>
        )}
      </header>
      {task.description && <p>{task.description}</p>}
      <footer>
        <span>Score: {(task.ml_score * 100).toFixed(0)}%</span>
        {task.due_date && (
          <span>Due: {new Date(task.due_date).toLocaleDateString()}</span>
        )}
        <span className={`status status-${task.status}`}>{task.status}</span>
      </footer>
      <style>{`
        .task-card {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem 1.25rem;
        }
        .task-card header {
          display: flex;
          justify-content: space-between;
          align-items: flex-start;
          gap: 0.75rem;
          margin-bottom: 0.5rem;
        }
        .task-card h3 { font-size: 1rem; font-weight: 600; }
        .task-card p { color: var(--text-muted); font-size: 0.875rem; margin-bottom: 0.75rem; }
        .task-card footer {
          display: flex;
          gap: 1rem;
          font-size: 0.8rem;
          color: var(--text-muted);
        }
        .status { text-transform: capitalize; }
        .status-done { color: var(--success); }
        .status-blocked { color: var(--danger); }
      `}</style>
    </article>
  );
}

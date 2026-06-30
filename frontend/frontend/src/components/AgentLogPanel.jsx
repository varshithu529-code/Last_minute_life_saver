import { useEffect, useState } from 'react';
import { api } from '../services/api';

export default function AgentLogPanel() {
  const [logs, setLogs] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getAgentLogs()
      .then(setLogs)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  if (loading) return <p className="muted">Loading agent activity…</p>;

  return (
    <section className="log-panel">
      <h2>Agent Activity</h2>
      {logs.length === 0 ? (
        <p className="muted">No actions yet. Run the agent workflow to see activity.</p>
      ) : (
        <ul>
          {logs.map((log) => (
            <li key={log.id}>
              <span className="action-type">{log.action_type}</span>
              <span className="desc">{log.description}</span>
              <span className="meta">
                {(log.confidence * 100).toFixed(0)}% · {log.status}
              </span>
            </li>
          ))}
        </ul>
      )}
      <style>{`
        .log-panel h2 { font-size: 1.1rem; margin-bottom: 1rem; }
        .log-panel ul { list-style: none; display: flex; flex-direction: column; gap: 0.5rem; }
        .log-panel li {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: 8px;
          padding: 0.75rem 1rem;
          display: grid;
          gap: 0.25rem;
        }
        .action-type {
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--accent);
          font-weight: 600;
        }
        .desc { font-size: 0.875rem; }
        .meta { font-size: 0.75rem; color: var(--text-muted); }
        .muted { color: var(--text-muted); font-size: 0.875rem; }
      `}</style>
    </section>
  );
}

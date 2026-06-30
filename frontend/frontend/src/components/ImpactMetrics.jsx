export default function ImpactMetrics({ metrics, liveSummary }) {
  const m = metrics || {};
  const conflicts = liveSummary?.conflicts_resolved ?? m.conflicts_resolved ?? 0;
  const deadlines = liveSummary?.deadlines_rescued ?? m.deadlines_rescued ?? 0;
  const preps = liveSummary?.meetings_prepped ?? m.meetings_prepped ?? 0;
  const focus = m.focus_score ?? 85;
  const streak = m.streak_days ?? 0;

  return (
    <section className="impact-metrics">
      <div className="metrics-row">
        <div className="metric">
          <span className="value">{conflicts}</span>
          <span className="label">Conflicts Resolved</span>
        </div>
        <div className="metric">
          <span className="value">{deadlines}</span>
          <span className="label">Deadlines Rescued</span>
        </div>
        <div className="metric">
          <span className="value">{preps}</span>
          <span className="label">Meetings Prepped</span>
        </div>
      </div>
      <div className="gamification">
        <div className="game-stat">
          <span className="game-label">Focus Score</span>
          <div className="focus-bar">
            <div className="focus-fill" style={{ width: `${focus}%` }} />
          </div>
          <span className="game-value">{focus}/100</span>
        </div>
        <div className="game-stat streak">
          <span className="game-label">Streak</span>
          <span className="game-value">🔥 {streak} days rescued</span>
        </div>
      </div>
      <style>{`
        .impact-metrics {
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1.25rem 1.5rem;
          margin-bottom: 1.5rem;
        }
        .metrics-row {
          display: grid;
          grid-template-columns: repeat(3, 1fr);
          gap: 1rem;
          margin-bottom: 1.25rem;
          padding-bottom: 1.25rem;
          border-bottom: 1px solid var(--border);
        }
        .metric { text-align: center; }
        .metric .value {
          display: block;
          font-size: 1.75rem;
          font-weight: 700;
          color: var(--accent);
        }
        .metric .label {
          font-size: 0.75rem;
          color: var(--text-muted);
          text-transform: uppercase;
          letter-spacing: 0.04em;
        }
        .gamification {
          display: flex;
          gap: 2rem;
          align-items: center;
          flex-wrap: wrap;
        }
        .game-stat { flex: 1; min-width: 140px; }
        .game-label {
          display: block;
          font-size: 0.7rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-muted);
          margin-bottom: 0.35rem;
        }
        .focus-bar {
          height: 8px;
          background: var(--bg);
          border-radius: 999px;
          overflow: hidden;
          margin-bottom: 0.25rem;
        }
        .focus-fill {
          height: 100%;
          background: linear-gradient(90deg, var(--accent), var(--success));
          border-radius: 999px;
          transition: width 0.4s ease;
        }
        .game-value { font-size: 0.9rem; font-weight: 600; }
        .streak .game-value { color: var(--warning); }
      `}</style>
    </section>
  );
}

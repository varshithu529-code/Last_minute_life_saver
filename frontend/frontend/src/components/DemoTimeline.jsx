export default function DemoTimeline({ steps, icons }) {
  return (
    <section className="timeline">
      <h2>Proactive interventions</h2>
      <ol>
        {steps.map((step) => (
          <li key={step.step} className={`step step-${step.status}`}>
            <span className="icon">{icons[step.icon] || '•'}</span>
            <div className="content">
              <strong>{step.title}</strong>
              <p>{step.detail}</p>
              {step.prep_checklist && (
                <p className="extra">{step.prep_checklist}…</p>
              )}
            </div>
          </li>
        ))}
      </ol>
      <style>{`
        .timeline { margin-bottom: 2rem; }
        .timeline h2 { font-size: 1rem; margin-bottom: 1rem; }
        .timeline ol { list-style: none; display: flex; flex-direction: column; gap: 0.75rem; }
        .step {
          display: flex;
          gap: 1rem;
          background: var(--surface);
          border: 1px solid var(--border);
          border-radius: var(--radius);
          padding: 1rem 1.25rem;
        }
        .step-completed { border-left: 3px solid var(--success); }
        .step-proposed { border-left: 3px solid var(--warning); }
        .icon { font-size: 1.25rem; }
        .content strong { display: block; font-size: 0.95rem; margin-bottom: 0.25rem; }
        .content p { font-size: 0.85rem; color: var(--text-muted); }
        .extra { margin-top: 0.5rem; font-style: italic; }
      `}</style>
    </section>
  );
}

import ConflictCard from './ConflictCard';
import DeadlineCard from './DeadlineCard';
import PrepCard from './PrepCard';

export default function ActionCardsPanel({ cards, onToast }) {
  if (!cards?.length) {
    return (
      <section className="action-panel empty">
        <p>Proactive actions will appear here when you ask for help.</p>
        <style>{`
          .action-panel.empty {
            border: 1px dashed var(--border);
            border-radius: var(--radius);
            padding: 2rem;
            text-align: center;
            color: var(--text-muted);
            font-size: 0.875rem;
          }
        `}</style>
      </section>
    );
  }

  return (
    <section className="action-panel">
      <h2>Dynamic Interventions</h2>
      <div className="cards-list">
        {cards.map((card) => {
          if (card.type === 'conflict') {
            return (
              <ConflictCard
                key={card.id}
                card={card}
                onUndo={() => onToast('Undo requested — calendar revert (demo).')}
                onConfirm={() => onToast('Reschedule confirmed!')}
              />
            );
          }
          if (card.type === 'deadline') {
            return (
              <DeadlineCard
                key={card.id}
                card={card}
                onPreview={() => {}}
                onSend={() => onToast('Email queued to send (demo).')}
              />
            );
          }
          if (card.type === 'prep') {
            return (
              <PrepCard
                key={card.id}
                card={card}
                onOpenNotes={() => {}}
              />
            );
          }
          return null;
        })}
      </div>
      <style>{`
        .action-panel { margin-bottom: 1.5rem; }
        .action-panel h2 {
          font-size: 0.85rem;
          text-transform: uppercase;
          letter-spacing: 0.05em;
          color: var(--text-muted);
          margin-bottom: 0.75rem;
        }
        .cards-list { display: flex; flex-direction: column; gap: 0.75rem; }
      `}</style>
    </section>
  );
}

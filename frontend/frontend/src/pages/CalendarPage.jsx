import { useEffect, useState } from 'react';
import { api } from '../services/api';
import EventCard from '../components/EventCard';

export default function CalendarPage() {
  const [events, setEvents] = useState([]);
  const [conflicts, setConflicts] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api.getEvents(), api.detectConflicts()])
      .then(([evts, conf]) => {
        setEvents(evts);
        setConflicts(conf);
      })
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <header className="page-header">
        <h1>Calendar</h1>
        <p>
          {conflicts.length > 0
            ? `${conflicts.length} conflict(s) detected — agent can propose reschedules`
            : 'No conflicts in the next 7 days'}
        </p>
      </header>

      {loading ? (
        <p className="muted">Loading events…</p>
      ) : (
        <div className="event-list">
          {events.map((event) => (
            <EventCard key={event.id} event={event} />
          ))}
        </div>
      )}

      <style>{`
        .page-header { margin-bottom: 1.5rem; }
        .page-header h1 { font-size: 1.75rem; }
        .page-header p { color: var(--text-muted); margin-top: 0.25rem; }
        .event-list { display: flex; flex-direction: column; gap: 0.75rem; }
        .muted { color: var(--text-muted); }
      `}</style>
    </div>
  );
}

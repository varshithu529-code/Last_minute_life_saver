import { useEffect, useState } from 'react';
import { api } from '../services/api';
import TaskCard from '../components/TaskCard';

export default function TasksPage() {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.getTasks(true)
      .then(setTasks)
      .catch(console.error)
      .finally(() => setLoading(false));
  }, []);

  return (
    <div>
      <header className="page-header">
        <h1>Tasks</h1>
        <p>Eisenhower Matrix prioritization · ML scoring</p>
      </header>

      {loading ? (
        <p className="muted">Loading tasks…</p>
      ) : (
        <div className="task-grid">
          {tasks.map((task) => (
            <TaskCard key={task.id} task={task} />
          ))}
        </div>
      )}

      <style>{`
        .page-header { margin-bottom: 1.5rem; }
        .page-header h1 { font-size: 1.75rem; }
        .page-header p { color: var(--text-muted); margin-top: 0.25rem; }
        .task-grid { display: grid; gap: 0.75rem; }
        .muted { color: var(--text-muted); }
      `}</style>
    </div>
  );
}

import { Link, useLocation } from 'react-router-dom';

const NAV = [
  { to: '/', label: 'Home' },
  { to: '/tasks', label: 'Tasks' },
  { to: '/calendar', label: 'Calendar' },
];

export default function Layout({ children }) {
  const location = useLocation();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-icon">⚡</span>
          <div>
            <strong>Last Minute</strong>
            <small>Life Saver</small>
          </div>
        </div>
        <nav>
          {NAV.map(({ to, label }) => (
            <Link
              key={to}
              to={to}
              className={location.pathname === to ? 'active' : ''}
            >
              {label}
            </Link>
          ))}
        </nav>
      </aside>
      <main className="main">{children}</main>
      <style>{`
        .layout { display: flex; min-height: 100vh; }
        .sidebar {
          width: 220px;
          background: var(--surface);
          border-right: 1px solid var(--border);
          padding: 1.5rem 1rem;
          display: flex;
          flex-direction: column;
          gap: 2rem;
        }
        .brand { display: flex; align-items: center; gap: 0.75rem; padding: 0 0.5rem; }
        .brand-icon { font-size: 1.5rem; }
        .brand strong { display: block; font-size: 0.95rem; }
        .brand small { color: var(--text-muted); font-size: 0.75rem; }
        nav { display: flex; flex-direction: column; gap: 0.25rem; }
        nav a {
          color: var(--text-muted);
          text-decoration: none;
          padding: 0.625rem 0.875rem;
          border-radius: 8px;
          font-weight: 500;
          font-size: 0.9rem;
        }
        nav a:hover { background: var(--surface-hover); color: var(--text); }
        nav a.active { background: var(--accent-soft); color: var(--accent); }
        .main { flex: 1; padding: 2rem; overflow-y: auto; }
      `}</style>
    </div>
  );
}

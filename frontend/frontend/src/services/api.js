const API_BASE = import.meta.env.VITE_API_URL || '/v1';

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { 'Content-Type': 'application/json', ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || `Request failed: ${res.status}`);
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getTasks: (prioritize = true) =>
    request(`/tasks?prioritize=${prioritize}`),

  getEvents: () => request('/events'),

  getAgentLogs: () => request('/agent/logs'),

  getMetrics: () => request('/agent/metrics'),

  runAgent: () => request('/agent/run', { method: 'POST' }),

  detectConflicts: () => request('/agent/conflicts'),

  chat: (message) =>
    request('/chat', {
      method: 'POST',
      body: JSON.stringify({ message }),
    }),

  health: () => request('/health'),
};

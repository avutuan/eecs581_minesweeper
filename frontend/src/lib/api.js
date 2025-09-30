const MODE = import.meta.env.VITE_API_MODE ?? 'demo'; // 'demo' or 'http'
const BASE = import.meta.env.VITE_API_BASE ?? '';

/* ============ HTTP MODE ============ */
async function send(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined
  });
  if (!res.ok) throw new Error(await res.text().catch(() => `HTTP ${res.status}`));
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

export const api = MODE === 'http' ? {
  newGame: (params) => send('/api/new', { method: 'POST', body: params }),
  state: () => send('/api/state'),
  click: (body) => send('/api/click', { method: 'POST', body }),
  toggleFlag: (body) => send('/api/flag', { method: 'POST', body }),
  aiMove: (difficulty) => send(`/api/ai/${difficulty}`),   // <-- NEW
} : {
  newGame: (params) => demo.newGame(params),
  state: () => demo.state(),
  click: (body) => demo.click(body),
  toggleFlag: (body) => demo.toggleFlag(body),
  aiMove: (difficulty) => demo.aiMove(difficulty),         // <-- NEW stub for demo mode
};

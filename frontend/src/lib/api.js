const MODE = import.meta.env.VITE_API_MODE ?? 'demo'; // 'demo' or 'http'
const BASE = import.meta.env.VITE_API_BASE ?? '';

/* ============ HTTP MODE (stub) ============ */
async function send(path, opts = {}) {
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined
  });
  if (!res.ok) throw new Error(await res.text().catch(()=>`HTTP ${res.status}`));
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

export const api = MODE === 'http' ? {
  newGame: (params) => send('/api/new', { method:'POST', body: params }),
  state: () => send('/api/state'),
  click: (body) => send('/api/click', { method:'POST', body }),
  toggleFlag: (body) => send('/api/flag', { method:'POST', body }),
} : {
  newGame: (params) => demo.newGame(params),
  state: () => demo.state(),
  click: (body) => demo.click(body),
  toggleFlag: (body) => demo.toggleFlag(body),
};

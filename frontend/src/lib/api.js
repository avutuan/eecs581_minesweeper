/*
Description: API interface for frontend to communicate with backend or demo mode.
Inputs: API mode and base URL from environment variables.
Outputs: API functions for game actions.
External Sources: N/A
Author(s): Nicholas Holmes, Kobe Jordan
Creation Date: 18 September 2025
*/

// Initialize environment variables
const MODE = import.meta.env.VITE_API_MODE ?? 'demo'; // 'demo' or 'http'
const BASE = import.meta.env.VITE_API_BASE ?? '';

// ============ HTTP MODE ============
// Send HTTP requests to the backend server.
async function send(path, opts = {}) {
  /* 
  Description: Send an HTTP request to the backend server.
  Inputs: API path and fetch options (method, body, etc.)
  Outputs: Parsed JSON or text response from the server.
  Throws: Error if the response is not OK.
  Author(s): Nicholas Holmes
  Creation Date: 18 September 2025
  */
  // Default options: JSON content type and include credentials
  const res = await fetch(BASE + path, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...opts,
    body: opts.body ? JSON.stringify(opts.body) : undefined
  });
  // Check for HTTP errors
  if (!res.ok) throw new Error(await res.text().catch(() => `HTTP ${res.status}`));
  // Parse response as JSON if possible, otherwise as text
  const ct = res.headers.get('content-type') || '';
  return ct.includes('application/json') ? res.json() : res.text();
}

// Export API functions for HTTP mode
export const api = MODE === 'http' ? {
  newGame: (params) => send('/api/new', { method: 'POST', body: params }),
  state: () => send('/api/state'),
  click: (body) => send('/api/click', { method: 'POST', body }),
  toggleFlag: (body) => send('/api/flag', { method: 'POST', body }),
  aiMove: (difficulty) => send(`/api/ai/${difficulty}`),   // <-- NEW
  aiTurn: () => send('/api/ai-turn', { method: 'POST' }),  // <-- NEW for co-op mode
} : {
  newGame: (params) => demo.newGame(params),
  state: () => demo.state(),
  click: (body) => demo.click(body),
  toggleFlag: (body) => demo.toggleFlag(body),
  aiMove: (difficulty) => demo.aiMove(difficulty),         // <-- NEW stub for demo mode
  aiTurn: () => demo.aiTurn(),                              // <-- NEW stub for demo mode
};
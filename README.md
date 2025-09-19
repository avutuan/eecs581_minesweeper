## EECS 581 Project 1: Minesweeper
### Group & Team Structure:
- **Project Coordinator:** Riley Meyerkorth
- **Backend Developer:** Aiden Burke
- **Backend Developer:** Brett Suhr
- **Frontend Developer:** Nick Holmes
- **Quality Assurance & Testing Lead:** Andrew Reyes
- **Documentation & Communication Lead:** Ty Farrington

### Roadmap (future enhancements)
- Backend HTTP mode parity with demo mode
  - Implement flags and alive/win tracking in Python `Board`
  - Add `/api/flag` logic and persist state between requests
  - Optional: difficulty presets (Beginner/Intermediate/Expert)
- Game features
  - Persisted timer in backend; include elapsed time in API
  - Leaderboard (fastest time per difficulty) with a simple DB
  - Sound effects and subtle animations for reveals/flags
  - Keyboard accessibility and screen-reader improvements
  - Mobile layout polish; larger tap targets
- Quality & DX
  - Unit tests for engine (JS demo and Python back end)
  - E2E tests (Playwright) for core flows
  - CI workflow: lint, test, build
  - Deploy frontend (Netlify/Vercel) and backend (Railway/Fly.io)
- Nice-to-haves
  - Theming presets; color-blind friendly palette
  - PWA installability and offline demo mode

### Project structure

Root
- `board.py` — Python board logic (mines placement, reveal, win check)
- `requirements.txt` — Python dependencies (FastAPI backend optional)
- `README.md` — this file
- `.gitignore` — ignores Node, Python, and editor artifacts

Frontend (`frontend/`)
- `package.json` — Node dependencies and scripts (`npm run dev`)
- `vite.config.js` — Vite dev server config and `/api` proxy
- `postcss.config.js` — PostCSS + Tailwind setup
- `index.html` — Vite entry; mounts the Svelte app
- `src/`
  - `main.js` — Svelte 5 mount point
  - `app.css` — Tailwind directives + global tweaks
  - `App.svelte` — top-level UI: controls, status, timer, overlay
  - `lib/Board.svelte` — visual grid and cell interactions
  - `lib/api.js` — demo-mode engine and HTTP stubs; swap via `VITE_API_MODE`
  - `server.py` — example FastAPI server (optional HTTP mode)

### Setup (run the frontend)

Prereqs:
- Node.js (18+ recommended) and npm

Steps:
1) Install dependencies (from the `frontend/` directory):

```
cd frontend
npm install
```

2) Start the dev server:

```
npm run dev
```

Vite will print a local URL (for example `http://localhost:5173` or `5174`). Open it in your browser.

Notes:
- The app runs fully in demo mode (no backend required).
- If you later want to use the Python backend, start it separately and update the frontend to use HTTP mode (set `VITE_API_MODE=http`).
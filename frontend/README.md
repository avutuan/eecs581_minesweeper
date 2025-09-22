# Frontend

This directory contains the frontend of the application as a [Svelte](https://svelte.dev/) web application.

## Directory Structure

- `package.json` - Node dependencies and scripts (`npm run dev`)
- `vite.config.js` - Vite dev server config and `/api` proxy
- `postcss.config.js` - PostCSS + Tailwind setup
- `index.html` - Vite entry; mounts the Svelte app
- `src/`
  - `main.js` - Svelte 5 mount point
  - `app.css` - Tailwind directives + global tweaks
  - `App.svelte` - top-level UI: controls, status, timer, overlay
  - `lib/Board.svelte` - visual grid and cell interactions
  - `lib/api.js` - demo-mode engine and HTTP stubs; swap via `VITE_API_MODE`
  - `server.py` - example FastAPI server (optional HTTP mode)

## Setup

### Environment Dependencies

- [Node.js v18+](https://nodejs.org/)
- [npm](https://www.npmjs.com/)

### Steps

#### 1

Ensure that you are within the `frontend` directory. If you opened the repo in an IDE from the root, run the following command in the terminal:

```bash
cd frontend
```

#### 2

Install the frontend dependencies:

```bash
npm install
```

#### 3

Ensure that you have created a `.env` file in the `frontend` directory with the following within:

```env
VITE_API_MODE=http
```

#### 4

Start the dev server:

```bash
npm run dev
```

Vite will print a local URL (for example `http://localhost:5173` or `5174`).

#### 5

Open the printed local URL in your browser.
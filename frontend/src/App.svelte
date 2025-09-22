<!--
  Name: App.svelte
  Description: Main web application component for the Minesweeper game.
  Inputs: None
  Outputs: None
  External Sources: N/A
  Author(s): Nicholas Holmes
  Creation Date: 18 September 2025
-->

<script>
  import Board from './lib/Board.svelte';
  import { api } from './lib/api.js';

  let state = null;
  let status = 'idle';
  let error = '';
  let rows = 10, cols = 10, mines = 10;   // easy defaults; UI allows changing
  let overlayDismissed = false;

  // timer (seconds)
  let timerSeconds = 0;
  let timerId = null;

  function formatTime(s){
    const m = Math.floor(s/60).toString().padStart(2,'0');
    const ss = (s%60).toString().padStart(2,'0');
    return `${m}:${ss}`;
  }
  function startTimer(){
    if (timerId) return;
    timerId = setInterval(()=>{ timerSeconds += 1; }, 1000);
  }
  function stopTimer(){
    if (timerId){ clearInterval(timerId); timerId = null; }
  }

  async function load() {
    status = 'loading'; error = '';
    try {
      const res = await api.state();
      state = res.state;
      status = 'ready';
    } catch (e) {
      error = e?.message ?? 'Failed to load';
      status = 'error';
    }
  }

  async function newGame() {
    status = 'loading'; error = '';
    try {
      const res = await api.newGame({ rows, cols, mines });
      state = res.state;
      status = 'ready';
      overlayDismissed = false;
      // reset timer and start
      stopTimer();
      timerSeconds = 0;
      startTimer();
    } catch (e) { error = e?.message ?? 'Failed'; status = 'error'; }
  }

  async function onCellClick(e) {
    const { row, col } = e.detail;
    const res = await api.click({ row, col });
    const refresh = await api.state(); // NEW: get updated state AFTER click
    state = refresh.state;
  }
  async function onCellFlag(e) {
    const { row, col } = e.detail;
    const res = await api.toggleFlag({ row, col });
    state = res.state;
  }

  function dismissOverlay(){ overlayDismissed = true; }

  // stop timer when game ends
  $: if (state && (!state.alive || state.win)) { stopTimer(); }

  function toggleTheme(){
    const el = document.documentElement;
    const isDark = el.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  $: flagsCount = state?.flags?.flat().filter(Boolean).length ?? 0;
  $: minesLeft = (state?.mines ?? mines) - flagsCount;

  newGame(); // start immediately
</script>

<div class="min-h-screen">
  <header class="border-b bg-white dark:bg-slate-950">
    <div class="container py-4 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Minesweeper</h1>
      <div class="flex items-center gap-2">
        <button class="px-3 py-2 rounded-xl border hover:bg-slate-100 dark:hover:bg-slate-800"
                on:click={toggleTheme}>Toggle theme</button>
      </div>
    </div>
  </header>

  <main class="container py-6 grid gap-6 md:grid-cols-12">
    <aside class="md:col-span-4 space-y-4">
      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4 space-y-3">
        <h2 class="font-medium">New Game</h2>
        <div class="grid grid-cols-3 gap-2">
          <label class="text-sm">Rows
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min="5" max="30" bind:value={rows}/>
          </label>
          <label class="text-sm">Cols
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min="5" max="30" bind:value={cols}/>
          </label>
          <label class="text-sm">Mines
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min="1" max="300" bind:value={mines}/>
          </label>
        </div>
        <div class="text-xs text-slate-500 dark:text-slate-400">
          Max values — Rows: 30, Cols: 30, Mines: 300
        </div>
        <div class="flex gap-2">
          <button class="px-3 py-2 rounded-xl border bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700"
                  on:click={newGame}>Start</button>
          <button class="px-3 py-2 rounded-xl border"
                  on:click={load}>Refresh</button>
        </div>
      </div>

      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4">
        <h2 class="font-medium mb-2">Status</h2>
        {#if status === 'loading'}
          <div>Loading…</div>
        {:else if status === 'error'}
          <div class="text-red-600">Error: {error}</div>
        {:else if state}
          <div class="text-sm space-y-1">
            <div>Mines left: <span class="font-semibold">{minesLeft}</span></div>
            <div>Flags: <span class="font-semibold">{flagsCount}</span></div>
            <div>Alive: <span class="font-semibold">{state.alive ? 'Yes' : 'No'}</span></div>
            <div>Win: <span class="font-semibold">{state.win ? 'Yes' : 'No'}</span></div>
            <div>Grid: {state.rows}×{state.cols}</div>
          </div>
        {/if}
      </div>
    </aside>

    <section class="md:col-span-8">
      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4 relative overflow-hidden">
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-medium">Board</h2>
          {#if state && (!state.alive || state.win)}
            <div class="text-sm">
              {#if state.win}<span class="font-semibold">You win!</span>{/if}
              {#if !state.alive}<span class="font-semibold text-red-600">Game over</span>{/if}
            </div>
          {/if}
          <div class="ml-auto text-sm font-mono">Time: <span class="font-semibold">{formatTime(timerSeconds)}</span></div>
        </div>
        {#if state}
          <Board {state} on:cellClick={onCellClick} on:cellFlag={onCellFlag}/>
        {/if}

        {#if state && (state.win || !state.alive) && !overlayDismissed}
          <div class="absolute inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center">
            <div class="rounded-2xl border bg-white dark:bg-slate-900 p-6 shadow-xl text-center max-w-sm w-full mx-4">
              <h3 class={`text-3xl md:text-4xl font-bold mb-3 ${state.win ? 'text-green-600' : 'text-red-600'}`}>
                {state.win ? 'You Won!' : 'Game Over'}
              </h3>
              <p class="text-sm text-slate-600 dark:text-slate-300 mb-4">
                {state.win ? 'All safe cells revealed.' : 'You clicked a bomb.'}
              </p>
              <div class="flex items-center justify-center gap-2">
                <button class="px-3 py-2 rounded-xl border bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700"
                        on:click={newGame}>Start new game</button>
                <button class="px-3 py-2 rounded-xl border"
                        on:click={dismissOverlay}>View board</button>
              </div>
            </div>
          </div>
        {/if}
      </div>
    </section>
  </main>

  <footer class="border-t">
    <div class="container py-6 text-xs text-slate-500">
      Nick is super cool, thanks for playing! :3
    </div>
  </footer>
</div>

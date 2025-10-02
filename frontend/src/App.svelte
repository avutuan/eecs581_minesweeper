<!--
  Name: App.svelte
  Description: Main web application component for the Minesweeper game.
  Inputs: None
  Outputs: None
  External Sources: N/A
  Author(s): Nicholas Holmes, Kobe Jordan, Changwen Gong, Raj Kaura
  Creation Date: 18 September 2025
-->

<script>
  // Import components and utilities
  import Board from './lib/Board.svelte';
  import { api } from './lib/api.js';
  import { soundManager } from './lib/sounds.js';

  // Initialize variables
  let state = null;
  let status = 'idle';
  let error = '';
  let rows = 10, cols = 10, mines = 10;
  
  // Debug: Log when values change
  $: console.log('[DEBUG] Grid size changed:', { rows, cols, mines });
  let overlayDismissed = false;
  let soundEnabled = true;
  
  // Track previous game state to detect changes
  let previousWin = false;
  let previousAlive = true;
  
  // Validation constants
  const MIN_ROWS = 10, MAX_ROWS = 20;
  const MIN_COLS = 10, MAX_COLS = 20;
  const MIN_MINES = 10, MAX_MINES = 20;

  // timer
  let timerSeconds = 0;
  let timerId = null;

  // AI solver
  let solving = false;
  let solvingDifficulty = null;

  // Co-op mode
  let gameMode = 'solo'; // 'solo' or 'coop'
  let aiDifficulty = 'medium';
  let currentPlayer = 'human';
  let humanAlive = true;
  let aiAlive = true;
  let winner = null;

  function formatTime(s){
    /*
    Description: Format seconds into MM:SS format.
    Inputs: seconds (integer)
    Outputs: formatted time string
    External Sources: N/A
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    */
    // m = minutes, ss = seconds
    const m = Math.floor(s/60).toString().padStart(2,'0');
    const ss = (s%60).toString().padStart(2,'0');
    return `${m}:${ss}`;
  }
  function startTimer(){
    /*
    Description: Start the game timer.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    */
    // prevent multiple timers
    if (timerId) return;
    // increment every second
    timerId = setInterval(()=>{ timerSeconds += 1; }, 1000);
  }
  function stopTimer(){
    /*
    Description: Stop the game timer.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    */
    // clear interval if exists
    if (timerId){ clearInterval(timerId); timerId = null; }
  }

  async function load() {
    /*
    Description: Load the current game state from the server.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    */
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
    /*
    Description: Start a new game with the specified settings.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes, Changwen Gong, John Tran
    Creation Date: 18 September 2025
    */
    // Validate inputs before sending to server
    if (rows < MIN_ROWS || rows > MAX_ROWS) {
      error = `Rows must be between ${MIN_ROWS} and ${MAX_ROWS}`;
      status = 'error';
      return;
    }
    if (cols < MIN_COLS || cols > MAX_COLS) {
      error = `Columns must be between ${MIN_COLS} and ${MAX_COLS}`;
      status = 'error';
      return;
    }
    if (mines < MIN_MINES || mines > MAX_MINES) {
      error = `Mines must be between ${MIN_MINES} and ${MAX_MINES}`;
      status = 'error';
      return;
    }
    
    const totalCells = rows * cols;
    const maxAllowedMines = Math.min(MAX_MINES, totalCells - 1);
    if (mines > maxAllowedMines) {
      error = `Too many mines for board size. Maximum allowed: ${maxAllowedMines}`;
      status = 'error';
      return;
    }
    
    status = 'loading'; error = '';
    console.log('[DEBUG] Creating new game with dimensions:', { rows, cols, mines, gameMode, aiDifficulty });
    try {
      const res = await api.newGame({ rows, cols, mines });
      if (!res.ok) {
        error = res.error || 'Failed to create new game';
        status = 'error';
        return;
      }

      state = res.state;
      status = 'ready';
      overlayDismissed = false;
      // Reset previous game state trackers
      previousWin = false;
      previousAlive = true;

      // reset timer and start
      stopTimer();
      timerSeconds = 0;
      startTimer();
      
      // Initialize co-op mode variables
      if (gameMode === 'coop') {
        currentPlayer = state.current_player || 'human';
        humanAlive = state.human_alive !== false;
        aiAlive = state.ai_alive !== false;
        winner = state.winner;
      }
    } catch (e) { error = e?.message ?? 'Failed'; status = 'error'; }
  }

  async function onCellClick(e) {
    /*
    Description: Handle cell click events from the Board component.
    Inputs: event with row and column details
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes, Kobe Jordan, Raj Kaura
    Creation Date: 18 September 2025
    */
    const { row, col } = e.detail;
    try {
      const res = await api.click({ row, col });
      if (res.state) {
        state = res.state;
        // Check if a bomb was just revealed
        if (state.revealed[row][col] && state.board[row][col] === -1) {
          soundManager.playBomb();
        }
      } else {
        const refresh = await api.state();
        state = refresh.state;
      }
    } catch (error) {
      console.error('Error during cell click:', error);
      // Refresh state on error to ensure consistency
      const refresh = await api.state();
      state = refresh.state;
    }
  }
  
  async function onCellFlag(e) {
    /*
    Description: Handle cell flag events from the Board component.
    Inputs: event with row and column details
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes, Kobe Jordan, Raj Kaura
    Creation Date: 18 September 2025
    */
    const { row, col } = e.detail;
    try {
      const res = await api.toggleFlag({ row, col });
      // Use the state from the response, with fallback refresh
      if (res.state) {
        state = res.state;
      } else {
        const refresh = await api.state();
        state = refresh.state;
      }
    } catch (error) {
      console.error('Error during flag toggle:', error);
      // Refresh state on error to ensure consistency
      const refresh = await api.state();
      state = refresh.state;
    }
  }

  function dismissOverlay(){ 
    /*
    Description: Dismiss the win/loss overlay to view the board.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    */
    overlayDismissed = true; 
  }

  function toggleSound(){
    /*
    Description: Toggle sound effects on or off.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): John Tran, Changwen Gong
    Creation Date: 18 September 2025
    */
    soundEnabled = soundManager.toggle();
  }

  // stop timer when game ends
  $: if (state && (!state.alive || state.win)) { stopTimer(); }

  // Play sounds when game state changes
  $: if (state) {
    // Check for win
    if (state.win && !previousWin) {
      soundManager.playWin();
    }
    // Check for lose
    if (!state.alive && previousAlive && !state.win) {
      soundManager.playLose();
    }
    // Update previous state
    previousWin = state.win;
    previousAlive = state.alive;
  }

  function toggleTheme(){
    /*
    Description: Toggle between light and dark themes.
    Inputs: None
    Outputs: None
    External Sources: N/A
    Author(s): Nicholas Holmes
    Creation Date: 18 September 2025
    */
    const el = document.documentElement;
    const isDark = el.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  // Initialize variables
  $: flagsCount = state?.flags?.flat().filter(Boolean).length ?? 0;
  $: minesLeft = (state?.mines ?? mines) - flagsCount;
  $: currentRows = state?.rows ?? rows;
  $: currentCols = state?.cols ?? cols;
  $: currentMines = state?.mines ?? mines;

  newGame(); // start immediately
</script>

<!-- Main application layout -->
<div class="min-h-screen">
  <!-- Header with title and controls -->
  <header class="border-b bg-white dark:bg-slate-950">
    <div class="container py-4 flex items-center justify-between">
      <h1 class="text-xl font-semibold tracking-tight">Minesweeper</h1>
      <div class="flex items-center gap-2">
        <button class="px-3 py-2 rounded-xl border hover:bg-slate-100 dark:hover:bg-slate-800"
                on:click={toggleSound} 
                title={soundEnabled ? 'Sound On' : 'Sound Off'}>
          {soundEnabled ? '🔊' : '🔇'}
        </button>
        <button class="px-3 py-2 rounded-xl border hover:bg-slate-100 dark:hover:bg-slate-800"
                on:click={toggleTheme}>Toggle theme</button>
      </div>
    </div>
  </header>

  <!-- Main content area with sidebar and board -->
  <main class="container py-6 grid gap-6 md:grid-cols-12">
    <aside class="md:col-span-4 space-y-4">
      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4 space-y-3">

        <!-- New Game Settings -->
        <h2 class="font-medium">New Game</h2>
        <div class="grid grid-cols-3 gap-2">
          <label class="text-sm">Rows
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min={MIN_ROWS} max={MAX_ROWS} bind:value={rows}/>
          </label>
          <label class="text-sm">Cols
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min={MIN_COLS} max={MAX_COLS}  bind:value={cols}/>
          </label>
          <label class="text-sm">Mines
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min={MIN_MINES} max={MAX_MINES} bind:value={mines}/>
          </label>
        </div>

        <!-- Validation Info -->
        <div class="text-xs text-slate-500 dark:text-slate-400">
          Rows: {MIN_ROWS}-{MAX_ROWS}, Cols: {MIN_COLS}-{MAX_COLS}, Mines: {MIN_MINES}-{MAX_MINES}
        </div>
        <div class="text-xs text-blue-600 dark:text-blue-400">
          Current: {rows}×{cols}, {mines} mines
        </div>

        <!-- Game Mode Selection -->
        <div class="space-y-2">
          <h3 class="font-medium text-sm">Game Mode</h3>
          <div class="flex gap-2">
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" bind:group={gameMode} value="solo" />
              <span class="text-sm">Solo Play</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <input type="radio" bind:group={gameMode} value="coop" />
              <span class="text-sm">Co-op vs AI</span>
            </label>
          </div>
          {#if gameMode === 'coop'}
            <div class="space-y-1">
              <label class="text-sm">AI Difficulty</label>
              <select class="input input-bordered w-full rounded-xl text-sm" bind:value={aiDifficulty}>
                <option value="easy">Easy</option>
                <option value="medium">Medium</option>
                <option value="hard">Hard</option>
              </select>
            </div>
          {/if}
        </div>

        <!-- Action Buttons -->
        <div class="flex gap-2">
          <button class="px-3 py-2 rounded-xl border bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700"
                  on:click={newGame}>Start New Game</button>
          <button class="px-3 py-2 rounded-xl border"
                  on:click={load}>Refresh</button>
        </div>

        <!-- AI Controls -->
        <div class="flex flex-wrap gap-2 mt-2">
          <!-- Continuous AI Solve -->
          <button class="px-3 py-2 rounded-xl border bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800"
                  on:click={() => aiSolve('easy')}>AI Solve (Easy)</button>
          <button class="px-3 py-2 rounded-xl border bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800"
                  on:click={() => aiSolve('medium')}>AI Solve (Medium)</button>
          <button class="px-3 py-2 rounded-xl border bg-green-100 hover:bg-green-200 dark:bg-green-900 dark:hover:bg-green-800"
                  on:click={() => aiSolve('hard')}>AI Solve (Hard)</button>

          <!-- Stop AI Solve -->
          {#if solving}
            <button class="px-3 py-2 rounded-xl border bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800"
                    on:click={stopSolve}>Stop</button>
            <span class="text-xs text-slate-500">Solving: {solvingDifficulty}</span>
          {/if}
        </div>
      </div>

      <!-- Status Display -->
      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4">
        <h2 class="font-medium mb-2">Status</h2>
        <!-- Status messages -->
        <!-- Loading, Error, or Game Info -->
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
            <div>Grid: {currentRows}×{currentCols}</div>
            <div>Total mines: <span class="font-semibold">{currentMines}</span></div>
          </div>
        {/if}
      </div>
    </aside>

    <!-- Game Board Section -->
    <section class="md:col-span-8">
      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4 relative overflow-hidden">
        <!-- Board Header -->
        <div class="flex items-center justify-between mb-3">
          <h2 class="font-medium">Board</h2>
          <!-- Win/Loss Message -->
          {#if state && (!state.alive || state.win)}
            <div class="text-sm">
              {#if state.win}<span class="font-semibold">You win!</span>{/if}
              {#if !state.alive}<span class="font-semibold text-red-600">Game over</span>{/if}
            </div>
          {/if}
          <div class="ml-auto text-sm font-mono">Time: <span class="font-semibold">{formatTime(timerSeconds)}</span></div>
        </div>
        <!-- Board Component -->
        {#if state}
          <Board {state} {gameMode} {currentPlayer} on:cellClick={onCellClick} on:cellFlag={onCellFlag}/>
        {/if}

        <!-- Win/Loss Overlay -->
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

  <!-- Footer -->
  <footer class="border-t">
    <div class="container py-6 text-xs text-slate-500">
      Nick is super cool, thanks for playing! :3
    </div>
  </footer>
</div>
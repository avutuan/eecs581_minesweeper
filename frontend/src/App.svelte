<!--
  Name: App.svelte
  Description: Main web application component for the Minesweeper game.
  Inputs: None
  Outputs: None
  External Sources: N/A
  Author(s): Nicholas Holmes + AI Solver Integration
  Creation Date: 18 September 2025
-->

<script>
  import Board from './lib/Board.svelte';
  import { api } from './lib/api.js';
  import { soundManager } from './lib/sounds.js';

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
      const res = await api.newGame({ 
        rows, cols, mines, 
        game_mode: gameMode,
        ai_difficulty: aiDifficulty 
      });
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
      solving = false;
      solvingDifficulty = null;
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
    const { row, col } = e.detail;
    try {
      // Check if it's human's turn in co-op mode
      if (gameMode === 'coop' && currentPlayer !== 'human') {
        return; // Not human's turn
      }

      const res = await api.click({ row, col });
      // Use the state from the response first, then refresh for consistency
      if (res.state) {
        state = res.state;
        // Check if a bomb was just revealed
        if (state.revealed[row][col] && state.board[row][col] === -1) {
          soundManager.playBomb();
        }
      } else {
        const refresh = await api.state();
        state = refresh.state;

        // Update co-op mode variables after human move
        if (gameMode === 'coop') {
          // Handle enum values from backend
          const playerValue = typeof state.current_player === 'string' ? state.current_player : 'human';
          currentPlayer = playerValue;
          humanAlive = state.human_alive !== false;
          aiAlive = state.ai_alive !== false;
          winner = state.winner;
          
          console.log('[DEBUG] After human move:', { 
            currentPlayer, 
            humanAlive, 
            aiAlive, 
            game_over: state.game_over,
            winner: state.winner,
            raw_current_player: state.current_player,
            playerValue
          });
          
          // If it's now AI's turn, trigger AI move after delay
          if (currentPlayer === 'ai' && aiAlive && !state.game_over) {
            console.log('[DEBUG] Triggering AI turn in 1 second...');
            setTimeout(() => {
              console.log('[DEBUG] AI turn timeout triggered');
              aiTurn();
            }, 1000);
          } else {
            console.log('[DEBUG] Not triggering AI turn:', {
              currentPlayer,
              aiAlive,
              gameOver: state.game_over,
              reason: currentPlayer !== 'ai' ? 'not AI turn' : !aiAlive ? 'AI not alive' : 'game over'
            });
          }
        } else if (gameMode === 'solo') {
          // SOLO mode: No AI involvement - just traditional single-player Minesweeper
          console.log('[DEBUG] SOLO mode - no AI involvement, traditional single-player game');
        } else {
          console.log('[DEBUG] Unknown game mode:', gameMode);
        }
      }
    } catch (error) {
      console.error('Error during cell click:', error);
      // Refresh state on error to ensure consistency
      const refresh = await api.state();
      state = refresh.state;
    }
    
  }
  
  async function onCellFlag(e) {
    const { row, col } = e.detail;
    
    // Check if it's human's turn in co-op mode
    if (gameMode === 'coop' && currentPlayer !== 'human') {
      return; // Not human's turn
    }
    
    try {
      const res = await api.toggleFlag({ row, col });
      // Use the state from the response, with fallback refresh
      if (res.state) {
        state = res.state;
        // In co-op mode, flagging should also trigger AI turn after a delay
        if (gameMode === 'coop') {
          // Handle enum values from backend
          const playerValue = typeof state.current_player === 'string' ? state.current_player : 'human';
          currentPlayer = playerValue;
          humanAlive = state.human_alive !== false;
          aiAlive = state.ai_alive !== false;
          winner = state.winner;
          
          console.log('[DEBUG] After human flag:', { 
            currentPlayer, 
            humanAlive, 
            aiAlive, 
            game_over: state.game_over,
            winner: state.winner,
            raw_current_player: state.current_player,
            playerValue
          });
          
          // Trigger AI turn after flagging if it's now AI's turn
          if (currentPlayer === 'ai' && aiAlive && !state.game_over) {
            console.log('[DEBUG] Triggering AI turn after flag in 1.5 seconds...');
            setTimeout(() => {
              console.log('[DEBUG] AI turn after flag timeout triggered');
              aiTurn();
            }, 1500); // Slightly longer delay for flagging
          } else {
            console.log('[DEBUG] Not triggering AI turn after flag:', {
              currentPlayer,
              aiAlive,
              gameOver: state.game_over,
              reason: currentPlayer !== 'ai' ? 'not AI turn' : !aiAlive ? 'AI not alive' : 'game over'
            });
          }
        } else if (gameMode === 'solo') {
          // SOLO mode: No AI involvement - just traditional single-player Minesweeper
          console.log('[DEBUG] SOLO mode - no AI involvement, traditional single-player game');
        } else {
          console.log('[DEBUG] Unknown game mode in flag:', gameMode);
        }
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

  // AI turn function for co-op mode
  async function aiTurn() {
    console.log('[DEBUG] aiTurn called:', { gameMode, currentPlayer, aiAlive });
    
    // For debugging, allow manual AI turn even if conditions aren't met
    if (gameMode !== 'coop') {
      console.log('[DEBUG] aiTurn aborted: not in co-op mode');
      return;
    }
    
    if (currentPlayer !== 'ai' && currentPlayer !== 'human') {
      console.log('[DEBUG] aiTurn aborted: invalid current player:', currentPlayer);
      return;
    }
    
    if (!aiAlive) {
      console.log('[DEBUG] aiTurn aborted: AI not alive');
      return;
    }
    
    try {
      console.log('[DEBUG] Making AI turn API call...');
      const res = await api.aiTurn();
      console.log('[DEBUG] AI turn response:', res);
      
      if (res.error) {
        console.error('[DEBUG] AI turn API error:', res.error);
        error = res.error;
        return;
      }
      
      state = res.state;
      
      // Update co-op mode variables after AI move
      const playerValue = typeof state.current_player === 'string' ? state.current_player : 'human';
      currentPlayer = playerValue;
      humanAlive = state.human_alive !== false;
      aiAlive = state.ai_alive !== false;
      winner = state.winner;
      
      console.log('[DEBUG] After AI move:', { 
        currentPlayer, 
        humanAlive, 
        aiAlive, 
        winner 
      });
    } catch (e) {
      console.error('[DEBUG] AI turn error:', e);
      error = e?.message ?? 'AI turn failed';
    }
  }

  async function aiAction(difficulty) {
    try {
      const res = await api.aiMove(difficulty);
      if (res.error) { error = res.error; return null; }
      
      // Update state from the AI move response
      if (res.state) {
        state = res.state;
      } else {
        // If no state in response, fetch current state
        const refresh = await api.state();
        state = refresh.state;
      }
      
      return res;
    } catch (e) {
      error = e?.message ?? 'AI failed';
      return null;
    }
  }

  // Continuous solver
  async function aiSolve(difficulty){
    if (!state || !state.alive || state.win) return;
    solving = true;
    solvingDifficulty = difficulty;

    async function step(){
      if (!solving) return;
      if (!state.alive || state.win) { solving = false; solvingDifficulty = null; return; }

      const res = await aiAction(difficulty);

      // FIX: If AI has no moves ("none"), try random easy reveal to keep progressing
      if (!res || res.action === "none") {
        const fallback = await aiAction("easy");
        if (!fallback || fallback.action === 'none') {
          solving = false; solvingDifficulty = null; return;
        }
      }

      setTimeout(step, 300); // delay between moves
    }
    step();
  }

  function stopSolve(){ solving = false; solvingDifficulty = null; }

  function dismissOverlay(){ overlayDismissed = true; }

  function toggleSound(){
    soundEnabled = soundManager.toggle();
  }

  // stop timer when game ends
  $: if (state && (!state.alive || state.win)) { stopTimer(); solving = false; solvingDifficulty = null; }

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
    const el = document.documentElement;
    const isDark = el.classList.toggle('dark');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
  }

  $: flagsCount = state?.flags?.flat().filter(Boolean).length ?? 0;
  $: minesLeft = (state?.mines ?? mines) - flagsCount;
  $: currentRows = state?.rows ?? rows;
  $: currentCols = state?.cols ?? cols;
  $: currentMines = state?.mines ?? mines;

  newGame(); // start immediately
</script>

<div class="min-h-screen">
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

  <main class="container py-6 grid gap-6 md:grid-cols-12">
    <aside class="md:col-span-4 space-y-4">
      <div class="rounded-2xl border bg-white dark:bg-slate-950 p-4 space-y-3">
        <h2 class="font-medium">New Game</h2>
        <div class="grid grid-cols-3 gap-2">
          <label class="text-sm">Rows
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min={MIN_ROWS} max={MAX_ROWS} step="1" bind:value={rows}/>
          </label>
          <label class="text-sm">Cols
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min={MIN_COLS} max={MAX_COLS} step="1" bind:value={cols}/>
          </label>
          <label class="text-sm">Mines
            <input class="mt-1 input input-bordered w-full rounded-xl"
                   type="number" min={MIN_MINES} max={MAX_MINES} step="1" bind:value={mines}/>
          </label>
        </div>
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

          {#if solving}
            <button class="px-3 py-2 rounded-xl border bg-red-100 hover:bg-red-200 dark:bg-red-900 dark:hover:bg-red-800"
                    on:click={stopSolve}>Stop</button>
            <span class="text-xs text-slate-500">Solving: {solvingDifficulty}</span>
          {/if}
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
            <div>Grid: <span class="font-semibold">{currentRows}×{currentCols}</span></div>
            <div>Total mines: <span class="font-semibold">{currentMines}</span></div>
            
            <!-- Co-op mode status -->
            {#if gameMode === 'coop'}
              <div class="border-t pt-2 mt-2 space-y-1">
                <div class="font-medium text-xs text-slate-600 dark:text-slate-400">Co-op Mode</div>
                <div>Current Turn: <span class="font-semibold">{currentPlayer === 'human' ? 'You' : 'AI'}</span></div>
                <div>Human: <span class="font-semibold {humanAlive ? 'text-green-600' : 'text-red-600'}">{humanAlive ? 'Alive' : 'Lost'}</span></div>
                <div>AI: <span class="font-semibold {aiAlive ? 'text-green-600' : 'text-red-600'}">{aiAlive ? 'Alive' : 'Lost'}</span></div>
                {#if winner}
                  <div class="font-semibold text-blue-600">
                    Winner: {winner === 'human' ? 'You' : winner === 'ai' ? 'AI' : 'Draw'}
                  </div>
                {/if}
              </div>
            {/if}
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
          <Board {state} {gameMode} {currentPlayer} on:cellClick={onCellClick} on:cellFlag={onCellFlag}/>
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
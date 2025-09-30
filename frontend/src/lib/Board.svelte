<!--
  Name: Board.svelte
  Description: The board component for the Minesweeper game.
  Inputs: None
  Outputs: None
  External Sources: N/A
  Author(s): Nicholas Holmes
  Creation Date: 18 September 2025
-->

<script>
  import { createEventDispatcher } from 'svelte';
  export let state; // { rows, cols, board, flags, alive, win, ... }
  const dispatch = createEventDispatcher();
  
  // Track animations
  let clickedCells = new Set();
  let flaggedCells = new Set();
  let revealedCells = new Set();
  
  // Track previously revealed cells to detect new reveals
  let previouslyRevealed = new Set();
  
  $: {
    if (state) {
      const currentRevealed = new Set();
      for (let r = 0; r < state.rows; r++) {
        for (let c = 0; c < state.cols; c++) {
          if (state.revealed[r][c]) {
            const cellKey = `${r}-${c}`;
            currentRevealed.add(cellKey);
            // If this cell wasn't revealed before, add reveal animation
            if (!previouslyRevealed.has(cellKey)) {
              revealedCells.add(cellKey);
              setTimeout(() => {
                revealedCells.delete(cellKey);
                revealedCells = revealedCells;
              }, 400);
            }
          }
        }
      }
      previouslyRevealed = currentRevealed;
      revealedCells = revealedCells; // trigger reactivity
    }
  }

  function cellClick(r,c){ 
    if (!state?.alive || state?.win) return; 
    
    // Add click animation
    const cellKey = `${r}-${c}`;
    clickedCells.add(cellKey);
    clickedCells = clickedCells; // trigger reactivity
    
    // Remove animation after a short delay
    setTimeout(() => {
      clickedCells.delete(cellKey);
      clickedCells = clickedCells;
    }, 200);
    
    dispatch('cellClick', { row:r, col:c }); 
  }
  
  function cellFlag(e, r, c){
    e.preventDefault();
    if (!state?.alive || state?.win) return;
    
    // Add flag animation
    const cellKey = `${r}-${c}`;
    flaggedCells.add(cellKey);
    flaggedCells = flaggedCells; // trigger reactivity
    
    // Remove animation after a short delay
    setTimeout(() => {
      flaggedCells.delete(cellKey);
      flaggedCells = flaggedCells;
    }, 300);
    
    dispatch('cellFlag', { row:r, col:c });
  }

  function cellContent(val, flagged) {
    if (flagged) return '🚩';
    if (val === null) return '';
    if (val === -1) return '💣';
    return val === 0 ? '' : String(val);
  }

  function cellColor(val) {
    switch (val) {
      case 1: return "text-blue-600";
      case 2: return "text-green-600";
      case 3: return "text-red-600";
      case 4: return "text-purple-600";
      case 5: return "text-yellow-600";
      case 6: return "text-teal-600";
      case 7: return "text-black";
      case 8: return "text-gray-600";
      default: return ""; // blank or mines/flags
    }}
</script>

<div class="grid" style={`grid-template-columns: repeat(${state.cols}, minmax(0, 1fr)); gap: .5rem;`}>
  {#each Array(state.rows) as _, r}
    {#each Array(state.cols) as __, c}
      {#key (r+'-'+c)}
        {@const cellKey = `${r}-${c}`}
        {@const isClicked = clickedCells.has(cellKey)}
        {@const isFlagged = flaggedCells.has(cellKey)}
        {@const isNewlyRevealed = revealedCells.has(cellKey)}
        <button
          class={`aspect-square rounded-xl border transition-all duration-200 
          ${state?.revealed[r][c]
          ? "bg-slate-150 dark:bg-slate-900"  // revealed cells
          : "bg-slate-100 dark:bg-slate-800"} // not revealed cells
          hover:bg-slate-200 dark:hover:bg-slate-700 
          disabled:opacity-70 
          flex items-center justify-center
          ${isClicked ? 'scale-95 bg-blue-200 dark:bg-blue-800' : ''}
          ${isFlagged ? 'scale-110 bg-yellow-200 dark:bg-yellow-800' : ''}
          ${isNewlyRevealed ? 'scale-105 bg-green-200 dark:bg-green-800 animate-pulse' : ''}`}
          on:click={() => cellClick(r,c)}
          on:contextmenu={(e) => cellFlag(e, r, c)}
          disabled={!state.alive || state.win}
          aria-label={`cell ${r},${c}`}
        >
          <span class={`font-semibold text-2xl md:text-3xl leading-none transition-all duration-200 
          ${cellColor(state.board[r][c])}
          ${isClicked ? 'scale-90' : ''}
          ${isFlagged ? 'scale-125' : ''}
          ${isNewlyRevealed ? 'scale-110' : ''}`}>
            {cellContent(state.board[r][c], state.flags[r][c])}
          </span> 
        </button>
      {/key}
    {/each}
  {/each}
</div>

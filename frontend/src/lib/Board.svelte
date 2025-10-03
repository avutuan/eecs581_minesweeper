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
  export let gameMode = 'solo'; // 'solo' or 'coop'
  export let currentPlayer = 'human'; // 'human' or 'ai'
  const dispatch = createEventDispatcher();

  function cellClick(r,c){ 
    if (!state?.alive || state?.win) return; 
    // In co-op mode, only allow human clicks on human's turn
    if (gameMode === 'coop' && currentPlayer !== 'human') return;
    dispatch('cellClick', { row:r, col:c }); 
  }
  function cellFlag(e, r, c){
    e.preventDefault();
    if (!state?.alive || state?.win) return;
    // In co-op mode, only allow human flags on human's turn
    if (gameMode === 'coop' && currentPlayer !== 'human') return;
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
        <button
          class={`aspect-square rounded-xl border ${state?.revealed[r][c]
          ? "bg-slate-150 dark:bg-slate-900"  // revealed cells
          : "bg-slate-100 dark:bg-slate-800"} // not revealed cells
          hover:bg-slate-200 dark:hover:bg-slate-700 
          disabled:opacity-70 
          flex items-center justify-center
          ${gameMode === 'coop' && currentPlayer !== 'human' ? 'cursor-not-allowed opacity-50' : ''}`}
          on:click={() => cellClick(r,c)}
          on:contextmenu={(e) => cellFlag(e, r, c)}
          disabled={!state.alive || state.win || (gameMode === 'coop' && currentPlayer !== 'human')}
          aria-label={`cell ${r},${c}`}
        >
          <span class={`font-semibold text-2xl md:text-3xl leading-none ${cellColor(state.board[r][c])}`}>
            {cellContent(state.board[r][c], state.flags[r][c])}
          </span> 
        </button>
        {console.log(state)}
      {/key}
    {/each}
  {/each}
</div>

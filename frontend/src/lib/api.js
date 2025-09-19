const MODE = import.meta.env.VITE_API_MODE ?? 'demo'; // 'demo' or 'http'
const BASE = import.meta.env.VITE_API_BASE ?? '';

/* ---------- Shared Types ----------
state = {
  rows, cols, mines,
  board: number|null[][],   // null = unrevealed, 0..8 or -1 (if revealed and mine)
  revealed: boolean[][],
  flags: boolean[][],
  alive: boolean, // false if exploded
  win: boolean
}
-----------------------------------*/

function deepCopy(x){ return JSON.parse(JSON.stringify(x)); }

/* ============ DEMO MODE ENGINE ============ */
function makeEmpty(rows, cols, val) {
  return Array.from({length: rows}, () => Array.from({length: cols}, () => val));
}
function neighbors(r,c){ 
  return [
    [-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]
  ].map(([dr,dc])=>[r+dr,c+dc]);
}
function countAdj(board, r, c, rows, cols){
  let cnt=0;
  for(const [nr,nc] of neighbors(r,c)){
    if(nr>=0 && nr<rows && nc>=0 && nc<cols && board[nr][nc]===-1) cnt++;
  }
  return cnt;
}

class DemoAPI {
  constructor(){
    this.rows = 10; this.cols = 10; this.mines = 10;
    this.initialized = false;
    this.board = makeEmpty(this.rows,this.cols,0);  // -1 for mine, else count
    this.revealed = makeEmpty(this.rows,this.cols,false);
    this.flags = makeEmpty(this.rows,this.cols,false);
    this.alive = true;
    this.win = false;
  }
  async newGame(params={}){
    if (params?.rows) this.rows = params.rows;
    if (params?.cols) this.cols = params.cols;
    if (params?.mines) this.mines = params.mines;
    this.initialized = false;
    this.board = makeEmpty(this.rows,this.cols,0);
    this.revealed = makeEmpty(this.rows,this.cols,false);
    this.flags = makeEmpty(this.rows,this.cols,false);
    this.alive = true; this.win = false;
    return { ok: true, state: this._visibleState() };
  }
  _placeMines(firstRow, firstCol){
    const safeR = new Set([firstRow-1, firstRow, firstRow+1]);
    const safeC = new Set([firstCol-1, firstCol, firstCol+1]);
    let placed = 0;
    while (placed < this.mines) {
      const r = Math.floor(Math.random()*this.rows);
      const c = Math.floor(Math.random()*this.cols);
      if (!safeR.has(r) && !safeC.has(c) && this.board[r][c]!==-1) { // keep 3x3 clear
        this.board[r][c] = -1;
        placed++;
      }
    }
    // update counts
    for(let r=0;r<this.rows;r++){
      for(let c=0;c<this.cols;c++){
        if (this.board[r][c]===-1) continue;
        this.board[r][c] = countAdj(this.board,r,c,this.rows,this.cols);
      }
    }
  }
  _reveal(r,c){
    if (r<0||r>=this.rows||c<0||c>=this.cols) return;
    if (this.revealed[r][c] || this.flags[r][c]) return;
    this.revealed[r][c]=true;
    if (this.board[r][c]===0){
      for(const [nr,nc] of neighbors(r,c)){
        if (nr>=0&&nr<this.rows&&nc>=0&&nc<this.cols && !this.revealed[nr][nc]){
          this._reveal(nr,nc);
        }
      }
    }
  }
  _checkWin(){
    for(let r=0;r<this.rows;r++){
      for(let c=0;c<this.cols;c++){
        if (this.board[r][c]!==-1 && !this.revealed[r][c]) return false;
      }
    }
    return true;
  }
  _visibleState(revealAll=false){
    const board = makeEmpty(this.rows,this.cols,null);
    for(let r=0;r<this.rows;r++){
      for(let c=0;c<this.cols;c++){
        if (this.revealed[r][c] || (revealAll && !this.flags[r][c])){
          board[r][c] = this.board[r][c];
        } else {
          board[r][c] = null;
        }
      }
    }
    return {
      rows:this.rows, cols:this.cols, mines:this.mines,
      board, revealed: deepCopy(this.revealed), flags: deepCopy(this.flags),
      alive:this.alive, win:this.win
    };
  }
  async state(){ return { ok: true, state: this._visibleState(!this.alive) }; }
  async click({row,col}){
    if (!this.alive) return { ok: true, state: this._visibleState(true), alive:false, win:this.win };
    if (!this.initialized){
      this._placeMines(row,col);
      this.initialized = true;
    }
    if (this.flags[row][col]) return { ok: true, state: this._visibleState(), alive:this.alive, win:this.win };
    if (this.board[row][col]===-1){
      this.revealed[row][col]=true;
      this.alive=false;
      return { ok:true, state:this._visibleState(true), alive:false, win:false };
    }
    this._reveal(row,col);
    this.win = this._checkWin();
    return { ok:true, state:this._visibleState(), alive:this.alive, win:this.win };
  }
  async toggleFlag({row,col}){
    if (this.revealed[row][col] || !this.alive) return { ok:true, state:this._visibleState(), alive:this.alive, win:this.win };
    this.flags[row][col] = !this.flags[row][col];
    return { ok:true, state:this._visibleState(), alive:this.alive, win:this.win };
  }
}
const demo = new DemoAPI();

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

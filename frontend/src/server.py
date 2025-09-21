"""
Name: server.py
Description: The FastAPI server for the Minesweeper backend.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Nicholas Holmes
Creation Date: 18 September 2025
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import sys

# Ensure the project root is on sys.path so 'backend' can be imported
# when running this file directly (e.g., `python frontend/src/server.py`).
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.board import Board, BoardPos, BoardSize

app = FastAPI()

# Add CORS middleware to allow frontend to connect
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

board = None
initialized = False
alive = True

class Click(BaseModel):
    row: int
    col: int

class NewGameParams(BaseModel):
    rows: int = 10
    cols: int = 10
    mines: int = 10

@app.post("/api/new")
def new_game(params: NewGameParams):
    global board, initialized, alive
    board = Board(params.mines)
    board.size = BoardSize(params.rows, params.cols)
    board.board = [[0 for _ in range(params.cols)] for _ in range(params.rows)]
    board.revealed = [[False for _ in range(params.cols)] for _ in range(params.rows)]
    # Reset flags and status to match new size
    if hasattr(board, 'flags'):
        board.flags = [[False for _ in range(params.cols)] for _ in range(params.rows)]
    if hasattr(board, 'numOfFlags'):
        board.numOfFlags = 0
    if hasattr(board, 'isAlive'):
        board.isAlive = True
    initialized = False
    alive = True
    return {"ok": True, "state": board.to_dict()}

@app.get("/api/state")
def state():
    if board is None:
        return {"ok": True, "state": None}
    state_dict = board.to_dict(reveal_all=(not alive))
    state_dict["alive"] = alive
    return {"ok": True, "state": state_dict}

@app.post("/api/click")
def click(c: Click):
    global initialized, alive
    if board is None:
        return {"ok": False, "error": "No game"}
    if not alive:
        return {"ok": True, "state": board.to_dict(reveal_all=True), "alive": alive, "win": False}
    
    # First click: place mines around it and compute counts
    if not initialized:
        board.place_mines(BoardPos(c.row, c.col))
        board.update_mine_counts()
        initialized = True
    
    alive = board.reveal_cell(BoardPos(c.row, c.col))
    win = board.check_win()
    
    return {
        "ok": True,
        "alive": alive,
        "win": win,
        "state": board.to_dict(reveal_all=(not alive)),
    }

@app.post("/api/flag")
def toggle_flag(c: Click):
    global alive
    if board is None:
        return {"ok": False, "error": "No game"}
    if not alive:
        return {"ok": True, "state": board.to_dict(reveal_all=True), "alive": alive, "win": False}
    
    # Toggle flag at the specified position
    board.flag_cell(BoardPos(c.row, c.col))    
    
    # Toggle flag (simplified - just return current state for now)
    # TODO: Implement actual flagging logic in Board class
    return {
        "ok": True,
        "state": board.to_dict(),
        "alive": alive,
        "win": board.check_win()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

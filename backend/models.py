
from pydantic import BaseModel, model_validator, Field, ValidationError
from typing import Optional, Union, List
from enum import Enum

from .constants import (
    DEFAULT_COLS,
    DEFAULT_MINE_COUNT,
    DEFAULT_ROWS,
    MIN_ROWS,
    MAX_ROWS,
    MIN_COLS,
    MAX_COLS,
    MIN_MINES,
    MAX_MINES
)

from dataclasses import dataclass

class GameMode(str, Enum):
    SOLO = "solo"           # Traditional single-player
    COOP = "coop"           # Human vs AI turn-based

class PlayerType(str, Enum):
    HUMAN = "human"
    AI = "ai"

class BoardPos(BaseModel):
    """
    A dataclass to represent a position on the board with row (x) and column (y) coordinates.
    """
    x: int
    y: int

    @model_validator(mode="before")
    @classmethod
    def accept_row_col(cls, data):
        # Allow requests that send {row, col} instead of {x, y}
        if isinstance(data, dict):
            if 'row' in data and 'col' in data:
                data = {**data, 'x': data.get('x', data['row']), 'y': data.get('y', data['col'])}
        return data

@dataclass
class BoardSize:
    """
    A dataclass to represent the size of the board with rows and columns.
    """
    rows: int
    cols: int

class BoardStateModel(BaseModel):
    rows: int
    cols: int
    mines: int
    board: List[List[Optional[int]]]
    revealed: List[List[bool]]
    flags: List[List[bool]]
    flag_count: int
    alive: bool
    win: bool
    # Co-op mode fields
    game_mode: GameMode = GameMode.SOLO
    current_player: PlayerType = PlayerType.HUMAN
    human_alive: bool = True
    ai_alive: bool = True
    winner: PlayerType | None = None
    game_over: bool = False

    def __getitem__(self, key):
        return getattr(self, key)

class BoardFrontendModel(BaseModel):
    ok: bool
    alive: Optional[bool] = None
    win: Optional[bool] = None
    error: Optional[str] = None
    state: Optional[BoardStateModel] = None

    def __getitem__(self, key):
        return getattr(self, key)

class NewGameParams(BaseModel):
    rows: int = Field(default=DEFAULT_ROWS, ge=MIN_ROWS, le=MAX_ROWS)
    cols: int = Field(default=DEFAULT_COLS, ge=MIN_COLS, le=MAX_COLS)
    mines: int = Field(default=DEFAULT_MINE_COUNT, ge=MIN_MINES, le=MAX_MINES)
    interactive: bool = False   # <--- NEW
    game_mode: GameMode = GameMode.SOLO
    ai_difficulty: str = "medium"  # for co-op mode

    @model_validator(mode='after')
    def validate_mines_vs_cells(self):
        total_cells = self.rows * self.cols
        max_allowed_mines = min(MAX_MINES, total_cells - 1)  # Leave at least one safe cell
        if self.mines > max_allowed_mines:
            raise ValueError(f"Too many mines for board size. Maximum allowed: {max_allowed_mines}")
        return self
    
class AIMove(BaseModel):
    action: str  # "reveal" | "flag" | "none"
    pos: BoardPos | None
    
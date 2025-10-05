"""
Description: Pydantic schemas and simple dataclasses for the Minesweeper
backend API. This module defines payloads and small helper containers used
by the server and frontend (positions, sizes, game state, and requests).
Inputs: None (type definitions only)
Outputs: None
Author(s): Riley Meyerkorth
Creation Date: 05 October 2025
External Sources: N/A
"""

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
    """
    Description: Enumerates supported game modes.
    Inputs: None
    Outputs: Enum values used across the server and frontend.
    Author(s): Riley Meyerkorth
    Creation Date: 05 October 2025
    """
    SOLO = "solo"           # Traditional single-player
    COOP = "coop"           # Human vs AI turn-based

class PlayerType(str, Enum):
    """
    Description: Identifies a player in co-op mode (human or AI).
    Inputs: None
    Outputs: Enum values used to track turns and winners.
    Author(s): Riley Meyerkorth
    Creation Date: 05 October 2025
    """
    HUMAN = "human"
    AI = "ai"

class BoardPos(BaseModel):
    """
    Description: Simple Pydantic model representing a board coordinate.
    Inputs: x (row index), y (column index)
    Outputs: Validated position object used by API endpoints.
    Author(s): Riley Meyerkorth
    Creation Date: 05 October 2025
    """
    x: int
    y: int

    @model_validator(mode="before")
    @classmethod
    def accept_row_col(cls, data):
        """
        Description: Accept alternative payload keys 'row'/'col' and map them
        to the internal fields 'x'/'y'.
        Inputs: raw payload (dict or other)
        Outputs: normalized dict acceptable to the BaseModel constructor
        Author(s): Riley Meyerkorth
        Creation Date: 05 October 2025
        """
        # Allow requests that send {row, col} instead of {x, y}
        if isinstance(data, dict):
            if 'row' in data and 'col' in data:
                data = {**data, 'x': data.get('x', data['row']), 'y': data.get('y', data['col'])}
        return data

@dataclass
class BoardSize:
    """
    Description: Holds the number of rows and columns for a board.
    Inputs: rows (int), cols (int)
    Outputs: dataclass used to size Board instances and validate API payloads.
    Author(s): Riley Meyerkorth
    Creation Date: 05 October 2025
    """
    rows: int
    cols: int

class BoardStateModel(BaseModel):
    """
    Description: Complete serializable snapshot of the game board returned
    to the frontend. Includes cell values, revealed/flag matrices, and
    cooperative-mode metadata.
    Inputs: internal Board representation
    Outputs: JSON-serializable state consumed by the UI
    Author(s): Riley Meyerkorth, Changwen Gong, John Tran
    Creation Date: 05 October 2025
    """
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
    """
    Description: Standard API response wrapper used by endpoints. Carries
    an 'ok' flag plus optional state, error, and win/alive values.
    Inputs: results from server handlers
    Outputs: payload sent to the frontend
    Author(s): Riley Meyerkorth, Changwen Gong, John Tran
    Creation Date: 05 October 2025
    """
    ok: bool
    alive: Optional[bool] = None
    win: Optional[bool] = None
    error: Optional[str] = None
    state: Optional[BoardStateModel] = None

    def __getitem__(self, key):
        return getattr(self, key)

class NewGameParams(BaseModel):
    """
    Description: Parameters accepted when creating a new game. Performs
    basic validation via pydantic (bounds on rows/cols/mines).
    Inputs: rows, cols, mines, interactive, game_mode, ai_difficulty
    Outputs: validated parameters or a raised ValidationError
    Author(s): Riley Meyerkorth, Changwen Gong, John Tran
    Creation Date: 05 October 2025
    """
    rows: int = Field(default=DEFAULT_ROWS, ge=MIN_ROWS, le=MAX_ROWS)
    cols: int = Field(default=DEFAULT_COLS, ge=MIN_COLS, le=MAX_COLS)
    mines: int = Field(default=DEFAULT_MINE_COUNT, ge=MIN_MINES, le=MAX_MINES)
    interactive: bool = False   # <--- NEW
    game_mode: GameMode = GameMode.SOLO
    ai_difficulty: str = "medium"  # for co-op mode

    @model_validator(mode='after')
    def validate_mines_vs_cells(self):
        """
        Description: Validator that ensures the requested mine count fits
        within the requested board dimensions (reserves at least one safe cell).
        Inputs: self (NewGameParams)
        Outputs: self or raises ValueError on invalid mine count
        Author(s): Changwen Gong, John Tran
        Creation Date: 05 October 2025
        """
        total_cells = self.rows * self.cols
        max_allowed_mines = min(MAX_MINES, total_cells - 1)  # Leave at least one safe cell
        if self.mines > max_allowed_mines:
            raise ValueError(f"Too many mines for board size. Maximum allowed: {max_allowed_mines}")
        return self
    
class AIMove(BaseModel):
    """
    Description: Represents a single AI move returned to the frontend.
    Inputs: action string and optional BoardPos
    Outputs: validated move payload
    Author(s): Kobe Jordan, Raj Kaura
    Creation Date: 05 October 2025
    """
    action: str  # "reveal" | "flag" | "none"
    pos: BoardPos | None
    
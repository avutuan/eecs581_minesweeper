
from pydantic import BaseModel, model_validator

from .constants import (
    DEFAULT_COLS,
    DEFAULT_MINE_COUNT,
    DEFAULT_ROWS
)

from dataclasses import dataclass

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
    board: list[list[int | None]]
    revealed: list[list[bool]]
    flags: list[list[bool]]
    flag_count: int
    alive: bool
    win: bool

    def __getitem__(self, key):
        return getattr(self, key)

class BoardFrontendModel(BaseModel):
    ok: bool
    alive: bool | None = None
    win: bool | None = None
    error: str | None = None
    state: BoardStateModel | None = None

    def __getitem__(self, key):
        return getattr(self, key)

class NewGameParams(BaseModel):
    rows: int = DEFAULT_ROWS
    cols: int = DEFAULT_COLS
    mines: int = DEFAULT_MINE_COUNT
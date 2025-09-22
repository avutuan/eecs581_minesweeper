
from dataclasses import dataclass
from pydantic import BaseModel

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

class Click(BaseModel):
    row: int
    col: int

class NewGameParams(BaseModel):
    rows: int = 10
    cols: int = 10
    mines: int = 10
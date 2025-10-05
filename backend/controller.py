"""
Name: controller.py
Description: A controller for the Minesweeper game.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Riley Meyerkorth
Creation Date: 10 September 2025
"""

from .board import Board
from .models import BoardPos
from .constants import (
    DEFAULT_MINE_COUNT,
    KEY_QUIT,
    LETTER_TO_ROW
)

class Controller:
    """
    Description: A controller for the Minesweeper game.
    External Sources: N/A
    Author(s): Riley Meyerkorth
    Creation Date: 10 September 2025
    """
    """
    A controller for the Minesweeper game.
    Mainly just runs a simple CLI game loop for testing.
    """
    def __init__(self):
        self._board: Board = Board(DEFAULT_MINE_COUNT)
        self._row: int = 0
        self._col: int = 0
        self._pos: BoardPos = BoardPos(x=self._row, y=self._col)
        self._running: bool = True

    def run(self):
        """
        Runs a simple CLI game loop for testing.
        """
        # Initialize game
        self._init_game()
        
        # Main game loop
        self._running = True
        while self._running:
            self._running = self._gameloop()

    def _init_game(self):
        """
        Initializes the game by setting up the board and handling the first click.
        The first click determines mine placement.
        """
        # Init board
        self._board.print_board()

        # First click: place mines around it and compute counts
        first_click = input("Enter your first click (e.g. A5): ")
        self._row = LETTER_TO_ROW[first_click[0].upper()]
        self._col = int(first_click[1:]) - 1
        self._pos = BoardPos(x=self._row, y=self._col)

        # Place mines and reveal first cell
        self._board.place_mines(self._pos)
        self._board.update_mine_counts()
        self._board.reveal_cell(self._pos)


    def _gameloop(self) -> bool:
        """
        The function that runs every game loop iteration.
        Returns True if the game should continue, False if it should end.
        """
        self._board.print_board()
        click = input(f"Enter your next click (e.g. A5), or '{KEY_QUIT}' to quit: ")
        if click.lower() == KEY_QUIT:
            return False
        row = LETTER_TO_ROW[click[0].upper()]
        col = int(click[1:]) - 1
        pos = BoardPos(x=row, y=col)
        if not self._board.reveal_cell(pos):
            self._board.print_board(show_mines=True)
            print("Game Over! You hit a mine.")
            return False
        
        # Check for win after a successful reveal
        if self._board.check_win():
            print("Congratulations! You cleared the board.")
            self._board.print_board(show_mines=True)
            return False

        # Continue the game loop
        return True

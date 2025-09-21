"""
Name: board.py
Description: Board representation and logic for the Minesweeper game.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Aiden Burke, Riley Meyerkorth
Creation Date: 1 September 2025
"""

from constants import CELL_BLANK, CELL_MINE, CHAR_MINE, CHAR_UNREVEALED, DEFAULT_COLS, DEFAULT_ROWS, ROW_TITLES
from directions import DIRECTIONS
from dataclasses import dataclass

@dataclass
class BoardPos:
    """
    A dataclass to represent a position on the board with x (row) and y (column) coordinates.
    """
    x: int
    y: int

@dataclass
class BoardSize:
    """
    A dataclass to represent the size of the board with rows and columns.
    """
    rows: int
    cols: int

class Board:
    '''
    General Idea:
    store the board as a 2D array of ints where each int is the number of adjacent mines, CELL_MINE if mine
    also store a 2D array of booleans to track revealed cells
    provide methods to reveal cells, check for win/loss, print the board, etc.
    '''

    #TODO: change mine count to be user-specified, default 10x10 board, label columns and rows
    #TODO: add flags functionality and counter of remaining flags/mines

    def __init__(self, mines: int):
        self.mines: int = mines
        self.size: BoardSize = BoardSize(DEFAULT_ROWS, DEFAULT_COLS)
        self.board: list[list[int]] = [[0 for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        # store board as array of ints where each int is the number of adjacent mines, CELL_MINE if mine
        self.revealed: list[list[bool]] = [[False for _ in range(self.size.cols)] for _ in range(self.size.rows)]

    def place_mines(self, first_pos: BoardPos) -> None:
        """
        Places mines on the board, ensuring the first click is not a mine.

        first_pos: BoardPos object representing the first cell clicked by the user
        """
        # this implementation of place_mines will guarantee first click to be on a 0 cell for better playability
        from random import randint
        rows, cols = self.size.rows, self.size.cols
        mines_placed = 0

        # Place mines randomly until we reach the desired mine count
        while mines_placed < self.mines:
            r = randint(0, rows - 1)
            c = randint(0, cols - 1)

            # Ensure we don't place a mine on the first clicked cell or its adjacent cells
            if (r not in [first_pos.x-1, first_pos.x, first_pos.x+1] or c not in [first_pos.y-1, first_pos.y, first_pos.y+1]) and self.board[r][c] != CELL_MINE:
                self.board[r][c] = CELL_MINE
                mines_placed += 1
 
    def update_mine_counts(self) -> None:
        """
        Updates the mine counts for each cell based on adjacent mines.
        Called after placing mines.
        """
        rows, cols = self.size.rows, self.size.cols

        # Update counts for each cell
        for r in range(rows):
            for c in range(cols):

                # Skip if it's a mine
                if self.board[r][c] == CELL_MINE:
                    continue
                
                # Count adjacent mines
                count = 0
                for dr, dc in DIRECTIONS:
                    nPos = BoardPos(r + dr, c + dc)

                    # Check bounds and if it's a mine
                    if 0 <= nPos.x < rows and 0 <= nPos.y < cols and self.board[nPos.x][nPos.y] == CELL_MINE:
                        count += 1

                # Update the cell with the count
                self.board[r][c] = count

    
    def reveal_cell(self, pos: BoardPos) -> bool:
        """
        Reveals the cell at `pos`. If the cell has 0 adjacent mines, recursively reveals adjacent cells.
        Called after each pos, revealing the cell at (row, col) and any adjacent cells if it has 0 adjacent mines
        Returns False if a mine is revealed (game over), True otherwise.
        pos: BoardPos object representing the cell to reveal
        """
        row, col = pos.x, pos.y
        rows, cols = self.size.rows, self.size.cols

        # If the cell is a mine, game over
        if self.board[row][col] == CELL_MINE:
            self.revealed[row][col] = True
            return False
        
        # If the cell is already revealed, do nothing
        if self.revealed[row][col]:
            return True
        
        # Reveal the cell
        self.revealed[row][col] = True

        # If the cell is blank, recursively reveal adjacent cells
        if self.board[row][col] == CELL_BLANK:
            for dr, dc in DIRECTIONS:
                nPos = BoardPos(row + dr, col + dc)
                if 0 <= nPos.x < rows and 0 <= nPos.y < cols and not self.revealed[nPos.x][nPos.y]:
                    self.reveal_cell(nPos)
        return True
    
    def check_win(self) -> bool:
        """
        Checks if the player has won the game (all non-mine cells revealed).
        Returns True if the player has won, False otherwise.
        """
        # win condition: all non-mine cells revealed
        rows, cols = self.size.rows, self.size.cols
        for r in range(rows):
            for c in range(cols):
                # If it's not a mine and not revealed, not a win and return early
                if self.board[r][c] != CELL_MINE and not self.revealed[r][c]:
                    return False
        return True
    
    def _print_column_titles(self) -> None:
        """
        Prints the column titles for the board.
        """
        print(f"    ", end='')
        for i in range(self.size.cols): # number of columns
            print(f"| {i+1} ", end='')
        print("|")
        print((self.size.cols*4+4)*"-")

    def _print_row(self, row: int, show_mines: bool) -> None:
        """
        Prints a single row of the board.
        row: int representing the row index to print
        """
        print(f"{ROW_TITLES[row]} |", end=' ')
        for col in range(self.size.cols): # number of columns
            if self.revealed[row][col]:
                if self.board[row][col] == CELL_MINE:
                    print(f"  {CHAR_MINE}", end=' ')
                else:
                    print(f"  {self.board[row][col]}", end=' ')
            else:
                print(f"  {CHAR_UNREVEALED}", end=' ')
            # else:
            #     if show_mines and self.board[r][c] == CELL_MINE:
            #         print('X', end=' ')
            #     else:
            #         print(self.board[r][c], end=' ')
        print()

    
    def print_board(self, show_mines: bool = False) -> None:
        """
        Prints the board to console.
        Primarily for debugging purposes.
        """
        self._print_column_titles()

        # Print each row
        for r in range(self.size.rows): # number of rows
            self._print_row(r, show_mines)

    def to_dict(self, reveal_all: bool = False) -> dict[str, any]:
        """
        Convert board state to dictionary format expected by frontend
        """
        rows, cols = self.size.rows, self.size.cols
        board = [[None for _ in range(cols)] for _ in range(rows)]
        flags = [[False for _ in range(cols)] for _ in range(rows)]  # TODO: implement flags
        
        # Fill in board with current state
        for r in range(rows):
            for c in range(cols):
                if self.revealed[r][c] or reveal_all:
                    board[r][c] = self.board[r][c]
                else:
                    board[r][c] = None
        
        # Return the board state as a dictionary
        return {
            'rows': rows,
            'cols': cols, 
            'mines': self.mines,
            'board': board,
            'revealed': [row[:] for row in self.revealed],
            'flags': flags,
            'alive': True,  # TODO: track game state
            'win': self.check_win()
        }

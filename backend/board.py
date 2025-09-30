"""
Name: board.py
Description: Board representation and logic for the Minesweeper game.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Aiden Burke, Riley Meyerkorth
Creation Date: 1 September 2025
"""

from .models import (
    BoardStateModel,
    BoardSize,
    BoardPos
)
from .constants import (
    CELL_BLANK,
    CELL_MINE,
    CHAR_MINE,
    CHAR_UNREVEALED,
    DEFAULT_COLS,
    DEFAULT_ROWS,
    ROW_TITLES,
    DIRECTIONS
)
import random



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
        # store board as array of ints where each int is the number of adjacent mines, CELL_MINE if mine
        self.board: list[list[int]] = [[0 for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        self.revealed: list[list[bool]] = [[False for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        # flags are tracked separately from board values
        self.flags: list[list[bool]] = [[False for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        self.flag_count: int = 0
        self.isAlive: bool = True
        
    def _hidden_neighbors(self, pos: BoardPos) -> list[BoardPos]:
        rows, cols = self.size.rows, self.size.cols
        neighbors = []
        for dr, dc in DIRECTIONS:
            r, c = pos.x + dr, pos.y + dc
            if 0 <= r < rows and 0 <= c < cols and not self.revealed[r][c] and not self.flags[r][c]:
                neighbors.append(BoardPos(x=r, y=c))
        return neighbors

    def _flagged_neighbors(self, pos: BoardPos) -> list[BoardPos]:
        rows, cols = self.size.rows, self.size.cols
        neighbors = []
        for dr, dc in DIRECTIONS:
            r, c = pos.x + dr, pos.y + dc
            if 0 <= r < rows and 0 <= c < cols and self.flags[r][c]:
                neighbors.append(BoardPos(x=r, y=c))
        return neighbors

    def ai_move_easy(self) -> tuple[str, BoardPos]:
        """Pick any hidden cell at random."""
        hidden = [
            BoardPos(r, c)
            for r in range(self.size.rows)
            for c in range(self.size.cols)
            if not self.revealed[r][c] and not self.flags[r][c]
        ]
        if not hidden:
            return ("none", None)
        return ("reveal", random.choice(hidden))

    def ai_move_medium(self) -> tuple[str, BoardPos]:
        """Apply flag/reveal neighbor rules, else random."""
        for r in range(self.size.rows):
            for c in range(self.size.cols):
                if not self.revealed[r][c]:
                    continue
                value = self.board[r][c]
                if value in (CELL_BLANK, CELL_MINE):
                    continue

                hidden = self._hidden_neighbors(BoardPos(x=r, y=c))
                flagged = self._flagged_neighbors(BoardPos(x=r, y=c))

                # Rule 1: all hidden neighbors are mines
                if len(hidden) > 0 and len(hidden) == value - len(flagged):
                    return ("flag", hidden[0])

                # Rule 2: all other hidden neighbors are safe
                if len(flagged) == value and len(hidden) > 0:
                    return ("reveal", hidden[0])

        # Fallback: random
        return self.ai_move_easy()

    def ai_move_hard(self) -> tuple[str, BoardPos]:
        """Apply medium + 1-2-1 pattern rule."""
        # Check rows for 1-2-1 patterns
        for r in range(self.size.rows):
            for c in range(self.size.cols - 2):
                if (
                    self.revealed[r][c]
                    and self.revealed[r][c + 1]
                    and self.revealed[r][c + 2]
                    and self.board[r][c] == 1
                    and self.board[r][c + 1] == 2
                    and self.board[r][c + 2] == 1
                ):
                    # Deduce: outer neighbors are mines, middle safe
                    # Return one of those moves
                    hidden_left = self._hidden_neighbors(BoardPos(r, c))
                    hidden_mid = self._hidden_neighbors(BoardPos(r, c + 1))
                    hidden_right = self._hidden_neighbors(BoardPos(r, c + 2))
                    if hidden_mid:
                        return ("reveal", hidden_mid[0])
                    if hidden_left:
                        return ("flag", hidden_left[0])
                    if hidden_right:
                        return ("flag", hidden_right[0])
        # Fallback to medium
        return self.ai_move_medium()

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
                    nPos = BoardPos(x=r + dr, y=c + dc)

                    # Check bounds and if it's a mine
                    if 0 <= nPos.x < rows and 0 <= nPos.y < cols and self.board[nPos.x][nPos.y] == CELL_MINE:
                        count += 1

                # Update the cell with the count
                self.board[r][c] = count

    def flag_cell(self, pos: BoardPos) -> None:
        """
        Flags or unflags the cell at `pos`.
        pos: BoardPos object representing the cell to flag/unflag
        """
        row, col = pos.x, pos.y
        # Do not allow flagging revealed cells
        if self.revealed[row][col]:
            return
        # Toggle flag state without modifying underlying board values
        self.flags[row][col] = not self.flags[row][col]
        self.flag_count += 1 if self.flags[row][col] else -1

    def reveal_cell(self, pos: BoardPos) -> bool:
        """
        Reveals the cell at `pos`. If the cell has 0 adjacent mines, recursively reveals adjacent cells.
        Called after each pos, revealing the cell at (row, col) and any adjacent cells if it has 0 adjacent mines
        Returns False if a mine is revealed (game over), True otherwise.
        pos: BoardPos object representing the cell to reveal
        """
        row, col = pos.x, pos.y
        rows, cols = self.size.rows, self.size.cols

        # Don't reveal flagged cells
        if self.flags[row][col]:
            return True

        # If the cell is a mine, game over
        if self.board[row][col] == CELL_MINE:
            self.revealed[row][col] = True
            self.isAlive = False
            return False
        
        # If the cell is already revealed, do nothing
        if self.revealed[row][col]:
            return True
        
        # Reveal the cell
        self.revealed[row][col] = True

        # If the cell is blank, recursively reveal adjacent cells.
        # IMPORTANT: Do not reveal mines during flood fill.
        if self.board[row][col] == CELL_BLANK:
            for dr, dc in DIRECTIONS:
                nPos = BoardPos(x=row + dr, y=col + dc)
                if 0 <= nPos.x < rows and 0 <= nPos.y < cols and not self.revealed[nPos.x][nPos.y]:
                    # Skip revealing mines during expansion
                    if self.board[nPos.x][nPos.y] != CELL_MINE:
                        self.reveal_cell(nPos)
        return True
    
    def check_win(self) -> bool:
        """
        Checks if the player has won the game (all non-mine cells revealed).
        Returns True if the player has won, False otherwise.
        """
        # win condition: all non-mine cells revealed (flags are cosmetic)
        rows, cols = self.size.rows, self.size.cols
        for r in range(rows):
            for c in range(cols):
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

    def to_dict(self, reveal_all: bool = False) -> BoardStateModel:
        """
        Convert board state to dictionary format expected by frontend
        """
        rows, cols = self.size.rows, self.size.cols
        board = [[None for _ in range(cols)] for _ in range(rows)]
        flags = [[False for _ in range(cols)] for _ in range(rows)]
        
        # Fill in board with current state
        for r in range(rows):
            for c in range(cols):
                if self.revealed[r][c] or reveal_all:
                    board[r][c] = self.board[r][c]
                else:
                    board[r][c] = None

                # Fill in flags from separate matrix
                flags[r][c] = self.flags[r][c]
        
        # Return the board state as a dictionary
        return BoardStateModel(
            rows=rows,
            cols=cols,
            mines=self.mines,
            board=board,
            revealed=[row[:] for row in self.revealed],
            flags=flags,
            flag_count=self.flag_count,
            alive=self.isAlive,
            win=self.check_win()
        )
        
    

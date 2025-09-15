# board.py
from constants import CHAR_MINE, CHAR_UNREVEALED, COLUMN_TITLES, DEFAULT_COLS, DEFAULT_ROWS, ROW_TITLES
from directions import DIRECTIONS
from dataclasses import dataclass

@dataclass
class BoardPos:
    """
    A dataclass to represent a position on the board with x (row) and y (column) coordinates.
    """
    x: int
    y: int

class Board:
    '''
    General Idea:
    store the board as a 2D array of ints where each int is the number of adjacent mines, -1 if mine
    also store a 2D array of booleans to track revealed cells
    provide methods to reveal cells, check for win/loss, print the board, etc.
    '''

    #TODO: change mine count to be user-specified, default 10x10 board, label columns and rows
    #TODO: add flags functionality and counter of remaining flags/mines

    def __init__(self, mines):
        rows = DEFAULT_ROWS
        cols = DEFAULT_COLS
        self.mines = mines
        self.size = (rows, cols)
        self.board = [[0 for _ in range(cols)] for _ in range(rows)] 
        # store board as array of ints where each int is the number of adjacent mines, -1 if mine
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]

    def place_mines(self, first_pos: BoardPos) -> None:
        """
        Places mines on the board, ensuring the first click is not a mine.

        first_pos: BoardPos object representing the first cell clicked by the user
        """
        # this implementation of place_mines will guarantee first click to be on a 0 cell for better playability
        from random import randint
        rows, cols = self.size
        mines_placed = 0
        while mines_placed < self.mines:
            r = randint(0, rows - 1)
            c = randint(0, cols - 1)
            if (r not in [first_pos.x-1, first_pos.x, first_pos.x+1] or c not in [first_pos.y-1, first_pos.y, first_pos.y+1]) and self.board[r][c] != -1:
                self.board[r][c] = -1
                mines_placed += 1
 
    def update_mine_counts(self) -> None:
        """
        Updates the mine counts for each cell based on adjacent mines.
        Called after placing mines.
        """
        rows, cols = self.size
        for r in range(rows):
            for c in range(cols):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for dr, dc in DIRECTIONS:
                    nPos = BoardPos(r + dr, c + dc)
                    if 0 <= nPos.x < rows and 0 <= nPos.y < cols and self.board[nPos.x][nPos.y] == -1:
                        count += 1
                self.board[r][c] = count

    
    def reveal_cell(self, pos: BoardPos) -> bool:
        """
        Reveals the cell at `pos`. If the cell has 0 adjacent mines, recursively reveals adjacent cells.
        Called after each pos, revealing the cell at (row, col) and any adjacent cells if it has 0 adjacent mines
        Returns False if a mine is revealed (game over), True otherwise.
        pos: BoardPos object representing the cell to reveal
        """
        row, col = pos.x, pos.y
        rows, cols = self.size
        if self.board[row][col] == -1:
            self.revealed[row][col] = True
            return False
        if self.revealed[row][col]:
            return True
        self.revealed[row][col] = True
        if self.board[row][col] == 0: # recursively update adjacent cells if 0
            for dr, dc in DIRECTIONS:
                nPos = BoardPos(row + dr, col + dc)
                if 0 <= nPos.x < rows and 0 <= nPos.y < cols and not self.revealed[nPos.x][nPos.y]:
                    self.reveal_cell(nPos)
        return True

    
    def check_win(self):
        """
        Checks if the player has won the game (all non-mine cells revealed).
        TODO: Implement this method.
        """
        assert False

    
    def print_board(self, show_mines=False):
        """
        Prints the board to console.
        Primarily for debugging purposes.
        """
        rows, cols = self.size

        # Print column titles
        print(f"    ", end='')
        for i in range(cols):
            print(f"| {i+1} ", end='')
        print("|")
        print((self.size[1]*4+4)*"-")

        # Print each row
        for r in range(rows):
            print(f"{ROW_TITLES[r]} |", end=' ')
            for c in range(cols):
                if self.revealed[r][c]:
                    if self.board[r][c] == -1:
                        print(f"  {CHAR_MINE}", end=' ')
                    else:
                        print(f"  {self.board[r][c]}", end=' ')
                else:
                    print(f"  {CHAR_UNREVEALED}", end=' ')
                # else:
                #     if show_mines and self.board[r][c] == -1:
                #         print('X', end=' ')
                #     else:
                #         print(self.board[r][c], end=' ')
            print()

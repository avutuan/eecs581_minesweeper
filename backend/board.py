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
    BoardPos,
    GameMode,
    PlayerType
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
    """
    Description: Manages the Minesweeper board state and game logic
    Author(s): Aiden Burke, Riley Meyerkorth, Raj Kaura, Kobe Jordan
    Creation Date: 1 September 2025
    External Sources: N/A
    """
    '''
    General Idea:
    store the board as a 2D array of ints where each int is the number of adjacent mines, CELL_MINE if mine
    also store a 2D array of booleans to track revealed cells
    provide methods to reveal cells, check for win/loss, print the board, etc.
    '''

    def __init__(self, mines: int, game_mode: GameMode = GameMode.SOLO):
        """
        Description: initializes the board with given number of mines and size
        Inputs: mines (int): number of mines to place on the board, game_mode (GameMode): game mode (solo or co-op)
        Outputs: None
        Author(s): Aiden Burke, Riley Meyerkorth, Raj Kaura, Kobe Jordan
        Creation Date: 1 September 2025
        External Sources: N/A
        """

        # Initialize board properties
        self.mines: int = mines
        self.size: BoardSize = BoardSize(DEFAULT_ROWS, DEFAULT_COLS)
        # store board as array of ints where each int is the number of adjacent mines, CELL_MINE if mine
        self.board: list[list[int]] = [[0 for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        self.revealed: list[list[bool]] = [[False for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        # flags are tracked separately from board values
        self.flags: list[list[bool]] = [[False for _ in range(self.size.cols)] for _ in range(self.size.rows)]
        self.flag_count: int = 0
        self.isAlive: bool = True
        
        # Co-op mode fields
        self.game_mode: GameMode = game_mode
        self.current_player: PlayerType = PlayerType.HUMAN
        self.human_alive: bool = True
        self.ai_alive: bool = True
        self.winner: PlayerType | None = None
        self.game_over: bool = False
    
    def handle_player_move(self, pos: BoardPos, player: PlayerType) -> bool:
        """
        Description: handles a move by a specific player in co-op mode
        Inputs: pos (BoardPos): position of the cell to reveal, player (PlayerType): player making the move
        Outputs: bool: True if the move was successful, False if the player hit a mine
        Author(s): Aiden Burke, Riley Meyerkorth, Raj Kaura, Kobe Jordan
        Creation Date: 1 September 2025
        External Sources: N/A
        """
        """
        Handle a move by a specific player in co-op mode.
        Returns True if the move was successful, False if the player hit a mine.
        """
        
        # Solo mode behaves as normal
        if self.game_mode != GameMode.COOP:
            return self.reveal_cell(pos)
        
        # Check if it's the player's turn and if they are alive
        if self.current_player != player:
            return False  # Not this player's turn

        # Check if the player is alive
        if player == PlayerType.HUMAN and not self.human_alive:
            return False  # Human player is out
        if player == PlayerType.AI and not self.ai_alive:
            return False  # AI player is out
        
        # Make the move
        success = self.reveal_cell(pos)

        # Check if someone hit a mine
        if not success:
            # Player hit a mine, they lose
            if player == PlayerType.HUMAN:
                self.human_alive = False
                self.winner = PlayerType.AI
            # AI player hit a mine, they lose
            else: 
                self.ai_alive = False
                self.winner = PlayerType.HUMAN
            self.game_over = True
        else:
            # Switch turns
            self.current_player = PlayerType.AI if player == PlayerType.HUMAN else PlayerType.HUMAN
        
        return success
    
    def check_coop_win(self) -> bool:
        """
        Description: checks if the game is won in co-op mode (all non-mine cells revealed)
        Inputs: None
        Outputs: bool: True if the game is won, False otherwise
        Author(s): Raj Kaura, Kobe Jordan
        Creation Date: 3 October 2025
        External Sources: N/A
        """
        """
        Check if the game is won in co-op mode (all non-mine cells revealed).
        """
        if self.game_mode != GameMode.COOP:
            return self.check_win()
        
        # In co-op mode, if all cells are revealed without anyone hitting a mine,
        # it's a draw (both players win)
        if self.check_win() and not self.game_over:
            self.winner = None  # Draw
            self.game_over = True
            return True
        
        return False
        
    def _hidden_neighbors(self, pos: BoardPos) -> list[BoardPos]:
        """
        Description: returns a list of hidden neighbors for a given position
        Inputs: pos (BoardPos): position to check neighbors for
        Outputs: list[BoardPos]: list of hidden neighbor positions
        Author(s): Raj Kaura, Kobe Jordan
        Creation Date: 3 October 2025
        External Sources: N/A
        """
        # Initialize variables
        rows, cols = self.size.rows, self.size.cols
        neighbors = []
        # Check all 8 possible directions for hidden neighbors
        for dr, dc in DIRECTIONS:
            r, c = pos.x + dr, pos.y + dc
            if 0 <= r < rows and 0 <= c < cols and not self.revealed[r][c] and not self.flags[r][c]:
                neighbors.append(BoardPos(x=r, y=c))
        # Return the list of hidden neighbors
        return neighbors

    def _flagged_neighbors(self, pos: BoardPos) -> list[BoardPos]:
        """
        Description: returns a list of flagged neighbors for a given position
        Inputs: pos (BoardPos): position to check neighbors for
        Outputs: list[BoardPos]: list of flagged neighbor positions
        Author(s): Raj Kaura, Kobe Jordan
        Creation Date: 3 October 2025
        External Sources: N/A
        """
        # Initialize variables
        rows, cols = self.size.rows, self.size.cols
        neighbors = []
        # Check all 8 possible directions for flagged neighbors
        for dr, dc in DIRECTIONS:
            r, c = pos.x + dr, pos.y + dc
            if 0 <= r < rows and 0 <= c < cols and self.flags[r][c]:
                neighbors.append(BoardPos(x=r, y=c))
        # Return the list of flagged neighbors
        return neighbors

    def ai_move_easy(self) -> tuple[str, BoardPos]:
        """
        Description: picks any hidden cell at random
        Inputs: None
        Outputs: tuple[str, BoardPos]: ("flag" or "reveal", position to act on)
        Author(s): Raj Kaura, Kobe Jordan
        Creation Date: 3 October 2025
        External Sources: N/A
        """
        """Pick any hidden cell at random."""
        # Get list of all hidden cells
        hidden = [
            BoardPos(x=r, y=c)
            for r in range(self.size.rows)
            for c in range(self.size.cols)
            if not self.revealed[r][c] and not self.flags[r][c]
        ]
        # Randomly choose to flag or reveal a hidden cell
        if not hidden:
            return ("none", None)
        return ("reveal", random.choice(hidden))

    def ai_move_medium(self) -> tuple[str, BoardPos]:
        """
        Description: applies flag/reveal neighbor rules, else random
        Inputs: None
        Outputs: tuple[str, BoardPos]: ("flag" or "reveal", position to act on)
        Author(s): Raj Kaura, Kobe Jordan
        Creation Date: 3 October 2025
        External Sources: N/A
        """
        """Apply flag/reveal neighbor rules, else random."""
        # Check all revealed cells for rules
        for r in range(self.size.rows):
            for c in range(self.size.cols):
                # Only consider revealed cells with numbers
                if not self.revealed[r][c]:
                    continue
                # Get the value of the cell
                value = self.board[r][c]
                # Skip blank cells and mines
                if value in (CELL_BLANK, CELL_MINE):
                    continue

                # Get hidden and flagged neighbors
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
        """
        Description: applies medium + 1-2-1 pattern rule, else medium
        Inputs: None
        Outputs: tuple[str, BoardPos]: ("flag" or "reveal", position to act on)
        Author(s): Raj Kaura, Kobe Jordan
        Creation Date: 3 October 2025
        External Sources: N/A
        """
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
        Description: places mines on the board, ensuring the first click is not a mine
        Inputs: first_pos (BoardPos): position of the first cell clicked by the user
        Outputs: None
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: updates the mine counts for each cell based on adjacent mines
        Inputs: None
        Outputs: None
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: flags or unflags the cell at the given position
        Inputs: pos (BoardPos): position of the cell to flag/unflag
        Outputs: None
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: reveals the cell at the given position, recursively reveals adjacent cells if it's blank
        Inputs: pos (BoardPos): position of the cell to reveal
        Outputs: bool: False if a mine is revealed (game over), True otherwise
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: checks if the player has won the game (all non-mine cells revealed)
        Inputs: None
        Outputs: bool: True if the player has won, False otherwise
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: prints the column titles for the board
        Inputs: None
        Outputs: None
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: prints a single row of the board
        Inputs: row (int): the row index to print, show_mines (bool): whether to show mines (for debugging)
        Outputs: None
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: prints the board to console
        Inputs: show_mines (bool): whether to show mines (for debugging)
        Outputs: None
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
        Description: converts the board state to a dictionary format expected by the frontend
        Inputs: reveal_all (bool): whether to reveal all cells (for game over)
        Outputs: BoardStateModel: dictionary representation of the board state
        Author(s): Riley Meyerkorth, Aiden Burke
        Creation Date: 1 September 2025
        External Sources: N/A
        """
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
            win=self.check_win(),
            # Co-op mode fields
            game_mode=self.game_mode,
            current_player=self.current_player,
            human_alive=self.human_alive,
            ai_alive=self.ai_alive,
            winner=self.winner,
            game_over=self.game_over
        )
        
    

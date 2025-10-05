"""
Name: constants.py
Description: Constants for the Minesweeper game. Primarily for minimizing magic values.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Riley Meyerkorth
Creation Date: 10 September 2025
"""

### API CONFIG
API_HOST = "0.0.0.0"
API_PORT = 8000
API_PREFIX = "/api"

class APIRoutes:
    """
    Description: Defines API route constants.
    Author(s): Riley Meyerkorth
    Creation Date: 10 September 2025
    External Sources: N/A
    """
    """
    Defines API route constants.
    """
    API_ROUTE_NEW_GAME = f"{API_PREFIX}/new"
    API_ROUTE_STATE = f"{API_PREFIX}/state"
    API_ROUTE_CLICK = f"{API_PREFIX}/click"
    API_ROUTE_FLAG = f"{API_PREFIX}/flag"

### VISUALS
CHAR_MINE = '*'
CHAR_FLAG = 'F'
CHAR_UNREVEALED = '/'
COLUMN_TITLES = '12345678910'
ROW_TITLES = 'ABCDEFGHIJ'

### GAME CONFIG
DEFAULT_ROWS = 10
DEFAULT_COLS = 10
DEFAULT_MINE_COUNT = 10

# Validation constraints
MIN_ROWS = 10
MAX_ROWS = 20
MIN_COLS = 10
MAX_COLS = 20
MIN_MINES = 10
MAX_MINES = 20

### GAME_DATA
CELL_MINE = -1
CELL_BLANK = 0

### INPUT
KEY_QUIT = 'q'

### UTILS
LETTER_TO_ROW = {chr(i + ord('A')): i for i in range(DEFAULT_ROWS)}

class Direction:
    """
    Description: Enum-like class to represent possible movement directions.
    Author(s): Riley Meyerkorth
    Creation Date: 10 September 2025
    External Sources: N/A
    """
    """
    Enum-like class to represent possible movement directions.
    """
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)
    UP_LEFT = (-1, -1)
    UP_RIGHT = (-1, 1)
    DOWN_LEFT = (1, -1)
    DOWN_RIGHT = (1, 1)

"""
An array of all possible directions to check adjacent cells.
"""
DIRECTIONS = [Direction.UP_LEFT, Direction.UP, Direction.UP_RIGHT, Direction.LEFT, Direction.RIGHT, Direction.DOWN_LEFT, Direction.DOWN, Direction.DOWN_RIGHT]

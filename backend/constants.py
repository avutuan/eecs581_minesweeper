"""
Name: constants.py
Description: Constants for the Minesweeper game. Primarily for minimizing magic values.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Riley Meyerkorth
Creation Date: 10 September 2025
"""

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

### GAME_DATA
CELL_MINE = -1
CELL_BLANK = 0

### INPUT
KEY_QUIT = 'q'

### UTILS
LETTER_TO_ROW = {chr(i + ord('A')): i for i in range(DEFAULT_ROWS)}
"""
Name: directions.py
Description: Defines the possible directions for movement in the game.
Inputs: None
Outputs: None
External Sources: N/A
Author(s): Riley Meyerkorth
Creation Date: 10 September 2025
"""

class Direction:
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

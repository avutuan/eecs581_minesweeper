# directions.py

class Direction:
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

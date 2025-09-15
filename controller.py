# controller.py

from board import Board, BoardPos
from constants import DEFAULT_MINE_COUNT, KEY_QUIT, LETTER_TO_ROW

class Controller:
    def run(self):
        """
        Runs a simple CLI game loop for testing.
        """
        b = Board(DEFAULT_MINE_COUNT)

        b.print_board()
        first_click = input("Enter your first click (e.g. A5): ")
        row = LETTER_TO_ROW[first_click[0].upper()]
        col = int(first_click[1:]) - 1
        pos = BoardPos(row, col)
        b.place_mines(pos)
        b.update_mine_counts()
        b.reveal_cell(pos)
        while True:
            b.print_board()
            click = input(f"Enter your next click (e.g. A5), or '{KEY_QUIT}' to quit: ")
            if click.lower() == KEY_QUIT:
                break
            row = LETTER_TO_ROW[click[0].upper()]
            col = int(click[1:]) - 1
            pos = BoardPos(row, col)
            if not b.reveal_cell(pos):
                print("Game Over! You hit a mine.")
                b.print_board(show_mines=True)
                break
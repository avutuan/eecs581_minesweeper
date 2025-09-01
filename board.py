class Board:
    '''
    store the board as a 2D array of ints where each int is the number of adjacent mines, -1 if mine
    also store a 2D array of booleans to track revealed cells
    provide methods to reveal cells, check for win/loss, and print the board
    1. __init__(difficulty): initialize board size and number of mines based on difficulty
    2. place_mines(first_click): randomly place mines on the board, ensuring first click is not a mine
    3. update_mine_counts(): calculate number of adjacent mines for each cell
    4. reveal_cell(row, col): reveal a cell, return False if mine, True otherwise; if cell has 0 adjacent mines, reveal neighbors recursively
    5. check_win(): check if all non-mine cells are revealed
    6. print_board(show_mines=False): print the board to console, optionally showing mines (mainly for debugging, not actual UI)
    '''
    def __init__(self, difficulty):
        '''
        difficulties        board size          mines
        1: easy             9x9                 10
        2: medium           16x16               40
        3: hard             30x16               99
        '''
        self.difficulty = difficulty
        rows = 9 if difficulty == 1 else 16
        cols = 9 if difficulty == 1 else 16 if difficulty == 2 else 30 
        self.mines = 10 if difficulty == 1 else 40 if difficulty == 2 else 99
        self.size = (rows, cols)
        self.board = [[0 for _ in range(cols)] for _ in range(rows)] 
        # store board as array of ints where each int is the number of adjacent mines, -1 if mine
        self.revealed = [[False for _ in range(cols)] for _ in range(rows)]

    def place_mines(self, first_click):
        # this implementation of place_mines will guarantee first click to be on a 0 cell for better playability
        from random import randint
        rows, cols = self.size
        mines_placed = 0
        while mines_placed < self.mines:
            r = randint(0, rows - 1)
            c = randint(0, cols - 1)
            if (r not in [first_click[0]-1, first_click[0], first_click[0]+1] or c not in [first_click[1]-1, first_click[1], first_click[1]+1]) and self.board[r][c] != -1:
                self.board[r][c] = -1
                mines_placed += 1

    '''
    def place_mines(self, first_click):
        # this implementation of place_mines will just guarantee first click to not be a mine
        from random import randint
        rows, cols = self.size
        mines_placed = 0
        while mines_placed < self.mines:
            r = randint(0, rows - 1)
            c = randint(0, cols - 1)
            if (r, c) != first_click and self.board[r][c] != -1:
                self.board[r][c] = -1
                mines_placed += 1
    '''
 
    def update_mine_counts(self):
        # call after place_mines to update counts of adjacent mines for each cell
        rows, cols = self.size
        directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
        for r in range(rows):
            for c in range(cols):
                if self.board[r][c] == -1:
                    continue
                count = 0
                for dr, dc in directions:
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < rows and 0 <= nc < cols and self.board[nr][nc] == -1:
                        count += 1
                self.board[r][c] = count

    def reveal_cell(self, click):
        row, col = click[0], click[1]
        # call after each click, revealing the cell at (row, col) and any adjacent cells if it has 0 adjacent mines
        rows, cols = self.size
        if self.board[row][col] == -1:
            return False
        if self.revealed[row][col]:
            return True
        self.revealed[row][col] = True
        if self.board[row][col] == 0: # recursively update adjacent cells if 0
            directions = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                if 0 <= nr < rows and 0 <= nc < cols and not self.revealed[nr][nc]:
                    self.reveal_cell((nr, nc))
        return True

    def check_win(self):
        # win condition: all non-mine cells revealed
        assert False # TODO

    def print_board(self, show_mines=False): # for debugging
        rows, cols = self.size
        for r in range(rows):
            for c in range(cols):
                if self.revealed[r][c]:
                    if self.board[r][c] == -1:
                        print('*', end=' ')
                    else:
                        print(self.board[r][c], end=' ')
                else:
                    print('/', end=' ')
                # else:
                #     if show_mines and self.board[r][c] == -1:
                #         print('X', end=' ')
                #     else:
                #         print(self.board[r][c], end=' ')
            print()

if __name__ == "__main__":
    b = Board(1)
    b.place_mines((4, 5))
    b.reveal_cell((4, 5))
    b.update_mine_counts()
    b.print_board()

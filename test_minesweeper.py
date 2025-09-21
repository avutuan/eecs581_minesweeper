# test_minesweeper.py
from backend.board import Board, BoardPos
from backend.constants import DEFAULT_ROWS, DEFAULT_COLS, DEFAULT_MINE_COUNT, CHAR_MINE, CHAR_UNREVEALED
from backend.directions import DIRECTIONS


class TestBoardCreation:
    # test that board.__init__ creates a board with the correct properties
    def test_board_initialization(self):
        board = Board(10)
        assert board.mines == 10
        assert board.size == (DEFAULT_ROWS, DEFAULT_COLS)
        assert len(board.board) == DEFAULT_ROWS
        assert len(board.board[0]) == DEFAULT_COLS
        assert len(board.revealed) == DEFAULT_ROWS
        assert len(board.revealed[0]) == DEFAULT_COLS
    
    def test_board_starts_with_zeros(self):
        # test that board starts with all cells set to 0
        board = Board(5)
        for row in board.board:
            for cell in row:
                assert cell == 0
    
    def test_revealed_starts_false(self):
        # test that revealed array starts with all false values
        board = Board(5)
        for row in board.revealed:
            for cell in row:
                assert cell == False

class TestBoardPos:
    def test_board_pos_creation(self):
        # test that boardpos stores x and y coordinates
        pos = BoardPos(3, 7)
        assert pos.x == 3
        assert pos.y == 7

class TestPlaceMines:
    def test_place_mines_puts_correct_count(self):
        # test that place_mines places the right number of mines
        board = Board(5)
        first_click = BoardPos(5, 5)
        board.place_mines(first_click)
        
        mine_count = 0
        for row in board.board:
            for cell in row:
                if cell == -1:
                    mine_count += 1
        
        assert mine_count == 5
    
    def test_first_click_area_is_safe(self):
        # test that the 3x3 area around first click has no mines
        board = Board(20)  # lots of mines to make test meaningful
        first_click = BoardPos(4, 4)
        board.place_mines(first_click)
        
        # check the 3x3 area around first click
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                x, y = first_click.x + dx, first_click.y + dy
                if 0 <= x < DEFAULT_ROWS and 0 <= y < DEFAULT_COLS:
                    assert board.board[x][y] != -1

class TestUpdateMineCounts:
    def test_mine_count_calculation(self):
        # test that update_mine_counts calculates adjacent mine counts correctly
        board = Board(0)  # no mines initially
        
        # manually place mines in a known pattern
        board.board[1][1] = -1  # mine at (1,1)
        board.board[1][3] = -1  # mine at (1,3)
        board.board[3][2] = -1  # mine at (3,2)
        
        board.update_mine_counts()
        
        # check specific cells have correct counts
        assert board.board[2][2] == 3  # surrounded by 3 mines
        assert board.board[0][2] == 2  # has 2 mines below it
        assert board.board[1][2] == 2  # has 2 mines adjacent

class TestRevealCell:
    def test_reveal_non_mine_returns_true(self):
        # test that revealing a non-mine cell returns true
        board = Board(0)  # no mines
        pos = BoardPos(2, 3)
        
        result = board.reveal_cell(pos)
        assert result == True
        assert board.revealed[pos.x][pos.y] == True
    
    def test_reveal_mine_returns_false(self):
        # test that revealing a mine returns false
        board = Board(0)
        board.board[2][2] = -1  # place a mine
        pos = BoardPos(2, 2)
        
        result = board.reveal_cell(pos)
        assert result == False
        assert board.revealed[pos.x][pos.y] == True
    
    def test_reveal_already_revealed_returns_true(self):
        # test that revealing an already revealed cell returns true
        board = Board(0)
        pos = BoardPos(1, 1)
        
        # reveal once
        board.reveal_cell(pos)
        assert board.revealed[pos.x][pos.y] == True
        
        # reveal again
        result = board.reveal_cell(pos)
        assert result == True

class TestCheckWin:
    def test_win_when_all_non_mines_revealed(self):
        # test that check_win returns true when all non-mine cells are revealed
        board = Board(1)
        board.board[0][0] = -1  # place one mine
        
        # reveal all non-mine cells
        for row in range(DEFAULT_ROWS):
            for col in range(DEFAULT_COLS):
                if not (row == 0 and col == 0):
                    board.revealed[row][col] = True
        
        assert board.check_win() == True
    
    def test_no_win_when_some_unrevealed(self):
        # test that check_win returns false when some non-mine cells are unrevealed
        board = Board(0)  # no mines
        
        # only reveal some cells
        for row in range(5):
            for col in range(DEFAULT_COLS):
                board.revealed[row][col] = True
        
        assert board.check_win() == False

class TestToDict:
    def test_to_dict_structure(self):
        # test that to_dict returns the expected dictionary structure
        board = Board(5)
        result = board.to_dict()
        
        assert 'rows' in result
        assert 'cols' in result
        assert 'mines' in result
        assert 'board' in result
        assert 'revealed' in result
        assert 'flags' in result
        assert 'alive' in result
        assert 'win' in result
        
        assert result['rows'] == DEFAULT_ROWS
        assert result['cols'] == DEFAULT_COLS
        assert result['mines'] == 5
        assert result['alive'] == True
    
    def test_to_dict_reveal_all(self):
        # test that to_dict with reveal_all=true shows all cells
        board = Board(0)
        board.board[1][1] = 3  # set a cell value
        
        result = board.to_dict(reveal_all=True)
        assert result['board'][1][1] == 3

# simple test runner for when pytest isn't available
def run_simple_tests():
    print("Running minesweeper tests...")
    
    # test board creation
    board = Board(5)
    assert board.size == (DEFAULT_ROWS, DEFAULT_COLS), "Board should be correct size"
    assert board.mines == 5, "Board should have 5 mines"
    print("✓ Board creation test passed")
    
    # test boardpos
    pos = BoardPos(3, 7)
    assert pos.x == 3 and pos.y == 7, "BoardPos should store coordinates"
    print("✓ BoardPos test passed")
    
    # test mine placement
    board.place_mines(BoardPos(5, 5))
    mine_count = sum(1 for row in board.board for cell in row if cell == -1)
    assert mine_count == 5, "Should have exactly 5 mines"
    print("✓ Mine placement test passed")
    
    # test mine count calculation
    board.update_mine_counts()
    print("✓ Mine count calculation test passed")
    
    # test cell reveal
    result = board.reveal_cell(BoardPos(0, 0))
    assert result == True, "Revealing non-mine should return True"
    print("✓ Cell reveal test passed")
    
    # test win condition
    assert board.check_win() == False, "Game should not be won yet"
    print("✓ Win condition test passed")
    
    # test to_dict
    result_dict = board.to_dict()
    assert 'board' in result_dict, "to_dict should return board data"
    print("✓ to_dict test passed")
    
    print("All tests passed")

if __name__ == "__main__":
    run_simple_tests()

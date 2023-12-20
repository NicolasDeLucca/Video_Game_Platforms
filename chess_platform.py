class Board:
    def __init__(self):
          # black
        self.board = [
            # 0    1    2    3    4    5    6    7 
            ['r', 'h', 'b', 'q', 'k', 'b', 'h', 'r'], # 0
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], # 1
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], # 2
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], # 3
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], # 4
            [' ', ' ', ' ', ' ', ' ', ' ', ' ', ' '], # 5
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], # 6
            ['R', 'H', 'B', 'Q', 'K', 'B', 'H', 'R']  # 7
        ] # white 

    def display(self):
        for row in self.board:
            print(' '.join(row))

    def make_move(self, piece_row, piece_col, new_row, new_col):
        self.board[new_row][new_col] = self.board[piece_row][piece_col]
        self.board[piece_row][piece_col] = ' '
        if self._is_castling_move(piece_row, piece_col, new_col): 
            rook_row = new_rook_row = piece_row
            if new_col == 2: 
                rook_col = new_col - 2 
                new_rook_col = new_col + 1 
            else: # new_col == 6
                rook_col = new_col + 1 
                new_rook_col = new_col - 1 
            # moves the rook
            self.board[new_rook_row][new_rook_col] = self.board[rook_row][rook_col]
            self.board[rook_row][rook_col] = ' '        

    def is_game_over(self):
        # checks if it is checkmate
        # checks if it is stalemate
        return False
    
    def is_legal_move(self, rules, piece_row, piece_col, new_row, new_col):
        # checks if the new position is not occupied by allied pieces
        # checks if the king is not being attacked
        # checks if the king is unattacked next
        # checks that if the piece is not a horse, then the path to the new position must be clear
        # checks that if the piece is a pawn and the move is a capture on the go, then the last opponent move must be a double pawn move 
        # checks that if it is a castling move, then:
            # the king must not have moved before
            # the rook must not have moved before
            # the king must not be in check
            # the king must not pass through a square that is attacked by an enemy piece (including the square the king is moving to)
            # there are no pieces between the king and the rook
        return True
    
    # helper methods

    def _is_castling_move(self, piece_row, piece_col, new_col):
        # checks if it is a king double move
        return (self.board[piece_row][piece_col]).lower() == 'k' and abs(piece_col - new_col) == 2

class Gameplay:
    def __init__(self):
        self.chess_rules = Rules()
        self.chess_board = Board()
        self.turn = 1 # white turn

    def play(self):
        self.chess_board.display()
        while not self.chess_board.is_game_over():
            try:
                piece_row = int(input('Piece row: ')) - 1
                piece_col = int(input('Piece column: ')) - 1
                new_row = int(input('Piece new row: ')) - 1
                new_col = int(input('Piece new column: ')) - 1
            except ValueError:
                print('Invalid input format: not a number')
                continue
            if self._is_valid_input(piece_row, piece_col, new_row, new_col):
                piece = self.chess_board.board[piece_row][piece_col]
                if piece != ' ' and self._is_player_piece(piece):
                    if self.chess_rules.is_piece_move(piece, piece_row, piece_col, new_row, new_col):
                        if self.chess_board.is_legal_move(piece_row, piece_col, new_row, new_col):
                            self.chess_board.make_move(piece_row, piece_col, new_row, new_col)
                            self.chess_board.display() # board refresh
                            self.turn = (self.turn % 2) + 1 # player update
                        else:
                            print('Invalid input: illegal move')
                    else:
                        print('Invalid input: wrong piece move')
                else:
                    print('Invalid input: wrong square')        
            else:
                print('Invalid input: out of board')           
    
    # helper methods       

    def _is_valid_input(self, piece_row, piece_col, new_row, new_col):
        return piece_row >= 0 and piece_row <= 7 and piece_col >= 0 and piece_col <= 7 and \
                   new_row >= 0 and new_row <= 7 and new_col >= 0 and new_col <= 7

    def _is_player_piece(self, piece):  
        return self.turn == 1 and piece.isupper() or self.turn == 2 and piece.islower()

class Rules:
    def is_piece_move(self, piece, piece_row, piece_col, new_row, new_col):
        # rememeber pieces basic rules
        if piece.upper() == 'P': # pawn   
            return self._is_pawn_move(piece, piece_row, piece_col, new_row, new_col)
        elif piece.upper() == 'R': # rook
            return self._is_rook_move(piece_row, piece_col, new_row, new_col)
        elif piece.upper() == 'H': # horse
            return self._is_knight_move(piece_row, piece_col, new_row, new_col)
        elif piece.upper() == 'B': # bishop
            return self._is_bishop_move(piece_row, piece_col, new_row, new_col)
        elif piece.upper() == 'Q': # queen
            return self._is_queen_move(piece_row, piece_col, new_row, new_col)
        elif piece.upper() == 'K': # king
            return self._is_king_move(piece, piece_row, piece_col, new_row, new_col)
    
    # helper methods

    def _is_rook_move(self, piece_row, piece_col, new_row, new_col):
        return piece_row == new_row and piece_col != new_col or \
            piece_col == new_col and piece_row != new_row

    def _is_knight_move(self, piece_row, piece_col, new_row, new_col):
        # checks if it is a L move
        return abs(piece_row - new_row) == 2 and abs(piece_col - new_col) == 1 or \
            abs(piece_row - new_row) == 1 and abs(piece_col - new_col) == 2

    def _is_bishop_move(self, piece_row, piece_col, new_row, new_col):
        return piece_row != new_row and abs(piece_row - new_row) == abs(piece_col - new_col)

    def _is_queen_move(self, piece_row, piece_col, new_row, new_col):
        return self._is_random_move(piece_row, piece_col, new_row, new_col, 7)

    def _is_king_move(self, piece, piece_row, piece_col, new_row, new_col):
        king_initial_row = 7 if piece.isupper() else 0 
        return self._is_random_move(piece_row, piece_col, new_row, new_col, 1) or \
            piece_row == new_row == king_initial_row and abs(piece_col - new_col) == 2 # castling move
        
    def _is_random_move(self, piece_row, piece_col, new_row, new_col, steps):
        return not (piece_row == new_row and piece_col == new_col) and \
            abs(piece_row - new_row) <= steps and abs(piece_col - new_col) <= steps

    def _is_pawn_move(self, piece, piece_row, piece_col, new_row, new_col):
        move_direction = -1 if piece.isupper() else 1 # white is up, black is down
        return self._is_simple_pawn_move(move_direction, piece_row, piece_col, new_row, new_col) or \
            self._is_double_pawn_move(move_direction, piece_row, piece_col, new_row, new_col)       

    def _is_simple_pawn_move(self, move_direction, piece_row, piece_col, new_row, new_col):
        # checks if it is a walk move or a capture move
        return new_row - piece_row == move_direction and abs(piece_col - new_col) <= 1
    
    def _is_double_pawn_move(self, move_direction, piece_row, piece_col, new_row, new_col):
        return new_row - piece_row == 2 * move_direction and piece_col == new_col and \
            piece_row == (7 + move_direction) % 7
    
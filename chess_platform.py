# Chess Platform development in Python

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

    def is_game_over(self, turn):
        king_piece = 'k' if turn == 1 else 'K'
        # find the king and checks if the player has other remaining pieces
        only_king_left = True
        king_row, king_col = None, None
        end_loops = False
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                square = self.board[row][col]
                if square == king_piece:
                    king_row, king_col = row, col
                elif square != ' ':
                    only_king_left = False
                    if king_row and king_col:
                        end_loops = True
                        break
            if end_loops:
                break        
        # get all adjacent cells to the king        
        adjacent_cells = [(king_row-1, king_col), (king_row+1, king_col), (king_row, king_col-1), (king_row, king_col+1),
                              (king_row-1, king_col-1), (king_row-1, king_col+1), (king_row+1, king_col-1), (king_row+1, king_col+1)]
        # the cells must be on the board
        adjacent_cells = [(row, col) for row, col in adjacent_cells if 0 <= row <= 7 and 0 <= col <= 7] 
        # the cells must be enemy pieces or empty squares
        adjacent_cells = [(row, col) for row, col in adjacent_cells if self.board[row][col] == ' ' or \
                            self.board[row][col].islower() and turn == 1 or self.board[row][col].isupper() and turn == 2]
        # checks if all adjacent cells are under attack
        all_adjacent_cells_are_under_attack = True
        for cell in adjacent_cells:
            if not self._is_king_in_check(cell[0], cell[1]):
                all_adjacent_cells_are_under_attack = False
                break    
        # checks if it is stalemate or checkmate
        if all_adjacent_cells_are_under_attack:
            if self._is_king_in_check(king_row, king_col) and self._any_allied_piece_can_shield_the_king(king_row, king_col) or \
              self._is_king_in_double_check(king_row, king_col):  
                print('Checkmate!')
                return True   
            elif not self._is_king_in_check(king_row, king_col) and self._is_allied_pieces_frozen(only_king_left, king_row, king_col): 
                print('Stalemate!')
                return True
        return False    
        
    def is_legal_move(self, rules, turn, piece_row, piece_col, new_row, new_col, enemy_last_move, \
                      is_king_already_moved, is_rook_left_already_moved, is_rook_right_already_moved):
        piece = self.board[piece_row][piece_col]
        end_square = self.board[new_row][new_col]
        # checks if the new square is not occupied by allied pieces
        if turn == 1 and end_square.isupper() or turn == 2 and end_square.islower():
            return False
        # checks if the king is unattacked next
        if self._is_king_in_check(new_row, new_col):
            return False
        # checks that if the piece is not a horse, then the path to the new position must be clear
        if piece.upper() != 'H' and self._is_path_dirty(piece_row, piece_col, new_row, new_col):
            return False
        # checks that if the piece is a pawn and the move is a capture on the go, then the last opponent move must be a double pawn move  
        is_move_capture_on_the_go = piece.upper() == 'P' and piece_col != new_col and end_square == ' '
        if is_move_capture_on_the_go:
            if enemy_last_move:
                last_enemy_piece_row, last_enemy_piece_col, last_enemy_new_row, last_enemy_new_col = enemy_last_move
                enemy_move_direction = -1 if piece.islower() else 1
                if not rules.is_double_pawn_move(enemy_move_direction, last_enemy_piece_row, last_enemy_piece_col, last_enemy_new_row, last_enemy_new_col):
                    return False
            return False
        # checks that if it is a castling move, then:
        if self._is_castling_move(piece_row, piece_col, new_col):
            # the king must be in the initial position
            if piece_col != 4 or turn == 1 and piece_row != 7 or turn == 2 and piece_row != 0:
                return False
            # the king must not be in check
            # the king and the rook must not have been moved before
            # the king must not pass through a square that is attacked by an enemy piece
            # there must be no pieces between the king and the rook
            rook_row = piece_row
            if new_col == 2:
                rook_col = 0
                is_rook_already_moved = is_rook_left_already_moved
            else:
                rook_col = 7
                is_rook_already_moved = is_rook_right_already_moved
            if self._is_king_in_check(piece_row, piece_col) or \
               is_king_already_moved or is_rook_already_moved or \
               self._is_castling_path_insecure(piece_row, piece_col, rook_row, rook_col) or \
               self._is_path_dirty(piece_row, piece_col, rook_row, rook_col):
                return False
        return True
    
    # helper methods

    def _is_castling_move(self, piece_row, piece_col, new_col):
        # checks if it is a king double move
        return (self.board[piece_row][piece_col]).lower() == 'k' and abs(piece_col - new_col) == 2

    def _is_castling_path_insecure(self, piece_row, piece_col, new_row, new_col):
        # checks if the cells of the king path is attacked by an enemy piece
        pass

    def _is_path_dirty(self, piece_row, piece_col, new_row, new_col):
        # checks if there are pieces in the cells of the piece path
        pass

    def _is_king_in_check(self, king_row, king_col):
        # checks if the king is attacked by an enemy piece
        pass

    def _is_king_in_double_check(self, king_row, king_col):
        # checks if the king is attacked by two enemy pieces
        pass

    def _is_allied_pieces_frozen(self, only_king_left, king_row, king_col):
        # only the king left OR
        # remaining pieces are shield OR 
        # there are only pawns and are all stucked
        pass

    def _any_allied_piece_can_shield_the_king(self, king_row, king_col):
        # checks if there is an allied piece that can move to a cell that intercepts the king attack
        pass


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
    
    def is_double_pawn_move(self, move_direction, piece_row, piece_col, new_row, new_col):
        return new_row - piece_row == 2 * move_direction and piece_col == new_col and \
            piece_row == (7 + move_direction) % 7
    
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
            self.is_double_pawn_move(move_direction, piece_row, piece_col, new_row, new_col)       

    def _is_simple_pawn_move(self, move_direction, piece_row, piece_col, new_row, new_col):
        # checks if it is a walk move or a capture move
        return new_row - piece_row == move_direction and abs(piece_col - new_col) <= 1    


class Gameplay:
    def __init__(self):
        self.rules = Rules()
        self.board = Board()
        self.turn = 1 # white turn
        self.last_move = None
        self.is_white_king_already_moved = self.is_black_king_already_moved = \
        self.is_white_left_rook_already_moved = self.is_white_right_rook_already_moved = \
        self.is_black_left_rook_already_moved = self.is_black_right_rook_already_moved = False

    def play(self):
        self.board.display()
        while not self.board.is_game_over(self.turn):
            try:
                piece_row = int(input('Piece row: ')) - 1
                piece_col = int(input('Piece column: ')) - 1
                new_row = int(input('Piece new row: ')) - 1
                new_col = int(input('Piece new column: ')) - 1
            except ValueError:
                print('Invalid input format: not a number')
                continue
            if self._is_valid_input(piece_row, piece_col, new_row, new_col):
                piece = self.board.board[piece_row][piece_col]
                if piece != ' ' and self._is_player_piece(piece):
                    if self.rules.is_piece_move(piece, piece_row, piece_col, new_row, new_col):
                        # get king and rook stats
                        if self.turn == 1:
                            is_king_already_moved = self.is_white_king_already_moved
                            is_rook_left_already_moved = self.is_white_left_rook_already_moved
                            is_rook_right_already_moved = self.is_white_right_rook_already_moved
                        else:
                            is_king_already_moved = self.is_black_king_already_moved
                            is_rook_left_already_moved = self.is_black_left_rook_already_moved
                            is_rook_right_already_moved = self.is_black_right_rook_already_moved
                        # checks if it is a legal move
                        if self.board.is_legal_move(self.rules, self.turn, piece_row, piece_col, new_row, new_col, self.last_move, \
                          is_king_already_moved, is_rook_left_already_moved, is_rook_right_already_moved):
                            self.board.make_move(piece_row, piece_col, new_row, new_col) # board update
                            self.board.display() # board ui refresh
                            self.turn = (self.turn % 2) + 1 # player update
                            # king and rook stats update
                            if piece == 'K' and not self.is_white_king_already_moved:
                               self.is_white_king_already_moved = True
                            elif piece == 'k' and not self.is_black_king_already_moved:
                               self.is_black_king_already_moved = True
                            elif piece_col == 0:
                                if piece == 'R' and not self.is_white_left_rook_already_moved:
                                    self.is_white_left_rook_already_moved = True
                                elif piece == 'r' and not self.is_black_left_rook_already_moved:
                                    self.is_black_left_rook_already_moved = True
                            elif piece_col == 7:
                                if piece == 'R' and not self.is_white_right_rook_already_moved:
                                    self.is_white_right_rook_already_moved = True
                                elif piece == 'r' and not self.is_black_right_rook_already_moved:
                                    self.is_black_right_rook_already_moved = True  
                            # last move update   
                            self.last_move = (piece_row, piece_col, new_row, new_col)
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
    
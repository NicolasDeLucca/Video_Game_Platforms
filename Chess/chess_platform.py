# Chess Platform development in Python

class Board:
    def __init__(self):
          # black
        self.board = [
            # 0    1    2    3    4    5    6    7 
            ['r', 'h', 'b', 'q', 'k', 'b', 'h', 'r'], # 0
            ['p', 'p', 'p', 'p', 'p', 'p', 'p', 'p'], # 1
            ['#', '#', '#', '#', '#', '#', '#', '#'], # 2
            ['#', '#', '#', '#', '#', '#', '#', '#'], # 3
            ['#', '#', '#', '#', '#', '#', '#', '#'], # 4
            ['#', '#', '#', '#', '#', '#', '#', '#'], # 5
            ['P', 'P', 'P', 'P', 'P', 'P', 'P', 'P'], # 6
            ['R', 'H', 'B', 'Q', 'K', 'B', 'H', 'R']  # 7
        ] # white 

    def display(self):
        print('\nblack')
        for row in self.board:
            print(' '.join(row))
        print('white')	

    def make_move(self, piece_row, piece_col, new_row, new_col, promotion_piece):
        piece = self.board[piece_row][piece_col]
        if promotion_piece:
            piece = promotion_piece
        self.board[piece_row][piece_col] = '#'
        self.board[new_row][new_col] = piece # also we are deleting the enemy piece if it is a capture move
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
            self.board[rook_row][rook_col] = '#'        

    def is_game_over(self, turn, rules, enemy_last_move):
        king_piece = 'K' if turn == 1 else 'k'
        # find the king and checks if the player has other remaining pieces
        only_king_left = True
        king_row, king_col = None, None
        end_loops = False
        for row in range(len(self.board)):
            for col in range(len(self.board[row])):
                square = self.board[row][col]
                if square == king_piece:
                    king_row, king_col = row, col
                elif square != '#':
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
        adjacent_cells = [(row, col) for row, col in adjacent_cells if self.board[row][col] == '#' or \
                            self.board[row][col].islower() and turn == 1 or self.board[row][col].isupper() and turn == 2]
        # checks if all adjacent cells are under attack
        all_adjacent_cells_are_under_attack = True
        for cell in adjacent_cells:
            if not self._is_king_in_check(turn, cell[0], cell[1], rules):
                all_adjacent_cells_are_under_attack = False
                break    
        # checks if it is stalemate or checkmate
        if all_adjacent_cells_are_under_attack:
            if self._is_king_in_check(turn, king_row, king_col, rules) and not self._an_allied_piece_can_shield_the_king(turn, king_row, king_col, rules) or \
              self._is_king_in_double_check(king_row, king_col, rules):  
                print('Checkmate!')
                return True   
            elif not self._is_king_in_check(turn, king_row, king_col, rules) and self._are_allied_pieces_frozen(turn, only_king_left, king_row, king_col, rules, enemy_last_move): 
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
        # checks if the king is unattacked next and the path to the new position is clear
        if self._is_path_dirty(piece_row, piece_col, new_row, new_col) or self._is_king_in_check(turn, new_row, new_col, rules):
            return False
        # checks that if the piece is a pawn and the move is a capture on the go, then the last opponent move must be a double pawn move  
        is_move_capture_on_the_go = piece.upper() == 'P' and piece_col != new_col and end_square == '#'
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
            if self._is_path_dirty(piece_row, piece_col, rook_row, rook_col) or \
              self._is_castling_path_insecure(turn, piece_row, piece_col, rook_col) or \
              self._is_king_in_check(turn, piece_row, piece_col, rules) or \
              is_king_already_moved or is_rook_already_moved:
                return False
        return True
    
    # helper methods

    def _is_castling_move(self, piece_row, piece_col, new_col):
        # checks if it is a king double move
        return (self.board[piece_row][piece_col]).lower() == 'k' and abs(piece_col - new_col) == 2
    
    def _is_castling_path_insecure(self, turn, row, col, new_col):
        # checks if the cells of the king path is attacked by an enemy piece
        start_col, end_col = (col, new_col) if new_col < col else (new_col, col)
        path_cells = [
            (row, col) 
            for col in range(start_col + 1, end_col)
        ]
        return any(
            self._is_cell_under_attack(turn, king_row, king_col) 
            for king_row, king_col in path_cells
        )
      
    def _is_king_in_check(self, turn, king_row, king_col, rules):
        # checks if the king is attacked by an enemy piece
        return self._is_cell_under_attack(turn, king_row, king_col, rules)

    def _is_cell_under_attack(self, turn, row, col, rules):
        # checks if a specific cell is under attack by an enemy piece
        enemy_turn = 1 if turn == 2 else 2  
        return any(
            rules.is_piece_move(self.board[i][j], i, j, row, col) and turn == enemy_turn
            for i in range(8)
                for j in range(8)
                    if self.board[i][j] != '#'
        )

    def _is_king_in_double_check(self, king_row, king_col, rules):
        king = self.board[king_row][king_col]
        turn = 1 if king.isupper() else 2 # white is 1
        # checks if the king is attacked by one enemy piece
        if self._is_king_in_check(turn, king_row, king_col, rules):
            # iterates over all enemy pieces to check for a second attack
            for row in range(8):
                for col in range(8):
                    if square != '#' and (row, col) != (king_row, king_col):
                        square = self.board[row][col]
                        enemy_turn = 1 if square.islower() else 2
                        if turn != enemy_turn and self.rules.is_piece_move(square, row, col, king_row, king_col):
                            return True
        return False
    
    def _is_path_dirty(self, piece_row, piece_col, new_row, new_col):
        # checks if there are pieces in the cells of the piece path
        upper_piece = self.board[piece_row][piece_col].upper()
        if upper_piece == 'R':
             rook_path = self._get_rook_path(piece_row, piece_col, new_row, new_col)
             return any(
                self.board[rook_row][rook_col] != '#'
                for rook_row, rook_col in rook_path
             )
        elif upper_piece == 'B':
            return self._is_bishop_path_dirty(piece_row, piece_col, new_row, new_col)
        elif upper_piece == 'Q':
            rook_path = self._get_rook_path(piece_row, piece_col, new_row, new_col)
            return any(
                self.board[rook_row][rook_col] != '#'
                for rook_row, rook_col in rook_path
            ) or self._is_bishop_path_dirty(piece_row, piece_col, new_row, new_col)
        return False
    
    def _is_bishop_path_dirty(self, row, col, new_row, new_col):
        # checks if there are pieces in the cells of the bishop path
        row_direction = 1 if new_row > row else -1
        col_direction = 1 if new_col > col else -1
        current_row, current_col = row + row_direction, col + col_direction
        while (current_row, current_col) != (new_row, new_col):
            if self.board[current_row][current_col] != '#':
                return True
            current_row += row_direction
            current_col += col_direction
        return False

    def _are_allied_pieces_frozen(self, turn, only_king_left, king_row, king_col, rules, enemy_last_move):
        if only_king_left:
            return True
        # checks if there are no more than remaining pieces that are a shield to the king, or pawns locked
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '#':
                    if turn == 1 and piece.isupper() or turn == 2 and piece.islower():
                        if not self._is_piece_a_king_shield(turn, row, col, king_row, king_col, rules) or \
                           not piece.upper() == 'P' or not self._is_pawn_locked(row, col, rules, enemy_last_move):
                                return False
        return True
    
    def _is_piece_a_king_shield(self, turn, row, col, king_row, king_col, rules):
        # checks if a piece is protecting the king from an enemy piece 
        piece = self.board[row][col]
        self.board[row][col] = '#'
        is_piece_a_king_shield = self._is_king_in_check(turn, king_row, king_col, rules)
        self.board[row][col] = piece
        return is_piece_a_king_shield 

    def _is_pawn_locked(self, pawn_row, pawn_col, rules, enemy_last_move):
        # checks if the pawn is locked in the board
        move_direction = -1 if self.board[pawn_row][pawn_col].isupper() else 1
        last_enemy_move_was_a_double_pawn_move = rules.is_double_pawn_move(move_direction, *enemy_last_move) # enemy_last_move is not None
        next_row = pawn_row + move_direction
        if 0 <= next_row < 8:
            if self.board[next_row][pawn_col] == '#': # next step available
                return False
            left_diagonal_col = pawn_col - 1 # left diagonal
            if 0 <= left_diagonal_col < 8:
                square_to_move = self.board[next_row][left_diagonal_col]
                # checks if the pawn can capture an enemy pawn as en passant
                is_en_passant_available = last_enemy_move_was_a_double_pawn_move and \
                  self._is_en_passant_available(enemy_last_move[2], pawn_row, enemy_last_move[3], left_diagonal_col)
                if self._is_available_square_to_eat(move_direction, square_to_move) or is_en_passant_available:
                    return False
            right_diagonal_col = pawn_col + 1 # right diagonal    
            if 0 <= right_diagonal_col < 8:
                square_to_move = self.board[next_row][right_diagonal_col]
                is_en_passant_available = last_enemy_move_was_a_double_pawn_move and \
                  self._is_en_passant_available(enemy_last_move[2], pawn_row, enemy_last_move[3], right_diagonal_col)
                if self._is_available_square_to_eat(move_direction, square_to_move) or is_en_passant_available:
                    return False
        return True
    
    def _is_available_square_to_eat(self, move_direction, square_to_eat):
        return square_to_eat == '#' or (square_to_eat.isupper() if move_direction == 1 else square_to_eat.islower())
    
    # pre: enemy last move was a double pawn move
    def _is_en_passant_available(self, last_enemy_pawn_row, pawn_row, last_enemy_pawn_col, diagonal_col):
        # checks if the pawn can capture an enemy pawn as en passant
        return last_enemy_pawn_row == pawn_row and last_enemy_pawn_col == diagonal_col       

    def _an_allied_piece_can_shield_the_king(self, turn, king_row, king_col, rules):
        attacker_piece = self._get_attacker_piece(turn, king_row, king_col)
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '#':
                    if turn == 1 and piece.isupper() or turn == 2 and piece.islower():
                        attacker_path = self._get_attacker_path(row, col, king_row, king_col, attacker_piece)
                        if self._piece_can_intercept_the_attack(row, col, king_row, king_col, rules, attacker_path):
                            return True
        return False

    # pre: the king is under attack
    def _get_attacker_piece(self, turn, king_row, king_col):
        # identifies the first piece that is attacking the king
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != '#':
                    if turn == 1 and piece.islower() or turn == 2 and piece.isupper():
                        if self.rules.is_piece_move(piece, row, col, king_row, king_col) and \
                           not self._is_path_dirty(row, col, king_row, king_col):
                              return piece     
    
    def _get_attacker_path(self, piece_row, piece_col, king_row, king_col, attacker_piece):
        upper_attacker_piece = attacker_piece.upper()
        if upper_attacker_piece == 'B':
            return self._get_bishop_path(piece_row, piece_col, king_row, king_col)
        elif upper_attacker_piece == 'R':
            return self._get_rook_path(piece_row, piece_col, king_row, king_col)
        elif upper_attacker_piece == 'Q':
            return self._get_bishop_path(piece_row, piece_col, king_row, king_col) or \
                self._get_rook_path(piece_row, piece_col, king_row, king_col)
        return []
    
    def _piece_can_intercept_the_attack(self, piece_row, piece_col, rules, attacker_path):
        piece = self.board[piece_row][piece_col] 
        for row, col in attacker_path: 
            if piece != '#' and rules.is_piece_move(piece, piece_row, piece_col, row, col) and \
                not self._is_path_dirty(piece_row, piece_col, row, col):
                return True
        return False
    
    def _get_rook_path(self, row, col, new_row, new_col):
        path = []
        start_row, end_row = (row, new_row) if new_row < row else (new_row, row)
        if start_row == end_row: # horizontal move
            start_col, end_col = (col, new_col) if new_col < col else (new_col, col)
            path = [
                (row, col) 
                for col in range(start_col + 1, end_col)
            ]
        else: # vertical move
            path = [
                (row, col) 
                for row in range(start_row + 1, end_row)
            ]
        return path

    def _get_bishop_path(self, row, col, king_row, king_col):
        bishop_path = []
        row_direction = 1 if king_row > row else -1
        col_direction = 1 if king_col > col else -1
        current_row, current_col = row + row_direction, col + col_direction
        while (current_row, current_col) != (king_row, king_col):
            bishop_path.append((current_row, current_col))
            current_row += row_direction
            current_col += col_direction
        return bishop_path


class Rules:
    def is_piece_move(self, piece, piece_row, piece_col, new_row, new_col):
        # rememeber pieces basic rules
        upper_piece = piece.upper()
        if upper_piece == 'P': # pawn   
            return self._is_pawn_move(piece, piece_row, piece_col, new_row, new_col)
        elif upper_piece == 'R': # rook
            return self._is_rook_move(piece_row, piece_col, new_row, new_col)
        elif upper_piece == 'H': # horse
            return self._is_knight_move(piece_row, piece_col, new_row, new_col)
        elif upper_piece == 'B': # bishop
            return self._is_bishop_move(piece_row, piece_col, new_row, new_col)
        elif upper_piece == 'Q': # queen
            return self._is_rook_move(piece_row, piece_col, new_row, new_col) or \
            self._is_bishop_move(piece_row, piece_col, new_row, new_col)
        elif upper_piece == 'K': # king
            return self._is_king_move(piece, piece_row, piece_col, new_row, new_col)
    
    def is_double_pawn_move(self, move_direction, piece_row, piece_col, new_row, new_col):
        return new_row - piece_row == 2 * move_direction and piece_col == new_col and \
            piece_row == (7 + move_direction) % 7
    
    # helper methods

    def _is_rook_move(self, piece_row, piece_col, new_row, new_col, steps=7):
        return piece_row == new_row and piece_col != new_col and abs(piece_col - new_col) <= steps or \
            piece_col == new_col and piece_row != new_row and abs(piece_row - new_row) <= steps

    def _is_knight_move(self, piece_row, piece_col, new_row, new_col):
        # checks if it is a L move
        return abs(piece_row - new_row) == 2 and abs(piece_col - new_col) == 1 or \
            abs(piece_row - new_row) == 1 and abs(piece_col - new_col) == 2

    def _is_bishop_move(self, piece_row, piece_col, new_row, new_col, steps=7):
        return piece_row != new_row and abs(piece_row - new_row) <= steps and \
            abs(piece_row - new_row) == abs(piece_col - new_col)

    def _is_king_move(self, piece, piece_row, piece_col, new_row, new_col):
        steps = 1
        king_initial_row = 7 if piece.isupper() else 0 
        return self._is_rook_move(piece_row, piece_col, new_row, new_col, steps) or \
            self._is_bishop_move(piece_row, piece_col, new_row, new_col, steps) or \
            piece_row == new_row == king_initial_row and abs(piece_col - new_col) == 2 # castling move

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
        self.chess_board = Board()
        self.turn = 1 # white turn
        self.last_move = None
        self.is_white_king_already_moved = self.is_black_king_already_moved = \
        self.is_white_left_rook_already_moved = self.is_white_right_rook_already_moved = \
        self.is_black_left_rook_already_moved = self.is_black_right_rook_already_moved = False

    def play(self):
        while not self.chess_board.is_game_over(self.turn, self.rules, self.last_move):
            king_position = self.get_king_position_in_board()
            if self.chess_board.is_king_in_check(self.turn, *king_position, self.rules):
                print('Check!')
            try:
                self.chess_board.display() # board ui refresh
                piece_row = int(input('\nPiece row: ')) - 1
                piece_col = int(input('Piece column: ')) - 1
                new_row = int(input('Piece new row: ')) - 1
                new_col = int(input('Piece new column: ')) - 1
            except ValueError:
                print('Invalid input format: not a number')
                continue
            promotion_piece = None
            # checks if it is a pawn promotion move
            if self._is_valid_input(piece_row, piece_col, new_row, new_col):
                piece = self.chess_board.board[piece_row][piece_col]             
                if piece.upper() == 'P' and (new_row == 0 or new_row == 7):
                    while True:
                        promotion_piece = input('Enter promotion piece (Q, R, B, or H): ')
                        if promotion_piece in ['Q', 'R', 'B', 'H']:
                            break
                        else:
                            print('Invalid promotion piece. Please enter Q, R, B, or H.')
                if piece != '#' and self._is_player_piece(piece):
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
                        if self.chess_board.is_legal_move(self.rules, self.turn, piece_row, piece_col, new_row, new_col, self.last_move, \
                          is_king_already_moved, is_rook_left_already_moved, is_rook_right_already_moved):
                            self.chess_board.make_move(piece_row, piece_col, new_row, new_col, promotion_piece) # board update
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

    def get_king_position_in_board(self):
        board = self.chess_board.board
        king_piece = 'K' if self.turn == 1 else 'k'
        for row in range(len(board)):
            for col in range(len(board[row])):
                if board[row][col] == king_piece:
                    return (row, col)

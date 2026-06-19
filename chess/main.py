from abc import ABC, abstractmethod
from uuid import uuid4
from enum import Enum
from __future__ import annotations

class Color(Enum):
    WHITE = "White"
    BLACK = "Black"

class Piece(ABC):
    
    def __init__(self, color:Color):
        self.color = color
        self.has_moved = False

    @abstractmethod
    def is_valid_move(self, board:Board, source:Position, destination:Position):
        pass

    def check_out_of_range(self, row:int, col:int):
        if row>7 or row<0 or col>7 or col<0:
            return True
        return False

class King(Piece):
    def __init__(self, color):
        super().__init__(color)
    
    def is_valid_move(self, board:Board, source:Position, destination:Position) -> bool:
        target = board.get_piece(destination)
        if target and target.color == self.color:
            return False

        if self.check_out_of_range(destination.row, destination.col):
            return False
        valid_moves = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]
        
        for move in valid_moves:
            n_r = source.row + move[0]
            n_c = source.col + move[1]
            if not self.check_out_of_range(n_r, n_c):
                if (n_r == destination.row and n_c == destination.col):
                    return True
        return False   

class Queen(Piece):
    def __init__(self, color):
        super().__init__(color)
    
    def is_valid_move(self, board:Board, source:Position, destination:Position) -> bool:
        target = board.get_piece(destination)
        if target and target.color == self.color:
            return False
        
        if self.check_out_of_range(destination.row, destination.col):
            return False
        
        row_diff = destination.row - source.row
        col_diff = destination.col - source.col

        is_straight = (source.col == destination.col) or (source.row == destination.row)
        is_diagonal = abs(row_diff) == abs(col_diff)

        if not (is_diagonal or is_straight):
            return False
        
        # check where are we moving up down wrt row and col
        row_step = 0 if row_diff == 0 else (1 if row_diff>0 else -1)
        col_step = 0 if col_diff == 0 else (1 if col_diff>0 else -1)

        if not board.is_path_clear(source, destination, row_step, col_step):
            return False
        return True

class Rook(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(self, board:Board, source:Position, destination:Position) -> bool:
        target = board.get_piece(destination)
        if target and (target.color == self.color):
            return False
        if self.check_out_of_range(destination.row, destination.col): return False

        is_straight = (source.row == destination.row) or (source.col) == (destination.col)

        if not is_straight:
            return False
        
        # check where are we moving
        row_step = 0 if source.row == destination.row else (1 if (source.row<destination.row) else -1)
        col_step = 0 if source.col == destination.col else (1 if (source.col<destination.col) else -1)

        if not board.is_path_clear(source, destination, row_step, col_step):
            return False
        return True

class Bishop(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(self, board:Board, source:Position, destination:Position) -> bool:
        return super().is_valid_move(board, source, destination)

class Knight(Piece):
    def __init__(self, color):
        super().__init__(color)
    
    def is_valid_move(self, board, source, destination):
        return super().is_valid_move(board, source, destination)

class Pawn(Piece):
    def __init__(self, color):
        super().__init__(color)

    def is_valid_move(self, board, source, destination):
        return super().is_valid_move(board, source, destination)


class Position:
    def __init__(self, row, col):
        self.row = row
        self.col = col

class Player:
    def __init__(self, name, color):
        self.color = color
        self.name = name


class Board:
    def __init__(self):
        self.board:list[list[Piece]] = [[None for _ in range(8)] for _ in range(8)]
        self.initialize_board()
    
    def is_path_clear(self, source:Position, destination:Position, row_step:int, col_step:int) -> bool:
        curr_row = source.row + row_step
        curr_col = source.col + col_step

        while curr_row!=destination.row or curr_col!=destination.col:
            if self.get_piece(Position(curr_row, curr_col)) is not None:
                return False
            curr_row += row_step
            curr_col += col_step
        return True

    def get_piece(self, pos:Position):
        return self.board[pos.row][pos.col]
    
    def set_piece(self, dst:Position, piece:Piece):
        self.board[dst.row][dst.col] = piece
    
    def initialize_board(self):
        for c in range(8):
            self.board[1][c] = Pawn(Color.BLACK)
            self.board[6][c] = Pawn(Color.WHITE)
        
        # set rook
        self.board[0][0] = Rook(Color.BLACK)
        self.board[0][7] = Rook(Color.BLACK)
        self.board[7][0] = Rook(Color.WHITE)
        self.board[7][7] = Rook(Color.WHITE)

        # set knights
        self.board[0][1] = Knight(Color.BLACK)
        self.board[0][6] = Knight(Color.BLACK)
        self.board[7][1] = Knight(Color.WHITE)
        self.board[7][6] = Knight(Color.WHITE)

        # set bishops
        self.board[0][2] = Bishop(Color.BLACK)
        self.board[0][5] = Bishop(Color.BLACK)
        self.board[7][2] = Bishop(Color.WHITE)
        self.board[7][5] = Bishop(Color.WHITE)

        # set queen
        self.board[0][3] = Queen(Color.BLACK)
        self.board[7][3] = Queen(Color.WHITE)

        # set king
        self.board[0][4] = King(Color.BLACK)
        self.board[7][4] = King(Color.WHITE)

class Game:
    
    def __init__(self, player1:Player, player2:Player):
        self.board = Board()
        self.players= [player1, player2]
        self.curr_turn = player1
        self.game_status  =  None

    def make_move(self, src:Position, dst:Position):
        if src.row == dst.row and src.col == dst.col:
            raise ValueError("Source and destination cannot be same")
        
        piece = self.board.get_piece(src)
        if piece is None:
            raise ValueError("Select a valid piece.")
        
        # check color
        if piece.color != self.curr_turn.color:
            raise ValueError("Its not your turn.")
        
        if not piece.is_valid_move(self.board, src, dst):
            raise ValueError("Invalid move")
        
        self.board.set_piece(dst, piece)
        piece.has_moved = True
        self.board.set_piece(src, None)

        self.curr_turn = self.players[1] if self.curr_turn == self.players[0] else self.players[0]

        
        






# This Python program implements a simplified Checkers game agent using Minimax with alpha-beta pruning.
# It allows two AI agents (one representing "white" and the other "black") to play against each other on an 8x8 board.
# The program follows the basic rules of Checkers, including piece movement, capturing, and promotion to "king" status.
# The game will run until one player has no pieces left or no available moves.
#
# Usage:
# - Run the program to see the game play out between two AI players.
# - The game displays the board after each move, with "=" separators for clarity.
# - At the end of the game, the winner is announced, either because one player has captured all pieces or no moves are available.

import copy
import random

# Constants
WHITE = "white"
BLACK = "black"
EMPTY = None
ROWS, COLS = 8, 8


class Piece:
    """A class representing a checkers piece, including king status."""
    def __init__(self, color, king=False):
        self.color = color
        self.king = king

    def make_king(self):
        """Promotes the piece to a king."""
        self.king = True

    def __repr__(self):
        return "K" if self.king else self.color[0].upper()


class Board:
    """A class to represent and manage the checkers game board."""
    def __init__(self):
        self.board = self.create_board()
        self.white_left = self.black_left = 12
        self.white_kings = self.black_kings = 0

    def create_board(self):
        """Sets up the initial board."""
        board = [[EMPTY] * COLS for _ in range(ROWS)]
        for row in range(3):
            for col in range(row % 2, COLS, 2):
                board[row][col] = Piece(BLACK)
        for row in range(5, ROWS):
            for col in range(row % 2, COLS, 2):
                board[row][col] = Piece(WHITE)
        return board

    def move_piece(self, piece, start, end):
        """Moves a piece and handles king promotion."""
        start_row, start_col = start
        end_row, end_col = end
        self.board[start_row][start_col] = EMPTY
        self.board[end_row][end_col] = piece

        if end_row == ROWS - 1 and piece.color == WHITE:
            piece.make_king()
            self.white_kings += 1
        elif end_row == 0 and piece.color == BLACK:
            piece.make_king()
            self.black_kings += 1

    def remove_piece(self, pieces):
        """Removes captured pieces."""
        for piece in pieces:
            row, col = piece
            removed_piece = self.board[row][col]
            if removed_piece:
                if removed_piece.color == WHITE:
                    self.white_left -= 1
                    if removed_piece.king:
                        self.white_kings -= 1
                else:
                    self.black_left -= 1
                    if removed_piece.king:
                        self.black_kings -= 1
                self.board[row][col] = EMPTY

    def get_piece(self, row, col):
        """Returns the piece at a given location."""
        return self.board[row][col]

    def get_all_pieces(self, color):
        """Returns all pieces of a specific color."""
        pieces = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    pieces.append((piece, row, col))
        return pieces

    def get_valid_moves(self, piece, row, col):
        """Returns valid moves for a piece."""
        moves = {}
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse(row, col, -1, -1, piece.color, [], 1))
            moves.update(self._traverse(row, col, -1, 1, piece.color, [], 1))
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse(row, col, 1, -1, piece.color, [], 1))
            moves.update(self._traverse(row, col, 1, 1, piece.color, [], 1))
        return moves

    def _traverse(self, start_row, start_col, row_inc, col_inc, color, skipped, depth):
        """Helper function to explore moves in a specific direction."""
        moves = {}
        row, col = start_row + row_inc, start_col + col_inc
        if 0 <= row < ROWS and 0 <= col < COLS:
            next_piece = self.get_piece(row, col)
            if next_piece == EMPTY:
                moves[(row, col)] = skipped
            elif next_piece.color != color:
                new_row, new_col = row + row_inc, col + col_inc
                if 0 <= new_row < ROWS and 0 <= new_col < COLS and self.get_piece(new_row, new_col) == EMPTY:
                    moves[(new_row, new_col)] = skipped + [(row, col)]
        return moves

    def evaluate(self):
        """Uses an enhanced heuristic to evaluate the board state."""
        return enhanced_heuristic(self)

    def is_terminal(self):
        """Checks if the game has ended."""
        return self.white_left == 0 or self.black_left == 0

    def clone(self):
        """Creates a deep copy of the board."""
        return copy.deepcopy(self)


def enhanced_heuristic(board):
    """Enhanced heuristic evaluation function."""
    white_score = 0
    black_score = 0

    for row in range(ROWS):
        for col in range(COLS):
            piece = board.get_piece(row, col)
            if piece:
                base_score = 3 if piece.king else 1
                position_score = 0.5 if 2 <= row <= 5 and 2 <= col <= 5 else 0
                total_score = base_score + position_score
                if piece.color == WHITE:
                    white_score += total_score
                else:
                    black_score += total_score

    return white_score - black_score


def minimax(board, depth, alpha, beta, maximizing_player):
    """Implements the minimax algorithm with alpha-beta pruning."""
    if depth == 0 or board.is_terminal():
        return board.evaluate(), None

    best_move = None
    if maximizing_player:
        max_eval = float('-inf')
        for piece, row, col in board.get_all_pieces(WHITE):
            moves = board.get_valid_moves(piece, row, col)
            for move, skipped in moves.items():
                new_board = board.clone()
                new_board.move_piece(piece, (row, col), move)
                new_board.remove_piece(skipped)
                evaluation, _ = minimax(new_board, depth - 1, alpha, beta, False)
                if evaluation > max_eval:
                    max_eval = evaluation
                    best_move = (piece, (row, col), move)
                alpha = max(alpha, evaluation)
                if beta <= alpha:
                    break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for piece, row, col in board.get_all_pieces(BLACK):
            moves = board.get_valid_moves(piece, row, col)
            for move, skipped in moves.items():
                new_board = board.clone()
                new_board.move_piece(piece, (row, col), move)
                new_board.remove_piece(skipped)
                evaluation, _ = minimax(new_board, depth - 1, alpha, beta, True)
                if evaluation < min_eval:
                    min_eval = evaluation
                    best_move = (piece, (row, col), move)
                beta = min(beta, evaluation)
                if beta <= alpha:
                    break
        return min_eval, best_move


def display_board(board):
    """Displays the game board."""
    print("=" * 20)
    for row in board.board:
        print(" ".join([str(piece) if piece else "." for piece in row]))
    print("=" * 20)
    print()


def play_ai_vs_ai(board):
    """Plays a game between two AI agents."""
    player_turn = WHITE
    depth = 3
    while not board.is_terminal():
        display_board(board)
        _, best_move = minimax(board, depth, float('-inf'), float('inf'), player_turn == WHITE)
        if best_move:
            piece, start, end = best_move
            skipped = board.get_valid_moves(piece, *start)[end]
            board.move_piece(piece, start, end)
            board.remove_piece(skipped)
        player_turn = BLACK if player_turn == WHITE else WHITE
    print("Game Over! Winner:", "WHITE" if board.white_left > board.black_left else "BLACK")


def play_human_vs_ai(board):
    """Allows a human player to play against an AI agent."""
    player_turn = WHITE
    depth = 3
    while not board.is_terminal():
        display_board(board)
        if player_turn == WHITE:
            # Human's turn
            print("Your turn (WHITE).")
            try:
                row, col = map(int, input("Enter row and col of piece to move (e.g., 5 0): ").split())
                piece = board.get_piece(row, col)
                if piece and piece.color == WHITE:
                    moves = board.get_valid_moves(piece, row, col)
                    print("Valid moves:", moves)
                    end_row, end_col = map(int, input("Enter row and col to move to: ").split())
                    if (end_row, end_col) in moves:
                        skipped = moves[(end_row, end_col)]
                        board.move_piece(piece, (row, col), (end_row, end_col))
                        board.remove_piece(skipped)
                    else:
                        print("Invalid move. Try again.")
                        continue
                else:
                    print("Invalid piece. Try again.")
                    continue
            except ValueError:
                print("Invalid input. Try again.")
                continue
        else:
            # AI's turn
            _, best_move = minimax(board, depth, float('-inf'), float('inf'), False)
            if best_move:
                piece, start, end = best_move
                skipped = board.get_valid_moves(piece, *start)[end]
                board.move_piece(piece, start, end)
                board.remove_piece(skipped)
                print("AI moves from", start, "to", end)

        player_turn = BLACK if player_turn == WHITE else WHITE
    print("Game Over! Winner:", "WHITE" if board.white_left > board.black_left else "BLACK")


def play_human_vs_human(board):
    """Allows two human players to play against each other."""
    player_turn = WHITE
    while not board.is_terminal():
        display_board(board)
        print("Player turn:", "WHITE" if player_turn == WHITE else "BLACK")
        try:
            row, col = map(int, input("Enter row and col of piece to move: ").split())
            piece = board.get_piece(row, col)
            if piece and piece.color == player_turn:
                moves = board.get_valid_moves(piece, row, col)
                print("Valid moves:", moves)
                end_row, end_col = map(int, input("Enter row and col to move to: ").split())
                if (end_row, end_col) in moves:
                    skipped = moves[(end_row, end_col)]
                    board.move_piece(piece, (row, col), (end_row, end_col))
                    board.remove_piece(skipped)
                else:
                    print("Invalid move. Try again.")
                    continue
            else:
                print("Invalid piece. Try again.")
                continue
        except ValueError:
            print("Invalid input. Try again.")
            continue
        player_turn = BLACK if player_turn == WHITE else WHITE
    print("Game Over! Winner:", "WHITE" if board.white_left > board.black_left else "BLACK")


def main():
    """Main game loop."""
    print("Choose game mode:")
    print("1. AI vs AI")
    print("2. Human vs AI")
    print("3. Human vs Human")
    mode = int(input("Enter choice (1/2/3): "))

    board = Board()
    print("Initial Board:")
    display_board(board)

    if mode == 1:
        play_ai_vs_ai(board)
    elif mode == 2:
        play_human_vs_ai(board)
    elif mode == 3:
        play_human_vs_human(board)
    else:
        print("Invalid choice. Exiting.")


if __name__ == "__main__":
    main()

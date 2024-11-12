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

# Constants for game settings; not needed but helps for clarity
WHITE = "white"
BLACK = "black"
EMPTY = None
ROWS, COLS = 8, 8


# Piece class to define a checker piece, including king functionality
class Piece:
    """
    A class representing a checkers piece, which includes its color (WHITE or BLACK) and king status.
    """

    def __init__(self, color, king=False):
        """
        Initializes a Piece object with a specified color and an optional king status.

        Parameters:
        color (str): The color of the piece (WHITE or BLACK).
        king (bool): Whether the piece is a king or not (default is False).
        """
        self.color = color
        self.king = king

    def make_king(self):
        """
        Promotes the piece to a king, granting it additional movement capabilities.
        """
        self.king = True

    def __repr__(self):
        """
        Returns a string representation of the piece for display on the board.

        Returns:
        str: 'K' if the piece is a king, otherwise the first letter of the color.
        """
        return "K" if self.king else self.color[0].upper()


# Board class to manage the game board and basic rules
class Board:
    """
    A class to represent and manage the checkers game board, including piece movement, captures, and valid moves.
    """

    def __init__(self):
        """
        Initializes the Board object, setting up the board with pieces and tracking the number of pieces for each player.
        """
        self.board = self.create_board()
        self.white_left = self.black_left = 12  # Total pieces per player
        self.white_kings = self.black_kings = 0  # Total kings per player

    def create_board(self):
        """
        Creates the initial setup of the checkers board, with white and black pieces in their starting positions.

        Returns:
        list: A 2D list representing the board with pieces in their initial positions.
        """
        board = [[EMPTY] * COLS for _ in range(ROWS)]
        for row in range(3):
            for col in range(row % 2, COLS, 2):
                board[row][col] = Piece(BLACK)
        for row in range(5, ROWS):
            for col in range(row % 2, COLS, 2):
                board[row][col] = Piece(WHITE)
        return board

    def move_piece(self, piece, start, end):
        """
        Moves a piece from a start position to an end position on the board, handling any king promotion if necessary.

        Parameters:
        piece (Piece): The piece being moved.
        start (tuple): The (row, col) starting position of the piece.
        end (tuple): The (row, col) destination position for the piece.
        """
        start_row, start_col = start
        end_row, end_col = end
        self.board[start_row][start_col] = EMPTY
        self.board[end_row][end_col] = piece

        # Promote to king if reaching the opposite end
        if end_row == ROWS - 1 and piece.color == WHITE:
            piece.make_king()
            self.white_kings += 1
        elif end_row == 0 and piece.color == BLACK:
            piece.make_king()
            self.black_kings += 1

    def remove_piece(self, pieces):
        """
        Removes captured pieces from the board and updates the count of remaining pieces.

        Parameters:
        pieces (list): A list of (row, col) tuples representing the positions of captured pieces.
        """
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
        """
        Returns the piece at a specific location on the board.

        Parameters:
        row (int): The row of the piece's location.
        col (int): The column of the piece's location.

        Returns:
        Piece or None: The piece at the specified location or None if the cell is empty.
        """
        return self.board[row][col]

    def get_all_pieces(self, color):
        """
        Retrieves all pieces of a specific color from the board.

        Parameters:
        color (str): The color of the pieces to retrieve (WHITE or BLACK).

        Returns:
        list: A list of (Piece, row, col) tuples for each piece of the specified color.
        """
        pieces = []
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.get_piece(row, col)
                if piece and piece.color == color:
                    pieces.append((piece, row, col))
        return pieces

    def get_valid_moves(self, piece, row, col):
        """
        Determines valid moves for a given piece, including both standard moves and captures.

        Parameters:
        piece (Piece): The piece to find moves for.
        row (int): The current row of the piece.
        col (int): The current column of the piece.

        Returns:
        dict: A dictionary where keys are destination positions and values are lists of captured pieces.
        """
        moves = {}
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse(row, col, -1, -1, piece.color, [], 1))
            moves.update(self._traverse(row, col, -1, 1, piece.color, [], 1))
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse(row, col, 1, -1, piece.color, [], 1))
            moves.update(self._traverse(row, col, 1, 1, piece.color, [], 1))
        return moves

    def _traverse(self, start_row, start_col, row_inc, col_inc, color, skipped, depth):
        """
        Helper function to check moves in a specific direction, including captures.

        Parameters:
        start_row (int): Starting row of the piece.
        start_col (int): Starting column of the piece.
        row_inc (int): Row increment for direction.
        col_inc (int): Column increment for direction.
        color (str): Color of the piece moving.
        skipped (list): List of captured pieces.
        depth (int): Depth of the search (only used for recursion).

        Returns:
        dict: Possible moves with positions as keys and skipped pieces as values.
        """
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
        """
        Evaluates the board state by comparing piece and king counts.

        Returns:
        float: A score representing the advantage of one player over the other.
        """
        return self.white_left - self.black_left + (self.white_kings - self.black_kings) * 0.5

    def is_terminal(self):
        """
        Checks if the game has reached a terminal state (no pieces left for one player).

        Returns:
        bool: True if the game is over, otherwise False.
        """
        return self.white_left == 0 or self.black_left == 0

    def clone(self):
        """
        Creates a deep copy of the board for use in simulations (e.g., in minimax).

        Returns:
        Board: A new Board object identical to the current one.
        """
        return copy.deepcopy(self)


# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
    """
    Implements the minimax algorithm with alpha-beta pruning for optimal move selection.

    Parameters:
    board (Board): The current game board.
    depth (int): The maximum depth of the search.
    alpha (float): Alpha value for pruning.
    beta (float): Beta value for pruning.
    maximizing_player (bool): Whether the current player is maximizing or minimizing.

    Returns:
    tuple: The best evaluation score and corresponding move.
    """
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
    """
    Displays the current state of the board with a separator line for clarity.

    Parameters:
    board (Board): The game board to be displayed.
    """
    print("=" * 20)  # Separator line
    for row in board.board:
        print(" ".join([str(piece) if piece else "." for piece in row]))
    print("=" * 20)  # Another separator line
    print()  # Blank line for better readability


def main():
    """
    Main function to execute the game loop. The game continues until one player wins by capturing all pieces or blocking the opponent.
    """
    board = Board()
    player_turn = WHITE
    depth = 3  # Depth limit for minimax

    print("Initial Board:")
    display_board(board)

    while True:
        # Check for terminal state (game over)
        if board.is_terminal():
            winner = WHITE if board.black_left == 0 else BLACK
            print(f"Game Over! {winner} wins!")
            break

        # Determine the best move for the current player
        if player_turn == WHITE:
            _, best_move = minimax(board, depth, float('-inf'), float('inf'), True)
        else:
            _, best_move = minimax(board, depth, float('-inf'), float('inf'), False)

        # If there is a valid move, execute it
        if best_move:
            piece, start, end = best_move
            skipped = board.get_valid_moves(piece, *start)[end]
            board.move_piece(piece, start, end)
            board.remove_piece(skipped)
            print(f"{player_turn.capitalize()} moves from {start} to {end}.")
            display_board(board)  # Show board after each move
        else:
            winner = BLACK if player_turn == WHITE else WHITE
            print(f"Game Over! {winner} wins due to no available moves!")
            break

        # Switch turns
        player_turn = BLACK if player_turn == WHITE else WHITE


if __name__ == "__main__":
    main()

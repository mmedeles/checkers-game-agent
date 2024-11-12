import copy

# Constants for game settings
WHITE = "white"
BLACK = "black"
EMPTY = None
ROWS, COLS = 8, 8

# Piece class to define a checker piece, including king functionality
class Piece:
    def __init__(self, color, king=False):
        self.color = color
        self.king = king

    def make_king(self):
        self.king = True

    def __repr__(self):
        return "K" if self.king else self.color[0].upper()


# Board class to manage the game board and basic rules
class Board:
    def __init__(self):
        self.board = self.create_board()
        self.white_left = self.black_left = 12  # Total pieces per player
        self.white_kings = self.black_kings = 0  # Total kings per player

    def create_board(self):
        """Sets up the initial board with pieces for both players."""
        board = [[EMPTY] * COLS for _ in range(ROWS)]
        for row in range(3):
            for col in range(row % 2, COLS, 2):
                board[row][col] = Piece(BLACK)
        for row in range(5, ROWS):
            for col in range(row % 2, COLS, 2):
                board[row][col] = Piece(WHITE)
        return board

    def move_piece(self, piece, start, end):
        """Moves a piece from start to end, handling any king promotion."""
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
        """Removes pieces from the board (used for capturing)."""
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
        """Returns the piece at a specific location."""
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
        """Returns valid moves for a piece, including captures."""
        moves = {}
        if piece.color == WHITE or piece.king:
            moves.update(self._traverse(row, col, -1, -1, piece.color, [], 1))
            moves.update(self._traverse(row, col, -1, 1, piece.color, [], 1))
        if piece.color == BLACK or piece.king:
            moves.update(self._traverse(row, col, 1, -1, piece.color, [], 1))
            moves.update(self._traverse(row, col, 1, 1, piece.color, [], 1))
        return moves

    def _traverse(self, start_row, start_col, row_inc, col_inc, color, skipped, depth):
        """Helper function to check moves in a specific direction."""
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
        """Returns a simple evaluation of board state."""
        return self.white_left - self.black_left + (self.white_kings - self.black_kings) * 0.5

    def is_terminal(self):
        """Checks if the game has ended."""
        return self.white_left == 0 or self.black_left == 0

    def clone(self):
        """Creates a deep copy of the board."""
        return copy.deepcopy(self)


# Minimax algorithm with alpha-beta pruning
def minimax(board, depth, alpha, beta, maximizing_player):
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


# Display board in terminal with separators
def display_board(board):
    print("=" * 20)  # Separator line
    for row in board.board:
        print(" ".join([str(piece) if piece else "." for piece in row]))
    print("=" * 20)  # Another separator line
    print()  # Blank line for better readability



def main():
    board = Board()
    player_turn = WHITE
    depth = 3  # Depth limit for minimax, reduced for simplicity

    print("Initial Board:")
    display_board(board)

    while True:
        if board.is_terminal():
            winner = WHITE if board.black_left == 0 else BLACK
            print(f"Game Over! {winner} wins!")
            break

        if player_turn == WHITE:
            _, best_move = minimax(board, depth, float('-inf'), float('inf'), True)
        else:
            _, best_move = minimax(board, depth, float('-inf'), float('inf'), False)

        if best_move:
            piece, start, end = best_move
            skipped = board.get_valid_moves(piece, *start)[end]
            board.move_piece(piece, start, end)
            board.remove_piece(skipped)
            print(f"{player_turn.capitalize()} moves from {start} to {end}.")
            display_board(board)
        else:
            winner = BLACK if player_turn == WHITE else WHITE
            print(f"Game Over! {winner} wins due to no available moves!")
            break

        player_turn = BLACK if player_turn == WHITE else WHITE

if __name__ == "__main__":
    main()

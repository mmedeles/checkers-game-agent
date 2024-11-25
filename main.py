import math

# Constants for player pieces
WHITE = 'W'
BLACK = 'B'
EMPTY = '.'
MAX_DEPTH = 4

def apply_move(board, start_row, start_col, end_row, end_col, player):
    """Apply a move to the board."""
    board[start_row][start_col] = EMPTY
    board[end_row][end_col] = player
    return board

def get_possible_moves(board, player):
    """Get all possible moves for the player."""
    moves = []
    for row in range(8):
        for col in range(8):
            if board[row][col] == player:
                for d_row, d_col in [(-1, -1), (-1, 1)] if player == WHITE else [(1, -1), (1, 1)]:
                    new_row, new_col = row + d_row, col + d_col
                    if 0 <= new_row < 8 and 0 <= new_col < 8 and board[new_row][new_col] == EMPTY:
                        moves.append(((row, col), (new_row, new_col)))  # Save as tuples of (start, end)
    return moves

def minimax(board, depth, alpha, beta, maximizing, player):
    """Minimax algorithm with alpha-beta pruning."""
    if depth == 0 or is_game_over(board):
        return evaluate_board_using_heuristics(board, player), None

    if maximizing:
        max_score = -math.inf
        best_move = None
        for move in get_possible_moves(board, player):
            start, end = move
            temp_board = [row[:] for row in board]  # Create a copy of the board
            temp_board = apply_move(temp_board, start[0], start[1], end[0], end[1], player)
            current_score, _ = minimax(temp_board, depth - 1, alpha, beta, False, WHITE if player == BLACK else BLACK)
            if current_score > max_score:
                max_score = current_score
                best_move = move
            alpha = max(alpha, current_score)
            if beta <= alpha:
                break
        return max_score, best_move
    else:
        min_eval = math.inf
        best_move = None
        for move in get_possible_moves(board, player):
            start, end = move
            temp_board = [row[:] for row in board]  # Create a copy of the board
            temp_board = apply_move(temp_board, start[0], start[1], end[0], end[1], player)
            current_score, _ = minimax(temp_board, depth - 1, alpha, beta, True, WHITE if player == BLACK else BLACK)
            if current_score < min_eval:
                min_eval = current_score
                best_move = move
            beta = min(beta, current_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def evaluate_board_using_heuristics(board, player):
    """
    Evaluate the board for a checkers game, considering base score, position score, and piece types (regular or king).
    """
    
    # Score constants
    BASE_SCORE = 1
    KING_SCORE = 3
    POSITION_BONUS = 0.5
    
    def get_position_bonus(row, col):
        """Returns a position bonus if the piece is near the center."""
        if 1 <= row <= 4 and 1 <= col <= 4:  # Rows 2-5 and columns 2-5
            return POSITION_BONUS
        return 0
    
    # Calculate score for the player and the opponent
    player_score = 0
    opponent_score = 0
    
    for row_index, row in enumerate(board):
        for col_index, cell in enumerate(row):
            if cell == player or cell == (player + "_KING"):
                # Base score + Position bonus (if piece is in central region)
                piece_score = BASE_SCORE
                if 'KING' in cell:
                    piece_score = KING_SCORE
                piece_score += get_position_bonus(row_index, col_index)
                player_score += piece_score
            elif cell == (WHITE if player == 'BLACK' else 'BLACK') or cell == (WHITE if player == 'BLACK' else 'BLACK' + "_KING"):
                # Opponent's piece (either regular or king)
                piece_score = BASE_SCORE
                if 'KING' in cell:
                    piece_score = KING_SCORE
                piece_score += get_position_bonus(row_index, col_index)
                opponent_score += piece_score
    
    # Return the difference: Positive means the player is winning, negative means the opponent is
    return player_score - opponent_score

def suggest_next_move(board, player):
    """Suggest the best move for the current player."""
    best_score = -math.inf if player == WHITE else math.inf
    best_move = None

    for move in get_possible_moves(board, player):
        start, end = move
        temp_board = [row[:] for row in board]  # Create a copy of the board
        temp_board = apply_move(temp_board, start[0], start[1], end[0], end[1], player)
        score, _ = minimax(temp_board, MAX_DEPTH, -math.inf, math.inf, player == WHITE, WHITE if player == BLACK else BLACK)
        
        if (player == WHITE and score > best_score) or (player == BLACK and score < best_score):
            best_score = score
            best_move = move

    return best_move

def print_board(board):
    """Print the board in a readable format."""
    print("  0 1 2 3 4 5 6 7")
    for row in range(8):
        print(f"{row} {' '.join(board[row])}")

def is_game_over(board):
    """Check if the game is over (no more moves)."""
    return not any(EMPTY in row for row in board)

def find_move_coordinates(old_board, new_board, player):
    """Finds the coordinates of the move from old board to new board"""
    start, end = None, None
    for row in range(8):
        for col in range(8):
            if old_board[row][col] == player and new_board[row][col] == EMPTY:
                start = (row, col)
            if old_board[row][col] == EMPTY and new_board[row][col] == player:
                end = (row, col)
    return start, end
    
def is_game_over(board):
    """Check if the game is over (no more moves for one player or one player has no pieces)."""
    white_pieces = sum(row.count(WHITE) for row in board)
    black_pieces = sum(row.count(BLACK) for row in board)

    # If a player has no pieces left, the game is over
    if white_pieces == 0 or black_pieces == 0:
        return True

    # Check if any player has no valid moves left
    for player in [WHITE, BLACK]:
        if not get_possible_moves(board, player):
            return True  # No valid moves left for the current player

    return False

def simulate_game():
    """Simulate the full game between two computer players."""
    board = [
        [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK],
        [BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY],
        [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY],
        [EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE],
        [WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY],
    ]

    print_board(board)

    while not is_game_over(board):
        # White (maximizing) turn
        print("\nWhite's turn...")
        suggested_move_white = suggest_next_move(board, WHITE)
        if suggested_move_white:
            start, end = suggested_move_white
            print(f"\nWhite moves from {start} to {end}\n")
            board = apply_move(board, start[0], start[1], end[0], end[1], WHITE)

        print_board(board)

        if is_game_over(board):
            print("\n****Game Over! White wins!****\n")
            break

        # Black (minimizing) turn
        print("\nBlack's turn...")
        suggested_move_black = suggest_next_move(board, BLACK)
        if suggested_move_black:
            start, end = suggested_move_black
            print(f"\nBlack moves from {start} to {end}\n")
            board = apply_move(board, start[0], start[1], end[0], end[1], BLACK)

        print_board(board)

        if is_game_over(board):
            print("\n****Game Over! Black wins!****\n")
            break

def is_valid_move(board, start_row, start_col, end_row, end_col, player):
    """
    Check if the move is valid based on the board state and player.
    """
    possible_moves = get_possible_moves(board, player)
    return ((start_row, start_col), (end_row, end_col)) in possible_moves

def human_vs_computer():
    """Human vs Computer game mode."""
    board = [
        [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK],
        [BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY],
        [EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK, EMPTY, BLACK],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY, EMPTY],
        [WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY],
        [EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE],
        [WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY, WHITE, EMPTY],
    ]

    print_board(board)

    while not is_game_over(board):
        # Human (white) turn
        print("\nWhite's (human) turn...")
        valid_move = False
        while not valid_move:
            try:
                move = input("Enter your move (e.g., 5 0 4 1): ").split()
                if len(move) != 4:
                    raise ValueError("Input must contain exactly 4 numbers.")

                start_row, start_col, end_row, end_col = map(int, move)

                # Check if the move is valid
                if is_valid_move(board, start_row, start_col, end_row, end_col, WHITE):
                    valid_move = True
                else:
                    print("Invalid move. Please try again.")
            except ValueError as e:
                print(f"Invalid input: {e}. Please enter in the format 'start_row start_col end_row end_col'.")

        # Apply the move for the human player
        board = apply_move(board, start_row, start_col, end_row, end_col, WHITE)

        print_board(board)

        if is_game_over(board):
            print("\n****Game Over! White wins!****\n")
            break

        # Computer (black) turn
        print("\nBlack's turn (computer)...")
        suggested_move_black = suggest_next_move(board, BLACK)
        if suggested_move_black:
            start, end = suggested_move_black
            print(f"Black moves from {start} to {end}")
            board = apply_move(board, start[0], start[1], end[0], end[1], BLACK)

        print_board(board)

        if is_game_over(board):
            print("\n****Game Over! Black wins!****\n")
            break

def main():
    print("Welcome to Checkers! \n")
    
    print("Choose game mode:")
    print("1. Human vs Computer")
    print("2. Game simulation")
    mode = int(input("Enter choice (1/2): "))

    if mode == 1:
        human_vs_computer()
    elif mode == 2:
        simulate_game()
    else:
        print("Invalid choice. Please select either 1 or 2.")
    
if __name__ == "__main__":
    main()

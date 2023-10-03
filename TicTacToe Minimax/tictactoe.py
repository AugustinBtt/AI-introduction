"""
Tic Tac Toe Player
"""

import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)

    # if counts are equal, then it's X's turn
    # if X's count is more by 1, then it's O's turn
    return X if x_count == o_count else O


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board. i = x ; j = y
    """
    possible_actions = set()

    # Check if board is a terminal state
    if terminal(board):
        return possible_actions

    for i in range(3):  # Loop through rows
        for j in range(3):  # Loop through columns
            if board[i][j] == EMPTY:
                possible_actions.add((i, j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid action.")

    new_board = copy.deepcopy(board)
    curr_player = player(board)

    # update the board state with the action
    i, j = action
    if new_board[i][j] == EMPTY:
        new_board[i][j] = curr_player  # marks the cell with the symbol of the current player
    else:
        raise Exception("Cell already occupied.")

    return new_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for i in range(3):
        # rows
        if board[i][0] == board[i][1] == board[i][2] and board[i][0] is not None:
            return board[i][0]
        # columns
        if board[0][i] == board[1][i] == board[2][i] and board[0][i] is not None:
            return board[0][i]
    # diagonals
    if board[0][0] == board[1][1] == board[2][2] and board[0][0] is not None:
        return board[0][0]
    if board[0][2] == board[1][1] == board[2][0] and board[0][2] is not None:
        return board[0][2]

    # no winner
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True

    for i in range(3):
        for j in range(3):
            if board[i][j] == EMPTY:
                return False

    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise. X will maximize 0 minimize
    """
    winner_char = winner(board)
    if winner_char == 'X':
        return 1
    elif winner_char == 'O':
        return -1
    else:
        return 0


def minimax(board, alpha=float("-inf"), beta=float("inf")):

    if terminal(board):
        return utility(board), None

    best_move = None

    if player(board) == 'X':
        max_value = float('-inf')
        for action in actions(board):
            val, _ = minimax(result(board, action), alpha, beta)
            if val > max_value:
                max_value = val
                best_move = action
            alpha = max(alpha, val)
            if alpha >= beta:
                break
        return max_value, best_move

    else:
        min_value = float('inf')
        for action in actions(board):
            val, _ = minimax(result(board, action), alpha, beta)
            if val < min_value:
                min_value = val
                best_move = action
            beta = min(beta, val)
            if beta <= alpha:
                break
        return min_value, best_move

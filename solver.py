import chess


class PuzzleSolver:
    def __init__(self, board_state):
        self.board_state = board_state

    def dfs(self):
        return "DFS Result"

    def bfs(self):
        return "BFS Result"

    def minimax(self, depth):
        return "Minimax Result"

    def minimax_with_pruning(self, depth):
        return "Minimax with Alpha-Beta Result"

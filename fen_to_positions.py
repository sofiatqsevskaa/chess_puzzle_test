from chess import Board

fen = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

def fen_to_dict(fen):
    board = Board(fen)
    positions = {}
    for square, piece in board.piece_map().items():
        row = 7 - (square // 8)
        col = square % 8
        positions[f"{row},{col}"] = f"{'white' if piece.color else 'black'}_{piece.piece_type}"
    return positions

puzzle_positions = fen_to_dict(fen)
print(puzzle_positions)

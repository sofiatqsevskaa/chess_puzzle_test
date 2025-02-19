from chess import Board

fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"


def fen_to_dict(fen):
    piece_type_map = {
        1: "pawn",
        2: "knight",
        3: "bishop",
        4: "rook",
        5: "queen",
        6: "king"
    }
    board = Board(fen)
    positions = {}
    for square, piece in board.piece_map().items():
        row = 7 - (square // 8)
        col = square % 8
        piece_color = "white" if piece.color else "black"
        piece_name = piece_type_map[piece.piece_type]
        positions[(row, col)] = f"{piece_color} {piece_name}"

    current_player = "white" if fen.split()[1] == "w" else "black"
    return positions, current_player


# puzzle_positions = fen_to_dict(fen)
# print(puzzle_positions)

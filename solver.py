from collections import deque
import chess
from config import Config
import pygame
import sys
sys.setrecursionlimit(10000)

move_index = None
move_set_calculated = None


def display_moves(board, moves, screen, font):
    board.draw()
    for piece in board.pieces:
        piece.draw(screen)
    pygame.display.flip()
    pygame.display.update()


def convert_to_uci(piece, target_position):
    from_square = chess.square(piece.position[1], 7 - piece.position[0])
    to_square = chess.square(target_position[1], 7 - target_position[0])
    return chess.Move(from_square, to_square).uci()


def convert_from_uci(board, move_uci):
    x_piece = {"a": 0, "b": 1, "c": 2, "d": 3, "e": 4, "f": 5, "g": 6, "h": 7}

    start_file, start_rank, end_file, end_rank = move_uci[0], move_uci[1], move_uci[2], move_uci[3]

    start_x = 7 - (int(start_rank) - 1)
    start_y = x_piece[start_file]
    end_x = 7 - (int(end_rank) - 1)
    end_y = x_piece[end_file]

    piece = next((p for p in board.pieces if p.position ==
                 (start_x, start_y)), None)

    return (piece, (end_x, end_y)) if piece else None


def dfs(board, depth, max_depth, player, sequence, moves):
    global move_index
    global move_set_calculated

    print(f"DFS: {depth}, maxdepth: {max_depth}, player: {player}")

    move_index = max_depth
    original_position_fen = board.generate_fen()
    board_state_before = board.get_state()

    if move_set_calculated is None:
        if depth >= max_depth:
            if board.check_game_over():
                print("Game over! Sequence found:", sequence)
                move_set_calculated = display_moves(
                    board, moves, board.screen, board.font)
                return (sequence, board)
            return None

        possible_moves = board.generate_possible_moves(player)
        board_1 = chess.Board(original_position_fen)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]

        possible_moves_uci = [convert_to_uci(
            piece, target_position) for piece, target_position in possible_moves]

        possible = board.check_for_differences(
            legal_moves_uci, possible_moves_uci)

        possible_moves = [convert_from_uci(
            board, move_uci) for move_uci in possible]
        possible_moves = [move for move in possible_moves if move is not None]

        for piece, target_position in possible_moves:
            sequence.append(
                (piece.piece_type, piece.position, target_position))
            original_position = piece.position

            board.move_piece(piece, target_position)
            moves.append(
                (piece, original_position, target_position))

            board.current_player = "white" if player == "black" else "black"
            result = dfs(board, depth + 1, max_depth, "white" if player ==
                         "black" else "black", sequence, moves)

            if result is None:
                board.load_state(board_state_before)
                sequence.pop()
                moves.pop()
                print("No res found")

            if depth == max_depth:
                board.captured_pieces = []
                print("Max depth reached")

            if result is not None:
                print("Result found")
                return result

        return None
    else:
        return (sequence, board)


def bfs(board, max_depth, player, sequence, moves):
    global move_set_calculated
    global move_index

    move_index = max_depth
    moves = []

    if move_set_calculated is None:
        queue = deque([(board, 0, player, [], [])])

        while queue:
            current_board, depth, current_player, sequence, move_list = queue.popleft()
            print("BFS: ", depth, max_depth, current_player)

            if depth >= max_depth:

                if current_board.check_game_over():
                    print("Game over! Sequence found:", sequence)
                    print("Moves:", move_set_calculated)
                    return (sequence, current_board)
                continue

            possible_moves = current_board.generate_possible_moves(
                current_player)

            original_position_fen = current_board.generate_fen()
            board_state_before = current_board.get_state()

            board_1 = chess.Board(original_position_fen)
            legal_moves_uci = [move.uci() for move in board_1.legal_moves]
            possible_moves_uci = [convert_to_uci(
                piece, target_position) for piece, target_position in possible_moves]

            possible = current_board.check_for_differences(
                legal_moves_uci, possible_moves_uci)

            possible_moves = [convert_from_uci(
                current_board, move_uci) for move_uci in possible]
            possible_moves = [
                move for move in possible_moves if move is not None]

            for piece, target_position in possible_moves:
                new_sequence = sequence + \
                    [(piece.piece_type, piece.position, target_position)]
                new_move_list = move_list + \
                    [(piece, piece.position, target_position)]

                new_board = current_board.clone()
                new_board.move_piece(piece, target_position)

                next_player = "white" if current_player == "black" else "black"
                new_board.current_player = next_player
                queue.append((new_board, depth + 1, next_player,
                             new_sequence, new_move_list))

            current_board.load_state(board_state_before)

        print("no solution found")
        return None
    else:
        return (sequence, board)


def check_game_over_minimax(board, player):
    possible_moves = board.generate_possible_moves(player)

    original_position_fen = board.generate_fen().split(" ")[0]

    legal_moves_uci = [move.uci() for move in chess.Board(
        original_position_fen + " " + player[0]).legal_moves]

    possible_moves_uci = [convert_to_uci(piece, target_position)
                          for piece, target_position in possible_moves
                          if isinstance(convert_to_uci(piece, target_position), str)]

    possible_moves = board.check_for_differences(
        legal_moves_uci, possible_moves_uci)
    possible_moves = [convert_from_uci(
        board, move_uci) for move_uci in possible_moves]
    possible_moves = [move for move in possible_moves if move is not None]

    opp = board.opponent(player)

    # print(
    #     f"opp {opp} king in check {board.king_in_check} possible moves {possible_moves}")

    for move in possible_moves:
        if opp == move[0].piece_type[0]:
            possible_moves.remove(move)

    if not possible_moves and board.king_in_check:
        print("checkmate")
        board.winner = opp
        return True
    else:
        return False


def minmaxing(board, max_depth, player):
    global move_index
    global move_set_calculated
    global current_player

    current_player = player
    max_depth = max_depth + max_depth - 1
    move_index = max_depth

    print(f"Starting minmaxing as {player}")

    print(f"MAX DEPTH IS {max_depth}")

    if move_set_calculated is None:
        best_sequence = None
        best_score = -200
        best_board = None
        possible_moves = board.generate_possible_moves(player)

        original_position_fen = board.generate_fen().split(" ")[0]
        legal_moves_uci = [move.uci() for move in chess.Board(
            original_position_fen + " " + player[0]).legal_moves]

        possible_moves_uci = [convert_to_uci(piece, target_position)
                              for piece, target_position in possible_moves
                              if isinstance(convert_to_uci(piece, target_position), str)]

        possible_moves = board.check_for_differences(
            legal_moves_uci, possible_moves_uci)
        possible_moves = [convert_from_uci(
            board, move_uci) for move_uci in possible_moves]
        possible_moves = [move for move in possible_moves if move is not None]

        for move in possible_moves:
            print(f"i will be doing {move}")
            piece, square_to = move
            original_fen = board.generate_fen()
            board.move_piece_minimax(piece, square_to)

            score, sequence, fen_of_board = minimax(
                board, 1, False, max_depth, player, [move])
            board.load_fen_minimax(original_fen)
            if score > best_score:
                best_score = score
                best_sequence = sequence
                best_board = fen_of_board

        print(f"best score {best_score}, best sequence {best_sequence}")
        move_set_calculated = best_sequence
        print(f"MOVE SET CALCULATED  {move_set_calculated}")
        return move_set_calculated, best_board
    else:
        return move_set_calculated, best_board


def minimax(board, depth, isMaximising, max_depth, player, current_sequence=[]):
    if depth >= max_depth:
        opp = None
        if current_player == "white":
            player = "black"
            opp = "white"
        else:
            player = "white"
            opp = "black"

        if check_game_over_minimax(board, player):
            return board.evaluate(opp), current_sequence, board.generate_fen()
        else:
            return -100, current_sequence, board.generate_fen()

    best_sequence = None
    original_position_fen = board.generate_fen().split(" ")[0]
    best_fen = None

    if isMaximising:
        best_score = float('-inf')
        if current_player == "white":
            player = "white"
        else:
            player = "black"

        possible_moves = board.generate_possible_moves(player)
        legal_moves_uci = [move.uci() for move in chess.Board(
            original_position_fen + " " + player[0]).legal_moves]

        possible_moves_uci = [convert_to_uci(piece, target_position)
                              for piece, target_position in possible_moves
                              if isinstance(convert_to_uci(piece, target_position), str)]

        possible_moves = board.check_for_differences(
            legal_moves_uci, possible_moves_uci)
        possible_moves = [convert_from_uci(
            board, move_uci) for move_uci in possible_moves]
        possible_moves = [move for move in possible_moves if move is not None]

        for move in possible_moves:
            print(f"i will be doing {move}")
            piece, square_to = move
            original_fen = board.generate_fen()
            board.move_piece_minimax(piece, square_to)
            score, sequence, fen = minimax(
                board, depth + 1, False, max_depth, player, current_sequence + [move])
            board.load_fen_minimax(original_fen)
            if score > best_score:
                best_score = score
                best_sequence = sequence
                best_fen = fen
        return best_score, best_sequence, best_fen

    else:
        best_score = float('inf')
        if current_player == "white":
            player = "black"
        else:
            player = "white"
        possible_moves = board.generate_possible_moves(player)
        legal_moves_uci = [move.uci() for move in chess.Board(
            original_position_fen + " " + player[0]).legal_moves]

        possible_moves_uci = [convert_to_uci(piece, target_position)
                              for piece, target_position in possible_moves
                              if isinstance(convert_to_uci(piece, target_position), str)]

        possible_moves = board.check_for_differences(
            legal_moves_uci, possible_moves_uci)
        possible_moves = [convert_from_uci(
            board, move_uci) for move_uci in possible_moves]
        possible_moves = [move for move in possible_moves if move is not None]

        for move in possible_moves:
            piece, square_to = move
            original_fen = board.generate_fen()
            board.move_piece_minimax(piece, square_to)
            score, sequence, fen = minimax(
                board, depth + 1, True, max_depth, player, current_sequence + [move])
            board.load_fen_minimax(original_fen)
            if score < best_score:
                best_score = score
                best_sequence = sequence
                best_fen = fen
        return best_score, best_sequence, best_fen

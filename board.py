import pygame
from pygame import BLEND_ADD
from piece import Piece
from config import Config
import chess


class Board:
    def __init__(self, screen, pieces, current_player):
        self.size = Config.WINDOW_SIZE
        self.tile_size = Config.TILE_SIZE
        self.offset = Config.GAP
        self.font = pygame.font.SysFont('Verdana', 10)
        self.screen = screen
        self.pieces = pieces
        self.current_player = current_player
        self.occupied = [piece.position for piece in pieces]
        self.captured_pieces = []
        self.captured_piece = None
        self.king_in_check = False
        self.check_on_player = None
        self.checking_piece = None
        self.winner = None
        path = "assets/"

        self.piece_images = {
            "white pawn": pygame.image.load(path + "white_pawn.png"),
            "black pawn": pygame.image.load(path + "black_pawn.png"),
            "white rook": pygame.image.load(path + "white_rook.png"),
            "black rook": pygame.image.load(path + "black_rook.png"),
            "white knight": pygame.image.load(path + "white_knight.png"),
            "black knight": pygame.image.load(path + "black_knight.png"),
            "white bishop": pygame.image.load(path + "white_bishop.png"),
            "black bishop": pygame.image.load(path + "black_bishop.png"),
            "white queen": pygame.image.load(path + "white_queen.png"),
            "black queen": pygame.image.load(path + "black_queen.png"),
            "white king": pygame.image.load(path + "white_king.png"),
            "black king": pygame.image.load(path + "black_king.png"),
        }

        for key in self.piece_images:
            self.piece_images[key] = pygame.transform.smoothscale(
                self.piece_images[key], (Config.TILE_SIZE, Config.TILE_SIZE))

    def generate_fen(self):
        board_grid = [['' for _ in range(8)] for _ in range(8)]

        for piece in self.pieces:
            x, y = piece.position
            rank = x + 1
            file = y
            symbol = piece.piece_type.split(' ')[1][0].upper(
            ) if piece.color == 'white' else piece.piece_type.split(' ')[1][0].lower()
            if piece.piece_type.split(' ')[1] == 'knight':
                symbol = 'N' if piece.color == 'white' else 'n'
            board_grid[rank - 1][file] = symbol

        fen_rows = []
        for row in board_grid:
            fen_row = ''
            empty_count = 0
            for cell in row:
                if cell == '':
                    empty_count += 1
                else:
                    if empty_count > 0:
                        fen_row += str(empty_count)
                        empty_count = 0
                    fen_row += cell
            if empty_count > 0:
                fen_row += str(empty_count)
            fen_rows.append(fen_row)
        fen_board = '/'.join(fen_rows)

        current_player_fen = 'w' if self.current_player == 'white' else 'b'

        castling_rights = '-'
        en_passant = '-'
        halfmove_clock = '0'
        fullmove_number = '1'

        fen = f"{fen_board} {current_player_fen} {castling_rights} {en_passant} {halfmove_clock} {fullmove_number}"
        return fen

    def load_fen(self, fen):
        parts = fen.split()
        board_fen = parts[0]
        self.current_player = 'white' if parts[1] == 'w' else 'black'

        piece_symbols = {
            'P': 'pawn', 'N': 'knight', 'B': 'bishop', 'R': 'rook', 'Q': 'queen', 'K': 'king',
            'p': 'pawn', 'n': 'knight', 'b': 'bishop', 'r': 'rook', 'q': 'queen', 'k': 'king'
        }

        self.pieces = []
        rows = board_fen.split('/')

        for rank in range(8):
            file = 0
            for char in rows[rank]:
                if char.isdigit():
                    file += int(char)
                else:
                    color = 'white' if char.isupper() else 'black'
                    piece_type = piece_symbols[char]
                    self.pieces.append(
                        Piece(piece_type, color, (rank, file),  self.piece_images[f"{color} {piece_type}"], self.screen))
                    self.occupied.append((rank, file))
                    file += 1

    def clone(self):
        cloned_pieces = [piece.clone() for piece in self.pieces]
        cloned_board = Board(None, cloned_pieces, self.current_player)

        cloned_board.screen = self.screen
        cloned_board.font = self.font
        return cloned_board

    def draw(self):
        self.screen.fill((255, 255, 255))
        for row in range(8):
            for col in range(8):
                color = Config.WHITE if (row + col) % 2 == 0 else Config.GRAY
                pygame.draw.rect(self.screen, color,
                                 (self.offset + col * self.tile_size, self.offset + row * self.tile_size,
                                  self.tile_size, self.tile_size))
            self.draw_coordinates(row)

    def draw_coordinates(self, row):
        rank_text = self.font.render(str(8 - row), False, Config.BLACK)
        file_text = self.font.render(chr(ord('a') + row), False, Config.BLACK)
        self.screen.blit(rank_text,
                         (5, self.offset + row * self.tile_size + self.tile_size // 2 - rank_text.get_height() // 2))
        self.screen.blit(file_text, (self.offset + row * self.tile_size + self.tile_size // 2 - file_text.get_width() // 2,
                                     self.offset + self.size + Config.GAP // 4))

    def get_board_state(self):
        board_state = {
            "pieces": {piece.position: piece.piece_type for piece in self.pieces},
            "current_player": self.current_player
        }
        return board_state

    def convert_to_uci(self, piece, target_position):
        from_square = chess.square(piece.position[1], 7 - piece.position[0])
        to_square = chess.square(target_position[1], 7 - target_position[0])
        return chess.Move(from_square, to_square).uci()

    def check_for_differences(self, legal_moves_uci, possible_moves_uci):
        legal_moves_set = set(legal_moves_uci)
        possible_moves_set = set(possible_moves_uci)
        moves_to_add = legal_moves_set - possible_moves_set

        moves_to_remove = possible_moves_set - legal_moves_set

        updated_possible_moves = list(
            possible_moves_set - moves_to_remove) + list(moves_to_add)

        return updated_possible_moves

    def is_position_attacked(self, position, opponent_moves):
        return position in opponent_moves

    def load_move(self, move):
        piece_name = move[0]
        pos_to = move[2]

        p = None
        for piece in self.pieces:
            if piece.piece_type == piece_name:
                p = piece
                break

        self.move_piece(p, pos_to)

    def move_piece(self, piece_from, square_to):
        captured = None
        for piece_to in self.pieces:
            if piece_to.position == square_to:
                if piece_to.color == piece_from.color:
                    print(
                        f"Invalid move: Cannot capture own piece {piece_to.piece_type}")
                    return None

                if "king" in piece_to.piece_type:
                    return None

                captured = piece_to
                self.pieces.remove(piece_to)
                self.occupied.remove(square_to)
                break

        self.occupied.remove(piece_from.position)
        piece_from.position = square_to
        self.occupied.append(square_to)

        return captured

    def undo(self, piece, original_square, square_to, captured, captured_position):
        original_piece = None
        for p in self.pieces:
            if p.piece_type == piece.piece_type and p.position == square_to:
                original_piece = p
                break

        if original_piece is None:
            print(
                f"Undo failed: Original piece {piece.piece_type} at {original_square} not found")
            print(f"pieces: {self.pieces}")
            return None

        self.occupied.remove(original_piece.position)
        original_piece.position = original_square
        self.occupied.append(original_square)

        if captured and captured_position == square_to:
            print(
                f"Restoring captured piece {captured.piece_type} at {captured_position}")
            self.pieces.append(captured)
            self.occupied.append(captured_position)

        return original_piece

    def opponent(self, player):
        return 'black' if player == 'white' else 'white'

    def evaluate_king_safety(self, player):
        king = next(piece for piece in self.pieces if piece.piece_type.split(
            ' ')[1] == 'king' and piece.color == player)
        king_x, king_y = king.position
        score = 0

        pawn_shield = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if (king_x + dx, king_y + dy) in [(p.position[0], p.position[1]) for p in self.pieces if p.piece_type.split(' ')[1] == 'pawn' and p.color == player]:
                    pawn_shield += 1
        score += pawn_shield

        open_files = 0
        for dy in [-1, 1]:
            if not any(p.position[1] == king_y + dy for p in self.pieces if p.piece_type.split(' ')[1] == 'pawn' and p.color == player):
                open_files += 1
        score -= 0.2 * open_files

        return score

    def evaluate(self, player):
        score = 0
        for piece in self.pieces:
            piece_type = piece.piece_type.split(
                ' ')[1]
            piece_color = piece.color
            value = Config.PIECE_VALUES.get(piece_type, 0)
            score += value if piece.color == player else -value

        mobility_score = len(self.generate_possible_moves(player)) - \
            len(self.generate_possible_moves(self.opponent(player)))

        score += mobility_score

        king_safety_score = self.evaluate_king_safety(
            player) - self.evaluate_king_safety(self.opponent(player))
        score += king_safety_score

        if self.king_in_check and self.check_on_player == self.opponent(player):
            score += 100
            if len(self.generate_possible_moves(self.opponent(player))) == 0:
                score += 150

        if self.king_in_check and self.check_on_player == player:
            score -= 100

        print(score)
        return score

    def generate_possible_moves(self, current_player):
        possible_moves = []
        opponent_king_squares = []
        opponent_attacking_squares = []
        all_attacking_squares = []
        pieces_saying_check = []

        def is_within_board(x, y):
            return 0 < x <= 8 and 0 < y <= 8

        for piece in self.pieces:
            if not isinstance(piece, Piece):
                # print(
                #     f"Unexpected type in self.pieces: {piece} (type: {type(piece)})")
                continue
            if piece.piece_type.lower() == f"{'black' if current_player == 'white' else 'white'} king":
                opponent_king_moves = [
                    (1, 0), (0, 1), (-1, 0), (0, -1), (1,
                                                       1), (1, -1), (-1, 1), (-1, -1)
                ]
                for dx, dy in opponent_king_moves:
                    x = piece.position[0] + dx
                    y = piece.position[1] + dy
                    if is_within_board(x, y):
                        opponent_king_squares.append((x, y))

        def get_attacking_squares():
            for piece in self.pieces:
                if (current_player == 'white' and piece.color == 'black') or (current_player == 'black' and piece.color == 'white'):
                    piece_type = piece.piece_type.split()[1]
                    if piece_type in ["rook", "knight", "bishop", "queen", "pawn"]:
                        directions = {
                            "rook": [(0, 1), (1, 0), (0, -1), (-1, 0)],
                            "knight": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
                            "bishop": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
                            "queen": [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
                            "pawn": [(1, -1), (-1, -1)] if piece.color == "black" else [(1, 1), (-1, 1)]
                        }[piece_type]
                        for dx, dy in directions:
                            x, y = piece.position

                            while True:
                                x += dx
                                y += dy

                                if 0 <= x < 8 and 0 <= y < 8:
                                    for p in self.pieces:
                                        if p.position == (x, y):
                                            all_attacking_squares.append(
                                                (piece, (x, y)))
                                    opponent_attacking_squares.append((x, y))

                                    if piece_type in ["knight", "pawn"]:
                                        break
                                    if any(p.position == (x, y) for p in self.pieces):
                                        break
                                else:
                                    break
        get_attacking_squares()

        current_king = next(
            (piece for piece in self.pieces if piece.piece_type.lower()
             == f"{current_player} king"), None
        )

        def if_check(position, opponent_moves):
            for attacking_piece, attacking_position in opponent_moves:
                if attacking_position == position:
                    pieces_saying_check.append(attacking_piece)
                    return True
            self.king_in_check = False
            self.check_on_player = None
            return False

        # print(f"checking for check on player {current_player}")

        white_rook_positions = [
            piece.position for piece in self.pieces if piece.piece_type == 'white rook']

        # print(f"white rook on {white_rook_positions}")

        self.king_in_check = if_check(
            current_king.position, all_attacking_squares)

        if self.king_in_check:
            self.check_on_player = current_player

        def is_square_attacked(square, opponent_moves):
            return any(attack_square == square for attack_square in opponent_moves)

        def can_capture_checking_piece(piece):
            return any(checking_piece.piece_type == piece.piece_type and checking_piece.position == piece.position for checking_piece in pieces_saying_check)

        def can_move_resolve_check(move):
            original_position = move[0].position
            target_position = move[1]
            piece = move[0]

            if original_position not in self.occupied:
                print(
                    f"WARNING: Trying to move piece {piece.piece_type}! Original position {original_position} is not in occupied: {self.occupied}")
            else:
                self.occupied.remove(original_position)
            piece.position = target_position
            self.occupied.append(target_position)

            recalculated_opponent_attacking_squares = []
            for opponent_piece in self.pieces:
                if (current_player == 'white' and opponent_piece.color == 'black') or (current_player == 'black' and opponent_piece.color == 'white'):
                    directions = {
                        'white rook': [(0, 1), (1, 0), (0, -1), (-1, 0)],
                        'black rook': [(0, 1), (1, 0), (0, -1), (-1, 0)],
                        'white knight': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
                        'black knight': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
                        'white bishop': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'black bishop': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'white queen': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'black queen': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'white pawn': [(1, 1), (-1, 1)],
                        'black pawn': [(1, -1), (-1, -1)]
                    }.get(opponent_piece.piece_type, [])

                    for dx, dy in directions:
                        x, y = opponent_piece.position
                        while True:
                            x += dx
                            y += dy
                            if 0 <= x < 8 and 0 <= y < 8:
                                next_position = (x, y)
                                recalculated_opponent_attacking_squares.append(
                                    next_position)
                                if opponent_piece.piece_type in ['white knight', 'black knight', 'white pawn', 'black pawn'] or next_position in self.occupied:
                                    break
                            else:
                                break

            king_safe = not is_square_attacked(
                current_king.position, recalculated_opponent_attacking_squares)

            self.occupied.remove(target_position)
            piece.position = original_position
            self.occupied.append(original_position)

            king_moves = [(1, 0), (-1, 0), (0, 1), (0, -1),
                          (1, 1), (1, -1), (-1, 1), (-1, -1)]
            for dx, dy in king_moves:
                new_pos = (current_king.position[0] +
                           dx, current_king.position[1] + dy)
                if 0 <= new_pos[0] < 8 and 0 <= new_pos[1] < 8:
                    if new_pos not in self.occupied and not is_square_attacked(new_pos, recalculated_opponent_attacking_squares):
                        # print(f"King can escape to {new_pos}")
                        king_safe = True

            return king_safe

        for piece in self.pieces:
            if (current_player == 'white' and piece.color == 'white') or (current_player == 'black' and piece.color == 'black'):
                if piece.piece_type == "black pawn":
                    forward_square = (piece.position[0], piece.position[1] - 1)
                    if forward_square not in self.occupied:
                        move = (piece, forward_square)
                        if (not self.king_in_check or can_move_resolve_check(move)):
                            possible_moves.append((piece, forward_square))
                    if piece.position[0] > 0:
                        capture_left_square = (
                            piece.position[0] - 1, piece.position[1] - 1)
                        if capture_left_square in [(p.position[0], p.position[1]) for p in self.pieces if p.color == "white"]:
                            move = (piece, capture_left_square)
                            captured_piece = next((p for p in self.pieces if (
                                p.position[0], p.position[1]) == capture_left_square), None)
                            if captured_piece and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                possible_moves.append(
                                    (piece, capture_left_square))
                    if piece.position[0] < 7:
                        capture_right_square = (
                            piece.position[0] + 1, piece.position[1] - 1)
                        if capture_right_square in [(p.position[0], p.position[1]) for p in self.pieces if p.color == "white"]:
                            move = (piece, capture_right_square)
                            captured_piece = next((p for p in self.pieces if (
                                p.position[0], p.position[1]) == capture_right_square), None)
                            if captured_piece and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                possible_moves.append(
                                    (piece, capture_right_square))
                elif piece.piece_type == "white pawn":
                    forward_square = (piece.position[0], piece.position[1] + 1)
                    if forward_square not in self.occupied:
                        move = (piece, forward_square)
                        if (not self.king_in_check or can_move_resolve_check(move)):
                            possible_moves.append((piece, forward_square))
                    if piece.position[0] > 0:
                        capture_left_square = (
                            piece.position[0] - 1, piece.position[1] + 1)
                        if capture_left_square in [(p.position[0], p.position[1]) for p in self.pieces if p.color == "black"]:
                            move = (piece, capture_left_square)
                            captured_piece = next((p for p in self.pieces if (
                                p.position[0], p.position[1]) == capture_left_square), None)
                            if captured_piece and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                possible_moves.append(
                                    (piece, capture_left_square))
                    if piece.position[0] < 7:
                        capture_right_square = (
                            piece.position[0] + 1, piece.position[1] + 1)
                        if capture_right_square in [(p.position[0], p.position[1]) for p in self.pieces if p.color == "black"]:
                            move = (piece, capture_right_square)
                            captured_piece = next((p for p in self.pieces if (
                                p.position[0], p.position[1]) == capture_right_square), None)
                            if captured_piece and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                possible_moves.append(
                                    (piece, capture_right_square))
                elif piece.piece_type.split(" ")[1] in ["rook", "knight", "bishop", "queen"]:
                    directions = {
                        'rook': [(0, 1), (1, 0), (0, -1), (-1, 0)],
                        'knight': [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
                        'bishop': [(1, 1), (1, -1), (-1, 1), (-1, -1)],
                        'queen': [(1, 0), (0, 1), (-1, 0), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
                    }[piece.piece_type.split(" ")[1]]
                    for dx, dy in directions:
                        x, y = piece.position
                        while True:
                            x += dx
                            y += dy
                            if 0 <= x < 8 and 0 <= y < 8:
                                next_square = (x, y)
                                move = (piece, next_square)
                                if next_square not in self.occupied:
                                    if (not self.king_in_check or can_move_resolve_check(move)):
                                        possible_moves.append(
                                            (piece, next_square))
                                    if piece.piece_type.split(" ")[1] == 'knight':
                                        break
                                else:
                                    if next_square in [(p.position[0], p.position[1]) for p in self.pieces if p.color != piece.color]:
                                        captured_piece = next((p for p in self.pieces if (
                                            p.position[0], p.position[1]) == next_square), None)
                                        if captured_piece and (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece)):
                                            possible_moves.append(
                                                (piece, next_square))
                                    break
                            else:
                                break
                elif piece.piece_type in ["black king", "white king"]:
                    directions = [(0, 1), (1, 0), (0, -1), (-1, 0),
                                  (1, 1), (1, -1), (-1, 1), (-1, -1)]
                    for dx, dy in directions:
                        x, y = piece.position
                        next_position = (x + dx, y + dy)

                        if 0 <= next_position[0] < 8 and 0 <= next_position[1] < 8:
                            move = (piece, next_position)

                            if (next_position not in self.occupied and
                                next_position not in opponent_king_squares and
                                    not is_square_attacked(next_position, opponent_attacking_squares)):

                                if not self.king_in_check or can_move_resolve_check(move):
                                    possible_moves.append(
                                        (piece, next_position))

                            else:
                                captured_piece = next(
                                    (p for p in self.pieces if p.position == next_position and p.color != piece.color), None)

                                if (captured_piece and
                                    next_position not in opponent_king_squares and
                                    not is_square_attacked(next_position, opponent_attacking_squares) and
                                        (not self.king_in_check or can_move_resolve_check(move) or can_capture_checking_piece(captured_piece))):

                                    possible_moves.append(
                                        (piece, next_position))

        for piece, square in possible_moves:
            if square in self.occupied:
                for p in self.pieces:
                    if p.piece_type == "king" and (p.position[0], p.position[1]) == square:
                        possible_moves.remove((piece, square))
        return possible_moves

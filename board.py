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
        self.font = pygame.font.SysFont('Verdana', 16)
        self.screen = screen
        self.pieces = pieces
        self.current_player = current_player
        self.occupied_squares = [piece.position for piece in pieces]
        self.captured_pieces = []

    def draw(self):
        self.screen.fill((255, 255, 255))
        for row in range(8):
            for col in range(8):
                color = Config.YELLOW if (row + col) % 2 == 0 else Config.BROWN
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

    def is_in_check(self, color):
        king = next(
            (piece for piece in self.pieces if piece.piece_type == f"{color} king"), None)
        if not king:
            return False
        opponent_moves = [move for piece in self.pieces if piece.piece_type.split(
        )[0] != color for move in piece.valid_moves(self)]
        return king.position in opponent_moves

    def check_game_over(self):
        possible_moves = self.generate_possible_moves(self.current_player)

        original_position_fen = self.generate_fen()

        board_1 = chess.Board(original_position_fen)
        legal_moves_uci = [move.uci() for move in board_1.legal_moves]

        possible_moves = self.check_for_differences(
            legal_moves_uci, possible_moves)

        if not possible_moves and self.king_in_check:
            return True
        return False

    def is_position_attacked(self, position, opponent_moves):
        return position in opponent_moves

    def generate_possible_moves(self, current_player):
        possible_moves = []
        opponent_king_squares = []
        opponent_attacking_squares = []
        all_attacking_squares = []
        pieces_saying_check = []

        def is_within_board(x, y):
            return 0 <= x < 8 and 0 <= y < 8

        for piece in self.pieces:
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
                if piece.piece_type.split()[0] != current_player:
                    attacking_squares = piece.valid_moves(self, current_player)
                    for target_position in attacking_squares:
                        all_attacking_squares.append((piece, target_position))
                        opponent_attacking_squares.append(target_position)

        get_attacking_squares()

        current_king = next(
            (piece for piece in self.pieces if piece.piece_type.lower()
             == f"{current_player} king"), None
        )

        def if_check(position):
            for attacking_piece, attack_position in all_attacking_squares:
                if attack_position == position:
                    pieces_saying_check.append(attacking_piece)
                    self.king_in_check = True
                    return True
            self.king_in_check = False
            return False

        self.king_in_check = if_check(current_king.position)

        def can_move_resolve_check(move):
            original_position, target_position, piece = move
            self.occupied_squares.remove(original_position)
            piece.position = target_position
            self.occupied_squares.append(target_position)

            recalculated_opponent_attacking_squares = []
            for opponent_piece in self.pieces:
                if opponent_piece.piece_type.split()[0] != current_player:
                    opponent_attacking_squares = opponent_piece.valid_moves(
                        self, current_player)
                    recalculated_opponent_attacking_squares.extend(
                        opponent_attacking_squares)

            king_safe = not if_check(current_king.position)

            self.occupied_squares.remove(target_position)
            piece.position = original_position
            self.occupied_squares.append(original_position)

            return king_safe

        for piece in self.pieces:
            if piece.piece_type.split()[0] == current_player:
                valid_moves = piece.valid_moves(self, current_player)
                for target_position in valid_moves:
                    move = (piece.position, target_position, piece)
                    if (not self.king_in_check or can_move_resolve_check(move)):
                        possible_moves.append((piece, target_position))

        return possible_moves

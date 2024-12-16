import pygame
from pygame import BLEND_ADD

from config import *


class Board:
    def __init__(self, screen, pieces, current_player):
        self.size = Config.WINDOW_SIZE
        self.tile_size = Config.TILE_SIZE
        self.offset = Config.GAP
        self.font = pygame.font.SysFont('Verdana', 16)
        self.screen = screen
        self.pieces = pieces
        self.current_player = current_player

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
            "pieces": {},
            "current_player": self.current_player
        }

        for piece in self.pieces:
            position = piece.position
            piece_info = piece.piece_type
            board_state["pieces"][position] = piece_info

        return board_state

    def is_in_check(self, color):
        king = None
        for piece in self.pieces:
            if piece.piece_type.split()[0] == color and piece.piece_type.split()[1] == "king":
                king = piece
                break

        if not king:
            return False

        king_position = king.position
        opponent_color = "black" if color == "white" else "white"

        for piece in self.pieces:
            if piece.piece_type.split()[0] == opponent_color:
                moves = piece.valid_moves(self)
                if king_position in moves:
                    return True

        return False

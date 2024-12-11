import pygame
from config import Config


class Piece:
    def __init__(self, piece_type, color, position, image):
        self.piece_type = f"{color} {piece_type}"
        self.position = position
        self.image = pygame.transform.scale(image, (Config.PIECE_SIZE, Config.PIECE_SIZE))

    def draw(self, screen):
        row, col = self.position
        board_offset = (Config.WINDOW_SIZE + 2 * Config.GAP - 8 * Config.TILE_SIZE) // 2
        x = board_offset + col * Config.TILE_SIZE + (Config.TILE_SIZE - Config.PIECE_SIZE) // 2
        y = board_offset + row * Config.TILE_SIZE + (Config.TILE_SIZE - Config.PIECE_SIZE) // 2
        screen.blit(self.image, (x, y))

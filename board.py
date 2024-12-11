import pygame
from config import *


screen = pygame.display.set_mode((Config.WINDOW_SIZE + Config.GAP * 2, Config.WINDOW_SIZE + Config.GAP * 2))


class Board:
    def __init__(self):
        self.size = Config.WINDOW_SIZE
        self.tile_size = Config.TILE_SIZE
        self.offset = Config.GAP
        self.font = pygame.font.SysFont('Verdana', 16)

    def draw(self):
        screen.fill((255, 255, 255))
        for row in range(8):
            for col in range(8):
                color = Config.YELLOW if (row + col) % 2 == 0 else Config.BROWN
                pygame.draw.rect(screen, color,
                                 (self.offset + col * self.tile_size, self.offset + row * self.tile_size,
                                  self.tile_size, self.tile_size))
            self.draw_coordinates(row)

    def draw_coordinates(self, row):
        rank_text = self.font.render(str(8 - row), False, Config.BLACK)
        file_text = self.font.render(chr(ord('a') + row), False, Config.BLACK)

        screen.blit(rank_text,
                    (5, self.offset + row * self.tile_size + self.tile_size // 2 - rank_text.get_height() // 2))
        screen.blit(file_text, (self.offset + row * self.tile_size + self.tile_size // 2 - file_text.get_width() // 2,
                                self.offset + self.size + Config.GAP // 4))



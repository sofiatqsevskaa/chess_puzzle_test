import pygame
from config import Config


class Piece:
    def __init__(self, piece_type, color, position, image, screen):
        self.piece_type = f"{color} {piece_type}"
        self.color = color
        self.position = position
        if image is not None:
            self.image = pygame.transform.scale(
                image, (Config.PIECE_SIZE, Config.PIECE_SIZE))
        else:
            self.image = None
        self.screen = screen
        self.id = hash((piece_type, color, position))

    def draw(self, screen):
        row, col = self.position
        board_offset = (Config.WINDOW_SIZE + 2 * Config.GAP -
                        8 * Config.TILE_SIZE) // 2
        x = board_offset + col * Config.TILE_SIZE + \
            (Config.TILE_SIZE - Config.PIECE_SIZE) // 2
        y = board_offset + row * Config.TILE_SIZE + \
            (Config.TILE_SIZE - Config.PIECE_SIZE) // 2
        screen.blit(self.image, (x, y))

    def update(self, position, board):
        if position[0] >= 8 or position[0] < 0 or position[1] >= 8 or position[1] < 0:
            return False

        target_piece = next(
            (p for p in board.pieces if p.position == position), None)

        if target_piece:
            if target_piece.piece_type.split()[0] != self.piece_type.split()[0]:
                board.pieces.remove(target_piece)
            else:
                return False

        self.position = position
        self.draw(self.screen)
        return True

    def __repr__(self):
        return f"Piece ({self.piece_type}, {self.position})"

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.position == other.position
        return False

    def clone(self):
        return Piece(
            self.piece_type.split(
                " ")[1], self.color, self.position, self.image, self.screen
        )

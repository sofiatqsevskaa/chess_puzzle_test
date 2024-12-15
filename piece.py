import pygame
from config import Config


class Piece:
    def __init__(self, piece_type, color, position, image, screen):
        self.piece_type = f"{color} {piece_type}"
        self.position = position
        self.image = pygame.transform.scale(image, (Config.PIECE_SIZE, Config.PIECE_SIZE))
        self.screen = screen

    def draw(self, screen):
        row, col = self.position
        board_offset = (Config.WINDOW_SIZE + 2 * Config.GAP - 8 * Config.TILE_SIZE) // 2
        x = board_offset + col * Config.TILE_SIZE + (Config.TILE_SIZE - Config.PIECE_SIZE) // 2
        y = board_offset + row * Config.TILE_SIZE + (Config.TILE_SIZE - Config.PIECE_SIZE) // 2
        screen.blit(self.image, (x, y))

    def valid_moves(self, board, color):
        moves = []
        directions = {
            "pawn": [(1, 0), (2, 0), (1, -1), (1, 1)] if "white" in self.piece_type else [(-1, 0), (-2, 0), (-1, -1),
                                                                                          (-1, 1)],
            "rook": [(1, 0), (-1, 0), (0, 1), (0, -1)],
            "knight": [(2, 1), (2, -1), (-2, 1), (-2, -1), (1, 2), (1, -2), (-1, 2), (-1, -2)],
            "bishop": [(1, 1), (1, -1), (-1, 1), (-1, -1)],
            "queen": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)],
            "king": [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]
        }
        piece_moves = directions[self.piece_type.split()[1]]
        for direction in piece_moves:
            for step in range(1, 8):
                new_row = self.position[0] + direction[0] * step
                new_col = self.position[1] + direction[1] * step
                if not (0 <= new_row < 8 and 0 <= new_col < 8):
                    break
                target_piece = next((p for p in board.pieces if p.position == (new_row, new_col)), None)
                if target_piece:
                    if target_piece.piece_type.split()[0] != self.piece_type.split()[0]:
                        moves.append((new_row, new_col))
                    break
                moves.append((new_row, new_col))
                if "pawn" in self.piece_type or "king" in self.piece_type or "knight" in self.piece_type:
                    break

        valid_moves = []
        for move in moves:
            temp_board = board.pieces.copy()
            temp_piece = Piece(self.piece_type.split()[1], self.piece_type.split()[0], move, self.image, self.screen)
            temp_board.remove(self)
            temp_board.append(temp_piece)
            if not board.is_in_check(temp_board, color):
                valid_moves.append(move)

        return valid_moves

    def update(self, position):
        if position[0]>=8 or position[0]<0 or position[1]>=8 or position[1]<0:
            return False
        self.position = position
        self.draw(self.screen)

    def __repr__(self):
        return f"Piece ({self.piece_type}, {self.position})"

    def __eq__(self, other):
        if isinstance(other, Piece):
            return self.position == other.position
        return False
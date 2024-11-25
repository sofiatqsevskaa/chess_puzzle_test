import pygame
import os

pygame.init()

WINDOW_SIZE = 640
TILE_SIZE = WINDOW_SIZE // 8
WHITE = (255, 255, 255)
BLACK = (70, 70, 70)

screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chess Puzzle Solver")

assets_folder = "chess_pieces"
piece_images = {}

for color in ["white", "black"]:
    for piece in ["king", "queen", "rook", "bishop", "knight", "pawn"]:
        filename = f"{color}_{piece}.png"
        image_path = os.path.join(assets_folder, filename)
        if os.path.exists(image_path):
            piece_images[f"{color}_{piece}"] = pygame.image.load(image_path)

initial_pieces = {
    (0, 0): "black_rook", (0, 1): "black_knight", (0, 2): "black_bishop", (0, 3): "black_queen",
    (0, 4): "black_king", (0, 5): "black_bishop", (0, 6): "black_knight", (0, 7): "black_rook",
    (1, 0): "black_pawn", (1, 1): "black_pawn", (1, 2): "black_pawn", (1, 3): "black_pawn",
    (1, 4): "black_pawn", (1, 5): "black_pawn", (1, 6): "black_pawn", (1, 7): "black_pawn",
    (6, 0): "white_pawn", (6, 1): "white_pawn", (6, 2): "white_pawn", (6, 3): "white_pawn",
    (6, 4): "white_pawn", (6, 5): "white_pawn", (6, 6): "white_pawn", (6, 7): "white_pawn",
    (7, 0): "white_rook", (7, 1): "white_knight", (7, 2): "white_bishop", (7, 3): "white_queen",
    (7, 4): "white_king", (7, 5): "white_bishop", (7, 6): "white_knight", (7, 7): "white_rook",
}

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for (row, col), piece_name in initial_pieces.items():
        piece_image = piece_images.get(piece_name)
        if piece_image:
            scaled_image = pygame.transform.scale(piece_image, (TILE_SIZE, TILE_SIZE))
            screen.blit(scaled_image, (col * TILE_SIZE, row * TILE_SIZE))

    pygame.display.flip()

pygame.quit()

import pygame
import sqlite3
import json
import os

pygame.init()

WINDOW_SIZE = 640
TILE_SIZE = WINDOW_SIZE // 8
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

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


def get_puzzle_positions(puzzle_id):
    conn = sqlite3.connect("chess_puzzles.db")
    cursor = conn.cursor()
    cursor.execute("SELECT positions FROM puzzles WHERE id = ?", (puzzle_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return {}


puzzle_id = 1
positions = get_puzzle_positions(puzzle_id)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    for row in range(8):
        for col in range(8):
            color = WHITE if (row + col) % 2 == 0 else BLACK
            pygame.draw.rect(screen, color, (col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE))

    for pos, piece_name in positions.items():
        row, col = map(int, pos.split(","))
        piece_image = piece_images.get(piece_name)
        if piece_image:
            scaled_image = pygame.transform.scale(piece_image, (TILE_SIZE, TILE_SIZE))
            screen.blit(scaled_image, (col * TILE_SIZE, row * TILE_SIZE))

    pygame.display.flip()

pygame.quit()

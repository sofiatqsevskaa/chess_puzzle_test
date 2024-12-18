import pygame
from config import Config
from board import Board as Chess_Board
from fen_to_positions import fen_to_dict
from piece import Piece
from solver import PuzzleSolver

def initialize_game():
    pygame.init()
    pygame.display.set_caption("Chess Board")

def get_puzzle_positions(fen):
    return fen_to_dict(fen)

def load_piece_images():
    path = "assets/"
    piece_images = {
        "white pawn": pygame.image.load(path + "white pawn.png"),
        "black pawn": pygame.image.load(path + "black pawn.png"),
        "white rook": pygame.image.load(path + "white rook.png"),
        "black rook": pygame.image.load(path + "black rook.png"),
        "white knight": pygame.image.load(path + "white knight.png"),
        "black knight": pygame.image.load(path + "black knight.png"),
        "white bishop": pygame.image.load(path + "white bishop.png"),
        "black bishop": pygame.image.load(path + "black bishop.png"),
        "white queen": pygame.image.load(path + "white queen.png"),
        "black queen": pygame.image.load(path + "black queen.png"),
        "white king": pygame.image.load(path + "white king.png"),
        "black king": pygame.image.load(path + "black king.png"),
    }
    for key in piece_images:
        piece_images[key] = pygame.transform.smoothscale(piece_images[key], (Config.TILE_SIZE, Config.TILE_SIZE))
    return piece_images

def create_pieces(puzzle_positions, piece_images, screen):
    pieces = []
    for position, piece_info in puzzle_positions.items():
        color, piece_type = piece_info.split()
        x, y = position
        image = piece_images.get(f"{color} {piece_type}")
        piece = Piece(piece_type, color, (x, y), image, screen)
        pieces.append(piece)
    return pieces

def draw_board(board):
    board.draw()

def draw_pieces(pieces, screen):
    for piece in pieces:
        piece.draw(screen)

import pygame

def draw_buttons(screen):
    font = pygame.font.SysFont('Verdana', 20)
    button_x = Config.WINDOW_SIZE + Config.GAP * 2 + 50

    dfs_button = pygame.Rect(button_x, Config.GAP, 150, 50)
    bfs_button = pygame.Rect(button_x, Config.GAP + 70, 150, 50)
    a_star_button = pygame.Rect(button_x, Config.GAP + 140, 150, 50)
    minimax_button = pygame.Rect(button_x, Config.GAP + 210, 150, 50)
    alpha_beta_button = pygame.Rect(button_x, Config.GAP + 280, 150, 50)

    buttons = [
        (dfs_button, "DFS"),
        (bfs_button, "BFS"),
        (a_star_button, "A*"),
        (minimax_button, "Minimax"),
        (alpha_beta_button, "Alpha-Beta")
    ]

    mouse_x, mouse_y = pygame.mouse.get_pos()

    for button, text in buttons:
        if button.collidepoint(mouse_x, mouse_y):
            button_color = (150, 150, 150)
        else:
            button_color = (200, 200, 200)

        pygame.draw.rect(screen, button_color, button)
        button_text = font.render(text, True, (0, 0, 0))
        screen.blit(button_text, (button.x + 25, button.y + 15))

    return {text: button for button, text in buttons}


def main():
    initialize_game()
    fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
    puzzle_positions, current_player = get_puzzle_positions(fen)

    screen = pygame.display.set_mode((Config.WINDOW_SIZE + Config.GAP * 2 + 300, Config.WINDOW_SIZE + Config.GAP * 2))
    piece_images = load_piece_images()
    pieces = create_pieces(puzzle_positions, piece_images, screen)
    board = Chess_Board(screen, pieces, current_player)

    board_state = board.get_board_state()
    solver = PuzzleSolver(board_state)

    solver_methods = {
        "DFS": solver.dfs,
        "BFS": solver.bfs,
        "A*": solver.a_star,
        "Minimax": lambda: solver.minimax(depth=3),  # Example depth value
        "Alpha-Beta": lambda: solver.minimax_with_pruning(depth=3),  # Example depth value
    }

    draw_board(board)
    draw_pieces(pieces, screen)
    buttons = draw_buttons(screen)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for algorithm, button in buttons.items():
                    if button.collidepoint(event.pos):
                        result = solver_methods[algorithm]()
                        print(f"{algorithm} result: {result}")

        screen.fill((255, 255, 255))
        draw_board(board)
        draw_pieces(pieces, screen)
        buttons = draw_buttons(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

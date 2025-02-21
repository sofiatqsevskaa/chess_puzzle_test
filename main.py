import time
from board import Board as Chess_Board
from fen_to_positions import fen_to_dict
from piece import Piece
from solver import *


def initialize_game():
    pygame.init()
    pygame.display.set_caption("Chess Board")


def get_puzzle_positions(fen):
    return fen_to_dict(fen)


def load_piece_images():
    path = "chess_puzzle_test/assets/"
    piece_images = {
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
    for key in piece_images:
        piece_images[key] = pygame.transform.smoothscale(
            piece_images[key], (Config.TILE_SIZE, Config.TILE_SIZE))
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


def display_moves(screen, moves, winner=None):
    font = pygame.font.SysFont('Verdana', 16)
    pos_x, pos_y, offset_y, offset_x = 700, 450, 60, 250
    winner_text = f"{winner} won!"
    if winner:
        screen.blit(font.render(winner_text, True, (0, 0, 0)),
                    (700, 400))
    for i, move in enumerate(moves):
        move_text = f"{move[0]} {move[1]} -> {move[2]}"
        if "white" in move[0]:
            offset_x = 0
        else:
            offset_x = 250
        screen.blit(font.render(move_text, True, (0, 0, 0)),
                    (pos_x + offset_x, pos_y + i//2 * offset_y))


def parse_fen_with_mate(file):
    with open(file, "r") as f:
        line = f.readline().strip()

    fen, moves_until_mate = line.split(";")
    moves_until_mate = int(moves_until_mate)

    return fen, moves_until_mate


def main():
    initialize_game()

    fen, moves_until_mate = parse_fen_with_mate(
        "chess_puzzle_test/position5.txt")

    puzzle_positions, current_player = get_puzzle_positions(
        fen)

    screen = pygame.display.set_mode(
        (Config.WINDOW_SIZE + Config.GAP * 2 + 600, Config.WINDOW_SIZE + Config.GAP * 2))
    piece_images = load_piece_images()
    pieces = create_pieces(puzzle_positions, piece_images, screen)
    board = Chess_Board(screen, pieces, current_player)

    draw_board(board)
    draw_pieces(pieces, screen)
    buttons = draw_buttons(screen)
    pygame.display.flip()

    moves = []
    running = True
    move_set = []

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for algorithm, button in buttons.items():
                    if button.collidepoint(event.pos):
                        if algorithm == "DFS":
                            sequence = []
                            moves = []
                            start_time = time.time()
                            move_set, new_board = dfs(
                                board, 0, moves_until_mate, current_player, sequence, moves)

                            board = new_board
                            end_time = time.time()
                            duration_time = round(end_time - start_time, 2)

                        elif algorithm == "BFS":
                            sequence = []
                            moves = []
                            start_time = time.time()
                            move_set, new_board = bfs(
                                board, moves_until_mate/2, current_player, sequence, moves)

                            board = new_board
                            end_time = time.time()
                            duration_time = round(end_time - start_time, 2)

                        elif algorithm == "Minimax":
                            sequence = []
                            moves = []
                            start_time = time.time()
                            if moves_until_mate == 1:
                                moves_until_mate = 2
                            move_set_c, new_fen = minmaxing(
                                board, moves_until_mate/2, current_player)
                            board.load_fen(new_fen)
                            end_time = time.time()
                            duration_time = round(end_time - start_time, 2)

                            for move in move_set_c:
                                move_set.append((
                                    move[0].piece_type, move[0].position, move[1]))

        screen.fill((255, 255, 255))
        draw_board(board)
        # print(move_set)
        draw_pieces(board.pieces, screen)
        buttons = draw_buttons(screen)
        # print(board.winner)
        display_moves(screen, move_set, board.winner)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()

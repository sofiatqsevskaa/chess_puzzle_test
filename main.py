import pygame
from config import Config
from board import screen, Board as Chess_Board
from fen_to_positions import fen_to_dict
from piece import Piece


def initialize_game():
    pygame.init()
    pygame.display.set_caption("Chess Board")


def get_puzzle_positions(fen):
    return fen_to_dict(fen)

def load_piece_images():
    path ="assets/"
    piece_images = {
        "white pawn": pygame.image.load(path+"white pawn.png"),
        "black pawn": pygame.image.load(path+"black pawn.png"),
        "white rook": pygame.image.load(path+"white rook.png"),
        "black rook": pygame.image.load(path+"black rook.png"),
        "white knight": pygame.image.load(path+"white knight.png"),
        "black knight": pygame.image.load(path+"black knight.png"),
        "white bishop": pygame.image.load(path+"white bishop.png"),
        "black bishop": pygame.image.load(path+"black bishop.png"),
        "white queen": pygame.image.load(path+"white queen.png"),
        "black queen": pygame.image.load(path+"black queen.png"),
        "white king": pygame.image.load(path+"white king.png"),
        "black king": pygame.image.load(path+"black king.png"),
    }
    for key in piece_images:
        piece_images[key] = pygame.transform.scale(piece_images[key], (Config.TILE_SIZE, Config.TILE_SIZE))
    return piece_images


def create_pieces(puzzle_positions, piece_images):
    pieces = []
    for position, piece_info in puzzle_positions.items():
        color, piece_type = piece_info.split()
        x, y = position
        image = piece_images.get(f"{color} {piece_type}")
        piece = Piece(piece_type, color, (x, y), image)
        pieces.append(piece)
    return pieces


def draw_board_and_pieces(board, pieces):
        board.draw()
        for piece in pieces:
            piece.draw(screen)


def main():
    initialize_game()
    fen = "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2"
    fen1 = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

    #CHANGE FEN
    puzzle_positions = get_puzzle_positions(fen1)

    piece_images = load_piece_images()
    board = Chess_Board()
    pieces = create_pieces(puzzle_positions, piece_images)

    draw_board_and_pieces(board, pieces)
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

    pygame.quit()


if __name__ == "__main__":
    main()

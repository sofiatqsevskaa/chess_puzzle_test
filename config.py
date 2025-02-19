class Config:
    WINDOW_SIZE = 640
    TILE_SIZE = WINDOW_SIZE // 8
    PIECE_SIZE = 60
    YELLOW = (245, 215, 142)
    BROWN = (142, 83, 18)
    BLACK = (0, 0, 0)
    GAP = 25
    SCALED_SIZE = 60
    ASSETS_FOLDER = "assets"
    PIECE_VALUES = {
        'pawn': 1, 'knight': 3, 'bishop': 3, 'rook': 5, 'queen': 9, 'king': 0
    }

import pygame
from config import Config  # Make sure Config is properly imported
from board import *

pygame.init()

pygame.display.set_caption("Chess Board")

board = Board()

board.draw()
pygame.display.flip()
running = True


while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False


pygame.quit()

"""
Trivia Game - Portfolio Project
A quiz game using the Open Trivia Database API
"""

import pygame
import sys
from game_ui import TriviaGame

# Initialize Pygame
pygame.init()

# Set up the display
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 810
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Trivia Challenge')

# Set icon (optional)
try:
    icon = pygame.image.load('icon.png')
    pygame.display.set_icon(icon)
except:
    pass  # Icon not required

# Initialize and run game
def main():
    game = TriviaGame(screen)
    game.run()

if __name__ == "__main__":
    main()
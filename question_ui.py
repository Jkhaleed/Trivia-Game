import pygame
from constants import *


class Question(pygame.sprite.Sprite):
    """Sprite for displaying a quiz question."""

    def __init__(self, question, font, x, y):
        super().__init__()
        self.font = font
        self.image = pygame.Surface((SCREEN_WIDTH - 40, 200), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.render_question(question)

    def render_question(self, question):
        """Render the question text on the surface."""
        self.image.fill((0, 0, 0, 0))  # Clear surface
        self.render_text(question['question'], self.font,
                         self.image, BRIGHT_COLOR, 10, 60)

    def render_text(self, text, font, surface, color, x, y):
        """
        Render multi-line text with word wrapping.

        Args:
            text: Text to render
            font: Pygame font object
            surface: Surface to render on
            color: Text color
            x, y: Starting position
        """
        words = text.split(' ')
        lines = []
        current_line = []

        # Word wrap
        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = font.render(test_line, True, color)

            if text_surface.get_width() <= surface.get_width() - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Render lines
        y_offset = y
        for line in lines:
            text_surface = font.render(line, True, color)
            surface.blit(text_surface, (x, y_offset))
            y_offset += font.get_height() + 5
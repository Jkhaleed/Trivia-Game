import pygame
from constants import *


class JeopardyBoard:
    """Interactive Jeopardy-style board for selecting questions."""

    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font

        # Islamic categories
        self.categories = ['Quran', 'Seerah', 'Dua And Dhikr', 'Salah', 'Prophets']
        self.point_values = [100, 200, 300, 400, 500, 600, 700]

        # Track which questions have been answered
        self.answered_questions = set()  # Store tuples of (category, points)

        # Board dimensions
        self.cell_width = 200
        self.cell_height = 80
        self.start_x = 50
        self.start_y = 150

        # Colors
        self.cell_color = (0, 50, 100)
        self.hover_color = (0, 100, 200)
        self.answered_color = (30, 30, 30)
        self.text_color = BRIGHT_COLOR
        self.answered_text_color = GRAY

    def draw_board(self, mouse_pos):
        """Draw the Jeopardy board with categories and point values."""
        # Title
        title_font = pygame.font.Font(None, 56)
        title_text = title_font.render('Islamic Trivia Challenge', True, BRIGHT_COLOR)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)

        # Draw category headers
        for col, category in enumerate(self.categories):
            x = self.start_x + col * self.cell_width
            y = self.start_y

            # Category header
            header_rect = pygame.Rect(x, y, self.cell_width - 10, self.cell_height - 10)
            pygame.draw.rect(self.screen, PURPLE, header_rect, border_radius=10)
            pygame.draw.rect(self.screen, BRIGHT_COLOR, header_rect, 3, border_radius=10)

            # Category text (word wrap if needed)
            self.draw_wrapped_text(category, self.small_font, WHITE, header_rect)

        # Draw point value cells
        for row, points in enumerate(self.point_values):
            for col, category in enumerate(self.categories):
                x = self.start_x + col * self.cell_width
                y = self.start_y + (row + 1) * self.cell_height

                cell_rect = pygame.Rect(x, y, self.cell_width - 10, self.cell_height - 10)

                # Check if question has been answered
                is_answered = (category, points) in self.answered_questions

                # Determine cell color
                if is_answered:
                    cell_color = self.answered_color
                    text_color = self.answered_text_color
                    border_color = GRAY
                elif cell_rect.collidepoint(mouse_pos):
                    cell_color = self.hover_color
                    text_color = WHITE
                    border_color = BRIGHT_COLOR
                else:
                    # Color code by difficulty
                    if points <= 200:
                        cell_color = (0, 100, 0)  # Green
                    elif points <= 400:
                        cell_color = (150, 150, 0)  # Yellow
                    elif points == 500:
                        cell_color = (200, 100, 0)  # Orange
                    else:
                        cell_color = (150, 0, 0)  # Red
                    text_color = self.text_color
                    border_color = WHITE

                # Draw cell
                pygame.draw.rect(self.screen, cell_color, cell_rect, border_radius=10)
                pygame.draw.rect(self.screen, border_color, cell_rect, 3, border_radius=10)

                # Draw points text or checkmark if answered
                if is_answered:
                    text = "✓"
                    font_to_use = self.font
                else:
                    text = str(points)
                    font_to_use = self.font

                text_surface = font_to_use.render(text, True, text_color)
                text_rect = text_surface.get_rect(center=cell_rect.center)
                self.screen.blit(text_surface, text_rect)

        # Draw stats at bottom
        total_possible = len(self.categories) * len(self.point_values)
        answered = len(self.answered_questions)
        remaining = total_possible - answered

        stats_y = self.start_y + (len(self.point_values) + 1) * self.cell_height + 20
        stats_text = f"Questions Answered: {answered} / {total_possible}  •  Remaining: {remaining}"
        stats_surface = self.font.render(stats_text, True, WHITE)
        stats_rect = stats_surface.get_rect(center=(SCREEN_WIDTH // 2, stats_y))
        self.screen.blit(stats_surface, stats_rect)

    def draw_wrapped_text(self, text, font, color, rect):
        """Draw text with word wrapping within a rectangle."""
        words = text.split()
        lines = []
        current_line = []

        for word in words:
            test_line = ' '.join(current_line + [word])
            text_surface = font.render(test_line, True, color)

            if text_surface.get_width() <= rect.width - 20:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                current_line = [word]

        if current_line:
            lines.append(' '.join(current_line))

        # Center lines vertically and horizontally
        total_height = len(lines) * font.get_height()
        y_offset = rect.y + (rect.height - total_height) // 2

        for line in lines:
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(rect.centerx, y_offset + font.get_height() // 2))
            self.screen.blit(text_surface, text_rect)
            y_offset += font.get_height()

    def get_clicked_question(self, pos):
        """
        Get the category and points value that was clicked.
        Returns (category, points) tuple or None.
        """
        for row, points in enumerate(self.point_values):
            for col, category in enumerate(self.categories):
                x = self.start_x + col * self.cell_width
                y = self.start_y + (row + 1) * self.cell_height

                cell_rect = pygame.Rect(x, y, self.cell_width - 10, self.cell_height - 10)

                if cell_rect.collidepoint(pos):
                    # Check if already answered
                    if (category, points) not in self.answered_questions:
                        return (category, points)

        return None

    def mark_answered(self, category, points):
        """Mark a question as answered."""
        self.answered_questions.add((category, points))

    def is_board_complete(self):
        """Check if all questions have been answered."""
        total_questions = len(self.categories) * len(self.point_values)
        return len(self.answered_questions) >= total_questions

    def reset_board(self):
        """Reset the board for a new game."""
        self.answered_questions.clear()

    def get_questions_answered(self):
        """Get the number of questions answered."""
        return len(self.answered_questions)

    def get_total_questions(self):
        """Get total number of questions on the board."""
        return len(self.categories) * len(self.point_values)
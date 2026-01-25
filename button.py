import pygame


class Button(pygame.sprite.Sprite):
    """Basic button for menu selections."""

    def __init__(self, x, y, width, height, text, font, bg_color, text_color, action):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.text = text
        self.font = font
        self.bg_color = bg_color
        self.text_color = text_color
        self.action = action
        self.render_text()

    def render_text(self):
        """Render button background and centered text."""
        self.image.fill(self.bg_color)
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=(self.rect.width // 2, self.rect.height // 2))
        self.image.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        """Check if button was clicked at given position."""
        return self.rect.collidepoint(pos)

    def draw(self, surface):
        """Draw button on surface."""
        surface.blit(self.image, self.rect.topleft)


class OptionButton(pygame.sprite.Sprite):
    """Button for quiz answer options with hover effect."""

    def __init__(self, x, y, width, height, text, font, bg_color, fg_color, hover_color):
        super().__init__()
        self.bg_color = bg_color
        self.fg_color = fg_color
        self.hover_color = hover_color
        self.default_color = bg_color
        self.text = text
        self.font = font
        self.width = width
        self.height = height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.is_hovered = False
        self.render_button()

    def render_button(self):
        """Render button with current color state."""
        self.image.fill((0, 0, 0, 0))  # Clear surface
        current_color = self.hover_color if self.is_hovered else self.default_color

        # Draw rounded rectangle
        pygame.draw.rect(self.image, current_color,
                         self.image.get_rect(), border_radius=10)

        # Render text
        text_surf = self.font.render(self.text, True, self.fg_color)
        text_rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.image.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        """Check if button was clicked at given position."""
        return self.rect.collidepoint(pos)

    def update(self, mouse_pos):
        """Update button hover state based on mouse position."""
        self.is_hovered = self.is_clicked(mouse_pos)
        self.render_button()
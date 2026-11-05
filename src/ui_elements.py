"""Shared theme colors and widgets used by the Photon screens."""

import pygame

# Shared theme colors used by every screen
BACKGROUND = (8, 8, 10)
PANEL = (22, 22, 28)
TEXT = (235, 235, 235)
MUTED_TEXT = (165, 165, 170)
BORDER = (80, 80, 90)

INPUT_BG = (245, 245, 245)
INPUT_TEXT = (25, 25, 25)
INPUT_DISABLED = (195, 195, 195)
BLUE = (80, 105, 255)


class TextInput:
    def __init__(self, rect: pygame.Rect, placeholder: str, numeric_only: bool = False, max_length: int = 20, enabled=True):
        self.rect = rect
        self.placeholder = placeholder
        self.numeric_only = numeric_only
        self.max_length = max_length
        self.text = ""
        self.active = False
        self.enabled = enabled

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
        elif event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in (pygame.K_RETURN, pygame.K_TAB):
                self.active = False
            elif len(self.text) < self.max_length and event.unicode and event.unicode.isprintable():
                if not self.numeric_only or event.unicode.isdigit():
                    self.text += event.unicode

    def draw(self, surface: pygame.Surface, font: pygame.font.Font) -> None:
        if self.enabled:
            pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=4)
            if self.text:
                value = self.text
                color = INPUT_TEXT
            else:
                value = self.placeholder
                color = (125, 125, 125)
        else:
            pygame.draw.rect(surface, INPUT_DISABLED, self.rect, border_radius=4)
            value = "UNAVAILABLE"
            color = (125, 125, 125)
            
        pygame.draw.rect(surface, BLUE if self.active else BORDER, self.rect, 2, border_radius=4)
        
        rendered = font.render(value, True, color)
        surface.blit(rendered, (self.rect.x + 12, self.rect.centery - rendered.get_height() // 2))


class Button:
    def __init__(self, rect: pygame.Rect, text: str, normal, hover):
        self.rect = rect
        self.text = text
        self.normal = normal
        self.hover = hover

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, mouse_pos) -> None:
        color = self.hover if self.rect.collidepoint(mouse_pos) else self.normal
        pygame.draw.rect(surface, color, self.rect, border_radius=6)
        pygame.draw.rect(surface, BORDER, self.rect, 1, border_radius=6)
        label = font.render(self.text, True, TEXT)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def clicked(self, event: pygame.event.Event) -> bool:
        return (
            event.type == pygame.MOUSEBUTTONDOWN
            and event.button == 1
            and self.rect.collidepoint(event.pos)
        )

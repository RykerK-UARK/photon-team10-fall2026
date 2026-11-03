"""Screen manager for the Photon application.

This file owns the Pygame window, the clock, and the main loop. Each screen
(splash, player entry, countdown, play action) is a Screen subclass that only
draws itself and reports which screen should come next.
"""

from typing import Optional

import pygame

from ui_elements import BACKGROUND, TEXT, MUTED_TEXT

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
FPS = 60


class Screen:
    """Base class for every screen. Subclasses override what they need."""

    caption = "Photon"

    def __init__(self, manager: "ScreenManager"):
        self.manager = manager
        self.screen = manager.screen
        self.title_font = manager.title_font
        self.small_font = manager.small_font

    def draw_background(self) -> None:
        self.screen.fill(BACKGROUND)

    def draw_header(self, title_text: str, subtitle_text: str) -> None:
        """Title and subtitle shared by the player-entry and play-action screens."""
        title = self.title_font.render(title_text, True, TEXT)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 62)))
        subtitle = self.small_font.render(subtitle_text, True, MUTED_TEXT)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 98)))

    def on_enter(self) -> None:
        """Called each time this screen becomes the active screen."""

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Return a screen name (or 'quit') to switch, otherwise None."""
        return None

    def update(self) -> Optional[str]:
        """Called once per frame. Return a screen name (or 'quit') to switch."""
        return None

    def draw(self) -> None:
        """Draw this screen. The manager flips the display afterwards."""


class ScreenManager:
    """Runs the one Pygame loop and switches between registered screens."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        # Fonts shared by every screen
        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.small_font = pygame.font.SysFont("arial", 16)

        # Roster shared by every screen so it survives screen changes.
        self.players: list = []

        self.screens: dict[str, Screen] = {}
        self.current: Optional[Screen] = None
        self.running = False

    def register(self, name: str, screen: Screen) -> None:
        self.screens[name] = screen

    def switch_to(self, name: str) -> None:
        if name == "quit":
            self.running = False
            return
        self.current = self.screens[name]
        pygame.display.set_caption(self.current.caption)
        self.current.on_enter()

    def run(self, start_name: str) -> None:
        self.running = True
        self.switch_to(start_name)

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break
                next_screen = self.current.handle_event(event)
                if next_screen:
                    self.switch_to(next_screen)
                    if not self.running:
                        break

            if not self.running:
                break

            next_screen = self.current.update()
            if next_screen:
                self.switch_to(next_screen)

            self.current.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

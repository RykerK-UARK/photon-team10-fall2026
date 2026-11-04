"""Pre-game countdown screen, independent of the play-action display.

Flow: player entry -> countdown -> play action.

This screen is intentionally self-contained so the team can replace its
simple text countdown with images, sounds, or a more elaborate countdown
without changing the player-entry screen or the play-action screen.
"""

from typing import Optional

import pygame

from screen_manager import Screen
from ui_elements import BACKGROUND, PANEL, TEXT, MUTED_TEXT, BORDER


COUNTDOWN_SECONDS = 30


class GameCountdown(Screen):
    """Display the countdown, then hand control to the next screen.

    Returns (through handle_event/update):
        'play_action':   countdown finished (or SPACE pressed for testing).
        'player_entry':  ESC pressed; return to player entry without starting.

    Don't call pygame.init(), set_mode(), or pygame.quit() here: all screens
    share the application's existing Pygame window.
    """

    caption = "Photon - Game Countdown"

    def __init__(self, manager, seconds: int = COUNTDOWN_SECONDS):
        super().__init__(manager)
        self.seconds = seconds
        self.heading_font = pygame.font.SysFont("arial", 38, bold=True)
        self.number_font = pygame.font.SysFont("arial", 128, bold=True)
        self.hint_font = pygame.font.SysFont("arial", 20)
        self.started_at_ms = 0

    def on_enter(self) -> None:
        # Restart the countdown every time this screen is opened.
        self.started_at_ms = pygame.time.get_ticks()

    def _remaining(self) -> int:
        # Use real elapsed milliseconds instead of assuming a fixed frame rate.
        elapsed_ms = max(0, pygame.time.get_ticks() - self.started_at_ms)
        return max(0, self.seconds - elapsed_ms // 1000)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "player_entry"
        # SPACE skips the countdown (for testing).
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return "play_action"
        return None

    def update(self) -> Optional[str]:
        if self._remaining() == 0:
            return "play_action"
        return None

    def draw(self) -> None:
        width, height = self.screen.get_size()
        self.screen.fill(BACKGROUND)

        panel = pygame.Rect(0, 0, 650, 360)
        panel.center = (width // 2, height // 2)
        pygame.draw.rect(self.screen, PANEL, panel, border_radius=14)
        pygame.draw.rect(self.screen, BORDER, panel, width=2, border_radius=14)

        heading = self.heading_font.render("GAME STARTS IN", True, TEXT)
        self.screen.blit(heading, heading.get_rect(center=(width // 2, height // 2 - 105)))

        number = self.number_font.render(f"00:{self._remaining():02d}", True, TEXT)
        self.screen.blit(number, number.get_rect(center=(width // 2, height // 2 + 10)))

        hint = self.hint_font.render("ESC = Return to Player Entry", True, MUTED_TEXT)
        self.screen.blit(hint, hint.get_rect(center=(width // 2, height // 2 + 135)))

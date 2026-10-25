"""Sprint 3 play-action display with a non-blocking 30-second countdown.

The player-entry screen passes its current Player objects into this screen.
This screen only displays the rosters and countdown: scoring/events are future work.
"""

import pygame

# Overall window and timer configuration for the play-action screen.
WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
FPS = 60
COUNTDOWN_SECONDS = 30

# Simple palette used throughout the UI so the game view is easy to scan.
BACKGROUND = (8, 8, 10)
PANEL = (22, 22, 28)
TEXT = (235, 235, 235)
MUTED = (165, 165, 170)
RED = (210, 59, 67)
GREEN = (80, 205, 113)
BORDER = (80, 80, 90)


class PlayActionScreen:
    """Draw the countdown and both team lists in the existing Pygame window."""

    def __init__(self, players, screen: pygame.Surface, clock: pygame.time.Clock):
        # Keep a local, ordered copy of the player roster so this screen can
        # render team membership without mutating the original collection.
        self.players = list(players)
        self.screen = screen
        self.clock = clock
        # None until the screen starts its countdown timer.
        self.started_at_ms = None

        # Preload fonts once so each frame does not have to create new surface
        # objects for text rendering.
        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.heading_font = pygame.font.SysFont("arial", 27, bold=True)
        self.timer_font = pygame.font.SysFont("arial", 94, bold=True)
        self.player_font = pygame.font.SysFont("arial", 19)
        self.small_font = pygame.font.SysFont("arial", 17)

        # Bottom navigation/control area for returning to the previous screen.
        self.back_button = pygame.Rect(32, 656, 232, 45)

    def seconds_remaining(self, now_ms=None) -> int:
        """Calculate the seconds left without stopping the Pygame event loop."""
        # If the countdown has not started yet, the full 30-second window remains.
        if self.started_at_ms is None:
            return COUNTDOWN_SECONDS

        if now_ms is None:
            now_ms = pygame.time.get_ticks()

        # Quantize elapsed time to full seconds so the counter behaves like a
        # typical game timer rather than a floating-point clock.
        elapsed_ms = max(0, now_ms - self.started_at_ms)
        return max(0, COUNTDOWN_SECONDS - elapsed_ms // 1000)

    def _draw_team(self, team: str, rect: pygame.Rect, accent) -> None:
        # Draw the panel and a subtle border to visually separate the red and green
        # team rosters from the rest of the play-action layout.
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=12)
        pygame.draw.rect(self.screen, accent, rect, width=2, border_radius=12)
        heading = self.heading_font.render(f"{team.upper()} TEAM", True, accent)
        self.screen.blit(heading, heading.get_rect(center=(rect.centerx, rect.y + 30)))

        # Create a roster list for the selected team only.
        players = [p for p in self.players if p.team == team]
        count = self.small_font.render(f"{len(players)} player(s)", True, MUTED)
        self.screen.blit(count, count.get_rect(center=(rect.centerx, rect.y + 65)))

        if not players:
            empty = self.player_font.render("No players assigned", True, MUTED)
            self.screen.blit(empty, empty.get_rect(center=(rect.centerx, rect.y + 126)))
            return

        # Limit the visible list to six entries to keep the panel readable while
        # still showing the most relevant players in the first view.
        for index, player in enumerate(players[:6], start=1):
            player_text = f"{index}.  {player.codename}    ID: {player.equipment_id}"
            line = self.player_font.render(player_text, True, TEXT)
            self.screen.blit(line, (rect.x + 24, rect.y + 92 + (index - 1) * 29))

        if len(players) > 6:
            remaining = self.small_font.render(
                f"+ {len(players) - 6} additional player(s)", True, MUTED
            )
            self.screen.blit(remaining, (rect.x + 24, rect.bottom - 27))

    def draw(self, now_ms=None) -> None:
        """Render one frame. The roster stays visible during the countdown."""
        # Clear the frame and paint the background for each redraw.
        self.screen.fill(BACKGROUND)

        title = self.title_font.render("PHOTON PLAY ACTION", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 49)))
        subtitle = self.small_font.render("Sprint 3 - Team Roster", True, MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 87)))

        # Large timer panel in the center of the screen; updates every frame.
        timer_rect = pygame.Rect(345, 115, 410, 197)
        pygame.draw.rect(self.screen, PANEL, timer_rect, border_radius=12)
        pygame.draw.rect(self.screen, BORDER, timer_rect, width=2, border_radius=12)

        remaining = self.seconds_remaining(now_ms)
        if remaining > 0:
            caption = "GAME STARTS IN"
            timer_value = f"00:{remaining:02d}"
            timer_color = TEXT
        else:
            caption = "GAME STARTED"
            timer_value = "GO!"
            timer_color = GREEN

        caption_text = self.small_font.render(caption, True, MUTED)
        self.screen.blit(caption_text, caption_text.get_rect(center=(550, 153)))
        countdown_text = self.timer_font.render(timer_value, True, timer_color)
        self.screen.blit(countdown_text, countdown_text.get_rect(center=(550, 226)))

        # Team panels are anchored below the timer and show the roster for each side.
        self._draw_team("Red", pygame.Rect(45, 334, 488, 303), RED)
        self._draw_team("Green", pygame.Rect(567, 334, 488, 303), GREEN)

        # Bottom navigation button and status text at the far right.
        mouse_over = self.back_button.collidepoint(pygame.mouse.get_pos())
        pygame.draw.rect(
            self.screen, (78, 82, 92) if mouse_over else (55, 58, 67),
            self.back_button, border_radius=7
        )
        back_label = self.small_font.render("BACK TO ENTRY (ESC)", True, TEXT)
        self.screen.blit(back_label, back_label.get_rect(center=self.back_button.center))
        status = self.small_font.render("No game events yet", True, MUTED)
        self.screen.blit(status, status.get_rect(midright=(1060, 679)))

    def run(self) -> str:
        """Return 'back' or 'quit' to the player-entry screen."""
        # Start the countdown when this screen enters its main loop.
        pygame.display.set_caption("Photon - Play Action")
        self.started_at_ms = pygame.time.get_ticks()

        while True:
            # Handle keyboard, mouse, and close events before drawing the frame.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return "back"
                if (event.type == pygame.MOUSEBUTTONDOWN
                        and event.button == 1
                        and self.back_button.collidepoint(event.pos)):
                    return "back"

            self.draw()
            pygame.display.flip()
            self.clock.tick(FPS)

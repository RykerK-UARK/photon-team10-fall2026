"""Sprint 3 play-action display (no countdown logic).

This screen is shown only after countdown.run_countdown() has completed.
It displays the team rosters; scoring/events are future work.
"""

import pygame

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
FPS = 60

BACKGROUND = (8, 8, 10)
PANEL = (22, 22, 28)
TEXT = (235, 235, 235)
MUTED = (165, 165, 170)
RED = (210, 59, 67)
GREEN = (80, 205, 113)
BORDER = (80, 80, 90)


class PlayActionScreen:
    """Draw both team lists in the existing Pygame window."""

    def __init__(self, players, screen: pygame.Surface, clock: pygame.time.Clock):
        self.players = list(players)
        self.screen = screen
        self.clock = clock

        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.heading_font = pygame.font.SysFont("arial", 27, bold=True)
        self.player_font = pygame.font.SysFont("arial", 19)
        self.small_font = pygame.font.SysFont("arial", 17)
        self.back_button = pygame.Rect(32, 656, 232, 45)

    def _draw_team(self, team: str, rect: pygame.Rect, accent) -> None:
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=12)
        pygame.draw.rect(self.screen, accent, rect, width=2, border_radius=12)
        heading = self.heading_font.render(f"{team.upper()} TEAM", True, accent)
        self.screen.blit(heading, heading.get_rect(center=(rect.centerx, rect.y + 30)))

        players = [p for p in self.players if p.team == team]
        count = self.small_font.render(f"{len(players)} player(s)", True, MUTED)
        self.screen.blit(count, count.get_rect(center=(rect.centerx, rect.y + 65)))

        if not players:
            empty = self.player_font.render("No players assigned", True, MUTED)
            self.screen.blit(empty, empty.get_rect(center=(rect.centerx, rect.y + 126)))
            return

        for index, player in enumerate(players[:10], start=1):
            player_text = f"{index}.  {player.codename}    eID: {player.equipment_id}"
            line = self.player_font.render(player_text, True, TEXT)
            self.screen.blit(line, (rect.x + 24, rect.y + 92 + (index - 1) * 29))

        if len(players) > 10:
            remaining = self.small_font.render(
                f"+ {len(players) - 10} additional player(s)", True, MUTED
            )
            self.screen.blit(remaining, (rect.x + 24, rect.bottom - 27))

    def draw(self) -> None:
        """Render team rosters only; the countdown has already finished."""
        self.screen.fill(BACKGROUND)
        title = self.title_font.render("PHOTON PLAY ACTION", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 49)))
        subtitle = self.small_font.render("Game started - no events yet", True, MUTED)
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 87)))

        # The rosters now have the space previously occupied by the timer.
        self._draw_team("Red", pygame.Rect(45, 137, 488, 494), RED)
        self._draw_team("Green", pygame.Rect(567, 137, 488, 494), GREEN)

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
        pygame.display.set_caption("Photon - Play Action")
        while True:
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

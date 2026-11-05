"""Sprint 3 play-action display (no countdown logic).

This screen is shown only after countdown.run_countdown() has completed.
It displays the team rosters; scoring/events are future work.
"""

from typing import Optional

import pygame

from screen_manager import Screen
from ui_elements import Button, PANEL, TEXT, MUTED_TEXT

RED = (210, 59, 67)
GREEN = (80, 205, 113)


class PlayActionScreen(Screen):
    """Draw both team lists in the existing Pygame window."""

    caption = "Photon - Play Action"

    def __init__(self, manager):
        super().__init__(manager)
        self.players = []

        self.heading_font = pygame.font.SysFont("arial", 27, bold=True)
        self.player_font = pygame.font.SysFont("arial", 19)
        self.back_button = Button(pygame.Rect(32, 656, 232, 45), "BACK TO ENTRY (ESC)", (55, 58, 67), (78, 82, 92))

    def on_enter(self) -> None:
        # Take a snapshot of the roster when the game starts.
        self.players = list(self.manager.players)

    def _draw_team(self, team: str, rect: pygame.Rect, accent) -> None:
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=12)
        pygame.draw.rect(self.screen, accent, rect, width=2, border_radius=12)
        heading = self.heading_font.render(f"{team.upper()} TEAM", True, accent)
        self.screen.blit(heading, heading.get_rect(center=(rect.centerx, rect.y + 30)))

        players = [p for p in self.players if p.team == team]
        count = self.small_font.render(f"{len(players)} player(s)", True, MUTED_TEXT)
        self.screen.blit(count, count.get_rect(center=(rect.centerx, rect.y + 65)))

        if not players:
            empty = self.player_font.render("No players assigned", True, MUTED_TEXT)
            self.screen.blit(empty, empty.get_rect(center=(rect.centerx, rect.y + 126)))
            return

        for index, player in enumerate(players[:10], start=1):
            player_text = f"{index}.  {player.codename}    eID: {player.equipment_id}"
            line = self.player_font.render(player_text, True, TEXT)
            self.screen.blit(line, (rect.x + 24, rect.y + 92 + (index - 1) * 29))

        if len(players) > 10:
            remaining = self.small_font.render(
                f"+ {len(players) - 10} additional player(s)", True, MUTED_TEXT
            )
            self.screen.blit(remaining, (rect.x + 24, rect.bottom - 27))

    def draw(self) -> None:
        """Render team rosters only; the countdown has already finished."""
        self.draw_background()
        self.draw_header("PHOTON PLAY ACTION", "Game started - no events yet")

        # The rosters now have the space previously occupied by the timer.
        self._draw_team("Red", pygame.Rect(45, 137, 488, 494), RED)
        self._draw_team("Green", pygame.Rect(567, 137, 488, 494), GREEN)

        self.back_button.draw(self.screen, self.small_font, pygame.mouse.get_pos())
        status = self.small_font.render("No game events yet", True, MUTED_TEXT)
        self.screen.blit(status, status.get_rect(midright=(1060, 679)))

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Return 'player_entry' to go back to the player-entry screen."""
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "player_entry"
        if self.back_button.clicked(event):
            return "player_entry"
        return None

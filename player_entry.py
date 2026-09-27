"""Photon player-entry screen for Sprint 2.

This module contains the user interface for entering players before a game.
It intentionally keeps database/UDP logic outside of the UI so the team's
existing database and socket code can be connected with ``on_player_added``.
"""

from dataclasses import dataclass
from typing import Callable, Optional

import pygame


WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
FPS = 60

BACKGROUND = (8, 8, 10)
PANEL = (22, 22, 28)
TEXT = (235, 235, 235)
MUTED_TEXT = (165, 165, 170)
BORDER = (80, 80, 90)
INPUT_BG = (245, 245, 245)
INPUT_TEXT = (25, 25, 25)
RED = (135, 26, 32)
RED_HOVER = (170, 34, 41)
GREEN = (31, 112, 53)
GREEN_HOVER = (40, 142, 67)
BLUE = (80, 105, 255)
ERROR = (235, 95, 95)
SUCCESS = (100, 220, 130)


@dataclass
class Player:
    equipment_id: int
    codename: str
    team: str


class TextInput:
    def __init__(self, rect: pygame.Rect, placeholder: str, numeric_only: bool = False, max_length: int = 20):
        self.rect = rect
        self.placeholder = placeholder
        self.numeric_only = numeric_only
        self.max_length = max_length
        self.text = ""
        self.active = False

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
        pygame.draw.rect(surface, INPUT_BG, self.rect, border_radius=4)
        pygame.draw.rect(surface, BLUE if self.active else BORDER, self.rect, 2, border_radius=4)
        if self.text:
            value = self.text
            color = INPUT_TEXT
        else:
            value = self.placeholder
            color = (125, 125, 125)
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


class PlayerEntryScreen:
    """Pygame UI for adding players to red and green teams.

    ``on_player_added`` is called after a player passes validation.  The team
    can use that callback to insert the player into PostgreSQL and broadcast
    the equipment code over UDP without putting database/socket code in this
    UI file.
    """

    def __init__(self, on_player_added: Optional[Callable[[Player], None]] = None, on_ip_changed: Optional[Callable[[None], bool]] = None):
        pygame.init()
        pygame.display.set_caption("Photon - Player Entry")
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.clock = pygame.time.Clock()

        self.title_font = pygame.font.SysFont("arial", 36, bold=True)
        self.heading_font = pygame.font.SysFont("arial", 25, bold=True)
        self.font = pygame.font.SysFont("arial", 20)
        self.small_font = pygame.font.SysFont("arial", 16)

        self.on_player_added = on_player_added
        self.on_ip_changed = on_ip_changed
        self.players: list[Player] = []
        self.team = "Red"
        self.message = "Enter an equipment ID and codename."
        self.message_color = MUTED_TEXT

        self.equipment_input = TextInput(
            pygame.Rect(360, 150, 380, 48), "Equipment ID", numeric_only=True, max_length=4
        )
        self.codename_input = TextInput(
            pygame.Rect(360, 220, 380, 48), "Codename", numeric_only=False, max_length=20
        )
        self.ipaddress_input = TextInput(
            pygame.Rect(100, 370, 190, 48), "Default: 127.0.0.1", numeric_only=False, max_length=15
        )

        self.red_button = Button(pygame.Rect(360, 292, 180, 46), "RED TEAM", RED, RED_HOVER)
        self.green_button = Button(pygame.Rect(560, 292, 180, 46), "GREEN TEAM", GREEN, GREEN_HOVER)
        self.add_button = Button(pygame.Rect(430, 365, 240, 52), "ADD PLAYER", (65, 70, 82), (85, 90, 105))
        self.clear_button = Button(pygame.Rect(430, 645, 240, 42), "CLEAR ALL PLAYERS", (55, 55, 62), (75, 75, 84))
        self.ip_button = Button(pygame.Rect(300, 380, 60, 30), "Apply", (55, 55, 62), (75, 75, 84))

    def add_player(self) -> None:
        equipment_text = self.equipment_input.text.strip()
        codename = self.codename_input.text.strip()

        if not equipment_text:
            self._set_message("Equipment ID is required.", ERROR)
            return
        if not codename:
            self._set_message("Codename is required.", ERROR)
            return

        equipment_id = int(equipment_text)
        if equipment_id <= 0:
            self._set_message("Equipment ID must be greater than 0.", ERROR)
            return
        if any(player.equipment_id == equipment_id for player in self.players):
            self._set_message(f"Equipment ID {equipment_id} is already assigned.", ERROR)
            return

        player = Player(equipment_id=equipment_id, codename=codename, team=self.team)

        try:
            if self.on_player_added is not None:
                self.on_player_added(player)
        except Exception as exc:
            # Keep the player off the local roster if database/UDP integration fails.
            self._set_message(f"Could not add player: {exc}", ERROR)
            return

        self.players.append(player)
        self.equipment_input.text = ""
        self.codename_input.text = ""
        self._set_message(
            f"Added {codename} (equipment {equipment_id}) to {self.team} Team.", SUCCESS
        )

    def _change_network_address(self) -> None:
        ipaddress_text = self.ipaddress_input.text.strip()
        if self.on_ip_changed(ipaddress_text):
            self._set_message(f"Network Address set to {ipaddress_text}", SUCCESS)
        else:
            self._set_message(f"Invalid IP Address", ERROR)

    def _set_message(self, text: str, color) -> None:
        self.message = text
        self.message_color = color

    def _draw_header(self) -> None:
        title = self.title_font.render("PHOTON PLAYER ENTRY", True, TEXT)
        self.screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 62)))
        subtitle = self.small_font.render(
            "Add players before starting the game", True, MUTED_TEXT
        )
        self.screen.blit(subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 98)))

    def _draw_form(self) -> None:
        label_equipment = self.font.render("Equipment ID", True, TEXT)
        label_codename = self.font.render("Codename", True, TEXT)
        label_ipaddress = self.font.render("Network", True, TEXT)
        self.screen.blit(label_equipment, (215, 163))
        self.screen.blit(label_codename, (215, 233))
        self.screen.blit(label_ipaddress, (15, 383))

        self.equipment_input.draw(self.screen, self.font)
        self.codename_input.draw(self.screen, self.font)
        self.ipaddress_input.draw(self.screen, self.font)

        mouse_pos = pygame.mouse.get_pos()
        self.red_button.draw(self.screen, self.font, mouse_pos)
        self.green_button.draw(self.screen, self.font, mouse_pos)
        self.add_button.draw(self.screen, self.heading_font, mouse_pos)
        self.ip_button.draw(self.screen, self.font, mouse_pos)

        selected_rect = self.red_button.rect if self.team == "Red" else self.green_button.rect
        pygame.draw.rect(self.screen, TEXT, selected_rect, 3, border_radius=6)

        msg = self.small_font.render(self.message, True, self.message_color)
        self.screen.blit(msg, msg.get_rect(center=(WINDOW_WIDTH // 2, 447)))

    def _draw_roster_column(self, title: str, team: str, rect: pygame.Rect, color) -> None:
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=8)
        pygame.draw.rect(self.screen, color, rect, 2, border_radius=8)
        heading = self.heading_font.render(title, True, color)
        self.screen.blit(heading, heading.get_rect(center=(rect.centerx, rect.y + 28)))

        team_players = [player for player in self.players if player.team == team]
        if not team_players:
            empty = self.small_font.render("No players yet", True, MUTED_TEXT)
            self.screen.blit(empty, empty.get_rect(center=(rect.centerx, rect.y + 80)))
            return

        y = rect.y + 62
        for index, player in enumerate(team_players[:6], start=1):
            row = f"{index}.  {player.equipment_id:<4}  {player.codename}"
            rendered = self.small_font.render(row, True, TEXT)
            self.screen.blit(rendered, (rect.x + 18, y))
            y += 27

        if len(team_players) > 6:
            extra = self.small_font.render(
                f"+ {len(team_players) - 6} more player(s)", True, MUTED_TEXT
            )
            self.screen.blit(extra, (rect.x + 18, y + 4))

    def _draw_rosters(self) -> None:
        self._draw_roster_column(
            "RED TEAM", "Red", pygame.Rect(105, 480, 400, 150), RED_HOVER
        )
        self._draw_roster_column(
            "GREEN TEAM", "Green", pygame.Rect(595, 480, 400, 150), GREEN_HOVER
        )
        self.clear_button.draw(self.screen, self.small_font, pygame.mouse.get_pos())

    def run(self) -> None:
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    running = False

                self.equipment_input.handle_event(event)
                self.codename_input.handle_event(event)
                self.ipaddress_input.handle_event(event)

                if self.red_button.clicked(event):
                    self.team = "Red"
                elif self.green_button.clicked(event):
                    self.team = "Green"
                elif self.add_button.clicked(event):
                    self.add_player()
                elif self.clear_button.clicked(event):
                    self.players.clear()
                    self._set_message("Player list cleared.", MUTED_TEXT)
                elif self.ip_button.clicked(event):
                    self._change_network_address()
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    if not self.equipment_input.active and not self.codename_input.active:
                        self.add_player()

            self.screen.fill(BACKGROUND)
            self._draw_header()
            self._draw_form()
            self._draw_rosters()

            footer = self.small_font.render("ESC = Exit", True, MUTED_TEXT)
            self.screen.blit(footer, (20, WINDOW_HEIGHT - 30))

            pygame.display.flip()
            self.clock.tick(FPS)

        pygame.quit()


def run_player_entry(on_player_added: Optional[Callable[[Player], None]] = None, on_ip_changed: Optional[Callable[[None], bool]] = None) -> None:
    PlayerEntryScreen(on_player_added=on_player_added, on_ip_changed=on_ip_changed).run()


#if __name__ == "__main__":
#    run_player_entry()

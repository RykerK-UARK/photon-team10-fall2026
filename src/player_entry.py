"""Photon player-entry screen for Sprint 3.

This module contains the user interface for entering players before a game.
It intentionally keeps database/UDP logic outside of the UI so the team's
existing database and socket code can be connected with ``on_player_added``.
"""

from typing import Callable, Optional

import pygame

from player_database import Player
from screen_manager import Screen, WINDOW_WIDTH, WINDOW_HEIGHT
from ui_elements import Button, TextInput, PANEL, TEXT, MUTED_TEXT


RED = (135, 26, 32)
RED_HOVER = (170, 34, 41)
GREEN = (31, 112, 53)
GREEN_HOVER = (40, 142, 67)
ERROR = (235, 95, 95)
SUCCESS = (100, 220, 130)
MAX_PLAYERS_PER_TEAM = 15
ROSTER_VISIBLE_ROWS = 3
ROSTER_ROW_HEIGHT = 22


class PlayerEntryScreen(Screen):
    """Pygame UI for adding players to red and green teams.

    ``on_player_added`` is called after a player passes validation.  The team
    can use that callback to insert the player into PostgreSQL and broadcast
    the equipment code over UDP without putting database/socket code in this
    UI file.
    """

    caption = "Photon - Player Entry"

    def __init__(self, manager):
        super().__init__(manager)

        self.heading_font = pygame.font.SysFont("arial", 25, bold=True)
        self.font = pygame.font.SysFont("arial", 20)
        
        self.players: list[Player] = manager.players  # shared with the other screens
        self.team = "Red"
        self.roster_rects = {
            "Red": pygame.Rect(105, 480, 400, 150),
            "Green": pygame.Rect(595, 480, 400, 150),
        }
        self.roster_scroll = {"Red": 0, "Green": 0}
        self.database_connected = self.manager.get_database().conn is not None and self.manager.get_database().cursor is not None
        self.message = ("Enter an equipment ID and codename." if self.database_connected else "Offline demo: players are not saved to PostgreSQL.")

        self.message_color = MUTED_TEXT

        self.player_id_input = TextInput(
            pygame.Rect(360, 150, 100, 48), "Player ID", numeric_only=True, max_length=4
        )
        self.equipment_input = TextInput(
            pygame.Rect(640, 150, 100, 48), "Equip. ID", numeric_only=True, max_length=4
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
        self.clear_button = Button(pygame.Rect(270, 645, 240, 42), "CLEAR ALL PLAYERS", (55, 55, 62), (75, 75, 84))
        self.start_button = Button(pygame.Rect(590, 645, 240, 42), "START GAME", GREEN, GREEN_HOVER)
        self.ip_button = Button(pygame.Rect(300, 380, 60, 30), "Apply", (55, 55, 62), (75, 75, 84))

    def _add_player_to_database(self, player) -> None:
        player_id = player.player_id
        equipment_id = player.equipment_id    
        saved_player = self.manager.get_database().get_player(player_id)

        # Existing IDs keep their saved name; new IDs require a supplied name.
        codename = saved_player[1] if saved_player is not None else player.codename
        if not codename:
            return False

        codename_owner = self.manager.get_database().get_player_by_codename(codename)
        if codename_owner is not None and codename_owner[0] != player_id:
            raise ValueError(f"Codename {codename} is already used by another player ID.")

        if any(
            other.player_id != player_id
            and other.codename.casefold() == codename.casefold()
            for other in self.players
        ):
            raise ValueError(f"Codename {codename} is already used by another player ID.")

        if saved_player is not None:
            player.set_codename(codename)
        else:
            self.manager.get_database().add_player(player_id, codename)

        self.manager.get_network().broadcast(equipment_id)
        return True

    def add_player(self) -> None:
        player_id_text = self.player_id_input.text.strip()
        equipment_text = self.equipment_input.text.strip()
        codename = self.codename_input.text.strip()

        if not player_id_text:
            self._set_message("Player ID is required.", ERROR)
            return
        if not equipment_text:
            self._set_message("Equipment ID is required.", ERROR)
            return

        player_id = int(player_id_text)
        if player_id <= 0:
            self._set_message("Player ID must be greater than 0.", ERROR)
            return
        if any(player.player_id == player_id for player in self.players):
            self._set_message(f"Player ID {player_id} is already in game.", ERROR)
            return

        equipment_id = int(equipment_text)
        if equipment_id <= 0:    
            self._set_message("Equipment ID must be greater than 0.", ERROR)
            return
        if any(player.equipment_id == equipment_id for player in self.players):
            self._set_message(f"Equipment ID {equipment_id} is already assigned.", ERROR)
            return
        if equipment_id in (43, 53):
            self._set_message(f"Equipment ID {equipment_id} is reserved for the team bases.", ERROR)
            return
        team_player_count = sum(
            player.team.casefold() == self.team.casefold()
            for player in self.players
        )
        if team_player_count >= MAX_PLAYERS_PER_TEAM:
            self._set_message(f"{self.team} Team already has {MAX_PLAYERS_PER_TEAM} players.", ERROR)
            return

        player = Player(player_id=player_id, equipment_id=equipment_id, codename=codename, team=self.team, base_hit=False)

        # Without a database, the roster is the only place to catch duplicate codenames.
        if not self.database_connected:
            if not codename:
                self._set_message("Codename is required.", ERROR)
                return
            # The roster is the only place left to catch duplicate codenames.
            if any(other.codename.casefold() == codename.casefold() for other in self.players):
                self._set_message(f"Codename {codename} is already used by another player ID.", ERROR)
                return

        else:
            try:
                if not self._add_player_to_database(player):
                    if not codename:
                        self._set_message("Player ID not found in database and codename not entered", ERROR)
                    else:
                        self._set_message("PostgreSQL is unavailable", ERROR)
                    return
            except ValueError as exc:
                self._set_message(str(exc), ERROR)
                return
            except Exception as exc:
                # Keep the player off the local roster if database/UDP integration fails.
                self._set_message(f"Could not add player: {exc}", ERROR)
                return

        self.players.append(player)
        self.roster_scroll[self.team] = max(
            0,
            team_player_count + 1 - ROSTER_VISIBLE_ROWS,
        )
        self.player_id_input.text = ""
        self.equipment_input.text = ""
        self.codename_input.text = ""
        self._set_message(
            f"Added {codename} (ID: {player_id}) (equipment {equipment_id}) to {self.team} Team.", SUCCESS
        )

    def _change_network_address(self) -> None:
        ipaddress_text = self.ipaddress_input.text.strip()
        
        if self.manager.get_network().set_network_address(ipaddress_text):
            self._set_message(f"Network Address set to {ipaddress_text}", SUCCESS)
        else:
            self._set_message(f"Invalid IP Address", ERROR)

    def _set_message(self, text: str, color) -> None:
        self.message = text
        self.message_color = color

    def _draw_header(self) -> None:
        self.draw_header("PHOTON PLAYER ENTRY", "Add players before starting the game")

    def _draw_form(self) -> None:
        label_player_id = self.font.render("Player ID", True, TEXT)
        label_equipment = self.font.render("Equipment ID", True, TEXT)
        label_codename = self.font.render("Codename", True, TEXT)
        label_ipaddress = self.font.render("Network", True, TEXT)
        self.screen.blit(label_player_id, (255, 163))
        self.screen.blit(label_equipment, (505, 163))
        self.screen.blit(label_codename, (255, 233))
        self.screen.blit(label_ipaddress, (15, 383))

        self.player_id_input.draw(self.screen, self.font)
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

        max_scroll = max(0, len(team_players) - ROSTER_VISIBLE_ROWS)
        scroll = max(0, min(self.roster_scroll[team], max_scroll))
        self.roster_scroll[team] = scroll
        row_area = pygame.Rect(rect.x + 12, rect.y + 54, rect.width - 34, 70)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(row_area)
        for row_index, player in enumerate(
            team_players[scroll:scroll + ROSTER_VISIBLE_ROWS], start=scroll + 1
        ):
            row = f"{row_index}.  {player.equipment_id:<4}  {player.codename}"
            rendered = self.small_font.render(row, True, TEXT)
            y = row_area.y + (row_index - scroll - 1) * ROSTER_ROW_HEIGHT
            self.screen.blit(rendered, (rect.x + 18, y))
        self.screen.set_clip(previous_clip)

        if len(team_players) > ROSTER_VISIBLE_ROWS:
            last_visible = min(scroll + ROSTER_VISIBLE_ROWS, len(team_players))
            range_text = self.small_font.render(
                f"{scroll + 1}-{last_visible} of {len(team_players)}", True, MUTED_TEXT
            )
            self.screen.blit(range_text, (rect.x + 18, rect.bottom - 22))

    def _draw_rosters(self) -> None:
        self._draw_roster_column(
            "RED TEAM", "Red", self.roster_rects["Red"], RED_HOVER
        )
        self._draw_roster_column(
            "GREEN TEAM", "Green", self.roster_rects["Green"], GREEN_HOVER
        )
        self.clear_button.draw(self.screen, self.small_font, pygame.mouse.get_pos())
        self.start_button.draw(self.screen, self.small_font, pygame.mouse.get_pos())

    def clear_players(self) -> None:
        # Clear the players on screen, but not those in the database
        self.players.clear()
        self.roster_scroll = {"Red": 0, "Green": 0}
        self.equipment_input.text = ""
        self.codename_input.text = ""
        self._set_message("All player entries cleared.", MUTED_TEXT)

    def start_game(self) -> Optional[str]:
        """Ask the screen manager to start the countdown, then play action."""
        if not self.players:
            self._set_message("Add at least one player before starting.", ERROR)
            return None

        # The countdown and play-action screens are separate files, so a
        # teammate can change them without editing this screen.
        return "countdown"

    def update(self) -> Optional[str]:
        # Only allow a codename to be typed once a usable player ID is entered.
        player_id_text = self.player_id_input.text.strip()
        if not player_id_text or int(player_id_text) <= 0 or any(player.player_id == int(player_id_text) for player in self.players):
            self.codename_input.enabled = False
        else:
            self.codename_input.enabled = True
        return None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEWHEEL:
            mouse_pos = pygame.mouse.get_pos()
            for team, rect in self.roster_rects.items():
                if rect.collidepoint(mouse_pos):
                    team_count = sum(
                        player.team.casefold() == team.casefold()
                        for player in self.players
                    )
                    max_scroll = max(0, team_count - ROSTER_VISIBLE_ROWS)
                    self.roster_scroll[team] = max(
                        0,
                        min(max_scroll, self.roster_scroll[team] - event.y),
                    )
                    break

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "quit"
            elif event.key == pygame.K_F5:
                return self.start_game()
            elif event.key == pygame.K_F12:
                # Clear this game's roster without deleting database records.
                self.players.clear()
                self.roster_scroll = {"Red": 0, "Green": 0}
                self.player_id_input.text = ""
                self.equipment_input.text = ""
                self.codename_input.text = ""
                self._set_message("Player list cleared.", MUTED_TEXT)

        self.player_id_input.handle_event(event)
        self.equipment_input.handle_event(event)
        self.ipaddress_input.handle_event(event)

        if self.codename_input.enabled:
            self.codename_input.handle_event(event)

        if self.red_button.clicked(event):
            self.team = "Red"
        elif self.green_button.clicked(event):
            self.team = "Green"
        elif self.add_button.clicked(event):
            self.add_player()
        elif self.clear_button.clicked(event):
            self.clear_players()
        elif self.start_button.clicked(event):
            return self.start_game()
        elif self.ip_button.clicked(event):
            self._change_network_address()
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            if not self.equipment_input.active and not self.codename_input.active:
                self.add_player()
        return None

    def draw(self) -> None:
        self.draw_background()
        self._draw_header()
        self._draw_form()
        self._draw_rosters()
        footer_text = "F5 = Start game | F12 = Clear players | ESC = Exit"

        footer = self.small_font.render(footer_text, True, MUTED_TEXT)
        self.screen.blit(footer, (20, WINDOW_HEIGHT - 30))


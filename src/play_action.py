"""Photon Team 10: Player Action Screen (play-by-play display).

Responsibilities in THIS file:
    - Accept already-decoded hit events through register_tag(shooter_id, target_id).
    - Calculate points for valid opponent tags and display team totals.
    - Keep a scrollable, newest-first list of plays and show player rosters.

Responsibilities OUTSIDE this file:
    - UDP sockets, packet decoding, and generator communication. You can use register_tag(shooter_id, target_id) on the active PlayActionScreen, from the same thread as the Pygame event loop.
    - JH owns the six-minute game timer; RK owns base-hit logic and icons;
      RP owns friendly-fire scoring and event logging.

The existing Player Entry -> 30-second Countdown -> Player Action transition
remains unchanged. This file contains no network, music, or timer logic.
"""

from typing import Optional

import pygame

from screen_manager import Screen
from ui_elements import BACKGROUND, BORDER, MUTED_TEXT, PANEL, TEXT, Button

# RGB colors used to distinguish teams and different types of information.
RED = (231, 74, 83)
GREEN = (92, 214, 118)
BLUE = (101, 175, 239)
YELLOW = (246, 192, 78)

# Gameplay and display settings. Keeping these values together makes them
# easy to adjust without searching through the rendering code.
POINTS_PER_TAG = 10
BASE_HIT_CODES = {43, 53}  # Reserved base IDs; base scoring is not implemented yet.
MAX_LOG_ENTRIES = 250       # Keep only the most recent 250 events in memory.
VISIBLE_LOG_ROWS = 7       # Number of event entries displayed without scrolling.


class PlayActionScreen(Screen):
    """Manage game events and render the play-by-play gameplay screen.

    The manager calls on_enter() after the countdown, update() each frame,
    handle_event() for keyboard/mouse input, and draw() to render the screen.
    A separate network controller calls register_tag() as hits arrive.
    """

    caption = "Photon - Player Action"

    def __init__(self, manager):
        super().__init__(manager)
        # Match data is populated in on_enter(), after player entry/countdown.
        self.players = []
        self.players_by_equipment = {}  # equipment_id -> player; fast hit lookup.
        self.scores = {}                # equipment_id -> current individual score.

        # Each event is stored as (event number, description, display color).
        # New events are inserted at index 0, so the newest play appears first.
        self.event_log = []
        self.event_number = 0  # Increases whenever an event is recorded.
        self.log_scroll = 0    # 0 = newest events; higher = older events.

        # Separate fonts keep team headings, scores, players, and events readable.
        self.heading_font = pygame.font.SysFont("arial", 21, bold=True)
        self.score_font = pygame.font.SysFont("arial", 46, bold=True)
        self.player_font = pygame.font.SysFont("arial", 15)
        self.event_font = pygame.font.SysFont("arial", 16)
        self.small_label_font = pygame.font.SysFont("arial", 14, bold=True)

        # Main layout: Red roster on the left, play-by-play in the middle,
        # and Green roster on the right. These rectangles define each panel.
        self.red_rect = pygame.Rect(38, 253, 270, 391)
        self.feed_rect = pygame.Rect(320, 253, 460, 391)
        self.green_rect = pygame.Rect(792, 253, 270, 391)
        # Return to the player entry screen through the existing screen manager.
        self.back_button = Button(
            pygame.Rect(38, 656, 225, 44),
            "BACK TO ENTRY (ESC)",
            (55, 58, 67),
            (78, 82, 92),
        )

    def on_enter(self) -> None:
        """Prepare a fresh match when the countdown transitions to this screen.

        Copy the registered players from the screen manager, reset every score
        and clear the previous game's play-by-play history. This method does
        NOT run the 30-second countdown; that is handled by another screen.
        """
        # Snapshot the players entered before the game starts.
        self.players = list(self.manager.players)
        # Equipment-code lookup lets register_tag() resolve incoming IDs
        # without searching every player in the roster.
        self.players_by_equipment = {p.equipment_id: p for p in self.players}
        self.scores = {p.equipment_id: 0 for p in self.players}
        # Reset event numbering and scroll position for the new match.
        self.event_log.clear()
        self.event_number = 0
        self.log_scroll = 0
        self.record_event("Match started - waiting for tags", BLUE)

        # TODO (RK - network integration): The networking/controller code
        # owns any game-start signal. The screen does not send UDP messages.

        # TODO (JH - timer): Initialize the six-minute gameplay clock here.
        # This method is called AFTER the separate 30-second countdown.

    def team_score(self, team: str) -> int:
        """Sum the individual scores of all players on the requested team.

        Team totals are calculated from self.scores instead of being stored
        separately. This prevents team and individual scores from getting
        out of sync when a teammate adds another scoring rule.
        """
        return sum(
            self.scores.get(p.equipment_id, 0)
            for p in self.players
            if p.team.casefold() == team.casefold()
        )

    def record_event(self, description: str, color=TEXT) -> None:
        """Add a numbered play to the feed, using the supplied text/color.

        Teammates can call this when implementing base hits or friendly fire.
        The feed is capped at MAX_LOG_ENTRIES to avoid growing indefinitely.
        New events also return the view to the latest play.
        """
        self.event_number += 1
        self.event_log.insert(0, (self.event_number, str(description), color))
        del self.event_log[MAX_LOG_ENTRIES:]
        self.log_scroll = 0

    def add_points(self, equipment_id: int, points: int) -> bool:
        """Change one registered player's score and report whether it worked.

        Returns False for an unknown equipment ID. Positive and negative point
        amounts are both accepted, so other scoring rules can reuse this helper.
        """
        if equipment_id not in self.scores:
            return False
        self.scores[equipment_id] += int(points)
        return True

    def register_tag(self, shooter_id: int, target_id: int) -> bool:
        """Record one decoded equipment hit; return True if it scored.

        This is the integration point for the networking teammate. The caller
        supplies two integer equipment IDs (NOT raw UDP bytes). For example:

            action_screen.register_tag(11, 21)

        The caller must invoke this on the Pygame/main thread, not directly
        from a background socket thread. An unregistered shooter/target,
        self-tag, same-team tag, or base code does not award points yet.
        """
        # Resolve the shooter from the roster created during player entry.
        shooter = self.players_by_equipment.get(shooter_id)
        if shooter is None:
            return False

        # Base equipment codes must be interpreted separately from player IDs.
        if target_id in BASE_HIT_CODES:
            # TODO (RK - base hits): Validate the opposing base, award points
            # once per player per game, record the event, and mark the icon.
            return False

        target = self.players_by_equipment.get(target_id)
        if target is None or shooter_id == target_id:
            return False

        if shooter.team.casefold() == target.team.casefold():
            # TODO (RP - friendly fire): Add the team's friendly-fire rule
            # and log here. Teammate hits are currently ignored entirely.
            return False

        # Valid opponent tag: score the shooter and show who tagged whom.
        self.add_points(shooter_id, POINTS_PER_TAG)
        color = RED if shooter.team.casefold() == "red" else GREEN
        self.record_event(
            f"{shooter.codename} tagged {target.codename}  +{POINTS_PER_TAG} pts",
            color,
        )
        return True

    def update(self) -> Optional[str]:
        """Run screen-only per-frame work; do not access any UDP sockets.

        The networking teammate should call register_tag() from the app's
        main thread when a decoded hit arrives. draw() renders the new score
        and feed automatically on the next frame.
        """
        # TODO (JH - timer): Update the six-minute gameplay timer and end the
        # match here when it expires; the 30-second pregame timer is separate.
        return None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """Handle navigation and scrolling of the play-by-play feed.

        Escape or the Back button requests the player-entry screen. Mouse
        wheel scrolling works while the cursor is over the event panel;
        Page Up/Down moves through older/newer plays in larger steps.
        """
        # Screen transitions are requested by returning the destination name.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "player_entry"
        if self.back_button.clicked(event):
            return "player_entry"

        # Clamp scrolling so the feed cannot move past its first/last row.
        # Offset 0 shows the newest events; a larger offset shows older plays.
        max_scroll = max(0, len(self.event_log) - VISIBLE_LOG_ROWS)
        if event.type == pygame.MOUSEWHEEL and self.feed_rect.collidepoint(pygame.mouse.get_pos()):
            self.log_scroll = max(0, min(max_scroll, self.log_scroll + event.y))
        elif event.type == pygame.KEYDOWN and event.key in (pygame.K_PAGEUP, pygame.K_PAGEDOWN):
            delta = 5 if event.key == pygame.K_PAGEUP else -5
            self.log_scroll = max(0, min(max_scroll, self.log_scroll + delta))
        return None

    def _panel(self, rect: pygame.Rect, accent=BORDER) -> None:
        """Draw a rounded panel with a background and optional border color."""
        pygame.draw.rect(self.screen, PANEL, rect, border_radius=11)
        pygame.draw.rect(self.screen, accent, rect, width=2, border_radius=11)

    def _draw_score_card(self, team: str, rect: pygame.Rect, color) -> None:
        """Draw the team name and its live total above the three main panels."""
        self._panel(rect, color)
        title = self.heading_font.render(team.upper() + " TEAM", True, color)
        self.screen.blit(title, title.get_rect(center=(rect.centerx, rect.y + 29)))
        points = self.score_font.render(str(self.team_score(team)), True, TEXT)
        self.screen.blit(points, points.get_rect(center=(rect.centerx, rect.y + 80)))

    def _draw_roster(self, team: str, rect: pygame.Rect, color) -> None:
        """Draw one team's players with the highest scorers listed first."""
        self._panel(rect, color)
        heading = self.heading_font.render(team.upper() + " PLAYERS", True, color)
        self.screen.blit(heading, (rect.x + 16, rect.y + 15))
        pygame.draw.line(
            self.screen, BORDER,
            (rect.x + 12, rect.y + 51), (rect.right - 12, rect.y + 51),
        )

        # Sort by score descending; alphabetical codename breaks score ties.
        # Scores still belong to equipment IDs even if roster order changes.
        roster = sorted(
            (p for p in self.players if p.team.casefold() == team.casefold()),
            key=lambda p: (-self.scores.get(p.equipment_id, 0), (p.codename or "").casefold()),
        )
        if not roster:
            message = self.player_font.render("No players on this team", True, MUTED_TEXT)
            self.screen.blit(message, (rect.x + 15, rect.y + 80))
            return

        # Fit up to 15 player rows in this panel at the current window size.
        for index, player in enumerate(roster[:15]):
            y = rect.y + 62 + index * 21
            player_name = (player.codename or f"Player {player.player_id}")[:18]
            name = self.player_font.render(player_name, True, TEXT)
            self.screen.blit(name, (rect.x + 14, y))

            # TODO (RK - base icon): Draw a persistent base icon by any
            # player who has successfully hit the opposing base.

            score = self.player_font.render(str(self.scores.get(player.equipment_id, 0)), True, TEXT)
            self.screen.blit(score, score.get_rect(topright=(rect.right - 14, y)))

        if len(roster) > 15:
            extra = self.player_font.render(f"+{len(roster) - 15} more players", True, MUTED_TEXT)
            self.screen.blit(extra, (rect.x + 14, rect.bottom - 20))

    def _draw_feed(self) -> None:
        """Draw the center panel showing the current page of match events."""
        area = self.feed_rect
        self._panel(area, BLUE)
        heading = self.heading_font.render("LIVE PLAY-BY-PLAY", True, TEXT)
        self.screen.blit(heading, (area.x + 16, area.y + 14))
        newer = self.small_font.render("NEWEST FIRST", True, MUTED_TEXT)
        self.screen.blit(newer, newer.get_rect(topright=(area.right - 15, area.y + 19)))
        pygame.draw.line(
            self.screen, BORDER,
            (area.x + 14, area.y + 51), (area.right - 14, area.y + 51),
        )

        # Select just the events visible at the current scroll position.
        # The complete event history stays in self.event_log.
        visible = self.event_log[self.log_scroll:self.log_scroll + VISIBLE_LOG_ROWS]
        for index, (sequence, description, color) in enumerate(visible):
            y = area.y + 64 + index * 44
            number = self.small_label_font.render(f"#{sequence:03d}", True, YELLOW)
            self.screen.blit(number, (area.x + 15, y + 6))
            pygame.draw.rect(self.screen, color, (area.x + 73, y + 4, 3, 31), border_radius=1)
            # Shorten overly long descriptions until they fit on one line.
            # This prevents text from overlapping the player panels.
            fitting = description
            max_width = area.width - 107
            while fitting and self.event_font.size(fitting)[0] > max_width:
                fitting = fitting[:-1]
            if fitting != description:
                fitting = fitting[:-3] + "..." if len(fitting) >= 3 else "..."
            text_surface = self.event_font.render(fitting, True, color)
            self.screen.blit(text_surface, (area.x + 87, y + 11))

        # Show a reminder when the user is reading older plays rather than
        # the newest incoming events.
        if self.log_scroll:
            older = self.small_font.render(f"Viewing older plays ({self.log_scroll} back)", True, MUTED_TEXT)
            self.screen.blit(older, (area.x + 15, area.bottom - 20))

    def draw(self) -> None:
        """Render the complete screen from the latest in-memory game state."""
        # Pygame redraws the background and every panel each frame; no manual
        # refresh is needed after add_points() or record_event().
        self.screen.fill(BACKGROUND)
        self.draw_header("PHOTON PLAYER ACTION", "LIVE PLAY-BY-PLAY / RED VS. GREEN")

        # The total-score cards are across the top of the window.
        self._draw_score_card("Red", pygame.Rect(38, 121, 302, 117), RED)
        self._draw_score_card("Green", pygame.Rect(760, 121, 302, 117), GREEN)

        # TODO (JH - timer): Replace the center status panel with the
        # six-minute game clock. On entry, the 30-second countdown is over.
        center = pygame.Rect(353, 121, 394, 117)
        self._panel(center)
        status_title = self.small_label_font.render("GAME IN PROGRESS", True, MUTED_TEXT)
        self.screen.blit(status_title, status_title.get_rect(center=(center.centerx, 154)))
        status_text = self.heading_font.render("LIVE GAME", True, BLUE)
        self.screen.blit(status_text, status_text.get_rect(center=(center.centerx, 196)))

        # Main content: two player lists with the chronological action feed
        # between them. The log displays newest events first.
        self._draw_roster("Red", self.red_rect, RED)
        self._draw_feed()
        self._draw_roster("Green", self.green_rect, GREEN)

        # Navigation button and event status at the bottom. UDP reception is
        # handled elsewhere; this screen never opens or polls a socket.
        self.back_button.draw(self.screen, self.small_font, pygame.mouse.get_pos())
        status = self.small_font.render("WAITING FOR GAME EVENTS", True, GREEN)
        self.screen.blit(status, status.get_rect(midright=(1062, 680)))

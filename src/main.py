"""Main entry point for the Photon laser-tag application."""
# Library imports
from pathlib import Path

import pygame
from player_database import playerDatabase
from player_entry import PlayerEntryScreen
from game_start_countdown import GameStartCountdown
from play_action import PlayActionScreen
from screen_manager import Screen, ScreenManager
from udp_sockets import broadcast_code, poll_receive, set_network_address, get_network_address, close_sockets

# Create a database connection for the application
database = playerDatabase()

class SplashScreen(Screen):
    """Display the Photon splash screen before opening player entry.

    A key press or mouse click skips the remaining splash delay.
    """

    caption = "Photon"

    def __init__(self, manager, duration_ms: int = 2500):
        super().__init__(manager)
        self.duration_ms = duration_ms
        self.start_time = 0

        width, height = self.screen.get_size()

        # Load the Photon logo from the assets folder.
        logo_path = Path(__file__).resolve().parent.parent / "assets" / "logo.jpg"
        try:
            logo = pygame.image.load(str(logo_path)).convert()

            # Scale the image to fit the window while preserving its aspect ratio.
            max_width = width - 100
            max_height = height - 120
            scale = min(max_width / logo.get_width(), max_height / logo.get_height())
            logo_size = (
                max(1, int(logo.get_width() * scale)),
                max(1, int(logo.get_height() * scale)),
            )
            self.logo = pygame.transform.smoothscale(logo, logo_size)
            self.logo_rect = self.logo.get_rect(center=(width // 2, height // 2 - 10))
        except (pygame.error, FileNotFoundError):
            # Fallback if logo.jpg cannot be loaded.
            title_font = pygame.font.SysFont("arial", 72, bold=True)
            self.logo = title_font.render("PHOTON", True, (235, 235, 235))
            self.logo_rect = self.logo.get_rect(center=(width // 2, height // 2))

        small_font = pygame.font.SysFont("arial", 18)
        self.subtitle = small_font.render(
            "Team 10 Laser Tag System", True, (180, 180, 185)
        )
        self.subtitle_rect = self.subtitle.get_rect(center=(width // 2, height - 45))

    def on_enter(self) -> None:
        self.start_time = pygame.time.get_ticks()

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN or (
            event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
        ):
            return "player_entry"
        return None

    def update(self):
        if pygame.time.get_ticks() - self.start_time >= self.duration_ms:
            return "player_entry"
        return None

    def draw(self) -> None:
        self.draw_background()
        self.screen.blit(self.logo, self.logo_rect)
        self.screen.blit(self.subtitle, self.subtitle_rect)

def main() -> None:
    """Run Splash -> Player Entry -> Countdown -> Play Action using one Pygame session."""
    try:
        manager = ScreenManager()

        # The local UI can still be demonstrated when PostgreSQL is offline.
        connected = database.conn is not None and database.cursor is not None
        manager.register("splash", SplashScreen(manager))
        manager.register("player_entry", PlayerEntryScreen(
            manager,
            on_player_added=add_player if connected else None,
            on_ip_changed=set_network_address
        ))
        manager.register("countdown", GameStartCountdown(manager))
        manager.register("play_action", PlayActionScreen(manager))
        manager.run("splash")
        
        # TEST: Print all players in the database and then clear the database
        #database.print_all_players()
        #database.clear_players() TESTING ONLY, DO NOT UNCOMMENT HAPHAZORDLY
        
        # TEST: Print current Network Address    
        #print(get_network_address())
    finally:
        shutdown()

### Socket Section Start ###

# Add a player to PostgreSQL, then announces the equipment ID to the UDP server
def add_player(player):  # player_id, codename, equipment_id
    if database.conn is None or database.cursor is None:
        return False

    # Get values from the player object
    player_id = player.player_id
    equipment_id = player.equipment_id    
    codename = player.codename

    if database.get_player(player_id) != None: # player already in database
        player.set_codename(database.get_player(player_id)[1])
        broadcast_code(equipment_id)
        return True
        
    if not codename:
        return False
        
    database.add_player(player_id, codename)
    broadcast_code(equipment_id)
    return True


# Close sockets
def shutdown():
    database.disconnect()
    close_sockets()

# Run Main
if __name__ == "__main__":
    main()

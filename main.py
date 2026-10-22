"""Main entry point for the Photon laser-tag application."""
# Library imports
from pathlib import Path

import pygame
from player_database import playerDatabase
from player_entry import run_player_entry
from udp_socket import broadcast_code, poll_receive, set_network_address, get_network_address, close_sockets

# Create a database connection for the application
database = playerDatabase()


def run_splash_screen(duration_ms: int = 2500) -> bool:
    """Display the Photon splash screen before opening player entry.

    Returns False if the user closes the splash window, otherwise True.
    A key press or mouse click skips the remaining splash delay.
    """
    pygame.init()
    pygame.display.set_caption("Photon")

    width, height = 1100, 720
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()

    background = (8, 8, 10)
    screen.fill(background)

    # Load the Photon logo from the same folder as main.py.
    logo_path = Path(__file__).resolve().with_name("logo.jpg")
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
        logo = pygame.transform.smoothscale(logo, logo_size)
        logo_rect = logo.get_rect(center=(width // 2, height // 2 - 10))
        screen.blit(logo, logo_rect)
    except (pygame.error, FileNotFoundError):
        # Fallback if logo.jpg cannot be loaded.
        title_font = pygame.font.SysFont("arial", 72, bold=True)
        title = title_font.render("PHOTON", True, (235, 235, 235))
        screen.blit(title, title.get_rect(center=(width // 2, height // 2)))

    small_font = pygame.font.SysFont("arial", 18)
    subtitle = small_font.render(
        "Team 10 Laser Tag System", True, (180, 180, 185)
    )
    screen.blit(subtitle, subtitle.get_rect(center=(width // 2, height - 45)))

    pygame.display.flip()
    start_time = pygame.time.get_ticks()

    while pygame.time.get_ticks() - start_time < duration_ms:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            if event.type == pygame.KEYDOWN or (
                event.type == pygame.MOUSEBUTTONDOWN and event.button == 1
            ):
                pygame.quit()
                return True

        clock.tick(60)

    pygame.quit()
    return True

def main() -> None:
    # Sprint 2 UI entry point.
    if not run_splash_screen():
        shutdown()
        return

    # Database/UDP integration can be passed to run_player_entry as a callback.
    run_player_entry(add_player, set_network_address)
    
    # TEST: Print all players in the database and then clear the database
    database.print_all_players()
    database.clear_players()
    
    # TEST: Print current Network Address
    print(get_network_address())
    
    shutdown()



# Add a player to PostgreSQL, then announces the equipment ID to the UDP server
def add_player(player): # player_id, codename, equipment_id
    # Do not try database operations if connection failed at startup.
    if database.conn is None or database.cursor is None:
        print("PostgreSQL is unavailable.")
        return False

	# Get values from the player object
	player_id = database.get_new_player_id(player.team)
	equipment_id = player.equipment_id
	codename = player.codename

    if not database.add_player(player_id, codename):
        return False

    broadcast_code(equipment_id)
    return True

# Close sockets
def shutdown():
    database.disconnect()
    close_sockets()

# Run Main
if __name__ == "__main__":
    main()

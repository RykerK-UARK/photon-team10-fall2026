"""Pre-game countdown screen, independent of the play-action display.

Flow: player entry -> run_countdown(...) -> play action.

This function is intentionally self-contained so the team can replace its
simple text countdown with images, sounds, or a more elaborate countdown
without changing the player-entry screen or the play-action screen.
"""

import pygame


COUNTDOWN_SECONDS = 30
FPS = 60
BACKGROUND = (8, 8, 10)
PANEL = (22, 22, 28)
TEXT = (235, 235, 235)
MUTED = (165, 165, 170)
BORDER = (80, 80, 90)


def run_countdown(
    screen: pygame.Surface,
    clock: pygame.time.Clock,
    seconds: int = COUNTDOWN_SECONDS,
) -> str:
    """Display the countdown, then return control to the player-entry screen.

    Returns:
        'complete': countdown finished; load the play-action screen.
        'back':     ESC pressed; return to player entry without starting.
        'quit':     the window was closed; shut down the application.

    Keep this return contract when replacing the countdown implementation.
    Don't call pygame.init(), set_mode(), or pygame.quit() here: all screens
    share the application's existing Pygame window.
    """
    pygame.display.set_caption("Photon - Game Countdown")
    title_font = pygame.font.SysFont("arial", 38, bold=True)
    number_font = pygame.font.SysFont("arial", 128, bold=True)
    small_font = pygame.font.SysFont("arial", 20)

    started_at_ms = pygame.time.get_ticks()

    while True:
        # Process events every frame to keep the app responsive.
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "back"

        # Use real elapsed milliseconds instead of assuming a fixed frame rate.
        elapsed_ms = max(0, pygame.time.get_ticks() - started_at_ms)
        remaining = max(0, seconds - elapsed_ms // 1000)
        if remaining == 0:
            return "complete"

        width, height = screen.get_size()
        screen.fill(BACKGROUND)

        panel = pygame.Rect(0, 0, 650, 360)
        panel.center = (width // 2, height // 2)
        pygame.draw.rect(screen, PANEL, panel, border_radius=14)
        pygame.draw.rect(screen, BORDER, panel, width=2, border_radius=14)

        heading = title_font.render("GAME STARTS IN", True, TEXT)
        screen.blit(heading, heading.get_rect(center=(width // 2, height // 2 - 105)))

        number = number_font.render(f"00:{remaining:02d}", True, TEXT)
        screen.blit(number, number.get_rect(center=(width // 2, height // 2 + 10)))

        hint = small_font.render("ESC = Return to Player Entry", True, MUTED)
        screen.blit(hint, hint.get_rect(center=(width // 2, height // 2 + 135)))

        pygame.display.flip()
        clock.tick(FPS)

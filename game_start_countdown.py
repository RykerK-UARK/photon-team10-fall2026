from pathlib import Path
import pygame

WINDOW_WIDTH = 1100
WINDOW_HEIGHT = 720
FPS = 60

BACKGROUND = (8, 8, 10)

class GameStartCountdown:

    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock):
        self.screen = screen
        self.clock = clock

    def change_image(self, image_name) -> None:
        # Load the Photon image from the same folder as main.py.
        image_path = Path(__file__).resolve().parent / "countdown_images" / image_name
        self.screen.fill(BACKGROUND)
        try:
            image = pygame.image.load(str(image_path)).convert()

            # Scale the image to fit the window while preserving its aspect ratio.
            max_width = self.screen.get_width() - 100
            max_height = self.screen.get_height() - 120
            scale = min(max_width / image.get_width(), max_height / image.get_height())
            image_size = (
                max(1, int(image.get_width() * scale)),
                max(1, int(image.get_height() * scale)),
            )
            image = pygame.transform.smoothscale(image, image_size)
            image_rect = image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 10))
            self.screen.blit(image, image_rect)
        except (pygame.error, FileNotFoundError):
            # Fallback if image cannot be loaded.
            title_font = pygame.font.SysFont("arial", 72, bold=True)
            title = title_font.render("PHOTON", True, (235, 235, 235))
            self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2)))
        pygame.display.flip()

    # duration_ms is the time for each frame of the countdown, not the entire countdown
    def run(self, duration_ms: int = 1000) -> bool:
        pygame.display.set_caption("Photon")
        countdown_images = [f"countdown{i}.jpg" for i in range(31)]
        
        for i in range(31):
            self.change_image(countdown_images[30-i])
            start_time = pygame.time.get_ticks()
            while pygame.time.get_ticks() - start_time < duration_ms:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return "quit"
                self.clock.tick(FPS)

        return "complete"

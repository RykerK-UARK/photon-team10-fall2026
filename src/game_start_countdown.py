from pathlib import Path
from typing import Optional

import pygame

from screen_manager import Screen
from ui_elements import BACKGROUND

class GameStartCountdown(Screen):

    caption = "Photon"

    # duration_ms is the time for each frame of the countdown, not the entire countdown
    def __init__(self, manager, duration_ms: int = 1000):
        super().__init__(manager)
        self.duration_ms = duration_ms
        self.countdown_images = [f"countdown{i}.jpg" for i in range(31)]
        self.image = None
        self.image_index = -1
        self.start_time = 0

    def on_enter(self) -> None:
        # Restart the countdown every time this screen is opened.
        self.start_time = pygame.time.get_ticks()
        self.image_index = -1
        self.image = None

    def change_image(self, image_name) -> None:
        # Load the Photon image from the assets folder.
        image_path = Path(__file__).resolve().parent.parent / "assets" / "countdown_images" / image_name
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
            self.image = pygame.transform.smoothscale(image, image_size)
        except (pygame.error, FileNotFoundError):
            # Fallback if image cannot be loaded (draw() shows the title instead).
            self.image = None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        # ESC cancels the countdown and returns to player entry.
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "player_entry"
        # SPACE skips the countdown (for testing).
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            return "play_action"
        return None

    def update(self) -> Optional[str]:
        i = (pygame.time.get_ticks() - self.start_time) // self.duration_ms
        if i >= len(self.countdown_images):
            return "play_action"

        # Only reload the image when the countdown moves to the next frame.
        if i != self.image_index:
            self.image_index = i
            self.change_image(self.countdown_images[30 - i])
        return None

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        if self.image is not None:
            image_rect = self.image.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 - 10))
            self.screen.blit(self.image, image_rect)
        else:
            title_font = pygame.font.SysFont("arial", 72, bold=True)
            title = title_font.render("PHOTON", True, (235, 235, 235))
            self.screen.blit(title, title.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2)))

from pathlib import Path
from typing import Optional

import pygame
import random
from screen_manager import Screen
from ui_elements import BACKGROUND

COUNTDOWN_SECONDS = 30
TRACK_INTRO_SECONDS = 17
VOICE_COUNTDOWN_START_SECONDS = 9

class GameStartCountdown(Screen):

    caption = "Photon"

    # duration_ms is the time for each frame of the countdown, not the entire countdown
    def __init__(self, manager, duration_ms: int = 1000):
        super().__init__(manager)
        self.duration_ms = duration_ms
        self.countdown_images = [f"countdown{i}.jpg" for i in range(30, 0, -1)]
        self.image = None
        self.image_index = -1
        self.start_time = 0
        self.music_loaded = False
        self.music_started = False
        self.music_started_at = None
        self.displayed_number = None

    def on_enter(self) -> None:
        # Restart the countdown every time this screen is opened.
        pygame.mixer.music.stop()
        self.image_index = -1
        self.image = None
        self.music_loaded = False
        self.music_started = False
        self.music_started_at = None
        self.displayed_number = None

        track_number = random.randint(1, 8)
        track_path = (
            Path(__file__).resolve().parent.parent
            / "assets"
            / "photon_tracks"
            / f"Track{track_number:02d}.mp3"
        )
        try:
            pygame.mixer.music.load(str(track_path))
            self.music_loaded = True
        except (pygame.error, OSError) as exc:
            print(f"Could not load game music: {exc}")

        self.start_time = pygame.time.get_ticks()

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
            pygame.mixer.music.stop()
            return "player_entry"
        # SPACE skips the countdown (for testing).
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            if self.music_loaded:
                try:
                    pygame.mixer.music.play(start=TRACK_INTRO_SECONDS)
                    self.music_started = True
                except pygame.error as exc:
                    print(f"Could not start game music: {exc}")
            return "play_action"
        return None

    def update(self) -> Optional[str]:
        now = pygame.time.get_ticks()
        elapsed_ms = now - self.start_time
        countdown_duration_ms = len(self.countdown_images) * self.duration_ms
        music_start_ms = countdown_duration_ms - TRACK_INTRO_SECONDS * 1000
        if self.music_loaded and not self.music_started and elapsed_ms >= music_start_ms:
            self.music_started = True
            try:
                pygame.mixer.music.play()
                self.music_started_at = pygame.time.get_ticks()
            except pygame.error as exc:
                print(f"Could not start game music: {exc}")

        if self.music_started_at is not None:
            track_elapsed_ms = now - self.music_started_at
            if track_elapsed_ms >= TRACK_INTRO_SECONDS * 1000:
                return "play_action"
            voice_countdown_starts_at = self.music_started_at + VOICE_COUNTDOWN_START_SECONDS * 1000
        else:
            if elapsed_ms >= countdown_duration_ms:
                return "play_action"
            track_elapsed_ms = elapsed_ms - music_start_ms
            voice_countdown_starts_at = self.start_time + music_start_ms + VOICE_COUNTDOWN_START_SECONDS * 1000

        if now >= voice_countdown_starts_at:
            if track_elapsed_ms >= 15_500:
                countdown_number = 1
            elif track_elapsed_ms >= 13_500:
                countdown_number = 2
            elif track_elapsed_ms >= 12_000:
                countdown_number = 3
            elif track_elapsed_ms >= 10_000:
                countdown_number = 4
            else:
                countdown_number = 5
        else:
            early_phase_ms = music_start_ms + VOICE_COUNTDOWN_START_SECONDS * 1000
            step_ms = early_phase_ms / (COUNTDOWN_SECONDS - 5)
            countdown_number = max(6, COUNTDOWN_SECONDS - int(elapsed_ms / step_ms))

        if countdown_number != self.displayed_number:
            self.displayed_number = countdown_number
            self.change_image(f"countdown{countdown_number}.jpg")
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

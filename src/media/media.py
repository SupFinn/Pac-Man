from __future__ import annotations

import os

import cv2
import pygame

from src.media import constants
from src.media import render


class VideoBackground:
    def __init__(self, window_width: int, window_height: int) -> None:
        """Set up the video state and load the default theme."""
        self.window_width: int = window_width
        self.window_height: int = window_height

        self.capture: cv2.VideoCapture | None = None
        self.current_theme: int | None = None

        self.video_width: int = 0
        self.video_height: int = 0
        self.frame_duration_ms: float = 1000 / 30
        self.accum_ms: float = 0

        self.display_width: int = 0
        self.display_height: int = 0
        self.offset_y: int = 0
        self.scale: float = 1.0

        self._frame_surface: pygame.Surface | None = None
        self._blur_kernel: int = self._compute_blur_kernel()

        self.load_theme(constants.DEFAULT_THEME)

    @staticmethod
    def _compute_blur_kernel() -> int:
        """Return an odd blur kernel size from the blur level."""
        if constants.BLUR_LEVEL <= 0:
            return 0
        kernel = max(3, int(constants.BLUR_MAX_KERNEL * constants.BLUR_LEVEL))
        return kernel if kernel % 2 else kernel + 1

    def load_theme(self, theme_number: int) -> bool:
        """Open the video of a theme and recompute the layout."""
        path = constants.THEME_VIDEOS.get(theme_number)
        if not path or not os.path.exists(path):
            print("Could not find video:", path)
            return False

        self.release()

        capture = cv2.VideoCapture(path)
        if not capture.isOpened():
            print("Could not open video:", path)
            return False

        self.capture = capture
        self.current_theme = theme_number
        self.video_width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.video_height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT))

        fps = capture.get(cv2.CAP_PROP_FPS)
        self.frame_duration_ms = 1000 / (fps if fps > 0 else 30)
        self.accum_ms = 0

        self._recalculate_layout()
        self._decode_frame()
        return True

    def _recalculate_layout(self) -> None:
        """Compute the scaled video size and its vertical offset."""
        if self.video_width <= 0 or self.video_height <= 0:
            return

        self.scale = self.window_width / self.video_width
        self.display_width = max(1, int(self.video_width * self.scale))
        self.display_height = max(1, int(self.video_height * self.scale))
        self.offset_y = (self.window_height - self.display_height) // 2
        self._frame_surface = pygame.Surface(
            (self.display_width, self.display_height)
        )

    def _decode_frame(self) -> None:
        """Read, resize and blur the next frame onto the surface."""
        if self.capture is None or self._frame_surface is None:
            return

        success, frame = self.capture.read()
        if not success:
            self.capture.set(cv2.CAP_PROP_POS_FRAMES, 0)
            success, frame = self.capture.read()
            if not success:
                return

        interpolation = (
            cv2.INTER_AREA if self.scale <= 1.0 else cv2.INTER_LINEAR
        )
        frame = cv2.resize(
            frame,
            (self.display_width, self.display_height),
            interpolation=interpolation,
        )
        if self._blur_kernel:
            kernel = (self._blur_kernel, self._blur_kernel)
            frame = cv2.GaussianBlur(frame, kernel, 0)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        pygame.surfarray.blit_array(self._frame_surface, frame.swapaxes(0, 1))

    def update(self, dt_ms: int) -> None:
        """Decode a new frame when enough time has passed."""
        if self.capture is None:
            return
        self.accum_ms += dt_ms
        if self.accum_ms < self.frame_duration_ms:
            return
        self.accum_ms %= self.frame_duration_ms
        self._decode_frame()

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the visible part of the current frame."""
        if self._frame_surface is None:
            return

        source_y = max(0, -self.offset_y)
        source_height = max(
            0, min(self.display_height - source_y, self.window_height)
        )
        source_width = max(0, min(self.display_width, self.window_width))
        if source_width <= 0 or source_height <= 0:
            return

        area = pygame.Rect(0, source_y, source_width, source_height)
        screen.blit(self._frame_surface, (0, max(0, self.offset_y)), area)

    def release(self) -> None:
        """Release the video capture."""
        if self.capture is not None:
            self.capture.release()
            self.capture = None


class AudioManager:
    def __init__(self) -> None:
        """Initialize the mixer and load every sound effect."""
        try:
            pygame.mixer.init()
        except pygame.error:
            os.environ["SDL_AUDIODRIVER"] = "dummy"
            pygame.mixer.quit()
            pygame.mixer.init()
        pygame.mixer.set_num_channels(24)
        self.music_volume: float = constants.MUSIC_VOLUME
        self.sfx_volume: float = constants.SFX_VOLUME
        self.playing_mode: bool = False
        self.current_theme: int | None = None
        self.sounds: dict[str, pygame.mixer.Sound | None] = {
            name: self._load_sound(path)
            for name, path in constants.SFX_FILES.items()
        }
        pygame.mixer.music.set_volume(self.music_volume)

    @staticmethod
    def _load_sound(path: str) -> pygame.mixer.Sound | None:
        """Load a sound file, returning None if it fails."""
        try:
            return pygame.mixer.Sound(path)
        except (pygame.error, FileNotFoundError) as exc:
            print("Could not load sound:", path, exc)
            return None

    def play_theme_music(self, theme_number: int) -> None:
        """Load and loop the music of a theme."""
        if theme_number == self.current_theme:
            return
        path = constants.MUSIC_FILES.get(theme_number)
        if not path:
            return
        try:
            pygame.mixer.music.load(path)
            self._apply_music_volume()
            pygame.mixer.music.play(-1)
            self.current_theme = theme_number
        except pygame.error as exc:
            print("Could not play music:", path, exc)

    def _apply_music_volume(self) -> None:
        """Set the music volume, capped while playing."""
        volume = self.music_volume
        if self.playing_mode:
            volume = min(volume, constants.PLAYING_MUSIC_VOLUME)
        pygame.mixer.music.set_volume(volume)

    def set_playing_mode(self, playing: bool) -> None:
        """Turn the lower in-game music volume on or off."""
        self.playing_mode = playing
        self._apply_music_volume()

    def adjust_music_volume(self, amount: float) -> None:
        """Change the music volume, clamped between 0 and 1."""
        self.music_volume = min(1.0, max(0.0, self.music_volume + amount))
        self._apply_music_volume()

    def adjust_sfx_volume(self, amount: float) -> None:
        """Change the effects volume, clamped between 0 and 1."""
        self.sfx_volume = min(1.0, max(0.0, self.sfx_volume + amount))

    def play(self, name: str, loops: int = 0) -> None:
        """Play a sound effect at the current effects volume."""
        sound = self.sounds.get(name)
        if sound is None:
            return
        sound.set_volume(self.sfx_volume)
        sound.play(loops=loops)

    def stop(self, *names: str) -> None:
        """Stop the named sound effects."""
        for name in names:
            sound = self.sounds.get(name)
            if sound is not None:
                sound.stop()

    def play_move(self) -> None:
        """Play the menu move sound."""
        self.play("move")

    def play_confirm(self) -> None:
        """Play the menu confirm sound."""
        self.play("confirm")

    def play_back(self) -> None:
        """Play the menu back sound."""
        self.play("back")


class Cursor:
    def __init__(self) -> None:
        """Hide the system cursor and load the custom sprites."""
        blank = pygame.Surface((1, 1), pygame.SRCALPHA)
        pygame.mouse.set_cursor(pygame.cursors.Cursor((0, 0), blank))
        pygame.mouse.set_visible(False)

        self.sprites: dict[str, pygame.Surface] = {}
        self.offsets: dict[str, tuple[int, int]] = {}
        for name, path in constants.CURSOR_FILES.items():
            try:
                sprite = render.images.load_by_height(
                    path, constants.CURSOR_HEIGHT
                )
            except (pygame.error, FileNotFoundError) as exc:
                print("Could not load cursor:", path, exc)
                continue
            hx, hy = constants.CURSOR_HOTSPOTS[name]
            self.sprites[name] = sprite
            self.offsets[name] = (
                int(sprite.get_width() * hx),
                int(sprite.get_height() * hy),
            )

        if not self.sprites:
            pygame.mouse.set_cursor(
                pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
            )
            pygame.mouse.set_visible(True)

    def draw(self, screen: pygame.Surface, state: str) -> None:
        """Draw the cursor sprite for a state at the mouse position."""
        sprite = self.sprites.get(state) or self.sprites.get("normal")
        if sprite is None:
            return
        ox, oy = self.offsets.get(state) or self.offsets["normal"]
        x, y = pygame.mouse.get_pos()
        screen.blit(sprite, (x - ox, y - oy))

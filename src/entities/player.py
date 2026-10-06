from typing import List, Tuple, Dict
from src.media.render import IconSheet
import pygame


class Player:
    def __init__(
            self,
            name: str,
            iconsheet: IconSheet,
            frames: Dict[str, List[pygame.Rect]],
            x: int = 0,
            y: int = 0) -> None:
        """Create a player with a skin, start cell, lives and animation."""

        self.name = name
        self.lives = 3
        self.currentx = x
        self.currenty = y

        self.visualx = x
        self.visualy = y
        self.iconsheet = iconsheet
        self.frames = frames
        self.direction = "S"
        self.last_movement = 0
        self.move_speed_ms = 150

        self.anim_frame = 0
        self.anim_last_switch = 0
        self.anim_interval = 200

    def reset(self) -> None:
        """Restore the player's lives to three."""
        self.lives = 3

    def update_position(self, x: int, y: int) -> None:
        """Teleport the player to a cell without sliding."""
        self.currentx = x
        self.currenty = y
        self.visualx = x
        self.visualy = y

    def get_visual_position(self, now: int) -> Tuple[float, float]:
        """Interpolate the drawn position between two cells."""
        elapsed = now - self.last_movement
        t = min(1.0, elapsed / self.move_speed_ms)
        vx = self.visualx + (self.currentx - self.visualx) * t
        vy = self.visualy + (self.currenty - self.visualy) * t
        return vx, vy

    def update_animation(self, now: int) -> None:
        """Advance the animation frame at a fixed interval."""
        if now - self.anim_last_switch >= self.anim_interval:
            frame_count = len(self.frames[self.direction])
            self.anim_frame = (self.anim_frame + 1) % frame_count
            self.anim_last_switch = now

    def get_current_rect(self) -> pygame.Rect:
        """Return the sprite rect for the facing direction."""
        frames = self.frames.get(self.direction, self.frames["S"])
        return frames[self.anim_frame]

from abc import ABC, abstractmethod
from enum import Enum
from collections import deque
import random
from src.media.constants import (
    BLINKY_FRAMES,
    INKY_FRAMES,
    PINKY_FRAMES,
    CLYDE_FRAMES,
    EYES_RECT,
    BLUE_FRAMES,
    GHOST_EAT_COOLDOWN_MS
)
from src.media.render import ghosts, eyes
import pygame
from typing import Any, Dict, List, Optional, Tuple


class TARGET(Enum):
    PACMAN = "pacman"
    HOME = "home"


class GhostState(Enum):
    NORMAL = "normal"
    FRIGHTENED = "frightened"
    EATEN = "eaten"


DIRECTIONS = {
    "N": (0, -1),
    "S": (0, +1),
    "W": (-1, 0),
    "E": (+1, 0),
}

OPPOSITE = {
    "N": "S",
    "S": "N",
    "E": "W",
    "W": "E",
}


class Ghost(ABC):

    frames: Dict[str, List[pygame.Rect]]
    rect: Optional[pygame.Rect]

    def __init__(self,
                 cornerx: int,
                 cornery: int,
                 last_movement: int,
                 cooldown: int) -> None:
        """Set up a ghost's corner, position, speed, animation and state."""

        self.cornerx: int = cornerx
        self.cornery: int = cornery

        self.currentx = cornerx
        self.currenty = cornery

        self.visualx = cornerx
        self.visualy = cornery

        self.last_direction = "N"

        self.last_movement = last_movement

        self.initial_cooldown = cooldown
        self.base_cooldown = cooldown
        self.cooldown = cooldown

        self.anim_frame = 0
        self.anim_last_switch = 0
        self.anim_interval = 250

        self.target = TARGET.PACMAN
        self.iconsheet = ghosts
        self.line = 0

        self.ghoststate = GhostState.NORMAL
        self.frightened_start: Optional[int] = None
        self.frightened_duration = 4000

        self.eat_cooldown = 0.

    def _direction_delta(self, dx: int, dy: int) -> str:
        """Convert a (dx, dy) step into "N", "S", "E" or "W"."""
        for direction, (ddx, ddy) in DIRECTIONS.items():
            if (ddx, ddy) == (dx, dy):
                return direction
        return self.last_direction

    def apply_level_speed(self,
                          level_index: int,
                          min_cooldown: int = 250,
                          step: int = 27) -> None:
        """Lower the base cooldown as the level rises, down to a minimum."""

        self.base_cooldown = max(
            min_cooldown, self.initial_cooldown - level_index * step
        )
        if self.ghoststate == GhostState.NORMAL:
            self.cooldown = self.base_cooldown

    def update_animation(self, now: int) -> None:
        """Flip the ghost's animation frame at a fixed interval."""
        if self.ghoststate == GhostState.EATEN:
            return
        if now - self.anim_last_switch >= self.anim_interval:
            self.anim_frame = 1 - self.anim_frame
            self.anim_last_switch = now

    def get_current_rect(self) -> pygame.Rect:
        """Return the sprite rect matching the ghost's state and direction."""
        if self.ghoststate == GhostState.FRIGHTENED:
            return BLUE_FRAMES[self.anim_frame]

        if self.ghoststate == GhostState.EATEN:
            return EYES_RECT
        frames = self.frames.get(self.last_direction, self.frames["S"])
        return frames[self.anim_frame]

    def get_visual_position(self, now: int) -> Tuple[float, float]:
        """Interpolate the ghost's drawn position between two maze cells."""
        elapsed = now - self.last_movement
        t = min(1.0, elapsed / self.cooldown)
        vx = self.visualx + (self.currentx - self.visualx) * t
        vy = self.visualy + (self.currenty - self.visualy) * t
        return (vx, vy)

    @abstractmethod
    def move(self, *args: Any, **kwargs: Any) -> None:
        """Abstract method: advance the ghost using its own chase strategy."""
        ...

    def resetGhostPosition(self, x: int, y: int) -> None:
        """Move the ghost and its home corner to the given cell."""
        self.currenty = self.visualy = self.cornery = y
        self.currentx = self.visualx = self.cornerx = x

    def set_state(self, state: GhostState, now: int = 0) -> None:
        """Switch state and apply the matching cooldown and sprite sheet."""
        if state == GhostState.FRIGHTENED:
            self.frightened_start = now
            self.cooldown = 500
            self.rect = self.get_current_rect()
            self.iconsheet = ghosts
        elif state == GhostState.NORMAL:
            self.cooldown = self.base_cooldown
            self.rect = self.get_current_rect()
            self.iconsheet = ghosts
        elif state == GhostState.EATEN:
            self.rect = EYES_RECT
            self.cooldown = 50
            self.iconsheet = eyes
        self.ghoststate = state

    def move_random_direction(
            self,
            maze: List[List[int]],
            width: int,
            height: int,
            now: int) -> None:
        """Step to a random open neighbor without reversing, if possible.

        If no direction is open except the reverse of the last move (a
        dead end), fall back to reversing -- but only after confirming
        that direction is genuinely open, so the ghost never steps
        through a wall (e.g. into the '42' logo block)."""
        cell = maze[self.currenty][self.currentx]
        direction = []
        # decide where to move
        # N
        if (
            self.last_direction != "S"
            and (cell & 1) == 0
            and self.currenty - 1 >= 0
        ):
            direction.append("N")
        # E
        if (
            self.last_direction != "W"
            and (cell & 2) == 0
            and self.currentx + 1 < width
        ):
            direction.append("E")
        # S
        if (
            self.last_direction != "N"
            and (cell & 4) == 0
            and self.currenty + 1 < height
        ):
            direction.append("S")
        # W
        if (
            self.last_direction != "E"
            and (cell & 8) == 0
            and self.currentx - 1 >= 0
        ):
            direction.append("W")

        if len(direction) == 0:
            fallback = OPPOSITE.get(self.last_direction)
            if fallback is None or not self._is_open(maze, width, height,
                                                     fallback):
                return
            key = fallback
        else:
            key = random.choice(direction)

        self.last_direction = key
        x, y = DIRECTIONS[key]
        self.visualx, self.visualy = self.currentx, self.currenty
        self.currentx += x
        self.currenty += y
        self.last_movement = now

    def _is_open(self, maze: List[List[int]], width: int, height: int,
                 direction: str) -> bool:
        """Check whether the given direction is actually open from here."""
        cell = maze[self.currenty][self.currentx]
        if direction == "N":
            return (cell & 1) == 0 and self.currenty - 1 >= 0
        if direction == "E":
            return (cell & 2) == 0 and self.currentx + 1 < width
        if direction == "S":
            return (cell & 4) == 0 and self.currenty + 1 < height
        # "W"
        return (cell & 8) == 0 and self.currentx - 1 >= 0

    def move_back_to_home(
            self,
            maze: List[List[int]],
            width: int,
            height: int,
            now: int) -> None:
        """Walk an eaten ghost to its corner by BFS, then revive it."""
        if now - self.last_movement < self.cooldown:
            return
        if self.currentx == self.cornerx and self.currenty == self.cornery:
            assert self.frightened_start is not None
            if now - self.frightened_start > self.frightened_duration:
                self.set_state(GhostState.NORMAL, now)
            else:
                self.set_state(GhostState.FRIGHTENED, self.frightened_start)
                self.eat_cooldown = now + GHOST_EAT_COOLDOWN_MS
            return
        start = (self.currentx, self.currenty)

        queue = deque([start])
        visited = {start}
        track: Dict[Tuple[int, int], Tuple[int, int]] = {}

        while queue:
            current_pos = queue.popleft()
            if current_pos == (self.cornerx, self.cornery):
                path = []
                while current_pos in track:
                    path.append(current_pos)
                    current_pos = track[current_pos]
                path.append(current_pos)
                path.reverse()
                if len(path) > 1:
                    cx, cy = path[1]
                    self.visualx, self.visualy = self.currentx, self.currenty
                    self.currentx = cx
                    self.currenty = cy
                    self.last_movement = now
                break

            cx, cy = current_pos
            cell = maze[cy][cx]

            # N
            neighbor = (cx, cy - 1)
            if (cell & 1) == 0 and cy - 1 >= 0 and neighbor not in visited:
                visited.add(neighbor)
                track[neighbor] = current_pos
                queue.append(neighbor)

            # E
            neighbor = (cx + 1, cy)
            if (cell & 2) == 0 and cx + 1 < width and neighbor not in visited:
                visited.add(neighbor)
                track[neighbor] = current_pos
                queue.append(neighbor)

            # S
            neighbor = (cx, cy + 1)
            if (cell & 4) == 0 and cy + 1 < height and neighbor not in visited:
                visited.add(neighbor)
                track[neighbor] = current_pos
                queue.append(neighbor)

            # W
            neighbor = (cx - 1, cy)
            if (cell & 8) == 0 and cx - 1 >= 0 and neighbor not in visited:
                visited.add(neighbor)
                track[neighbor] = current_pos
                queue.append(neighbor)
        self.last_movement = now


class Blinky(Ghost):

    def __init__(
            self,
            cornerx: int,
            cornery: int,
            last_movement: int,
            cooldown: int) -> None:
        """Create Blinky with his sprite frames."""
        self.frames = BLINKY_FRAMES
        self.rect = None
        super().__init__(cornerx, cornery, last_movement, cooldown)

    def move(
            self,
            maze: List[List[int]],
            width: int,
            height: int,
            playerx: int,
            playery: int,
            now: int
            ) -> None:
        """Chase the player's exact cell using a BFS shortest path."""
        if self.ghoststate == GhostState.EATEN:
            self.move_back_to_home(maze, width, height, now)
        elif self.ghoststate == GhostState.FRIGHTENED:
            assert self.frightened_start is not None
            if now - self.frightened_start > self.frightened_duration:
                self.set_state(GhostState.NORMAL, now)
            elif now - self.last_movement >= self.cooldown:
                self.move_random_direction(maze, width, height, now)
        elif self.ghoststate == GhostState.NORMAL:
            if now - self.last_movement < self.cooldown:
                return
            start = (self.currentx, self.currenty)

            queue = deque([start])
            visited = {start}
            track: Dict[Tuple[int, int], Tuple[int, int]] = {}

            while queue:
                current_pos = queue.popleft()
                # Found pacman
                if current_pos == (playerx, playery):
                    path = []
                    while current_pos in track:
                        path.append(current_pos)
                        current_pos = track[current_pos]
                    path.append(current_pos)
                    path.reverse()
                    if len(path) > 1:
                        cx, cy = path[1]
                        dx = cx - self.currentx
                        dy = cy - self.currenty
                        self.last_direction = self._direction_delta(dx, dy)

                        self.visualx = self.currentx
                        self.visualy = self.currenty
                        self.currentx, self.currenty = cx, cy
                        self.last_movement = now
                    break
                cx, cy = current_pos
                cell = maze[cy][cx]

                # N
                neighbor = (cx, cy - 1)
                if (cell & 1) == 0 and cy - 1 >= 0 and neighbor not in visited:
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

                # E
                neighbor = (cx + 1, cy)
                if (
                    (cell & 2) == 0
                    and cx + 1 < width
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

                # S
                neighbor = (cx, cy + 1)
                if (
                    (cell & 4) == 0
                    and cy + 1 < height
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

                # W
                neighbor = (cx - 1, cy)
                if (cell & 8) == 0 and cx - 1 >= 0 and neighbor not in visited:
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)
            self.last_movement = now
            self.rect = self.get_current_rect()


class Clyde(Ghost):

    OPPOSITE = {
        "N": "S",
        "S": "N",
        "E": "W",
        "W": "E",
    }

    def __init__(
            self,
            cornerx: int,
            cornery: int,
            last_movement: int,
            cooldown: int) -> None:
        """Create Clyde with his sprite frames."""
        self.frames = CLYDE_FRAMES
        self.rect = None
        super().__init__(cornerx, cornery, last_movement, cooldown)

    def move(
            self,
            maze: List[List[int]],
            width: int,
            height: int,
            playerx: int,
            playery: int,
            now: int) -> None:
        """Chase the player, but retreat to his corner when too close."""
        if self.ghoststate == GhostState.EATEN:
            self.move_back_to_home(maze, width, height, now)
        elif self.ghoststate == GhostState.FRIGHTENED:
            assert self.frightened_start is not None
            if now - self.frightened_start > self.frightened_duration:
                self.set_state(GhostState.NORMAL, now)
            elif now - self.last_movement >= self.cooldown:
                self.move_random_direction(maze, width, height, now)
        elif self.ghoststate == GhostState.NORMAL:
            if now - self.last_movement < self.cooldown:
                return
            distances = {
                "N": float("inf"),
                "S": float("inf"),
                "W": float("inf"),
                "E": float("inf"),
            }
            dist = self._distance_to_target(
                self.currentx, self.currenty, playerx, playery, 1
            )
            self.target = TARGET.HOME if dist <= 16 else TARGET.PACMAN
            cell = maze[self.currenty][self.currentx]
            # decide where to move
            # N
            if (
                self.last_direction != "S"
                and (cell & 1) == 0
                and self.currenty - 1 >= 0
            ):
                distances["N"] = self._distance_to_target(
                    self.currentx, self.currenty - 1, playerx, playery
                )
            # E
            if (
                self.last_direction != "W"
                and (cell & 2) == 0
                and self.currentx + 1 < width
            ):
                distances["E"] = self._distance_to_target(
                    self.currentx + 1, self.currenty, playerx, playery
                )
            # S
            if (
                self.last_direction != "N"
                and (cell & 4) == 0
                and self.currenty + 1 < height
            ):
                distances["S"] = self._distance_to_target(
                    self.currentx, self.currenty + 1, playerx, playery
                )
            # W
            if (
                self.last_direction != "E"
                and (cell & 8) == 0
                and self.currentx - 1 >= 0
            ):
                distances["W"] = self._distance_to_target(
                    self.currentx - 1, self.currenty, playerx, playery
                )
            # optimal
            mindistance = min(distances.values())
            if mindistance == float("inf"):
                # Dead end: no direction is legal except reversing.
                # check the single reversed direction against the actual walls
                # before committing to it.
                fallback = self.OPPOSITE.get(self.last_direction)
                if fallback is None:
                    # No previous direction recorded  and
                    # nothing legal was found  nowhere to go, stay put.
                    return
                fallback_ok = {
                    "N": (cell & 1) == 0 and self.currenty - 1 >= 0,
                    "E": (cell & 2) == 0 and self.currentx + 1 < width,
                    "S": (cell & 4) == 0 and self.currenty + 1 < height,
                    "W": (cell & 8) == 0 and self.currentx - 1 >= 0,
                }[fallback]
                if not fallback_ok:
                    # Truly boxed in on all sides — don't move.
                    return
                key = fallback
            else:
                key = next(k for k, v in distances.items() if v == mindistance)
            self.last_direction = key
            x, y = DIRECTIONS[key]
            self.visualx, self.visualy = self.currentx, self.currenty
            self.currentx += x
            self.currenty += y
            self.last_movement = now

    def _distance_to_target(
            self,
            currentx: int,
            currenty: int,
            playerx: int,
            playery: int,
            player: int = 0) -> int:
        """Return the squared distance to the player or to Clyde's corner."""
        if self.target == TARGET.PACMAN or player:
            return (currentx - playerx) ** 2 + (currenty - playery) ** 2
        return (currentx - self.cornerx) ** 2 + (currenty - self.cornery) ** 2


class Pinky(Ghost):

    DIRECTIONS = {
        "N": (-4, -4),
        "S": (0, +4),
        "W": (-4, 0),
        "E": (+4, 0),
    }

    def __init__(
            self,
            cornerx: int,
            cornery: int,
            last_movement: int,
            cooldown: int) -> None:
        """Create Pinky with her sprite frames."""
        self.frames = PINKY_FRAMES
        self.rect = None
        super().__init__(cornerx, cornery, last_movement, cooldown)

    def move(
            self,
            maze: List[List[int]],
            width: int,
            height: int,
            playerx: int,
            playery: int,
            direction: str,
            now: int) -> None:
        """Path toward the cell four tiles ahead of the player via BFS."""
        if self.ghoststate == GhostState.EATEN:
            self.move_back_to_home(maze, width, height, now)
        elif self.ghoststate == GhostState.FRIGHTENED:
            assert self.frightened_start is not None
            if now - self.frightened_start > self.frightened_duration:
                self.set_state(GhostState.NORMAL, now)
            elif now - self.last_movement >= self.cooldown:
                self.move_random_direction(maze, width, height, now)
        elif self.ghoststate == GhostState.NORMAL:
            if now - self.last_movement < self.cooldown:
                return
            target_pos = self._gettarget(
                width,
                height,
                playerx,
                playery,
                direction)
            start = (self.currentx, self.currenty)

            queue = deque([start])
            visited = {start}
            track = {}

            best_pos = start
            best_distance = (self.currentx - target_pos[0]) ** 2 + (
                self.currenty - target_pos[1]
            ) ** 2

            while queue:
                current_pos = queue.popleft()
                distance = (current_pos[0] - target_pos[0]) ** 2 + (
                    current_pos[1] - target_pos[1]
                ) ** 2
                # print("queue"queue)
                if distance < best_distance:
                    best_distance = distance
                    best_pos = current_pos

                cx, cy = current_pos
                cell = maze[cy][cx]

                # N
                neighbor = (cx, cy - 1)
                if (cell & 1) == 0 and cy - 1 >= 0 and neighbor not in visited:
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

                    # E
                neighbor = (cx + 1, cy)
                if (
                    (cell & 2) == 0
                    and cx + 1 < width
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

                    # S
                neighbor = (cx, cy + 1)
                if (
                    (cell & 4) == 0
                    and cy + 1 < height
                    and neighbor not in visited
                ):
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

                    # W
                neighbor = (cx - 1, cy)
                if (cell & 8) == 0 and cx - 1 >= 0 and neighbor not in visited:
                    visited.add(neighbor)
                    track[neighbor] = current_pos
                    queue.append(neighbor)

            path = []
            while best_pos != start:
                path.append(best_pos)
                best_pos = track[best_pos]
            path.append(best_pos)
            path.reverse()
            if len(path) > 1:
                cx, cy = path[1]
                dx = cx - self.currentx
                dy = cy - self.currenty
                self.last_direction = self._direction_delta(dx, dy)
                self.visualx, self.visualy = self.currentx, self.currenty
                self.currentx = cx
                self.currenty = cy
            self.last_movement = now

    def _gettarget(
            self,
            width: int,
            height: int,
            playerx: int,
            playery: int,
            direction: str) -> Tuple[int, int]:
        """Return the cell ahead of the player, clamped inside the maze."""
        dx, dy = self.DIRECTIONS[direction]

        targetx, targety = playerx + dx, playery + dy
        if targetx < 0:
            targetx = 0
        elif targetx >= width:
            targetx = width - 1

        if targety < 0:
            targety = 0
        elif targety >= height:
            targety = height - 1

        return (targetx, targety)


class Inky(Ghost):

    DIRECTIONS = {
        "N": (0, -2),
        "S": (0, +2),
        "W": (-2, 0),
        "E": (+2, 0),
    }

    def __init__(
            self,
            cornerx: int,
            cornery: int,
            last_movement: int,
            cooldown: int) -> None:
        """Create Inky with his sprite frames."""
        self.frames = INKY_FRAMES
        self.rect = None
        super().__init__(cornerx, cornery, last_movement, cooldown)

    def move(
        self,
        maze: List[List[int]],
        width: int,
        height: int,
        playerx: int,
        playery: int,
        direction: str,
        blinkyx: int,
        blinky_y: int,
        now: int
    ) -> None:
        """Target a cell derived from the player's position and Blinky's."""
        if self.ghoststate == GhostState.EATEN:
            self.move_back_to_home(maze, width, height, now)
        elif self.ghoststate == GhostState.FRIGHTENED:
            assert self.frightened_start is not None
            if now - self.frightened_start > self.frightened_duration:
                self.set_state(GhostState.NORMAL, now)
            elif now - self.last_movement >= self.cooldown:
                self.move_random_direction(maze, width, height, now)
        elif self.ghoststate == GhostState.NORMAL:
            if now - self.last_movement < self.cooldown:
                return
            tx, ty = self._get_target(
                width, height, playerx, playery, direction, blinkyx, blinky_y
            )

            self._move_towards_target(maze, width, height, tx, ty, now)

    def _get_target(
        self,
        width: int,
        height: int,
        playerx: int,
        playery: int,
        direction: str,
        blinkyx: int,
        blinky_y: int
    ) -> Tuple[int, int]:
        """Double the vector from Blinky to the tile ahead of the player."""
        # 1. Find the tile two spaces in front of Pac-Man
        dx, dy = self.DIRECTIONS[direction]

        targetx = playerx + dx
        targety = playery + dy

        # Keep target inside maze
        targetx = max(0, min(targetx, width - 1))
        targety = max(0, min(targety, height - 1))

        # 2. Vector from Blinky to that target
        vectorx = targetx - blinkyx
        vectory = targety - blinky_y

        # 3. Double the vector
        targetx += vectorx
        targety += vectory

        # Keep final target inside maze
        targetx = max(0, min(targetx, width - 1))
        targety = max(0, min(targety, height - 1))

        return targetx, targety

    def _move_towards_target(
            self,
            maze: List[List[int]],
            width: int,
            height: int,
            targetx: int,
            targety: int,
            now: int) -> None:
        """Step to the open neighbor closest to the target,
        allowing reverse."""
        cell = maze[self.currenty][self.currentx]

        distances = {
            "N": float("inf"),
            "E": float("inf"),
            "S": float("inf"),
            "W": float("inf"),
        }

        # N
        if self.last_direction != "S":
            if (cell & 1) == 0 and self.currenty - 1 >= 0:
                nx = self.currentx
                ny = self.currenty - 1
                distances["N"] = (nx - targetx) ** 2 + (ny - targety) ** 2

        # E
        if self.last_direction != "W":
            if (cell & 2) == 0 and self.currentx + 1 < width:
                nx = self.currentx + 1
                ny = self.currenty
                distances["E"] = (nx - targetx) ** 2 + (ny - targety) ** 2

        # S
        if self.last_direction != "N":
            if (cell & 4) == 0 and self.currenty + 1 < height:
                nx = self.currentx
                ny = self.currenty + 1
                distances["S"] = (nx - targetx) ** 2 + (ny - targety) ** 2

        # W
        if self.last_direction != "E":
            if (cell & 8) == 0 and self.currentx - 1 >= 0:
                nx = self.currentx - 1
                ny = self.currenty
                distances["W"] = (nx - targetx) ** 2 + (ny - targety) ** 2

        # Pick closest legal direction
        mindistance = min(distances.values())
        if mindistance == float("inf"):
            # Dead end: allow reversing
            opposite = {
                "N": "S",
                "S": "N",
                "E": "W",
                "W": "E",
            }

            key = opposite[self.last_direction]

        else:
            key = min(distances, key=lambda k: distances[k])

        self.last_direction = key

        dx, dy = DIRECTIONS[key]
        self.visualx, self.visualy = self.currentx, self.currenty
        self.currentx += dx
        self.currenty += dy

        self.last_movement = now

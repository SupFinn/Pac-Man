from enum import Enum
from src.entities.player import Player
from src.entities.level import Level
from src.entities.ghosts import Blinky, Clyde, Ghost, Pinky, GhostState, Inky
import pygame
from pathlib import Path
import json
import bisect
from src.media.constants import (COUNTDOWN_START, CHEAT_POPUP_DURATION_MS,
                                 WIN_LEVEL)
import random
from typing import Any, List, Optional, Tuple, Dict
from src.media.render import IconSheet
from src.media.media import AudioManager


class Gamestate(Enum):
    LOST = "lost"
    WIN = "win"
    START = "start"
    COUNTDOWN = "countdown"
    LEVEL_WIN = "level_win"


ARROW_KEYS = {
    pygame.K_UP: "N",
    pygame.K_DOWN: "S",
    pygame.K_LEFT: "W",
    pygame.K_RIGHT: "E",
}
WASD_KEYS = {
    pygame.K_w: "N",
    pygame.K_s: "S",
    pygame.K_a: "W",
    pygame.K_d: "E",
}


class GameState:
    def __init__(self, data: Dict[str, Any], audio: AudioManager) -> None:
        """Load the levels from the config and set up the game state."""
        self.audio = audio
        self.data = data
        self.levels = self.levels_generator(data)
        self.level_index = 0
        self.current_level = self.levels[self.level_index]

        self.player: Player
        self.player2: Player
        self.clyde: Clyde
        self.blinky: Blinky
        self.pinky: Pinky
        self.inky: Inky

        self.ghosts: Optional[List[Ghost]] = None
        self.game_state: Gamestate = Gamestate.COUNTDOWN
        self.current_level.start_time = None
        self.time_remaining = self.current_level.max_time

        self.move_next_level = 0
        self.player_direction = "N"
        self.player2_direction = "S"
        self.score_file = data["highscore_filename"]
        self.two_players = False
        self.score = 0
        self.line = 0
        self.gums_eaten = 0
        self.ghosts_eaten = {"blinky": 0, "clyde": 0, "pinky": 0, "inky": 0}
        self.countdown_start = 0

        self.is_door_open = False
        self.unlocked_levels = 1

        # cheat mode
        self.cheat_god_mode = False
        self.cheat_freeze_ghosts = False
        self.cheat_invisible = False

        self.game_start_time = 0
        self.total_elapsed_seconds = 0

        self.pending_skip_until: int | None = None
        self.countdown_sound_played = False

        self.game_won = False
        self.warning_playing = False

        self.death_at: int | None = None
        self.pause_started: int | None = None

    def characteres_init(
            self,
            player_image: Tuple[IconSheet, Dict[str, List[pygame.Rect]]],
            player2_image: Tuple[IconSheet, Dict[str, List[pygame.Rect]]],
            is_multiplayer: bool) -> None:
        """Create the ghosts and players and reset the run timers."""
        width = self.levels[self.level_index].width
        height = self.levels[self.level_index].height
        init_time = pygame.time.get_ticks()
        x, y = self._find_spawn_point()

        self.clyde = Clyde(0, height - 1, init_time, 700)
        self.blinky = Blinky(width - 1, 0, init_time, 700)
        self.pinky = Pinky(0, 0, init_time, 700)
        self.inky = Inky(width - 1, height - 1, init_time, 700)
        self.player = Player("eyomi", player_image[0], player_image[1], x, y)
        self.ghosts = [self.blinky, self.clyde, self.pinky, self.inky]
        self.is_paused = False
        self.pause_started = None
        self.current_level.generate_gums()
        self.paused_total = 0
        self.countdown = COUNTDOWN_START
        self.countdown_start = init_time
        self.game_start_time = init_time
        self.two_players = is_multiplayer

        if self.two_players:
            self.player2 = Player(
                "eyomi", player2_image[0], player2_image[1], x, y + 1)
            self.two_players = is_multiplayer

    def _count_down_handler(self) -> None:
        """Tick the pre-level countdown and start play when it ends."""
        now = pygame.time.get_ticks()
        elapsed = now - self.countdown_start

        self.countdown = COUNTDOWN_START - elapsed // 1000

        if self.countdown <= 0:
            self.countdown = 0
            self.game_state = Gamestate.START
            assert self.ghosts is not None
            for ghost in self.ghosts:
                ghost.last_movement = now
            assert self.current_level.start_time is not None
            if self.death_at is not None:
                self.current_level.start_time += now - self.death_at
                self.death_at = None
            else:
                self.current_level.start_time = now
        if not self.countdown_sound_played:
            self.countdown_sound_played = True
            self.audio.play("countdown")

    def update(self) -> None:
        """Advance the timer, gums, ghosts, collisions and win checks."""
        now = pygame.time.get_ticks()

        if self.is_paused:
            if self.pause_started is None:
                self.pause_started = now
            self._stop_warning()
            return
        if self.pause_started is not None:
            self._shift_timers(now - self.pause_started)
            self.pause_started = None

        if self.game_state == Gamestate.COUNTDOWN:
            self._count_down_handler()
            return

        assert self.current_level.start_time is not None
        elapsed_seconds = (
            (now - self.paused_total) - self.current_level.start_time
        ) // 1000
        remaining = self.current_level.max_time - elapsed_seconds
        self.time_remaining = max(0, remaining)
        self.total_elapsed_seconds = max(
            0, ((now - self.paused_total) - self.game_start_time) // 1000
        )

        if 0 < self.time_remaining <= 10:
            if not self.warning_playing:
                self.warning_playing = True
                self.audio.play("time_warning")

        if self.time_remaining == 0:
            self.score += self.current_level.collected_score
            self.game_state = Gamestate.LOST
            self._stop_warning()
            self.audio.play("level_lost")
            return

        self._check_gum_eating()
        self._move_ghosts(now)
        self._check_collisions()
        if (self.pending_skip_until is not None
                and now >= self.pending_skip_until):
            self.pending_skip_until = None
            self.move_next_level = 1

        if self.move_next_level:
            self.move_next_level = 0
            self._stop_warning()
            self.audio.play("level_win")
            if (self.level_index + 1 >= len(self.levels)
                    or self.level_index + 1 == WIN_LEVEL):
                self.game_state = Gamestate.WIN
                self.game_won = True
                self.unlocked_levels = max(
                    self.unlocked_levels,
                    min(self.level_index + 2, len(self.levels)),
                )
            else:
                self.game_state = Gamestate.LEVEL_WIN
                level_index = self.level_index + 2
                self.unlocked_levels = max(self.unlocked_levels, level_index)
            self.score += self.current_level.collected_score

    def _stop_warning(self) -> None:
        """Stop the low-time warning sound."""
        self.audio.stop("time_warning")
        self.warning_playing = False

    def _shift_timers(self, paused_ms: int) -> None:
        """Move the timer anchors forward so paused time is not counted."""
        if self.current_level.start_time is not None:
            self.current_level.start_time += paused_ms
        self.game_start_time += paused_ms

    def update_held_movement(self, held_keys: List[int]) -> None:
        """Repeat player movement while direction keys stay held."""
        if self.game_state != Gamestate.START or self.is_paused:
            return
        now = pygame.time.get_ticks()

        if self.two_players:
            arrow = next((k for k in reversed(held_keys)
                          if k in ARROW_KEYS), None)
            wasd = next((k for k in reversed(held_keys)
                         if k in WASD_KEYS), None)
            if arrow is not None and (
                now - self.player.last_movement >= self.player.move_speed_ms
            ):
                self.move_player(arrow)
            if wasd is not None and (
                now - self.player2.last_movement >= self.player2.move_speed_ms
            ):
                self.move_player(wasd)
        elif held_keys:
            if now - self.player.last_movement >= self.player.move_speed_ms:
                self.move_player(held_keys[-1])

    def move_player(self, event_key: int) -> None:
        """Move the matching player for a pressed direction key."""
        if self.game_state != Gamestate.START:
            return
        now = pygame.time.get_ticks()
        if self.is_paused is False:
            if self.two_players:
                if event_key in ARROW_KEYS:
                    self._move_single_player(
                        self.player, ARROW_KEYS[event_key], self.player2, now
                    )
                    self.player_direction = ARROW_KEYS[event_key]
                elif event_key in WASD_KEYS:
                    self._move_single_player(
                        self.player2, WASD_KEYS[event_key], self.player, now
                    )
                    self.player2_direction = WASD_KEYS[event_key]
            else:
                direction = (ARROW_KEYS.get(event_key) or
                             WASD_KEYS.get(event_key))
                if direction is not None:
                    self._move_single_player(self.player, direction, None, now)
                    self.player_direction = direction

    def _move_single_player(
            self,
            player: Player,
            direction: str,
            other_player: Optional[Player],
            now: int) -> None:
        """Move one player a cell if walls and the other player allow."""
        level = self.current_level
        moved = False

        if direction == "N":
            target = (player.currentx, player.currenty - 1)
            if (
                player.currenty - 1 >= 0
                and (level.maze[player.currenty][player.currentx] & 1 == 0)
                and not self._occupied_by(other_player, target)
            ):
                player.visualx = player.currentx
                player.visualy = player.currenty
                player.currenty -= 1
                moved = True

        elif direction == "S":
            target = (player.currentx, player.currenty + 1)
            if (
                player.currenty + 1 < level.height
                and (level.maze[player.currenty][player.currentx] & 4 == 0)
                and not self._occupied_by(other_player, target)
            ):
                player.visualx = player.currentx
                player.visualy = player.currenty
                player.currenty += 1
                moved = True

        elif direction == "W":
            if (
                player.currentx == 0
                and level.height // 2 == player.currenty
                and self.is_door_open is True
            ):
                target = (level.width - 1, player.currenty)
                if not self._occupied_by(other_player, target):
                    player.visualx = player.currentx
                    player.visualy = player.currenty
                    player.currentx = level.width - 1
                    moved = True
            else:
                target = (player.currentx - 1, player.currenty)
                if (
                    player.currentx - 1 >= 0
                    and (level.maze[player.currenty][player.currentx] & 8 == 0)
                    and not self._occupied_by(other_player, target)
                ):
                    player.visualx = player.currentx
                    player.visualy = player.currenty
                    player.currentx -= 1
                    moved = True

        elif direction == "E":
            if (
                player.currentx == level.width - 1
                and level.height // 2 == player.currenty
                and self.is_door_open is True
            ):
                target = (0, player.currenty)
                if not self._occupied_by(other_player, target):
                    player.visualx = player.currentx
                    player.visualy = player.currenty
                    player.currentx = 0
                    moved = True
            else:
                target = (player.currentx + 1, player.currenty)
                if (
                    player.currentx + 1 < level.width
                    and (level.maze[player.currenty][player.currentx] & 2 == 0)
                    and not self._occupied_by(other_player, target)
                ):
                    player.visualx = player.currentx
                    player.visualy = player.currenty
                    player.currentx += 1
                    moved = True

        player.direction = (
            direction  # face this way even if the move was blocked by a wall
        )
        if moved:
            player.last_movement = now
            if abs(player.currentx - player.visualx) > 1:
                self.audio.play("door")

    def _occupied_by(
            self,
            other_player: Optional[Player],
            target_pos: Tuple[int, int]) -> bool:
        """Return True if the other player stands on the target cell."""
        if other_player is None:
            return False
        return (other_player.currentx, other_player.currenty) == target_pos

    def next_level(self, level_index: int) -> None:
        """Reset the ghosts, players, gums and timer for a level."""
        if level_index == len(self.levels):
            self.game_state = Gamestate.WIN
            return
        now = pygame.time.get_ticks()
        self.countdown = COUNTDOWN_START
        self.countdown_sound_played = False
        self.game_state = Gamestate.COUNTDOWN
        self.countdown_start = now
        self.death_at = None

        self._stop_warning()

        self.move_next_level = 0
        self.level_index = level_index

        self.current_level = self.levels[self.level_index]
        self.current_level.collected_score = 0
        self.current_level.start_time = now
        self.current_level.generate_gums()
        self.time_remaining = self.current_level.max_time
        self.is_door_open = False

        self.clyde.resetGhostPosition(0, self.current_level.height - 1)
        self.blinky.resetGhostPosition(self.current_level.width - 1, 0)
        self.pinky.resetGhostPosition(0, 0)
        self.inky.resetGhostPosition(
            self.current_level.width - 1, self.current_level.height - 1
        )

        x, y = self._find_spawn_point()
        self.player.update_position(x, y)
        self.player.reset()
        if self.two_players:
            self.player2.update_position(x, y + 1)
            self.player2.reset()
        assert self.ghosts is not None
        for ghost in self.ghosts:
            ghost.set_state(GhostState.NORMAL)
            ghost.apply_level_speed(self.level_index)

    def _closest_player(self, ghost: Ghost) -> Tuple[Tuple[int, int], str]:
        """Return the position and direction of the player nearest a ghost."""
        if self.cheat_invisible:
            level = self.current_level
            pos = (random.randrange(level.width),
                   random.randrange(level.height))
            direction = random.choice(["N", "S", "E", "W"])
            return pos, direction
        if not self.two_players:
            pos = (self.player.currentx, self.player.currenty)
            return pos, self.player_direction

        dist_p1 = (ghost.currentx - self.player.currentx) ** 2 + (
            ghost.currenty - self.player.currenty
        ) ** 2
        dist_p2 = (ghost.currentx - self.player2.currentx) ** 2 + (
            ghost.currenty - self.player2.currenty
        ) ** 2

        if dist_p1 <= dist_p2:
            pos = (self.player.currentx, self.player.currenty)
            return pos, self.player_direction
        return ((self.player2.currentx, self.player2.currenty),
                self.player2_direction)

    def _move_ghosts(self, now: int) -> None:
        """Run each ghost's movement unless frozen or not started."""
        if self.game_state != Gamestate.START or self.cheat_freeze_ghosts:
            return
        maze = self.current_level.maze
        width = self.current_level.width
        height = self.current_level.height

        clyde_target, _ = self._closest_player(self.clyde)
        self.clyde.move(maze,
                        width,
                        height, clyde_target[0], clyde_target[1], now)

        blinky_target, _ = self._closest_player(self.blinky)
        self.blinky.move(maze,
                         width,
                         height, blinky_target[0], blinky_target[1], now)

        pinky_target, pinky_direction = self._closest_player(self.pinky)
        self.pinky.move(
            maze,
            width,
            height, pinky_target[0], pinky_target[1], pinky_direction, now
        )

        inky_target, inky_direction = self._closest_player(self.inky)
        self.inky.move(
            maze,
            width,
            height,
            inky_target[0],
            inky_target[1],
            inky_direction,
            self.blinky.currentx,
            self.blinky.currenty,
            now,
        )

    def _check_gum_eating(self) -> None:
        """Eat gums, super gums and the key, and detect a cleared maze."""
        assert self.player is not None
        assert self.ghosts is not None

        players = [self.player]

        if self.two_players:
            players.append(self.player2)

        for player in players:
            pos = (player.currentx, player.currenty)

            if pos in self.current_level.supergums:
                self.audio.play("super_gum")
                now = pygame.time.get_ticks()

                for ghost in self.ghosts:
                    if ghost.ghoststate != GhostState.EATEN:
                        ghost.set_state(GhostState.FRIGHTENED, now)

                self.current_level.collected_score += (
                    self.current_level.points_per_super_pacgum
                )
                self.gums_eaten += 1
                self.current_level.supergums.remove(pos)

            elif pos in self.current_level.gums:
                self.audio.play("gum")
                self.current_level.collected_score += (
                    self.current_level.points_per_pacgum
                )
                self.gums_eaten += 1
                self.current_level.gums.remove(pos)

            if self.is_door_open is False:
                if self.current_level.key == pos:
                    self.is_door_open = True
                    self.audio.play("key")

        if not self.current_level.supergums and not self.current_level.gums:
            self.move_next_level = 1

    def _check_collisions(self) -> None:
        """Resolve ghost contact: lose a life or eat a frightened ghost."""
        if self.cheat_invisible:
            return
        now = pygame.time.get_ticks()
        collision_radius = 0.65
        assert self.player is not None
        assert self.ghosts is not None

        players = [self.player]
        if self.two_players:
            players.append(self.player2)

        for ghost in self.ghosts:
            gx, gy = ghost.get_visual_position(now)

            for player in players:
                dx = gx - player.currentx
                dy = gy - player.currenty
                dist_sq = dx * dx + dy * dy

                if dist_sq <= collision_radius**2:
                    if ghost.ghoststate == GhostState.NORMAL:
                        if self.cheat_god_mode:
                            return
                        if self.player.lives - 1 > 0:
                            self.player.lives -= 1
                            self.death_at = now
                            self._stop_warning()
                            for ghost in self.ghosts:
                                ghost.resetGhostPosition(ghost.cornerx,
                                                         ghost.cornery)
                            x, y = self._find_spawn_point()
                            self.player.update_position(x, y)
                            if self.two_players:
                                self.player2.update_position(x, y + 1)
                            self.game_state = Gamestate.COUNTDOWN
                            self.countdown = COUNTDOWN_START
                            self.countdown_sound_played = False
                            self.countdown_start = pygame.time.get_ticks()
                            return
                        else:
                            self.game_state = Gamestate.LOST
                            self.score += self.current_level.collected_score
                            self._stop_warning()
                            self.audio.play("level_lost")
                            return
                    elif ghost.ghoststate == GhostState.FRIGHTENED:
                        if now < ghost.eat_cooldown:
                            continue
                        self.audio.play("ghost_eaten")
                        self.current_level.collected_score += (
                            self.current_level.points_per_ghost
                        )
                        ghost_name = ghost.__class__.__name__.lower()
                        self.ghosts_eaten[ghost_name] += 1
                        ghost.set_state(GhostState.EATEN)

    def toggle_cheat(self, name: str) -> None:
        """Switch one cheat on or off, turning the others off."""
        attrs = {
            "invisible": "cheat_invisible",
            "god_mode": "cheat_god_mode",
            "freeze": "cheat_freeze_ghosts",
        }
        target = attrs[name]
        turning_on = not getattr(self, target)
        for attr in attrs.values():
            setattr(self, attr, False)
        if turning_on:
            setattr(self, target, True)
            self.audio.play(name)

    def request_skip_level(self) -> None:
        """Clear the active cheats and schedule a level skip."""
        now = pygame.time.get_ticks()
        self.cheat_invisible = False
        self.cheat_god_mode = False
        self.cheat_freeze_ghosts = False
        self.pending_skip_until = now + CHEAT_POPUP_DURATION_MS

    def active_cheat(self) -> str | None:
        """Return the name of the active cheat, or None."""
        if self.cheat_invisible:
            return "invisible"
        if self.cheat_god_mode:
            return "god_mode"
        if self.cheat_freeze_ghosts:
            return "freeze"
        return None

    def _find_spawn_point(self) -> Tuple[int, int]:
        """Find the open cell nearest the maze center for the player."""
        height = self.current_level.height
        width = self.current_level.width
        cy = height // 2
        cx = width // 2

        for offset in range(width):
            for x in (cx - offset, cx + offset):
                if 0 <= x < width and self.current_level.maze[cy][x] != 15:
                    return x, cy
        return 0, 0

    def game_reset(self) -> None:
        """Reset the scores, stats and levels and restart the run."""
        for level in self.levels:
            level.generate_gums()
            level.collected_score = 0
        start = 0
        if (self.game_won and WIN_LEVEL < len(self.levels)
                and self.level_index >= WIN_LEVEL):
            start = WIN_LEVEL
        self.next_level(start)
        self.score = 0
        self.gums_eaten = 0
        if not self.game_won:
            self.unlocked_levels = 1
        self.ghosts_eaten = {"blinky": 0, "clyde": 0, "pinky": 0, "inky": 0}
        self.game_start_time = pygame.time.get_ticks()
        self.paused_total = 0

    def levels_generator(self, data: Dict[str, Any]) -> List[Level]:
        """Build a Level object for each level in the config."""
        levels = []
        i = 0
        while i < len(self.data["levels"]):
            level = Level(
                i + 1,
                data["levels"][i]["width"],
                data["levels"][i]["height"],
                data["points_per_pacgum"],
                data["points_per_super_pacgum"],
                data["points_per_ghost"],
                data["levels"][i]["max_time"],
                data["seed"],
            )
            levels.append(level)
            i += 1
        return levels

    def load_scores(self) -> list[tuple[int, str]]:
        """Read the saved scores from the high score file."""
        file_path = self.score_file
        try:
            path = Path(file_path)
            path.parent.mkdir(parents=True, exist_ok=True)

            if path.exists() and path.stat().st_size > 0:
                with open(path, "r", encoding="utf-8") as f:
                    scores = [
                        (int(entry["score"]), entry["name"])
                        for entry in json.load(f)
                    ]
            else:
                scores = []
            return scores

        except PermissionError:
            raise Exception(
                f"You don't have permission to write to '{file_path}'"
            )
        except FileNotFoundError:
            raise Exception(f"Invalid output path: '{file_path}'")
        except json.JSONDecodeError:
            raise Exception(f"'{file_path}' contains invalid JSON")
        except OSError as e:
            raise Exception(f"Could not write output file '{file_path}': {e}")

    def insert_score(self) -> None:
        """Add the current score to the top ten and save the file."""
        file_path = self.score_file
        try:
            scores = self.load_scores()

            if len(scores) >= 10:
                if self.score <= scores[0][0]:
                    return
                scores.pop(0)

            entry = (self.score, self.player.name)
            bisect.insort_left(scores, entry)

            data = [{"name": name, "score": score} for score, name in scores]
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)

        except PermissionError:
            raise Exception(
                f"You don't have permission to write to '{file_path}'"
            )
        except FileNotFoundError:
            raise Exception(f"Invalid output path: '{file_path}'")
        except json.JSONDecodeError:
            raise Exception(f"'{file_path}' contains invalid JSON")
        except OSError as e:
            raise Exception(f"Could not write output file '{file_path}': {e}")

from typing import Any, cast

import pygame

from src.game.gameplay import Gamestate, GameState
from src.media.render import (
    gums,
    score_img,
    timer,
    fonts,
    ghosts,
    buttons,
    gameover_icons,
    key_icon,
    cheat_icons,
    pause_icon,
    images,
    paint,
)
from src.media import constants
from src.media import render
from src.entities.ghosts import GhostState


GHOST_STAT_ICONS: dict[str, pygame.Rect] = {
    "blinky": constants.BLINKY_FRAMES["E"][0],
    "clyde": constants.CLYDE_FRAMES["E"][0],
    "pinky": constants.PINKY_FRAMES["E"][0],
    "inky": constants.INKY_FRAMES["E"][0],
}


class Plying:
    def __init__(
        self, screen: pygame.Surface, game: GameState, video: Any
    ) -> None:
        """Store screen, game and video and set up the gameplay UI state."""
        self.screen = screen
        self.game: GameState = game

        self.video = video
        self.line = 0
        self.offset_x = 0
        self.offset_y = 0
        self.padding_y = 0

        self.entered_name = ""
        self.name_done = False

        self.heart = images.load_by_width(
            constants.HEART_FILE, constants.HEART_WIDTH
        )

        self.submit_rect: pygame.Rect | None = None

        self.retry_rect: pygame.Rect | None = None
        self.next_rect: pygame.Rect | None = None
        self.back_rect: pygame.Rect | None = None

        self.pause_button_rects: list[tuple[pygame.Rect, str]] = []
        self.pause_selected_index: int = 0

        self.cheat_popup_name: str | None = None
        self.cheat_popup_until: int = 0

        self.pause_button_rect: pygame.Rect | None = None

        self.top_panel_until: int = 0

    def _calculate_maze_layout(self) -> None:
        """Compute the cell size and the maze offsets to center it on the
        video."""
        video_y = self.video.offset_y
        self.padding_y = 30

        maze = self.game.current_level.maze

        maze_width = len(maze[0])
        maze_height = len(maze)

        video_width = self.video.display_width
        video_height = self.video.display_height
        available_height = video_height - (self.padding_y * 2)

        scale_x = (video_width * constants.MAZE_MAX_WIDTH_RATIO) / maze_width
        scale_y = (
            available_height * constants.MAZE_MAX_HEIGHT_RATIO
        ) / maze_height

        self.line = max(1, int(min(scale_x, scale_y)))
        self.game.line = self.line

        maze_pixel_width = maze_width * self.line
        maze_pixel_height = maze_height * self.line

        self.offset_x = (video_width - maze_pixel_width) // 2
        self.offset_y = (
            video_y
            + self.padding_y
            + (available_height - maze_pixel_height) // 2
        )

    def draw(self) -> None:
        """Update the game unless it has ended, then render the frame."""
        if self.game.game_state not in [
            Gamestate.LOST,
            Gamestate.WIN,
            Gamestate.LEVEL_WIN,
        ]:
            self.game.update()
        self.render()

    def coordinates_converter(
        self, coordinates: tuple[float, float]
    ) -> tuple[float, float]:
        """Convert grid coordinates to the screen pixel center of that cell."""
        currentx, currenty = coordinates

        x = self.offset_x + (currentx * self.line) + (self.line // 2)
        y = self.offset_y + (currenty * self.line) + (self.line // 2)

        return (x, y)

    def render(self) -> None:
        """Draw the screen matching the state: lost, win, level win or the
        game."""
        state = self.game.game_state
        if state == Gamestate.LOST:
            self.draw_lost()
        elif state == Gamestate.WIN:
            self.draw_win()
        elif state == Gamestate.LEVEL_WIN:
            self.draw_level_win()
        else:
            self._gui_draw()
            self._panel_draw()
            self._draw_maze()
            self._draw_side_info()
            self._draw_gums_and_key()
            self._draw_player()
            self._draw_ghosts()
            flashing = pygame.time.get_ticks() < self.top_panel_until
            if flashing:
                self._panel_draw(
                    fill_alpha=constants.MAZE_TOP_PANEL_FILL_ALPHA_ACTIVE
                )
            self._draw_cheat_popup()
            if self.game.is_paused:
                self._pause_panel()
                return
            if self.game.countdown > 0:
                self._draw_countdown()

    def _draw_panel(self, padding_y: int) -> pygame.Rect:
        """Draw the centered end-screen panel and return its rect."""
        screen_rect = self.screen.get_rect()
        rect = pygame.Rect(
            0,
            0,
            constants.GAMEOVER_PANEL_WIDTH,
            screen_rect.height - padding_y * 2,
        )
        rect.center = screen_rect.center
        paint.panel(
            self.screen, rect,
            radius=constants.GAMEOVER_PANEL_RADIUS,
            fill_alpha=constants.GAMEOVER_PANEL_ALPHA,
            border_color=constants.GAMEOVER_PANEL_BORDER_COLOR,
        )
        self.gameover_rect = rect
        return rect

    def _draw_headline(
        self, rect: pygame.Rect, text: str, offset_y: int
    ) -> pygame.Rect:
        """Draw a headline at the top of the panel."""
        return paint.text(
            self.screen, fonts.get(constants.GAMEOVER_TITLE_FONT_SIZE),
            text, constants.GAMEOVER_TITLE_COLOR,
            "midtop", (rect.centerx, rect.top + offset_y), shadow=None
        )

    def draw_lost(self) -> None:
        """Draw the game over screen."""
        rect = self._draw_panel(constants.GAMEOVER_PANEL_PADDING_Y)
        self._draw_stats(rect)
        self._draw_name_entry()
        self._draw_gameover_buttons()

    def draw_win(self) -> None:
        """Draw the game won screen."""
        rect = self._draw_panel(constants.WIN_PANEL_PADDING_Y)
        self._draw_headline(rect, "YOU WON", constants.WIN_HEADLINE_OFFSET_Y)
        self._draw_name_entry(constants.WIN_NAME_BOX_OFFSET_Y)
        self._draw_gameover_buttons()

    def draw_level_win(self) -> None:
        """Draw the level completed screen."""
        self.submit_rect = None
        rect = self._draw_panel(constants.LEVEL_WIN_PANEL_PADDING_Y)
        headline_rect = self._draw_headline(
            rect, "PAC-TASTIC!", constants.LEVEL_WIN_HEADLINE_OFFSET_Y
        )
        hint_rect = paint.text(
            self.screen, fonts.get(constants.LEVEL_WIN_HINT_SIZE),
            constants.LEVEL_WIN_HINT_TEXT, constants.LEVEL_WIN_HINT_COLOR,
            "midtop",
            (
                rect.centerx,
                headline_rect.bottom + constants.LEVEL_WIN_HINT_TOP_GAP,
            ),
            shadow=None
        )
        buttons_center_y = (
            hint_rect.bottom
            + constants.LEVEL_WIN_HINT_BOTTOM_GAP
            + constants.GAMEOVER_BUTTON_HEIGHT // 2
        )
        self._draw_gameover_buttons(buttons_center_y)

    def _draw_countdown(self) -> None:
        """Draw the GET READY overlay with the countdown number."""
        if self.game.countdown <= 0:
            return

        panel_rect = pygame.Rect(
            self.offset_x - 20,
            self.offset_y - 20,
            len(self.game.current_level.maze[0]) * self.line + 40,
            len(self.game.current_level.maze) * self.line + 40,
        )

        paint.panel(
            self.screen, panel_rect,
            fill_alpha=constants.COUNTDOWN_OVERLAY_ALPHA,
            border_color=(0, 0, 0, 0),
        )

        center = panel_rect.center

        circle_size = constants.COUNTDOWN_CIRCLE_RADIUS * 2
        circle_surface = pygame.Surface(
            (circle_size, circle_size), pygame.SRCALPHA
        )
        circle_center = circle_surface.get_rect().center
        pygame.draw.circle(
            circle_surface,
            (0, 0, 0, constants.COUNTDOWN_CIRCLE_ALPHA),
            circle_center,
            constants.COUNTDOWN_CIRCLE_RADIUS,
        )
        pygame.draw.circle(
            circle_surface,
            constants.COUNTDOWN_CIRCLE_BORDER_COLOR,
            circle_center,
            constants.COUNTDOWN_CIRCLE_RADIUS,
            width=2,
        )
        self.screen.blit(
            circle_surface, circle_surface.get_rect(center=center)
        )

        paint.text(
            self.screen, fonts.get(constants.COUNTDOWN_LABEL_SIZE),
            constants.COUNTDOWN_LABEL_TEXT, constants.COUNTDOWN_LABEL_COLOR,
            "midbottom",
            (
                center[0],
                center[1]
                - constants.COUNTDOWN_CIRCLE_RADIUS
                - constants.COUNTDOWN_LABEL_GAP,
            ),
            shadow=None,
        )

        paint.text(
            self.screen, fonts.get(constants.COUNTDOWN_NUMBER_SIZE),
            str(self.game.countdown), constants.COUNTDOWN_NUMBER_COLOR,
            "center", center, shadow=constants.COUNTDOWN_NUMBER_SHADOW_OFFSET,
        )

    def _draw_ghosts(self) -> None:
        """Animate and draw all ghosts at their interpolated positions."""
        now = pygame.time.get_ticks()
        ghost_size = max(1, int(self.line * constants.GHOST_SIZE_RATIO))
        eyes_size = max(1, int(self.line * constants.EYES_SIZE_RATIO))
        assert self.game.ghosts is not None
        for ghost in self.game.ghosts:
            ghost.update_animation(now)
            rect = ghost.get_current_rect()
            size = (
                eyes_size
                if ghost.ghoststate == GhostState.EATEN
                else ghost_size
            )
            g = ghost.iconsheet.scaled_to_height(rect, size)
            vx, vy = ghost.get_visual_position(now)
            gx, gy = self.coordinates_converter((vx, vy))
            self.screen.blit(g, g.get_rect(center=(gx, gy)))

    def _draw_maze(self) -> None:
        """Draw the maze walls, the filled cells and the doors."""
        self._calculate_maze_layout()
        level = self.game.current_level
        maze = level.maze

        for iy, row in enumerate(maze):
            y = self.offset_y + iy * self.line
            for ix, cell in enumerate(row):
                x = self.offset_x + ix * self.line
                if cell == 15:
                    my_rect = pygame.Rect(x + 1, y + 1, self.line, self.line)
                    rect_surface = pygame.Surface(
                        my_rect.size, pygame.SRCALPHA
                    )
                    rect_surface.fill((196, 154, 108, 50))
                    self.screen.blit(rect_surface, my_rect.topleft)
                else:
                    if cell & 1:
                        pygame.draw.line(
                            self.screen, constants.WALLS_COLOR,
                            (x, y), (x + self.line, y),
                            constants.WALLS_WIDTH,
                        )
                    # E
                    if cell & 2:
                        if (iy != (len(maze) // 2) or (ix != len(row) - 1)):
                            pygame.draw.line(
                                self.screen, constants.WALLS_COLOR,
                                (x + self.line, y),
                                (x + self.line, y + self.line),
                                constants.WALLS_WIDTH,
                            )
                        if (
                            iy == (len(maze) // 2)
                            and self.game.is_door_open is False
                        ):
                            pygame.draw.line(
                                self.screen, constants.WALLS_COLOR,
                                (x + self.line, y),
                                (x + self.line, y + self.line),
                                constants.WALLS_WIDTH,
                            )
                    # S
                    if cell & 4:
                        pygame.draw.line(
                            self.screen, constants.WALLS_COLOR,
                            (x, y + self.line),
                            (x + self.line, y + self.line),
                            constants.WALLS_WIDTH,
                        )
                    # W
                    if cell & 8:
                        if (iy != (len(maze) // 2) or (ix != 0)):
                            pygame.draw.line(
                                self.screen, constants.WALLS_COLOR,
                                (x, y), (x, y + self.line),
                                constants.WALLS_WIDTH,
                            )
                        if (
                            iy == (len(maze) // 2)
                            and self.game.is_door_open is False
                        ):
                            pygame.draw.line(
                                self.screen, constants.WALLS_COLOR,
                                (x, y), (x, y + self.line),
                                constants.WALLS_WIDTH,
                            )

    def _draw_gums_and_key(self) -> None:
        """Draw the remaining gums, super gums and the key."""
        gum_size = max(1, int(self.line * constants.GUM_SIZE_RATIO))
        supergum_size = max(1, int(self.line * constants.SUPERGUM_SIZE_RATIO))
        key_size = max(1, int(self.line * constants.KEY_SIZE_RATIO))

        gum = gums.scaled_to_height(constants.GUM_RECT, gum_size)
        supergum = gums.scaled_to_height(
            constants.SUPERGUM_RECT, supergum_size
        )
        key = key_icon.scaled_to_height(
            pygame.Rect(319, 286, 897, 437), key_size
        )

        for g in self.game.current_level.gums:
            x, y = self.coordinates_converter(g)
            self.screen.blit(gum, gum.get_rect(center=(x, y)))

        for g in self.game.current_level.supergums:
            x, y = self.coordinates_converter(g)
            self.screen.blit(supergum, supergum.get_rect(center=(x, y)))

        if self.game.is_door_open is False:
            assert self.game.current_level.key is not None
            kx, ky = self.coordinates_converter(self.game.current_level.key)
            self.screen.blit(key, key.get_rect(center=(kx, ky)))

    def _draw_player(self) -> None:
        """Animate and draw the player(s), faded when invisible."""
        now = pygame.time.get_ticks()
        size = max(1, int(self.line * constants.PLAYER_SIZE_RATIO))

        player = self.game.player
        player.update_animation(now)
        rect = player.get_current_rect()
        sprite = player.iconsheet.scaled_to_height(rect, size)
        if self.game.cheat_invisible:
            sprite = sprite.copy()
            sprite.set_alpha(constants.INVISIBLE_PLAYER_ALPHA)
        vx, vy = player.get_visual_position(now)
        x, y = self.coordinates_converter((vx, vy))
        self.screen.blit(sprite, sprite.get_rect(center=(x, y)))

        if self.game.two_players:
            player2 = self.game.player2
            player2.update_animation(now)
            rect2 = player2.get_current_rect()
            sprite2 = player2.iconsheet.scaled_to_height(rect2, size)
            if self.game.cheat_invisible:
                sprite2 = sprite2.copy()
                sprite2.set_alpha(constants.INVISIBLE_PLAYER_ALPHA)
            vx2, vy2 = player2.get_visual_position(now)
            x2, y2 = self.coordinates_converter((vx2, vy2))
            self.screen.blit(sprite2, sprite2.get_rect(center=(x2, y2)))

    def _panel_draw(self, fill_alpha: int | None = None) -> None:
        """Draw the translucent panel behind the maze."""
        panel_rect = pygame.Rect(
            self.offset_x - 20,
            self.offset_y - 20,
            len(self.game.current_level.maze[0]) * self.line + 40,
            len(self.game.current_level.maze) * self.line + 40,
        )

        if fill_alpha is None:
            fill_alpha = constants.MAZE_PANEL_FILL_ALPHA

        paint.panel(
            self.screen, panel_rect,
            fill_alpha=fill_alpha,
            border_color=self._theme_color(),
            border_width=2,
            border_alpha=constants.MAZE_PANEL_BORDER_ALPHA,
        )

    def _gui_draw(self) -> None:
        """Draw the HUD: score, timer, hearts and the pause button."""
        video_top = self.video.offset_y
        video_right = self.video.display_width
        default_color = (243, 244, 231)
        danger_color = (255, 14, 14)

        score_icon = score_img.scaled_to_height(constants.score_rect, 230)
        padding = 30
        padding_x = 54
        score_pos = score_icon.get_rect(
            topleft=(padding_x, video_top + self.padding_y - padding)
        )
        self.screen.blit(score_icon, score_pos)

        timer_icon = timer.scaled_to_height(constants.timer_rect, 150)
        timer_pos_rect = timer_icon.get_rect(
            topright=(
                video_right - 50,
                video_top + self.padding_y - padding,
            )
        )
        self.screen.blit(timer_icon, timer_pos_rect)

        self._draw_pause_toggle_button(timer_pos_rect)

        for i in range(self.game.player.lives):
            x = (
                score_pos.left
                + constants.HEART_OFFSET_X
                + i * (self.heart.get_width() + constants.HEART_GAP)
            )
            y = score_pos.top + constants.HEART_OFFSET_Y
            self.screen.blit(self.heart, (x, y))

        paint.text(
            self.screen,
            fonts.get(constants.GUI_FONT_SIZE),
            str(self.game.current_level.collected_score + self.game.score),
            (243, 244, 231), "topleft",
            (100, video_top + 165)
        )
        if self.game.time_remaining <= 10:
            color = danger_color if self._blink_on() else (255, 255, 255)
        else:
            color = default_color
        paint.text(
            self.screen,
            fonts.get(constants.GUI_FONT_SIZE),
            self._format_mmss(self.game.time_remaining),
            color, "topright",
            (self.video.display_width - 73, video_top + 105)
        )

    def _format_mmss(self, total_seconds: int) -> str:
        """Format seconds as MM:SS."""
        minutes, seconds = divmod(total_seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _draw_name_entry(
        self, offset_y: int = constants.GAMEOVER_NAME_BOX_OFFSET_Y
    ) -> None:
        """Draw the name input box and the submit button when needed."""
        rect = self.gameover_rect
        box_rect = pygame.Rect(
            0,
            0,
            int(rect.width * constants.GAMEOVER_NAME_BOX_WIDTH_RATIO),
            constants.GAMEOVER_NAME_BOX_HEIGHT,
        )
        box_rect.center = (rect.centerx, rect.top + offset_y)

        paint.text(
            self.screen, fonts.get(constants.GAMEOVER_LABEL_FONT_SIZE),
            "INSERT YOUR NAME", constants.GAMEOVER_LABEL_COLOR,
            "midbottom",
            (
                box_rect.centerx,
                box_rect.top - constants.GAMEOVER_NAME_LABEL_GAP,
            ),
            shadow=None
        )

        border_color = (
            constants.GAMEOVER_INPUT_BORDER_COLOR_LOCKED
            if self.name_done
            else constants.GAMEOVER_INPUT_BORDER_COLOR
        )
        panel_alpha = (
            constants.GAMEOVER_INPUT_PANEL_ALPHA_LOCKED
            if self.name_done
            else constants.GAMEOVER_INPUT_PANEL_ALPHA
        )
        paint.panel(
            self.screen, box_rect,
            fill_alpha=panel_alpha, border_color=border_color,
        )

        display_text = self.entered_name
        if not self.name_done and self._blink_on():
            display_text += "|"

        text_alpha = (
            constants.GAMEOVER_INPUT_TEXT_ALPHA_LOCKED
            if self.name_done
            else constants.GAMEOVER_INPUT_TEXT_ALPHA
        )
        paint.text(
            self.screen, fonts.get(constants.GAMEOVER_INPUT_FONT_SIZE),
            display_text, constants.GAMEOVER_INPUT_COLOR,
            "center", box_rect.center, alpha=text_alpha, shadow=None
        )

        if self.game.game_state != Gamestate.WIN:
            submit_rect = pygame.Rect(
                0, 0, box_rect.width, constants.GAMEOVER_SUBMIT_BUTTON_HEIGHT
            )
            submit_rect.midtop = (
                box_rect.centerx,
                box_rect.bottom + constants.GAMEOVER_SUBMIT_BUTTON_GAP,
            )
            self.submit_rect = self._draw_gameover_button(
                "SUBMIT", submit_rect,
                forced_pressed=self.name_done,
                locked=self._submit_locked(),
            )

    def _name_ready(self) -> bool:
        """Return True if the entered name is not empty."""
        return bool(self.entered_name.strip())

    def _submit_locked(self) -> bool:
        """Return True if submitting is not possible yet."""
        return not self.name_done and not self._name_ready()

    def submit_name(self) -> None:
        """Validate the name and save the score if valid."""
        if self.name_done or not self._name_ready():
            return
        name = self.entered_name.strip()
        if len(name) > 2 and len(name) <= 10:
            for c in name:
                if c.isalnum() is False and c != ' ':
                    return
            self.game.player.name = name
            self.game.insert_score()
            self.name_done = True

    def _draw_stats(self, rect: pygame.Rect) -> None:
        """Draw the game over title and the stats grid."""
        game = self.game
        title_font = fonts.get(constants.GAMEOVER_TITLE_FONT_SIZE)
        stats_font = fonts.get(constants.STATS_TITLE_FONT_SIZE)
        font = fonts.get(constants.GAMEOVER_STATS_FONT_SIZE)
        row_gap = constants.GAMEOVER_STATS_SECTION_GAP
        col_gap = constants.GAMEOVER_STATS_LINE_GAP
        icon_text_gap = 10
        row_height = max(
            font.get_height(), constants.GAMEOVER_STATS_ICON_SIZE
        )

        y = rect.centery - constants.GAMEOVER_STATS_OFFSET_Y

        headline_rect = paint.text(
            self.screen, title_font, "GAME OVER",
            constants.GAMEOVER_TITLE_COLOR,
            "midtop", (rect.centerx, y), shadow=None
        )
        y = headline_rect.bottom + constants.GAMEOVER_TITLE_GAP

        title_rect = paint.text(
            self.screen, stats_font, "STATS", (243, 244, 231),
            "midtop", (rect.centerx, y), shadow=None
        )
        y = title_rect.bottom + row_gap

        elapsed = game.total_elapsed_seconds
        stats = [
            ("SCORE: ", str(game.score)),
            ("LEVEL: ", str(game.level_index + 1)),
            ("TIME: ", self._format_mmss(elapsed)),
            ("GUMS EATEN: ", str(game.gums_eaten)),
        ]

        cells: list[tuple[pygame.Surface, str, str, int]] = []
        for label, value in stats:
            icon = gameover_icons.scaled_to_height(
                constants.GAMEOVER_STAT_ICON_RECTS[label.rstrip(": ")],
                constants.GAMEOVER_STATS_ICON_SIZE,
            )
            width = (
                icon.get_width()
                + icon_text_gap
                + font.size(label + value)[0]
            )
            cells.append((icon, label, value, width))

        for name, icon_rect in GHOST_STAT_ICONS.items():
            icon = ghosts.scaled_to_height(
                icon_rect, constants.GAMEOVER_STATS_ICON_SIZE
            )
            label, value = ": ", f"{game.ghosts_eaten[name]}"
            width = (
                icon.get_width()
                + icon_text_gap
                + font.size(label + value)[0]
            )
            cells.append((icon, label, value, width))

        rows = [cells[i:i + 2] for i in range(0, len(cells), 2)]

        col_width = max(cell[3] for cell in cells)
        table_width = col_width * 2 + col_gap
        table_left = rect.centerx - table_width // 2
        col_left = [table_left, table_left + col_width + col_gap]

        for row in rows:
            center_y = y + row_height // 2
            for c, (icon, label, value, width) in enumerate(row):
                x = col_left[c] + (col_width - width) // 2
                if icon is not None:
                    self.screen.blit(
                        icon, icon.get_rect(midleft=(x, center_y))
                    )
                    x += icon.get_width() + icon_text_gap
                label_rect = paint.text(
                    self.screen, font, label, constants.GAMEOVER_STATS_COLOR,
                    "midleft", (x, center_y), shadow=None
                )
                paint.text(
                    self.screen, font, value, constants.GAMEOVER_VALUE_COLOR,
                    "midleft", (label_rect.right, center_y), shadow=None
                )
            y += row_height + row_gap

    def _blink_on(self) -> bool:
        """Return True during the visible half of a blink."""
        return cast(bool, (pygame.time.get_ticks() // 500) % 2 == 0)

    def handle_name_key(self, event: pygame.event.Event) -> None:
        """Handle typing, backspace and enter in the name box."""
        if self.name_done:
            return
        if event.key == pygame.K_RETURN:
            self.submit_name()
        elif event.key == pygame.K_BACKSPACE:
            self.entered_name = self.entered_name[:-1]
        elif event.unicode.isprintable() and len(self.entered_name) < 10:
            self.entered_name += event.unicode

    def _pause_panel(self) -> None:
        """Draw the pause overlay with its title and buttons."""
        rect = pygame.Rect(
            self.offset_x - 20,
            self.offset_y - 20,
            len(self.game.current_level.maze[0]) * self.line + 40,
            len(self.game.current_level.maze) * self.line + 40,
        )

        paint.panel(
            self.screen, rect,
            fill_alpha=constants.PAUSE_PANEL_ALPHA,
            border_color=constants.PAUSE_PANEL_BORDER_COLOR,
        )

        title_font = fonts.get(constants.PAUSE_TITLE_FONT_SIZE)
        title_height = title_font.get_height()

        button_sprite = buttons.scaled_to_height(
            constants.BUTTON_RECT, constants.PAUSE_BUTTON_HEIGHT
        )
        button_width, button_height = button_sprite.get_size()

        buttons_block_height = (
            len(constants.PAUSE_BUTTON_LABELS) * button_height
            + (len(constants.PAUSE_BUTTON_LABELS) - 1)
            * constants.PAUSE_BUTTON_GAP
        )
        content_height = (
            title_height
            + constants.PAUSE_TITLE_TO_BUTTONS_GAP
            + buttons_block_height
        )

        y = rect.centery - content_height // 2

        title_rect = paint.text(
            self.screen, title_font, constants.PAUSE_TITLE_TEXT,
            constants.PAUSE_TITLE_COLOR,
            "midtop", (rect.centerx, y), shadow=None
        )

        y = title_rect.bottom + constants.PAUSE_TITLE_TO_BUTTONS_GAP
        self.pause_button_rects = []
        for index, (label, action) in enumerate(constants.PAUSE_BUTTON_LABELS):
            slot = pygame.Rect(0, 0, button_width, button_height)
            slot.midtop = (rect.centerx, y)
            selected = index == self.pause_selected_index
            self._draw_pause_button(label, slot, selected)
            self.pause_button_rects.append((slot, action))
            y = slot.bottom + constants.PAUSE_BUTTON_GAP

    def _draw_pause_button(
        self, label: str, slot_rect: pygame.Rect, selected: bool = False
    ) -> None:
        """Draw one pause menu button, highlighted if selected or hovered."""
        pressed = selected or slot_rect.collidepoint(pygame.mouse.get_pos())
        sprite_rect = (
            constants.BUTTON_PRESSED_RECT if pressed else constants.BUTTON_RECT
        )
        sprite = buttons.scaled_to_height(
            sprite_rect, constants.PAUSE_BUTTON_HEIGHT
        )
        text = fonts.get(constants.PAUSE_BUTTON_FONT_SIZE).render(
            label, True, constants.PAUSE_BUTTON_TEXT_COLOR
        )
        self.screen.blit(sprite, sprite.get_rect(center=slot_rect.center))
        self.screen.blit(text, text.get_rect(center=slot_rect.center))

    def handle_pause_click(self, pos: tuple[int, int]) -> str | None:
        """Return the pause action under pos, or None."""
        for rect, action in self.pause_button_rects:
            if rect.collidepoint(pos):
                return action
        return None

    def handle_pause_key(self, event: pygame.event.Event) -> str | None:
        """Move the pause selection with keys and return the chosen action."""
        if event.key in (pygame.K_UP, pygame.K_w):
            self.pause_selected_index = (
                self.pause_selected_index - 1
            ) % len(constants.PAUSE_BUTTON_LABELS)
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.pause_selected_index = (
                self.pause_selected_index + 1
            ) % len(constants.PAUSE_BUTTON_LABELS)
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            return constants.PAUSE_BUTTON_LABELS[self.pause_selected_index][1]
        return None

    def reset_pause_selection(self) -> None:
        """Select the first pause button."""
        self.pause_selected_index = 0

    def _draw_gameover_buttons(self, center_y: int | None = None) -> None:
        """Draw the end screen buttons that fit the current state."""
        rect = self.gameover_rect
        width, height = buttons.scaled_to_height(
            constants.BUTTON_RECT, constants.GAMEOVER_BUTTON_HEIGHT
        ).get_size()
        y = (
            rect.bottom - constants.GAMEOVER_BUTTON_OFFSET_Y
            if center_y is None
            else center_y
        )
        locked = not self.name_done
        state = self.game.game_state

        def slot(offset_x: int) -> pygame.Rect:
            """Return a button rect centered at the given x offset."""
            r = pygame.Rect(0, 0, width, height)
            r.center = (rect.centerx + offset_x, y)
            return r

        left, right = (
            slot(-constants.GAMEOVER_BUTTON_GAP),
            slot(constants.GAMEOVER_BUTTON_GAP),
        )
        self.retry_rect = None
        self.next_rect = None

        if state == Gamestate.LEVEL_WIN:
            self.back_rect = self._draw_gameover_button("BACK TO MENU", left)
            self.next_rect = self._draw_gameover_button("LEVELS MAP", right)

        elif state == Gamestate.WIN:
            self.back_rect = self._draw_gameover_button(
                "LEVELS MAP", left, locked=locked
            )
            self.submit_rect = self._draw_gameover_button(
                "SUBMIT", right,
                forced_pressed=self.name_done,
                locked=self._submit_locked(),
            )

        else:
            self.back_rect = self._draw_gameover_button(
                "BACK TO MENU", left, locked=locked
            )
            self.retry_rect = self._draw_gameover_button(
                "RETRY", right, locked=locked
            )

    def _draw_gameover_button(
        self,
        label: str,
        slot_rect: pygame.Rect,
        forced_pressed: bool = False,
        locked: bool = False,
    ) -> pygame.Rect:
        """Draw one end screen button (optionally locked)
        and return its rect."""
        pressed = not locked and (
            forced_pressed
            or slot_rect.collidepoint(pygame.mouse.get_pos())
        )
        sprite_rect = (
            constants.BUTTON_PRESSED_RECT if pressed else constants.BUTTON_RECT
        )
        sprite = buttons.scaled_to_height(
            sprite_rect, constants.GAMEOVER_BUTTON_HEIGHT
        )
        text = fonts.get(constants.GAMEOVER_BUTTON_FONT_SIZE).render(
            label, True, constants.GAMEOVER_BUTTON_TEXT_COLOR
        )
        if locked:
            sprite = sprite.copy()
            sprite.set_alpha(constants.GAMEOVER_BUTTON_LOCKED_ALPHA)
            text.set_alpha(constants.GAMEOVER_BUTTON_LOCKED_ALPHA)
        self.screen.blit(sprite, sprite.get_rect(center=slot_rect.center))
        self.screen.blit(text, text.get_rect(center=slot_rect.center))
        return slot_rect

    def trigger_cheat_popup(self, name: str) -> None:
        """Start showing the popup for the given cheat."""
        now = pygame.time.get_ticks()
        self.cheat_popup_name = name
        self.cheat_popup_until = now + constants.CHEAT_POPUP_DURATION_MS
        self.top_panel_until = (
            now
            + constants.CHEAT_POPUP_DURATION_MS
            + constants.TOP_PANEL_EXTRA_MS
        )

    def _theme_color(self) -> tuple[int, int, int]:
        """Return the active cheat color, or the accent color."""
        if (
            self.cheat_popup_name is not None
            and pygame.time.get_ticks() < self.cheat_popup_until
        ):
            return constants.CHEAT_POPUP_COLORS.get(
                self.cheat_popup_name, constants.ACCENT_COLOR
            )
        return constants.ACCENT_COLOR

    def _draw_cheat_popup(self) -> None:
        """Draw the fading cheat popup over the maze."""
        if self.cheat_popup_name is None:
            return
        now = pygame.time.get_ticks()
        remaining = self.cheat_popup_until - now
        if remaining <= 0:
            self.cheat_popup_name = None
            return

        elapsed = constants.CHEAT_POPUP_DURATION_MS - remaining
        fade = constants.CHEAT_POPUP_FADE_MS
        if elapsed < fade:
            alpha = int(255 * elapsed / fade)
        elif remaining < fade:
            alpha = int(255 * remaining / fade)
        else:
            alpha = 255
        alpha = max(0, min(255, alpha))

        title, subtitle = constants.CHEAT_POPUP_TEXTS.get(
            self.cheat_popup_name, constants.CHEAT_POPUP_TEXTS["none"]
        )
        color = constants.CHEAT_POPUP_COLORS.get(
            self.cheat_popup_name, constants.ACCENT_COLOR
        )

        icon = cheat_icons.scaled_to_height(
            constants.CHEAT_ICON_RECTS[self.cheat_popup_name],
            constants.CHEAT_POPUP_ICON_HEIGHT,
        )
        title_surf = fonts.get(constants.CHEAT_POPUP_TITLE_SIZE).render(
            title, True, color
        )
        subtitle_surf = fonts.get(constants.CHEAT_POPUP_SUBTITLE_SIZE).render(
            subtitle, True, color
        )

        content_width = max(
            icon.get_width(), title_surf.get_width(), subtitle_surf.get_width()
        )
        content_height = (
            icon.get_height() + constants.CHEAT_POPUP_ICON_TEXT_GAP
            + title_surf.get_height() + constants.CHEAT_POPUP_TEXT_GAP
            + subtitle_surf.get_height()
        )

        center = (
            self.offset_x
            + (len(self.game.current_level.maze[0]) * self.line) // 2,
            self.offset_y
            + (len(self.game.current_level.maze) * self.line) // 2,
        )

        panel_rect = pygame.Rect(0, 0, content_width, content_height).inflate(
            constants.CHEAT_POPUP_PANEL_PADDING * 2,
            constants.CHEAT_POPUP_PANEL_PADDING * 2,
        )
        panel_rect.center = center

        paint.panel(
            self.screen, panel_rect,
            radius=constants.CHEAT_POPUP_PANEL_RADIUS,
            fill_alpha=int(constants.CHEAT_POPUP_PANEL_ALPHA * alpha / 255),
            border_color=color,
            border_width=2,
            border_alpha=alpha,
        )

        y = panel_rect.centery - content_height // 2

        icon_copy = icon.copy()
        icon_copy.set_alpha(alpha)
        icon_rect = icon_copy.get_rect(midtop=(panel_rect.centerx, y))
        self.screen.blit(icon_copy, icon_rect)
        y = icon_rect.bottom + constants.CHEAT_POPUP_ICON_TEXT_GAP

        title_copy = title_surf.copy()
        title_copy.set_alpha(alpha)
        title_rect = title_copy.get_rect(midtop=(panel_rect.centerx, y))
        self.screen.blit(title_copy, title_rect)
        y = title_rect.bottom + constants.CHEAT_POPUP_TEXT_GAP

        subtitle_copy = subtitle_surf.copy()
        subtitle_copy.set_alpha(alpha)
        self.screen.blit(
            subtitle_copy,
            subtitle_copy.get_rect(midtop=(panel_rect.centerx, y)),
        )

    def handle_gameover_click(self, pos: tuple[int, int]) -> str | None:
        """Return the end screen action under pos, or None."""
        if self.game.game_state == Gamestate.LEVEL_WIN:
            if self.next_rect and self.next_rect.collidepoint(pos):
                return "next"
            if self.back_rect and self.back_rect.collidepoint(pos):
                return "back"
            return None

        if (
            self.submit_rect
            and not self.name_done
            and self.submit_rect.collidepoint(pos)
        ):
            return "submit" if self._name_ready() else None
        if not self.name_done:
            return None
        if self.retry_rect and self.retry_rect.collidepoint(pos):
            return "retry"
        if self.back_rect and self.back_rect.collidepoint(pos):
            return ("levels" if self.game.game_state == Gamestate.WIN else
                    "back")
        return None

    def reset_name_entry(self) -> None:
        """Clear the entered name and unlock the input."""
        self.entered_name = ""
        self.name_done = False

    def _draw_side_panel(
        self, side: str, title: str, lines: list[str]
    ) -> None:
        """Draw a left or right info panel with a title and lines."""
        title_font = fonts.get(constants.SIDE_INFO_TITLE_SIZE)
        text_font = fonts.get(constants.SIDE_INFO_TEXT_SIZE)

        color = self._theme_color()

        panel_rect = pygame.Rect(
            0, 0, constants.SIDE_INFO_WIDTH, constants.SIDE_INFO_HEIGHT
        )
        video_bottom = self.video.offset_y + self.video.display_height

        if side == "left":
            panel_rect.bottomleft = (
                constants.SIDE_INFO_OUTER_MARGIN,
                video_bottom - constants.SIDE_INFO_BOTTOM_MARGIN,
            )
        else:
            panel_rect.bottomright = (
                self.video.display_width - constants.SIDE_INFO_OUTER_MARGIN,
                video_bottom - constants.SIDE_INFO_BOTTOM_MARGIN,
            )

        paint.panel(
            self.screen, panel_rect,
            radius=constants.SIDE_INFO_PANEL_RADIUS,
            fill_alpha=constants.SIDE_INFO_PANEL_ALPHA,
            border_color=color,
        )

        max_text_width = (
            panel_rect.width - constants.SIDE_INFO_PANEL_PADDING * 2
        )

        title_surf = title_font.render(title, True, color)
        y = panel_rect.top + constants.SIDE_INFO_PANEL_PADDING
        title_rect = title_surf.get_rect(midtop=(panel_rect.centerx, y))
        self.screen.blit(title_surf, title_rect)
        y = title_rect.bottom + constants.SIDE_INFO_TITLE_GAP

        pygame.draw.line(
            self.screen, color,
            (
                panel_rect.left + constants.SIDE_INFO_PANEL_PADDING,
                y - constants.SIDE_INFO_TITLE_GAP // 2,
            ),
            (
                panel_rect.right - constants.SIDE_INFO_PANEL_PADDING,
                y - constants.SIDE_INFO_TITLE_GAP // 2,
            ),
            width=1,
        )

        for line in lines:
            wrapped = (
                render.fonts.wrap_text(line, text_font, max_text_width)
                if line
                else [""]
            )
            for sub_line in wrapped:
                surf = text_font.render(
                    sub_line, True, constants.SIDE_INFO_TEXT_COLOR
                )
                rect = surf.get_rect(midtop=(panel_rect.centerx, y))
                if (
                    rect.bottom
                    > panel_rect.bottom - constants.SIDE_INFO_PANEL_PADDING
                ):
                    return
                self.screen.blit(surf, rect)
                y = rect.bottom + constants.SIDE_INFO_LINE_GAP

    def _draw_side_info(self) -> None:
        """Draw the controls and cheat codes panels."""
        self._draw_side_panel(
            "left", constants.CONTROLS_TITLE, constants.CONTROLS_LINES
        )
        self._draw_side_panel(
            "right", constants.CHEATS_TITLE, constants.CHEATS_LINES
        )

    def _draw_pause_toggle_button(
        self, timer_pos_rect: pygame.Rect
    ) -> None:
        """Draw the pause/play button under the timer and store its rect."""
        pressed = (
            self.pause_button_rect is not None
            and self.pause_button_rect.collidepoint(pygame.mouse.get_pos())
        )
        if self.game.is_paused:
            rect = (
                constants.PLAY_BUTTON_PRESSED_RECT
                if pressed
                else constants.PLAY_BUTTON_RECT
            )
        else:
            rect = (
                constants.PAUSE_BUTTON_PRESSED_RECT
                if pressed
                else constants.PAUSE_BUTTON_RECT
            )
        icon = pause_icon.scaled_to_height(
            rect, constants.PAUSE_BUTTON_ICON_HEIGHT
        )
        icon_rect = icon.get_rect(
            midtop=(
                timer_pos_rect.right - constants.PAUSE_BUTTON_OFFSET_X,
                timer_pos_rect.bottom + constants.PAUSE_BUTTON_OFFSET_Y,
            )
        )
        self.screen.blit(icon, icon_rect)
        self.pause_button_rect = icon_rect

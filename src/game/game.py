from __future__ import annotations

import sys
from typing import Any, Callable, TypedDict

import pygame

from src.media import constants
from src.media import render
from src.media.media import AudioManager, VideoBackground, Cursor
from src.ui.menu_ui import (DialogueBox,
                            Footer,
                            Header,
                            MenuCarousel,
                            BackToMenu)
from src.ui.pages_ui import InfoPage, ScoreboardPage
from src.ui.select_ui import SkinSelector, SoundPage, LevelsPage
from src.game.gameplay import GameState, Gamestate
from src.ui.visualizer import Plying

TARGET_FPS: int = 60

WASD_KEYS: dict[int, tuple[int, int]] = {
    pygame.K_a: (-1, 0),
    pygame.K_d: (1, 0),
    pygame.K_w: (0, -1),
    pygame.K_s: (0, 1),
}
ARROW_KEYS: dict[int, tuple[int, int]] = {
    pygame.K_LEFT: (-1, 0),
    pygame.K_RIGHT: (1, 0),
    pygame.K_UP: (0, -1),
    pygame.K_DOWN: (0, 1),
}

GRID_KEYS: dict[int, tuple[int, int]] = dict(WASD_KEYS)
GRID_KEYS.update(ARROW_KEYS)

OVERLAY_PAGES: frozenset[str] = frozenset(
    {
        "info_page",
        "scoreboard_page",
        "sound_page",
        "skin_select_1p",
        "skin_select_2p",
        "levels_page",
    }
)


class CarouselLayout(TypedDict):
    header_rect: pygame.Rect
    carousel_center_y: int


class Game:
    def __init__(self, data: dict[str, Any]) -> None:
        """Initialize pygame, the window, audio, pages and handlers."""
        pygame.init()

        self.window_width, self.window_height = self.window_size()
        self.screen: pygame.Surface = self._init_display()
        pygame.display.set_caption("PAC-MAN")

        self.video: VideoBackground = VideoBackground(
            self.window_width, self.window_height
        )
        self.audio: AudioManager = AudioManager()
        self.audio.play_theme_music(constants.DEFAULT_THEME)
        self._music_playing: bool = False

        self.content_top, self.content_bottom = self._compute_content_bounds()

        self.gamestate: GameState = GameState(data, self.audio)
        self.plying: Plying = Plying(self.screen, self.gamestate, self.video)

        self.carousel: MenuCarousel = MenuCarousel()
        self.skins: SkinSelector = SkinSelector(
            self.window_width, self.window_height
        )
        self.info_page: InfoPage = InfoPage(self.audio)
        self.scoreboard_page: ScoreboardPage = ScoreboardPage()
        self.sound_page: SoundPage = SoundPage(
            constants.SOUND_TITLE,
            [
                {"label": name, "icon_rect": rect}
                for name, rect in constants.SOUND_METER_ICON_RECTS.items()
            ],
        )
        self.header: Header = Header(self.window_width)
        self.footer: Footer = Footer(self.window_width, self.window_height)
        self.dialogue_box: DialogueBox = DialogueBox(
            self.window_width, self.content_bottom, self.audio
        )

        self.carousel_layout: CarouselLayout = self._compute_carousel_layout()

        self.page: str = "carousel"
        self.entered_label: str = constants.MENU_ITEMS[0]

        self.pending_action: tuple[str, str | int | None] | None = None
        self.is_pressing: bool = False
        self.press_elapsed_ms: int = 0

        self.skin_selected: int = 0
        self.player1_skin: int = 0
        self.player2_skin: int = 1

        self.skin_arrow_rects_1p: tuple[pygame.Rect, ...] | None = None
        self.skin_arrow_rects_2p: tuple[pygame.Rect, ...] | None = None

        self.player1_ready: bool = False
        self.player2_ready: bool = False

        self.pending_start: Any = None

        self.hoverable_rects: list[tuple[pygame.Rect, int]] = []
        self.running: bool = True
        self.clock: pygame.time.Clock = pygame.time.Clock()

        self.back_to_menu = BackToMenu(self.screen, self.video)

        self.levels_page: LevelsPage = LevelsPage(self.gamestate)

        self.cursor: Cursor = Cursor()
        self.held_keys: list[int] = []

        self._input_handlers: dict[
            str, Callable[[pygame.event.Event], None]
        ] = {
            "carousel": self._handle_carousel_input,
            "sound_page": self._handle_sound_input,
            "skin_select_1p": self._handle_skin_1p_input,
            "skin_select_2p": self._handle_skin_2p_input,
            "levels_page": self._handle_levels_page_input,
            "playing": self._handle_play_input,
            "info_page": self._handle_info_page_input,
        }
        self._page_drawers: dict[str, Callable[[], None]] = {
            "carousel": self._draw_carousel,
            "info_page": self._draw_info_page,
            "scoreboard_page": self._draw_scoreboard_page,
            "sound_page": self._draw_sound_page,
            "skin_select_1p": self._draw_skin_1p,
            "skin_select_2p": self._draw_skin_2p,
            "levels_page": self._draw_levels_page,
            "playing": self._draw_playing,
        }
        self._actions: dict[str, Callable[[str | int | None], None]] = {
            "quit": self._quit,
            "info_page": self._open_info_page,
            "scoreboard_page": self._go_to_scoreboard_page,
            "sound_page": self._go_to_sound_page,
            "skin_1p": self._open_skin_1p,
            "skin_2p": self._go_to_skin_2p_page,
            "push": self._push_submenu,
            "pop": self._pop_submenu,
            "theme": self._apply_theme,
        }

    def _init_display(self) -> pygame.Surface:
        """Open a fullscreen scaled window, falling back without vsync."""
        flags = pygame.FULLSCREEN | pygame.SCALED
        size = (self.window_width, self.window_height)
        try:
            return pygame.display.set_mode(size, flags, vsync=1)
        except pygame.error:
            return pygame.display.set_mode(size, flags)

    def _compute_content_bounds(self) -> tuple[int, int]:
        """Return the top and bottom of the area covered by the video."""
        top = max(0, self.video.offset_y)
        bottom = min(
            self.window_height,
            self.video.offset_y + self.video.display_height,
        )
        if bottom <= top:
            return 0, self.window_height
        return top, bottom

    def _compute_carousel_layout(self) -> CarouselLayout:
        """Compute the logo rect and center line of the menu carousel."""
        carousel_height = 2 * self.carousel.spacing + self.carousel.side_height
        block_height = (
            self.header.total_height
            + constants.CAROUSEL_TOP_GAP
            + carousel_height
        )
        content_height = self.content_bottom - self.content_top
        carousel_top = self.content_top + (content_height - block_height) // 2

        header_rect = self.header.layout(self.window_width, carousel_top)
        top_edge = header_rect.bottom + constants.CAROUSEL_TOP_GAP
        center_y = (
            top_edge
            + self.carousel.spacing
            + self.carousel.side_height // 2
            - 50
        )
        return {"header_rect": header_rect, "carousel_center_y": center_y}

    def _confirm_skin_1p(self) -> None:
        """Save the chosen skin and open the level select page."""
        iconsheet = render.SKINS_ICONSHEETS[self.skin_selected]
        frames = constants.FRAMES[self.skin_selected]
        self.pending_start = ((iconsheet, frames), None, False)
        self.page = "levels_page"
        self.audio.play_confirm()

    def _start_selected_level(self) -> None:
        """Create the characters and start the selected level."""
        self.gamestate.characteres_init(*self.pending_start)
        self.gamestate.next_level(self.levels_page.selected_index)
        self.page = "playing"
        self.audio.play_confirm()

    def _handle_click(self, pos: tuple[int, int]) -> None:
        """Route a left mouse click to the active page's controls."""
        if (
            self.page == "playing"
            and self.gamestate.game_state == Gamestate.START
            and self.plying.pause_button_rect is not None
            and self.plying.pause_button_rect.collidepoint(pos)
        ):
            self.gamestate.is_paused = not self.gamestate.is_paused
            if self.gamestate.is_paused:
                self.plying.reset_pause_selection()
            self.audio.play_confirm()
            return
        if self.page == "playing" and self.gamestate.is_paused:
            action = self.plying.handle_pause_click(pos)
            self._handle_pause_action(action)
            return
        if self.page == "playing" and self.gamestate.game_state in (
            Gamestate.LOST, Gamestate.WIN, Gamestate.LEVEL_WIN
        ):
            action = self.plying.handle_gameover_click(pos)
            if action == "submit":
                self.plying.submit_name()
            elif action == "next":
                self.page = "levels_page"
            elif action == "retry":
                self.gamestate.game_reset()
                self.plying.reset_name_entry()
            elif action == "back":
                self.carousel.reset_to_root()
                self.gamestate.game_reset()
                self.plying.reset_name_entry()
                self.page = "carousel"
                self.audio.stop("countdown")
                self.audio.play_back()
            elif action == "levels":
                self.gamestate.game_reset()
                self.plying.reset_name_entry()
                self.page = "levels_page"
                self.audio.play_back()
            return

        if self.page == "carousel":
            if self.is_pressing:
                return
            up = self.carousel.up_arrow_rect
            down = self.carousel.down_arrow_rect
            if up is not None and up.collidepoint(pos):
                if self.carousel.move_selection(-1):
                    self.audio.play_move()
            elif down is not None and down.collidepoint(pos):
                if self.carousel.move_selection(1):
                    self.audio.play_move()
            else:
                selected = self.carousel.current_menu["selected_index"]
                for rect, index in self.hoverable_rects:
                    if rect.collidepoint(pos):
                        if index == selected:
                            self._activate_carousel_selection()
                        elif self.carousel.move_selection(index - selected):
                            self.audio.play_move()
                        break
            return

        if self.page == "levels_page":
            node_index = self.levels_page.node_at(pos)
            if node_index is not None:
                self.levels_page.selected_index = node_index
                self._start_selected_level()
                return

        if self.page == "info_page" and self.entered_label == "INSTRUCTIONS":
            if (
                self.info_page.skip_rect
                and self.info_page.skip_rect.collidepoint(pos)
            ):
                self.info_page.skip_dialogue()
                self.audio.play_move()
                return
            if (
                self.info_page.previous_rect
                and self.info_page.previous_rect.collidepoint(pos)
            ):
                self.info_page.previous_dialogue()
                self.audio.play_move()
                return

        if self.page == "skin_select_1p":
            if self.skin_arrow_rects_1p is not None:
                left_rect, right_rect = self.skin_arrow_rects_1p
                if left_rect.collidepoint(pos):
                    self._move_skin_1p(-1)
                    return
                if right_rect.collidepoint(pos):
                    self._move_skin_1p(1)
                    return
            cells = self.skins.cell_rects
            if "left" in cells and cells["left"].collidepoint(pos):
                self._move_skin_1p(-1)
                return
            if "right" in cells and cells["right"].collidepoint(pos):
                self._move_skin_1p(1)
                return
            if "main" in cells and cells["main"].collidepoint(pos):
                self._confirm_skin_1p()
                return

        if (
            self.page == "skin_select_2p"
            and self.skin_arrow_rects_2p is not None
        ):
            p1_left, p1_right, p2_left, p2_right = self.skin_arrow_rects_2p
            if p1_left.collidepoint(pos):
                self.player1_skin = self.skins.move_selection(
                    self.player1_skin, -1
                )
                self.audio.play_move()
                return
            if p1_right.collidepoint(pos):
                self.player1_skin = self.skins.move_selection(
                    self.player1_skin, 1
                )
                self.audio.play_move()
                return
            if p2_left.collidepoint(pos):
                self.player2_skin = self.skins.move_selection(
                    self.player2_skin, -1
                )
                self.audio.play_move()
                return
            if p2_right.collidepoint(pos):
                self.player2_skin = self.skins.move_selection(
                    self.player2_skin, 1
                )
                self.audio.play_move()
                return

        if (
            self._should_draw_back_to_menu()
            and self.back_to_menu.rect.collidepoint(pos)
        ):
            self._handle_escape()

    def _handle_wheel(self, dy: int) -> None:
        """Scroll the carousel, skins or levels with the mouse wheel."""
        if dy == 0:
            return
        step = -1 if dy > 0 else 1
        if self.page == "carousel":
            if self.carousel.move_selection(step):
                self.audio.play_move()
        elif self.page == "skin_select_1p":
            self._move_skin_1p(step)
        elif self.page == "levels_page":
            self.levels_page.move_selection(step)
            self.audio.play_move()

    def window_size(self) -> tuple[int, int]:
        """Return the current display resolution."""
        pygame.display.init()
        info = pygame.display.Info()
        return info.current_w, info.current_h

    def _activate_carousel_selection(self) -> None:
        """Start the press flash and queue the selected menu action."""
        if self.is_pressing:
            return
        self.is_pressing = True
        self.press_elapsed_ms = 0
        self.pending_action = self.carousel.resolve_action(
            self.carousel.current_menu["name"], self.carousel.selected_label()
        )
        self.audio.play_confirm()

    def _move_skin_1p(self, delta: int) -> None:
        """Shift the single-player skin selection and play a sound."""
        self.skin_selected = self.skins.move_selection(
            self.skin_selected, delta
        )
        self.audio.play_move()

    def _handle_pause_action(self, action: str | None) -> None:
        """Run a pause menu choice: resume, restart or quit."""
        if action == "resume":
            self.gamestate.is_paused = False
            self.audio.play_confirm()
        elif action == "restart":
            self.gamestate.is_paused = False
            self.gamestate.next_level(self.gamestate.level_index)
            self.plying.reset_name_entry()
            self.audio.play_confirm()
        elif action == "quit":
            self.gamestate.is_paused = False
            self.carousel.reset_to_root()
            self.gamestate.game_reset()
            self.plying.reset_name_entry()
            self.page = "carousel"
            self.audio.stop("countdown")
            self.audio.play_back()

    def _handle_info_page_input(self, event: pygame.event.Event) -> None:
        """Step through the instructions dialogue with the keyboard."""
        if self.entered_label != "INSTRUCTIONS":
            return
        if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_RIGHT):
            self.info_page.skip_dialogue()
            self.audio.play_move()
        elif event.key == pygame.K_LEFT:
            self.info_page.previous_dialogue()
            self.audio.play_move()

    def handle_input(self, event: pygame.event.Event) -> None:
        """Dispatch one pygame event to the right handler."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._handle_click(event.pos)
            return
        if event.type == pygame.MOUSEWHEEL:
            self._handle_wheel(event.y)
            return
        if event.type != pygame.KEYDOWN:
            return
        if event.key == pygame.K_ESCAPE:
            self._handle_escape()
            return
        handler = self._input_handlers.get(self.page)
        if handler is not None:
            handler(event)

    def _handle_escape(self) -> None:
        """Go back, pause or quit depending on the current page."""
        if self.page == "playing":
            state = self.gamestate.game_state
            if state == Gamestate.COUNTDOWN:
                return
            if state == Gamestate.LEVEL_WIN:
                self.page = "levels_page"
                self.audio.play_back()
            elif state in (Gamestate.LOST, Gamestate.WIN):
                if not self.plying.name_done:
                    return
                self.gamestate.game_reset()
                self.plying.reset_name_entry()
                self.page = "levels_page"
                self.audio.play_back()
            else:
                self.gamestate.is_paused = not self.gamestate.is_paused
                if self.gamestate.is_paused:
                    self.plying.reset_pause_selection()
        elif self.page in OVERLAY_PAGES:
            self.info_page.stop_voice()
            self.page = "carousel"
            self.audio.play_back()
        elif self.carousel.pop():
            self.audio.play_back()
        else:
            self.running = False

    def _handle_carousel_input(self, event: pygame.event.Event) -> None:
        """Move or confirm the main menu selection by keyboard."""
        if event.key in (pygame.K_UP, pygame.K_w, pygame.K_DOWN, pygame.K_s):
            delta = -1 if event.key in (pygame.K_UP, pygame.K_w) else 1
            if self.carousel.move_selection(delta):
                self.audio.play_move()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._activate_carousel_selection()

    def _handle_sound_input(self, event: pygame.event.Event) -> None:
        """Select a volume meter and change its value by keyboard."""
        if event.key in (pygame.K_UP, pygame.K_w):
            self.sound_page.move_selection(-1)
            self.audio.play_move()
        elif event.key in (pygame.K_DOWN, pygame.K_s):
            self.sound_page.move_selection(1)
            self.audio.play_move()
        elif event.key in (
            pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d
        ):
            amount = (
                constants.SOUND_STEP
                if event.key in (pygame.K_RIGHT, pygame.K_d)
                else -constants.SOUND_STEP
            )
            if self.sound_page.selected_index == 0:
                self.audio.adjust_music_volume(amount)
            else:
                self.audio.adjust_sfx_volume(amount)

    def _handle_skin_1p_input(self, event: pygame.event.Event) -> None:
        """Browse and confirm skins on the single-player page."""
        if event.key in (pygame.K_LEFT, pygame.K_a):
            self.skin_selected = self.skins.move_selection(
                self.skin_selected, -1
            )
            self.audio.play_move()
        elif event.key in (pygame.K_RIGHT, pygame.K_d):
            self.skin_selected = self.skins.move_selection(
                self.skin_selected, 1
            )
            self.audio.play_move()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._confirm_skin_1p()

    def _handle_skin_2p_input(self, event: pygame.event.Event) -> None:
        """Browse skins and ready up both players on the 2P page."""
        if event.key in (pygame.K_a, pygame.K_d):
            delta = -1 if event.key == pygame.K_a else 1
            self.player1_skin = self.skins.move_selection(
                self.player1_skin, delta
            )
            self.audio.play_move()
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            delta = -1 if event.key == pygame.K_LEFT else 1
            self.player2_skin = self.skins.move_selection(
                self.player2_skin, delta
            )
            self.audio.play_move()
        elif event.key == pygame.K_SPACE:
            self.player1_ready = True
            self.audio.play_confirm()
        elif event.key == pygame.K_RETURN:
            self.player2_ready = True
            self.audio.play_confirm()

        if self.player1_ready and self.player2_ready:
            iconsheet1 = render.SKINS_ICONSHEETS[self.player1_skin]
            iconsheet2 = render.SKINS_ICONSHEETS[self.player2_skin]

            frames1 = constants.FRAMES[self.player1_skin]
            frames2 = constants.FRAMES[self.player2_skin]

            image_p1 = (iconsheet1, frames1)
            image_p2 = (iconsheet2, frames2)

            self.pending_start = (image_p2, image_p1, True)

            self.player1_ready = False
            self.player2_ready = False
            self.page = "levels_page"

    def _handle_levels_page_input(self, event: pygame.event.Event) -> None:
        """Move through and start levels from the level select page."""
        if event.key in (
            pygame.K_LEFT, pygame.K_a, pygame.K_RIGHT, pygame.K_d
        ):
            delta = -1 if event.key in (pygame.K_LEFT, pygame.K_a) else 1
            self.levels_page.move_selection(delta)
            self.audio.play_move()
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            self._start_selected_level()

    def _is_hovering_clickable(self) -> bool:
        """Return True if the mouse is over a clickable element."""
        pos = pygame.mouse.get_pos()
        rects: list[pygame.Rect | None] = []

        if self.page == "carousel":
            rects += [r for r, _ in self.hoverable_rects]
            rects += [self.carousel.up_arrow_rect,
                      self.carousel.down_arrow_rect]
        elif self.page == "levels_page":
            unlocked = self.gamestate.unlocked_levels
            rects += [
                r
                for i, r in enumerate(self.levels_page.node_rects)
                if i < unlocked
            ]
        elif self.page == "skin_select_1p":
            rects += list(self.skins.cell_rects.values())
            rects += list(self.skin_arrow_rects_1p or ())
        elif self.page == "info_page" and self.entered_label == "INSTRUCTIONS":
            rects += [self.info_page.skip_rect, self.info_page.previous_rect]
        elif self.page == "playing":
            state = self.gamestate.game_state
            if self.gamestate.is_paused:
                rects += [r for r, _ in self.plying.pause_button_rects]
                rects.append(self.plying.pause_button_rect)
            elif state == Gamestate.START:
                rects.append(self.plying.pause_button_rect)
            elif state in (Gamestate.LOST, Gamestate.WIN, Gamestate.LEVEL_WIN):
                rects += [
                    self.plying.submit_rect,
                    self.plying.retry_rect,
                    self.plying.next_rect,
                    self.plying.back_rect,
                ]

        if self._should_draw_back_to_menu():
            rects.append(self.back_to_menu.rect)

        return any(r is not None and r.collidepoint(pos) for r in rects)

    def _cursor_state(self) -> str:
        """Return click, hover or normal for the custom cursor."""
        if pygame.mouse.get_pressed()[0]:
            return "click"
        if self._is_hovering_clickable():
            return "hover"
        return "normal"

    def _draw_levels_page(self) -> None:
        """Draw the level select page."""
        self.levels_page.draw(
            self.screen,
            self.window_width,
            self.content_top,
            self.content_bottom,
        )

    def _should_draw_back_to_menu(self) -> bool:
        """Return True when the back button should be visible."""
        return self.page not in ("carousel", "playing")

    def _handle_play_input(self, event: pygame.event.Event) -> None:
        """Handle keys while playing: pause, cheats, names and moves."""
        state = self.gamestate.game_state
        if self.gamestate.is_paused:
            old_index = self.plying.pause_selected_index
            action = self.plying.handle_pause_key(event)
            if (action is None and
                    self.plying.pause_selected_index != old_index):
                self.audio.play_move()
            self._handle_pause_action(action)
            return
        if state == Gamestate.LEVEL_WIN:
            if event.key == pygame.K_RETURN:
                self.gamestate.next_level(self.gamestate.level_index + 1)
        elif state in (Gamestate.LOST, Gamestate.WIN):
            self.plying.handle_name_key(event)
        elif state == Gamestate.COUNTDOWN:
            return
        elif event.key == pygame.K_F1:
            self.gamestate.toggle_cheat("invisible")
            self.plying.trigger_cheat_popup(
                self.gamestate.active_cheat() or "none"
            )
        elif event.key == pygame.K_F2:
            self.gamestate.toggle_cheat("freeze")
            self.plying.trigger_cheat_popup(
                self.gamestate.active_cheat() or "none"
            )
        elif event.key == pygame.K_F3:
            self.gamestate.toggle_cheat("god_mode")
            self.plying.trigger_cheat_popup(
                self.gamestate.active_cheat() or "none"
            )
        elif event.key == pygame.K_F4:
            self.gamestate.request_skip_level()
            self.plying.trigger_cheat_popup("skip_level")
        else:
            self.gamestate.move_player(event.key)

    def _quit(self, _data: str | int | None) -> None:
        """Stop the main loop."""
        self.running = False

    def _open_info_page(self, data: str | int | None) -> None:
        """Open the instructions or credits page."""
        self.entered_label = str(data)
        if self.entered_label == "INSTRUCTIONS":
            self.info_page.reset_dialogue()
        self.page = "info_page"

    def _go_to_scoreboard_page(self, _data: str | int | None) -> None:
        """Switch to the scoreboard page."""
        self.page = "scoreboard_page"

    def _go_to_sound_page(self, _data: str | int | None) -> None:
        """Switch to the sound settings page."""
        self.page = "sound_page"

    def _open_skin_1p(self, _data: str | int | None) -> None:
        """Open the single-player skin page on the current skin."""
        self.skin_selected = self.player1_skin
        self.page = "skin_select_1p"

    def _go_to_skin_2p_page(self, _data: str | int | None) -> None:
        """Switch to the two-player skin page."""
        self.page = "skin_select_2p"

    def _push_submenu(self, data: str | int | None) -> None:
        """Open a submenu in the carousel."""
        self.carousel.push(str(data))

    def _pop_submenu(self, _data: str | int | None) -> None:
        """Return to the previous carousel menu."""
        self.carousel.pop()

    def _apply_theme(self, data: str | int | None) -> None:
        """Load a theme's video and music and recompute the layout."""
        assert data is not None
        theme_number = int(data)
        self.video.load_theme(theme_number)
        self.audio.play_theme_music(theme_number)
        self.content_top, self.content_bottom = self._compute_content_bounds()
        self.carousel_layout = self._compute_carousel_layout()

    def update(self, dt_ms: int) -> None:
        """Update held keys, audio mode, animations and queued actions."""
        if self.page == "playing":
            pressed = pygame.key.get_pressed()
            self.held_keys = [k for k in self.held_keys if pressed[k]]
            self.gamestate.update_held_movement(self.held_keys)
        else:
            self.held_keys.clear()
        playing = self.page == "playing"
        if playing != self._music_playing:
            self._music_playing = playing
            self.audio.set_playing_mode(playing)
        self.video.update(dt_ms)
        self.dialogue_box.update(dt_ms, self.page == "carousel")
        self.carousel.update(dt_ms)
        self.info_page.update(dt_ms)

        if not self.is_pressing:
            return

        self.press_elapsed_ms += dt_ms
        if self.press_elapsed_ms < constants.PRESS_FLASH_MS:
            return

        self.is_pressing = False
        if self.pending_action is None:
            return

        action_type, action_data = self.pending_action
        self.pending_action = None
        handler = self._actions.get(action_type)
        if handler is not None:
            handler(action_data)

    def _draw_carousel(self) -> None:
        """Draw the logo, menu carousel, dialogue box and footer."""
        self.header.draw(self.screen, self.carousel_layout["header_rect"])
        self.hoverable_rects = self.carousel.draw(
            self.screen,
            self.window_width // 2,
            self.carousel_layout["carousel_center_y"],
            self.is_pressing,
        )
        self.dialogue_box.draw(self.screen)
        self.footer.draw(self.screen, self.content_bottom)

    def _draw_info_page(self) -> None:
        """Draw the instructions or credits page."""
        self.info_page.draw(
            self.screen,
            self.window_width,
            self.content_top,
            self.content_bottom,
            self.entered_label,
        )

    def _draw_scoreboard_page(self) -> None:
        """Draw the scoreboard using the saved scores."""
        data = self.gamestate.load_scores()[::-1]
        self.scoreboard_page.draw(
            self.screen,
            self.window_width,
            self.content_top,
            self.content_bottom,
            data,
        )

    def _draw_sound_page(self) -> None:
        """Draw the sound page with the current volumes."""
        self.sound_page.draw(
            self.screen,
            self.window_width,
            self.content_top,
            self.content_bottom,
            [self.audio.music_volume, self.audio.sfx_volume],
        )

    def _draw_skin_1p(self) -> None:
        """Draw the single-player skin page and keep its arrow rects."""
        self.skin_arrow_rects_1p = self.skins.draw_single_player_page(
            self.screen, self.skin_selected, self.content_top,
            self.content_bottom
        )

    def _draw_skin_2p(self) -> None:
        """Draw the two-player skin page and keep its arrow rects."""
        self.skin_arrow_rects_2p = self.skins.draw_two_player_page(
            self.screen,
            self.player1_skin,
            self.player2_skin,
            self.content_top,
            self.content_bottom,
            self.player1_ready,
            self.player2_ready,
        )

    def _draw_playing(self) -> None:
        """Update and draw the gameplay screen."""
        self.plying.draw()

    def draw(self) -> None:
        """Draw the video, panel, active page, back button and cursor."""
        self.screen.fill((0, 0, 0))
        self.video.draw(self.screen)
        panel = pygame.Rect(
            0,
            self.content_top,
            self.window_width,
            self.content_bottom - self.content_top,
        )
        render.paint.panel(self.screen, panel, radius=12)

        self.hoverable_rects = []
        drawer = self._page_drawers.get(self.page)

        if drawer is not None:
            drawer()

        if self._should_draw_back_to_menu():
            self.back_to_menu.update_position()
            self.back_to_menu.draw()

        self.cursor.draw(self.screen, self._cursor_state())

        pygame.display.flip()

    def run(self) -> None:
        """Run the main loop, then release the video and exit."""
        while self.running:
            dt_ms = self.clock.tick(TARGET_FPS)

            move_event: pygame.event.Event | None = None
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    continue
                self.dialogue_box.handle_event(event, self.page == "carousel")
                if (
                    self.page == "playing"
                    and event.type == pygame.KEYDOWN
                    and event.key in GRID_KEYS
                ):
                    if event.key in self.held_keys:
                        self.held_keys.remove(event.key)
                    self.held_keys.append(event.key)
                    move_event = event
                    continue
                self.handle_input(event)

            if move_event is not None:
                self.handle_input(move_event)

            self.update(dt_ms)
            self.draw()

        self.video.release()
        pygame.quit()
        sys.exit()

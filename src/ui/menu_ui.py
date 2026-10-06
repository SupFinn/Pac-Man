from __future__ import annotations

from typing import Any, TypedDict, cast

import pygame

from src.media import constants
from src.media import render
from src.media.media import AudioManager

TypedFrame = tuple[pygame.Surface, pygame.Surface]


class Header:
    def __init__(self, window_width: int) -> None:
        """Load the logo scaled to a ratio of the window width."""
        logo_width = max(1, int(window_width * constants.LOGO_WIDTH_RATIO))
        self.logo: pygame.Surface = render.images.load_by_width(
            constants.LOGO_FILE, logo_width
        )

    @property
    def total_height(self) -> int:
        """Return the height of the logo in pixels."""
        return cast(int, self.logo.get_height())

    def layout(self, window_width: int, carousel_top: int) -> pygame.Rect:
        """Return the logo rect centered horizontally at the given top
        position."""
        return self.logo.get_rect(midtop=(window_width // 2, carousel_top))

    def draw(self, screen: pygame.Surface, logo_rect: pygame.Rect) -> None:
        """Draw the logo, shifted up by the logo top offset."""
        screen.blit(self.logo, logo_rect.move(0, -constants.LOGO_TOP_OFFSET))


class Footer:
    def __init__(self, window_width: int, window_height: int) -> None:
        """Build the key-hint bar sized from the window height."""
        font = render.fonts.get(
            int(window_height * constants.FOOTER_SIZE_RATIO)
        )
        self.surface: pygame.Surface = render.paint.hint_bar(
            constants.FOOTER_KEYS, font
        )
        self.window_width: int = window_width
        self.window_height: int = window_height

    def draw(
        self, screen: pygame.Surface, bottom_y: int | None = None
    ) -> None:
        """Draw the hint bar centered near the bottom of the content area."""
        bottom = self.window_height if bottom_y is None else bottom_y
        rect = self.surface.get_rect(
            midbottom=(
                self.window_width // 2,
                bottom - constants.FOOTER_BOTTOM_MARGIN,
            )
        )
        screen.blit(self.surface, rect)


class DialogueBox:
    def __init__(
        self, window_width: int, content_bottom: int, audio: AudioManager
    ) -> None:
        """Load emotes and the speech box, and pre-render all typewriter text
        frames."""
        self.audio = audio
        sheet = render.IconSheet(constants.EMOTES_FILE)
        self.sets: dict[str, list[pygame.Surface]] = {
            "normal": self._build_frames(sheet, constants.EMOTE_RECTS),
            "hover": self._build_frames(sheet, constants.EMOTE_HOVER_RECTS),
            "click": self._build_frames(sheet, constants.EMOTE_CLICK_RECTS),
            "afk": self._build_frames(sheet, constants.EMOTE_AFK_RECTS),
        }
        self.mode: str = "normal"
        self.mode_ms: int = 0
        self.idle_ms: int = 0
        self.click_count: int = 0
        self.click_timer_ms: int = 0

        self.frame_index: int = 0
        self.elapsed_ms: int = 0

        width = max(1, int(window_width * constants.DIALOGUE_WIDTH_RATIO))
        self.box: pygame.Surface = render.images.load_by_width(
            constants.DIALOGUE_BOX, width
        )
        self.box_rect: pygame.Rect = self.box.get_rect(
            bottomleft=(
                constants.DIALOGUE_PADDING,
                content_bottom - constants.DIALOGUE_PADDING,
            )
        )

        base_size = int(self.box.get_height() * constants.BASE_FONT_RATIO)
        max_text_width = int(width * constants.DIALOGUE_TEXT_WIDTH_RATIO)
        font = render.fonts.fit_font(
            constants.DIALOGUE_SIZE_TEXT, base_size, max_text_width
        )

        self.messages: dict[str, list[str]] = {
            "normal": constants.DIALOGUE_TEXTS,
            "hover": constants.DIALOGUE_HOVER_TEXTS,
            "click": constants.DIALOGUE_CLICK_TEXTS,
            "afk": constants.DIALOGUE_AFK_TEXTS,
        }
        self.typed_frames: dict[str, list[list[TypedFrame]]] = {
            mode: [
                [
                    (
                        font.render(t[:i], True, constants.ACCENT_COLOR),
                        font.render(t[:i], True, constants.SHADOW_COLOR),
                    )
                    for i in range(1, len(t) + 1)
                ]
                for t in texts
            ]
            for mode, texts in self.messages.items()
        }

        self.text_rect: pygame.Rect = pygame.Rect(
            self.box_rect.left + constants.DIALOGUE_TEXT_PADDING_X,
            self.box_rect.top + constants.DIALOGUE_TEXT_PADDING_Y,
            *font.size(constants.DIALOGUE_SIZE_TEXT),
        )
        self.message_index: int = 0
        self.chars_shown: int = 0
        self.type_elapsed_ms: int = 0

        emote_y = content_bottom - constants.DIALOGUE_PADDING
        emote_y -= constants.DIALOGUE_EMOTE_BOTTOM_GAP
        self.emote_pos: tuple[int, int] = (
            constants.DIALOGUE_PADDING + constants.EMOTE_X_GAP,
            emote_y,
        )

        self.hit_rect: pygame.Rect = pygame.Rect(
            self.emote_pos, (constants.EMOTE_SIZE, constants.EMOTE_SIZE)
        ).inflate(20, 20)

    @staticmethod
    def _build_frames(
        sheet: render.IconSheet, rects: list[pygame.Rect]
    ) -> list[pygame.Surface]:
        """Cut the given emote rects from the sheet,
        scaled to the emote size."""
        return [
            sheet.scaled_to_height(rect, constants.EMOTE_SIZE)
            for rect in rects
        ]

    def _set_mode(self, mode: str) -> None:
        """Switch the mascot mode, resetting its animation, typing state and
        sound."""
        self.audio.stop(*constants.EMOTE_SOUNDS.values())
        sound_name = constants.EMOTE_SOUNDS.get(mode)
        if sound_name is not None:
            self.audio.play(sound_name, -1 if mode == "afk" else 0)

        self.mode = mode
        self.mode_ms = 0
        self.frame_index = 0
        self.elapsed_ms = 0
        self.message_index = 0
        self.chars_shown = 0
        self.type_elapsed_ms = 0

    def handle_event(
        self, event: pygame.event.Event, on_screen: bool
    ) -> None:
        """Track hover, clicks and idle time to switch between normal, hover,
        click and afk."""
        if event.type in (
            pygame.KEYDOWN,
            pygame.MOUSEMOTION,
            pygame.MOUSEBUTTONDOWN,
        ):
            self.idle_ms = 0
            if self.mode == "afk":
                self._set_mode("normal")

        if not on_screen:
            if self.mode == "hover":
                self._set_mode("normal")
            return

        if event.type == pygame.MOUSEMOTION:
            inside = self.hit_rect.collidepoint(event.pos)
            if inside and self.mode == "normal":
                self._set_mode("hover")
            elif not inside and self.mode == "hover":
                self._set_mode("normal")

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.hit_rect.collidepoint(event.pos):
                if self.mode == "click":
                    self.mode_ms = 0
                else:
                    self.click_count += 1
                    self.click_timer_ms = 0
                    if self.click_count >= constants.EMOTE_CLICKS_NEEDED:
                        self.click_count = 0
                        self._set_mode("click")

    def update(self, dt_ms: int, on_screen: bool = True) -> None:
        """Advance emote frames, mode timers and the
        typewriter text by dt_ms."""
        if not on_screen:
            self.idle_ms = 0
            if self.mode != "normal":
                self._set_mode("normal")
        self.elapsed_ms += dt_ms
        frames = self.sets[self.mode]
        if self.elapsed_ms >= constants.EMOTE_FRAME_MS:
            self.elapsed_ms %= constants.EMOTE_FRAME_MS
            self.frame_index = (self.frame_index + 1) % len(frames)

        self.mode_ms += dt_ms
        self.idle_ms += dt_ms

        if self.click_count:
            self.click_timer_ms += dt_ms
            if self.click_timer_ms > constants.EMOTE_CLICK_WINDOW_MS:
                self.click_count = 0

        if (
            self.mode == "click"
            and self.mode_ms >= constants.EMOTE_CLICK_IDLE_MS
        ):
            inside = self.hit_rect.collidepoint(pygame.mouse.get_pos())
            self._set_mode("hover" if inside else "normal")
        elif self.mode == "normal" and self.idle_ms >= constants.EMOTE_AFK_MS:
            self._set_mode("afk")

        texts = self.messages[self.mode]
        text = texts[self.message_index]
        cycle = len(text) * constants.TYPE_CHAR_MS
        cycle += constants.TYPE_END_PAUSE_MS

        self.type_elapsed_ms += dt_ms
        if self.type_elapsed_ms >= cycle:
            self.type_elapsed_ms -= cycle
            self.message_index = (self.message_index + 1) % len(texts)
            text = texts[self.message_index]

        typed = self.type_elapsed_ms // constants.TYPE_CHAR_MS
        self.chars_shown = min(len(text), typed)

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the speech box, the emote and the typed text."""
        screen.blit(self.box, self.box_rect)
        screen.blit(self.sets[self.mode][self.frame_index], self.emote_pos)
        if self.chars_shown > 0:
            i = self.chars_shown - 1
            text, shadow = self.typed_frames[self.mode][self.message_index][i]
            screen.blit(shadow, self.text_rect.move(*constants.SHADOW_OFFSET))
            screen.blit(text, self.text_rect)


class MenuItem(TypedDict):
    label: str
    main_button: pygame.Surface
    main_pressed: pygame.Surface
    main_text: pygame.Surface
    side_button: pygame.Surface
    side_text: pygame.Surface
    main_icon: pygame.Surface | None
    main_icon_pressed: pygame.Surface | None
    side_icon: pygame.Surface | None


class MenuFrame(TypedDict):
    name: str
    items: list[MenuItem]
    selected_index: int


class BackToMenu:
    def __init__(self, screen: pygame.Surface, video: Any) -> None:
        """Load the back icon and create its hit rect."""
        self.screen = screen
        self.video = video

        self.icon = render.icons.scaled_to_height(
            constants.ICON_RECTS["BACK"]["normal"],
            constants.BACK_TO_MENU_ICON_HEIGHT,
        )

        self.rect = self.icon.get_rect()

    def update_position(self) -> None:
        """Place the back button at the top-left of the video area."""
        video_top = max(0, self.video.offset_y)

        self.rect.topleft = (
            constants.BACK_TO_MENU_OFFSET_X,
            video_top + constants.BACK_TO_MENU_OFFSET_Y,
        )

    def draw(self) -> None:
        """Draw the back icon, with the pressed look on hover."""
        self.screen.blit(self.icon, self.rect)
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            pressed = render.icons.scaled_to_height(
                constants.ICON_RECTS["BACK"]["pressed"],
                constants.BACK_TO_MENU_ICON_HEIGHT,
            )
            self.screen.blit(
                pressed, pressed.get_rect(center=self.rect.center)
            )


class MenuCarousel:
    ARROW_HIT_PADDING = 30

    def __init__(self) -> None:
        """Set up button sizes, the item cache and the menu stack starting at
        MAIN."""
        self.main_height: int = constants.MAIN_BUTTON_HEIGHT
        self.side_height: int = constants.SIDE_BUTTON_HEIGHT
        self.spacing: int = (
            (self.main_height + self.side_height) // 2
            + constants.CAROUSEL_GAP
        )

        self.main_font_size: int = int(
            self.main_height * constants.BASE_FONT_RATIO
        )
        self.side_font_size: int = int(
            self.side_height * constants.BASE_FONT_RATIO
        )

        self._items_cache: dict[str, list[MenuItem]] = {}
        self.stack: list[MenuFrame] = [self._frame("MAIN")]

        self.arrow_flash_dir: str | None = None
        self.arrow_flash_ms: int = 0

        self.up_arrow_rect: pygame.Rect | None = None
        self.down_arrow_rect: pygame.Rect | None = None

    def _frame(self, name: str) -> MenuFrame:
        """Return a new menu frame for the name, building and caching its items
        once."""
        if name not in self._items_cache:
            if name == "MAIN":
                labels = constants.MENU_ITEMS
            else:
                labels = constants.SUBMENU_DEFS[name]
            self._items_cache[name] = self._build_items(labels)
        return {
            "name": name,
            "items": self._items_cache[name],
            "selected_index": 0,
        }

    @staticmethod
    def _icon_source(
        label: str,
    ) -> tuple[pygame.Rect, pygame.Rect, render.IconSheet] | None:
        """Return the normal/pressed rects and sheet for a label's icon, or
        None."""
        if label in constants.ICON_RECTS:
            rects = constants.ICON_RECTS[label]
            return rects["normal"], rects["pressed"], render.icons
        if label in constants.SUBMENU_ICON_RECTS:
            rects = constants.SUBMENU_ICON_RECTS[label]
            return rects["normal"], rects["pressed"], render.more_icons
        return None

    def _build_items(self, labels: list[str]) -> list[MenuItem]:
        """Pre-render the buttons, texts and icons for
        every label of a menu."""
        items: list[MenuItem] = []
        for label in labels:
            main_button, main_text = self._build_variant(
                label, self.main_height, self.main_font_size
            )
            main_pressed = render.buttons.get(
                constants.BUTTON_PRESSED_RECT,
                (main_button.get_width(), self.main_height),
            )

            side_button, side_text = self._build_variant(
                label, self.side_height, self.side_font_size
            )
            side_button = side_button.copy()
            side_button.set_alpha(constants.SIDE_ALPHA)
            side_text.set_alpha(constants.SIDE_ALPHA)

            main_icon: pygame.Surface | None = None
            main_icon_pressed: pygame.Surface | None = None
            side_icon: pygame.Surface | None = None
            source = self._icon_source(label)
            if source is not None:
                normal_rect, pressed_rect, sheet = source
                main_icon = sheet.scaled_to_height(
                    normal_rect, self.main_height
                )
                main_icon_pressed = sheet.scaled_to_height(
                    pressed_rect, self.main_height
                )
                side_icon = sheet.scaled_to_height(
                    normal_rect, self.side_height
                ).copy()
                side_icon.set_alpha(constants.SIDE_ALPHA)

            items.append({
                "label": label,
                "main_button": main_button,
                "main_pressed": main_pressed,
                "main_text": main_text,
                "side_button": side_button,
                "side_text": side_text,
                "main_icon": main_icon,
                "main_icon_pressed": main_icon_pressed,
                "side_icon": side_icon,
            })
        return items

    @staticmethod
    def _build_variant(
        label: str, height: int, font_size: int
    ) -> tuple[pygame.Surface, pygame.Surface]:
        """Build a button sprite stretched to fit its label, and the fitted
        text surface."""
        padding = int(height * constants.TEXT_PADDING_RATIO)

        button = constants.BUTTON_RECT
        base_width = max(1, int(height * button.width / button.height))

        max_width = int(base_width * constants.MAX_STRETCH_RATIO)

        text_space = max(1, max_width - padding * 2)
        text = render.fonts.fit_text(
            label, font_size, constants.ACCENT_COLOR, text_space
        )

        wanted_width = text.get_width() + padding * 2
        width = max(base_width, min(wanted_width, max_width))

        sprite = render.buttons.get(button, (width, height))
        return sprite, text

    @property
    def current_menu(self) -> MenuFrame:
        """Return the menu frame on top of the stack."""
        return self.stack[-1]

    def selected_label(self) -> str:
        """Return the label of the currently selected item."""
        menu = self.current_menu
        return menu["items"][menu["selected_index"]]["label"]

    def move_selection(self, delta: int) -> bool:
        """Move the selection by delta, returning True if it changed."""
        menu = self.current_menu
        index = max(
            0, min(len(menu["items"]) - 1, menu["selected_index"] + delta)
        )
        if index == menu["selected_index"]:
            return False
        menu["selected_index"] = index
        self.arrow_flash_dir = "up" if delta < 0 else "down"
        self.arrow_flash_ms = constants.CAROUSEL_ARROW_FLASH_MS
        return True

    def push(self, name: str) -> None:
        """Open a submenu by pushing its frame on the stack."""
        self.stack.append(self._frame(name))

    def pop(self) -> bool:
        """Close the current submenu, returning False if
        already at the root."""
        if len(self.stack) == 1:
            return False
        self.stack.pop()
        return True

    def reset_to_root(self) -> None:
        """Close all submenus and go back to MAIN."""
        del self.stack[1:]

    @staticmethod
    def resolve_action(
        menu_name: str, label: str
    ) -> tuple[str, str | int | None]:
        """Map a menu name and label to an (action, data) pair."""
        action = constants.MENU_ACTIONS.get((menu_name, label))
        if action is not None:
            return action
        if label == "BACK" and menu_name != "MAIN":
            return "pop", None
        if label in constants.THEME_LABEL_TO_NUMBER:
            return "theme", constants.THEME_LABEL_TO_NUMBER[label]
        if label in constants.SUBMENU_DEFS:
            return "push", label
        return "noop", None

    def update(self, dt_ms: int) -> None:
        """Count down the arrow flash timer by dt_ms."""
        if self.arrow_flash_ms <= 0:
            return
        self.arrow_flash_ms -= dt_ms
        if self.arrow_flash_ms <= 0:
            self.arrow_flash_ms = 0
            self.arrow_flash_dir = None

    def draw(
        self,
        screen: pygame.Surface,
        center_x: int,
        center_y: int,
        is_pressing: bool,
    ) -> list[tuple[pygame.Rect, int]]:
        """Draw the previous, current and next buttons and return their
        hoverable rects."""
        menu = self.current_menu
        items = menu["items"]
        selected_index = menu["selected_index"]
        hoverable: list[tuple[pygame.Rect, int]] = []
        first_rect: pygame.Rect | None = None
        last_rect: pygame.Rect | None = None

        for offset in (-1, 0, 1):
            index = selected_index + offset
            if not 0 <= index < len(items):
                continue

            item = items[index]
            if offset == 0:
                if is_pressing:
                    sprite = item["main_pressed"]
                    icon = item["main_icon_pressed"]
                else:
                    sprite = item["main_button"]
                    icon = item["main_icon"]
                text = item["main_text"]
            else:
                sprite = item["side_button"]
                text = item["side_text"]
                icon = item["side_icon"]

            rect = sprite.get_rect(
                center=(center_x, center_y + offset * self.spacing)
            )
            screen.blit(sprite, rect)
            screen.blit(text, text.get_rect(center=rect.center))

            if icon is None:
                hoverable.append((rect, index))
            else:
                icon_rect = icon.get_rect(
                    midright=(
                        rect.left - constants.ICON_BUTTON_GAP,
                        rect.centery,
                    )
                )
                screen.blit(icon, icon_rect)
                hoverable.append((rect.union(icon_rect), index))

            if first_rect is None:
                first_rect = rect
            last_rect = rect

        self._draw_arrows(
            screen, center_x, selected_index, len(items), first_rect, last_rect
        )
        return hoverable

    def _draw_one_arrow(
        self,
        screen: pygame.Surface,
        center_x: int,
        y: int,
        normal_rect: pygame.Rect,
        pressed_rect: pygame.Rect,
        is_flashing: bool,
    ) -> pygame.Rect:
        """Draw one carousel arrow and return its padded hit rect."""
        rect_src = pressed_rect if is_flashing else normal_rect
        icon = render.icons.scaled_by(
            rect_src, constants.CAROUSEL_ARROW_SCALE
        )
        icon_rect = icon.get_rect(center=(center_x, y))
        screen.blit(icon, icon_rect)
        pad = self.ARROW_HIT_PADDING
        return icon_rect.inflate(pad, pad)

    def _draw_arrows(
        self,
        screen: pygame.Surface,
        center_x: int,
        selected_index: int,
        count: int,
        first_rect: pygame.Rect | None,
        last_rect: pygame.Rect | None,
    ) -> None:
        """Draw the up/down arrows when more items exist and store their hit
        rects."""
        self.up_arrow_rect = None
        self.down_arrow_rect = None
        if first_rect is None or last_rect is None:
            return

        height = (
            constants.CAROUSEL_UP_ARROW.height * constants.CAROUSEL_ARROW_SCALE
        )

        if selected_index > 0:
            y = first_rect.top - constants.CAROUSEL_ARROW_GAP - height // 2
            self.up_arrow_rect = self._draw_one_arrow(
                screen,
                center_x,
                y,
                constants.CAROUSEL_UP_ARROW,
                constants.CAROUSEL_UP_ARROW_PRESSED,
                self.arrow_flash_dir == "up",
            )

        if selected_index < count - 1:
            y = last_rect.bottom + constants.CAROUSEL_ARROW_GAP + height // 2
            self.down_arrow_rect = self._draw_one_arrow(
                screen,
                center_x,
                y,
                constants.CAROUSEL_DOWN_ARROW,
                constants.CAROUSEL_DOWN_ARROW_PRESSED,
                self.arrow_flash_dir == "down",
            )

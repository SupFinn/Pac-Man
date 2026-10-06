from __future__ import annotations

import math
from typing import Any, TypedDict

import pygame

from src.media import constants
from src.media import render


class SoundMeter(TypedDict):
    label: str
    icon_rect: pygame.Rect


class SoundPage:
    def __init__(self, title: str, meters: list[SoundMeter]) -> None:
        """Store the title and meters and build the hint bar."""
        self.title: str = title
        self.meters: list[SoundMeter] = meters
        self.selected_index: int = 0
        self.hint_bar: pygame.Surface = render.paint.hint_bar(
            constants.SOUND_HINT_KEYS,
            render.fonts.get(constants.SLIDER_HINT_SIZE),
        )

    def move_selection(self, delta: int) -> None:
        """Move the selected meter by delta, clamped to the list."""
        self.selected_index = max(
            0, min(len(self.meters) - 1, self.selected_index + delta)
        )

    def draw(
        self,
        screen: pygame.Surface,
        window_width: int,
        content_top: int,
        content_bottom: int,
        values: list[float],
    ) -> None:
        """Draw the sound panel with its meters and hint bar."""
        center_y = content_top + (content_bottom - content_top) // 2
        panel_rect = pygame.Rect(
            0, 0, constants.SOUND_PANEL_WIDTH, constants.SOUND_PANEL_HEIGHT
        )
        panel_rect.center = (window_width // 2, center_y)

        render.paint.panel(
            screen, panel_rect,
            radius=constants.SOUND_PANEL_RADIUS,
            fill_alpha=constants.SOUND_PANEL_FILL_ALPHA,
            border_color=constants.ACCENT_COLOR,
        )

        gap = constants.SOUND_METER_ROW_GAP
        start_y = panel_rect.centery - (len(self.meters) - 1) * gap // 2
        start_y += 15

        for index, meter in enumerate(self.meters):
            self._draw_meter(
                screen,
                panel_rect.centerx,
                meter,
                values[index],
                start_y + index * gap,
                self.selected_index == index,
            )

        screen.blit(self.hint_bar, self.hint_bar.get_rect(
            midbottom=(panel_rect.centerx, panel_rect.bottom - 20)
        ))

    @staticmethod
    def _draw_meter(
        screen: pygame.Surface,
        center_x: int,
        meter: SoundMeter,
        value: float,
        center_y: int,
        selected: bool,
    ) -> None:
        """Draw one labeled tick meter with its percent value and selection
        outline."""
        label_font = render.fonts.get(constants.SOUND_LABEL_SIZE)
        render.paint.text(
            screen, label_font, meter["label"], constants.TITLE_COLOR,
            anchor_point="midright",
            anchor_pos=(center_x - constants.SOUND_LABEL_GAP, center_y),
            shadow=None,
        )

        tick = render.icons.scaled_by(
            meter["icon_rect"], constants.SOUND_METER_TICK_SCALE
        )
        tick_width, tick_height = tick.get_size()
        empty_tick = tick.copy()
        empty_tick.set_alpha(constants.SOUND_METER_EMPTY_ALPHA)

        max_ticks = constants.SOUND_METER_MAX_TICKS
        filled = round(value * max_ticks)
        start_x = center_x - constants.SOUND_METER_START_X
        step = tick_width + constants.SOUND_METER_TICK_GAP

        for index in range(max_ticks):
            surface = tick if index < filled else empty_tick
            screen.blit(
                surface,
                surface.get_rect(midleft=(start_x + index * step, center_y)),
            )

        end_x = start_x + max_ticks * step

        if selected:
            pad = constants.SOUND_METER_HIGHLIGHT_PAD
            highlight = pygame.Rect(
                start_x - pad,
                center_y - tick_height // 2 - pad,
                end_x - start_x + pad,
                tick_height + pad * 2,
            )
            pygame.draw.rect(
                screen, constants.TITLE_COLOR, highlight,
                width=2, border_radius=6,
            )

        percent_font = render.fonts.get(constants.SOUND_PERCENT_SIZE)
        render.paint.text(
            screen, percent_font, f"{round(value * 100)}%",
            constants.BODY_TEXT_COLOR,
            anchor_point="midleft",
            anchor_pos=(end_x + constants.SOUND_PERCENT_GAP, center_y),
            shadow=None,
        )


class SkinSelector:
    def __init__(self, window_width: int, window_height: int) -> None:
        """Load skin previews, carousel layouts and the hint bars."""
        self.window_width: int = window_width
        self.window_height: int = window_height
        self.images: list[pygame.Surface | None] = self._load_images()

        self.cell_rects: dict[str, pygame.Rect] = {}

        self.carousel_layouts: dict[str, dict[str, float]] = {
            "single": {
                "main_ratio": constants.SKIN_CAROUSEL_MAIN_HEIGHT_RATIO,
                "side_ratio": constants.SKIN_CAROUSEL_SIDE_HEIGHT_RATIO,
                "gap": constants.SKIN_CAROUSEL_GAP,
                "arrow_scale": constants.SKIN_CAROUSEL_ARROW_SCALE,
                "side_alpha": constants.SKIN_CAROUSEL_SIDE_ALPHA,
                "name_size": constants.SKIN_NAME_SIZE,
            },
            "two_player": {
                "main_ratio": constants.SKIN_CAROUSEL_MAIN_HEIGHT_RATIO_2P,
                "side_ratio": constants.SKIN_CAROUSEL_SIDE_HEIGHT_RATIO_2P,
                "gap": constants.SKIN_CAROUSEL_GAP_2P,
                "arrow_scale": constants.SKIN_CAROUSEL_ARROW_SCALE_2P,
                "side_alpha": constants.SKIN_CAROUSEL_SIDE_ALPHA,
                "name_size": constants.SKIN_NAME_SIZE_2P,
            },
        }

        self.hint_bar: pygame.Surface = render.paint.hint_bar(
            constants.SKIN_HINT_KEYS,
            render.fonts.get(constants.SKIN_HINT_SIZE),
        )
        self.hint_bars_2p: list[pygame.Surface] = [
            render.paint.hint_bar(
                keys, render.fonts.get(constants.SKIN_2P_HINT_SIZE)
            )
            for keys in (
                constants.SKIN_2P_HINT_KEYS_1,
                constants.SKIN_2P_HINT_KEYS_2,
            )
        ]

    @staticmethod
    def _load_images() -> list[pygame.Surface | None]:
        """Cut every skin preview from the sheet, using None on failure."""
        images: list[pygame.Surface | None] = []
        for index, rect in enumerate(constants.SKIN_PROFILE_RECTS):
            try:
                images.append(render.skins_sheet.get(rect))
            except (pygame.error, ValueError) as exc:
                print("Could not load skin frame:", index, exc)
                images.append(None)
        return images

    @property
    def count(self) -> int:
        """Return the number of available skins."""
        return len(self.images)

    def move_selection(self, index: int, delta: int) -> int:
        """Return the skin index moved by delta, wrapping around."""
        if self.count == 0:
            return index
        return (index + delta) % self.count

    def _build_skin_cell(
        self, index: int, height: int, selected: bool
    ) -> pygame.Surface:
        """Build a bordered cell with the skin preview fitted inside it."""
        source_rect = (
            constants.SKIN_BORDER_MAIN_RECT
            if selected
            else constants.SKIN_BORDER_SIDE_RECT
        )
        width = max(1, round(source_rect.width * height / source_rect.height))
        cell = render.skin_border.get(source_rect, (width, height)).copy()

        image = self.images[index] if 0 <= index < len(self.images) else None
        if image is not None:
            fit = min(
                width * constants.SKIN_BORDER_INNER_WIDTH_RATIO
                / image.get_width(),
                height * constants.SKIN_BORDER_INNER_HEIGHT_RATIO
                / image.get_height(),
            )
            icon = pygame.transform.smoothscale_by(
                image, fit * constants.SKIN_ICON_SCALE
            )
            center = (
                width // 2 + constants.SKIN_BORDER_INNER_OFFSET_X,
                height // 2 + constants.SKIN_BORDER_INNER_OFFSET_Y,
            )
            cell.blit(icon, icon.get_rect(center=center))
        return cell

    @staticmethod
    def _draw_title(
        screen: pygame.Surface, text: str, center_x: int, content_top: int
    ) -> None:
        """Draw the page title at the top of the content area."""
        render.paint.text(
            screen, render.fonts.get(constants.SKIN_TITLE_SIZE), text,
            constants.TITLE_COLOR,
            anchor_point="midtop",
            anchor_pos=(center_x, content_top + constants.SKIN_TITLE_TOP),
            shadow=constants.TITLE_SHADOW_OFFSET,
        )

    def _draw_side_cell(
        self,
        screen: pygame.Surface,
        side: str,
        selected_index: int,
        main_rect: pygame.Rect,
        center_y: int,
        side_height: int,
        side_alpha: int,
        gap: int,
    ) -> pygame.Rect:
        """Draw the dimmed left or right neighbor skin and return its rect."""
        delta = -1 if side == "left" else 1
        index = (selected_index + delta) % self.count
        cell = self._build_skin_cell(index, side_height, False)
        cell.set_alpha(side_alpha)

        if side == "left":
            rect = cell.get_rect(midright=(main_rect.left - gap, center_y))
        else:
            rect = cell.get_rect(midleft=(main_rect.right + gap, center_y))

        screen.blit(cell, rect)
        self.cell_rects[side] = rect
        return rect

    @staticmethod
    def _draw_hover_arrow(
        screen: pygame.Surface,
        normal_rect: pygame.Rect,
        pressed_rect: pygame.Rect,
        arrow_scale: float,
        anchor_point: str,
        anchor_pos: tuple[int, int],
        mouse: tuple[int, int],
    ) -> pygame.Rect:
        """Draw an arrow (pressed look on hover) and return its rect."""
        normal = render.icons.scaled_by(normal_rect, arrow_scale)
        rect = normal.get_rect(**{anchor_point: anchor_pos})
        if rect.collidepoint(mouse):
            sprite = render.icons.scaled_by(pressed_rect, arrow_scale)
        else:
            sprite = normal
        screen.blit(sprite, rect)
        return rect

    def _draw_carousel(
        self,
        screen: pygame.Surface,
        center_x: int,
        center_y: int,
        selected_index: int,
        layout: str,
    ) -> tuple[pygame.Rect, pygame.Rect]:
        """Draw the bobbing skin carousel with name and arrows, returning the
        arrow rects."""
        params = self.carousel_layouts[layout]
        main_height = max(16, int(self.window_height * params["main_ratio"]))
        side_height = max(16, int(self.window_height * params["side_ratio"]))
        gap = int(params["gap"])
        side_alpha = int(params["side_alpha"])
        name_size = int(params["name_size"])
        arrow_scale = params["arrow_scale"]

        bob_angle = pygame.time.get_ticks() * constants.SKIN_CAROUSEL_BOB_SPEED
        bob = int(math.sin(bob_angle) * constants.SKIN_CAROUSEL_BOB_AMPLITUDE)
        main_cell = self._build_skin_cell(selected_index, main_height, True)
        main_rect = main_cell.get_rect(center=(center_x, center_y + bob))

        self.cell_rects = {"main": main_rect}
        left_edge, right_edge = main_rect.left, main_rect.right

        if self.count > 1:
            left_rect = self._draw_side_cell(
                screen, "left", selected_index, main_rect,
                center_y, side_height, side_alpha, gap,
            )
            left_edge = left_rect.left

            right_rect = self._draw_side_cell(
                screen, "right", selected_index, main_rect,
                center_y, side_height, side_alpha, gap,
            )
            right_edge = right_rect.right

        screen.blit(main_cell, main_rect)

        if 0 <= selected_index < len(constants.SKIN_NAMES):
            name_font = render.fonts.get(name_size)
            render.paint.text(
                screen, name_font, constants.SKIN_NAMES[selected_index],
                constants.SKIN_NAME_COLOR,
                anchor_point="midtop",
                anchor_pos=(
                    center_x,
                    main_rect.bottom + constants.SKIN_NAME_GAP,
                ),
                shadow=None,
            )

        mouse = pygame.mouse.get_pos()
        arrow_gap = constants.SKIN_CAROUSEL_ARROW_GAP

        left_arrow_rect = self._draw_hover_arrow(
            screen,
            constants.SKIN_CAROUSEL_LEFT_ARROW_RECT,
            constants.SKIN_CAROUSEL_LEFT_ARROW_PRESSED_RECT,
            arrow_scale,
            "midright",
            (left_edge - arrow_gap, center_y),
            mouse,
        )
        right_arrow_rect = self._draw_hover_arrow(
            screen,
            constants.SKIN_CAROUSEL_RIGHT_ARROW_RECT,
            constants.SKIN_CAROUSEL_RIGHT_ARROW_PRESSED_RECT,
            arrow_scale,
            "midleft",
            (right_edge + arrow_gap, center_y),
            mouse,
        )

        return left_arrow_rect, right_arrow_rect

    @staticmethod
    def _draw_ready_icon(
        screen: pygame.Surface, ready: bool, center: tuple[int, int]
    ) -> None:
        """Draw the ready or not-ready icon centered at a point."""
        rect = constants.READY_ICON_RECTS["ready" if ready else "not_ready"]
        icon = render.icons.scaled_by(rect, constants.READY_ICON_SCALE_2P)
        screen.blit(icon, icon.get_rect(center=center))

    def draw_single_player_page(
        self,
        screen: pygame.Surface,
        selected_index: int,
        content_top: int,
        content_bottom: int,
    ) -> tuple[pygame.Rect, pygame.Rect]:
        """Draw the 1-player skin page and return its arrow rects."""
        center_y = (content_top + content_bottom) // 2

        self._draw_title(
            screen, constants.SKIN_TITLE_TEXT,
            self.window_width // 2, content_top,
        )

        arrows = self._draw_carousel(
            screen, self.window_width // 2, center_y, selected_index, "single"
        )

        screen.blit(self.hint_bar, self.hint_bar.get_rect(
            midbottom=(
                self.window_width // 2,
                content_bottom - constants.SKIN_HINT_BOTTOM,
            )
        ))
        return arrows

    def draw_two_player_page(
        self,
        screen: pygame.Surface,
        player1_skin: int,
        player2_skin: int,
        content_top: int,
        content_bottom: int,
        player1_ready: bool,
        player2_ready: bool,
    ) -> tuple[pygame.Rect, ...]:
        """Draw both players' carousels, ready icons and hints, returning all
        arrow rects."""
        half = self.window_width // 2
        divider_top = content_top + constants.SKIN_2P_DIVIDER_TOP
        divider_bottom = content_bottom - constants.SKIN_2P_DIVIDER_BOTTOM
        divider_height = max(0, divider_bottom - divider_top)
        pygame.draw.rect(
            screen, constants.ACCENT_COLOR,
            pygame.Rect(half - 1, divider_top, 2, divider_height),
        )

        self._draw_title(
            screen, constants.SKIN_TITLE_TEXT_2P, half, content_top
        )

        center_y = (content_top + content_bottom) // 2
        main_height_px = int(
            self.window_height * constants.SKIN_CAROUSEL_MAIN_HEIGHT_RATIO_2P
        )

        all_arrows: list[pygame.Rect] = []

        for center_x, selected_index, ready, hint, label in (
            (
                half // 2,
                player1_skin,
                player1_ready,
                self.hint_bars_2p[0],
                constants.SKIN_PLAYER_LABELS_2P[0],
            ),
            (
                half + half // 2,
                player2_skin,
                player2_ready,
                self.hint_bars_2p[1],
                constants.SKIN_PLAYER_LABELS_2P[1],
            ),
        ):
            left_rect, right_rect = self._draw_carousel(
                screen, center_x, center_y, selected_index, "two_player"
            )
            all_arrows.extend([left_rect, right_rect])

            render.paint.text(
                screen, render.fonts.get(constants.SKIN_PLAYER_LABEL_SIZE),
                label, constants.ACCENT_COLOR,
                anchor_point="midbottom",
                anchor_pos=(
                    center_x,
                    center_y - main_height_px // 2
                    - constants.SKIN_PLAYER_LABEL_GAP,
                ),
                shadow=None,
            )

            ready_y = (
                center_y + main_height_px // 2 + constants.SKIN_READY_GAP_2P
            )
            self._draw_ready_icon(screen, ready, (center_x, ready_y))

            screen.blit(hint, hint.get_rect(
                midbottom=(
                    center_x,
                    content_bottom - constants.SKIN_2P_HINT_BOTTOM,
                )
            ))

        return tuple(all_arrows)


class LevelsPage:
    def __init__(self, gamestate: Any) -> None:
        """Load the locked-level image and hint bar and set the initial
        selection."""
        self.game = gamestate
        self.node_count: int = constants.LEVELS_NODE_COUNT
        self.selected_index: int = 0

        self.node_rects: list[pygame.Rect] = []

        image = pygame.image.load(constants.LOCKED_LEVEL_FILE).convert_alpha()
        node_height = (
            constants.LEVELS_NODE_RECT.height * constants.LEVELS_NODE_SCALE
        )
        height = max(1, int(node_height * constants.LEVELS_LOCKED_SCALE))
        width = max(1, round(image.get_width() * height / image.get_height()))
        self.locked_image: pygame.Surface = pygame.transform.smoothscale(
            image, (width, height)
        )

        self.hint_bar: pygame.Surface = render.paint.hint_bar(
            constants.LEVELS_HINT_KEYS,
            render.fonts.get(constants.LEVELS_HINT_SIZE),
        )

    def move_selection(self, delta: int) -> None:
        """Move the selected level by delta, limited to unlocked levels."""
        last_unlocked = self.game.unlocked_levels - 1
        self.selected_index = max(
            0, min(last_unlocked, self.selected_index + delta)
        )

    def _node_rects(
        self,
        node: pygame.Surface,
        window_width: int,
        content_top: int,
        content_bottom: int,
    ) -> list[pygame.Rect]:
        """Compute the zigzag positions of all level nodes."""
        middle_y = content_top + (content_bottom - content_top) // 2
        low_y = middle_y + constants.LEVELS_HIGH_RISE // 2
        high_y = middle_y - constants.LEVELS_HIGH_RISE // 2
        span = (self.node_count - 1) * constants.LEVELS_STEP_X
        first_x = window_width // 2 - span // 2

        rects: list[pygame.Rect] = []
        for i in range(self.node_count):
            x = first_x + i * constants.LEVELS_STEP_X
            y = low_y if i % 2 == 0 else high_y
            rects.append(node.get_rect(center=(x, y)))
        return rects

    def _draw_lines(
        self, screen: pygame.Surface, rects: list[pygame.Rect]
    ) -> None:
        """Draw the path lines linking consecutive nodes."""
        for a, b in zip(rects, rects[1:]):
            if b.centery < a.centery:
                start = a.midtop
            else:
                start = a.midbottom

            corner = (a.centerx, b.centery)
            end = b.midleft
            pygame.draw.lines(
                screen, constants.LEVELS_LINE_COLOR, False,
                [start, corner, end], constants.LEVELS_LINE_WIDTH,
            )

    def node_at(self, pos: tuple[int, int]) -> int | None:
        """Return the index of the unlocked node at pos, or None."""
        for index, rect in enumerate(self.node_rects):
            if index < self.game.unlocked_levels and rect.collidepoint(pos):
                return index
        return None

    def draw(
        self,
        screen: pygame.Surface,
        window_width: int,
        content_top: int,
        content_bottom: int,
    ) -> None:
        """Draw the whole level map: path, nodes, info
        cards, title and hint."""
        normal = render.icons.scaled_by(
            constants.LEVELS_NODE_RECT, constants.LEVELS_NODE_SCALE
        )
        pressed = render.icons.scaled_by(
            constants.LEVELS_NODE_PRESSED_RECT, constants.LEVELS_NODE_SCALE
        )

        rects = self._node_rects(
            normal, window_width, content_top, content_bottom
        )
        self.node_rects = rects

        self._draw_lines(screen, rects)
        self._draw_nodes(screen, rects, normal, pressed)
        self._draw_info_lines(screen, window_width, rects)
        self._draw_title_and_hint(
            screen, window_width, content_top, content_bottom
        )

    def _draw_nodes(
        self,
        screen: pygame.Surface,
        rects: list[pygame.Rect],
        normal: pygame.Surface,
        pressed: pygame.Surface,
    ) -> None:
        """Draw each node as locked, normal or highlighted, with its number."""
        number_font = render.fonts.get(constants.LEVELS_NUMBER_SIZE)
        mouse = pygame.mouse.get_pos()

        for index, rect in enumerate(rects):
            if index >= self.game.unlocked_levels:
                screen.blit(
                    self.locked_image,
                    self.locked_image.get_rect(center=rect.center),
                )
                continue

            is_pressed = (
                index == self.selected_index or rect.collidepoint(mouse)
            )
            if is_pressed:
                screen.blit(pressed, pressed.get_rect(center=rect.center))
                color = constants.LEVELS_NUMBER_PRESSED_COLOR
            else:
                screen.blit(normal, rect)
                color = constants.LEVELS_NUMBER_COLOR

            render.paint.text(
                screen, number_font, str(index + 1), color,
                anchor_point="center", anchor_pos=rect.center, shadow=None,
            )

    def _draw_info_lines(
        self,
        screen: pygame.Surface,
        window_width: int,
        rects: list[pygame.Rect],
    ) -> None:
        """Draw the info cards describing the main and
        optional level ranges."""
        range_font = render.fonts.get(constants.LEVELS_CARD_RANGE_SIZE)
        tag_font = render.fonts.get(constants.LEVELS_CARD_TAG_SIZE)
        text_font = render.fonts.get(constants.LEVELS_INFO_SIZE)

        cards = constants.LEVELS_INFO_CARDS
        pad = constants.LEVELS_CARD_PADDING
        gap = constants.LEVELS_CARD_GAP
        card_w = constants.LEVELS_CARD_WIDTH

        wrapped = [
            render.fonts.wrap_text(text, text_font, card_w - pad * 2)
            for _, _, text in cards
        ]
        head_h = range_font.get_height()
        line_h = text_font.get_height()
        body_h = max(len(lines) for lines in wrapped) * line_h
        card_h = pad * 2 + head_h + 12 + body_h

        total_w = len(cards) * card_w + (len(cards) - 1) * gap
        left = window_width // 2 - total_w // 2
        top = (max(rect.bottom for rect in rects) +
               constants.LEVELS_INFO_TOP_GAP)

        for i, (levels, tag, _) in enumerate(cards):
            main = i == 0
            rect = pygame.Rect(left + i * (card_w + gap), top, card_w, card_h)

            render.paint.panel(
                screen, rect,
                radius=14,
                fill_alpha=constants.LEVELS_CARD_ALPHA,
                border_color=constants.ACCENT_COLOR,
                border_width=2 if main else 1,
                border_alpha=255 if main else 110,
            )

            render.paint.text(
                screen, range_font, f"LEVELS {levels}",
                constants.TITLE_COLOR,
                anchor_point="topleft",
                anchor_pos=(rect.left + pad, rect.top + pad),
                shadow=None,
            )

            tag_color = (
                constants.LEVELS_TAG_TEXT_DARK if main
                else constants.ACCENT_COLOR
            )
            tag_surf = tag_font.render(tag, True, tag_color)
            chip = tag_surf.get_rect(
                midright=(rect.right - pad, rect.top + pad + head_h // 2)
            ).inflate(24, 10)
            if main:
                pygame.draw.rect(
                    screen, constants.ACCENT_COLOR, chip,
                    border_radius=chip.height // 2,
                )
            else:
                pygame.draw.rect(
                    screen, constants.ACCENT_COLOR, chip,
                    width=2, border_radius=chip.height // 2,
                )
            screen.blit(tag_surf, tag_surf.get_rect(center=chip.center))

            line_y = rect.top + pad + head_h + 4
            pygame.draw.line(
                screen, constants.ACCENT_COLOR,
                (rect.left + pad, line_y), (rect.right - pad, line_y), 1,
            )

            y = line_y + 8
            for line in wrapped[i]:
                render.paint.text(
                    screen, text_font, line, constants.BODY_TEXT_COLOR,
                    anchor_point="topleft",
                    anchor_pos=(rect.left + pad, y),
                    shadow=None,
                )
                y += line_h

    def _draw_title_and_hint(
        self,
        screen: pygame.Surface,
        window_width: int,
        content_top: int,
        content_bottom: int,
    ) -> None:
        """Draw the title, unlocked counter pill and bottom hint bar."""
        cx = window_width // 2
        title_rect = render.paint.text(
            screen, render.fonts.get(constants.LEVELS_TITLE_SIZE),
            constants.LEVELS_TITLE_TEXT,
            constants.TITLE_COLOR,
            anchor_point="midtop",
            anchor_pos=(cx, content_top + constants.LEVELS_TITLE_TOP),
            shadow=constants.TITLE_SHADOW_OFFSET,
        )

        y = title_rect.centery
        d = constants.LEVELS_TITLE_DIAMOND
        for sign in (-1, 1):
            inner = cx + sign * (
                title_rect.width // 2 + constants.LEVELS_TITLE_LINE_GAP
            )
            outer = inner + sign * constants.LEVELS_TITLE_LINE_LEN
            pygame.draw.line(
                screen, constants.ACCENT_COLOR, (inner, y), (outer, y), 3
            )
            pygame.draw.polygon(
                screen, constants.ACCENT_COLOR,
                [(inner, y - d), (inner + d, y),
                 (inner, y + d), (inner - d, y)],
            )

        unlocked = min(self.game.unlocked_levels, self.node_count)
        sub = render.fonts.get(constants.LEVELS_SUBTITLE_SIZE).render(
            f"UNLOCKED {unlocked} / {self.node_count}",
            True, constants.ACCENT_COLOR,
        )
        pill = sub.get_rect(
            midtop=(cx, title_rect.bottom + constants.LEVELS_SUBTITLE_GAP)
        ).inflate(40, 14)
        render.paint.panel(
            screen, pill,
            radius=pill.height // 2,
            fill_alpha=constants.FOOTER_KEY_ALPHA,
            border_color=constants.ACCENT_COLOR,
        )
        screen.blit(sub, sub.get_rect(center=pill.center))

        hint_y = content_bottom - constants.LEVELS_HINT_BOTTOM
        screen.blit(self.hint_bar, self.hint_bar.get_rect(
            midbottom=(window_width // 2, hint_y)
        ))

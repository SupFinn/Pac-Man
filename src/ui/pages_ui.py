from __future__ import annotations

import math
from typing import Any, ClassVar, Sequence, TypedDict, cast

import pygame

from src.media import constants
from src.media import render
from src.media.media import AudioManager

ScoreData = Sequence[tuple[Any, Any]]


class SideSettings(TypedDict):
    frame_anchor: str
    expression_rects: dict[str, pygame.Rect]
    image_scale: float
    flip: bool
    char_offset: tuple[int, int]
    name_offset: tuple[int, int]
    name_text: str


class InfoPage:
    SIDE_SETTINGS: ClassVar[dict[str, SideSettings]] = {
        "left": {
            "frame_anchor": "midleft",
            "expression_rects": constants.LEFT_EXPRESSION_RECTS,
            "image_scale": constants.DIALOGUE_PAGE_LEFT_IMAGE_SCALE,
            "flip": False,
            "char_offset": (
                constants.LEFT_CHAR_OFFSET_X,
                constants.LEFT_CHAR_OFFSET_Y,
            ),
            "name_offset": (
                constants.LEFT_NAME_OFFSET_X,
                constants.LEFT_NAME_OFFSET_Y,
            ),
            "name_text": constants.DIALOGUE_PAGE_NAME_LEFT_TEXT,
        },
        "right": {
            "frame_anchor": "midright",
            "expression_rects": constants.RIGHT_EXPRESSION_RECTS,
            "image_scale": constants.DIALOGUE_PAGE_RIGHT_IMAGE_SCALE,
            "flip": True,
            "char_offset": (
                constants.RIGHT_CHAR_OFFSET_X,
                constants.RIGHT_CHAR_OFFSET_Y,
            ),
            "name_offset": (
                constants.RIGHT_NAME_OFFSET_X,
                constants.RIGHT_NAME_OFFSET_Y,
            ),
            "name_text": constants.DIALOGUE_PAGE_NAME_RIGHT_TEXT,
        },
    }

    def __init__(self, audio: AudioManager) -> None:
        """Load fonts, the conversation frame and initial dialogue and credits
        state."""
        self.audio = audio
        self.title_font = render.fonts.get(constants.INFO_TITLE_SIZE)
        self.panel_text_font = render.fonts.get(constants.INFO_QUAD_TEXT_SIZE)

        self.credits_name_font = render.fonts.get(constants.CREDITS_NAME_SIZE)
        self.credits_tagline_font = render.fonts.load(
            constants.CREDITS_TAGLINE_SIZE
        )
        self.credits_tagline_font.set_italic(True)
        self.nav_font = render.fonts.get(constants.INFO_NAV_BUTTON_FONT_SIZE)
        self.previous_rect: pygame.Rect | None = None

        self.dialogue_font = render.fonts.get(
            constants.DIALOGUE_PAGE_TEXT_SIZE
        )
        self.dialogue_index: int = 0
        self.dialogue_chars_shown: int = 0
        self.dialogue_type_elapsed_ms: int = 0
        self.left_expression: str = "thinking"
        self.right_expression: str = "thinking"
        self.skip_rect: pygame.Rect | None = None

        self.conv_frame_img = render.images.load_by_width(
            constants.CONV_FRAME_IMG, constants.CONV_FRAME_SIZE
        )
        self.dialogue_name_font = render.fonts.get(
            constants.DIALOGUE_PAGE_NAME_SIZE
        )

    def draw(
        self,
        screen: pygame.Surface,
        window_width: int,
        content_top: int,
        content_bottom: int,
        label: str,
    ) -> None:
        """Draw the page title, then the instructions
        dialogue or the credits."""
        title_rect = render.paint.text(
            screen, self.title_font, label, constants.TITLE_COLOR,
            anchor_point="midtop",
            anchor_pos=(
                window_width // 2,
                content_top + constants.INFO_TOP_GAP,
            ),
            shadow=constants.TITLE_SHADOW_OFFSET,
        )
        top = title_rect.bottom + constants.INFO_QUAD_GAP
        bottom = content_bottom - constants.INFO_BOTTOM_PADDING
        left = constants.INFO_QUAD_PADDING
        right = window_width - constants.INFO_QUAD_PADDING
        column_width = (right - left - constants.INFO_QUAD_GAP) // 2

        if label == "INSTRUCTIONS":
            self._draw_instructions(
                screen, window_width, top, bottom, column_width
            )
        else:
            self._draw_credits(screen, left, top, bottom, column_width)

    def _draw_instructions(
        self,
        screen: pygame.Surface,
        window_width: int,
        top: int,
        bottom: int,
        column_width: int,
    ) -> None:
        """Draw the current dialogue line with both character frames and nav
        buttons."""
        rect = pygame.Rect(
            constants.INFO_QUAD_PADDING,
            top,
            column_width * 2 + constants.INFO_QUAD_GAP,
            bottom - top,
        )

        if not constants.INSTRUCTIONS_DIALOGUE:
            return

        self.dialogue_index = max(
            0,
            min(self.dialogue_index, len(constants.INSTRUCTIONS_DIALOGUE) - 1),
        )
        speaker, expression, text = constants.INSTRUCTIONS_DIALOGUE[
            self.dialogue_index
        ]

        if speaker == "left":
            self.left_expression = expression
        else:
            self.right_expression = expression

        left_x = constants.BACK_TO_MENU_OFFSET_X
        right_x = window_width - constants.BACK_TO_MENU_OFFSET_X
        x_positions = {"left": left_x, "right": right_x}

        frame_rects = self._draw_character_frames(screen, rect, x_positions)

        revealed_text = text[:self.dialogue_chars_shown]
        bubble_width = int(
            rect.width * constants.DIALOGUE_PAGE_TEXT_WIDTH_RATIO
        )
        self._draw_speech_bubble(
            screen, revealed_text, bubble_width, frame_rects[speaker], speaker
        )

        self._draw_nav_buttons(screen, rect, left_x, right_x)

    def _draw_character_frames(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        x_positions: dict[str, int],
    ) -> dict[str, pygame.Rect]:
        """Draw both speaker frames, sprites and names, returning the frame
        rects."""
        expression_by_side = {
            "left": self.left_expression,
            "right": self.right_expression,
        }
        frame_rects: dict[str, pygame.Rect] = {}

        for side, settings in self.SIDE_SETTINGS.items():
            anchor_pos = (x_positions[side], rect.centery)
            anchor = settings["frame_anchor"]
            frame_rect = self.conv_frame_img.get_rect(**{anchor: anchor_pos})
            screen.blit(self.conv_frame_img, frame_rect)
            frame_rects[side] = frame_rect

            sprite = render.expressions.scaled_by(
                settings["expression_rects"][expression_by_side[side]],
                settings["image_scale"],
            )
            if settings["flip"]:
                sprite = pygame.transform.flip(sprite, True, False)

            offset_x, offset_y = settings["char_offset"]
            sprite_rect = sprite.get_rect(
                center=(
                    frame_rect.centerx + offset_x,
                    frame_rect.centery + offset_y,
                )
            )
            screen.blit(sprite, sprite_rect)

            name_offset_x, name_offset_y = settings["name_offset"]
            render.paint.text(
                screen, self.dialogue_name_font, settings["name_text"],
                constants.DIALOGUE_PAGE_NAME_COLOR,
                anchor_point="midtop",
                anchor_pos=(
                    frame_rect.centerx + name_offset_x,
                    frame_rect.bottom + name_offset_y,
                ),
                shadow=None,
            )

        return frame_rects

    def _draw_nav_buttons(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        left_x: int,
        right_x: int,
    ) -> None:
        """Draw the PREVIOUS and SKIP buttons and store their rects."""
        nav_width = self.conv_frame_img.get_width()
        nav_height = constants.INFO_NAV_BUTTON_HEIGHT
        nav_y = rect.bottom - constants.INFO_NAV_BUTTON_BOTTOM_PADDING

        previous_rect = pygame.Rect(0, 0, nav_width, nav_height)
        previous_rect.midleft = (left_x, nav_y)
        self.previous_rect = self._draw_nav_button(
            screen, "PREVIOUS", previous_rect
        )

        skip_rect = pygame.Rect(0, 0, nav_width, nav_height)
        skip_rect.midright = (right_x, nav_y)
        self.skip_rect = self._draw_nav_button(screen, "SKIP", skip_rect)

    def _draw_speech_bubble(
        self,
        screen: pygame.Surface,
        text: str,
        bubble_width: int,
        frame_rect: pygame.Rect,
        side: str,
    ) -> None:
        """Draw the wrapped, partially typed text in a bubble next to the
        speaker."""
        pad_x = constants.DIALOGUE_PAGE_TEXT_PADDING_X
        max_text_width = bubble_width - pad_x * 2
        if text:
            lines = render.fonts.wrap_text(
                text, self.dialogue_font, max_text_width)
        else:
            lines = [""]
        line_height = self.dialogue_font.get_height()
        line_gap = constants.DIALOGUE_PAGE_TEXT_LINE_GAP
        bubble_height = constants.DIALOGUE_PAGE_TEXT_PADDING_Y * 2
        bubble_height += len(lines) * line_height
        bubble_height += max(0, len(lines) - 1) * line_gap

        bubble_rect = pygame.Rect(0, 0, bubble_width, bubble_height)
        if side == "left":
            bubble_rect.midleft = (
                frame_rect.right + constants.DIALOGUE_PAGE_BUBBLE_GAP,
                frame_rect.centery,
            )
        else:
            bubble_rect.midright = (
                frame_rect.left - constants.DIALOGUE_PAGE_BUBBLE_GAP,
                frame_rect.centery,
            )

        render.paint.panel(
            screen, bubble_rect,
            radius=16, fill_alpha=150, border_color=constants.ACCENT_COLOR,
        )

        y = bubble_rect.top + constants.DIALOGUE_PAGE_TEXT_PADDING_Y
        for line in lines:
            render.paint.text(
                screen, self.dialogue_font, line,
                constants.DIALOGUE_PAGE_TEXT_COLOR,
                anchor_point="topleft",
                anchor_pos=(
                    bubble_rect.left + constants.DIALOGUE_PAGE_TEXT_PADDING_X,
                    y,
                ),
                shadow=None,
            )
            y += line_height + line_gap

    def update(self, dt_ms: int) -> None:
        """Advance the typewriter effect and stop the
        voice when the line ends."""
        if self.dialogue_index >= len(constants.INSTRUCTIONS_DIALOGUE):
            return
        text = constants.INSTRUCTIONS_DIALOGUE[self.dialogue_index][2]
        if self.dialogue_chars_shown >= len(text):
            return
        self.dialogue_type_elapsed_ms += dt_ms
        char_ms = constants.DIALOGUE_PAGE_TYPE_CHAR_MS
        typed = self.dialogue_type_elapsed_ms // char_ms
        self.dialogue_chars_shown = min(len(text), typed)
        if self.dialogue_chars_shown >= len(text):
            self.stop_voice()

    def _play_voice(self) -> None:
        """Play the voice sound of the current speaker."""
        self.stop_voice()
        speaker = constants.INSTRUCTIONS_DIALOGUE[self.dialogue_index][0]
        self.audio.play("finn_talks" if speaker == "left" else "eyomi_talks")

    def stop_voice(self) -> None:
        """Stop both speaker voice sounds."""
        self.audio.stop("finn_talks", "eyomi_talks")

    def reset_dialogue(self) -> None:
        """Restart the dialogue from the first line and play its voice."""
        self.dialogue_index = 0
        self.dialogue_chars_shown = 0
        self.dialogue_type_elapsed_ms = 0
        self.left_expression = "thinking"
        self.right_expression = "thinking"
        self._play_voice()

    def _goto_line(self, index: int) -> None:
        """Jump to a clamped dialogue line and restart its typing and voice."""
        last = len(constants.INSTRUCTIONS_DIALOGUE) - 1
        self.dialogue_index = max(0, min(last, index))
        self.dialogue_chars_shown = 0
        self.dialogue_type_elapsed_ms = 0
        self._play_voice()

    def skip_dialogue(self) -> None:
        """Go to the next dialogue line."""
        self._goto_line(self.dialogue_index + 1)

    def previous_dialogue(self) -> None:
        """Go back to the previous dialogue line."""
        self._goto_line(self.dialogue_index - 1)

    def _draw_nav_button(
        self, screen: pygame.Surface, label: str, slot_rect: pygame.Rect
    ) -> pygame.Rect:
        """Draw a nav button (pressed look on hover) and return its rect."""
        pressed = slot_rect.collidepoint(pygame.mouse.get_pos())
        if pressed:
            sprite_rect = constants.BUTTON_PRESSED_RECT
        else:
            sprite_rect = constants.BUTTON_RECT
        sprite = render.buttons.get(sprite_rect, slot_rect.size)
        screen.blit(sprite, sprite.get_rect(center=slot_rect.center))
        text = self.nav_font.render(
            label, True, constants.INFO_NAV_BUTTON_TEXT_COLOR
        )
        screen.blit(text, text.get_rect(center=slot_rect.center))
        return slot_rect

    def _draw_credits(
        self,
        screen: pygame.Surface,
        left: int,
        top: int,
        bottom: int,
        column_width: int,
    ) -> None:
        """Draw one credits panel per person."""
        gap = constants.INFO_QUAD_GAP
        height = bottom - top

        for index, person in enumerate(constants.CREDITS_PEOPLE):
            rect = pygame.Rect(
                left + index * (column_width + gap), top, column_width, height
            )
            render.paint.panel(screen, rect)
            self._draw_person(screen, rect, *person)

    def _draw_person(
        self,
        screen: pygame.Surface,
        rect: pygame.Rect,
        sprite_rect: pygame.Rect,
        name: str,
        full_name: str,
    ) -> None:
        """Draw a credits card: name, tagline, floating sprite and social
        links."""
        phase = rect.top * 0.02
        angle = pygame.time.get_ticks() * constants.CREDITS_FLOAT_SPEED
        bob = int(
            math.sin(angle + phase) * constants.CREDITS_FLOAT_AMPLITUDE
        )

        padding = constants.CREDITS_PERSON_PADDING
        max_width = rect.width - padding * 2
        line_gap = constants.CREDITS_LINE_GAP

        tagline = constants.CREDITS_TAGLINES.get(name, "")
        tagline_lines: list[str] = []
        if tagline:
            tagline_lines = render.fonts.wrap_text(
                tagline, self.credits_tagline_font, max_width
            )
        tagline_line_height = self.credits_tagline_font.get_height()
        tagline_block_height = len(tagline_lines) * tagline_line_height
        tagline_block_height += max(0, len(tagline_lines) - 1) * line_gap

        sprite_height = min(
            int(rect.height * constants.CREDITS_SPRITE_HEIGHT_RATIO),
            rect.height - padding * 2,
        )
        sprite = render.us_sheet.scaled_to_height(sprite_rect, sprite_height)

        socials = [
            (icon, handle)
            for icon, owner, handle in constants.SOCIAL_ENTRIES
            if owner == name
        ]
        size = constants.CREDITS_SOCIAL_ICON_SIZE
        row_gap = constants.SOCIAL_ROW_GAP
        socials_height = len(socials) * size
        socials_height += max(0, len(socials) - 1) * row_gap

        name_height = self.credits_name_font.get_height()

        total_height = name_height
        total_height += constants.CREDITS_TAGLINE_GAP + tagline_block_height
        total_height += constants.CREDITS_PERSON_TEXT_GAP + sprite.get_height()
        total_height += constants.CREDITS_PERSON_SOCIALS_GAP + socials_height

        y = rect.centery - total_height // 2

        name_rect = render.paint.text(
            screen, self.credits_name_font, name.upper(),
            constants.TITLE_COLOR,
            anchor_point="midtop", anchor_pos=(rect.centerx, y),
        )
        y = name_rect.bottom + constants.CREDITS_TAGLINE_GAP

        for i, line in enumerate(tagline_lines):
            line_rect = render.paint.text(
                screen, self.credits_tagline_font, line,
                constants.ACCENT_COLOR,
                anchor_point="midtop", anchor_pos=(rect.centerx, y),
                shadow=None,
            )
            y = line_rect.bottom
            if i < len(tagline_lines) - 1:
                y += line_gap
        y += constants.CREDITS_PERSON_TEXT_GAP

        sprite_dest = sprite.get_rect(midtop=(rect.centerx, y + bob))
        screen.blit(sprite, sprite_dest)
        y = sprite_dest.bottom + constants.CREDITS_PERSON_SOCIALS_GAP

        for icon_rect, handle in socials:
            icon = render.social_sheet.get(icon_rect, (size, size))
            handle_width = self.panel_text_font.size(handle)[0]
            row_width = size + constants.SOCIAL_ICON_TEXT_GAP + handle_width
            row_left = rect.centerx - row_width // 2
            icon_dest = icon.get_rect(midleft=(row_left, y + size // 2))
            screen.blit(icon, icon_dest)
            render.paint.text(
                screen, self.panel_text_font, handle,
                constants.BODY_TEXT_COLOR,
                anchor_point="midleft",
                anchor_pos=(
                    icon_dest.right + constants.SOCIAL_ICON_TEXT_GAP,
                    y + size // 2,
                ),
            )
            y += size + row_gap


class ScoreboardPage:
    def draw(
        self,
        screen: pygame.Surface,
        window_width: int,
        content_top: int,
        content_bottom: int,
        data: ScoreData,
    ) -> None:
        """Lay out and draw the leaderboard, champion and stats cards."""
        back_rects = constants.ICON_RECTS["BACK"]
        icon_height = constants.BACK_TO_MENU_ICON_HEIGHT
        back_normal = render.icons.scaled_to_height(
            back_rects["normal"], icon_height
        )
        back_pressed = render.icons.scaled_to_height(
            back_rects["pressed"], icon_height
        )
        back_width = max(back_normal.get_width(), back_pressed.get_width())

        margin = constants.BACK_TO_MENU_OFFSET_X + back_width
        margin += constants.SCOREBOARD_OUTER_GAP
        gap = constants.SCOREBOARD_COLUMN_GAP
        card_gap = constants.SCOREBOARD_CARD_GAP
        top = content_top + constants.SCOREBOARD_TOP_MARGIN
        height = content_bottom - constants.SCOREBOARD_BOTTOM_MARGIN - top

        main_w = int(window_width * constants.SCOREBOARD_MAIN_WIDTH_RATIO)
        main_rect = pygame.Rect(margin, top, main_w, height)

        right_left = main_rect.right + gap
        right_width = window_width - margin - right_left

        top_h = (height - card_gap) // 2
        bottom_h = height - card_gap - top_h
        champion_rect = pygame.Rect(right_left, top, right_width, top_h)
        stats_rect = pygame.Rect(
            right_left, champion_rect.bottom + card_gap, right_width, bottom_h
        )

        self._draw_board(screen, main_rect, data)
        self._draw_champion_card(screen, champion_rect, data)
        self._draw_stats_card(screen, stats_rect, data)

    @staticmethod
    def _row_height(
        panel_rect: pygame.Rect,
        rows: int,
        pad: int,
        title_font: pygame.font.Font,
        header_font: pygame.font.Font,
    ) -> int:
        """Compute the score row height so all rows fit inside the panel."""
        fixed_h = pad * 2 + title_font.get_height()
        fixed_h += constants.SCOREBOARD_TITLE_GAP
        fixed_h += header_font.get_height() + constants.SCOREBOARD_HEADER_GAP
        gaps = (rows - 1) * constants.SCOREBOARD_ROW_GAP
        available = (panel_rect.height - fixed_h - gaps) // rows
        return cast(int,
                    max(24, min(constants.SCOREBOARD_ROW_HEIGHT, available)))

    def _draw_board(
        self, screen: pygame.Surface, panel_rect: pygame.Rect, data: ScoreData
    ) -> None:
        """Draw the top-10 board with rank, name and score rows."""
        rows = constants.SCOREBOARD_MAX_ROWS
        pad = constants.SCOREBOARD_PANEL_PADDING

        title_font = render.fonts.get(constants.SCOREBOARD_TITLE_SIZE)
        header_font = render.fonts.get(constants.SCOREBOARD_HEADER_SIZE)
        row_font = render.fonts.get(constants.SCOREBOARD_ROW_SIZE)

        row_h = self._row_height(
            panel_rect, rows, pad, title_font, header_font
        )

        render.paint.panel(
            screen, panel_rect,
            radius=constants.SCOREBOARD_PANEL_RADIUS,
            fill_alpha=constants.SCOREBOARD_PANEL_ALPHA,
        )

        y = panel_rect.top + pad
        title_rect = render.paint.text(
            screen, title_font, constants.SCOREBOARD_TITLE_TEXT,
            constants.TITLE_COLOR,
            anchor_point="midtop", anchor_pos=(panel_rect.centerx, y),
            shadow=None,
        )
        y = title_rect.bottom + constants.SCOREBOARD_TITLE_GAP

        left = panel_rect.left + pad
        right = panel_rect.right - pad
        text_left = left + constants.SCOREBOARD_ROW_PADDING_X
        text_right = right - constants.SCOREBOARD_ROW_PADDING_X
        name_x = text_left + constants.SCOREBOARD_RANK_COL_WIDTH

        render.paint.text(
            screen, header_font, "RANK", constants.ACCENT_COLOR,
            anchor_point="topleft", anchor_pos=(text_left, y), shadow=None,
        )
        render.paint.text(
            screen, header_font, "NAME", constants.ACCENT_COLOR,
            anchor_point="topleft", anchor_pos=(name_x, y), shadow=None,
        )
        render.paint.text(
            screen, header_font, "SCORE", constants.ACCENT_COLOR,
            anchor_point="topright", anchor_pos=(text_right, y), shadow=None,
        )
        y += header_font.get_height() + constants.SCOREBOARD_HEADER_GAP

        for i in range(rows):
            row_rect = pygame.Rect(left, y, right - left, row_h)
            entry = data[i] if i < len(data) else None
            podium = i < len(constants.SCOREBOARD_RANK_COLORS)
            color = (
                constants.SCOREBOARD_RANK_COLORS[i]
                if podium
                else constants.ACCENT_COLOR
            )

            render.paint.panel(
                screen, row_rect,
                radius=constants.SCOREBOARD_ROW_RADIUS,
                fill_alpha=constants.SCOREBOARD_ROW_ALPHA,
                border_color=color,
                border_width=2 if podium else 1,
                border_alpha=255 if podium else 90,
            )

            text_color = color if podium else constants.BODY_TEXT_COLOR
            alpha = None if entry else constants.SCOREBOARD_EMPTY_ALPHA
            name = str(entry[1]) if entry else constants.SCOREBOARD_EMPTY_TEXT
            score = str(entry[0]) if entry else constants.SCOREBOARD_EMPTY_TEXT

            render.paint.text(
                screen, row_font, f"#{i + 1}", color,
                anchor_point="midleft",
                anchor_pos=(text_left, row_rect.centery),
                shadow=None, alpha=alpha,
            )
            render.paint.text(
                screen, row_font, name, text_color,
                anchor_point="midleft", anchor_pos=(name_x, row_rect.centery),
                shadow=None, alpha=alpha,
            )
            render.paint.text(
                screen, row_font, score, text_color,
                anchor_point="midright",
                anchor_pos=(text_right, row_rect.centery),
                shadow=None, alpha=alpha,
            )

            y += row_h + constants.SCOREBOARD_ROW_GAP

    @staticmethod
    def _draw_info_card(
        screen: pygame.Surface,
        rect: pygame.Rect,
        title: str,
        rows: list[tuple[str, str]],
        footer: str | None = None,
    ) -> None:
        """Draw a titled card of label/value rows with an optional footer."""
        pad = constants.SCOREBOARD_CARD_PADDING
        title_font = render.fonts.get(constants.SCOREBOARD_CARD_TITLE_SIZE)
        label_font = render.fonts.get(constants.SCOREBOARD_CARD_LABEL_SIZE)
        value_font = render.fonts.get(constants.SCOREBOARD_CARD_VALUE_SIZE)
        footer_font = render.fonts.get(constants.SCOREBOARD_CARD_FOOTER_SIZE)

        render.paint.panel(
            screen, rect,
            radius=constants.SCOREBOARD_PANEL_RADIUS,
            fill_alpha=constants.SCOREBOARD_PANEL_ALPHA,
        )

        y = rect.top + pad
        title_rect = render.paint.text(
            screen, title_font, title, constants.TITLE_COLOR,
            anchor_point="midtop", anchor_pos=(rect.centerx, y), shadow=None,
        )
        y = title_rect.bottom + constants.SCOREBOARD_TITLE_GAP

        line_y = y - constants.SCOREBOARD_TITLE_GAP // 2
        pygame.draw.line(
            screen, constants.ACCENT_COLOR,
            (rect.left + pad, line_y),
            (rect.right - pad, line_y),
            width=1,
        )

        footer_lines: list[str] = []
        if footer:
            footer_lines = render.fonts.wrap_text(
                footer, footer_font, rect.width - pad * 2
            )
        footer_h = len(footer_lines) * footer_font.get_height()
        limit = rect.bottom - pad - footer_h

        for label, value in rows:
            if y + value_font.get_height() > limit:
                break
            mid_y = y + value_font.get_height() // 2
            render.paint.text(
                screen, label_font, label, constants.ACCENT_COLOR,
                anchor_point="midleft", anchor_pos=(rect.left + pad, mid_y),
                shadow=None,
            )
            render.paint.text(
                screen, value_font, value, constants.BODY_TEXT_COLOR,
                anchor_point="midright", anchor_pos=(rect.right - pad, mid_y),
                shadow=None,
            )
            y += value_font.get_height() + constants.SCOREBOARD_CARD_ROW_GAP

        fy = rect.bottom - pad - footer_h
        for line in footer_lines:
            line_rect = render.paint.text(
                screen, footer_font, line, constants.BODY_TEXT_COLOR,
                anchor_point="midtop", anchor_pos=(rect.centerx, fy),
                shadow=None,
            )
            fy = line_rect.bottom

    def _draw_champion_card(
        self, screen: pygame.Surface, rect: pygame.Rect, data: ScoreData
    ) -> None:
        """Draw the card showing the top score holder,
        or an empty placeholder."""
        rows: list[tuple[str, str]]
        if data:
            score, name = data[0]
            rows = [("NAME", str(name)), ("SCORE", str(score)), ("RANK", "#1")]
            footer = constants.SCOREBOARD_CHAMPION_FOOTER
        else:
            rows = [
                ("NAME", constants.SCOREBOARD_EMPTY_TEXT),
                ("SCORE", constants.SCOREBOARD_EMPTY_TEXT),
                ("RANK", "#1"),
            ]
            footer = constants.SCOREBOARD_CHAMPION_EMPTY_FOOTER
        self._draw_info_card(
            screen, rect, constants.SCOREBOARD_CHAMPION_TITLE, rows, footer
        )

    def _draw_stats_card(
        self, screen: pygame.Surface, rect: pygame.Rect, data: ScoreData
    ) -> None:
        """Draw best, average, player count and the score needed to enter."""
        scores = [d[0] for d in data]
        best = str(max(scores)) if scores else constants.SCOREBOARD_EMPTY_TEXT
        if scores:
            average = str(sum(scores) // len(scores))
        else:
            average = constants.SCOREBOARD_EMPTY_TEXT
        if len(scores) >= constants.SCOREBOARD_MAX_ROWS:
            to_enter = str(min(scores) + 1)
        else:
            to_enter = "ANY"
        rows = [
            ("BEST", best),
            ("AVERAGE", average),
            ("PLAYERS", f"{len(scores)}/{constants.SCOREBOARD_MAX_ROWS}"),
            ("TO ENTER", to_enter),
        ]
        self._draw_info_card(
            screen, rect, constants.SCOREBOARD_STATS_TITLE, rows,
            constants.SCOREBOARD_STATS_FOOTER,
        )
